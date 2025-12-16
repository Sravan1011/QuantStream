"""
Pairs trading analytics using tick data (fallback when OHLC unavailable).
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime, timedelta
import logging
from sklearn.linear_model import LinearRegression

from app.storage.database import db

logger = logging.getLogger(__name__)


async def compute_spread_from_ticks(
    symbol1: str,
    symbol2: str,
    tick_count: int = 200,
    window: int = 20
) -> Dict[str, Any]:
    """
    Compute hedge ratio, spread, and z-score directly from tick data.
    
    This is a fallback method when OHLC data is not available.
    
    Args:
        symbol1: First symbol (e.g., 'btcusdt')
        symbol2: Second symbol (e.g., 'ethusdt')
        tick_count: Number of recent ticks to use
        window: Rolling window for z-score calculation
    
    Returns:
        Dictionary with spread metrics
    """
    try:
        # Get recent ticks for both symbols
        ticks1 = await db.get_ticks(symbol1, limit=tick_count)
        ticks2 = await db.get_ticks(symbol2, limit=tick_count)
        
        if not ticks1 or not ticks2:
            return {'error': 'Insufficient tick data'}
        
        if len(ticks1) < window or len(ticks2) < window:
            return {'error': f'Need at least {window} ticks for each symbol'}
        
        # Convert to DataFrames
        df1 = pd.DataFrame(ticks1)
        df2 = pd.DataFrame(ticks2)
        
        # Parse timestamps
        df1['timestamp'] = pd.to_datetime(df1['timestamp'])
        df2['timestamp'] = pd.to_datetime(df2['timestamp'])
        
        # Sort by timestamp
        df1 = df1.sort_values('timestamp').reset_index(drop=True)
        df2 = df2.sort_values('timestamp').reset_index(drop=True)
        
        # Use merge_asof to align timestamps (within 5 seconds tolerance)
        # This matches each tick in df1 to the nearest tick in df2
        merged = pd.merge_asof(
            df1[['timestamp', 'price']],
            df2[['timestamp', 'price']],
            on='timestamp',
            direction='nearest',
            tolerance=pd.Timedelta(seconds=5),
            suffixes=('_1', '_2')
        )
        
        # Drop rows with missing values
        merged = merged.dropna()
        
        if len(merged) < window:
            return {'error': f'Only {len(merged)} aligned data points, need at least {window}'}
        
        # Extract prices
        prices1 = merged['price_1'].values
        prices2 = merged['price_2'].values
        
        # Compute hedge ratio using linear regression
        # Model: price1 = beta * price2 + alpha
        X = prices2.reshape(-1, 1)
        y = prices1
        
        model = LinearRegression()
        model.fit(X, y)
        
        hedge_ratio = float(model.coef_[0])
        intercept = float(model.intercept_)
        
        # Compute spread: spread = price1 - beta * price2
        spread = prices1 - hedge_ratio * prices2
        
        # Rolling statistics for z-score
        spread_series = pd.Series(spread)
        rolling_mean = spread_series.rolling(window=window).mean()
        rolling_std = spread_series.rolling(window=window).std()
        
        # Current values (last point)
        current_spread = float(spread[-1])
        spread_mean = float(rolling_mean.iloc[-1])
        spread_std = float(rolling_std.iloc[-1])
        
        # Z-score: (current_spread - mean) / std
        if spread_std > 0:
            current_zscore = (current_spread - spread_mean) / spread_std
        else:
            current_zscore = 0.0
        
        # Current prices
        current_price1 = float(prices1[-1])
        current_price2 = float(prices2[-1])
        
        return {
            'symbol1': symbol1,
            'symbol2': symbol2,
            'hedge_ratio': hedge_ratio,
            'intercept': intercept,
            'current_spread': current_spread,
            'spread_mean': spread_mean,
            'spread_std': spread_std,
            'current_zscore': current_zscore,
            'price1': current_price1,
            'price2': current_price2,
            'timestamp': merged['timestamp'].iloc[-1].isoformat(),
            'window': window,
            'data_points': len(merged),
            'method': 'tick_based',
            'timeframe': 'tick'
        }
    
    except Exception as e:
        logger.error(f"Error computing spread from ticks: {e}")
        return {'error': str(e)}
