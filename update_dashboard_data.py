#!/usr/bin/env python3
"""
Dashboard data updater - generates dashboard_data.json from database
Runs continuously to keep dashboard updated
"""
import sys
import os
sys.path.insert(0, '.')
os.environ['PYTHONUNBUFFERED'] = '1'

import json
import time
from datetime import datetime

from src.database import get_db_context, Strategy, Backtest, ScrapedContent

def generate_dashboard_data():
    """Generate dashboard data from database"""
    with get_db_context() as db:
        # Get all data
        strategies = db.query(Strategy).order_by(Strategy.created_at.desc()).all()
        backtests = db.query(Backtest).order_by(Backtest.created_at.desc()).all()
        content = db.query(ScrapedContent).order_by(ScrapedContent.scraped_at.desc()).limit(20).all()
        
        # Stats
        total_strategies = len(strategies)
        total_backtests = len(backtests)
        
        sharpes = [b.sharpe_ratio for b in backtests if b.sharpe_ratio]
        best_sharpe = max(sharpes) if sharpes else 0
        avg_sharpe = sum(sharpes)/len(sharpes) if sharpes else 0
        
        # Top backtests
        top = sorted([b for b in backtests if b.sharpe_ratio], 
                    key=lambda x: x.sharpe_ratio, reverse=True)[:10]
        
        return {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stats": {
                "total_strategies": total_strategies,
                "total_backtests": total_backtests,
                "total_content": len(content),
                "best_sharpe": round(best_sharpe, 2),
                "avg_sharpe": round(avg_sharpe, 2)
            },
            "top_backtests": [{
                "rank": i+1,
                "strategy": b.strategy.name,
                "asset": b.symbol,
                "sharpe": round(b.sharpe_ratio, 2),
                "return": round((b.total_return or 0)*100, 2),
                "win_rate": round((b.win_rate or 0)*100, 1),
                "max_drawdown": round((b.max_drawdown or 0)*100, 2),
                "trades": b.total_trades or 0
            } for i, b in enumerate(top)],
            "recent_strategies": [{
                "name": s.name,
                "category": s.category or "N/A",
                "status": s.status,
                "created": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "N/A"
            } for s in strategies[:10]],
            "all_strategies": [{
                "name": s.name,
                "category": s.category or "N/A",
                "created": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "N/A"
            } for s in strategies]
        }

def main():
    """Main update loop"""
    print("🔄 Starting dashboard data updater...", flush=True)
    print("📊 Updates every 2 seconds", flush=True)
    print("📁 Writing to: dashboard_data.json", flush=True)
    
    update_count = 0
    
    try:
        while True:
            update_count += 1
            data = generate_dashboard_data()
            
            # Write to both locations
            for path in ['dashboard_data.json', '/app/dashboard_data.json']:
                try:
                    with open(path, 'w') as f:
                        json.dump(data, f, indent=2)
                except:
                    pass
            
            stats = data['stats']
            print(f"[{data['last_updated']}] Update #{update_count}: "
                  f"📊 {stats['total_strategies']} strategies, "
                  f"🧪 {stats['total_backtests']} backtests, "
                  f"📈 Sharpe: {stats['best_sharpe']:.2f}", flush=True)
            
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("🛑 Dashboard updater stopped", flush=True)
    except Exception as e:
        print(f"❌ Dashboard updater crashed: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
