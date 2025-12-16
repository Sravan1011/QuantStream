'use client';

import { useStore } from '@/lib/store';
import { Settings2 } from 'lucide-react';

export function ControlPanel() {
    const { selectedSymbols, timeframe, window, setTimeframe, setWindow } = useStore();

    return (
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-4">
                <Settings2 className="w-5 h-5 text-blue-400" />
                <h3 className="text-lg font-semibold text-white">Controls</h3>
            </div>

            <div className="space-y-4">
                {/* Symbols Display */}
                <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                        Active Symbols
                    </label>
                    <div className="flex gap-2">
                        {selectedSymbols.map((symbol) => (
                            <span
                                key={symbol}
                                className="px-3 py-1 bg-blue-600 text-white text-sm font-semibold rounded-full"
                            >
                                {symbol.toUpperCase()}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Timeframe Selector */}
                <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                        Timeframe
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                        {['1s', '1m', '5m'].map((tf) => (
                            <button
                                key={tf}
                                onClick={() => setTimeframe(tf)}
                                className={`px-4 py-2 rounded-lg font-semibold transition-colors ${timeframe === tf
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                                    }`}
                            >
                                {tf}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Rolling Window */}
                <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                        Rolling Window: {window}
                    </label>
                    <input
                        type="range"
                        min="5"
                        max="100"
                        value={window}
                        onChange={(e) => setWindow(parseInt(e.target.value))}
                        className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
                    />
                    <div className="flex justify-between text-xs text-slate-500 mt-1">
                        <span>5</span>
                        <span>50</span>
                        <span>100</span>
                    </div>
                </div>

                {/* Info */}
                <div className="bg-slate-800 rounded-lg p-3 text-sm text-slate-400">
                    <p>• Timeframe: OHLC aggregation interval</p>
                    <p>• Window: Rolling calculation period</p>
                </div>
            </div>
        </div>
    );
}
