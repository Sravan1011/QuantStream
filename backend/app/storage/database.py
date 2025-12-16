"""
SQLite database operations with async support.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, and_, func
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from .models import Base, Tick, OHLC, Alert
from config import settings

logger = logging.getLogger(__name__)


class Database:
    """Async SQLite database manager."""
    
    def __init__(self):
        self.engine = create_async_engine(
            f"sqlite+aiosqlite:///{settings.SQLITE_DB_PATH}",
            echo=settings.DEBUG,
        )
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def init_db(self):
        """Initialize database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized")
    
    async def insert_ticks(self, ticks: List[Dict[str, Any]]):
        """Bulk insert tick data."""
        async with self.async_session() as session:
            tick_objects = [
                Tick(
                    symbol=tick['symbol'],
                    timestamp=tick['timestamp'],
                    price=tick['price'],
                    size=tick['size']
                )
                for tick in ticks
            ]
            session.add_all(tick_objects)
            await session.commit()
            logger.debug(f"Inserted {len(ticks)} ticks")
    
    async def get_ticks(
        self,
        symbol: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Retrieve tick data with optional time filtering."""
        async with self.async_session() as session:
            query = select(Tick).where(Tick.symbol == symbol)
            
            if start_time:
                query = query.where(Tick.timestamp >= start_time)
            if end_time:
                query = query.where(Tick.timestamp <= end_time)
            
            query = query.order_by(Tick.timestamp.desc()).limit(limit)
            result = await session.execute(query)
            ticks = result.scalars().all()
            
            return [
                {
                    'symbol': tick.symbol,
                    'timestamp': tick.timestamp.isoformat(),
                    'price': tick.price,
                    'size': tick.size
                }
                for tick in reversed(ticks)  # Return in chronological order
            ]
    
    async def insert_ohlc(self, ohlc_data: Dict[str, Any]):
        """Insert or update OHLC data."""
        async with self.async_session() as session:
            # Check if exists
            query = select(OHLC).where(
                and_(
                    OHLC.symbol == ohlc_data['symbol'],
                    OHLC.timeframe == ohlc_data['timeframe'],
                    OHLC.timestamp == ohlc_data['timestamp']
                )
            )
            result = await session.execute(query)
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing
                existing.open = ohlc_data['open']
                existing.high = ohlc_data['high']
                existing.low = ohlc_data['low']
                existing.close = ohlc_data['close']
                existing.volume = ohlc_data['volume']
                existing.trade_count = ohlc_data.get('trade_count', 0)
            else:
                # Insert new
                ohlc = OHLC(**ohlc_data)
                session.add(ohlc)
            
            await session.commit()
    
    async def get_ohlc(
        self,
        symbol: str,
        timeframe: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 500
    ) -> List[Dict[str, Any]]:
        """Retrieve OHLC data."""
        async with self.async_session() as session:
            query = select(OHLC).where(
                and_(OHLC.symbol == symbol, OHLC.timeframe == timeframe)
            )
            
            if start_time:
                query = query.where(OHLC.timestamp >= start_time)
            if end_time:
                query = query.where(OHLC.timestamp <= end_time)
            
            query = query.order_by(OHLC.timestamp.desc()).limit(limit)
            result = await session.execute(query)
            ohlc_list = result.scalars().all()
            
            return [
                {
                    'symbol': ohlc.symbol,
                    'timeframe': ohlc.timeframe,
                    'timestamp': ohlc.timestamp.isoformat(),
                    'open': ohlc.open,
                    'high': ohlc.high,
                    'low': ohlc.low,
                    'close': ohlc.close,
                    'volume': ohlc.volume,
                    'trade_count': ohlc.trade_count
                }
                for ohlc in reversed(ohlc_list)
            ]
    
    async def create_alert(self, alert_data: Dict[str, Any]) -> int:
        """Create a new alert."""
        async with self.async_session() as session:
            alert = Alert(**alert_data)
            session.add(alert)
            await session.commit()
            await session.refresh(alert)
            return alert.id
    
    async def get_alerts(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all alerts."""
        async with self.async_session() as session:
            query = select(Alert)
            if active_only:
                query = query.where(Alert.is_active == 1)
            
            result = await session.execute(query)
            alerts = result.scalars().all()
            
            return [
                {
                    'id': alert.id,
                    'name': alert.name,
                    'symbol': alert.symbol,
                    'metric': alert.metric,
                    'condition': alert.condition,
                    'threshold': alert.threshold,
                    'is_active': bool(alert.is_active),
                    'created_at': alert.created_at.isoformat(),
                    'last_triggered': alert.last_triggered.isoformat() if alert.last_triggered else None
                }
                for alert in alerts
            ]
    
    async def update_alert_trigger(self, alert_id: int):
        """Update alert last triggered time."""
        async with self.async_session() as session:
            query = select(Alert).where(Alert.id == alert_id)
            result = await session.execute(query)
            alert = result.scalar_one_or_none()
            
            if alert:
                alert.last_triggered = datetime.utcnow()
                await session.commit()
    
    async def delete_alert(self, alert_id: int):
        """Delete an alert."""
        async with self.async_session() as session:
            query = select(Alert).where(Alert.id == alert_id)
            result = await session.execute(query)
            alert = result.scalar_one_or_none()
            
            if alert:
                await session.delete(alert)
                await session.commit()
    
    async def get_tick_count(self, symbol: Optional[str] = None) -> int:
        """Get total tick count."""
        async with self.async_session() as session:
            query = select(func.count(Tick.id))
            if symbol:
                query = query.where(Tick.symbol == symbol)
            
            result = await session.execute(query)
            return result.scalar()


# Global database instance
db = Database()
