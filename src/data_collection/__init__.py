"""Data collection module for web scraping and market data"""
from .web_search import WebSearcher
from .scrapers import StrategyScraperBase, GenericWebScraper
from .tradingview import TradingViewScraper
from .market_data import MarketDataCollector
from .minute_data import MinuteDataCollector
from .tradingview_scraper import TradingViewScraper as TVScraper
from .scribd_scraper import ScribdScraper

__all__ = [
    "WebSearcher",
    "StrategyScraperBase",
    "GenericWebScraper",
    "TradingViewScraper",
    "MarketDataCollector",
    "MinuteDataCollector",
    "TVScraper",
    "ScribdScraper",
]
