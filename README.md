# Trading Analytics Platform

> Real-time trading analytics platform for quantitative analysis with WebSocket data ingestion, statistical computations, and interactive visualization.

## 🎯 Project Overview

A complete full-stack application designed for traders and researchers at quantitative trading firms. The platform ingests live tick data from Binance Futures, performs statistical analysis including pairs trading analytics, and presents results through an interactive Next.js dashboard.

## ✨ Features

### Backend (Python/FastAPI)
- ✅ **Real-time Data Ingestion**: WebSocket connection to Binance Futures
- ✅ **Multi-timeframe Resampling**: Automatic OHLC aggregation (1s, 1m, 5m)
- ✅ **Pairs Trading Analytics**: Hedge ratio (OLS/Huber), spread, z-score
- ✅ **Statistical Tests**: ADF test for stationarity
- ✅ **Rolling Correlation**: Pearson correlation with configurable windows
- ✅ **Alert System**: Custom alerts on price, z-score, volume, volatility
- ✅ **Data Export**: CSV export for ticks and OHLC data
- ✅ **Dual Storage**: SQLite (persistence) + Redis (optional cache)

### Frontend (Next.js)
- ✅ **Interactive Charts**: Real-time OHLC price visualization
- ✅ **Spread & Z-Score**: Visual indicators for pairs trading
- ✅ **Live Statistics**: Real-time price updates via WebSocket
- ✅ **Alert Management**: Create, view, and delete custom alerts
- ✅ **Responsive Design**: Modern dark theme with Tailwind CSS
- ✅ **Parameter Controls**: Timeframe and window selection

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- pip and npm

### One-Command Setup

```bash
# Clone/navigate to project directory
cd "gemscap assigment"

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..

# Setup frontend
cd frontend
npm install
cd ..

# Start both servers
./start.sh
```

Then open:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Manual Setup

**Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

**Frontend** (in new terminal):
```bash
cd frontend
npm install
npm run dev
```

## 📊 Architecture

```
┌─────────────────┐
│ Binance Futures │
│   WebSocket     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Python Backend │
│    (FastAPI)    │
├─────────────────┤
│ • WebSocket     │
│ • SQLite/Redis  │
│ • Analytics     │
│ • REST/WS API   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Next.js Frontend│
│  (TypeScript)   │
├─────────────────┤
│ • Charts        │
│ • Real-time UI  │
│ • Alerts        │
│ • Controls      │
└─────────────────┘
```

## 📁 Project Structure

```
gemscap assigment/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── ingestion/         # WebSocket data ingestion
│   │   ├── storage/           # Database & cache
│   │   ├── analytics/         # Statistical computations
│   │   ├── api/               # REST & WebSocket APIs
│   │   ├── alerts/            # Alert system
│   │   └── main.py            # FastAPI application
│   ├── config.py              # Configuration
│   ├── requirements.txt       # Python dependencies
│   ├── run.py                 # Entry point
│   └── README.md              # Backend documentation
│
├── frontend/                   # Next.js frontend
│   ├── app/                   # Next.js App Router
│   ├── components/            # React components
│   │   ├── charts/           # Chart components
│   │   ├── StatsCard.tsx     # Statistics display
│   │   ├── ControlPanel.tsx  # Parameter controls
│   │   └── AlertManager.tsx  # Alert management
│   ├── hooks/                 # Custom React hooks
│   ├── lib/                   # Utilities & state
│   └── README.md              # Frontend documentation
│
├── start.sh                    # Launcher script
└── README.md                   # This file
```

## 🔧 Configuration

### Backend (.env)
```env
DEBUG=True
HOST=0.0.0.0
PORT=8000
SQLITE_DB_PATH=data/trading_data.db
REDIS_ENABLED=False
DEFAULT_SYMBOLS=btcusdt,ethusdt
LOG_LEVEL=INFO
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## 📈 Analytics Methodology

### Hedge Ratio
- **Method**: OLS or Huber regression (robust)
- **Formula**: `symbol1 = α + β * symbol2`
- **Output**: β (hedge ratio), R²

### Spread & Z-Score
- **Spread**: `spread = price1 - β * price2`
- **Z-score**: `(spread - rolling_mean) / rolling_std`
- **Interpretation**: |z-score| > 2 indicates potential mean reversion

### ADF Test
- **Purpose**: Test for stationarity
- **Null Hypothesis**: Series has unit root (non-stationary)
- **Result**: p-value < 0.05 → stationary (good for pairs trading)

### Rolling Correlation
- **Method**: Pearson correlation
- **Window**: Configurable (default 20 periods)
- **Use**: Identify correlated pairs for trading

## 🎨 UI Features

- **Dark Theme**: Professional slate color palette
- **Real-time Updates**: WebSocket for sub-second latency
- **Interactive Charts**: Zoom, pan, hover tooltips
- **Responsive**: Works on desktop and mobile
- **Visual Alerts**: Color-coded z-score indicators
- **Live Ticker**: Real-time price updates

## 📊 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/status` | System status |
| `GET /api/ticks/{symbol}` | Get tick data |
| `GET /api/ohlc/{symbol}` | Get OHLC data |
| `GET /api/analytics/basic/{symbol}` | Basic statistics |
| `GET /api/analytics/spread` | Spread & z-score |
| `GET /api/analytics/correlation` | Rolling correlation |
| `GET /api/analytics/adf/{symbol}` | ADF test |
| `POST /api/alerts` | Create alert |
| `GET /api/alerts` | List alerts |
| `WS /ws` | Real-time data stream |

Full API documentation: http://localhost:8000/docs

## 🧪 Testing

**Backend**:
```bash
cd backend
./venv/bin/python test_setup.py
```

**Frontend**:
```bash
cd frontend
npm run build  # Verify build
```

## 🔍 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.9+)
- Verify virtual environment is activated
- Check port 8000 is not in use

### Frontend won't connect
- Ensure backend is running first
- Check console for CORS errors
- Verify API_URL in `.env.local`

### No data in charts
- Wait 10-30 seconds for data to accumulate
- Check WebSocket connection (green "Live" indicator)
- Verify Binance API is accessible

### WebSocket disconnects
- Auto-reconnect is enabled (wait 3 seconds)
- Check network connectivity
- Verify firewall settings

## 📝 Design Decisions

### Modularity
- Clean separation of concerns
- Each module can be tested/replaced independently
- Easy to add new analytics or data sources

### Scalability
- Async operations throughout
- Batch inserts reduce database load
- Redis cache for hot data
- Ready to swap SQLite → PostgreSQL/TimescaleDB

### Real-time Performance
- WebSocket for sub-second updates
- Configurable update intervals
- Efficient data structures

### Graceful Degradation
- Redis is optional (falls back to SQLite)
- WebSocket auto-reconnects
- Error handling throughout

## 🚀 Future Enhancements

- [ ] Kalman Filter for dynamic hedge ratio
- [ ] Correlation heatmap visualization
- [ ] Mini mean-reversion backtest
- [ ] Historical data upload (CSV)
- [ ] More symbol pairs
- [ ] Advanced charting (candlesticks)
- [ ] User authentication
- [ ] Database migration to PostgreSQL/TimescaleDB

## 📄 License

MIT

## 👨‍💻 Development

Built with:
- **Backend**: FastAPI, SQLAlchemy, pandas, numpy, scipy, statsmodels
- **Frontend**: Next.js, TypeScript, Tailwind CSS, Recharts, Zustand
- **Data Source**: Binance Futures WebSocket API

---

**Note**: This is a demonstration project for quantitative trading analytics. Not intended for production trading without further development and testing.
