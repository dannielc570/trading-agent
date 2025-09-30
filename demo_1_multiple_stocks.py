"""
Demo 1: Test Multiple Stocks
Test the same strategy on different assets (stocks, crypto, etc.)
"""
import asyncio
import sys
sys.path.append('.')

from src.data_collection import MarketDataCollector
from src.backtesting import BacktestEngine
from src.backtesting.strategies import RSIStrategy
import pandas as pd

async def main():
    print("\n" + "="*80)
    print("📊 DEMO 1: TESTING MULTIPLE STOCKS WITH RSI STRATEGY")
    print("="*80)
    
    # Test symbols: stocks and crypto
    symbols = [
        ("AAPL", "Apple Inc.", "yfinance"),
        ("TSLA", "Tesla Inc.", "yfinance"),
        ("GOOGL", "Google (Alphabet)", "yfinance"),
        ("MSFT", "Microsoft", "yfinance"),
        ("BTC-USD", "Bitcoin", "yfinance"),
        ("ETH-USD", "Ethereum", "yfinance"),
    ]
    
    # Use the best strategy from our previous test
    strategy = RSIStrategy(period=14, oversold=30, overbought=70)
    engine = BacktestEngine(initial_capital=10000)
    
    results = []
    
    for symbol, name, source in symbols:
        print(f"\n🔍 Testing {name} ({symbol})...")
        
        try:
            # Fetch data
            collector = MarketDataCollector()
            data = await collector.fetch_ohlcv(symbol, "1d", source=source)
            
            if data is None or len(data) < 50:
                print(f"   ⚠️  Insufficient data for {symbol}")
                continue
            
            print(f"   ✓ Fetched {len(data)} days of data")
            print(f"   Latest price: ${data['close'].iloc[-1]:.2f}")
            
            # Generate signals and backtest
            signals = strategy.generate_signals(data)
            result = engine.run_backtest(data, signals, f"RSI 14 on {symbol}")
            
            if "error" not in result:
                results.append({
                    "Symbol": symbol,
                    "Asset": name,
                    "Days": len(data),
                    "Return %": f"{result['total_return']*100:+.2f}%",
                    "Sharpe": f"{result['sharpe_ratio']:.2f}",
                    "Drawdown": f"{result['max_drawdown']*100:.2f}%",
                    "Win Rate": f"{result['win_rate']*100:.1f}%",
                    "Trades": result['total_trades'],
                    "Final $": f"${result['final_value']:.2f}"
                })
                print(f"   ✓ Return: {result['total_return']*100:+.2f}% | Sharpe: {result['sharpe_ratio']:.2f}")
            else:
                print(f"   ✗ Backtest failed: {result['error']}")
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
            continue
    
    # Display results
    print("\n" + "="*80)
    print("📊 RESULTS COMPARISON - RSI 14 Strategy Across Assets")
    print("="*80)
    
    if results:
        df = pd.DataFrame(results)
        print(df.to_string(index=False))
        
        # Find best performers
        print("\n🏆 TOP PERFORMERS:")
        sorted_by_return = sorted(results, key=lambda x: float(x['Return %'].rstrip('%')), reverse=True)
        for i, r in enumerate(sorted_by_return[:3], 1):
            print(f"   {i}. {r['Asset']:20} ({r['Symbol']:8}) - {r['Return %']:8} return")
        
        print("\n📈 INSIGHTS:")
        avg_return = sum(float(r['Return %'].rstrip('%')) for r in results) / len(results)
        print(f"   • Average Return: {avg_return:+.2f}%")
        print(f"   • Assets Tested: {len(results)}")
        print(f"   • Strategy: RSI 14 (oversold=30, overbought=70)")
        print(f"   • Total Trades: {sum(r['Trades'] for r in results)}")
    
    print("\n" + "="*80)
    print("✅ Multi-Asset Testing Complete!")
    print("="*80)
    print("\n💡 Key Takeaway: The same strategy performs differently on different assets.")
    print("   This helps you find which assets work best with your strategy!")

if __name__ == "__main__":
    asyncio.run(main())
