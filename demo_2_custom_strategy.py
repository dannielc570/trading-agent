"""
Demo 2: Create and Test Custom Strategy
Shows how to create your own trading strategy logic
"""
import asyncio
import sys
sys.path.append('.')

from src.data_collection import MarketDataCollector
from src.backtesting import BacktestEngine
from src.backtesting.strategies import StrategyBase
import pandas as pd
import numpy as np

# ============================================================================
# CUSTOM STRATEGY 1: VWAP (Volume Weighted Average Price) Crossover
# ============================================================================
class VWAPStrategy(StrategyBase):
    """
    Custom Strategy: Buy when price crosses above VWAP, sell when below
    VWAP = Volume Weighted Average Price
    """
    
    def __init__(self, window: int = 20):
        super().__init__({'window': window})
        self.window = window
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on VWAP crossover"""
        # Calculate VWAP
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        vwap = (typical_price * data['volume']).rolling(self.window).sum() / \
               data['volume'].rolling(self.window).sum()
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Buy when price crosses above VWAP
        signals[(data['close'] > vwap) & (data['close'].shift(1) <= vwap.shift(1))] = 1
        
        # Sell when price crosses below VWAP
        signals[(data['close'] < vwap) & (data['close'].shift(1) >= vwap.shift(1))] = -1
        
        print(f"   Generated {(signals != 0).sum()} signals using VWAP strategy")
        return signals


# ============================================================================
# CUSTOM STRATEGY 2: Bollinger Bands Bounce
# ============================================================================
class BollingerBounceStrategy(StrategyBase):
    """
    Custom Strategy: Buy when price touches lower band, sell at upper band
    Uses Bollinger Bands for mean reversion
    """
    
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        super().__init__({'period': period, 'std_dev': std_dev})
        self.period = period
        self.std_dev = std_dev
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on Bollinger Bands"""
        # Calculate Bollinger Bands
        sma = data['close'].rolling(self.period).mean()
        std = data['close'].rolling(self.period).std()
        
        upper_band = sma + (std * self.std_dev)
        lower_band = sma - (std * self.std_dev)
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Buy when price touches or goes below lower band
        signals[data['close'] <= lower_band] = 1
        
        # Sell when price touches or goes above upper band
        signals[data['close'] >= upper_band] = -1
        
        # Only signal on new touches, not continuously
        signals = signals.diff().fillna(0)
        signals[signals > 0] = 1
        signals[signals < 0] = -1
        
        print(f"   Generated {(signals != 0).sum()} signals using Bollinger Bands")
        return signals


# ============================================================================
# CUSTOM STRATEGY 3: Multi-Timeframe Momentum
# ============================================================================
class MultiTimeframeMomentumStrategy(StrategyBase):
    """
    Custom Strategy: Combines short-term and long-term momentum
    Only trades when both timeframes agree
    """
    
    def __init__(self, short_period: int = 5, long_period: int = 20, threshold: float = 0.02):
        super().__init__({
            'short_period': short_period,
            'long_period': long_period,
            'threshold': threshold
        })
        self.short_period = short_period
        self.long_period = long_period
        self.threshold = threshold
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on multi-timeframe momentum"""
        # Calculate momentum for both timeframes
        short_momentum = data['close'].pct_change(self.short_period)
        long_momentum = data['close'].pct_change(self.long_period)
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Buy when both momentums are positive and above threshold
        buy_condition = (short_momentum > self.threshold) & (long_momentum > self.threshold)
        signals[buy_condition] = 1
        
        # Sell when both momentums are negative and below -threshold
        sell_condition = (short_momentum < -self.threshold) & (long_momentum < -self.threshold)
        signals[sell_condition] = -1
        
        # Only signal on changes
        signals = signals.diff().fillna(0)
        signals[signals > 0] = 1
        signals[signals < 0] = -1
        
        print(f"   Generated {(signals != 0).sum()} signals using Multi-Timeframe Momentum")
        return signals


# ============================================================================
# TEST ALL CUSTOM STRATEGIES
# ============================================================================
async def main():
    print("\n" + "="*80)
    print("🎨 DEMO 2: TESTING CUSTOM STRATEGIES")
    print("="*80)
    print("\nWe'll test 3 completely custom strategies that you can modify!")
    
    # Fetch data
    print("\n📊 Fetching Apple (AAPL) data...")
    collector = MarketDataCollector()
    data = await collector.fetch_ohlcv("AAPL", "1d", source="yfinance")
    
    if data is None or len(data) < 100:
        print("❌ Could not fetch data")
        return
    
    print(f"✓ Fetched {len(data)} days of data")
    
    # Define custom strategies
    strategies = [
        ("VWAP Crossover", VWAPStrategy(window=20)),
        ("Bollinger Bounce", BollingerBounceStrategy(period=20, std_dev=2.0)),
        ("Multi-TF Momentum", MultiTimeframeMomentumStrategy(short_period=5, long_period=20, threshold=0.03)),
    ]
    
    print("\n" + "="*80)
    print("🔬 TESTING CUSTOM STRATEGIES")
    print("="*80)
    
    engine = BacktestEngine(initial_capital=10000)
    results = []
    
    for name, strategy in strategies:
        print(f"\n⚙️  Testing: {name}...")
        print(f"   Strategy Class: {strategy.__class__.__name__}")
        print(f"   Parameters: {strategy.params}")
        
        signals = strategy.generate_signals(data)
        result = engine.run_backtest(data, signals, name)
        
        if "error" not in result:
            results.append({
                "Strategy": name,
                "Return %": f"{result['total_return']*100:+.2f}%",
                "Sharpe": f"{result['sharpe_ratio']:.2f}",
                "Drawdown": f"{result['max_drawdown']*100:.2f}%",
                "Win Rate": f"{result['win_rate']*100:.1f}%",
                "Trades": result['total_trades'],
                "Final $": f"${result['final_value']:.2f}"
            })
            print(f"   ✓ Return: {result['total_return']*100:+.2f}% | Sharpe: {result['sharpe_ratio']:.2f}")
        else:
            print(f"   ✗ Failed: {result['error']}")
    
    # Display results
    print("\n" + "="*80)
    print("📊 CUSTOM STRATEGIES PERFORMANCE")
    print("="*80)
    
    if results:
        df = pd.DataFrame(results)
        print(df.to_string(index=False))
        
        print("\n🏆 Best Custom Strategy:")
        best = max(results, key=lambda x: float(x['Return %'].rstrip('%')))
        print(f"   {best['Strategy']} - {best['Return %']} return")
    
    print("\n" + "="*80)
    print("✅ Custom Strategy Testing Complete!")
    print("="*80)
    print("\n💡 How to Create Your Own Strategy:")
    print("   1. Create a class that inherits from StrategyBase")
    print("   2. Implement generate_signals(data) method")
    print("   3. Return a pandas Series with signals: 1=buy, -1=sell, 0=hold")
    print("   4. Test it with the BacktestEngine!")
    print("\n   See the code in this file for 3 complete examples.")

if __name__ == "__main__":
    asyncio.run(main())
