"""Market data collection from multiple sources"""
from typing import Optional, List
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
import asyncio

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False


class MarketDataCollector:
    """Collect market data from various sources"""
    
    def __init__(self):
        """Initialize market data collector"""
        self.yf_available = YFINANCE_AVAILABLE
        self.ccxt_available = CCXT_AVAILABLE
        
        if CCXT_AVAILABLE:
            self.exchange = ccxt.binance({'enableRateLimit': True})
    
    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source: str = "yfinance"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV data
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe (1m, 5m, 15m, 1h, 1d, etc.)
            start_date: Start date
            end_date: End date
            source: Data source (yfinance, binance, etc.)
            
        Returns:
            DataFrame with OHLCV data
        """
        if source == "yfinance":
            return await self._fetch_yfinance(symbol, timeframe, start_date, end_date)
        elif source == "binance" and self.ccxt_available:
            return await self._fetch_binance(symbol, timeframe, start_date, end_date)
        else:
            logger.error(f"Source '{source}' not available")
            return None
    
    async def _fetch_yfinance(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> Optional[pd.DataFrame]:
        """Fetch data from Yahoo Finance"""
        if not self.yf_available:
            logger.error("yfinance not available")
            return None
        
        try:
            # Map timeframe to yfinance interval
            interval_map = {
                "1m": "1m", "5m": "5m", "15m": "15m",
                "30m": "30m", "1h": "1h", "1d": "1d"
            }
            interval = interval_map.get(timeframe, "1d")
            
            # Default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                if interval == "1m":
                    start_date = end_date - timedelta(days=7)
                else:
                    start_date = end_date - timedelta(days=365)
            
            logger.info(f"Fetching {symbol} data from yfinance ({interval})")
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval
            )
            
            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return None
            
            # Standardize column names
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            df['symbol'] = symbol
            df['timeframe'] = timeframe
            df.reset_index(inplace=True)
            df.rename(columns={'Date': 'timestamp'}, inplace=True)
            
            logger.info(f"Fetched {len(df)} bars for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching yfinance data for {symbol}: {e}")
            return None
    
    async def _fetch_binance(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> Optional[pd.DataFrame]:
        """Fetch data from Binance via CCXT"""
        if not self.ccxt_available:
            logger.error("CCXT not available")
            return None
        
        try:
            # Map timeframe to CCXT format
            timeframe_map = {
                "1m": "1m", "5m": "5m", "15m": "15m",
                "30m": "30m", "1h": "1h", "1d": "1d"
            }
            tf = timeframe_map.get(timeframe, "1d")
            
            logger.info(f"Fetching {symbol} data from Binance ({tf})")
            
            # Fetch OHLCV
            since = int(start_date.timestamp() * 1000) if start_date else None
            ohlcv = self.exchange.fetch_ohlcv(symbol, tf, since=since, limit=1000)
            
            if not ohlcv:
                logger.warning(f"No data returned for {symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['symbol'] = symbol
            df['timeframe'] = timeframe
            
            if end_date:
                df = df[df['timestamp'] <= end_date]
            
            logger.info(f"Fetched {len(df)} bars for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Binance data for {symbol}: {e}")
            return None
    
    async def fetch_multiple_symbols(
        self,
        symbols: List[str],
        timeframe: str = "1d",
        source: str = "yfinance"
    ) -> dict:
        """Fetch data for multiple symbols"""
        tasks = []
        for symbol in symbols:
            tasks.append(self.fetch_ohlcv(symbol, timeframe, source=source))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        output = {}
        for symbol, result in zip(symbols, results):
            if result is not None and not isinstance(result, Exception):
                output[symbol] = result
        
        return output
