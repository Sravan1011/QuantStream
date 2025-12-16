import { useEffect, useRef, useCallback } from 'react';
import { useStore } from '@/lib/store';
import { WS_URL } from '@/lib/api';

export function useWebSocket() {
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const { setWsConnected, updatePrice } = useStore();

    const connect = useCallback(() => {
        try {
            const ws = new WebSocket(WS_URL);

            ws.onopen = () => {
                console.log('WebSocket connected');
                setWsConnected(true);

                // Send subscribe message
                ws.send(JSON.stringify({
                    type: 'subscribe',
                    symbols: ['btcusdt', 'ethusdt']
                }));
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    if (data.type === 'update' && data.data) {
                        // Update prices in real-time
                        Object.entries(data.data).forEach(([symbol, tickData]: [string, any]) => {
                            if (tickData.price) {
                                updatePrice(symbol, tickData.price);
                            }
                        });
                    }
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            ws.onclose = () => {
                console.log('WebSocket disconnected');
                setWsConnected(false);
                wsRef.current = null;

                // Attempt to reconnect after 3 seconds
                reconnectTimeoutRef.current = setTimeout(() => {
                    console.log('Attempting to reconnect...');
                    connect();
                }, 3000);
            };

            wsRef.current = ws;
        } catch (error) {
            console.error('Error creating WebSocket:', error);
            setWsConnected(false);
        }
    }, [setWsConnected, updatePrice]);

    useEffect(() => {
        connect();

        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [connect]);

    return {
        ws: wsRef.current,
        isConnected: wsRef.current?.readyState === WebSocket.OPEN,
    };
}
