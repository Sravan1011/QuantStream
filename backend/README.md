# Trading Analytics Platform - Backend

## Overview
Real-time trading analytics platform for quantitative analysis with WebSocket data ingestion from Binance, statistical computations, and REST/WebSocket APIs.

## Features
- **Real-time Data Ingestion**: WebSocket connection to Binance Futures for live tick data
- **Multi-timeframe Resampling**: Automatic OHLC aggregation (1s, 1m, 5m)
- **Pairs Trading Analytics**: Hedge ratio, spread, z-score, correlation
- **Statistical Tests**: ADF test for stationarity
- **Alert System**: User-defined alerts on price, z-score, volume, volatility
- **Data Export**: CSV export for ticks and OHLC data
- **Real-time Updates**: WebSocket server for live frontend updates

## Architecture

### Components
1. **Ingestion Layer** (`app/ingestion/`)
   - `binance_ws.py`: WebSocket client with auto-reconnect
   - `manager.py`: Coordinates ingestion, buffering, and batch inserts

2. **Storage Layer** (`app/storage/`)
   - `database.py`: Async SQLite operations
   - `redis_client.py`: Redis cache for real-time data (optional)
   - `models.py`: SQLAlchemy models (Tick, OHLC, Alert)

3. **Analytics Engine** (`app/analytics/`)
   - `resampling.py`: OHLC aggregation engine
   - `basic_stats.py`: Price statistics and volatility
   - `pairs_trading.py`: Hedge ratio, spread, z-score, correlation
   - `statistical_tests.py`: ADF test

4. **API Layer** (`app/api/`)
   - `routes.py`: REST endpoints for data and analytics
   - `websocket.py`: WebSocket server for real-time updates

5. **Alert System** (`app/alerts/`)
   - `alert_engine.py`: Evaluates alerts and triggers notifications

## Setup

### Prerequisites
- Python 3.9+
- pip

### Installation

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

### Running the Application

**Single command**:
```bash
python run.py
```

The server will start on `http://localhost:8000`

### API Documentation

Once running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## API Endpoints

### System
- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `GET /api/status` - System status

### Data
- `GET /api/ticks/{symbol}` - Get tick data
- `GET /api/ohlc/{symbol}` - Get OHLC data

### Analytics
- `GET /api/analytics/basic/{symbol}` - Basic statistics
- `GET /api/analytics/volatility/{symbol}` - Volatility metrics
- `GET /api/analytics/hedge-ratio` - Hedge ratio (OLS/Huber)
- `GET /api/analytics/spread` - Spread and z-score
- `GET /api/analytics/correlation` - Rolling correlation
- `GET /api/analytics/adf/{symbol}` - ADF test
- `GET /api/analytics/spread-adf` - ADF test on spread

### Alerts
- `POST /api/alerts` - Create alert
- `GET /api/alerts` - List alerts
- `DELETE /api/alerts/{id}` - Delete alert
- `GET /api/alerts/triggers` - Recent triggered alerts

### Export
- `GET /api/export/ticks/{symbol}` - Export ticks as CSV
- `GET /api/export/ohlc/{symbol}` - Export OHLC as CSV

### WebSocket
- `WS /ws` - Real-time data stream

## Configuration

Edit `.env` file:

```env
# Server
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database
SQLITE_DB_PATH=data/trading_data.db

# Redis (optional)
REDIS_ENABLED=False
REDIS_HOST=localhost
REDIS_PORT=6379

# Binance
DEFAULT_SYMBOLS=btcusdt,ethusdt

# Logging
LOG_LEVEL=INFO
```

## Data Flow

```
Binance WebSocket → Ingestion Manager → Tick Buffer
                                      ↓
                            ┌─────────┴─────────┐
                            ↓                   ↓
                       SQLite DB          Redis Cache
                            ↓                   ↓
                    Resampling Engine    Real-time Access
                            ↓                   ↓
                        OHLC Data         WebSocket Server
                            ↓                   ↓
                    Analytics Engine      Frontend Clients
                            ↓
                       REST API
```

## Analytics Methodology

### Hedge Ratio
- **Method**: Ordinary Least Squares (OLS) or Huber regression
- **Formula**: `symbol1 = α + β * symbol2`
- **Output**: β (hedge ratio), R²

### Spread
- **Formula**: `spread = price1 - β * price2`
- **Z-score**: `(spread - rolling_mean) / rolling_std`

### ADF Test
- **Purpose**: Test for stationarity
- **Null Hypothesis**: Series has unit root (non-stationary)
- **Interpretation**: p-value < 0.05 → stationary

### Correlation
- **Method**: Pearson rolling correlation
- **Window**: Configurable (default 20 periods)

## Development

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── ingestion/           # WebSocket ingestion
│   ├── storage/             # Database & cache
│   ├── analytics/           # Analytics modules
│   ├── api/                 # REST & WebSocket APIs
│   └── alerts/              # Alert system
├── config.py                # Configuration
├── requirements.txt         # Dependencies
├── run.py                   # Entry point
└── .env                     # Environment variables
```

### Adding New Analytics

1. Create function in appropriate module (`app/analytics/`)
2. Add endpoint in `app/api/routes.py`
3. Update API documentation

## Troubleshooting

### Database locked error
- SQLite is single-writer. Reduce concurrent writes or use PostgreSQL for production.

### WebSocket connection fails
- Check Binance API status
- Verify network connectivity
- Check firewall settings

### Redis connection fails
- Set `REDIS_ENABLED=False` in `.env` to run without Redis
- System will use SQLite only

## Performance Optimization

- **Batch Inserts**: Ticks are batched (default 1s interval)
- **Redis Cache**: Hot data cached for fast access
- **Async Operations**: All I/O is asynchronous
- **Connection Pooling**: Database connections are pooled

## License
MIT
