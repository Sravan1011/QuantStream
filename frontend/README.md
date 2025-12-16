# Trading Analytics Platform - Frontend

## Overview
Next.js dashboard for real-time trading analytics with interactive charts, statistics, and alert management.

## Features
- **Real-time Price Charts**: OHLC visualization with Recharts
- **Pairs Trading Analytics**: Spread, z-score, and hedge ratio
- **Live Statistics**: Real-time price updates via WebSocket
- **Alert Management**: Create custom alerts on price, z-score, volume, volatility
- **Responsive Design**: Modern UI with Tailwind CSS
- **Interactive Controls**: Timeframe and window parameter selection

## Tech Stack
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **State Management**: Zustand
- **Icons**: Lucide React

## Setup

### Prerequisites
- Node.js 18+
- Backend server running on `http://localhost:8000`

### Installation

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment** (optional):
   Create `.env.local` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
   ```

4. **Run development server**:
   ```bash
   npm run dev
   ```

5. **Open browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main dashboard
│   └── globals.css         # Global styles
├── components/
│   ├── charts/
│   │   ├── PriceChart.tsx  # OHLC price chart
│   │   └── SpreadChart.tsx # Spread & z-score
│   ├── StatsCard.tsx       # Statistics display
│   ├── ControlPanel.tsx    # Parameter controls
│   └── AlertManager.tsx    # Alert management
├── hooks/
│   └── useWebSocket.ts     # WebSocket hook
├── lib/
│   ├── store.ts            # Zustand state
│   └── api.ts              # API client
└── next.config.ts          # Next.js config
```

## Components

### PriceChart
- Displays OHLC data as line chart
- Shows high/low with dashed lines
- Auto-refreshes every 5 seconds
- Supports multiple timeframes (1s, 1m, 5m)

### SpreadChart
- Visualizes spread between two symbols
- Shows z-score with color-coded indicator
- Displays hedge ratio and spread statistics
- Alerts when |z-score| > 2

### StatsCard
- Real-time price ticker
- 24h high/low
- Rolling mean and standard deviation
- Volume statistics
- Color-coded price changes

### ControlPanel
- Symbol display
- Timeframe selector (1s, 1m, 5m)
- Rolling window slider (5-100)

### AlertManager
- Create custom alerts
- Supported metrics: price, z-score, volume, volatility
- Conditions: >, <, >=, <=
- Delete alerts
- Real-time alert evaluation

## API Integration

The frontend connects to the backend via:

1. **REST API** (`http://localhost:8000/api/`)
   - Fetch OHLC data
   - Get statistics
   - Compute analytics
   - Manage alerts

2. **WebSocket** (`ws://localhost:8000/ws`)
   - Real-time price updates
   - Live data streaming
   - Auto-reconnect on disconnect

## State Management

Using Zustand for global state:
- Selected symbols
- Timeframe and window parameters
- Ticks and OHLC data
- Statistics and spread data
- Alerts
- WebSocket connection status

## Styling

- **Dark Theme**: Slate color palette
- **Responsive**: Mobile-first design
- **Modern**: Glassmorphism effects
- **Accessible**: Proper contrast ratios

## Development

### Available Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Adding New Components

1. Create component in `components/`
2. Import in `app/page.tsx`
3. Connect to store via `useStore()`
4. Fetch data via `api` client

## Troubleshooting

### Backend Connection Issues
- Ensure backend is running on `http://localhost:8000`
- Check CORS settings in backend
- Verify API_URL in environment variables

### WebSocket Not Connecting
- Check backend WebSocket server is running
- Verify WS_URL is correct
- Check browser console for errors

### Charts Not Displaying
- Ensure backend has data (wait for ticks to accumulate)
- Check browser console for API errors
- Verify timeframe has OHLC data

## License
MIT
