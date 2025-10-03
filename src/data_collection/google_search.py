"""
Google Search Integration for Trading Strategy Discovery
Uses DuckDuckGo as a Google alternative (no API key needed)
"""
import asyncio
from typing import List, Dict, Any
from loguru import logger
from duckduckgo_search import DDGS
import re

class GoogleSearchScraper:
    """Search Google (via DuckDuckGo) for trading strategies"""
    
    def __init__(self):
        self._ddgs = None
        
        # Comprehensive search queries
        self.search_queries = [
            # General strategy searches
            "best algorithmic trading strategies 2024",
            "profitable quantitative trading strategies",
            "high frequency trading algorithms",
            "statistical arbitrage strategies",
            
            # Technical analysis
            "RSI trading strategy backtest results",
            "moving average crossover strategy performance",
            "MACD trading strategy examples",
            "bollinger bands trading system",
            "stochastic oscillator strategy",
            
            # Advanced strategies
            "mean reversion trading algorithm",
            "momentum trading strategy python",
            "pairs trading quantitative strategy",
            "market making algorithm",
            "options arbitrage strategy",
            
            # Machine learning
            "machine learning trading strategies",
            "deep learning stock prediction",
            "reinforcement learning trading bot",
            "neural network trading algorithm",
            
            # Crypto
            "crypto trading bot strategy",
            "bitcoin arbitrage algorithm",
            "cryptocurrency market making",
            
            # Academic/Research
            "quantitative trading research papers",
            "algorithmic trading academic studies",
            "backtested trading strategies papers",
        ]
    
    @property
    def ddgs(self):
        """Lazy loading for DDGS"""
        if self._ddgs is None:
            self._ddgs = DDGS()
        return self._ddgs
    
    async def search_trading_strategies(self, max_results: int = 30) -> List[Dict[str, Any]]:
        """
        Search for trading strategies using comprehensive queries
        
        Args:
            max_results: Maximum number of strategies to find
            
        Returns:
            List of strategy dictionaries
        """
        logger.info(f"🔍 Searching Google for trading strategies (max: {max_results})")
        
        strategies = []
        seen_urls = set()
        
        # Rotate through queries
        for query in self.search_queries[:10]:  # Use first 10 queries
            if len(strategies) >= max_results:
                break
            
            try:
                await asyncio.sleep(0.5)  # Rate limiting
                
                logger.info(f"  Searching: {query[:60]}...")
                results = list(self.ddgs.text(query, max_results=5))
                
                for result in results:
                    url = result.get('href', '')
                    
                    # Skip duplicates
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    
                    # Parse result into strategy
                    strategy = self._parse_search_result(result, query)
                    if strategy:
                        strategies.append(strategy)
                        logger.info(f"    📝 Found: {strategy['name'][:60]}...")
                    
                    if len(strategies) >= max_results:
                        break
            
            except Exception as e:
                logger.warning(f"Search failed for '{query[:40]}...': {e}")
                continue
        
        logger.success(f"✅ Found {len(strategies)} strategies from Google search")
        return strategies
    
    def _parse_search_result(self, result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Parse a search result into a strategy dictionary"""
        try:
            title = result.get('title', '')
            snippet = result.get('body', '')
            url = result.get('href', '')
            
            # Extract strategy name from title
            strategy_name = self._clean_strategy_name(title)
            
            # Detect strategy type
            strategy_type = self._detect_strategy_type(title + " " + snippet)
            
            # Extract parameters
            params = self._extract_parameters(title + " " + snippet)
            
            # Build description
            description = f"{title}. {snippet[:400]}"
            
            return {
                'name': strategy_name,
                'description': description,
                'source_url': url,
                'category': 'google_discovered',
                'strategy_type': strategy_type,
                'parameters': params,
                'search_query': query,
                'code': f"# Strategy from Google: {strategy_name}\n# Source: {url}\n# Type: {strategy_type}\n# Query: {query}\n"
            }
        
        except Exception as e:
            logger.debug(f"Failed to parse search result: {e}")
            return None
    
    def _clean_strategy_name(self, title: str) -> str:
        """Clean up strategy name from search result title"""
        # Remove common noise
        title = re.sub(r'\s*[\|\-]\s*.*$', '', title)  # Remove " | Site Name" or " - Site Name"
        title = re.sub(r'\d{4}', '', title)  # Remove years
        title = re.sub(r'[^\w\s\-]', ' ', title)  # Remove special chars except dash
        title = ' '.join(title.split())  # Normalize whitespace
        
        # Truncate if too long
        if len(title) > 80:
            title = title[:77] + '...'
        
        return title.strip() or "Google_Discovery_Strategy"
    
    def _detect_strategy_type(self, text: str) -> str:
        """Detect strategy type from text"""
        text_lower = text.lower()
        
        patterns = {
            'mean_reversion': ['mean reversion', 'revert', 'oversold', 'overbought'],
            'momentum': ['momentum', 'trend following', 'breakout', 'swing'],
            'arbitrage': ['arbitrage', 'pairs trading', 'statistical arb', 'market neutral'],
            'high_frequency': ['hft', 'high frequency', 'latency', 'tick data'],
            'machine_learning': ['machine learning', 'ml', 'neural network', 'deep learning', 'ai'],
            'options': ['options', 'volatility', 'greeks', 'delta', 'gamma'],
            'rsi': ['rsi', 'relative strength index'],
            'moving_average': ['moving average', 'ma cross', 'ema', 'sma'],
            'macd': ['macd', 'moving average convergence divergence'],
            'bollinger': ['bollinger bands', 'bollinger'],
            'stochastic': ['stochastic', 'stoch'],
            'ichimoku': ['ichimoku', 'cloud'],
        }
        
        for strategy_type, keywords in patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                return strategy_type
        
        return 'general'
    
    def _extract_parameters(self, text: str) -> Dict[str, Any]:
        """Extract numerical parameters from text"""
        params = {}
        
        # Period/timeframe
        period_match = re.search(r'(\d+)[-\s]*(day|period|bar|minute|hour|week)', text.lower())
        if period_match:
            params['period'] = int(period_match.group(1))
            params['timeframe'] = period_match.group(2)
        
        # RSI levels
        rsi_match = re.search(r'rsi.*?(\d+)', text.lower())
        if rsi_match:
            params['rsi_threshold'] = int(rsi_match.group(1))
        
        # Moving averages
        ma_match = re.findall(r'(\d+)[-\s]*(?:and|/|,)[-\s]*(\d+)', text.lower())
        if ma_match:
            params['ma_fast'] = int(ma_match[0][0])
            params['ma_slow'] = int(ma_match[0][1])
        
        # Percentage thresholds
        pct_match = re.findall(r'(\d+(?:\.\d+)?)%', text)
        if pct_match:
            params['threshold_pct'] = float(pct_match[0])
        
        return params
    
    async def search_specific_strategy(self, strategy_name: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for a specific strategy by name"""
        logger.info(f"🔍 Searching for specific strategy: {strategy_name}")
        
        query = f"{strategy_name} trading strategy backtest"
        
        strategies = []
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            
            for result in results:
                strategy = self._parse_search_result(result, query)
                if strategy:
                    strategies.append(strategy)
        
        except Exception as e:
            logger.error(f"Search failed for '{strategy_name}': {e}")
        
        return strategies


if __name__ == "__main__":
    # Test the scraper
    async def test():
        scraper = GoogleSearchScraper()
        strategies = await scraper.search_trading_strategies(max_results=15)
        
        print(f"\n✅ Found {len(strategies)} strategies from Google:\n")
        for i, strategy in enumerate(strategies, 1):
            print(f"{i}. {strategy['name']}")
            print(f"   Type: {strategy['strategy_type']}")
            print(f"   Params: {strategy['parameters']}")
            print(f"   URL: {strategy['source_url'][:80]}...")
            print()
    
    asyncio.run(test())
