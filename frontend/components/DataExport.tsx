'use client';

import { useState } from 'react';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import { Download, FileText, Loader2 } from 'lucide-react';

export function DataExport() {
    const { selectedSymbols, timeframe } = useStore();
    const [loading, setLoading] = useState(false);
    const [exportType, setExportType] = useState<'ticks' | 'ohlc'>('ticks');
    const [showModal, setShowModal] = useState(false);
    const [selectedSymbol, setSelectedSymbol] = useState('');
    const [limit, setLimit] = useState(1000);

    const handleExport = async () => {
        if (!selectedSymbol) return;

        setLoading(true);
        try {
            let response;
            if (exportType === 'ticks') {
                response = await api.exportTicks(selectedSymbol, limit);
            } else {
                response = await api.exportOHLC(selectedSymbol, timeframe, limit);
            }

            // Create blob and download
            const blob = new Blob([response.data], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = response.filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            setShowModal(false);
        } catch (error) {
            console.error('Error exporting data:', error);
            alert('Failed to export data. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <button
                onClick={() => {
                    setSelectedSymbol(selectedSymbols[0] || 'btcusdt');
                    setShowModal(true);
                }}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold transition-colors"
            >
                <Download className="w-4 h-4" />
                Export Data (CSV)
            </button>

            {/* Export Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md">
                        <div className="flex items-center gap-2 mb-4">
                            <FileText className="w-6 h-6 text-blue-400" />
                            <h3 className="text-xl font-bold text-white">Export Data</h3>
                        </div>

                        <div className="space-y-4">
                            {/* Symbol Selection */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1">
                                    Symbol
                                </label>
                                <select
                                    value={selectedSymbol}
                                    onChange={(e) => setSelectedSymbol(e.target.value)}
                                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                                >
                                    {selectedSymbols.map((symbol) => (
                                        <option key={symbol} value={symbol}>
                                            {symbol.toUpperCase()}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Export Type */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1">
                                    Data Type
                                </label>
                                <div className="grid grid-cols-2 gap-2">
                                    <button
                                        onClick={() => setExportType('ticks')}
                                        className={`px-4 py-2 rounded-lg font-semibold transition-colors ${exportType === 'ticks'
                                                ? 'bg-blue-600 text-white'
                                                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                            }`}
                                    >
                                        Tick Data
                                    </button>
                                    <button
                                        onClick={() => setExportType('ohlc')}
                                        className={`px-4 py-2 rounded-lg font-semibold transition-colors ${exportType === 'ohlc'
                                                ? 'bg-blue-600 text-white'
                                                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                            }`}
                                    >
                                        OHLC Data
                                    </button>
                                </div>
                            </div>

                            {/* Limit */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1">
                                    Number of Records
                                </label>
                                <select
                                    value={limit}
                                    onChange={(e) => setLimit(parseInt(e.target.value))}
                                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                                >
                                    <option value={100}>100 records</option>
                                    <option value={500}>500 records</option>
                                    <option value={1000}>1,000 records</option>
                                    <option value={5000}>5,000 records</option>
                                    <option value={10000}>10,000 records</option>
                                </select>
                            </div>

                            {/* Info */}
                            <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-3">
                                <p className="text-sm text-blue-300">
                                    {exportType === 'ticks' ? (
                                        <>
                                            <strong>Tick Data:</strong> Raw price updates with timestamp, price, and size
                                        </>
                                    ) : (
                                        <>
                                            <strong>OHLC Data:</strong> Aggregated {timeframe} candles with open, high, low, close, and volume
                                        </>
                                    )}
                                </p>
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-2 mt-6">
                            <button
                                onClick={handleExport}
                                disabled={loading}
                                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-colors"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        Exporting...
                                    </>
                                ) : (
                                    <>
                                        <Download className="w-4 h-4" />
                                        Download CSV
                                    </>
                                )}
                            </button>
                            <button
                                onClick={() => setShowModal(false)}
                                disabled={loading}
                                className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
