#!/usr/bin/env python3
"""Quick test to verify agent can initialize"""
import sys
sys.path.insert(0, '.')

print("1. Testing database import...")
from src.database import get_db_context
print("✅ Database OK")

print("2. Testing knowledge base...")
from src.research_agent.knowledge_base import KnowledgeBase
kb = KnowledgeBase()
print("✅ KnowledgeBase OK")

print("3. Testing strategy discoverer...")
from src.research_agent.strategy_discoverer import StrategyDiscoverer
sd = StrategyDiscoverer()
print("✅ StrategyDiscoverer OK")

print("4. Testing improvement engine...")
from src.research_agent.improvement_engine import ImprovementEngine
ie = ImprovementEngine()
print("✅ ImprovementEngine OK")

print("5. Testing main agent...")
from src.research_agent.main_agent import ResearchAgent
agent = ResearchAgent()
print("✅ ResearchAgent OK")

print("\n" + "="*50)
print("✅✅✅ ALL TESTS PASSED! ✅✅✅")
print("="*50)
print("Agent is ready to run!")
