"""Example script to test the platform"""
import sys
import os
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_collection import WebSearcher, MarketDataCollector
from src.backtesting import BacktestEngine, MovingAverageCrossStrategy
from src.database import init_db, get_db_context, Strategy, Backtest
from datetime import datetime, timedelta


async def main():
    """Run example tests"""
    print("=== Trading Platform Example ===\n")
    
    # Initialize database
    print("1. Initializing database...")
    init_db()
    print("✓ Database initialized\n")
    
    # Test web search
    print("2. Testing web search...")
    searcher = WebSearcher()
    results = await searcher.search_strategies("momentum trading strategy", max_results=5)
    print(f"✓ Found {len(results)} search results")
    if results:
        print(f"   First result: {results[0]['title'][:60]}...\n")
    
    # Test market data
    print("3. Testing market data collection...")
    collector = MarketDataCollector()
    data = await collector.fetch_ohlcv("AAPL", "1d", source="yfinance")
    if data is not None:
        print(f"✓ Fetched {len(data)} bars for AAPL")
        print(f"   Latest close: ${data['close'].iloc[-1]:.2f}\n")
    else:
        print("⚠ Market data fetch failed (yfinance may not be installed)\n")
    
    # Test backtesting
    if data is not None and len(data) > 100:
        print("4. Testing backtest engine...")
        
        # Create strategy
        strategy = MovingAverageCrossStrategy(fast_period=10, slow_period=30)
        signals = strategy.generate_signals(data)
        
        # Run backtest
        engine = BacktestEngine(initial_capital=10000)
        results = engine.run_backtest(data, signals, "MA Cross Test")
        
        if "error" not in results:
            print(f"✓ Backtest completed")
            print(f"   Total Return: {results['total_return']*100:.2f}%")
            print(f"   Sharpe Ratio: {results['sharpe_ratio']:.2f}")
            print(f"   Max Drawdown: {results['max_drawdown']*100:.2f}%")
            print(f"   Total Trades: {results['total_trades']}\n")
        else:
            print(f"⚠ Backtest failed: {results['error']}\n")
    
    # Save to database
    print("5. Saving to database...")
    with get_db_context() as db:
        # Create strategy
        strategy = Strategy(
            name="Moving Average Cross Example",
            description="Simple MA cross strategy for testing",
            category="trend_following",
            parameters={"fast_period": 10, "slow_period": 30},
            status="tested"
        )
        db.add(strategy)
        db.flush()
        
        # Create backtest record if we have results
        if data is not None and 'results' in locals() and "error" not in results:
            backtest = Backtest(
                strategy_id=strategy.id,
                symbol="AAPL",
                timeframe="1d",
                start_date=data['timestamp'].iloc[0],
                end_date=data['timestamp'].iloc[-1],
                initial_capital=10000,
                total_return=results['total_return'],
                sharpe_ratio=results['sharpe_ratio'],
                max_drawdown=results['max_drawdown'],
                win_rate=results['win_rate'],
                total_trades=results['total_trades'],
                status="completed"
            )
            db.add(backtest)
        
        db.commit()
        print("✓ Data saved to database\n")
    
    print("=== Example Complete ===")
    print("\nYou can now:")
    print("1. Start the API: uvicorn src.api.main:app --reload")
    print("2. Start the dashboard: streamlit run src/dashboard/app.py")
    print("3. Start the scheduler: python src/scheduler/main.py")


if __name__ == "__main__":
    asyncio.run(main())
