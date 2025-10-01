"""Alpaca data source for YEARS of 1-minute historical data (FREE!)

Alpaca provides FREE access to years of 1-minute data for:
- All US stocks
- NO rate limits on historical data
- Up to 10,000 bars per request

Sign up FREE at: https://alpaca.markets/
"""
from typing import Optional
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
import os
import asyncio

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class AlpacaDataCollector:
    """
    Alpaca FREE data source for years of 1-minute data
    
    Setup:
    1. Sign up FREE at https://alpaca.markets/
    2. Get API keys (paper trading account is FREE)
    3. Add to .env file:
       ALPACA_API_KEY=your_key
       ALPACA_SECRET_KEY=your_secret
    """
    
    def __init__(self):
        self.api_key = os.getenv('ALPACA_API_KEY', '')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY', '')
        self.base_url = 'https://data.alpaca.markets/v2'
        
        self.available = bool(self.api_key and self.secret_key and REQUESTS_AVAILABLE)
        
        if self.available:
            logger.info("✅ Alpaca data source available (FREE years of 1-min data!)")
        else:
            logger.warning("⚠️  Alpaca not configured. Sign up FREE at https://alpaca.markets/")
    
    async def fetch_bars(
        self,
        symbol: str,
        timeframe: str = '1Min',
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 10000
    ) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV bars from Alpaca
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            timeframe: '1Min', '5Min', '15Min', '1Hour', '1Day'
            start: Start datetime (can go back YEARS!)
            end: End datetime
            limit: Max bars per request (10000 max)
            
        Returns:
            DataFrame with OHLCV data
        """
        if not self.available:
            return None
        
        try:
            # Default date range: 1 year of data!
            if not end:
                end = datetime.now()
            if not start:
                start = end - timedelta(days=365)  # 1 YEAR!
            
            logger.info(f"📊 Fetching Alpaca data for {symbol} ({start.date()} to {end.date()})")
            
            # Alpaca API endpoint
            url = f"{self.base_url}/stocks/{symbol}/bars"
            
            headers = {
                'APCA-API-KEY-ID': self.api_key,
                'APCA-API-SECRET-KEY': self.secret_key
            }
            
            params = {
                'timeframe': timeframe,
                'start': start.isoformat() + 'Z',
                'end': end.isoformat() + 'Z',
                'limit': limit,
                'adjustment': 'all'
            }
            
            # Make request
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Alpaca API error: {response.status_code}")
                return None
            
            data = response.json()
            
            if 'bars' not in data or not data['bars']:
                logger.warning(f"No data returned for {symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(data['bars'])
            
            # Rename columns to standard format
            df = df.rename(columns={
                't': 'timestamp',
                'o': 'open',
                'h': 'high',
                'l': 'low',
                'c': 'close',
                'v': 'volume'
            })
            
            # Convert timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['symbol'] = symbol
            df['timeframe'] = timeframe
            
            logger.success(f"✅ Got {len(df)} bars from Alpaca ({len(df)/(60*6.5):.1f} trading days)")
            
            return df
            
        except Exception as e:
            logger.error(f"Alpaca fetch failed: {e}")
            return None
    
    async def fetch_multi_year_data(
        self,
        symbol: str,
        years: int = 2,
        timeframe: str = '1Min'
    ) -> Optional[pd.DataFrame]:
        """
        Fetch MULTIPLE YEARS of 1-minute data
        
        Args:
            symbol: Stock symbol
            years: How many years of history (1-5 recommended)
            timeframe: Bar size
            
        Returns:
            DataFrame with multiple years of data
        """
        if not self.available:
            logger.warning("Alpaca not configured. Using fallback source.")
            return None
        
        logger.info(f"📊 Fetching {years} YEARS of {timeframe} data for {symbol}...")
        
        all_data = []
        end = datetime.now()
        
        # Fetch in chunks (10000 bars per request)
        # For 1-minute data, 10000 bars = ~25 trading days
        total_chunks = years * 12  # ~12 chunks per year
        
        for chunk in range(total_chunks):
            chunk_end = end - timedelta(days=30 * chunk)
            chunk_start = chunk_end - timedelta(days=30)
            
            df = await self.fetch_bars(
                symbol=symbol,
                timeframe=timeframe,
                start=chunk_start,
                end=chunk_end,
                limit=10000
            )
            
            if df is not None and len(df) > 0:
                all_data.append(df)
                logger.debug(f"  Chunk {chunk+1}/{total_chunks}: {len(df)} bars")
            
            # Rate limiting (be nice to free API)
            await asyncio.sleep(0.5)
        
        if not all_data:
            return None
        
        # Combine all chunks
        combined = pd.concat(all_data, ignore_index=True)
        combined = combined.sort_values('timestamp')
        combined = combined.drop_duplicates(subset=['timestamp'], keep='first')
        
        logger.success(f"✅ Total: {len(combined)} bars ({years} years of {timeframe} data)")
        
        return combined


# Instructions for user
SETUP_INSTRUCTIONS = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║      🎉 GET YEARS OF 1-MINUTE DATA FOR FREE! 🎉                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝


📊 ALPACA DATA - FREE UNLIMITED HISTORICAL DATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Alpaca provides 100% FREE access to:
✅ YEARS of 1-minute historical data
✅ All US stocks (NYSE, NASDAQ, etc.)
✅ Real-time quotes
✅ NO rate limits on historical data
✅ 10,000 bars per request


🚀 SETUP (5 MINUTES):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Go to: https://alpaca.markets/

2. Click "Sign Up" (100% FREE)

3. Choose "Paper Trading" account (FREE, no real money)

4. Get your API keys:
   - Go to Dashboard
   - Click "Generate API Keys"
   - Copy both keys

5. Add to your .env file:
   ALPACA_API_KEY=your_key_here
   ALPACA_SECRET_KEY=your_secret_here

6. Restart your agent


✅ DONE! Now you'll have YEARS of 1-minute data! 🎉


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Example usage:
- 1 year of 1-min data: 98,000+ bars per stock
- 2 years: 196,000+ bars
- 5 years: 490,000+ bars!

Perfect for robust backtesting! 📈
"""
