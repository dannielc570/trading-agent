"""Autonomous Research Agent Module

This module contains the main research agent that continuously:
- Monitors platform performance
- Identifies improvement opportunities
- Automatically adds new strategies, indicators, and assets
- Optimizes parameters based on results
- Integrates new ML techniques
- Learns from outcomes
"""

from .main_agent import ResearchAgent
from .knowledge_base import KnowledgeBase
from .strategy_discoverer import StrategyDiscoverer
from .improvement_engine import ImprovementEngine

__all__ = [
    "ResearchAgent",
    "KnowledgeBase",
    "StrategyDiscoverer",
    "ImprovementEngine",
]
