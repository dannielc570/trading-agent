"""Backtesting module for strategy testing"""
from .engine import BacktestEngine
from .fast_engine import FastBacktestEngine
from .strategies import MovingAverageCrossStrategy, RSIStrategy
from .metrics import calculate_metrics

__all__ = [
    "BacktestEngine",
    "FastBacktestEngine",
    "MovingAverageCrossStrategy",
    "RSIStrategy",
    "calculate_metrics",
]
