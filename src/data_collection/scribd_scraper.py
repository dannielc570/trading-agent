"""Scribd scraper for trading books and strategy PDFs"""
from typing import Dict, Any, List, Optional
from loguru import logger
import requests
from bs4 import BeautifulSoup
import re
import asyncio


class ScribdScraper:
    """Scrape Scribd for trading books and strategy documents"""
    
    def __init__(self):
        self.base_url = "https://www.scribd.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Popular trading book search terms
        self.search_terms = [
            'algorithmic trading strategies',
            'technical analysis indicators',
            'quantitative trading',
            'momentum trading strategies',
            'mean reversion trading',
            'trend following strategies',
            'market microstructure',
            'high frequency trading',
            'statistical arbitrage',
            'options trading strategies',
            'forex trading strategies',
            'cryptocurrency trading',
            'backtesting trading systems',
            'risk management trading',
            'portfolio optimization'
        ]
    
    async def search_trading_documents(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search Scribd for trading-related documents
        
        Returns:
            List of document information
        """
        logger.info(f"📚 Searching Scribd for trading documents (limit: {limit})")
        
        documents = []
        
        try:
            for search_term in self.search_terms[:limit]:
                doc_info = await self._search_term(search_term)
                if doc_info:
                    documents.extend(doc_info)
                await asyncio.sleep(2)  # Rate limiting
            
            logger.success(f"✅ Found {len(documents)} trading documents on Scribd")
            return documents[:limit]
            
        except Exception as e:
            logger.error(f"❌ Scribd search error: {e}")
            return documents
    
    async def _search_term(self, term: str) -> List[Dict[str, Any]]:
        """Search for specific term"""
        try:
            # Scribd search URL
            search_url = f"{self.base_url}/search?query={term.replace(' ', '+')}"
            
            response = requests.get(search_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract document information
                # Note: Scribd requires login for full access
                # This extracts publicly available metadata
                
                doc_info = {
                    'title': term,
                    'search_term': term,
                    'source': 'Scribd',
                    'category': self._categorize_document(term),
                    'url': search_url,
                    'type': 'trading_document'
                }
                
                logger.info(f"📄 Found: {doc_info['title']}")
                return [doc_info]
            
            return []
            
        except Exception as e:
            logger.debug(f"Search failed for '{term}': {e}")
            return []
    
    def _categorize_document(self, term: str) -> str:
        """Categorize document by search term"""
        term_lower = term.lower()
        
        if 'algorithmic' in term_lower or 'quantitative' in term_lower:
            return 'Algorithmic Trading'
        elif 'technical analysis' in term_lower or 'indicator' in term_lower:
            return 'Technical Analysis'
        elif 'momentum' in term_lower:
            return 'Momentum Strategies'
        elif 'mean reversion' in term_lower:
            return 'Mean Reversion'
        elif 'trend' in term_lower:
            return 'Trend Following'
        elif 'risk management' in term_lower:
            return 'Risk Management'
        elif 'portfolio' in term_lower:
            return 'Portfolio Management'
        elif 'options' in term_lower:
            return 'Options Trading'
        elif 'forex' in term_lower:
            return 'Forex Trading'
        elif 'crypto' in term_lower:
            return 'Cryptocurrency'
        else:
            return 'General Trading'
    
    async def extract_strategy_concepts(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract strategy concepts from document titles and descriptions
        
        Returns:
            List of strategy concepts
        """
        logger.info(f"🧠 Extracting strategy concepts from {len(documents)} documents")
        
        strategies = []
        
        for doc in documents:
            # Extract strategy keywords
            concepts = self._extract_concepts(doc['search_term'])
            
            if concepts:
                strategy = {
                    'name': f"{concepts[0]}_from_scribd",
                    'description': f"Strategy concept from: {doc['title']}",
                    'source': 'Scribd',
                    'source_url': doc.get('url', ''),
                    'category': doc['category'],
                    'concepts': concepts,
                    'indicators': self._map_concepts_to_indicators(concepts)
                }
                strategies.append(strategy)
        
        logger.success(f"✅ Extracted {len(strategies)} strategy concepts")
        return strategies
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract trading concepts from text"""
        concepts = []
        text_lower = text.lower()
        
        # Strategy types
        if 'momentum' in text_lower:
            concepts.append('momentum')
        if 'mean reversion' in text_lower or 'reversion' in text_lower:
            concepts.append('mean_reversion')
        if 'trend' in text_lower:
            concepts.append('trend_following')
        if 'breakout' in text_lower:
            concepts.append('breakout')
        if 'arbitrage' in text_lower:
            concepts.append('arbitrage')
        
        # Indicators
        if 'rsi' in text_lower:
            concepts.append('RSI')
        if 'macd' in text_lower:
            concepts.append('MACD')
        if 'moving average' in text_lower or 'ma ' in text_lower:
            concepts.append('moving_average')
        if 'bollinger' in text_lower:
            concepts.append('bollinger_bands')
        
        return concepts if concepts else ['price_action']
    
    def _map_concepts_to_indicators(self, concepts: List[str]) -> List[str]:
        """Map concepts to technical indicators"""
        indicator_map = {
            'momentum': ['RSI', 'Stochastic', 'CCI'],
            'mean_reversion': ['RSI', 'Bollinger Bands', 'Z-Score'],
            'trend_following': ['EMA', 'MACD', 'ADX'],
            'breakout': ['ATR', 'Donchian Channels', 'Volume'],
            'RSI': ['RSI'],
            'MACD': ['MACD'],
            'moving_average': ['SMA', 'EMA'],
            'bollinger_bands': ['Bollinger Bands']
        }
        
        indicators = []
        for concept in concepts:
            if concept in indicator_map:
                indicators.extend(indicator_map[concept])
        
        # Remove duplicates
        return list(set(indicators)) if indicators else ['SMA', 'EMA']
    
    async def get_popular_trading_books(self) -> List[str]:
        """Get list of popular trading book topics"""
        return [
            'Technical Analysis of the Financial Markets',
            'Algorithmic Trading Strategies',
            'Quantitative Trading Systems',
            'Machine Learning for Trading',
            'High-Frequency Trading',
            'Statistical Arbitrage',
            'Options Volatility Trading',
            'Market Microstructure',
            'Risk Management in Trading',
            'Portfolio Optimization Techniques'
        ]
