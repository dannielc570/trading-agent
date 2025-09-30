"""
Demo 3: Parameter Optimization
Find the best parameters for a strategy using automated optimization
"""
import asyncio
import sys
sys.path.append('.')

from src.data_collection import MarketDataCollector
from src.backtesting import BacktestEngine
from src.backtesting.strategies import RSIStrategy, MovingAverageCrossStrategy
from src.ml_optimization import StrategyOptimizer
import pandas as pd

# We'll optimize without optuna by doing a simple grid search
def grid_search_optimize(data, strategy_class, param_grid, engine):
    """Simple grid search optimization"""
    from itertools import product
    
    results = []
    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())
    
    total_combinations = 1
    for v in param_values:
        total_combinations *= len(v)
    
    print(f"\n   Testing {total_combinations} parameter combinations...")
    
    for i, combination in enumerate(product(*param_values), 1):
        params = dict(zip(param_names, combination))
        
        # Create strategy with these parameters
        strategy = strategy_class(**params)
        signals = strategy.generate_signals(data)
        result = engine.run_backtest(data, signals, f"Test {i}")
        
        if "error" not in result:
            results.append({
                'params': params,
                'return': result['total_return'],
                'sharpe': result['sharpe_ratio'],
                'drawdown': result['max_drawdown'],
                'trades': result['total_trades']
            })
        
        if i % 10 == 0:
            print(f"   Progress: {i}/{total_combinations} tested...")
    
    return results


async def main():
    print("\n" + "="*80)
    print("🎯 DEMO 3: PARAMETER OPTIMIZATION")
    print("="*80)
    print("\nFinding the best parameters for trading strategies...")
    
    # Fetch data
    print("\n📊 Fetching Apple (AAPL) data...")
    collector = MarketDataCollector()
    data = await collector.fetch_ohlcv("AAPL", "1d", source="yfinance")
    
    if data is None or len(data) < 100:
        print("❌ Could not fetch data")
        return
    
    print(f"✓ Fetched {len(data)} days of data")
    
    engine = BacktestEngine(initial_capital=10000)
    
    # ========================================================================
    # OPTIMIZATION 1: RSI Strategy
    # ========================================================================
    print("\n" + "="*80)
    print("🔧 OPTIMIZATION 1: RSI Strategy Parameters")
    print("="*80)
    print("\nTesting different RSI periods and thresholds...")
    
    rsi_param_grid = {
        'period': [10, 14, 20],
        'oversold': [25, 30, 35],
        'overbought': [65, 70, 75]
    }
    
    rsi_results = grid_search_optimize(data, RSIStrategy, rsi_param_grid, engine)
    
    if rsi_results:
        # Sort by Sharpe ratio
        rsi_results_sorted = sorted(rsi_results, key=lambda x: x['sharpe'], reverse=True)
        
        print("\n🏆 TOP 5 RSI PARAMETER COMBINATIONS:")
        for i, r in enumerate(rsi_results_sorted[:5], 1):
            print(f"   {i}. Period={r['params']['period']}, "
                  f"Oversold={r['params']['oversold']}, "
                  f"Overbought={r['params']['overbought']}")
            print(f"      Return: {r['return']*100:+.2f}% | "
                  f"Sharpe: {r['sharpe']:.2f} | "
                  f"Drawdown: {r['drawdown']*100:.2f}% | "
                  f"Trades: {r['trades']}")
        
        best = rsi_results_sorted[0]
        print(f"\n✨ BEST RSI PARAMETERS:")
        print(f"   • Period: {best['params']['period']}")
        print(f"   • Oversold: {best['params']['oversold']}")
        print(f"   • Overbought: {best['params']['overbought']}")
        print(f"   • Performance: {best['return']*100:+.2f}% return, {best['sharpe']:.2f} Sharpe")
    
    # ========================================================================
    # OPTIMIZATION 2: Moving Average Strategy
    # ========================================================================
    print("\n" + "="*80)
    print("🔧 OPTIMIZATION 2: Moving Average Cross Parameters")
    print("="*80)
    print("\nTesting different MA period combinations...")
    
    ma_param_grid = {
        'fast_period': [5, 10, 15, 20],
        'slow_period': [30, 40, 50, 60]
    }
    
    ma_results = grid_search_optimize(data, MovingAverageCrossStrategy, ma_param_grid, engine)
    
    if ma_results:
        # Sort by return
        ma_results_sorted = sorted(ma_results, key=lambda x: x['return'], reverse=True)
        
        print("\n🏆 TOP 5 MA CROSS PARAMETER COMBINATIONS:")
        for i, r in enumerate(ma_results_sorted[:5], 1):
            print(f"   {i}. Fast={r['params']['fast_period']}, "
                  f"Slow={r['params']['slow_period']}")
            print(f"      Return: {r['return']*100:+.2f}% | "
                  f"Sharpe: {r['sharpe']:.2f} | "
                  f"Drawdown: {r['drawdown']*100:.2f}% | "
                  f"Trades: {r['trades']}")
        
        best_ma = ma_results_sorted[0]
        print(f"\n✨ BEST MA CROSS PARAMETERS:")
        print(f"   • Fast Period: {best_ma['params']['fast_period']}")
        print(f"   • Slow Period: {best_ma['params']['slow_period']}")
        print(f"   • Performance: {best_ma['return']*100:+.2f}% return, {best_ma['sharpe']:.2f} Sharpe")
    
    # ========================================================================
    # COMPARISON
    # ========================================================================
    print("\n" + "="*80)
    print("📊 OPTIMIZATION SUMMARY")
    print("="*80)
    
    if rsi_results and ma_results:
        print("\n🎯 Overall Best Performers:")
        print(f"\n1. RSI Strategy (Optimized):")
        print(f"   Parameters: period={best['params']['period']}, "
              f"oversold={best['params']['oversold']}, "
              f"overbought={best['params']['overbought']}")
        print(f"   Return: {best['return']*100:+.2f}% | Sharpe: {best['sharpe']:.2f}")
        
        print(f"\n2. MA Cross Strategy (Optimized):")
        print(f"   Parameters: fast={best_ma['params']['fast_period']}, "
              f"slow={best_ma['params']['slow_period']}")
        print(f"   Return: {best_ma['return']*100:+.2f}% | Sharpe: {best_ma['sharpe']:.2f}")
        
        print("\n📈 Performance Improvement:")
        # Compare with default parameters
        default_rsi = [r for r in rsi_results if r['params'] == {'period': 14, 'oversold': 30, 'overbought': 70}]
        if default_rsi:
            improvement = ((best['return'] - default_rsi[0]['return']) / abs(default_rsi[0]['return'])) * 100
            print(f"   RSI: {improvement:+.1f}% improvement over default parameters")
    
    print("\n" + "="*80)
    print("✅ Parameter Optimization Complete!")
    print("="*80)
    print("\n💡 Key Insights:")
    print("   • Different parameters can dramatically change strategy performance")
    print("   • Optimization helps find the best settings for your data")
    print("   • Always validate optimized parameters on out-of-sample data")
    print("   • The platform tested", len(rsi_results) + len(ma_results), "combinations automatically!")

if __name__ == "__main__":
    asyncio.run(main())
