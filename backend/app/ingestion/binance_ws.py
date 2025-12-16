"""
Binance WebSocket client for real-time tick data ingestion.
"""
import asyncio
import websockets
import json
from datetime import datetime
from typing import Callable, List, Optional, Dict, Any
import logging

from config import settings

logger = logging.getLogger(__name__)


class BinanceWebSocketClient:
    """Async WebSocket client for Binance Futures trade streams."""
    
    def __init__(self, symbols: List[str], on_tick: Callable):
        """
        Initialize WebSocket client.
        
        Args:
            symbols: List of trading symbols (lowercase, e.g., ['btcusdt', 'ethusdt'])
            on_tick: Callback function to handle incoming ticks
        """
        self.symbols = [s.lower() for s in symbols]
        self.on_tick = on_tick
        self.connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        self.tasks: List[asyncio.Task] = []
        self.running = False
    
    def _normalize_tick(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Binance trade data to standard format.
        
        Args:
            raw_data: Raw Binance WebSocket message
        
        Returns:
            Normalized tick data
        """
        # Binance sends: {"e":"trade", "E":timestamp, "T":trade_time, "s":"BTCUSDT", "p":"50000", "q":"0.001"}
        timestamp = datetime.fromtimestamp(raw_data.get('T', raw_data.get('E')) / 1000)
        
        return {
            'symbol': raw_data['s'].lower(),
            'timestamp': timestamp,
            'price': float(raw_data['p']),
            'size': float(raw_data['q'])
        }
    
    async def _connect_symbol(self, symbol: str):
        """
        Connect to WebSocket for a single symbol with auto-reconnect.
        
        Args:
            symbol: Trading symbol (lowercase)
        """
        url = f"{settings.BINANCE_WS_BASE_URL}/{symbol}@trade"
        reconnect_delay = 1
        max_reconnect_delay = 60
        
        while self.running:
            try:
                logger.info(f"Connecting to Binance WebSocket for {symbol}")
                async with websockets.connect(url) as ws:
                    self.connections[symbol] = ws
                    logger.info(f"Connected to {symbol} stream")
                    reconnect_delay = 1  # Reset delay on successful connection
                    
                    async for message in ws:
                        if not self.running:
                            break
                        
                        try:
                            data = json.loads(message)
                            
                            # Binance sends trade events with "e": "trade"
                            if data.get('e') == 'trade':
                                tick = self._normalize_tick(data)
                                await self.on_tick(tick)
                        
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON decode error for {symbol}: {e}")
                        except Exception as e:
                            logger.error(f"Error processing tick for {symbol}: {e}")
            
            except websockets.exceptions.WebSocketException as e:
                logger.error(f"WebSocket error for {symbol}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error for {symbol}: {e}")
            
            # Cleanup connection
            if symbol in self.connections:
                del self.connections[symbol]
            
            # Reconnect with exponential backoff
            if self.running:
                logger.info(f"Reconnecting to {symbol} in {reconnect_delay}s...")
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)
    
    async def start(self):
        """Start WebSocket connections for all symbols."""
        if self.running:
            logger.warning("WebSocket client already running")
            return
        
        self.running = True
        logger.info(f"Starting WebSocket client for symbols: {self.symbols}")
        
        # Create a task for each symbol
        self.tasks = [
            asyncio.create_task(self._connect_symbol(symbol))
            for symbol in self.symbols
        ]
    
    async def stop(self):
        """Stop all WebSocket connections."""
        if not self.running:
            return
        
        logger.info("Stopping WebSocket client")
        self.running = False
        
        # Close all connections (iterate over copy to avoid RuntimeError)
        for symbol, ws in list(self.connections.items()):
            try:
                await ws.close()
                logger.info(f"Closed connection for {symbol}")
            except Exception as e:
                logger.error(f"Error closing connection for {symbol}: {e}")
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.connections.clear()
        self.tasks.clear()
        logger.info("WebSocket client stopped")
    
    def add_symbol(self, symbol: str):
        """
        Add a new symbol to track.
        
        Args:
            symbol: Trading symbol (lowercase)
        """
        symbol = symbol.lower()
        if symbol not in self.symbols:
            self.symbols.append(symbol)
            if self.running:
                task = asyncio.create_task(self._connect_symbol(symbol))
                self.tasks.append(task)
                logger.info(f"Added symbol: {symbol}")
    
    def remove_symbol(self, symbol: str):
        """
        Remove a symbol from tracking.
        
        Args:
            symbol: Trading symbol (lowercase)
        """
        symbol = symbol.lower()
        if symbol in self.symbols:
            self.symbols.remove(symbol)
            # Connection will be closed when task detects running=False for that symbol
            logger.info(f"Removed symbol: {symbol}")
    
    def get_connected_symbols(self) -> List[str]:
        """Get list of currently connected symbols."""
        return list(self.connections.keys())
