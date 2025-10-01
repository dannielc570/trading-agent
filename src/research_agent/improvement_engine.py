"""Improvement Engine - Continuously optimizes and improves strategies

This module:
- Automatically optimizes strategy parameters
- Tests strategies on new assets
- Adds new indicators to improve performance
- Learns from results and adapts
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from ..database import get_db_context, Strategy, Backtest
from ..data_collection import MarketDataCollector
from ..backtesting import BacktestEngine
from ..ml_optimization import StrategyOptimizer
from .knowledge_base import KnowledgeBase


class ImprovementEngine:
    """Continuously improves platform performance"""
    
    def __init__(self):
        self.knowledge = KnowledgeBase()
        self.data_collector = MarketDataCollector()
        self.backtest_engine = BacktestEngine()
        self.optimizer = StrategyOptimizer()
        
    async def optimize_strategy(self, strategy_id: int, asset: str = 'AAPL') -> Dict[str, Any]:
        """Optimize parameters for a specific strategy"""
        logger.info(f"🎯 Optimizing strategy {strategy_id} on {asset}...")
        
        try:
            with get_db_context() as db:
                strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
                
                if not strategy:
                    return {'success': False, 'error': 'Strategy not found'}
                
                # Fetch market data
                data = await self.data_collector.fetch_ohlcv(
                    symbol=asset,
                    timeframe='1d'
                )
                
                if data is None or len(data) < 100:
                    return {'success': False, 'error': 'Insufficient data'}
                
                # Define parameter grid based on strategy category
                param_grid = self._get_parameter_grid(strategy.category)
                
                # Run optimization
                best_params, best_metrics = self.optimizer.grid_search(
                    strategy_class=self._get_strategy_class(strategy.category),
                    data=data,
                    param_grid=param_grid,
                    metric='sharpe_ratio'
                )
                
                # Update strategy with best parameters
                strategy.parameters = best_params
                strategy.status = 'optimized'
                db.commit()
                
                logger.info(f"✅ Optimized {strategy.name}: Sharpe {best_metrics['sharpe_ratio']:.2f}")
                
                return {
                    'success': True,
                    'strategy_id': strategy_id,
                    'best_params': best_params,
                    'metrics': best_metrics
                }
                
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def test_on_new_asset(self, strategy_id: int, asset: str) -> Dict[str, Any]:
        """Test a strategy on a new asset"""
        logger.info(f"📊 Testing strategy {strategy_id} on {asset}...")
        
        try:
            with get_db_context() as db:
                strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
                
                if not strategy:
                    return {'success': False, 'error': 'Strategy not found'}
                
                # Check if already tested
                existing = db.query(Backtest).filter(
                    Backtest.strategy_id == strategy_id,
                    Backtest.symbol == asset
                ).first()
                
                if existing:
                    logger.info(f"Strategy already tested on {asset}")
                    return {'success': True, 'existing': True, 'backtest_id': existing.id}
                
                # Fetch data
                data = await self.data_collector.fetch_ohlcv(
                    symbol=asset,
                    timeframe='1d'
                )
                
                if data is None or len(data) < 100:
                    return {'success': False, 'error': f'Insufficient data for {asset}'}
                
                # Get strategy instance
                strategy_instance = self._get_strategy_instance(
                    strategy.category,
                    strategy.parameters or {}
                )
                
                # Generate signals
                signals = strategy_instance.generate_signals(data)
                
                # Run backtest
                results = self.backtest_engine.run_backtest(
                    data=data,
                    signals=signals,
                    name=f"{strategy.name} on {asset}"
                )
                
                # Save results
                backtest = Backtest(
                    strategy_id=strategy_id,
                    symbol=asset,
                    timeframe='1d',
                    start_date=data.index[0],
                    end_date=data.index[-1],
                    initial_capital=10000.0,
                    total_return=results['total_return'],
                    sharpe_ratio=results['sharpe_ratio'],
                    max_drawdown=results['max_drawdown'],
                    win_rate=results['win_rate'],
                    total_trades=results['total_trades'],
                    status='completed'
                )
                
                db.add(backtest)
                db.commit()
                db.refresh(backtest)
                
                logger.info(f"✅ Tested {strategy.name} on {asset}: Return {results['total_return']*100:.2f}%")
                
                return {
                    'success': True,
                    'backtest_id': backtest.id,
                    'metrics': results
                }
                
        except Exception as e:
            logger.error(f"Testing on {asset} failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def run_improvement_cycle(self) -> Dict[str, Any]:
        """Run a complete improvement cycle"""
        logger.info("🚀 Starting improvement cycle...")
        
        results = {
            'optimizations_run': 0,
            'new_tests': 0,
            'improvements_found': 0,
            'errors': []
        }
        
        try:
            # Get next actions from knowledge base
            actions = self.knowledge.get_next_actions()
            
            for action in actions[:10]:  # Limit to 10 actions per cycle
                try:
                    if action['action'] == 'optimize':
                        result = await self.optimize_strategy(
                            strategy_id=action['strategy_id'],
                            asset='AAPL'  # Default asset for optimization
                        )
                        if result['success']:
                            results['optimizations_run'] += 1
                            if result.get('metrics', {}).get('sharpe_ratio', 0) > 1.0:
                                results['improvements_found'] += 1
                    
                    elif action['action'] == 'backtest':
                        result = await self.test_on_new_asset(
                            strategy_id=action['strategy_id'],
                            asset=action['asset']
                        )
                        if result['success'] and not result.get('existing'):
                            results['new_tests'] += 1
                    
                except Exception as e:
                    logger.error(f"Action failed: {action['action']} - {e}")
                    results['errors'].append(str(e))
            
            logger.info(f"✅ Improvement cycle complete: {results}")
            
        except Exception as e:
            logger.error(f"Improvement cycle failed: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def _get_parameter_grid(self, category: Optional[str]) -> Dict[str, List]:
        """Get parameter grid for optimization based on strategy category"""
        from ..backtesting import (
            MovingAverageCrossStrategy,
            RSIMeanReversionStrategy,
            MomentumStrategy
        )
        
        if category == 'trend_following' or 'moving' in (category or '').lower():
            return {
                'fast_period': [10, 15, 20],
                'slow_period': [40, 50, 60]
            }
        elif category == 'mean_reversion' or 'rsi' in (category or '').lower():
            return {
                'period': [10, 14, 20],
                'oversold': [25, 30, 35],
                'overbought': [65, 70, 75]
            }
        elif category == 'momentum':
            return {
                'period': [10, 15, 20, 25]
            }
        else:
            # Default grid
            return {
                'period': [10, 14, 20]
            }
    
    def _get_strategy_class(self, category: Optional[str]):
        """Get strategy class based on category"""
        from ..backtesting import (
            MovingAverageCrossStrategy,
            RSIMeanReversionStrategy,
            MomentumStrategy
        )
        
        if category == 'trend_following' or 'moving' in (category or '').lower():
            return MovingAverageCrossStrategy
        elif category == 'mean_reversion' or 'rsi' in (category or '').lower():
            return RSIMeanReversionStrategy
        elif category == 'momentum':
            return MomentumStrategy
        else:
            return RSIMeanReversionStrategy  # Default
    
    def _get_strategy_instance(self, category: Optional[str], params: Dict):
        """Get strategy instance with parameters"""
        strategy_class = self._get_strategy_class(category)
        return strategy_class(**params) if params else strategy_class()
