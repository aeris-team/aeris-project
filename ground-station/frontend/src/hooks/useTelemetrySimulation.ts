import { useEffect } from 'react';
import { useAppStore } from '../stores/appStore';

export function useTelemetrySimulation() {
  useEffect(() => {
    const telemetryInterval = setInterval(() => {
      const state = useAppStore.getState();
      
      const time = Date.now() / 5000;
      const survivor = state.survivor;
      
      state.updateUAV({
        altitude: state.uav.altitude + (Math.random() - 0.5) * 0.5,
        speed: Math.max(0, state.uav.speed + (Math.random() - 0.5) * 0.2),
        battery: Math.max(0, state.uav.battery - (Math.random() > 0.95 ? 0.1 : 0)),
        heading: (state.uav.heading + 2) % 360,
        lat: survivor.lat + Math.sin(time) * 0.001,
        lng: survivor.lng + Math.cos(time) * 0.001,
      });

      state.updateLink('wifi', {
        latency: Math.max(30, state.link.wifi.latency + (Math.random() - 0.5) * 5),
        rssi: state.link.wifi.rssi + (Math.random() - 0.5) * 2,
      });

      state.updateLink('lora', {
        latency: Math.max(60, state.link.lora.latency + (Math.random() - 0.5) * 8),
        rssi: state.link.lora.rssi + (Math.random() - 0.5) * 1.5,
      });
    }, 1500);

    const missionInterval = setInterval(() => {
      useAppStore.getState().incrementMissionTime();
    }, 1000);

    return () => {
      clearInterval(telemetryInterval);
      clearInterval(missionInterval);
    };
  }, []);
}
