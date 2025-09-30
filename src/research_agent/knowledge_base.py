"""Knowledge Base - Tracks what works and what doesn't

This module maintains the platform's knowledge about:
- Which strategies perform well
- Which assets are profitable
- Which parameters work best
- Which indicators add value
- What has been tried and what to try next
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from loguru import logger

from ..database import get_db_context, Strategy, Backtest, OptimizationRun


class KnowledgeBase:
    """Maintains and queries platform knowledge"""
    
    def __init__(self):
        self.min_trades = 3  # Minimum trades to consider results valid
        self.min_sharpe = 0.5  # Minimum Sharpe ratio to consider "good"
        
    def get_best_strategies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing strategies"""
        with get_db_context() as db:
            results = db.query(
                Strategy.id,
                Strategy.name,
                Strategy.category,
                func.avg(Backtest.sharpe_ratio).label('avg_sharpe'),
                func.avg(Backtest.total_return).label('avg_return'),
                func.count(Backtest.id).label('test_count')
            ).join(
                Backtest, Strategy.id == Backtest.strategy_id
            ).filter(
                Backtest.status == 'completed',
                Backtest.total_trades >= self.min_trades
            ).group_by(
                Strategy.id
            ).order_by(
                desc('avg_sharpe')
            ).limit(limit).all()
            
            return [
                {
                    'strategy_id': r.id,
                    'name': r.name,
                    'category': r.category,
                    'avg_sharpe': float(r.avg_sharpe or 0),
                    'avg_return': float(r.avg_return or 0),
                    'test_count': r.test_count
                }
                for r in results
            ]
    
    def get_best_assets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get assets that perform well across strategies"""
        with get_db_context() as db:
            results = db.query(
                Backtest.symbol,
                func.avg(Backtest.sharpe_ratio).label('avg_sharpe'),
                func.avg(Backtest.total_return).label('avg_return'),
                func.avg(Backtest.win_rate).label('avg_win_rate'),
                func.count(Backtest.id).label('test_count')
            ).filter(
                Backtest.status == 'completed',
                Backtest.total_trades >= self.min_trades
            ).group_by(
                Backtest.symbol
            ).order_by(
                desc('avg_sharpe')
            ).limit(limit).all()
            
            return [
                {
                    'symbol': r.symbol,
                    'avg_sharpe': float(r.avg_sharpe or 0),
                    'avg_return': float(r.avg_return or 0),
                    'avg_win_rate': float(r.avg_win_rate or 0),
                    'test_count': r.test_count
                }
                for r in results
            ]
    
    def get_optimization_insights(self) -> Dict[str, Any]:
        """Get insights from optimization runs"""
        with get_db_context() as db:
            total_runs = db.query(OptimizationRun).count()
            completed_runs = db.query(OptimizationRun).filter(
                OptimizationRun.status == 'completed'
            ).count()
            
            best_runs = db.query(OptimizationRun).filter(
                OptimizationRun.status == 'completed',
                OptimizationRun.best_sharpe.isnot(None)
            ).order_by(
                desc(OptimizationRun.best_sharpe)
            ).limit(5).all()
            
            return {
                'total_optimizations': total_runs,
                'completed_optimizations': completed_runs,
                'best_results': [
                    {
                        'strategy_id': r.strategy_id,
                        'best_params': r.best_params,
                        'best_sharpe': float(r.best_sharpe or 0),
                        'improvement_pct': float(r.improvement_pct or 0)
                    }
                    for r in best_runs
                ]
            }
    
    def get_untested_combinations(self) -> List[Dict[str, Any]]:
        """Find strategy-asset combinations not yet tested"""
        with get_db_context() as db:
            # Get all strategies and assets
            strategies = db.query(Strategy).all()
            
            # Get tested symbols
            tested_symbols = set([
                b.symbol for b in db.query(Backtest.symbol).distinct()
            ])
            
            # Suggest new asset classes to test
            suggested_assets = [
                'SPY', 'QQQ', 'IWM',  # US Market ETFs
                'GLD', 'SLV',  # Commodities
                'BTC-USD', 'ETH-USD',  # Crypto
                'EURUSD=X', 'JPY=X',  # Forex
                'NVDA', 'AMD', 'INTC',  # Tech stocks
                'JPM', 'BAC', 'GS',  # Financials
            ]
            
            untested = []
            for strategy in strategies:
                for asset in suggested_assets:
                    if asset not in tested_symbols:
                        untested.append({
                            'strategy_id': strategy.id,
                            'strategy_name': strategy.name,
                            'asset': asset,
                            'priority': 'high' if 'BTC' in asset or 'ETH' in asset else 'medium'
                        })
            
            return untested[:20]  # Return top 20 suggestions
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall platform performance summary"""
        with get_db_context() as db:
            total_strategies = db.query(Strategy).count()
            total_backtests = db.query(Backtest).filter(
                Backtest.status == 'completed'
            ).count()
            
            # Calculate average metrics
            avg_metrics = db.query(
                func.avg(Backtest.sharpe_ratio).label('avg_sharpe'),
                func.avg(Backtest.total_return).label('avg_return'),
                func.avg(Backtest.win_rate).label('avg_win_rate'),
                func.max(Backtest.sharpe_ratio).label('max_sharpe'),
                func.max(Backtest.total_return).label('max_return')
            ).filter(
                Backtest.status == 'completed',
                Backtest.total_trades >= self.min_trades
            ).first()
            
            # Find best overall backtest
            best_backtest = db.query(Backtest).filter(
                Backtest.status == 'completed',
                Backtest.sharpe_ratio.isnot(None)
            ).order_by(
                desc(Backtest.sharpe_ratio)
            ).first()
            
            return {
                'total_strategies': total_strategies,
                'total_backtests': total_backtests,
                'avg_sharpe': float(avg_metrics.avg_sharpe or 0),
                'avg_return': float(avg_metrics.avg_return or 0),
                'avg_win_rate': float(avg_metrics.avg_win_rate or 0),
                'max_sharpe': float(avg_metrics.max_sharpe or 0),
                'max_return': float(avg_metrics.max_return or 0),
                'best_backtest': {
                    'symbol': best_backtest.symbol if best_backtest else None,
                    'sharpe': float(best_backtest.sharpe_ratio) if best_backtest else 0,
                    'return': float(best_backtest.total_return) if best_backtest else 0
                } if best_backtest else None
            }
    
    def needs_optimization(self, strategy_id: int) -> bool:
        """Check if a strategy needs parameter optimization"""
        with get_db_context() as db:
            # Check when last optimized
            last_opt = db.query(OptimizationRun).filter(
                OptimizationRun.strategy_id == strategy_id,
                OptimizationRun.status == 'completed'
            ).order_by(
                desc(OptimizationRun.created_at)
            ).first()
            
            if not last_opt:
                return True  # Never optimized
            
            # Check if it's been more than 7 days
            days_since = (datetime.utcnow() - last_opt.created_at).days
            if days_since > 7:
                return True
            
            # Check if performance is below average
            avg_sharpe = db.query(
                func.avg(Backtest.sharpe_ratio)
            ).filter(
                Backtest.strategy_id == strategy_id,
                Backtest.status == 'completed'
            ).scalar()
            
            if avg_sharpe and avg_sharpe < self.min_sharpe:
                return True
            
            return False
    
    def get_next_actions(self) -> List[Dict[str, Any]]:
        """Recommend next actions for the research agent"""
        actions = []
        
        with get_db_context() as db:
            # 1. Strategies that need optimization
            strategies = db.query(Strategy).all()
            for strategy in strategies[:5]:  # Check top 5
                if self.needs_optimization(strategy.id):
                    actions.append({
                        'action': 'optimize',
                        'target': strategy.name,
                        'strategy_id': strategy.id,
                        'priority': 'high',
                        'reason': 'Strategy needs parameter optimization'
                    })
            
            # 2. Untested asset-strategy combinations
            untested = self.get_untested_combinations()
            for combo in untested[:5]:
                actions.append({
                    'action': 'backtest',
                    'target': f"{combo['strategy_name']} on {combo['asset']}",
                    'strategy_id': combo['strategy_id'],
                    'asset': combo['asset'],
                    'priority': combo['priority'],
                    'reason': 'Untested combination'
                })
            
            # 3. Search for new strategies
            actions.append({
                'action': 'search',
                'target': 'New trading strategies',
                'priority': 'medium',
                'reason': 'Continuous knowledge expansion'
            })
        
        return actions
    
    def log_insight(self, insight: str, category: str = 'general'):
        """Log an insight discovered by the agent"""
        logger.info(f"[{category}] INSIGHT: {insight}")
        # Could also store in database for future reference
