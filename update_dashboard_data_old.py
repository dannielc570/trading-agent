#!/usr/bin/env python3
"""
Continuously update dashboard data to JSON file
Run this in the background to feed the live dashboard
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/project/workspace')

from src.database import get_db_context, Strategy, Backtest, ScrapedContent

def get_dashboard_data():
    """Get all dashboard data"""
    with get_db_context() as db:
        # Get strategies
        strategies = db.query(Strategy).order_by(Strategy.created_at.desc()).all()
        
        # Get backtests
        backtests = db.query(Backtest).order_by(Backtest.created_at.desc()).all()
        
        # Get scraped content
        content = db.query(ScrapedContent).order_by(ScrapedContent.scraped_at.desc()).limit(20).all()
        
        # Calculate stats
        total_strategies = len(strategies)
        total_backtests = len(backtests)
        total_content = len(content)
        
        # Best Sharpe
        sharpes = [b.sharpe_ratio for b in backtests if b.sharpe_ratio is not None]
        best_sharpe = max(sharpes) if sharpes else 0
        avg_sharpe = sum(sharpes) / len(sharpes) if sharpes else 0
        
        # Top 10 backtests
        backtests_with_sharpe = [b for b in backtests if b.sharpe_ratio is not None]
        backtests_with_sharpe.sort(key=lambda x: x.sharpe_ratio, reverse=True)
        top_backtests = backtests_with_sharpe[:10]
        
        # Recent strategies (last 10)
        recent_strategies = strategies[:10]
        
        # Build data structure
        data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stats": {
                "total_strategies": total_strategies,
                "total_backtests": total_backtests,
                "total_content": total_content,
                "best_sharpe": round(best_sharpe, 2),
                "avg_sharpe": round(avg_sharpe, 2)
            },
            "top_backtests": [
                {
                    "rank": i + 1,
                    "strategy": b.strategy.name,
                    "asset": b.symbol,
                    "sharpe": round(b.sharpe_ratio, 2),
                    "return": round((b.total_return or 0) * 100, 2),
                    "win_rate": round((b.win_rate or 0) * 100, 1),
                    "max_drawdown": round((b.max_drawdown or 0) * 100, 2),
                    "trades": b.total_trades or 0
                }
                for i, b in enumerate(top_backtests)
            ],
            "recent_strategies": [
                {
                    "name": s.name,
                    "category": s.category or "N/A",
                    "status": s.status,
                    "created": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "N/A"
                }
                for s in recent_strategies
            ],
            "all_strategies": [
                {
                    "name": s.name,
                    "category": s.category or "N/A",
                    "created": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "N/A"
                }
                for s in strategies
            ],
            "recent_content": [
                {
                    "title": c.title or "Untitled",
                    "url": c.source_url,
                    "scraped": c.scraped_at.strftime("%Y-%m-%d %H:%M") if c.scraped_at else "N/A",
                    "processed": c.processed,
                    "strategy_created": c.strategy_created
                }
                for c in content
            ]
        }
        
        return data

def main():
    """Main loop - update every 5 seconds"""
    print("🔄 Starting dashboard data updater...")
    print("📊 Updates every 5 seconds")
    print("📁 Writing to: dashboard_data.json")
    print("Press Ctrl+C to stop\n")
    
    update_count = 0
    
    try:
        while True:
            try:
                # Get fresh data
                data = get_dashboard_data()
                
                # Write to JSON file
                with open('dashboard_data.json', 'w') as f:
                    json.dump(data, f, indent=2)
                
                update_count += 1
                print(f"[{data['last_updated']}] Update #{update_count}: {data['stats']['total_strategies']} strategies, {data['stats']['total_backtests']} backtests")
                
            except Exception as e:
                print(f"Error updating data: {e}")
            
            # Wait 5 seconds
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n👋 Stopped updater.")
        print(f"Total updates: {update_count}\n")

if __name__ == "__main__":
    main()
