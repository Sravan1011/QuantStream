import type {
    OHLCResponse,
    TicksResponse,
    BasicStatsResponse,
    VolatilityResponse,
    HedgeRatioResponse,
    SpreadResponse,
    CorrelationResponse,
    ADFResponse,
    AlertsResponse,
    AlertTriggersResponse,
    ExportResponse,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
    private baseUrl: string;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
    }

    private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options?.headers,
            },
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }

        return response.json();
    }

    // Health & Status
    async getHealth() {
        return this.request<{ status: string }>('/api/health');
    }

    async getStatus() {
        return this.request<{ status: string; ws_connected: boolean }>('/api/status');
    }

    // Data
    async getTicks(symbol: string, limit: number = 100) {
        return this.request<TicksResponse>(`/api/ticks/${symbol}?limit=${limit}`);
    }

    async getOHLC(symbol: string, timeframe: string = '1m', limit: number = 100) {
        return this.request<OHLCResponse>(`/api/ohlc/${symbol}?timeframe=${timeframe}&limit=${limit}`);
    }

    // Analytics
    async getBasicStats(symbol: string, timeframe: string = '1m', window: number = 20) {
        return this.request<BasicStatsResponse>(`/api/analytics/basic/${symbol}?timeframe=${timeframe}&window=${window}`);
    }

    async getVolatility(symbol: string, timeframe: string = '1m', window: number = 20) {
        return this.request<VolatilityResponse>(`/api/analytics/volatility/${symbol}?timeframe=${timeframe}&window=${window}`);
    }

    async getHedgeRatio(symbol1: string, symbol2: string, timeframe: string = '1m', lookback: number = 100, method: string = 'ols') {
        return this.request<HedgeRatioResponse>(`/api/analytics/hedge-ratio?symbol1=${symbol1}&symbol2=${symbol2}&timeframe=${timeframe}&lookback=${lookback}&method=${method}`);
    }

    async getSpread(symbol1: string, symbol2: string, timeframe: string = '1m', lookback: number = 100, window: number = 20) {
        return this.request<SpreadResponse>(`/api/analytics/spread?symbol1=${symbol1}&symbol2=${symbol2}&timeframe=${timeframe}&lookback=${lookback}&window=${window}`);
    }

    async getCorrelation(symbol1: string, symbol2: string, timeframe: string = '1m', window: number = 20) {
        return this.request<CorrelationResponse>(`/api/analytics/correlation?symbol1=${symbol1}&symbol2=${symbol2}&timeframe=${timeframe}&window=${window}`);
    }

    async getADF(symbol: string, timeframe: string = '1m') {
        return this.request<ADFResponse>(`/api/analytics/adf/${symbol}?timeframe=${timeframe}`);
    }

    async getSpreadADF(symbol1: string, symbol2: string, timeframe: string = '1m', lookback: number = 100) {
        return this.request<ADFResponse>(`/api/analytics/spread-adf?symbol1=${symbol1}&symbol2=${symbol2}&timeframe=${timeframe}&lookback=${lookback}`);
    }

    // Alerts
    async createAlert(alert: {
        name: string;
        symbol: string;
        metric: string;
        condition: string;
        threshold: number;
    }) {
        return this.request<{ id: number }>('/api/alerts', {
            method: 'POST',
            body: JSON.stringify(alert),
        });
    }

    async getAlerts(activeOnly: boolean = true) {
        return this.request<AlertsResponse>(`/api/alerts?active_only=${activeOnly}`);
    }

    async deleteAlert(alertId: number) {
        return this.request<{ success: boolean }>(`/api/alerts/${alertId}`, {
            method: 'DELETE',
        });
    }

    async getAlertTriggers() {
        return this.request<AlertTriggersResponse>('/api/alerts/triggers');
    }

    // Export
    async exportTicks(symbol: string, limit: number = 1000) {
        return this.request<ExportResponse>(`/api/export/ticks/${symbol}?limit=${limit}`);
    }

    async exportOHLC(symbol: string, timeframe: string = '1m', limit: number = 500) {
        return this.request<ExportResponse>(`/api/export/ohlc/${symbol}?timeframe=${timeframe}&limit=${limit}`);
    }
}

export const api = new ApiClient(API_BASE_URL);
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
