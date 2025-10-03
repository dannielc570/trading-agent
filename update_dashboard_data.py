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
    """Generate dashboard data from database (OPTIMIZED)"""
    with get_db_context() as db:
        # OPTIMIZED: Use COUNT queries instead of loading everything
        total_strategies = db.query(Strategy).count()
        total_backtests = db.query(Backtest).count()
        total_content = db.query(ScrapedContent).count()
        
        # OPTIMIZED: Get only recent strategies (limit 50)
        strategies = db.query(Strategy).order_by(Strategy.created_at.desc()).limit(50).all()
        
        # OPTIMIZED: Get only best backtests with sharpe > -1
        top_backtests = db.query(Backtest).filter(
            Backtest.sharpe_ratio.isnot(None)
        ).order_by(Backtest.sharpe_ratio.desc()).limit(10).all()
        
        # OPTIMIZED: Calculate stats from top backtests only
        if top_backtests:
            best_sharpe = top_backtests[0].sharpe_ratio
            sharpes = [b.sharpe_ratio for b in top_backtests if b.sharpe_ratio]
            avg_sharpe = sum(sharpes) / len(sharpes) if sharpes else 0
        else:
            best_sharpe = 0
            avg_sharpe = 0
        
        return {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stats": {
                "total_strategies": total_strategies,
                "total_backtests": total_backtests,
                "total_content": total_content,
                "best_sharpe": round(best_sharpe, 2),
                "avg_sharpe": round(avg_sharpe, 2)
            },
            "top_backtests": [{
                "rank": i+1,
                "strategy": b.strategy.name if b.strategy else "Unknown",
                "asset": b.symbol,
                "sharpe": round(b.sharpe_ratio, 2),
                "return": round((b.total_return or 0)*100, 2),
                "win_rate": round((b.win_rate or 0)*100, 1),
                "max_drawdown": round((b.max_drawdown or 0)*100, 2),
                "trades": b.total_trades or 0
            } for i, b in enumerate(top_backtests)],
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
