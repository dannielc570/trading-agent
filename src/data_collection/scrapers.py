"""Web scraping functionality for extracting strategy content"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
from bs4 import BeautifulSoup
import requests
from loguru import logger
from datetime import datetime

from ..config import settings


class StrategyScraperBase(ABC):
    """Base class for strategy scrapers"""
    
    def __init__(self):
        self.headers = {
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
    
    @abstractmethod
    async def scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape content from URL"""
        pass
    
    def extract_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text from BeautifulSoup object"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text


class GenericWebScraper(StrategyScraperBase):
    """Generic web scraper for trading content"""
    
    async def scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape content from a URL
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with scraped content or None if failed
        """
        try:
            logger.info(f"Scraping: {url}")
            
            # Fetch page
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract metadata
            title = self._extract_title(soup)
            content = self.extract_text(soup)
            published_date = self._extract_date(soup)
            
            # Try to identify strategy-related content
            strategy_keywords = self._find_strategy_keywords(content)
            
            result = {
                "url": url,
                "title": title,
                "content": content,
                "raw_html": str(soup)[:10000],  # Limit HTML storage
                "published_date": published_date,
                "scraped_at": datetime.utcnow().isoformat(),
                "strategy_keywords": strategy_keywords,
                "word_count": len(content.split()),
                "source_type": "article"
            }
            
            logger.info(f"Successfully scraped: {title}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Request error scraping {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try multiple selectors
        if soup.title:
            return soup.title.string.strip()
        
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        og_title = soup.find('meta', property='og:title')
        if og_title:
            return og_title.get('content', '').strip()
        
        return "Untitled"
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publication date"""
        # Try common meta tags
        date_selectors = [
            ('meta', {'property': 'article:published_time'}),
            ('meta', {'name': 'publication_date'}),
            ('meta', {'name': 'date'}),
            ('time', {'datetime': True})
        ]
        
        for tag, attrs in date_selectors:
            element = soup.find(tag, attrs)
            if element:
                if tag == 'time':
                    return element.get('datetime')
                return element.get('content')
        
        return None
    
    def _find_strategy_keywords(self, content: str) -> list:
        """Find trading strategy-related keywords in content"""
        keywords = [
            "moving average", "RSI", "MACD", "bollinger bands",
            "fibonacci", "support", "resistance", "breakout",
            "momentum", "reversal", "trend", "scalping",
            "swing trading", "day trading", "backtest",
            "sharpe ratio", "drawdown", "stop loss", "take profit",
            "entry signal", "exit signal", "risk management",
            "position sizing", "portfolio", "algorithm"
        ]
        
        content_lower = content.lower()
        found_keywords = [kw for kw in keywords if kw in content_lower]
        return found_keywords
    
    async def scrape_multiple(self, urls: list) -> list:
        """Scrape multiple URLs concurrently"""
        tasks = [self.scrape(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None and exceptions
        valid_results = []
        for result in results:
            if result and not isinstance(result, Exception):
                valid_results.append(result)
        
        return valid_results


class ForumScraper(StrategyScraperBase):
    """Scraper for trading forums (Reddit, TradingView Ideas, etc.)"""
    
    async def scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape forum content"""
        # TODO: Implement specialized forum scraping
        # This would handle forums like r/algotrading, r/daytrading, etc.
        logger.info(f"Forum scraping not yet implemented for: {url}")
        return None
