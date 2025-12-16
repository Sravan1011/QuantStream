// API Response Types
export interface OHLCResponse {
    ohlc: OHLC[];
    error?: string;
}

export interface TicksResponse {
    ticks: Tick[];
    error?: string;
}

export interface BasicStatsResponse extends BasicStats {
    error?: string;
    stats?: string; // Optional field indicating data source (computed_from_ticks or computed_from_ohlc)
}

export interface ExportResponse {
    filename: string;
    data: string;
    count: number;
}

export interface VolatilityResponse {
    volatility: number;
    rolling_volatility: number[];
}

export interface HedgeRatioResponse {
    hedge_ratio: number;
    method: string;
}

export interface SpreadResponse {
    symbol1: string;
    symbol2: string;
    hedge_ratio: number;
    current_spread: number;
    spread_mean: number;
    spread_std: number;
    current_zscore: number;
    price1: number;
    price2: number;
    error?: string;
}

export interface CorrelationResponse {
    correlation: number;
    rolling_correlation: number[];
}

export interface ADFResponse {
    statistic: number;
    p_value: number;
    critical_values: Record<string, number>;
    is_stationary: boolean;
}

export interface AlertsResponse {
    alerts: Alert[];
}

export interface AlertTriggersResponse {
    triggers: AlertTrigger[];
}

export interface AlertTrigger {
    id: number;
    alert_id: number;
    alert_name: string;
    triggered_at: string;
    metric_value: number;
    threshold: number;
}

// Data Types (re-exported from store for convenience)
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

export interface Alert {
    id: number;
    name: string;
    symbol: string;
    metric: string;
    condition: string;
    threshold: number;
    is_active: boolean;
}
