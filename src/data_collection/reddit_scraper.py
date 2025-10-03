"""
Reddit Scraper for Trading Strategy Discovery
Scrapes r/algotrading, r/quantfinance, r/wallstreetbets for strategies
"""
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
from duckduckgo_search import DDGS
import re
from datetime import datetime

class RedditScraper:
    """Scrape Reddit for trading strategies and discussions"""
    
    def __init__(self):
        self.subreddits = [
            'algotrading',
            'quantfinance', 
            'algorithmictrading',
            'wallstreetbets',
            'options',
            'daytrading',
            'stocks'
        ]
        self._ddgs = None
    
    @property
    def ddgs(self):
        """Lazy loading for DDGS"""
        if self._ddgs is None:
            self._ddgs = DDGS()
        return self._ddgs
    
    async def scrape_trading_strategies(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape Reddit for trading strategy posts
        
        Args:
            limit: Maximum number of strategies to find
            
        Returns:
            List of strategy dictionaries with name, description, source_url
        """
        logger.info(f"🔍 Scraping Reddit for trading strategies (limit: {limit})")
        
        strategies = []
        
        # Search queries for different types of strategies
        search_queries = [
            "site:reddit.com/r/algotrading strategy that works",
            "site:reddit.com/r/quantfinance profitable algorithm",
            "site:reddit.com/r/algorithmictrading backtested strategy",
            "site:reddit.com/r/algotrading python trading bot",
            "site:reddit.com/r/quantfinance mean reversion",
            "site:reddit.com/r/algotrading momentum strategy",
            "site:reddit.com/r/quantfinance pairs trading",
            "site:reddit.com/r/algotrading RSI strategy",
        ]
        
        try:
            for query in search_queries[:6]:  # Limit queries
                try:
                    await asyncio.sleep(1)  # Rate limiting
                    
                    results = list(self.ddgs.text(query, max_results=3))
                    
                    for result in results:
                        if len(strategies) >= limit:
                            break
                        
                        # Extract strategy info
                        strategy = self._parse_reddit_post(result)
                        if strategy and strategy not in strategies:
                            strategies.append(strategy)
                            logger.info(f"📝 Found: {strategy['name']}")
                    
                except Exception as e:
                    logger.warning(f"Search failed for '{query}': {e}")
                    continue
                
                if len(strategies) >= limit:
                    break
        
        except Exception as e:
            logger.error(f"Reddit scraping failed: {e}")
        
        logger.success(f"✅ Found {len(strategies)} strategies from Reddit")
        return strategies
    
    def _parse_reddit_post(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse a Reddit search result into a strategy"""
        try:
            title = result.get('title', '')
            body = result.get('body', '')
            url = result.get('href', '')
            
            # Extract strategy name from title
            strategy_name = self._extract_strategy_name(title)
            
            # Combine title and body for description
            description = f"{title}. {body[:300]}"
            
            # Detect strategy type
            strategy_type = self._detect_strategy_type(title + " " + body)
            
            return {
                'name': strategy_name,
                'description': description,
                'source_url': url,
                'category': 'reddit_discovered',
                'strategy_type': strategy_type,
                'parameters': self._extract_parameters(title + " " + body),
                'code': f"# Strategy from Reddit: {strategy_name}\n# Source: {url}\n# Type: {strategy_type}\n"
            }
            
        except Exception as e:
            logger.debug(f"Failed to parse Reddit post: {e}")
            return None
    
    def _extract_strategy_name(self, title: str) -> str:
        """Extract a clean strategy name from Reddit post title"""
        # Remove common Reddit prefixes
        title = re.sub(r'\[.*?\]', '', title)
        title = re.sub(r'^\s*(Discussion|Question|Help|Strategy):\s*', '', title, flags=re.IGNORECASE)
        
        # Truncate if too long
        if len(title) > 80:
            title = title[:77] + '...'
        
        # Clean up
        title = title.strip()
        if not title:
            title = f"Reddit_Strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return title
    
    def _detect_strategy_type(self, text: str) -> str:
        """Detect the type of strategy from text"""
        text_lower = text.lower()
        
        patterns = {
            'mean_reversion': ['mean reversion', 'revert to mean', 'oversold', 'overbought'],
            'momentum': ['momentum', 'trend following', 'breakout', 'trend'],
            'arbitrage': ['arbitrage', 'pairs trading', 'statistical arbitrage'],
            'machine_learning': ['machine learning', 'neural network', 'ml', 'ai', 'lstm', 'random forest'],
            'options': ['options', 'iron condor', 'butterfly', 'straddle', 'vertical spread'],
            'rsi': ['rsi', 'relative strength'],
            'moving_average': ['moving average', 'ma cross', 'ema', 'sma'],
            'macd': ['macd', 'moving average convergence'],
            'bollinger': ['bollinger', 'bands'],
        }
        
        for strategy_type, keywords in patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                return strategy_type
        
        return 'general'
    
    def _extract_parameters(self, text: str) -> Dict[str, Any]:
        """Extract strategy parameters from text"""
        params = {}
        
        # Look for numbers that might be parameters
        period_match = re.search(r'(\d+)[-\s]*(day|period|bar|minute|hour)', text.lower())
        if period_match:
            params['period'] = int(period_match.group(1))
        
        # RSI thresholds
        rsi_match = re.search(r'rsi.*?(\d+)', text.lower())
        if rsi_match:
            params['rsi_threshold'] = int(rsi_match.group(1))
        
        # Moving averages
        ma_match = re.findall(r'(\d+)[-\s]*(?:and|/)[-\s]*(\d+)[-\s]*(?:ma|ema|sma)', text.lower())
        if ma_match:
            params['ma_fast'] = int(ma_match[0][0])
            params['ma_slow'] = int(ma_match[0][1])
        
        return params
    
    async def search_subreddit_strategies(self, subreddit: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search a specific subreddit for strategies"""
        logger.info(f"🔍 Searching r/{subreddit} for strategies...")
        
        query = f"site:reddit.com/r/{subreddit} trading strategy"
        
        strategies = []
        try:
            results = list(self.ddgs.text(query, max_results=limit))
            
            for result in results:
                strategy = self._parse_reddit_post(result)
                if strategy:
                    strategies.append(strategy)
        
        except Exception as e:
            logger.error(f"Failed to search r/{subreddit}: {e}")
        
        logger.info(f"✅ Found {len(strategies)} strategies from r/{subreddit}")
        return strategies


if __name__ == "__main__":
    # Test the scraper
    async def test():
        scraper = RedditScraper()
        strategies = await scraper.scrape_trading_strategies(limit=10)
        
        print(f"\n✅ Found {len(strategies)} strategies from Reddit:\n")
        for i, strategy in enumerate(strategies, 1):
            print(f"{i}. {strategy['name']}")
            print(f"   Type: {strategy['strategy_type']}")
            print(f"   URL: {strategy['source_url'][:80]}...")
            print()
    
    asyncio.run(test())
