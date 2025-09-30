"""Demo: Autonomous Research Agent in Action

This script demonstrates the 24/7 autonomous research agent that:
- Evaluates current platform state
- Decides what to do next automatically
- Discovers new strategies from the web
- Optimizes existing strategies
- Tests strategies on new assets
- Learns and improves continuously
"""

import sys
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

from src.research_agent import ResearchAgent

def main():
    print("\n" + "="*70)
    print("🤖 AUTONOMOUS RESEARCH AGENT DEMONSTRATION")
    print("="*70)
    print()
    print("This agent will:")
    print("  1. 📊 Evaluate the current state of the platform")
    print("  2. 🧠 Decide what actions to take next")
    print("  3. 🔍 Search for new trading strategies")
    print("  4. 🎯 Optimize existing strategies")
    print("  5. 📈 Test strategies on new assets")
    print("  6. 💡 Generate insights and learn")
    print()
    print("="*70)
    print()
    
    # Initialize the agent
    print("Initializing Research Agent...")
    agent = ResearchAgent()
    print()
    
    # Show current goals
    print("🎯 AGENT GOALS:")
    for goal, value in agent.goals.items():
        print(f"   • {goal}: {value}")
    print()
    
    # Get initial status
    print("📊 INITIAL STATUS REPORT:")
    status = agent.get_status_report()
    
    performance = status['current_evaluation']['performance']
    print(f"   • Total Strategies: {performance['total_strategies']}")
    print(f"   • Total Backtests: {performance['total_backtests']}")
    print(f"   • Average Sharpe: {performance['avg_sharpe']:.2f}")
    print(f"   • Best Sharpe: {performance['max_sharpe']:.2f}")
    print()
    
    # Show goal progress
    progress = status['current_evaluation']['goal_progress']
    print("📈 GOAL PROGRESS:")
    print(f"   • Strategies: {progress['strategies']['current']}/{progress['strategies']['target']} ({progress['strategies']['progress']:.1f}%)")
    print(f"   • Target Sharpe: {progress['sharpe']['current_best']:.2f}/{progress['sharpe']['target']} ({'✅' if progress['sharpe']['achieved'] else '❌'})")
    print()
    
    # Show next planned actions
    print("🔮 PLANNED ACTIONS:")
    for i, action in enumerate(status['next_actions'][:5], 1):
        print(f"   {i}. [{action['priority'].upper()}] {action['type']}: {action['reason']}")
    print()
    
    print("="*70)
    print("🚀 RUNNING ONE AUTONOMOUS CYCLE...")
    print("="*70)
    print()
    
    # Run one cycle
    results = agent.run_cycle()
    
    # Show results
    print()
    print("="*70)
    print("📊 CYCLE RESULTS")
    print("="*70)
    print()
    
    print(f"✅ Cycle #{results['cycle_number']} completed in {results['duration_seconds']:.1f}s")
    print()
    
    print("⚡ ACTIONS EXECUTED:")
    for i, action_result in enumerate(results['actions_executed'], 1):
        status_icon = "✅" if action_result['success'] else "❌"
        print(f"   {i}. {status_icon} {action_result['action']}")
        if 'details' in action_result:
            for key, value in action_result['details'].items():
                print(f"      • {key}: {value}")
    print()
    
    print("💡 INSIGHTS GENERATED:")
    for i, insight in enumerate(results['insights'], 1):
        print(f"   {i}. {insight}")
    print()
    
    if results['errors']:
        print("⚠️  ERRORS:")
        for error in results['errors']:
            print(f"   • {error}")
        print()
    
    # Show updated status
    print("="*70)
    print("📈 UPDATED PLATFORM STATE")
    print("="*70)
    print()
    
    final_eval = results['evaluation']
    final_perf = final_eval['performance']
    
    print(f"   • Total Strategies: {final_perf['total_strategies']}")
    print(f"   • Total Backtests: {final_perf['total_backtests']}")
    print(f"   • Average Sharpe: {final_perf['avg_sharpe']:.2f}")
    print(f"   • Best Sharpe: {final_perf['max_sharpe']:.2f}")
    print()
    
    # Show agent statistics
    print("🤖 AGENT STATISTICS:")
    print(f"   • Total Cycles Run: {agent.state['cycles_run']}")
    print(f"   • Strategies Added: {agent.state['total_strategies_added']}")
    print(f"   • Tests Run: {agent.state['total_tests_run']}")
    print(f"   • Optimizations: {agent.state['total_optimizations']}")
    print(f"   • Best Sharpe Found: {agent.state['best_sharpe_found']:.2f}")
    print()
    
    print("="*70)
    print("✅ DEMONSTRATION COMPLETE!")
    print("="*70)
    print()
    print("🎯 TO RUN CONTINUOUSLY 24/7:")
    print("   python -c \"from src.research_agent import ResearchAgent; ResearchAgent().run_forever(3600)\"")
    print()
    print("   This will run the agent every hour, continuously:")
    print("   • Discovering new strategies")
    print("   • Optimizing parameters")
    print("   • Testing on new assets")
    print("   • Learning and improving")
    print()
    print("="*70)


if __name__ == "__main__":
    main()
