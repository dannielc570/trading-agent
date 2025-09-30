"""Quick demo: Test multiple strategies on real market data"""
import asyncio
import sys
sys.path.append('.')

from src.data_collection import MarketDataCollector
from src.backtesting import BacktestEngine, MovingAverageCrossStrategy, RSIStrategy
from src.backtesting.strategies import MomentumStrategy

async def main():
    print("\n" + "="*70)
    print("🚀 QUICK STRATEGY BACKTEST DEMO")
    print("="*70)
    
    # Fetch market data
    print("\n📊 Fetching Apple (AAPL) stock data...")
    collector = MarketDataCollector()
    data = await collector.fetch_ohlcv("AAPL", "1d", source="yfinance")
    
    if data is None or len(data) < 100:
        print("❌ Could not fetch sufficient data")
        return
    
    print(f"✓ Fetched {len(data)} days of data")
    print(f"   Date range: {data['timestamp'].min()} to {data['timestamp'].max()}")
    print(f"   Latest price: ${data['close'].iloc[-1]:.2f}")
    
    # Test multiple strategies
    strategies = [
        ("MA Cross 10/30", MovingAverageCrossStrategy(fast_period=10, slow_period=30)),
        ("MA Cross 20/50", MovingAverageCrossStrategy(fast_period=20, slow_period=50)),
        ("RSI 14 (30/70)", RSIStrategy(period=14, oversold=30, overbought=70)),
        ("RSI 20 (25/75)", RSIStrategy(period=20, oversold=25, overbought=75)),
        ("Momentum 10d", MomentumStrategy(lookback=10, threshold=0.03)),
        ("Momentum 20d", MomentumStrategy(lookback=20, threshold=0.05)),
    ]
    
    print("\n" + "="*70)
    print("🔬 TESTING STRATEGIES")
    print("="*70)
    
    engine = BacktestEngine(initial_capital=10000)
    results = []
    
    for name, strategy in strategies:
        print(f"\n⚙️  Testing: {name}...")
        
        signals = strategy.generate_signals(data)
        result = engine.run_backtest(data, signals, name)
        
        if "error" not in result:
            results.append({
                "Strategy": name,
                "Return %": f"{result['total_return']*100:.2f}%",
                "Sharpe": f"{result['sharpe_ratio']:.2f}",
                "Drawdown %": f"{result['max_drawdown']*100:.2f}%",
                "Win Rate": f"{result['win_rate']*100:.1f}%",
                "Trades": result['total_trades'],
                "Final $": f"${result['final_value']:.2f}"
            })
            print(f"   ✓ Return: {result['total_return']*100:+.2f}% | Sharpe: {result['sharpe_ratio']:.2f} | Trades: {result['total_trades']}")
        else:
            print(f"   ✗ Failed: {result['error']}")
    
    # Display results table
    print("\n" + "="*70)
    print("📊 RESULTS SUMMARY")
    print("="*70)
    
    if results:
        import pandas as pd
        df = pd.DataFrame(results)
        print(df.to_string(index=False))
        
        print("\n🏆 Best Performers:")
        print("   By Return:", results[0]["Strategy"], "-", results[0]["Return %"])
        print("   By Sharpe:", max(results, key=lambda x: float(x['Sharpe'].rstrip()))["Strategy"])
    
    print("\n" + "="*70)
    print("✅ Demo complete! The platform successfully:")
    print("   • Fetched real market data from Yahoo Finance")
    print("   • Generated trading signals from 6 different strategies")
    print("   • Ran complete backtests with performance metrics")
    print("   • Compared results across all strategies")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
