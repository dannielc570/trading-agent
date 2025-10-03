#!/usr/bin/env python3
"""
Bootstrap initial data for dashboard
Runs ONCE on deployment to populate database with example data
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, '.')
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///data/trading_platform.db')

print("=" * 80)
print("🚀 BOOTSTRAPPING INITIAL DATA FOR DASHBOARD")
print("=" * 80)
print()

from src.database import get_db_context, Strategy, Backtest, ScrapedContent
import json

def bootstrap():
    """Add example data if database is empty"""
    
    with get_db_context() as db:
        # Check if we already have data
        strategy_count = db.query(Strategy).count()
        
        if strategy_count > 0:
            print(f"✅ Database already has {strategy_count} strategies - skipping bootstrap")
            return
        
        print("📊 Database is empty - adding example data...")
        
        # Add example strategies
        strategies = [
            Strategy(
                name="Moving Average Crossover",
                description="Simple moving average crossover strategy using 20/50 day periods",
                category="trend_following",
                parameters={"fast_period": 20, "slow_period": 50},
                status="active",
                created_at=datetime.now() - timedelta(days=7)
            ),
            Strategy(
                name="RSI Mean Reversion",
                description="RSI-based mean reversion strategy with 30/70 thresholds",
                category="mean_reversion",
                parameters={"rsi_period": 14, "oversold": 30, "overbought": 70},
                status="active",
                created_at=datetime.now() - timedelta(days=5)
            ),
            Strategy(
                name="Momentum Breakout",
                description="Momentum-based breakout strategy",
                category="momentum",
                parameters={"lookback": 20, "threshold": 0.02},
                status="active",
                created_at=datetime.now() - timedelta(days=3)
            ),
            Strategy(
                name="Bollinger Bands",
                description="Bollinger Bands mean reversion strategy",
                category="mean_reversion",
                parameters={"period": 20, "std_dev": 2},
                status="testing",
                created_at=datetime.now() - timedelta(days=1)
            ),
        ]
        
        for strategy in strategies:
            db.add(strategy)
        db.commit()
        db.refresh(strategies[0])  # Refresh to get IDs
        
        print(f"✅ Added {len(strategies)} example strategies")
        
        # Add example backtests
        backtests = [
            Backtest(
                strategy_id=strategies[0].id,
                symbol="AAPL",
                timeframe="1d",
                start_date=datetime.now() - timedelta(days=365),
                end_date=datetime.now(),
                initial_capital=10000,
                total_return=0.156,
                sharpe_ratio=1.23,
                max_drawdown=-0.089,
                win_rate=0.58,
                profit_factor=1.45,
                total_trades=47,
                status="completed",
                created_at=datetime.now() - timedelta(days=1)
            ),
            Backtest(
                strategy_id=strategies[1].id,
                symbol="SPY",
                timeframe="1d",
                start_date=datetime.now() - timedelta(days=365),
                end_date=datetime.now(),
                initial_capital=10000,
                total_return=0.089,
                sharpe_ratio=0.87,
                max_drawdown=-0.124,
                win_rate=0.52,
                profit_factor=1.18,
                total_trades=62,
                status="completed",
                created_at=datetime.now() - timedelta(hours=12)
            ),
            Backtest(
                strategy_id=strategies[0].id,
                symbol="QQQ",
                timeframe="1d",
                start_date=datetime.now() - timedelta(days=365),
                end_date=datetime.now(),
                initial_capital=10000,
                total_return=0.203,
                sharpe_ratio=1.56,
                max_drawdown=-0.067,
                win_rate=0.61,
                profit_factor=1.67,
                total_trades=39,
                status="completed",
                created_at=datetime.now() - timedelta(hours=6)
            ),
        ]
        
        for backtest in backtests:
            db.add(backtest)
        db.commit()
        
        print(f"✅ Added {len(backtests)} example backtests")
        
        # Add example scraped content
        content_items = [
            ScrapedContent(
                source_url="https://example.com/strategy1",
                source_type="web_search",
                title="Top 10 Trading Strategies for 2024",
                content="Article about profitable trading strategies...",
                category="strategies",
                processed=True,
                scraped_at=datetime.now() - timedelta(days=2)
            ),
            ScrapedContent(
                source_url="https://example.com/strategy2",
                source_type="web_search",
                title="How to Build a Profitable RSI Strategy",
                content="Guide to RSI-based trading...",
                category="strategies",
                processed=True,
                strategy_created=True,
                scraped_at=datetime.now() - timedelta(days=1)
            ),
        ]
        
        for content in content_items:
            db.add(content)
        db.commit()
        
        print(f"✅ Added {len(content_items)} example scraped articles")
        
        print()
        print("=" * 80)
        print("🎉 BOOTSTRAP COMPLETE!")
        print("=" * 80)
        print()
        print("Dashboard now has:")
        print(f"  - {len(strategies)} strategies")
        print(f"  - {len(backtests)} backtests")
        print(f"  - {len(content_items)} scraped articles")
        print()
        print("✅ Ready for agent to start discovering more!")
        print()

if __name__ == "__main__":
    try:
        bootstrap()
    except Exception as e:
        print(f"❌ Bootstrap failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
