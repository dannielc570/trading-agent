#!/usr/bin/env python3
"""
Check Results - View what the 24/7 agent has discovered

Run this anytime to see the latest results!
"""

import sys
sys.path.insert(0, '/project/workspace')

from src.database.models import SessionLocal, Strategy, Backtest, ScrapedContent
from datetime import datetime

def format_time_ago(dt):
    """Format datetime as 'X hours/days ago'"""
    if not dt:
        return "unknown"
    diff = datetime.utcnow() - dt
    if diff.days > 0:
        return f"{diff.days} days ago"
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours} hours ago"
    minutes = diff.seconds // 60
    return f"{minutes} minutes ago"

def main():
    print("\n" + "="*70)
    print("🤖 24/7 AUTONOMOUS AGENT - CURRENT RESULTS")
    print("="*70)
    
    db = SessionLocal()
    
    try:
        # Get strategies
        strategies = db.query(Strategy).order_by(Strategy.created_at.desc()).all()
        print(f"\n💡 STRATEGIES DISCOVERED: {len(strategies)}")
        print("-"*70)
        
        for i, s in enumerate(strategies[:10], 1):
            time_ago = format_time_ago(s.created_at)
            print(f"{i}. {s.name}")
            print(f"   Category: {s.category} | Created: {time_ago}")
            if s.description:
                desc = s.description[:80] + "..." if len(s.description) > 80 else s.description
                print(f"   {desc}")
        
        if len(strategies) > 10:
            print(f"\n   ... and {len(strategies) - 10} more strategies!")
        
        # Get backtests
        backtests = db.query(Backtest).order_by(Backtest.created_at.desc()).all()
        print(f"\n📈 BACKTESTS COMPLETED: {len(backtests)}")
        print("-"*70)
        
        # Show top 5 by Sharpe ratio
        backtests_with_sharpe = [
            (b, b.metrics.get('sharpe_ratio', -999)) 
            for b in backtests 
            if b.metrics and 'sharpe_ratio' in b.metrics
        ]
        backtests_with_sharpe.sort(key=lambda x: x[1], reverse=True)
        
        print("\n🏆 TOP PERFORMERS (by Sharpe Ratio):")
        for i, (b, sharpe) in enumerate(backtests_with_sharpe[:5], 1):
            total_return = b.metrics.get('total_return', 0)
            win_rate = b.metrics.get('win_rate', 0)
            time_ago = format_time_ago(b.created_at)
            
            print(f"\n{i}. {b.strategy.name} on {b.asset}")
            print(f"   Sharpe: {sharpe:.2f} | Return: {total_return:.2%} | Win Rate: {win_rate:.2%}")
            print(f"   Tested: {time_ago}")
        
        # Recent backtests
        print("\n📊 RECENT BACKTESTS:")
        for i, b in enumerate(backtests[:5], 1):
            if b.metrics:
                sharpe = b.metrics.get('sharpe_ratio', 'N/A')
                returns = b.metrics.get('total_return', 'N/A')
                time_ago = format_time_ago(b.created_at)
                
                print(f"{i}. {b.strategy.name} on {b.asset}")
                if isinstance(sharpe, (int, float)):
                    print(f"   Sharpe: {sharpe:.2f} | Return: {returns:.2%} | {time_ago}")
                else:
                    print(f"   Sharpe: {sharpe} | Return: {returns} | {time_ago}")
        
        # Get scraped content
        content = db.query(ScrapedContent).order_by(ScrapedContent.scraped_at.desc()).all()
        print(f"\n🌐 ARTICLES DISCOVERED: {len(content)}")
        print("-"*70)
        
        for i, c in enumerate(content[:5], 1):
            time_ago = format_time_ago(c.scraped_at)
            print(f"{i}. {c.title[:60]}...")
            print(f"   {time_ago} | {c.url[:50]}...")
        
        # Summary stats
        print("\n" + "="*70)
        print("📊 SUMMARY STATISTICS")
        print("="*70)
        
        if backtests_with_sharpe:
            avg_sharpe = sum(b[1] for b in backtests_with_sharpe) / len(backtests_with_sharpe)
            max_sharpe = backtests_with_sharpe[0][1]
            print(f"Average Sharpe Ratio: {avg_sharpe:.2f}")
            print(f"Best Sharpe Ratio: {max_sharpe:.2f}")
        
        # Unique assets tested
        assets = set(b.asset for b in backtests)
        print(f"Assets Tested: {len(assets)}")
        if assets:
            print(f"Assets: {', '.join(list(assets)[:10])}")
        
        # Categories
        categories = set(s.category for s in strategies if s.category)
        print(f"Strategy Categories: {len(categories)}")
        if categories:
            print(f"Categories: {', '.join(categories)}")
        
        print("\n" + "="*70)
        print("✅ Agent is working! Check back anytime to see new results.")
        print("="*70 + "\n")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
