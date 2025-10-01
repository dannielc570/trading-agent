"""Enhanced 1-minute data collection from multiple sources"""
from typing import Optional, List
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
import asyncio
import requests

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


class MinuteDataCollector:
    """Specialized collector for 1-minute historical data"""
    
    def __init__(self):
        self.sources_priority = [
            'yfinance',
            'polygon',
            'alpha_vantage',
            'twelve_data'
        ]
    
    async def fetch_1min_data(
        self,
        symbol: str,
        days_back: int = 7,
        source: str = 'auto'
    ) -> Optional[pd.DataFrame]:
        """
        Fetch 1-minute historical data
        
        Args:
            symbol: Trading symbol (e.g., 'AAPL', 'BTC-USD')
            days_back: How many days of history to fetch
            source: Data source ('auto' tries all sources)
            
        Returns:
            DataFrame with 1-minute OHLCV data
        """
        logger.info(f"📊 Fetching 1-minute data for {symbol} ({days_back} days)")
        
        if source == 'auto':
            # Try each source until one works
            for src in self.sources_priority:
                data = await self._fetch_from_source(symbol, days_back, src)
                if data is not None and len(data) > 0:
                    logger.success(f"✅ Got {len(data)} 1-minute bars from {src}")
                    return data
            logger.warning(f"⚠️  No 1-minute data available for {symbol}")
            return None
        else:
            return await self._fetch_from_source(symbol, days_back, source)
    
    async def _fetch_from_source(
        self,
        symbol: str,
        days_back: int,
        source: str
    ) -> Optional[pd.DataFrame]:
        """Fetch from specific source"""
        try:
            if source == 'yfinance':
                return await self._fetch_yfinance(symbol, days_back)
            elif source == 'polygon':
                return await self._fetch_polygon(symbol, days_back)
            elif source == 'alpha_vantage':
                return await self._fetch_alpha_vantage(symbol, days_back)
            elif source == 'twelve_data':
                return await self._fetch_twelve_data(symbol, days_back)
        except Exception as e:
            logger.debug(f"Failed to fetch from {source}: {e}")
            return None
    
    async def _fetch_yfinance(
        self,
        symbol: str,
        days_back: int
    ) -> Optional[pd.DataFrame]:
        """Fetch 1-minute data from Yahoo Finance (up to 7 days)"""
        if not YFINANCE_AVAILABLE:
            return None
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=min(days_back, 7))  # yfinance limit
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval='1m'
            )
            
            if df.empty:
                return None
            
            # Standardize columns
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            df['symbol'] = symbol
            df['timeframe'] = '1m'
            df.reset_index(inplace=True)
            df.rename(columns={'Datetime': 'timestamp'}, inplace=True)
            
            return df
            
        except Exception as e:
            logger.debug(f"yfinance 1m fetch failed: {e}")
            return None
    
    async def _fetch_polygon(
        self,
        symbol: str,
        days_back: int
    ) -> Optional[pd.DataFrame]:
        """Fetch from Polygon.io (free tier: 5 API calls/minute)"""
        # Polygon.io provides free 1-minute data with API key
        # Users can sign up at polygon.io for free tier
        
        # For now, return None (user needs to add API key to .env)
        # Future: implement with API key from environment
        return None
    
    async def _fetch_alpha_vantage(
        self,
        symbol: str,
        days_back: int
    ) -> Optional[pd.DataFrame]:
        """Fetch from Alpha Vantage (free tier: 5 API calls/minute)"""
        # Alpha Vantage provides 1-minute data
        # Users can get free API key from alphavantage.co
        
        # For now, return None (user needs to add API key to .env)
        # Future: implement with API key from environment
        return None
    
    async def _fetch_twelve_data(
        self,
        symbol: str,
        days_back: int
    ) -> Optional[pd.DataFrame]:
        """Fetch from Twelve Data (free tier: 8 API calls/minute)"""
        # Twelve Data provides intraday data
        # Users can get free API key from twelvedata.com
        
        # For now, return None (user needs to add API key to .env)
        # Future: implement with API key from environment
        return None
    
    async def fetch_multiple_assets(
        self,
        symbols: List[str],
        days_back: int = 7
    ) -> dict:
        """
        Fetch 1-minute data for multiple assets
        
        Returns:
            Dict with symbol as key, DataFrame as value
        """
        logger.info(f"📊 Fetching 1-minute data for {len(symbols)} assets")
        
        results = {}
        for symbol in symbols:
            data = await self.fetch_1min_data(symbol, days_back)
            if data is not None:
                results[symbol] = data
                logger.success(f"✅ {symbol}: {len(data)} bars")
            else:
                logger.warning(f"⚠️  {symbol}: No data")
            
            # Rate limiting - wait 1 second between requests
            await asyncio.sleep(1)
        
        logger.info(f"✅ Successfully fetched {len(results)}/{len(symbols)} assets")
        return results
