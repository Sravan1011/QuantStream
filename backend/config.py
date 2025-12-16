"""
Configuration settings for the trading analytics backend.
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "Trading Analytics Platform"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database
    SQLITE_DB_PATH: str = "data/trading_data.db"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_ENABLED: bool = False  # Set to True if Redis is available
    
    # Binance WebSocket
    BINANCE_WS_BASE_URL: str = "wss://fstream.binance.com/ws"
    DEFAULT_SYMBOLS: str = "btcusdt,ethusdt"
    
    @property
    def symbols_list(self) -> List[str]:
        """Parse DEFAULT_SYMBOLS into a list."""
        if isinstance(self.DEFAULT_SYMBOLS, str):
            return [s.strip().lower() for s in self.DEFAULT_SYMBOLS.split(',') if s.strip()]
        return self.DEFAULT_SYMBOLS
    
    # Data Processing
    TICK_BUFFER_SIZE: int = 10000  # Max ticks to keep in memory
    BATCH_INSERT_SIZE: int = 100   # Bulk insert batch size
    BATCH_INSERT_INTERVAL: float = 1.0  # Seconds between batch inserts
    
    # Resampling
    RESAMPLE_INTERVALS: List[str] = ["1s", "1m", "5m"]
    
    # Analytics
    ROLLING_WINDOW_DEFAULT: int = 20  # Default rolling window for z-score, correlation
    ADF_MAX_LAG: int = 10  # Maximum lag for ADF test
    
    # WebSocket Updates
    WS_UPDATE_INTERVAL: float = 0.5  # Send updates every 500ms
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Ensure data directory exists
os.makedirs(os.path.dirname(settings.SQLITE_DB_PATH), exist_ok=True)
