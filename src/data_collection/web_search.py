"""Web search functionality using multiple search engines"""
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from loguru import logger

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None


class WebSearcher:
    """Search the web for trading strategies and content"""
    
    def __init__(self):
        """Initialize web searcher"""
        # Lazy initialization to avoid blocking on init
        self._ddg = None
        self._ddg_available = DDGS is not None
    
    @property
    def ddg(self):
        """Lazy load DDGS only when needed"""
        if self._ddg is None and self._ddg_available:
            try:
                self._ddg = DDGS()
            except Exception as e:
                logger.warning(f"Failed to initialize DDGS: {e}")
                self._ddg_available = False
        return self._ddg
        
    async def search_strategies(
        self,
        query: str = "trading strategies",
        max_results: int = 20,
        region: str = "us-en"
    ) -> List[Dict[str, Any]]:
        """
        Search for trading strategies using DuckDuckGo
        
        Args:
            query: Search query
            max_results: Maximum number of results
            region: Search region
            
        Returns:
            List of search results with title, url, snippet
        """
        if not self.ddg:
            logger.warning("DuckDuckGo search not available. Install duckduckgo-search package.")
            return []
            
        try:
            logger.info(f"Searching for: {query}")
            
            # Perform search
            results = []
            search_results = self.ddg.text(query, region=region, max_results=max_results)
            
            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                    "source": "duckduckgo",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            logger.info(f"Found {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching with DuckDuckGo: {e}")
            return []
    
    async def search_multiple_topics(
        self,
        topics: List[str],
        max_results_per_topic: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for multiple topics in parallel
        
        Args:
            topics: List of search topics
            max_results_per_topic: Max results per topic
            
        Returns:
            Dictionary mapping topic to results
        """
        tasks = []
        for topic in topics:
            tasks.append(self.search_strategies(topic, max_results_per_topic))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        output = {}
        for topic, result in zip(topics, results):
            if isinstance(result, Exception):
                logger.error(f"Error searching topic '{topic}': {result}")
                output[topic] = []
            else:
                output[topic] = result
        
        return output
    
    def get_default_trading_topics(self) -> List[str]:
        """Get default list of trading strategy topics to search"""
        return [
            "algorithmic trading strategies",
            "momentum trading strategy",
            "mean reversion trading",
            "volume profile trading",
            "breakout trading strategies",
            "scalping strategies forex",
            "swing trading techniques",
            "quantitative trading strategies",
            "machine learning trading",
            "crypto trading strategies",
            "day trading strategies",
            "options trading strategies",
            "pair trading strategies",
            "trend following strategies",
            "market making strategies"
        ]
    
    async def comprehensive_search(
        self,
        custom_topics: List[str] = None,
        max_results_per_topic: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform comprehensive search across all trading topics
        
        Args:
            custom_topics: Custom list of topics (uses defaults if None)
            max_results_per_topic: Max results per topic
            
        Returns:
            Flattened list of all search results
        """
        topics = custom_topics or self.get_default_trading_topics()
        
        logger.info(f"Starting comprehensive search for {len(topics)} topics")
        
        results_by_topic = await self.search_multiple_topics(topics, max_results_per_topic)
        
        # Flatten results and deduplicate by URL
        all_results = []
        seen_urls = set()
        
        for topic, results in results_by_topic.items():
            for result in results:
                url = result.get("url")
                if url and url not in seen_urls:
                    result["topic"] = topic
                    all_results.append(result)
                    seen_urls.add(url)
        
        logger.info(f"Comprehensive search complete: {len(all_results)} unique results")
        return all_results


# Convenience function for sync usage
def search_trading_strategies(query: str = "trading strategies", max_results: int = 20):
    """Synchronous wrapper for searching trading strategies"""
    searcher = WebSearcher()
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(searcher.search_strategies(query, max_results))
