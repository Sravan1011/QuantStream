'use client';

import { useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';

interface SpreadChartProps {
    symbol1: string;
    symbol2: string;
}

export function SpreadChart({ symbol1, symbol2 }: SpreadChartProps) {
    const { spreadData, timeframe, window, setSpreadData } = useStore();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.getSpread(symbol1, symbol2, timeframe, 100, window);
                if (!response.error) {
                    setSpreadData(response);
                }
            } catch (error) {
                console.error('Error fetching spread:', error);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);

        return () => clearInterval(interval);
    }, [symbol1, symbol2, timeframe, window, setSpreadData]);

    if (!spreadData) {
        return (
            <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-4">Spread & Z-Score</h3>
                <p className="text-slate-400">Loading spread data...</p>
            </div>
        );
    }

    const { current_zscore, current_spread, spread_mean, spread_std, hedge_ratio } = spreadData;

    // Create visualization data
    const zscoreData = [
        { name: 'Current', value: current_zscore },
    ];

    return (
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">
                Spread & Z-Score: {symbol1.toUpperCase()} / {symbol2.toUpperCase()}
            </h3>

            <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-slate-800 rounded-lg p-3">
                    <p className="text-slate-400 text-sm">Hedge Ratio (β)</p>
                    <p className="text-2xl font-bold text-white">{hedge_ratio.toFixed(4)}</p>
                </div>
                <div className="bg-slate-800 rounded-lg p-3">
                    <p className="text-slate-400 text-sm">Current Spread</p>
                    <p className="text-2xl font-bold text-white">{current_spread.toFixed(2)}</p>
                </div>
                <div className="bg-slate-800 rounded-lg p-3">
                    <p className="text-slate-400 text-sm">Spread Mean</p>
                    <p className="text-xl font-semibold text-slate-300">{spread_mean.toFixed(2)}</p>
                </div>
                <div className="bg-slate-800 rounded-lg p-3">
                    <p className="text-slate-400 text-sm">Spread Std Dev</p>
                    <p className="text-xl font-semibold text-slate-300">{spread_std.toFixed(2)}</p>
                </div>
            </div>

            <div className="bg-slate-800 rounded-lg p-4">
                <h4 className="text-md font-semibold text-white mb-2">Z-Score</h4>
                <div className="flex items-center justify-between mb-2">
                    <span className="text-slate-400">Current:</span>
                    <span className={`text-3xl font-bold ${Math.abs(current_zscore) > 2 ? 'text-red-400' :
                            Math.abs(current_zscore) > 1 ? 'text-yellow-400' :
                                'text-green-400'
                        }`}>
                        {current_zscore.toFixed(3)}
                    </span>
                </div>

                <div className="relative h-8 bg-slate-700 rounded-full overflow-hidden mt-4">
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="absolute left-1/4 w-px h-full bg-yellow-500/30" />
                        <div className="absolute left-1/2 w-px h-full bg-green-500/50" />
                        <div className="absolute left-3/4 w-px h-full bg-yellow-500/30" />
                    </div>
                    <div
                        className="absolute top-0 h-full w-2 bg-blue-500 rounded-full transition-all duration-300"
                        style={{
                            left: `${Math.min(Math.max((current_zscore + 3) / 6 * 100, 0), 100)}%`,
                        }}
                    />
                </div>
                <div className="flex justify-between text-xs text-slate-500 mt-1">
                    <span>-3</span>
                    <span>-2</span>
                    <span>-1</span>
                    <span>0</span>
                    <span>+1</span>
                    <span>+2</span>
                    <span>+3</span>
                </div>
            </div>

            {Math.abs(current_zscore) > 2 && (
                <div className="mt-4 p-3 bg-red-900/30 border border-red-700 rounded-lg">
                    <p className="text-red-400 text-sm font-semibold">
                        ⚠️ Z-score exceeds ±2 threshold - potential mean reversion opportunity
                    </p>
                </div>
            )}
        </div>
    );
}
