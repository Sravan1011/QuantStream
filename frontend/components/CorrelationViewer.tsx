'use client';

import { useState } from 'react';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import { TrendingUp, Loader2, Info } from 'lucide-react';

export function CorrelationViewer() {
    const { selectedSymbols, timeframe } = useStore();
    const [loading, setLoading] = useState(false);
    const [showModal, setShowModal] = useState(false);
    const [symbol1, setSymbol1] = useState('');
    const [symbol2, setSymbol2] = useState('');
    const [window, setWindow] = useState(20);
    const [result, setResult] = useState<{
        correlation: number;
        rolling_correlation: number[];
    } | null>(null);

    const handleCalculate = async () => {
        if (!symbol1 || !symbol2) return;

        setLoading(true);
        try {
            const response = await api.getCorrelation(symbol1, symbol2, timeframe, window);
            setResult(response);
        } catch (error) {
            console.error('Error calculating correlation:', error);
            alert('Failed to calculate correlation. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const openModal = () => {
        if (selectedSymbols.length >= 2) {
            setSymbol1(selectedSymbols[0]);
            setSymbol2(selectedSymbols[1]);
        } else if (selectedSymbols.length === 1) {
            setSymbol1(selectedSymbols[0]);
        }
        setShowModal(true);
        setResult(null);
    };

    return (
        <>
            <button
                onClick={openModal}
                className="w-full px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm font-semibold transition-colors"
            >
                View Correlation
            </button>

            {/* Correlation Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
                        <div className="flex items-center gap-2 mb-4">
                            <TrendingUp className="w-6 h-6 text-purple-400" />
                            <h3 className="text-xl font-bold text-white">Correlation Analysis</h3>
                        </div>

                        <div className="space-y-4">
                            {/* Symbol 1 */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1">
                                    Symbol 1
                                </label>
                                <select
                                    value={symbol1}
                                    onChange={(e) => setSymbol1(e.target.value)}
                                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                                >
                                    <option value="">Select symbol</option>
                                    {selectedSymbols.map((symbol) => (
                                        <option key={symbol} value={symbol}>
                                            {symbol.toUpperCase()}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Symbol 2 */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1">
                                    Symbol 2
                                </label>
                                <select
                                    value={symbol2}
                                    onChange={(e) => setSymbol2(e.target.value)}
                                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                                >
                                    <option value="">Select symbol</option>
                                    {selectedSymbols.map((symbol) => (
                                        <option key={symbol} value={symbol}>
                                            {symbol.toUpperCase()}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Window */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1">
                                    Rolling Window
                                </label>
                                <select
                                    value={window}
                                    onChange={(e) => setWindow(parseInt(e.target.value))}
                                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                                >
                                    <option value={10}>10 periods</option>
                                    <option value={20}>20 periods</option>
                                    <option value={30}>30 periods</option>
                                    <option value={50}>50 periods</option>
                                </select>
                            </div>

                            {/* Info */}
                            <div className="bg-purple-900/30 border border-purple-700 rounded-lg p-3">
                                <div className="flex gap-2">
                                    <Info className="w-4 h-4 text-purple-300 flex-shrink-0 mt-0.5" />
                                    <p className="text-sm text-purple-300">
                                        Correlation measures how two assets move together.
                                        Values range from -1 (inverse) to +1 (perfect correlation).
                                    </p>
                                </div>
                            </div>

                            {/* Results */}
                            {result && (
                                <div className="bg-slate-900 border border-slate-600 rounded-lg p-4">
                                    <h4 className="text-sm font-semibold text-slate-300 mb-3">Results</h4>

                                    <div className="space-y-3">
                                        <div>
                                            <p className="text-xs text-slate-400 mb-1">Current Correlation</p>
                                            <p className={`text-2xl font-bold ${(result.correlation ?? 0) > 0.7 ? 'text-green-400' :
                                                    (result.correlation ?? 0) < -0.7 ? 'text-red-400' :
                                                        'text-yellow-400'
                                                }`}>
                                                {result.correlation?.toFixed(4) ?? 'N/A'}
                                            </p>
                                        </div>

                                        <div>
                                            <p className="text-xs text-slate-400 mb-1">Interpretation</p>
                                            <p className="text-sm text-slate-300">
                                                {Math.abs(result.correlation ?? 0) > 0.7 ? (
                                                    (result.correlation ?? 0) > 0 ?
                                                        '🟢 Strong positive correlation' :
                                                        '🔴 Strong negative correlation'
                                                ) : Math.abs(result.correlation ?? 0) > 0.3 ? (
                                                    (result.correlation ?? 0) > 0 ?
                                                        '🟡 Moderate positive correlation' :
                                                        '🟡 Moderate negative correlation'
                                                ) : (
                                                    '⚪ Weak correlation'
                                                )}
                                            </p>
                                        </div>

                                        {result.rolling_correlation && result.rolling_correlation.length > 0 && (
                                            <div>
                                                <p className="text-xs text-slate-400 mb-1">Rolling Statistics</p>
                                                <div className="grid grid-cols-2 gap-2 text-sm">
                                                    <div>
                                                        <span className="text-slate-400">Min:</span>
                                                        <span className="text-white ml-2">
                                                            {Math.min(...result.rolling_correlation).toFixed(3)}
                                                        </span>
                                                    </div>
                                                    <div>
                                                        <span className="text-slate-400">Max:</span>
                                                        <span className="text-white ml-2">
                                                            {Math.max(...result.rolling_correlation).toFixed(3)}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Actions */}
                        <div className="flex gap-2 mt-6">
                            <button
                                onClick={handleCalculate}
                                disabled={loading || !symbol1 || !symbol2}
                                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-colors"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        Calculating...
                                    </>
                                ) : (
                                    <>
                                        <TrendingUp className="w-4 h-4" />
                                        Calculate
                                    </>
                                )}
                            </button>
                            <button
                                onClick={() => setShowModal(false)}
                                disabled={loading}
                                className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-colors"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
