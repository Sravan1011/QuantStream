"""
OHLC resampling engine for tick data aggregation.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import pandas as pd
import logging

from app.storage.database import db
from app.storage.redis_client import cache
from config import settings

logger = logging.getLogger(__name__)


class ResamplingEngine:
    """Resamples tick data into OHLC candles at different timeframes."""
    
    def __init__(self):
        self.running = False
        self.tasks: List[asyncio.Task] = []
        self.current_candles: Dict[str, Dict[str, Any]] = defaultdict(dict)
    
    def _parse_timeframe(self, timeframe: str) -> timedelta:
        """Convert timeframe string to timedelta."""
        unit = timeframe[-1]
        value = int(timeframe[:-1])
        
        if unit == 's':
            return timedelta(seconds=value)
        elif unit == 'm':
            return timedelta(minutes=value)
        elif unit == 'h':
            return timedelta(hours=value)
        else:
            raise ValueError(f"Invalid timeframe: {timeframe}")
    
    def _get_candle_timestamp(self, timestamp: datetime, timeframe: str) -> datetime:
        """Get the start timestamp for a candle."""
        delta = self._parse_timeframe(timeframe)
        
        # Floor timestamp to candle boundary
        epoch = datetime(1970, 1, 1)
        seconds_since_epoch = (timestamp - epoch).total_seconds()
        candle_seconds = delta.total_seconds()
        floored_seconds = int(seconds_since_epoch / candle_seconds) * candle_seconds
        
        return epoch + timedelta(seconds=floored_seconds)
    
    async def _resample_symbol_timeframe(self, symbol: str, timeframe: str):
        """Resample ticks for a specific symbol and timeframe."""
        delta = self._parse_timeframe(timeframe)
        
        while self.running:
            try:
                # Get recent ticks from cache or database
                ticks = await cache.get_recent_ticks(symbol, count=1000)
                
                if not ticks:
                    # Fallback to database
                    end_time = datetime.utcnow()
                    start_time = end_time - timedelta(hours=1)
                    ticks = await db.get_ticks(symbol, start_time, end_time, limit=1000)
                
                if ticks:
                    # Convert to DataFrame
                    df = pd.DataFrame(ticks)
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df = df.set_index('timestamp')
                    
                    # Resample to OHLC
                    ohlc = df['price'].resample(timeframe).ohlc()
                    volume = df['size'].resample(timeframe).sum()
                    trade_count = df['price'].resample(timeframe).count()
                    
                    # Get the latest complete candle
                    now = datetime.utcnow()
                    complete_candles = ohlc[ohlc.index < self._get_candle_timestamp(now, timeframe)]
                    
                    if not complete_candles.empty:
                        latest = complete_candles.iloc[-1]
                        candle_time = latest.name.to_pydatetime()
                        
                        # Check if this is a new candle
                        key = f"{symbol}_{timeframe}"
                        last_candle_time = self.current_candles[key].get('timestamp')
                        
                        if last_candle_time != candle_time:
                            # New candle - save to database
                            ohlc_data = {
                                'symbol': symbol,
                                'timeframe': timeframe,
                                'timestamp': candle_time,
                                'open': float(latest['open']),
                                'high': float(latest['high']),
                                'low': float(latest['low']),
                                'close': float(latest['close']),
                                'volume': float(volume.loc[candle_time]) if candle_time in volume.index else 0.0,
                                'trade_count': int(trade_count.loc[candle_time]) if candle_time in trade_count.index else 0
                            }
                            
                            await db.insert_ohlc(ohlc_data)
                            self.current_candles[key] = {'timestamp': candle_time}
                            logger.info(f"Created {timeframe} candle for {symbol} at {candle_time}")
            
            except Exception as e:
                logger.error(f"Error resampling {symbol} {timeframe}: {e}")
            
            # Sleep based on timeframe
            await asyncio.sleep(delta.total_seconds())
    
    async def start(self, symbols: List[str]):
        """Start resampling for all symbols and timeframes."""
        if self.running:
            logger.warning("Resampling engine already running")
            return
        
        self.running = True
        logger.info("Starting resampling engine")
        
        # Create tasks for each symbol-timeframe combination
        for symbol in symbols:
            for timeframe in settings.RESAMPLE_INTERVALS:
                task = asyncio.create_task(
                    self._resample_symbol_timeframe(symbol, timeframe)
                )
                self.tasks.append(task)
        
        logger.info(f"Started {len(self.tasks)} resampling tasks")
    
    async def stop(self):
        """Stop resampling engine."""
        if not self.running:
            return
        
        logger.info("Stopping resampling engine")
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()
        logger.info("Resampling engine stopped")


# Global resampling engine instance
resampling_engine = ResamplingEngine()
