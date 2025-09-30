"""Pre-built trading strategies for testing"""
import pandas as pd
import numpy as np
from typing import Dict, Any
from loguru import logger


class StrategyBase:
    """Base class for trading strategies"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """Initialize strategy with parameters"""
        self.params = params or {}
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate trading signals from data"""
        raise NotImplementedError


class MovingAverageCrossStrategy(StrategyBase):
    """Simple moving average crossover strategy"""
    
    def __init__(self, fast_period: int = 10, slow_period: int = 50):
        """
        Initialize MA cross strategy
        
        Args:
            fast_period: Fast MA period
            slow_period: Slow MA period
        """
        super().__init__({'fast_period': fast_period, 'slow_period': slow_period})
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate signals based on MA crossover
        
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        try:
            close = data['close']
            
            # Calculate moving averages
            fast_ma = close.rolling(window=self.fast_period).mean()
            slow_ma = close.rolling(window=self.slow_period).mean()
            
            # Generate signals
            signals = pd.Series(0, index=data.index)
            
            # Buy when fast MA crosses above slow MA
            signals[fast_ma > slow_ma] = 1
            
            # Sell when fast MA crosses below slow MA
            signals[fast_ma < slow_ma] = -1
            
            # Only signal on crossover, not continuously
            signals = signals.diff().fillna(0)
            signals[signals > 0] = 1
            signals[signals < 0] = -1
            
            logger.info(f"Generated {(signals != 0).sum()} signals for MA Cross strategy")
            return signals
            
        except Exception as e:
            logger.error(f"Error generating MA Cross signals: {e}")
            return pd.Series(0, index=data.index)


class RSIStrategy(StrategyBase):
    """RSI-based mean reversion strategy"""
    
    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70):
        """
        Initialize RSI strategy
        
        Args:
            period: RSI period
            oversold: Oversold threshold (buy signal)
            overbought: Overbought threshold (sell signal)
        """
        super().__init__({
            'period': period,
            'oversold': oversold,
            'overbought': overbought
        })
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def calculate_rsi(self, data: pd.Series) -> pd.Series:
        """Calculate RSI indicator"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate signals based on RSI
        
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        try:
            close = data['close']
            
            # Calculate RSI
            rsi = self.calculate_rsi(close)
            
            # Generate signals
            signals = pd.Series(0, index=data.index)
            
            # Buy when RSI crosses below oversold level
            signals[(rsi < self.oversold) & (rsi.shift(1) >= self.oversold)] = 1
            
            # Sell when RSI crosses above overbought level
            signals[(rsi > self.overbought) & (rsi.shift(1) <= self.overbought)] = -1
            
            logger.info(f"Generated {(signals != 0).sum()} signals for RSI strategy")
            return signals
            
        except Exception as e:
            logger.error(f"Error generating RSI signals: {e}")
            return pd.Series(0, index=data.index)


class MomentumStrategy(StrategyBase):
    """Momentum-based strategy"""
    
    def __init__(self, lookback: int = 20, threshold: float = 0.02):
        """
        Initialize momentum strategy
        
        Args:
            lookback: Lookback period for returns
            threshold: Momentum threshold for signal
        """
        super().__init__({'lookback': lookback, 'threshold': threshold})
        self.lookback = lookback
        self.threshold = threshold
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on momentum"""
        try:
            close = data['close']
            
            # Calculate momentum
            returns = close.pct_change(self.lookback)
            
            # Generate signals
            signals = pd.Series(0, index=data.index)
            
            # Buy on strong positive momentum
            signals[returns > self.threshold] = 1
            
            # Sell on strong negative momentum
            signals[returns < -self.threshold] = -1
            
            # Only signal on changes
            signals = signals.diff().fillna(0)
            signals[signals > 0] = 1
            signals[signals < 0] = -1
            
            logger.info(f"Generated {(signals != 0).sum()} signals for Momentum strategy")
            return signals
            
        except Exception as e:
            logger.error(f"Error generating Momentum signals: {e}")
            return pd.Series(0, index=data.index)
