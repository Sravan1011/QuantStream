"""
WebSocket server for real-time data streaming to frontend.
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Set, Dict, Any
import asyncio
import json
import logging

from app.storage.redis_client import cache
from app.storage.database import db
from app.analytics import basic_stats, pairs_trading
from config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.broadcast_task: Optional[asyncio.Task] = None
        self.running = False
    
    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients."""
        if not self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def _broadcast_loop(self, symbols: list):
        """Periodically broadcast updates to all clients."""
        while self.running:
            try:
                if self.active_connections:
                    # Collect latest data for all symbols
                    updates = {
                        'type': 'update',
                        'timestamp': asyncio.get_event_loop().time(),
                        'data': {}
                    }
                    
                    for symbol in symbols:
                        # Get recent ticks from cache
                        recent_ticks = await cache.get_recent_ticks(symbol, count=10)
                        
                        if recent_ticks:
                            latest_tick = recent_ticks[-1]
                            updates['data'][symbol] = {
                                'price': latest_tick['price'],
                                'size': latest_tick['size'],
                                'timestamp': latest_tick['timestamp']
                            }
                    
                    if updates['data']:
                        await self.broadcast(updates)
                
                await asyncio.sleep(settings.WS_UPDATE_INTERVAL)
            
            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}")
                await asyncio.sleep(1)
    
    async def start_broadcasting(self, symbols: list):
        """Start the broadcast loop."""
        if self.running:
            return
        
        self.running = True
        self.broadcast_task = asyncio.create_task(self._broadcast_loop(symbols))
        logger.info("Started WebSocket broadcasting")
    
    async def stop_broadcasting(self):
        """Stop the broadcast loop."""
        if not self.running:
            return
        
        self.running = False
        if self.broadcast_task:
            self.broadcast_task.cancel()
            try:
                await self.broadcast_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped WebSocket broadcasting")


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint handler."""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            
            # Handle different message types
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # Client wants to subscribe to specific symbols
                symbols = data.get('symbols', [])
                await manager.send_personal_message({
                    'type': 'subscribed',
                    'symbols': symbols
                }, websocket)
            
            elif message_type == 'ping':
                # Heartbeat
                await manager.send_personal_message({
                    'type': 'pong',
                    'timestamp': asyncio.get_event_loop().time()
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
