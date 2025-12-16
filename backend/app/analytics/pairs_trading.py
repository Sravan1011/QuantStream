"""
Pairs trading analytics: hedge ratio, spread, z-score.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression, HuberRegressor
from scipy import stats
import logging

from app.storage.database import db

logger = logging.getLogger(__name__)


async def compute_hedge_ratio(
    symbol1: str,
    symbol2: str,
    timeframe: str = '1m',
    lookback: int = 100,
    method: str = 'ols'
) -> Dict[str, Any]:
    """
    Compute hedge ratio between two symbols using regression.
    
    Args:
        symbol1: First symbol (dependent variable)
        symbol2: Second symbol (independent variable)
        timeframe: OHLC timeframe
        lookback: Number of periods to use
        method: 'ols' or 'huber' (robust regression)
    
    Returns:
        Hedge ratio and regression statistics
    """
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        # Get OHLC data for both symbols
        data1 = await db.get_ohlc(symbol1, timeframe, start_time, end_time, limit=lookback)
        data2 = await db.get_ohlc(symbol2, timeframe, start_time, end_time, limit=lookback)
        
        if not data1 or not data2 or len(data1) < 10 or len(data2) < 10:
            return {'error': 'Insufficient data'}
        
        # Convert to DataFrames
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        df1['timestamp'] = pd.to_datetime(df1['timestamp'])
        df2['timestamp'] = pd.to_datetime(df2['timestamp'])
        
        # Merge on timestamp
        merged = pd.merge(df1[['timestamp', 'close']], df2[['timestamp', 'close']], 
                         on='timestamp', suffixes=('_1', '_2'))
        
        if len(merged) < 10:
            return {'error': 'Insufficient aligned data'}
        
        X = merged['close_2'].values.reshape(-1, 1)
        y = merged['close_1'].values
        
        # Perform regression
        if method == 'huber':
            model = HuberRegressor()
        else:
            model = LinearRegression()
        
        model.fit(X, y)
        
        hedge_ratio = float(model.coef_[0])
        intercept = float(model.intercept_)
        
        # R-squared
        y_pred = model.predict(X)
        r_squared = float(1 - (np.sum((y - y_pred) ** 2) / np.sum((y - y.mean()) ** 2)))
        
        return {
            'symbol1': symbol1,
            'symbol2': symbol2,
            'hedge_ratio': hedge_ratio,
            'intercept': intercept,
            'r_squared': r_squared,
            'method': method,
            'data_points': len(merged),
            'timeframe': timeframe
        }
    
    except Exception as e:
        logger.error(f"Error computing hedge ratio for {symbol1}/{symbol2}: {e}")
        return {'error': str(e)}


async def compute_spread_and_zscore(
    symbol1: str,
    symbol2: str,
    timeframe: str = '1m',
    lookback: int = 100,
    window: int = 20
) -> Dict[str, Any]:
    """
    Compute spread and z-score for pairs trading.
    
    Args:
        symbol1: First symbol
        symbol2: Second symbol
        timeframe: OHLC timeframe
        lookback: Number of periods for hedge ratio
        window: Rolling window for z-score
    
    Returns:
        Spread, z-score, and related metrics
    """
    try:
        # First compute hedge ratio
        hedge_result = await compute_hedge_ratio(symbol1, symbol2, timeframe, lookback)
        
        if 'error' in hedge_result:
            return hedge_result
        
        hedge_ratio = hedge_result['hedge_ratio']
        
        # Get recent data
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        data1 = await db.get_ohlc(symbol1, timeframe, start_time, end_time, limit=lookback)
        data2 = await db.get_ohlc(symbol2, timeframe, start_time, end_time, limit=lookback)
        
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        df1['timestamp'] = pd.to_datetime(df1['timestamp'])
        df2['timestamp'] = pd.to_datetime(df2['timestamp'])
        
        # Merge and compute spread
        merged = pd.merge(df1[['timestamp', 'close']], df2[['timestamp', 'close']], 
                         on='timestamp', suffixes=('_1', '_2'))
        
        merged['spread'] = merged['close_1'] - hedge_ratio * merged['close_2']
        
        # Compute z-score
        rolling_mean = merged['spread'].rolling(window=window).mean()
        rolling_std = merged['spread'].rolling(window=window).std()
        merged['zscore'] = (merged['spread'] - rolling_mean) / rolling_std
        
        # Get latest values
        latest = merged.iloc[-1]
        current_spread = float(latest['spread'])
        current_zscore = float(latest['zscore'])
        
        # Spread statistics
        spread_mean = float(merged['spread'].mean())
        spread_std = float(merged['spread'].std())
        
        return {
            'symbol1': symbol1,
            'symbol2': symbol2,
            'hedge_ratio': hedge_ratio,
            'current_spread': current_spread,
            'spread_mean': spread_mean,
            'spread_std': spread_std,
            'current_zscore': current_zscore,
            'timestamp': latest['timestamp'].isoformat(),
            'price1': float(latest['close_1']),
            'price2': float(latest['close_2']),
            'window': window,
            'timeframe': timeframe
        }
    
    except Exception as e:
        logger.error(f"Error computing spread/zscore for {symbol1}/{symbol2}: {e}")
        return {'error': str(e)}


async def compute_rolling_correlation(
    symbol1: str,
    symbol2: str,
    timeframe: str = '1m',
    window: int = 20
) -> Dict[str, Any]:
    """
    Compute rolling correlation between two symbols.
    
    Args:
        symbol1: First symbol
        symbol2: Second symbol
        timeframe: OHLC timeframe
        window: Rolling window size
    
    Returns:
        Correlation metrics and time series
    """
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        data1 = await db.get_ohlc(symbol1, timeframe, start_time, end_time, limit=500)
        data2 = await db.get_ohlc(symbol2, timeframe, start_time, end_time, limit=500)
        
        if not data1 or not data2:
            return {'error': 'Insufficient data'}
        
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        df1['timestamp'] = pd.to_datetime(df1['timestamp'])
        df2['timestamp'] = pd.to_datetime(df2['timestamp'])
        
        # Merge
        merged = pd.merge(df1[['timestamp', 'close']], df2[['timestamp', 'close']], 
                         on='timestamp', suffixes=('_1', '_2'))
        
        if len(merged) < window:
            return {'error': 'Insufficient aligned data'}
        
        # Rolling correlation
        merged['correlation'] = merged['close_1'].rolling(window=window).corr(merged['close_2'])
        
        # Remove NaN values
        correlation_series = merged[['timestamp', 'correlation']].dropna()
        
        current_correlation = float(correlation_series.iloc[-1]['correlation'])
        mean_correlation = float(correlation_series['correlation'].mean())
        
        return {
            'symbol1': symbol1,
            'symbol2': symbol2,
            'current_correlation': current_correlation,
            'mean_correlation': mean_correlation,
            'window': window,
            'timeframe': timeframe,
            'correlation_series': [
                {
                    'timestamp': row['timestamp'].isoformat(),
                    'correlation': float(row['correlation'])
                }
                for _, row in correlation_series.tail(100).iterrows()
            ]
        }
    
    except Exception as e:
        logger.error(f"Error computing correlation for {symbol1}/{symbol2}: {e}")
        return {'error': str(e)}
