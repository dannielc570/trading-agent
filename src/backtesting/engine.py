"""Backtesting engine using VectorBT"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

try:
    import vectorbt as vbt
    VECTORBT_AVAILABLE = True
except ImportError:
    VECTORBT_AVAILABLE = False
    logger.warning("VectorBT not available")


class BacktestEngine:
    """Backtesting engine for strategy evaluation"""
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0005
    ):
        """
        Initialize backtest engine
        
        Args:
            initial_capital: Starting capital
            commission: Commission rate (0.001 = 0.1%)
            slippage: Slippage rate
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.vectorbt_available = VECTORBT_AVAILABLE
    
    def run_backtest(
        self,
        data: pd.DataFrame,
        signals: pd.Series,
        strategy_name: str = "Strategy"
    ) -> Dict[str, Any]:
        """
        Run backtest with given signals
        
        Args:
            data: OHLCV DataFrame with 'close' column
            signals: Buy/sell signals (-1, 0, 1)
            strategy_name: Name of strategy
            
        Returns:
            Dictionary with backtest results
        """
        try:
            if not self.vectorbt_available:
                return self._simple_backtest(data, signals, strategy_name)
            
            return self._vectorbt_backtest(data, signals, strategy_name)
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return {"error": str(e)}
    
    def _vectorbt_backtest(
        self,
        data: pd.DataFrame,
        signals: pd.Series,
        strategy_name: str
    ) -> Dict[str, Any]:
        """Run backtest using VectorBT"""
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
            
            # Get equity curve
            equity_curve = portfolio.value().tolist()
            
            results = {
                "strategy_name": strategy_name,
                "total_return": float(total_return) if not np.isnan(total_return) else 0.0,
                "sharpe_ratio": float(sharpe_ratio) if not np.isnan(sharpe_ratio) else 0.0,
                "max_drawdown": float(max_drawdown) if not np.isnan(max_drawdown) else 0.0,
                "win_rate": float(win_rate) if not np.isnan(win_rate) else 0.0,
                "total_trades": int(total_trades),
                "final_value": float(portfolio.final_value()),
                "equity_curve": equity_curve,
                "status": "completed"
            }
            
            logger.info(f"Backtest completed: {strategy_name}")
            return results
            
        except Exception as e:
            logger.error(f"VectorBT backtest error: {e}")
            return {"error": str(e), "status": "failed"}
    
    def _simple_backtest(
        self,
        data: pd.DataFrame,
        signals: pd.Series,
        strategy_name: str
    ) -> Dict[str, Any]:
        """Simple backtest implementation without VectorBT"""
        try:
            close = data['close'].values
            capital = self.initial_capital
            position = 0
            trades = []
            equity_curve = [capital]
            
            for i in range(1, len(close)):
                if signals.iloc[i] == 1 and position == 0:
                    # Buy
                    position = capital / (close[i] * (1 + self.commission + self.slippage))
                    capital = 0
                    trades.append({'type': 'buy', 'price': close[i], 'index': i})
                    
                elif signals.iloc[i] == -1 and position > 0:
                    # Sell
                    capital = position * close[i] * (1 - self.commission - self.slippage)
                    position = 0
                    trades.append({'type': 'sell', 'price': close[i], 'index': i})
                
                # Calculate current equity
                current_equity = capital + (position * close[i] if position > 0 else 0)
                equity_curve.append(current_equity)
            
            # Close any open position
            if position > 0:
                capital = position * close[-1] * (1 - self.commission - self.slippage)
            
            final_value = capital
            total_return = (final_value - self.initial_capital) / self.initial_capital
            
            # Calculate metrics
            equity_series = pd.Series(equity_curve)
            returns = equity_series.pct_change().dropna()
            
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
            
            rolling_max = equity_series.expanding().max()
            drawdown = (equity_series - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            winning_trades = sum(1 for i in range(0, len(trades)-1, 2) 
                               if i+1 < len(trades) and trades[i+1]['price'] > trades[i]['price'])
            total_trades = len(trades) // 2
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            results = {
                "strategy_name": strategy_name,
                "total_return": float(total_return),
                "sharpe_ratio": float(sharpe_ratio),
                "max_drawdown": float(max_drawdown),
                "win_rate": float(win_rate),
                "total_trades": total_trades,
                "final_value": float(final_value),
                "equity_curve": equity_curve,
                "status": "completed"
            }
            
            logger.info(f"Simple backtest completed: {strategy_name}")
            return results
            
        except Exception as e:
            logger.error(f"Simple backtest error: {e}")
            return {"error": str(e), "status": "failed"}
