'use client';

import { useState, useEffect } from 'react';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import { Bell, Plus, Trash2, AlertCircle } from 'lucide-react';

export function AlertManager() {
    const { alerts, setAlerts } = useStore();
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newAlert, setNewAlert] = useState({
        name: '',
        symbol: 'btcusdt',
        metric: 'price',
        condition: '>',
        threshold: 0,
    });

    useEffect(() => {
        fetchAlerts();
        const interval = setInterval(fetchAlerts, 5000);
        return () => clearInterval(interval);
    }, []);

    const fetchAlerts = async () => {
        try {
            const response = await api.getAlerts();
            if (response.alerts) {
                setAlerts(response.alerts);
            }
        } catch (error) {
            console.error('Error fetching alerts:', error);
        }
    };

    const handleCreateAlert = async () => {
        try {
            await api.createAlert(newAlert);
            setShowCreateModal(false);
            setNewAlert({
                name: '',
                symbol: 'btcusdt',
                metric: 'price',
                condition: '>',
                threshold: 0,
            });
            fetchAlerts();
        } catch (error) {
            console.error('Error creating alert:', error);
        }
    };

    const handleDeleteAlert = async (id: number) => {
        try {
            await api.deleteAlert(id);
            fetchAlerts();
        } catch (error) {
            console.error('Error deleting alert:', error);
        }
    };

    return (
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Bell className="w-5 h-5 text-yellow-400" />
                    <h3 className="text-lg font-semibold text-white">Alerts</h3>
                </div>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="flex items-center gap-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold transition-colors"
                >
                    <Plus className="w-4 h-4" />
                    New Alert
                </button>
            </div>

            {alerts.length === 0 ? (
                <div className="text-center py-8 text-slate-400">
                    <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No alerts configured</p>
                </div>
            ) : (
                <div className="space-y-2">
                    {alerts.map((alert) => (
                        <div
                            key={alert.id}
                            className="flex items-center justify-between bg-slate-800 rounded-lg p-3"
                        >
                            <div>
                                <p className="font-semibold text-white">{alert.name}</p>
                                <p className="text-sm text-slate-400">
                                    {alert.symbol.toUpperCase()} {alert.metric} {alert.condition} {alert.threshold}
                                </p>
                            </div>
                            <button
                                onClick={() => handleDeleteAlert(alert.id)}
                                className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
                            >
                                <Trash2 className="w-4 h-4 text-red-400" />
                            </button>
                        </div>
                    ))}
                </div>
            )}

            {/* Create Alert Modal */}
            {showCreateModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md">
                        <h3 className="text-xl font-bold text-white mb-4">Create New Alert</h3>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1">
                                    Alert Name
                                </label>
                                <input
                                    type="text"
                                    value={newAlert.name}
                                    onChange={(e) => setNewAlert({ ...newAlert, name: e.target.value })}
                                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                                    placeholder="e.g., BTC High Price Alert"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1">
                                    Symbol
                                </label>
                                <select
                                    value={newAlert.symbol}
                                    onChange={(e) => setNewAlert({ ...newAlert, symbol: e.target.value })}
                                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                                >
                                    <option value="btcusdt">BTCUSDT</option>
                                    <option value="ethusdt">ETHUSDT</option>
                                    <option value="btcusdt_ethusdt">BTC/ETH Pair</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1">
                                    Metric
                                </label>
                                <select
                                    value={newAlert.metric}
                                    onChange={(e) => setNewAlert({ ...newAlert, metric: e.target.value })}
                                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                                >
                                    <option value="price">Price</option>
                                    <option value="z_score">Z-Score</option>
                                    <option value="volume">Volume</option>
                                    <option value="volatility">Volatility</option>
                                </select>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-1">
                                        Condition
                                    </label>
                                    <select
                                        value={newAlert.condition}
                                        onChange={(e) => setNewAlert({ ...newAlert, condition: e.target.value })}
                                        className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                                    >
                                        <option value=">">{'>'}</option>
                                        <option value="<">{'<'}</option>
                                        <option value=">=">{'>='}</option>
                                        <option value="<=">{'<='}</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-1">
                                        Threshold
                                    </label>
                                    <input
                                        type="number"
                                        value={newAlert.threshold}
                                        onChange={(e) => setNewAlert({ ...newAlert, threshold: parseFloat(e.target.value) })}
                                        className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
                                        step="0.01"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="flex gap-2 mt-6">
                            <button
                                onClick={handleCreateAlert}
                                className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors"
                            >
                                Create Alert
                            </button>
                            <button
                                onClick={() => setShowCreateModal(false)}
                                className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-semibold transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
