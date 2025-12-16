"""
FastAPI REST endpoints for analytics and data access.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.analytics import basic_stats, pairs_trading, statistical_tests
from app.storage.database import db
from app.ingestion.manager import ingestion_manager
from app.analytics.resampling import resampling_engine

router = APIRouter()


# Pydantic models for request/response
class AlertCreate(BaseModel):
    name: str
    symbol: str
    metric: str
    condition: str
    threshold: float


class SymbolUpdate(BaseModel):
    symbols: List[str]


# Health check
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Ingestion status
@router.get("/status")
async def get_status():
    """Get system status."""
    if ingestion_manager:
        ingestion_status = ingestion_manager.get_status()
    else:
        ingestion_status = {"running": False}
    
    tick_count = await db.get_tick_count()
    
    return {
        "ingestion": ingestion_status,
        "total_ticks": tick_count,
        "timestamp": datetime.utcnow().isoformat()
    }


# Symbol management
@router.post("/symbols")
async def update_symbols(data: SymbolUpdate):
    """Update tracked symbols."""
    if not ingestion_manager:
        raise HTTPException(status_code=503, detail="Ingestion manager not initialized")
    
    # Add new symbols
    for symbol in data.symbols:
        ingestion_manager.add_symbol(symbol.lower())
    
    return {"symbols": ingestion_manager.symbols}


@router.get("/symbols")
async def get_symbols():
    """Get currently tracked symbols."""
    if not ingestion_manager:
        return {"symbols": []}
    
    return {"symbols": ingestion_manager.symbols}


# Data endpoints
@router.get("/ticks/{symbol}")
async def get_ticks(
    symbol: str,
    limit: int = Query(default=100, le=1000)
):
    """Get recent tick data for a symbol."""
    ticks = await db.get_ticks(symbol.lower(), limit=limit)
    return {"symbol": symbol, "ticks": ticks, "count": len(ticks)}


@router.get("/ohlc/{symbol}")
async def get_ohlc(
    symbol: str,
    timeframe: str = Query(default="1m", regex="^(1s|1m|5m)$"),
    limit: int = Query(default=100, le=500)
):
    """Get OHLC data for a symbol."""
    ohlc = await db.get_ohlc(symbol.lower(), timeframe, limit=limit)
    return {"symbol": symbol, "timeframe": timeframe, "ohlc": ohlc, "count": len(ohlc)}


# Analytics endpoints
@router.get("/analytics/basic/{symbol}")
async def get_basic_stats(
    symbol: str,
    timeframe: str = Query(default="1m", regex="^(1s|1m|5m)$"),
    window: int = Query(default=20, ge=5, le=100)
):
    """Get basic statistics for a symbol."""
    stats = await basic_stats.compute_basic_stats(symbol.lower(), timeframe, window)
    return stats


@router.get("/analytics/volatility/{symbol}")
async def get_volatility(
    symbol: str,
    timeframe: str = Query(default="1m"),
    window: int = Query(default=20, ge=5, le=100)
):
    """Get volatility metrics."""
    vol = await basic_stats.compute_volatility(symbol.lower(), timeframe, window)
    return vol


@router.get("/analytics/hedge-ratio")
async def get_hedge_ratio(
    symbol1: str,
    symbol2: str,
    timeframe: str = Query(default="1m"),
    lookback: int = Query(default=100, ge=20, le=500),
    method: str = Query(default="ols", regex="^(ols|huber)$")
):
    """Compute hedge ratio between two symbols."""
    result = await pairs_trading.compute_hedge_ratio(
        symbol1.lower(), symbol2.lower(), timeframe, lookback, method
    )
    return result


@router.get("/analytics/spread")
async def get_spread_zscore(
    symbol1: str,
    symbol2: str,
    timeframe: str = Query(default="1m"),
    lookback: int = Query(default=100, ge=20, le=500),
    window: int = Query(default=20, ge=5, le=100)
):
    """Compute spread and z-score for pairs trading."""
    result = await pairs_trading.compute_spread_and_zscore(
        symbol1.lower(), symbol2.lower(), timeframe, lookback, window
    )
    return result


@router.get("/analytics/correlation")
async def get_correlation(
    symbol1: str,
    symbol2: str,
    timeframe: str = Query(default="1m"),
    window: int = Query(default=20, ge=5, le=100)
):
    """Compute rolling correlation between two symbols."""
    result = await pairs_trading.compute_rolling_correlation(
        symbol1.lower(), symbol2.lower(), timeframe, window
    )
    return result


@router.get("/analytics/adf/{symbol}")
async def get_adf_test(
    symbol: str,
    timeframe: str = Query(default="1m")
):
    """Perform ADF test for stationarity."""
    result = await statistical_tests.compute_adf_test(symbol.lower(), timeframe)
    return result


@router.get("/analytics/spread-adf")
async def get_spread_adf_test(
    symbol1: str,
    symbol2: str,
    timeframe: str = Query(default="1m"),
    lookback: int = Query(default=100, ge=50, le=500)
):
    """Perform ADF test on spread between two symbols."""
    result = await statistical_tests.compute_spread_adf_test(
        symbol1.lower(), symbol2.lower(), timeframe, lookback
    )
    return result


# Alert endpoints
@router.post("/alerts")
async def create_alert(alert: AlertCreate):
    """Create a new alert."""
    alert_id = await db.create_alert({
        'name': alert.name,
        'symbol': alert.symbol.lower(),
        'metric': alert.metric,
        'condition': alert.condition,
        'threshold': alert.threshold,
        'is_active': 1
    })
    return {"alert_id": alert_id, "message": "Alert created successfully"}


@router.get("/alerts")
async def get_alerts(active_only: bool = True):
    """Get all alerts."""
    alerts = await db.get_alerts(active_only=active_only)
    return {"alerts": alerts, "count": len(alerts)}


@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: int):
    """Delete an alert."""
    await db.delete_alert(alert_id)
    return {"message": "Alert deleted successfully"}


# Data export
@router.get("/export/ticks/{symbol}")
async def export_ticks(
    symbol: str,
    limit: int = Query(default=1000, le=10000)
):
    """Export tick data as CSV."""
    ticks = await db.get_ticks(symbol.lower(), limit=limit)
    
    if not ticks:
        raise HTTPException(status_code=404, detail="No data found")
    
    # Convert to CSV format
    import io
    import csv
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['symbol', 'timestamp', 'price', 'size'])
    writer.writeheader()
    writer.writerows(ticks)
    
    return {
        "filename": f"{symbol}_ticks.csv",
        "data": output.getvalue(),
        "count": len(ticks)
    }


@router.get("/export/ohlc/{symbol}")
async def export_ohlc(
    symbol: str,
    timeframe: str = Query(default="1m"),
    limit: int = Query(default=500, le=10000)
):
    """Export OHLC data as CSV."""
    ohlc = await db.get_ohlc(symbol.lower(), timeframe, limit=limit)
    
    if not ohlc:
        raise HTTPException(status_code=404, detail="No data found")
    
    import io
    import csv
    
    output = io.StringIO()
    fieldnames = ['symbol', 'timeframe', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'trade_count']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(ohlc)
    
    return {
        "filename": f"{symbol}_{timeframe}_ohlc.csv",
        "data": output.getvalue(),
        "count": len(ohlc)
    }
