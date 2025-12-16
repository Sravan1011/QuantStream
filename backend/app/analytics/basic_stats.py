"""
Basic statistical analytics for price data.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from app.storage.database import db

logger = logging.getLogger(__name__)


async def compute_basic_stats(
    symbol: str,
    timeframe: str = '1m',
    window: int = 20
) -> Dict[str, Any]:
    """
    Compute basic statistics for a symbol.
    
    Args:
        symbol: Trading symbol
        timeframe: OHLC timeframe
        window: Rolling window size
    
    Returns:
        Dictionary with statistics
    """
    try:
        # Try to get recent OHLC data first
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        ohlc_data = await db.get_ohlc(symbol, timeframe, start_time, end_time, limit=500)
        
        # Fallback to tick data if OHLC is insufficient
        if not ohlc_data or len(ohlc_data) < window:
            logger.info(f"No OHLC data for {symbol}, falling back to tick data")
            
            # Get recent ticks
            ticks = await db.get_ticks(symbol, limit=1000)
            
            if not ticks or len(ticks) < window:
                return {'error': 'Insufficient data', 'stats': None}
            
            # Convert ticks to DataFrame and resample manually
            df = pd.DataFrame(ticks)
            # Handle timestamp parsing - try with microseconds first, then without
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
            except:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Use price as close price for tick data
            current_price = df.iloc[-1]['price']
            
            # Rolling statistics on tick prices
            rolling_mean = df['price'].rolling(window=window).mean().iloc[-1]
            rolling_std = df['price'].rolling(window=window).std().iloc[-1]
            
            # Price changes
            price_change = current_price - df.iloc[-2]['price'] if len(df) > 1 else 0
            price_change_pct = (price_change / df.iloc[-2]['price'] * 100) if len(df) > 1 and df.iloc[-2]['price'] > 0 else 0
            
            # Volume statistics
            avg_volume = df['size'].mean()
            current_volume = df.iloc[-1]['size']
            
            # High/Low from recent ticks
            high_24h = df['price'].max()
            low_24h = df['price'].min()
            
            return {
                'symbol': symbol,
                'timeframe': 'tick',
                'timestamp': df.iloc[-1]['timestamp'].isoformat(),
                'current_price': float(current_price),
                'price_change': float(price_change),
                'price_change_pct': float(price_change_pct),
                'rolling_mean': float(rolling_mean),
                'rolling_std': float(rolling_std),
                'high_24h': float(high_24h),
                'low_24h': float(low_24h),
                'avg_volume': float(avg_volume),
                'current_volume': float(current_volume),
                'data_points': len(df),
                'stats': 'computed_from_ticks'
            }
        
        # Use OHLC data if available
        df = pd.DataFrame(ohlc_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Current price
        current_price = df.iloc[-1]['close']
        
        # Rolling statistics
        rolling_mean = df['close'].rolling(window=window).mean().iloc[-1]
        rolling_std = df['close'].rolling(window=window).std().iloc[-1]
        
        # Price changes
        price_change = current_price - df.iloc[-2]['close'] if len(df) > 1 else 0
        price_change_pct = (price_change / df.iloc[-2]['close'] * 100) if len(df) > 1 else 0
        
        # Volume statistics
        avg_volume = df['volume'].mean()
        current_volume = df.iloc[-1]['volume']
        
        # High/Low
        high_24h = df['high'].max()
        low_24h = df['low'].min()
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': df.iloc[-1]['timestamp'].isoformat(),
            'current_price': float(current_price),
            'price_change': float(price_change),
            'price_change_pct': float(price_change_pct),
            'rolling_mean': float(rolling_mean),
            'rolling_std': float(rolling_std),
            'high_24h': float(high_24h),
            'low_24h': float(low_24h),
            'avg_volume': float(avg_volume),
            'current_volume': float(current_volume),
            'data_points': len(df),
            'stats': 'computed_from_ohlc'
        }
    
    except Exception as e:
        logger.error(f"Error computing basic stats for {symbol}: {e}")
        return {'error': str(e), 'stats': None}


async def compute_volatility(
    symbol: str,
    timeframe: str = '1m',
    window: int = 20
) -> Dict[str, Any]:
    """
    Compute volatility metrics.
    
    Args:
        symbol: Trading symbol
        timeframe: OHLC timeframe
        window: Rolling window size
    
    Returns:
        Volatility metrics
    """
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        ohlc_data = await db.get_ohlc(symbol, timeframe, start_time, end_time, limit=500)
        
        if not ohlc_data or len(ohlc_data) < window:
            return {'error': 'Insufficient data'}
        
        df = pd.DataFrame(ohlc_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Calculate returns
        df['returns'] = df['close'].pct_change()
        
        # Historical volatility (annualized)
        # For crypto: 365 days, 24 hours, 60 minutes
        periods_per_year = 365 * 24 * (60 if timeframe.endswith('m') else 1)
        historical_vol = df['returns'].std() * np.sqrt(periods_per_year) * 100
        
        # Rolling volatility
        rolling_vol = df['returns'].rolling(window=window).std().iloc[-1] * np.sqrt(periods_per_year) * 100
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'historical_volatility': float(historical_vol),
            'rolling_volatility': float(rolling_vol),
            'window': window
        }
    
    except Exception as e:
        logger.error(f"Error computing volatility for {symbol}: {e}")
        return {'error': str(e)}
