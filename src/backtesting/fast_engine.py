"""Fast Backtesting Engine with Backtrader + Parallel Processing

This engine provides:
- Backtrader integration for faster execution
- Parallel processing for multiple strategies/assets
- Timeout handling to prevent stuck operations
- Performance monitoring
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger
import asyncio
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FuturesTimeoutError
import time

try:
    import backtrader as bt
    BACKTRADER_AVAILABLE = True
except ImportError:
    BACKTRADER_AVAILABLE = False
    logger.warning("⚠️  Backtrader not available, install with: pip install backtrader")

try:
    import vectorbt as vbt
    VECTORBT_AVAILABLE = True
except ImportError:
    VECTORBT_AVAILABLE = False


class FastBacktestEngine:
    """High-performance backtesting engine with multiple backends"""
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0005,
        max_workers: int = 4,
        timeout_seconds: int = 30
    ):
        """
        Initialize fast backtest engine
        
        Args:
            initial_capital: Starting capital
            commission: Commission rate (0.001 = 0.1%)
            slippage: Slippage rate
            max_workers: Number of parallel workers
            timeout_seconds: Timeout for each backtest
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.max_workers = max_workers
        self.timeout_seconds = timeout_seconds
        self.backtrader_available = BACKTRADER_AVAILABLE
        self.vectorbt_available = VECTORBT_AVAILABLE
        
        # Performance stats
        self.stats = {
            'total_backtests': 0,
            'successful': 0,
            'failed': 0,
            'timeouts': 0,
            'avg_duration': 0.0
        }
    
    async def run_backtest_parallel(
        self,
        backtests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Run multiple backtests in parallel
        
        Args:
            backtests: List of backtest configs with 'data', 'signals', 'name'
            
        Returns:
            List of backtest results
        """
        start_time = time.time()
        logger.info(f"🚀 Running {len(backtests)} backtests in parallel (max_workers={self.max_workers})...")
        
        # Use process pool for CPU-bound backtesting
        loop = asyncio.get_event_loop()
        results = []
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for bt_config in backtests:
                future = loop.run_in_executor(
                    executor,
                    self._run_single_backtest_sync,
                    bt_config['data'],
                    bt_config['signals'],
                    bt_config['name']
                )
                futures.append(future)
            
            # Wait for all with timeout
            for i, future in enumerate(futures):
                try:
                    result = await asyncio.wait_for(future, timeout=self.timeout_seconds)
                    results.append(result)
                    self.stats['successful'] += 1
                except asyncio.TimeoutError:
                    logger.warning(f"⏱️  Backtest {i+1} timed out after {self.timeout_seconds}s")
                    results.append({
                        'error': 'timeout',
                        'status': 'timeout',
                        'name': backtests[i]['name']
                    })
                    self.stats['timeouts'] += 1
                except Exception as e:
                    logger.error(f"❌ Backtest {i+1} failed: {e}")
                    results.append({
                        'error': str(e),
                        'status': 'failed',
                        'name': backtests[i]['name']
                    })
                    self.stats['failed'] += 1
        
        duration = time.time() - start_time
        self.stats['total_backtests'] += len(backtests)
        self.stats['avg_duration'] = duration / len(backtests)
        
        logger.info(f"✅ Completed {len(results)} backtests in {duration:.2f}s (avg: {self.stats['avg_duration']:.2f}s/test)")
        
        return results
    
    def _run_single_backtest_sync(
        self,
        data: pd.DataFrame,
        signals: pd.Series,
        name: str
    ) -> Dict[str, Any]:
        """
        Run single backtest synchronously (called in separate process)
        """
        try:
            # Try Backtrader first (fastest), fallback to VectorBT, then simple
            if self.backtrader_available:
                return self._backtrader_backtest(data, signals, name)
            elif self.vectorbt_available:
                return self._vectorbt_backtest(data, signals, name)
            else:
                return self._simple_fast_backtest(data, signals, name)
        except Exception as e:
            logger.error(f"Backtest error for {name}: {e}")
            return {'error': str(e), 'status': 'failed', 'name': name}
    
    def _backtrader_backtest(
        self,
        data: pd.DataFrame,
        signals: pd.Series,
        name: str
    ) -> Dict[str, Any]:
        """Run backtest using Backtrader (fastest)"""
        try:
            # Create Cerebro engine
            cerebro = bt.Cerebro()
            cerebro.broker.setcash(self.initial_capital)
            cerebro.broker.setcommission(commission=self.commission)
            
            # Add data feed
            data_feed = bt.feeds.PandasData(dataname=data)
            cerebro.adddata(data_feed)
            
            # Add custom strategy that follows signals
            class SignalStrategy(bt.Strategy):
                def __init__(strategy_self):
                    strategy_self.signals = signals
                    strategy_self.order = None
                
                def next(strategy_self):
                    idx = len(strategy_self)
                    if idx >= len(signals):
                        return
                    
                    signal = signals.iloc[idx]
                    
                    if signal == 1 and not strategy_self.position:
                        # Buy signal
                        strategy_self.order = strategy_self.buy()
                    elif signal == -1 and strategy_self.position:
                        # Sell signal
                        strategy_self.order = strategy_self.sell()
            
            cerebro.addstrategy(SignalStrategy)
            
            # Add analyzers
            cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
            cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
            cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
            cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
            
            # Run backtest
            results = cerebro.run()
            strat = results[0]
            
            # Extract metrics
            sharpe = strat.analyzers.sharpe.get_analysis().get('sharperatio', 0)
            drawdown = strat.analyzers.drawdown.get_analysis()
            trades = strat.analyzers.trades.get_analysis()
            returns = strat.analyzers.returns.get_analysis()
            
            final_value = cerebro.broker.getvalue()
            total_return = (final_value - self.initial_capital) / self.initial_capital
            
            # Calculate win rate
            total_trades = trades.get('total', {}).get('total', 0)
            won_trades = trades.get('won', {}).get('total', 0)
            win_rate = won_trades / total_trades if total_trades > 0 else 0
            
            result = {
                'name': name,
                'engine': 'backtrader',
                'total_return': float(total_return),
                'sharpe_ratio': float(sharpe) if sharpe else 0.0,
                'max_drawdown': float(drawdown.get('max', {}).get('drawdown', 0)) / 100,
                'win_rate': float(win_rate),
                'total_trades': int(total_trades),
                'final_value': float(final_value),
                'status': 'completed'
            }
            
            logger.debug(f"✅ Backtrader: {name} - Return: {total_return*100:.2f}%, Sharpe: {sharpe:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Backtrader error for {name}: {e}")
            raise
    
    def _vectorbt_backtest(
        self,
        data: pd.DataFrame,
        signals: pd.Series,
        name: str
    ) -> Dict[str, Any]:
        """Run backtest using VectorBT (fallback)"""
        try:
            close = data['close'].values
            
            # Create entries and exits
            entries = signals == 1
            exits = signals == -1
            
            # Run portfolio simulation
            portfolio = vbt.Portfolio.from_signals(
                close=close,
                entries=entries,
                exits=exits,
                init_cash=self.initial_capital,
                fees=self.commission,
                slippage=self.slippage
            )
            
            # Calculate metrics
            total_return = portfolio.total_return()
            sharpe_ratio = portfolio.sharpe_ratio()
            max_drawdown = portfolio.max_drawdown()
            win_rate = portfolio.win_rate()
            total_trades = portfolio.total_trades()
            
            result = {
                'name': name,
                'engine': 'vectorbt',
                'total_return': float(total_return) if not np.isnan(total_return) else 0.0,
                'sharpe_ratio': float(sharpe_ratio) if not np.isnan(sharpe_ratio) else 0.0,
                'max_drawdown': float(max_drawdown) if not np.isnan(max_drawdown) else 0.0,
                'win_rate': float(win_rate) if not np.isnan(win_rate) else 0.0,
                'total_trades': int(total_trades),
                'final_value': float(portfolio.final_value()),
                'status': 'completed'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"VectorBT error for {name}: {e}")
            raise
    
    def _simple_fast_backtest(
        self,
        data: pd.DataFrame,
        signals: pd.Series,
        name: str
    ) -> Dict[str, Any]:
        """Simple fast backtest (fallback)"""
        try:
            close = data['close'].values
            capital = self.initial_capital
            position = 0
            trades_count = 0
            wins = 0
            entry_price = 0
            
            for i in range(1, len(close)):
                if signals.iloc[i] == 1 and position == 0:
                    # Buy
                    position = capital / (close[i] * (1 + self.commission))
                    capital = 0
                    entry_price = close[i]
                    
                elif signals.iloc[i] == -1 and position > 0:
                    # Sell
                    capital = position * close[i] * (1 - self.commission)
                    position = 0
                    trades_count += 1
                    if close[i] > entry_price:
                        wins += 1
            
            # Close position
            if position > 0:
                capital = position * close[-1] * (1 - self.commission)
                if close[-1] > entry_price:
                    wins += 1
                trades_count += 1
            
            final_value = capital
            total_return = (final_value - self.initial_capital) / self.initial_capital
            win_rate = wins / trades_count if trades_count > 0 else 0
            
            # Quick Sharpe approximation
            returns = pd.Series(close).pct_change().dropna()
            sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
            
            # Quick drawdown
            equity = pd.Series([self.initial_capital + (final_value - self.initial_capital) * i / len(close) 
                              for i in range(len(close))])
            max_dd = (equity / equity.cummax() - 1).min()
            
            result = {
                'name': name,
                'engine': 'simple',
                'total_return': float(total_return),
                'sharpe_ratio': float(sharpe),
                'max_drawdown': float(max_dd),
                'win_rate': float(win_rate),
                'total_trades': trades_count,
                'final_value': float(final_value),
                'status': 'completed'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Simple backtest error for {name}: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.stats.copy()
