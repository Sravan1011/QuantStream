'use client';

import { useWebSocket } from '@/hooks/useWebSocket';
import { useStore } from '@/lib/store';
import { PriceChart } from '@/components/charts/PriceChart';
import { SpreadChart } from '@/components/charts/SpreadChart';
import { StatsCard } from '@/components/StatsCard';
import { ControlPanel } from '@/components/ControlPanel';
import { AlertManager } from '@/components/AlertManager';
import { Activity, Wifi, WifiOff } from 'lucide-react';

export default function Dashboard() {
  const { isConnected } = useWebSocket();
  const { selectedSymbols, wsConnected } = useStore();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Trading Analytics Platform</h1>
                <p className="text-sm text-slate-400">Real-time Quantitative Analysis</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {wsConnected ? (
                <div className="flex items-center gap-2 px-3 py-1 bg-green-900/30 border border-green-700 rounded-lg">
                  <Wifi className="w-4 h-4 text-green-400" />
                  <span className="text-sm font-semibold text-green-400">Live</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 px-3 py-1 bg-red-900/30 border border-red-700 rounded-lg">
                  <WifiOff className="w-4 h-4 text-red-400" />
                  <span className="text-sm font-semibold text-red-400">Disconnected</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Left Column - Stats Cards */}
          <div className="col-span-12 lg:col-span-3 space-y-4">
            {selectedSymbols.map((symbol) => (
              <StatsCard key={symbol} symbol={symbol} />
            ))}
            <ControlPanel />
          </div>

          {/* Middle Column - Charts */}
          <div className="col-span-12 lg:col-span-6 space-y-4">
            {selectedSymbols.map((symbol) => (
              <PriceChart key={symbol} symbol={symbol} />
            ))}

            {selectedSymbols.length >= 2 && (
              <SpreadChart
                symbol1={selectedSymbols[0]}
                symbol2={selectedSymbols[1]}
              />
            )}
          </div>

          {/* Right Column - Alerts & Additional Info */}
          <div className="col-span-12 lg:col-span-3 space-y-4">
            <AlertManager />

            {/* System Info */}
            <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3">System Info</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Backend:</span>
                  <span className="text-green-400 font-semibold">Connected</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">WebSocket:</span>
                  <span className={wsConnected ? 'text-green-400' : 'text-red-400'}>
                    {wsConnected ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Data Source:</span>
                  <span className="text-blue-400 font-semibold">Binance</span>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3">Quick Actions</h3>
              <div className="space-y-2">
                <button className="w-full px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm font-semibold transition-colors">
                  Export Data (CSV)
                </button>
                <button className="w-full px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm font-semibold transition-colors">
                  Run ADF Test
                </button>
                <button className="w-full px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm font-semibold transition-colors">
                  View Correlation
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-900/50 mt-12">
        <div className="container mx-auto px-4 py-4">
          <p className="text-center text-sm text-slate-500">
            Trading Analytics Platform • Real-time data from Binance Futures • Built with Next.js & FastAPI
          </p>
        </div>
      </footer>
    </div>
  );
}
