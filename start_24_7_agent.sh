#!/bin/bash

# Start the 24/7 Autonomous Agent
# This runs continuously and works every hour

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║          🤖 Starting 24/7 Autonomous Agent 🤖                 ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "The agent will:"
echo "  ✅ Discover new trading strategies"
echo "  ✅ Optimize parameters"
echo "  ✅ Test on multiple assets"
echo "  ✅ Store results in database"
echo "  ✅ Work every hour, forever"
echo ""
echo "Press Ctrl+C to stop (but don't! Let it run!)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd /project/workspace

# Run forever with 1 hour cycle
python3 -c "from src.research_agent import ResearchAgent; ResearchAgent().run_forever(3600)"
