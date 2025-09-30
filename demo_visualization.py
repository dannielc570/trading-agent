"""Simple demo to visualize platform results"""
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('./data/trading_platform.db')

# Get strategies
print("\n" + "="*60)
print("📊 STRATEGIES IN DATABASE")
print("="*60)
strategies_df = pd.read_sql_query("SELECT * FROM strategies", conn)
print(strategies_df.to_string())

# Get backtests
print("\n" + "="*60)
print("📈 BACKTEST RESULTS")
print("="*60)
backtests_df = pd.read_sql_query("""
    SELECT 
        b.id,
        s.name as strategy_name,
        b.symbol,
        b.timeframe,
        ROUND(b.total_return * 100, 2) as return_pct,
        ROUND(b.sharpe_ratio, 2) as sharpe,
        ROUND(b.max_drawdown * 100, 2) as drawdown_pct,
        ROUND(b.win_rate * 100, 1) as win_rate_pct,
        b.total_trades,
        b.status
    FROM backtests b
    JOIN strategies s ON b.strategy_id = s.id
""", conn)
print(backtests_df.to_string())

# Performance Summary
print("\n" + "="*60)
print("📊 PERFORMANCE SUMMARY")
print("="*60)
if not backtests_df.empty:
    print(f"Total Strategies Tested: {len(strategies_df)}")
    print(f"Total Backtests Run: {len(backtests_df)}")
    print(f"Average Return: {backtests_df['return_pct'].mean():.2f}%")
    print(f"Average Sharpe Ratio: {backtests_df['sharpe'].mean():.2f}")
    print(f"Average Max Drawdown: {backtests_df['drawdown_pct'].mean():.2f}%")
    print(f"Total Trades Executed: {backtests_df['total_trades'].sum()}")
else:
    print("No backtest data available yet")

conn.close()

print("\n" + "="*60)
print("✅ Platform is working! Database populated with test data")
print("="*60)
print("\nNext steps:")
print("1. View more data: sqlite3 ./data/trading_platform.db")
print("2. Start API: uvicorn src.api.main:app --host 0.0.0.0 --port 8000")
print("3. Start Dashboard: streamlit run src/dashboard/app.py")
print("4. Run more tests: python scripts/test_example.py")
