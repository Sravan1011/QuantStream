"""
Statistical tests for time series analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from statsmodels.tsa.stattools import adfuller
import logging

from app.storage.database import db
from config import settings

logger = logging.getLogger(__name__)


async def compute_adf_test(
    symbol: str,
    timeframe: str = '1m',
    max_lag: Optional[int] = None
) -> Dict[str, Any]:
    """
    Perform Augmented Dickey-Fuller test for stationarity.
    
    Args:
        symbol: Trading symbol
        timeframe: OHLC timeframe
        max_lag: Maximum lag for ADF test
    
    Returns:
        ADF test results
    """
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        ohlc_data = await db.get_ohlc(symbol, timeframe, start_time, end_time, limit=500)
        
        if not ohlc_data or len(ohlc_data) < 50:
            return {'error': 'Insufficient data for ADF test (need at least 50 points)'}
        
        df = pd.DataFrame(ohlc_data)
        prices = df['close'].values
        
        # Perform ADF test
        max_lag = max_lag or settings.ADF_MAX_LAG
        result = adfuller(prices, maxlag=max_lag, regression='c')
        
        adf_statistic = float(result[0])
        p_value = float(result[1])
        used_lag = int(result[2])
        n_obs = int(result[3])
        critical_values = {k: float(v) for k, v in result[4].items()}
        
        # Determine if stationary (p-value < 0.05)
        is_stationary = p_value < 0.05
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'adf_statistic': adf_statistic,
            'p_value': p_value,
            'used_lag': used_lag,
            'n_observations': n_obs,
            'critical_values': critical_values,
            'is_stationary': is_stationary,
            'interpretation': 'Stationary' if is_stationary else 'Non-stationary'
        }
    
    except Exception as e:
        logger.error(f"Error performing ADF test for {symbol}: {e}")
        return {'error': str(e)}


async def compute_spread_adf_test(
    symbol1: str,
    symbol2: str,
    timeframe: str = '1m',
    lookback: int = 100
) -> Dict[str, Any]:
    """
    Perform ADF test on the spread between two symbols.
    
    Args:
        symbol1: First symbol
        symbol2: Second symbol
        timeframe: OHLC timeframe
        lookback: Number of periods
    
    Returns:
        ADF test results for spread
    """
    try:
        from app.analytics.pairs_trading import compute_hedge_ratio
        
        # Get hedge ratio
        hedge_result = await compute_hedge_ratio(symbol1, symbol2, timeframe, lookback)
        
        if 'error' in hedge_result:
            return hedge_result
        
        hedge_ratio = hedge_result['hedge_ratio']
        
        # Get data
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
        
        spread = merged['close_1'] - hedge_ratio * merged['close_2']
        
        if len(spread) < 50:
            return {'error': 'Insufficient data for ADF test'}
        
        # Perform ADF test on spread
        result = adfuller(spread.values, maxlag=settings.ADF_MAX_LAG, regression='c')
        
        adf_statistic = float(result[0])
        p_value = float(result[1])
        is_stationary = p_value < 0.05
        
        return {
            'symbol1': symbol1,
            'symbol2': symbol2,
            'hedge_ratio': hedge_ratio,
            'adf_statistic': adf_statistic,
            'p_value': p_value,
            'critical_values': {k: float(v) for k, v in result[4].items()},
            'is_stationary': is_stationary,
            'interpretation': 'Spread is stationary (good for pairs trading)' if is_stationary else 'Spread is non-stationary',
            'timeframe': timeframe
        }
    
    except Exception as e:
        logger.error(f"Error performing spread ADF test for {symbol1}/{symbol2}: {e}")
        return {'error': str(e)}
