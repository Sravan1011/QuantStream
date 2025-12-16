"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings
from app.storage.database import db
from app.storage.redis_client import cache
from app.ingestion.manager import IngestionManager
from app.analytics.resampling import resampling_engine
from app.alerts.alert_engine import alert_engine
from app.api.routes import router
from app.api.websocket import websocket_endpoint, manager as ws_manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global ingestion manager
ingestion_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global ingestion_manager
    
    # Startup
    logger.info("Starting Trading Analytics Platform")
    
    # Initialize database
    await db.init_db()
    
    # Connect to Redis
    await cache.connect()
    
    # Initialize ingestion manager
    ingestion_manager = IngestionManager(settings.symbols_list)
    
    # Make it globally accessible
    import app.ingestion.manager as manager_module
    manager_module.ingestion_manager = ingestion_manager
    
    # Start ingestion
    await ingestion_manager.start()
    
    # Start resampling engine
    await resampling_engine.start(settings.symbols_list)
    
    # Start alert engine
    await alert_engine.start()
    
    # Start WebSocket broadcasting
    await ws_manager.start_broadcasting(settings.symbols_list)
    
    logger.info("All services started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Trading Analytics Platform")
    
    # Stop all services
    await ws_manager.stop_broadcasting()
    await alert_engine.stop()
    await resampling_engine.stop()
    await ingestion_manager.stop()
    await cache.disconnect()
    
    logger.info("All services stopped")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time trading analytics platform for quantitative analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket_endpoint(websocket)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


# Alert triggers endpoint
@app.get("/api/alerts/triggers")
async def get_alert_triggers():
    """Get recently triggered alerts."""
    triggers = alert_engine.get_recent_triggers()
    return {"triggers": triggers, "count": len(triggers)}
