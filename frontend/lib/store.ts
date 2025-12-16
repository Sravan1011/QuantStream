import { create } from 'zustand';

export interface Tick {
    symbol: string;
    timestamp: string;
    price: number;
    size: number;
}

export interface OHLC {
    symbol: string;
    timeframe: string;
    timestamp: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
    trade_count: number;
}

export interface BasicStats {
    symbol: string;
    current_price: number;
    price_change: number;
    price_change_pct: number;
    rolling_mean: number;
    rolling_std: number;
    high_24h: number;
    low_24h: number;
    avg_volume: number;
    current_volume: number;
}

export interface SpreadData {
    symbol1: string;
    symbol2: string;
    hedge_ratio: number;
    current_spread: number;
    spread_mean: number;
    spread_std: number;
    current_zscore: number;
    price1: number;
    price2: number;
}

export interface Alert {
    id: number;
    name: string;
    symbol: string;
    metric: string;
    condition: string;
    threshold: number;
    is_active: boolean;
}

interface AppState {
    // Symbols and settings
    selectedSymbols: string[];
    timeframe: string;
    window: number;

    // Data
    ticks: Record<string, Tick[]>;
    ohlc: Record<string, OHLC[]>;
    stats: Record<string, BasicStats>;
    spreadData: SpreadData | null;
    alerts: Alert[];

    // WebSocket
    wsConnected: boolean;

    // Actions
    setSelectedSymbols: (symbols: string[]) => void;
    setTimeframe: (timeframe: string) => void;
    setWindow: (window: number) => void;
    setTicks: (symbol: string, ticks: Tick[]) => void;
    setOHLC: (symbol: string, ohlc: OHLC[]) => void;
    setStats: (symbol: string, stats: BasicStats) => void;
    setSpreadData: (data: SpreadData | null) => void;
    setAlerts: (alerts: Alert[]) => void;
    setWsConnected: (connected: boolean) => void;
    updatePrice: (symbol: string, price: number) => void;
}

export const useStore = create<AppState>((set) => ({
    // Initial state
    selectedSymbols: ['btcusdt', 'ethusdt'],
    timeframe: '1m',
    window: 20,
    ticks: {},
    ohlc: {},
    stats: {},
    spreadData: null,
    alerts: [],
    wsConnected: false,

    // Actions
    setSelectedSymbols: (symbols) => set({ selectedSymbols: symbols }),
    setTimeframe: (timeframe) => set({ timeframe }),
    setWindow: (window) => set({ window }),
    setTicks: (symbol, ticks) => set((state) => ({
        ticks: { ...state.ticks, [symbol]: ticks }
    })),
    setOHLC: (symbol, ohlc) => set((state) => ({
        ohlc: { ...state.ohlc, [symbol]: ohlc }
    })),
    setStats: (symbol, stats) => set((state) => ({
        stats: { ...state.stats, [symbol]: stats }
    })),
    setSpreadData: (data) => set({ spreadData: data }),
    setAlerts: (alerts) => set({ alerts }),
    setWsConnected: (connected) => set({ wsConnected: connected }),
    updatePrice: (symbol, price) => set((state) => ({
        stats: {
            ...state.stats,
            [symbol]: state.stats[symbol]
                ? { ...state.stats[symbol], current_price: price }
                : state.stats[symbol]
        }
    })),
}));
