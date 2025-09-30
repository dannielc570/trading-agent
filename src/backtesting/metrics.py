"""Performance metrics calculation"""
import pandas as pd
import numpy as np
from typing import Dict, Any


def calculate_metrics(equity_curve: pd.Series, trades: list = None) -> Dict[str, Any]:
    """
    Calculate comprehensive performance metrics
    
    Args:
        equity_curve: Series of portfolio values over time
        trades: Optional list of trade dictionaries
        
    Returns:
        Dictionary with calculated metrics
    """
    try:
        # Returns
        returns = equity_curve.pct_change().dropna()
        total_return = (equity_curve.iloc[-1] - equity_curve.iloc[0]) / equity_curve.iloc[0]
        
        # Annualized metrics (assuming daily data)
        annual_return = (1 + total_return) ** (252 / len(equity_curve)) - 1
        volatility = returns.std() * np.sqrt(252)
        
        # Sharpe ratio (assuming 0% risk-free rate)
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        # Drawdown
        rolling_max = equity_curve.expanding().max()
        drawdown = (equity_curve - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # Calmar ratio
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252)
        sortino_ratio = returns.mean() * np.sqrt(252) / downside_std if downside_std > 0 else 0
        
        # Win rate and profit factor (if trades provided)
        win_rate = 0
        profit_factor = 0
        avg_win = 0
        avg_loss = 0
        
        if trades and len(trades) > 0:
            profits = [t.get('profit', 0) for t in trades if 'profit' in t]
            if profits:
                wins = [p for p in profits if p > 0]
                losses = [p for p in profits if p < 0]
                
                win_rate = len(wins) / len(profits) if profits else 0
                avg_win = np.mean(wins) if wins else 0
                avg_loss = abs(np.mean(losses)) if losses else 0
                
                total_profit = sum(wins)
                total_loss = abs(sum(losses))
                profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        metrics = {
            'total_return': float(total_return),
            'annual_return': float(annual_return),
            'volatility': float(volatility),
            'sharpe_ratio': float(sharpe_ratio),
            'sortino_ratio': float(sortino_ratio),
            'max_drawdown': float(max_drawdown),
            'calmar_ratio': float(calmar_ratio),
            'win_rate': float(win_rate),
            'profit_factor': float(profit_factor),
            'avg_win': float(avg_win),
            'avg_loss': float(avg_loss),
            'total_trades': len(trades) if trades else 0
        }
        
        return metrics
        
    except Exception as e:
        return {'error': str(e)}
