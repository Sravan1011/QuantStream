'use client';

import { useEffect, useState } from 'react';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';

interface StatsCardProps {
    symbol: string;
}

export function StatsCard({ symbol }: StatsCardProps) {
    const { stats, timeframe, window, setStats } = useStore();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await api.getBasicStats(symbol, timeframe, window);
                // The API returns stats directly, not wrapped in response.stats
                if (!response.error && response.current_price !== undefined) {
                    setStats(symbol, response);
                }
            } catch (error) {
                console.error('Error fetching stats:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
        const interval = setInterval(fetchStats, 3000);

        return () => clearInterval(interval);
    }, [symbol, timeframe, window, setStats]);

    const symbolStats = stats[symbol];

    if (loading || !symbolStats) {
        return (
            <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
                <div className="animate-pulse">
                    <div className="h-4 bg-slate-700 rounded w-1/2 mb-4"></div>
                    <div className="h-8 bg-slate-700 rounded w-3/4"></div>
                </div>
            </div>
        );
    }

    const {
        current_price,
        price_change,
        price_change_pct,
        rolling_mean,
        rolling_std,
        high_24h,
        low_24h,
        avg_volume,
        current_volume,
    } = symbolStats;

    const isPositive = price_change >= 0;

    return (
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">{symbol.toUpperCase()}</h3>
                <Activity className="w-5 h-5 text-blue-400" />
            </div>

            <div className="mb-4">
                <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold text-white">
                        ${current_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                    <div className={`flex items-center gap-1 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                        {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                        <span className="text-sm font-semibold">
                            {isPositive ? '+' : ''}{price_change.toFixed(2)} ({price_change_pct.toFixed(2)}%)
                        </span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-800 rounded-lg p-2">
                    <p className="text-xs text-slate-400">24h High</p>
                    <p className="text-sm font-semibold text-green-400">${high_24h.toFixed(2)}</p>
                </div>
                <div className="bg-slate-800 rounded-lg p-2">
                    <p className="text-xs text-slate-400">24h Low</p>
                    <p className="text-sm font-semibold text-red-400">${low_24h.toFixed(2)}</p>
                </div>
                <div className="bg-slate-800 rounded-lg p-2">
                    <p className="text-xs text-slate-400">Rolling Mean</p>
                    <p className="text-sm font-semibold text-slate-300">${rolling_mean.toFixed(2)}</p>
                </div>
                <div className="bg-slate-800 rounded-lg p-2">
                    <p className="text-xs text-slate-400">Rolling Std</p>
                    <p className="text-sm font-semibold text-slate-300">${rolling_std.toFixed(2)}</p>
                </div>
                <div className="bg-slate-800 rounded-lg p-2">
                    <p className="text-xs text-slate-400">Avg Volume</p>
                    <p className="text-sm font-semibold text-slate-300">{avg_volume.toFixed(4)}</p>
                </div>
                <div className="bg-slate-800 rounded-lg p-2">
                    <p className="text-xs text-slate-400">Current Vol</p>
                    <p className="text-sm font-semibold text-slate-300">{current_volume.toFixed(4)}</p>
                </div>
            </div>
        </div>
    );
}
