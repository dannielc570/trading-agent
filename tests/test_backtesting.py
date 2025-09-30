"""Tests for backtesting module"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.backtesting import BacktestEngine, MovingAverageCrossStrategy, RSIStrategy


@pytest.fixture
def sample_data():
    """Generate sample OHLCV data"""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    
    # Generate random walk price data
    returns = np.random.randn(100) * 0.02
    close = 100 * (1 + returns).cumprod()
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close * 0.99,
        'high': close * 1.01,
        'low': close * 0.98,
        'close': close,
        'volume': np.random.randint(1000000, 5000000, 100)
    })
    
    return df


def test_backtest_engine_initialization():
    """Test backtest engine initialization"""
    engine = BacktestEngine(initial_capital=10000, commission=0.001)
    assert engine.initial_capital == 10000
    assert engine.commission == 0.001


def test_moving_average_strategy(sample_data):
    """Test moving average crossover strategy"""
    strategy = MovingAverageCrossStrategy(fast_period=10, slow_period=20)
    signals = strategy.generate_signals(sample_data)
    
    assert len(signals) == len(sample_data)
    assert signals.isin([-1, 0, 1]).all()


def test_rsi_strategy(sample_data):
    """Test RSI strategy"""
    strategy = RSIStrategy(period=14, oversold=30, overbought=70)
    signals = strategy.generate_signals(sample_data)
    
    assert len(signals) == len(sample_data)
    assert signals.isin([-1, 0, 1]).all()


def test_backtest_run(sample_data):
    """Test backtest execution"""
    strategy = MovingAverageCrossStrategy(fast_period=10, slow_period=20)
    signals = strategy.generate_signals(sample_data)
    
    engine = BacktestEngine(initial_capital=10000)
    results = engine.run_backtest(sample_data, signals, "Test Strategy")
    
    assert "error" not in results or results["error"] is None
    assert "total_return" in results
    assert "sharpe_ratio" in results
    assert "max_drawdown" in results
