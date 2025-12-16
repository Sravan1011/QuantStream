"""
Database models using SQLAlchemy.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Tick(Base):
    """Raw tick data from WebSocket."""
    __tablename__ = "ticks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    price = Column(Float, nullable=False)
    size = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
    )


class OHLC(Base):
    """Resampled OHLC data."""
    __tablename__ = "ohlc"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)  # '1s', '1m', '5m'
    timestamp = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    trade_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('symbol', 'timeframe', 'timestamp', name='uix_ohlc'),
        Index('idx_ohlc_symbol_timeframe', 'symbol', 'timeframe', 'timestamp'),
    )


class Alert(Base):
    """User-defined alerts."""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    metric = Column(String(50), nullable=False)  # 'z_score', 'price', 'spread'
    condition = Column(String(10), nullable=False)  # '>', '<', '>=', '<=', '=='
    threshold = Column(Float, nullable=False)
    is_active = Column(Integer, default=1)  # SQLite doesn't have boolean
    created_at = Column(DateTime, default=datetime.utcnow)
    last_triggered = Column(DateTime, nullable=True)
