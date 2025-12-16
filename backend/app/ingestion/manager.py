"""
Data ingestion manager that coordinates WebSocket, storage, and resampling.
"""
import asyncio
from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime
import logging

from .binance_ws import BinanceWebSocketClient
from app.storage.database import db
from app.storage.redis_client import cache
from config import settings

logger = logging.getLogger(__name__)


class IngestionManager:
    """Manages data ingestion pipeline from WebSocket to storage."""
    
    def __init__(self, symbols: List[str]):
        """
        Initialize ingestion manager.
        
        Args:
            symbols: List of trading symbols to track
        """
        self.symbols = symbols
        self.ws_client = BinanceWebSocketClient(symbols, self._handle_tick)
        self.tick_buffer: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.running = False
        self.batch_task: Optional[asyncio.Task] = None
    
    async def _handle_tick(self, tick: Dict[str, Any]):
        """
        Handle incoming tick data.
        
        Args:
            tick: Normalized tick data
        """
        symbol = tick['symbol']
        
        # Add to buffer for batch insert
        self.tick_buffer[symbol].append(tick)
        
        # Push to Redis cache for real-time access
        await cache.push_tick(symbol, {
            'symbol': symbol,
            'timestamp': tick['timestamp'].isoformat(),
            'price': tick['price'],
            'size': tick['size']
        })
        
        logger.debug(f"Received tick: {symbol} @ {tick['price']}")
    
    async def _batch_insert_loop(self):
        """Periodically flush tick buffer to database."""
        while self.running:
            await asyncio.sleep(settings.BATCH_INSERT_INTERVAL)
            
            if not self.tick_buffer:
                continue
            
            try:
                # Collect all ticks from buffer
                all_ticks = []
                for symbol, ticks in self.tick_buffer.items():
                    all_ticks.extend(ticks)
                
                if all_ticks:
                    # Insert to database
                    await db.insert_ticks(all_ticks)
                    logger.info(f"Inserted {len(all_ticks)} ticks to database")
                    
                    # Clear buffer
                    self.tick_buffer.clear()
            
            except Exception as e:
                logger.error(f"Error in batch insert: {e}")
    
    async def start(self):
        """Start ingestion pipeline."""
        if self.running:
            logger.warning("Ingestion manager already running")
            return
        
        self.running = True
        logger.info("Starting ingestion manager")
        
        # Start WebSocket client
        await self.ws_client.start()
        
        # Start batch insert loop
        self.batch_task = asyncio.create_task(self._batch_insert_loop())
        
        logger.info("Ingestion manager started")
    
    async def stop(self):
        """Stop ingestion pipeline."""
        if not self.running:
            return
        
        logger.info("Stopping ingestion manager")
        self.running = False
        
        # Stop WebSocket client
        await self.ws_client.stop()
        
        # Cancel batch task
        if self.batch_task:
            self.batch_task.cancel()
            try:
                await self.batch_task
            except asyncio.CancelledError:
                pass
        
        # Flush remaining ticks
        all_ticks = []
        for symbol, ticks in self.tick_buffer.items():
            all_ticks.extend(ticks)
        
        if all_ticks:
            await db.insert_ticks(all_ticks)
            logger.info(f"Flushed {len(all_ticks)} remaining ticks")
        
        self.tick_buffer.clear()
        logger.info("Ingestion manager stopped")
    
    def add_symbol(self, symbol: str):
        """Add a new symbol to track."""
        if symbol not in self.symbols:
            self.symbols.append(symbol)
            self.ws_client.add_symbol(symbol)
    
    def remove_symbol(self, symbol: str):
        """Remove a symbol from tracking."""
        if symbol in self.symbols:
            self.symbols.remove(symbol)
            self.ws_client.remove_symbol(symbol)
    
    def get_status(self) -> Dict[str, Any]:
        """Get ingestion status."""
        return {
            'running': self.running,
            'symbols': self.symbols,
            'connected_symbols': self.ws_client.get_connected_symbols(),
            'buffered_ticks': sum(len(ticks) for ticks in self.tick_buffer.values())
        }


# Global ingestion manager instance (will be initialized in main.py)
ingestion_manager: Optional[IngestionManager] = None
