#!/usr/bin/env python3
"""
Run the agent for one cycle to generate visible results
This will populate the dashboard with data
"""

import sys
import os
import asyncio
from datetime import datetime

sys.path.insert(0, '.')
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///data/trading_platform.db')

print("=" * 80)
print("🚀 RUNNING AGENT CYCLE TO GENERATE DASHBOARD RESULTS")
print("=" * 80)
print(f"Started at: {datetime.now()}")
print()

async def main():
    from src.research_agent.main_agent import ResearchAgent
    from loguru import logger
    
    logger.info("Creating ResearchAgent...")
    agent = ResearchAgent()
    logger.info("✅ Agent created successfully!")
    
    print("\n" + "=" * 80)
    print("🔍 RUNNING ONE COMPLETE AGENT CYCLE")
    print("=" * 80)
    print()
    print("This will:")
    print("1. 🔍 Search for trading strategies on the web")
    print("2. 📊 Analyze and create new strategies")
    print("3. 🎯 Optimize existing strategies")
    print("4. 📈 Run backtests on multiple assets")
    print("5. 💾 Save all results to database")
    print()
    print("⏳ This may take 2-5 minutes...")
    print()
    
    # Run one cycle
    results = await agent.run_cycle()
    
    print("\n" + "=" * 80)
    print("✅ AGENT CYCLE COMPLETE!")
    print("=" * 80)
    print()
    print("Results:")
    for key, value in results.items():
        print(f"  {key}: {value}")
    print()
    print("🎉 Dashboard should now show data!")
    print(f"Visit: https://trading-agent-xu49.onrender.com")
    print()

if __name__ == "__main__":
    asyncio.run(main())
