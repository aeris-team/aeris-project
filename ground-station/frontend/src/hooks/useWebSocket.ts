import { useEffect, useRef } from 'react';
import { useAppStore } from '../stores/appStore';

export function useWebSocket(url: string = 'ws://localhost:8000/ws') {
  const wsRef = useRef<WebSocket | null>(null);
  const { updateUAV, addDetection } = useAppStore();

  useEffect(() => {
    const connect = () => {
      try {
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log('WebSocket connected');
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'telemetry') {
              updateUAV({
                altitude: data.altitude,
                speed: data.speed,
                heading: data.heading,
                battery: data.battery,
                lat: data.lat,
                lng: data.lng,
              });
            } else if (data.type === 'detection') {
              addDetection({
                id: data.id,
                timestamp: new Date(data.timestamp).toLocaleTimeString(),
                confidence: data.confidence,
                lat: data.lat,
                lng: data.lng,
                altitude: data.altitude,
                distance: data.distance,
                status: 'new',
              });
            }
          } catch (err) {
            console.error('WS parse error:', err);
          }
        };

        ws.onerror = (err) => {
          console.error('WS error:', err);
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected, reconnecting...');
          setTimeout(connect, 3000);
        };
      } catch (err) {
        console.error('WebSocket connection error:', err);
        setTimeout(connect, 3000);
      }
    };

    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url]);

  const send = (data: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  };

  return { send, ws: wsRef };
}
