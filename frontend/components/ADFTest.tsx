'use client';

import { useState } from 'react';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import { FlaskConical, Loader2, Info, CheckCircle, XCircle } from 'lucide-react';

export function ADFTest() {
    const { selectedSymbols, timeframe } = useStore();
    const [loading, setLoading] = useState(false);
    const [showModal, setShowModal] = useState(false);
    const [testType, setTestType] = useState<'single' | 'spread'>('single');
    const [symbol, setSymbol] = useState('');
    const [symbol1, setSymbol1] = useState('');
    const [symbol2, setSymbol2] = useState('');
    const [lookback, setLookback] = useState(100);
    const [result, setResult] = useState<{
        statistic: number;
        p_value: number;
        critical_values: Record<string, number>;
        is_stationary: boolean;
    } | null>(null);

    const handleRunTest = async () => {
        setLoading(true);
        try {
            let response;
            if (testType === 'single') {
                if (!symbol) return;
                response = await api.getADF(symbol, timeframe);
            } else {
                if (!symbol1 || !symbol2) return;
                response = await api.getSpreadADF(symbol1, symbol2, timeframe, lookback);
            }
            setResult(response);
        } catch (error) {
            console.error('Error running ADF test:', error);
            alert('Failed to run ADF test. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const openModal = () => {
        if (selectedSymbols.length >= 2) {
            setSymbol1(selectedSymbols[0]);
            setSymbol2(selectedSymbols[1]);
            setTestType('spread');
        } else if (selectedSymbols.length === 1) {
            setSymbol(selectedSymbols[0]);
            setTestType('single');
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
                Run ADF Test
            </button>

            {/* ADF Test Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
                        <div className="flex items-center gap-2 mb-4">
                            <FlaskConical className="w-6 h-6 text-cyan-400" />
                            <h3 className="text-xl font-bold text-white">ADF Stationarity Test</h3>
                        </div>

                        <div className="space-y-4">
                            {/* Test Type */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1">
                                    Test Type
                                </label>
                                <div className="grid grid-cols-2 gap-2">
                                    <button
                                        onClick={() => setTestType('single')}
                                        className={`px-4 py-2 rounded-lg font-semibold transition-colors ${testType === 'single'
                                            ? 'bg-cyan-600 text-white'
                                            : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                            }`}
                                    >
                                        Single Symbol
                                    </button>
                                    <button
                                        onClick={() => setTestType('spread')}
                                        className={`px-4 py-2 rounded-lg font-semibold transition-colors ${testType === 'spread'
                                            ? 'bg-cyan-600 text-white'
                                            : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                            }`}
                                    >
                                        Spread
                                    </button>
                                </div>
                            </div>

                            {/* Single Symbol Test */}
                            {testType === 'single' && (
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-1">
                                        Symbol
                                    </label>
                                    <select
                                        value={symbol}
                                        onChange={(e) => setSymbol(e.target.value)}
                                        className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                                    >
                                        <option value="">Select symbol</option>
                                        {selectedSymbols.map((sym) => (
                                            <option key={sym} value={sym}>
                                                {sym.toUpperCase()}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            )}

                            {/* Spread Test */}
                            {testType === 'spread' && (
                                <>
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
                                            {selectedSymbols.map((sym) => (
                                                <option key={sym} value={sym}>
                                                    {sym.toUpperCase()}
                                                </option>
                                            ))}
                                        </select>
                                    </div>

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
                                            {selectedSymbols.map((sym) => (
                                                <option key={sym} value={sym}>
                                                    {sym.toUpperCase()}
                                                </option>
                                            ))}
                                        </select>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-slate-300 mb-1">
                                            Lookback Period
                                        </label>
                                        <select
                                            value={lookback}
                                            onChange={(e) => setLookback(parseInt(e.target.value))}
                                            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                                        >
                                            <option value={50}>50 periods</option>
                                            <option value={100}>100 periods</option>
                                            <option value={200}>200 periods</option>
                                            <option value={500}>500 periods</option>
                                        </select>
                                    </div>
                                </>
                            )}

                            {/* Info */}
                            <div className="bg-cyan-900/30 border border-cyan-700 rounded-lg p-3">
                                <div className="flex gap-2">
                                    <Info className="w-4 h-4 text-cyan-300 flex-shrink-0 mt-0.5" />
                                    <p className="text-sm text-cyan-300">
                                        The ADF test checks if a time series is stationary (mean-reverting).
                                        Stationary spreads are suitable for pairs trading.
                                    </p>
                                </div>
                            </div>

                            {/* Results */}
                            {result && (
                                <div className="bg-slate-900 border border-slate-600 rounded-lg p-4">
                                    <h4 className="text-sm font-semibold text-slate-300 mb-3">Test Results</h4>

                                    <div className="space-y-3">
                                        {/* Stationarity */}
                                        <div className="flex items-center gap-2 p-3 rounded-lg bg-slate-800">
                                            {result.is_stationary ? (
                                                <>
                                                    <CheckCircle className="w-5 h-5 text-green-400" />
                                                    <div>
                                                        <p className="text-sm font-semibold text-green-400">Stationary</p>
                                                        <p className="text-xs text-slate-400">Series is mean-reverting</p>
                                                    </div>
                                                </>
                                            ) : (
                                                <>
                                                    <XCircle className="w-5 h-5 text-red-400" />
                                                    <div>
                                                        <p className="text-sm font-semibold text-red-400">Non-Stationary</p>
                                                        <p className="text-xs text-slate-400">Series has a unit root</p>
                                                    </div>
                                                </>
                                            )}
                                        </div>

                                        {/* Statistics */}
                                        <div className="grid grid-cols-2 gap-3">
                                            <div>
                                                <p className="text-xs text-slate-400 mb-1">ADF Statistic</p>
                                                <p className="text-lg font-bold text-white">
                                                    {result.statistic?.toFixed(4) ?? 'N/A'}
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-xs text-slate-400 mb-1">P-Value</p>
                                                <p className={`text-lg font-bold ${(result.p_value ?? 1) < 0.05 ? 'text-green-400' : 'text-red-400'
                                                    }`}>
                                                    {result.p_value?.toFixed(4) ?? 'N/A'}
                                                </p>
                                            </div>
                                        </div>

                                        {/* Critical Values */}
                                        {result.critical_values && Object.keys(result.critical_values).length > 0 && (
                                            <div>
                                                <p className="text-xs text-slate-400 mb-2">Critical Values</p>
                                                <div className="space-y-1">
                                                    {Object.entries(result.critical_values).map(([level, value]) => (
                                                        <div key={level} className="flex justify-between text-sm">
                                                            <span className="text-slate-400">{level}:</span>
                                                            <span className={`font-mono ${(result.statistic ?? 0) < value ? 'text-green-400' : 'text-slate-300'
                                                                }`}>
                                                                {value?.toFixed(4) ?? 'N/A'}
                                                            </span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* Interpretation */}
                                        <div className="bg-slate-800 rounded p-2">
                                            <p className="text-xs text-slate-400 mb-1">Interpretation</p>
                                            <p className="text-sm text-slate-300">
                                                {(result.p_value ?? 1) < 0.05 ? (
                                                    <>
                                                        ✅ P-value &lt; 0.05: Reject null hypothesis.
                                                        The series is stationary and suitable for mean reversion strategies.
                                                    </>
                                                ) : (
                                                    <>
                                                        ❌ P-value ≥ 0.05: Cannot reject null hypothesis.
                                                        The series may not be suitable for mean reversion.
                                                    </>
                                                )}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Actions */}
                        <div className="flex gap-2 mt-6">
                            <button
                                onClick={handleRunTest}
                                disabled={loading || (testType === 'single' ? !symbol : !symbol1 || !symbol2)}
                                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-colors"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        Running Test...
                                    </>
                                ) : (
                                    <>
                                        <FlaskConical className="w-4 h-4" />
                                        Run Test
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
