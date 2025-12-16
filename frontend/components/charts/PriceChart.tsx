'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';

interface PriceChartProps {
    symbol: string;
}

export function PriceChart({ symbol }: PriceChartProps) {
    const { ohlc, timeframe, setOHLC } = useStore();
    const [tickData, setTickData] = useState<any[]>([]);
    const [useTickFallback, setUseTickFallback] = useState(false);
    const data = ohlc[symbol] || [];

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Try to get OHLC data first
                const response = await api.getOHLC(symbol, timeframe, 100);
                if (response.ohlc && response.ohlc.length > 0) {
                    setOHLC(symbol, response.ohlc);
                    setUseTickFallback(false);
                } else {
                    // Fallback to tick data
                    const tickResponse = await api.getTicks(symbol, 100);
                    if (tickResponse.ticks && tickResponse.ticks.length > 0) {
                        setTickData(tickResponse.ticks);
                        setUseTickFallback(true);
                    }
                }
            } catch (error) {
                console.error('Error fetching chart data:', error);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);

        return () => clearInterval(interval);
    }, [symbol, timeframe, setOHLC]);

    // Prepare chart data based on what's available
    const chartData = useTickFallback
        ? tickData.slice(-50).map((tick, idx) => ({
            time: new Date(tick.timestamp).toLocaleTimeString(),
            price: tick.price,
            volume: tick.size,
        }))
        : data.map((candle) => ({
            time: new Date(candle.timestamp).toLocaleTimeString(),
            price: candle.close,
            high: candle.high,
            low: candle.low,
            volume: candle.volume,
        }));

    if (chartData.length === 0) {
        return (
            <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-4">
                    {symbol.toUpperCase()} Price Chart ({timeframe})
                </h3>
                <div className="h-[300px] flex items-center justify-center text-slate-500">
                    <p>Waiting for data... (collecting ticks)</p>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">
                {symbol.toUpperCase()} Price Chart {useTickFallback ? '(Tick Data)' : `(${timeframe})`}
            </h3>
            <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="time" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" domain={['auto', 'auto']} />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1e293b',
                            border: '1px solid #475569',
                            borderRadius: '8px',
                        }}
                        labelStyle={{ color: '#e2e8f0' }}
                    />
                    <Legend />
                    <Line
                        type="monotone"
                        dataKey="price"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        dot={false}
                        name="Price"
                    />
                    {!useTickFallback && (
                        <>
                            <Line
                                type="monotone"
                                dataKey="high"
                                stroke="#10b981"
                                strokeWidth={1}
                                dot={false}
                                name="High"
                                strokeDasharray="3 3"
                            />
                            <Line
                                type="monotone"
                                dataKey="low"
                                stroke="#ef4444"
                                strokeWidth={1}
                                dot={false}
                                name="Low"
                                strokeDasharray="3 3"
                            />
                        </>
                    )}
                </LineChart>
            </ResponsiveContainer>
            {useTickFallback && (
                <p className="text-xs text-slate-500 mt-2">
                    📊 Displaying last 50 ticks (OHLC data not available yet)
                </p>
            )}
        </div>
    );
}
