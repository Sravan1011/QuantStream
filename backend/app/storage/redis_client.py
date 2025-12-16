"""
Redis cache client for real-time data storage.
"""
import redis.asyncio as redis
from typing import Optional, Dict, Any, List
import json
import logging
from config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Async Redis cache manager."""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.enabled = settings.REDIS_ENABLED
    
    async def connect(self):
        """Connect to Redis."""
        if not self.enabled:
            logger.info("Redis is disabled")
            return
        
        try:
            self.client = await redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            await self.client.ping()
            logger.info("Redis connected")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Running without cache.")
            self.enabled = False
            self.client = None
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
            logger.info("Redis disconnected")
    
    async def set(self, key: str, value: Any, ttl: int = 60):
        """Set a value with optional TTL."""
        if not self.enabled or not self.client:
            return
        
        try:
            await self.client.setex(
                key,
                ttl,
                json.dumps(value) if not isinstance(value, str) else value
            )
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value."""
        if not self.enabled or not self.client:
            return None
        
        try:
            value = await self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def push_tick(self, symbol: str, tick: Dict[str, Any], max_size: int = 1000):
        """Push tick to a list (FIFO queue)."""
        if not self.enabled or not self.client:
            return
        
        try:
            key = f"ticks:{symbol}"
            await self.client.lpush(key, json.dumps(tick))
            await self.client.ltrim(key, 0, max_size - 1)  # Keep only latest N ticks
            await self.client.expire(key, 3600)  # 1 hour TTL
        except Exception as e:
            logger.error(f"Redis push_tick error: {e}")
    
    async def get_recent_ticks(self, symbol: str, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent ticks for a symbol."""
        if not self.enabled or not self.client:
            return []
        
        try:
            key = f"ticks:{symbol}"
            ticks = await self.client.lrange(key, 0, count - 1)
            return [json.loads(tick) for tick in reversed(ticks)]
        except Exception as e:
            logger.error(f"Redis get_recent_ticks error: {e}")
            return []
    
    async def set_analytics(self, key: str, data: Dict[str, Any], ttl: int = 60):
        """Store analytics results."""
        await self.set(f"analytics:{key}", data, ttl)
    
    async def get_analytics(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve analytics results."""
        return await self.get(f"analytics:{key}")


# Global cache instance
cache = RedisCache()
