"""Strategy Discoverer - Automatically finds and creates new trading strategies

This module:
- Searches the web for trading strategies
- Analyzes scraped content for strategy patterns
- Automatically creates new strategy implementations
- Adds new indicators and techniques
"""

from typing import List, Dict, Any, Optional
from loguru import logger
import re

from ..database import get_db_context, Strategy, ScrapedContent
from ..data_collection import WebSearcher, GenericWebScraper
# TVScraper and ScribdScraper imported lazily in properties to avoid hangs
# Note: Strategy classes are not imported here as discoverer only creates database entries


class StrategyDiscoverer:
    """Discovers and creates new trading strategies"""
    
    def __init__(self):
        self.searcher = WebSearcher()
        self.scraper = GenericWebScraper()
        # Lazy load these to avoid import hangs
        self._tv_scraper = None
        self._scribd_scraper = None
    
    @property
    def tv_scraper(self):
        if self._tv_scraper is None:
            from ..data_collection import TVScraper
            self._tv_scraper = TVScraper()
        return self._tv_scraper
    
    @property
    def scribd_scraper(self):
        if self._scribd_scraper is None:
            from ..data_collection import ScribdScraper
            self._scribd_scraper = ScribdScraper()
        return self._scribd_scraper
        
        # Known strategy patterns to detect
        self.strategy_patterns = {
            'moving_average': ['moving average', 'ma cross', 'sma', 'ema', 'golden cross', 'death cross'],
            'rsi': ['rsi', 'relative strength index', 'oversold', 'overbought'],
            'macd': ['macd', 'moving average convergence', 'signal line'],
            'bollinger': ['bollinger bands', 'bb', 'squeeze', 'band bounce'],
            'momentum': ['momentum', 'roc', 'rate of change'],
            'volume': ['volume', 'obv', 'on balance volume', 'vwap'],
            'breakout': ['breakout', 'breakout trading', 'support resistance'],
            'mean_reversion': ['mean reversion', 'revert to mean', 'statistical arbitrage'],
            'trend_following': ['trend following', 'trend trading', 'riding the trend'],
        }
        
        # New indicators to consider adding
        self.new_indicators = [
            'ATR', 'ADX', 'Stochastic', 'CCI', 'Ichimoku',
            'Fibonacci', 'Parabolic SAR', 'Williams %R'
        ]
    
    async def search_for_strategies(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search the web, TradingView, and Scribd for trading strategies"""
        logger.info("🔍 Searching for new trading strategies from multiple sources...")
        
        all_results = []
        
        # 1. Search web
        search_queries = [
            "best trading strategies 2024",
            "profitable algorithmic trading strategies",
            "quantitative trading techniques",
            "technical indicators that work",
            "high sharpe ratio strategies",
            "machine learning trading strategies",
        ]
        
        for query in search_queries[:3]:  # Reduced to 3 for faster execution
            try:
                results = self.searcher.search_strategies(query, max_results=3)
                all_results.extend(results)
                logger.info(f"Found {len(results)} results for '{query}'")
            except Exception as e:
                logger.error(f"Search failed for '{query}': {e}")
        
        # 2. Search TradingView
        try:
            logger.info("📈 Scraping TradingView strategies...")
            tv_strategies = await self.tv_scraper.scrape_top_strategies(limit=5)
            all_results.extend(tv_strategies)
            logger.success(f"✅ Found {len(tv_strategies)} strategies from TradingView")
        except Exception as e:
            logger.error(f"TradingView scraping failed: {e}")
        
        # 3. Search Scribd for trading books/strategies
        try:
            logger.info("📚 Scraping Scribd for trading documents...")
            scribd_docs = await self.scribd_scraper.search_trading_documents(limit=5)
            scribd_strategies = await self.scribd_scraper.extract_strategy_concepts(scribd_docs)
            all_results.extend(scribd_strategies)
            logger.success(f"✅ Found {len(scribd_strategies)} strategy concepts from Scribd")
        except Exception as e:
            logger.error(f"Scribd scraping failed: {e}")
        
        logger.success(f"🎯 Total strategies found: {len(all_results)}")
        return all_results[:max_results]
    
    def analyze_content_for_strategies(self, content: str) -> Dict[str, Any]:
        """Analyze scraped content to identify strategy types"""
        content_lower = content.lower()
        
        detected_strategies = []
        detected_indicators = []
        
        # Check for strategy patterns
        for strategy_type, keywords in self.strategy_patterns.items():
            for keyword in keywords:
                if keyword in content_lower:
                    if strategy_type not in detected_strategies:
                        detected_strategies.append(strategy_type)
                    break
        
        # Check for indicators
        for indicator in self.new_indicators:
            if indicator.lower() in content_lower:
                detected_indicators.append(indicator)
        
        # Extract parameter mentions
        parameters = self._extract_parameters(content)
        
        return {
            'strategies': detected_strategies,
            'indicators': detected_indicators,
            'parameters': parameters,
            'complexity': 'high' if len(detected_strategies) > 2 else 'medium' if detected_strategies else 'low'
        }
    
    def _extract_parameters(self, content: str) -> Dict[str, Any]:
        """Extract numerical parameters from content"""
        parameters = {}
        
        # Look for common parameter patterns
        period_match = re.search(r'(\d+)[-\s]*(day|period|bar)', content.lower())
        if period_match:
            parameters['period'] = int(period_match.group(1))
        
        # Look for RSI levels
        rsi_match = re.search(r'rsi.*?(\d+)', content.lower())
        if rsi_match:
            parameters['rsi_threshold'] = int(rsi_match.group(1))
        
        # Look for moving average combinations
        ma_match = re.findall(r'(\d+)[-\s]*(?:and|/)[-\s]*(\d+)', content.lower())
        if ma_match:
            parameters['ma_fast'] = int(ma_match[0][0])
            parameters['ma_slow'] = int(ma_match[0][1])
        
        return parameters
    
    def create_strategy_from_content(self, analysis: Dict[str, Any], 
                                     source_url: str,
                                     title: str) -> Optional[int]:
        """Create a new strategy in the database from analyzed content"""
        
        if not analysis['strategies']:
            return None
        
        # Determine primary strategy type
        primary_type = analysis['strategies'][0]
        
        # Generate strategy name
        strategy_name = f"Auto-discovered: {primary_type.replace('_', ' ').title()}"
        if analysis['indicators']:
            strategy_name += f" + {analysis['indicators'][0]}"
        
        # Create strategy description
        description = f"Automatically discovered strategy based on {primary_type}. "
        if analysis['indicators']:
            description += f"Uses indicators: {', '.join(analysis['indicators'])}. "
        if analysis['parameters']:
            description += f"Suggested parameters: {analysis['parameters']}. "
        
        # Save to database
        with get_db_context() as db:
            # Check if similar strategy already exists
            existing = db.query(Strategy).filter(
                Strategy.name == strategy_name
            ).first()
            
            if existing:
                logger.info(f"Strategy '{strategy_name}' already exists")
                return existing.id
            
            # Create new strategy
            strategy = Strategy(
                name=strategy_name,
                description=description,
                source_url=source_url,
                category=primary_type,
                parameters=analysis['parameters'],
                status='discovered'
            )
            
            db.add(strategy)
            db.commit()
            db.refresh(strategy)
            
            logger.info(f"✅ Created new strategy: {strategy_name} (ID: {strategy.id})")
            return strategy.id
    
    def process_scraped_content(self) -> List[int]:
        """Process unprocessed scraped content to find strategies"""
        logger.info("📊 Processing scraped content for strategies...")
        
        created_strategy_ids = []
        
        with get_db_context() as db:
            # Get unprocessed content
            unprocessed = db.query(ScrapedContent).filter(
                ScrapedContent.processed == False,
                ScrapedContent.content.isnot(None)
            ).limit(10).all()
            
            for content_item in unprocessed:
                try:
                    # Analyze content
                    analysis = self.analyze_content_for_strategies(
                        content_item.content or ""
                    )
                    
                    # Create strategy if found
                    if analysis['strategies']:
                        strategy_id = self.create_strategy_from_content(
                            analysis,
                            content_item.source_url,
                            content_item.title or "Unknown"
                        )
                        
                        if strategy_id:
                            created_strategy_ids.append(strategy_id)
                            content_item.strategy_created = True
                    
                    # Mark as processed
                    content_item.processed = True
                    db.commit()
                    
                except Exception as e:
                    logger.error(f"Failed to process content {content_item.id}: {e}")
                    db.rollback()
        
        logger.info(f"✅ Created {len(created_strategy_ids)} new strategies from content")
        return created_strategy_ids
    
    def suggest_new_indicators(self) -> List[str]:
        """Suggest new indicators to add based on research"""
        with get_db_context() as db:
            # Get all existing strategies
            strategies = db.query(Strategy).all()
            
            # Count indicator usage
            used_indicators = set()
            for strategy in strategies:
                if strategy.description:
                    for indicator in self.new_indicators:
                        if indicator.lower() in strategy.description.lower():
                            used_indicators.add(indicator)
            
            # Return unused indicators
            unused = [ind for ind in self.new_indicators if ind not in used_indicators]
            return unused[:5]  # Return top 5 suggestions
    
    def suggest_new_asset_classes(self) -> List[str]:
        """Suggest new asset classes to test"""
        asset_suggestions = {
            'crypto': ['BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 'ADA-USD'],
            'commodities': ['GLD', 'SLV', 'USO', 'UNG', 'DBA'],
            'forex': ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X'],
            'etfs': ['SPY', 'QQQ', 'IWM', 'DIA', 'EEM'],
            'sectors': ['XLF', 'XLE', 'XLK', 'XLV', 'XLI'],
        }
        
        # Return a mix from different categories
        suggestions = []
        for category, assets in asset_suggestions.items():
            suggestions.extend(assets[:2])
        
        return suggestions
    
    def run_discovery_cycle(self) -> Dict[str, Any]:
        """Run a complete discovery cycle"""
        logger.info("🚀 Starting strategy discovery cycle...")
        
        results = {
            'searched_urls': 0,
            'processed_content': 0,
            'strategies_created': 0,
            'new_indicators_suggested': 0,
            'new_assets_suggested': 0
        }
        
        try:
            # 1. Search for new strategies
            search_results = self.search_for_strategies(max_results=10)
            results['searched_urls'] = len(search_results)
            
            # Store search results
            with get_db_context() as db:
                for result in search_results:
                    # Check if URL already exists
                    existing = db.query(ScrapedContent).filter(
                        ScrapedContent.source_url == result['url']
                    ).first()
                    
                    if not existing:
                        content_item = ScrapedContent(
                            source_url=result['url'],
                            source_type='web_search',
                            title=result.get('title', 'Unknown'),
                            content=result.get('snippet', ''),
                            processed=False
                        )
                        db.add(content_item)
                
                db.commit()
            
            # 2. Process scraped content
            new_strategy_ids = self.process_scraped_content()
            results['strategies_created'] = len(new_strategy_ids)
            
            # 3. Suggest new indicators and assets
            new_indicators = self.suggest_new_indicators()
            results['new_indicators_suggested'] = len(new_indicators)
            
            new_assets = self.suggest_new_asset_classes()
            results['new_assets_suggested'] = len(new_assets)
            
            logger.info(f"✅ Discovery cycle complete: {results}")
            
        except Exception as e:
            logger.error(f"Discovery cycle failed: {e}")
        
        return results
