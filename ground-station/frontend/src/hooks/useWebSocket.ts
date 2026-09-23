import { useEffect, useRef } from 'react';
import { useAppStore } from '../stores/appStore';

function playAlertBeep() {
  try {
    const Ctx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    if (!Ctx) return;
    const ctx = new Ctx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'square';
    osc.frequency.value = 880;
    gain.gain.value = 0.08;
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.25);
    osc.onended = () => void ctx.close();
  } catch {
    // audio may be blocked before user gesture — ignore
  }
}

export function useWebSocket(url: string = 'ws://localhost:8000/ws') {
  const wsRef = useRef<WebSocket | null>(null);
  const lastDetectionAtRef = useRef(0);
  const { updateUAV, addDetection } = useAppStore();
  const reconnectNonce = useAppStore((s) => s.reconnectNonce);

  useEffect(() => {
    let closed = false;
    let retryTimer: number | undefined;

    const connect = () => {
      if (closed) return;
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
              const { hasRealGps } = useAppStore.getState();
              updateUAV({
                altitude: data.altitude,
                speed: data.speed,
                heading: data.heading,
                battery: data.battery,
                ...(hasRealGps ? {} : { lat: data.lat, lng: data.lng }),
              });
            } else if (data.type === 'detection') {
              const state = useAppStore.getState();
              const { mission, alerts } = state.settings;
              const confidence = Number(data.confidence) || 0;

              if (confidence < mission.minConfidence) return;

              const now = Date.now();
              if (mission.detectionCooldown > 0 && now - lastDetectionAtRef.current < mission.detectionCooldown * 1000) {
                return;
              }
              lastDetectionAtRef.current = now;

              const lowConfidence = confidence < mission.minConfidence + 15;
              const autoAck = mission.autoAcknowledge && lowConfidence;

              if (alerts.soundAlerts) playAlertBeep();

              addDetection({
                id: data.id,
                timestamp: new Date(data.timestamp).toLocaleTimeString(),
                confidence,
                lat: data.lat,
                lng: data.lng,
                altitude: data.altitude,
                distance: data.distance,
                status: autoAck ? 'acknowledged' : 'new',
              });

              if (!autoAck && alerts.popupsEnabled) {
                useAppStore.getState().setModalOpen(true);
              }
            }
          } catch (err) {
            console.error('WS parse error:', err);
          }
        };

        ws.onerror = (err) => {
          console.error('WS error:', err);
        };

        ws.onclose = () => {
          if (closed) return;
          console.log('WebSocket disconnected, reconnecting...');
          retryTimer = window.setTimeout(connect, 3000);
        };
      } catch (err) {
        console.error('WebSocket connection error:', err);
        retryTimer = window.setTimeout(connect, 3000);
      }
    };

    connect();

    return () => {
      closed = true;
      if (retryTimer) window.clearTimeout(retryTimer);
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.close();
      }
    };
  }, [url, reconnectNonce, updateUAV, addDetection]);

  const send = (data: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  };

  return { send, ws: wsRef };
}
