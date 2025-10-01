#!/usr/bin/env python3
"""
Startup script for autonomous research agent
Runs the agent 24/7 on cloud platforms
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.research_agent.main_agent import ResearchAgent
from loguru import logger

async def main():
    """Start the autonomous research agent"""
    logger.info("=" * 80)
    logger.info("🤖 STARTING AUTONOMOUS RESEARCH AGENT")
    logger.info("=" * 80)
    
    try:
        # Initialize agent
        agent = ResearchAgent()
        logger.info("✅ Agent initialized successfully")
        
        # Run forever with 1-hour cycles
        logger.info("🚀 Starting continuous operation (1-hour cycles)")
        await agent.run_forever(cycle_interval=3600)
        
    except KeyboardInterrupt:
        logger.info("🛑 Agent stopped by user")
    except Exception as e:
        logger.error(f"❌ Agent crashed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
