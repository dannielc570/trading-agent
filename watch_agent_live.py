#!/usr/bin/env python3
"""
Live Agent Monitor - See what your agent is doing in real-time!

Just run: python watch_agent_live.py

This will show you live updates every 10 seconds.
"""

import sys
import time
import os
from datetime import datetime

sys.path.insert(0, '/project/workspace')

from src.database import get_db_context, Strategy, Backtest, ScrapedContent

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')

def format_time_ago(dt):
    """Format datetime as 'X hours/days ago'"""
    if not dt:
        return "unknown"
    diff = datetime.utcnow() - dt
    if diff.days > 0:
        return f"{diff.days}d ago"
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours}h ago"
    minutes = diff.seconds // 60
    if minutes > 0:
        return f"{minutes}m ago"
    return "just now"

def get_agent_stats():
    """Get current agent statistics"""
    with get_db_context() as db:
        strategies = db.query(Strategy).order_by(Strategy.created_at.desc()).all()
        backtests = db.query(Backtest).order_by(Backtest.created_at.desc()).all()
        content = db.query(ScrapedContent).order_by(ScrapedContent.scraped_at.desc()).all()
        
        # Get latest items
        latest_strategy = strategies[0] if strategies else None
        latest_backtest = backtests[0] if backtests else None
        latest_content = content[0] if content else None
        
        # Calculate best Sharpe
        best_sharpe = None
        best_strategy = None
        for b in backtests:
            if b.sharpe_ratio is not None:
                if best_sharpe is None or b.sharpe_ratio > best_sharpe:
                    best_sharpe = b.sharpe_ratio
                    best_strategy = b.strategy.name
        
        return {
            'total_strategies': len(strategies),
            'total_backtests': len(backtests),
            'total_content': len(content),
            'latest_strategy': latest_strategy,
            'latest_backtest': latest_backtest,
            'latest_content': latest_content,
            'best_sharpe': best_sharpe,
            'best_strategy': best_strategy,
            'strategies': strategies[:5],
            'backtests': backtests[:5]
        }

def display_dashboard(stats, refresh_count):
    """Display the live dashboard"""
    clear_screen()
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                                                                ║")
    print("║          🤖 LIVE AGENT MONITOR - AUTO-REFRESH 🤖              ║")
    print("║                                                                ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    print(f"⏰ Last updated: {datetime.now().strftime('%H:%M:%S')} (Refresh #{refresh_count})")
    print(f"🔄 Auto-refreshing every 10 seconds... (Press Ctrl+C to stop)")
    print()
    
    print("="*70)
    print("📊 CURRENT TOTALS")
    print("="*70)
    print(f"  Strategies Discovered: {stats['total_strategies']}")
    print(f"  Backtests Completed:   {stats['total_backtests']}")
    print(f"  Articles Scraped:      {stats['total_content']}")
    if stats['best_sharpe']:
        print(f"  Best Sharpe Ratio:     {stats['best_sharpe']:.2f} ({stats['best_strategy']})")
    print()
    
    print("="*70)
    print("🆕 LATEST ACTIVITY")
    print("="*70)
    
    if stats['latest_strategy']:
        time_ago = format_time_ago(stats['latest_strategy'].created_at)
        print(f"  Latest Strategy: {stats['latest_strategy'].name}")
        print(f"                   Created {time_ago}")
    
    if stats['latest_backtest']:
        time_ago = format_time_ago(stats['latest_backtest'].created_at)
        sharpe = stats['latest_backtest'].sharpe_ratio or "N/A"
        print(f"  Latest Backtest: {stats['latest_backtest'].strategy.name} on {stats['latest_backtest'].symbol}")
        print(f"                   Tested {time_ago} | Sharpe: {sharpe}")
    
    if stats['latest_content']:
        time_ago = format_time_ago(stats['latest_content'].scraped_at)
        title = stats['latest_content'].title[:50] + "..." if len(stats['latest_content'].title or "") > 50 else stats['latest_content'].title
        print(f"  Latest Article:  {title}")
        print(f"                   Scraped {time_ago}")
    
    print()
    print("="*70)
    print("💡 RECENT STRATEGIES")
    print("="*70)
    for i, s in enumerate(stats['strategies'], 1):
        time_ago = format_time_ago(s.created_at)
        print(f"  {i}. {s.name} ({time_ago})")
    
    print()
    print("="*70)
    print("📈 RECENT BACKTESTS")
    print("="*70)
    for i, b in enumerate(stats['backtests'], 1):
        sharpe = b.sharpe_ratio if b.sharpe_ratio else "N/A"
        time_ago = format_time_ago(b.created_at)
        print(f"  {i}. {b.strategy.name} on {b.symbol}")
        print(f"      Sharpe: {sharpe} | {time_ago}")
    
    print()
    print("="*70)
    print("🎯 AGENT STATUS: RUNNING 24/7 🚀")
    print("="*70)
    print()

def main():
    """Main monitoring loop"""
    print("\n🤖 Starting Live Agent Monitor...\n")
    print("This will show you what the agent is doing in REAL-TIME!")
    print("Updates every 10 seconds automatically.\n")
    print("Press Ctrl+C to stop watching.\n")
    
    time.sleep(2)
    
    refresh_count = 0
    
    try:
        while True:
            refresh_count += 1
            
            try:
                stats = get_agent_stats()
                display_dashboard(stats, refresh_count)
            except Exception as e:
                print(f"\n⚠️  Error fetching data: {e}")
                print("Retrying in 10 seconds...\n")
            
            # Wait 10 seconds before next refresh
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n👋 Stopped monitoring. Agent is still running in background!\n")
        print("Run this script again anytime to check progress:")
        print("   python watch_agent_live.py\n")

if __name__ == "__main__":
    main()
