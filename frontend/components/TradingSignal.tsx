'use client';

import { useStore } from '@/lib/store';
import { TrendingUp, TrendingDown, Minus, AlertCircle } from 'lucide-react';

export function TradingSignal() {
    const { spreadData } = useStore();

    if (!spreadData || spreadData.current_zscore === undefined) {
        return (
            <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-2">Trading Signal</h3>
                <p className="text-slate-400 text-sm">Waiting for spread data...</p>
            </div>
        );
    }

    const { current_zscore, symbol1, symbol2 } = spreadData;
    const absZ = Math.abs(current_zscore);

    // Determine signal
    let signal: 'strong_buy' | 'buy' | 'neutral' | 'sell' | 'strong_sell';
    let color: string;
    let bgColor: string;
    let icon: React.ReactNode;
    let action: string;
    let description: string;

    if (current_zscore < -2) {
        signal = 'strong_buy';
        color = 'text-green-400';
        bgColor = 'bg-green-900/30 border-green-700';
        icon = <TrendingUp className="w-6 h-6" />;
        action = `BUY ${symbol1.toUpperCase()}`;
        description = `Spread is ${absZ.toFixed(2)} std devs below mean. Strong mean reversion opportunity.`;
    } else if (current_zscore < -1) {
        signal = 'buy';
        color = 'text-green-300';
        bgColor = 'bg-green-900/20 border-green-700/50';
        icon = <TrendingUp className="w-6 h-6" />;
        action = 'Watch for Entry';
        description = `Spread is ${absZ.toFixed(2)} std devs below mean. Monitor for stronger signal.`;
    } else if (current_zscore > 2) {
        signal = 'strong_sell';
        color = 'text-red-400';
        bgColor = 'bg-red-900/30 border-red-700';
        icon = <TrendingDown className="w-6 h-6" />;
        action = `SELL ${symbol1.toUpperCase()}`;
        description = `Spread is ${absZ.toFixed(2)} std devs above mean. Strong mean reversion opportunity.`;
    } else if (current_zscore > 1) {
        signal = 'sell';
        color = 'text-red-300';
        bgColor = 'bg-red-900/20 border-red-700/50';
        icon = <TrendingDown className="w-6 h-6" />;
        action = 'Watch for Entry';
        description = `Spread is ${absZ.toFixed(2)} std devs above mean. Monitor for stronger signal.`;
    } else {
        signal = 'neutral';
        color = 'text-slate-400';
        bgColor = 'bg-slate-800 border-slate-600';
        icon = <Minus className="w-6 h-6" />;
        action = 'No Action';
        description = `Spread is within normal range (${absZ.toFixed(2)} std devs). Wait for extreme values.`;
    }

    return (
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-white">Trading Signal</h3>
                <AlertCircle className="w-5 h-5 text-blue-400" />
            </div>

            <div className={`border rounded-lg p-4 ${bgColor}`}>
                <div className="flex items-center gap-3 mb-3">
                    <div className={color}>
                        {icon}
                    </div>
                    <div>
                        <p className={`text-xl font-bold ${color}`}>{action}</p>
                        <p className="text-xs text-slate-400">
                            {symbol1.toUpperCase()} / {symbol2.toUpperCase()} Spread
                        </p>
                    </div>
                </div>

                <p className="text-sm text-slate-300 mb-3">{description}</p>

                {(signal === 'strong_buy' || signal === 'strong_sell') && (
                    <div className="mt-3 pt-3 border-t border-slate-700">
                        <p className="text-xs font-semibold text-white mb-2">Suggested Action:</p>
                        <div className="space-y-1 text-xs text-slate-300">
                            {signal === 'strong_buy' ? (
                                <>
                                    <p>• Long {symbol1.toUpperCase()} (Buy)</p>
                                    <p>• Short {symbol2.toUpperCase()} (Sell)</p>
                                    <p>• Target: Z-score returns to 0</p>
                                    <p>• Stop: Z-score &lt; {(current_zscore - 1).toFixed(1)}</p>
                                </>
                            ) : (
                                <>
                                    <p>• Short {symbol1.toUpperCase()} (Sell)</p>
                                    <p>• Long {symbol2.toUpperCase()} (Buy)</p>
                                    <p>• Target: Z-score returns to 0</p>
                                    <p>• Stop: Z-score &gt; {(current_zscore + 1).toFixed(1)}</p>
                                </>
                            )}
                        </div>
                    </div>
                )}

                {signal === 'neutral' && (
                    <div className="mt-3 pt-3 border-t border-slate-600">
                        <p className="text-xs text-slate-400">
                            💡 Wait for Z-score to reach ±2 for high-confidence signals
                        </p>
                    </div>
                )}
            </div>

            <div className="mt-3 flex items-center justify-between text-xs">
                <span className="text-slate-500">Current Z-Score:</span>
                <span className={`font-mono font-bold ${color}`}>
                    {current_zscore.toFixed(3)}
                </span>
            </div>
        </div>
    );
}
