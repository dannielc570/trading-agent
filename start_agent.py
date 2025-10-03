#!/usr/bin/env python3
"""
Startup script for autonomous research agent
Runs the agent 24/7 on cloud platforms
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80, flush=True)
print("🤖 STARTING AUTONOMOUS RESEARCH AGENT", flush=True)
print("=" * 80, flush=True)

try:
    from src.research_agent.main_agent import ResearchAgent
    from loguru import logger
    print("✅ Imports successful", flush=True)
except Exception as e:
    print(f"❌ IMPORT ERROR: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

async def main():
    """Start the autonomous research agent"""
    try:
        print("Initializing ResearchAgent...", flush=True)
        agent = ResearchAgent()
        print("✅ Agent initialized successfully", flush=True)
        logger.info("✅ Agent initialized successfully")
        
        print("⚡ Starting HIGH-SPEED continuous operation", flush=True)
        print("🔥 Agent will run NON-STOP at maximum speed", flush=True)
        print("📊 Dashboard updates every 5 seconds showing progress", flush=True)
        logger.info("⚡ Starting HIGH-SPEED continuous operation")
        
        await agent.run_forever(cycle_interval=0)  # 0 = NO DELAYS, maximum speed!
        
    except KeyboardInterrupt:
        print("🛑 Agent stopped by user", flush=True)
        logger.info("🛑 Agent stopped by user")
    except Exception as e:
        print(f"❌ Agent crashed: {e}", flush=True)
        traceback.print_exc()
        logger.error(f"❌ Agent crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        print("Starting asyncio event loop...", flush=True)
        asyncio.run(main())
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}", flush=True)
        traceback.print_exc()
        sys.exit(1)
