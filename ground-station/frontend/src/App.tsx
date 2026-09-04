import { useEffect, useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { SurvivorModal } from './components/SurvivorModal';
import { Dashboard } from './pages/Dashboard';
import { LiveFeedPage } from './pages/LiveFeedPage';
import { DetectionsPage } from './pages/DetectionsPage';
import { MapPage } from './pages/MapPage';
import { SettingsPage } from './pages/SettingsPage';
import { useAppStore } from './stores/appStore';
import { useWebSocket } from './hooks/useWebSocket';

function App() {
  const { activeTab, modalOpen } = useAppStore();
  const [wsConnected, setWsConnected] = useState(false);

  const ws = useWebSocket('ws://localhost:8000/ws');

  useEffect(() => {
    if (ws && ws.ws) {
      const checkConnection = setInterval(() => {
        setWsConnected(ws.ws.current?.readyState === WebSocket.OPEN);
      }, 1000);
      return () => clearInterval(checkConnection);
    }
  }, [ws]);

  useEffect(() => {
    if (wsConnected) return;

    const conditions = ['Partly Cloudy', 'Sunny', 'Overcast', 'Light Rain', 'Clear'];

    const telemetryInterval = setInterval(() => {
      const state = useAppStore.getState();
      const time = Date.now() / 5000;
      const survivor = state.survivor;
      
      state.updateUAV({
        altitude: Math.max(0, state.uav.altitude + (Math.random() - 0.5) * 0.5),
        speed: Math.max(0, state.uav.speed + (Math.random() - 0.5) * 0.2),
        battery: Math.max(0, state.uav.battery - (Math.random() > 0.95 ? 0.1 : 0)),
        heading: (state.uav.heading + 2) % 360,
        lat: survivor.lat + Math.sin(time) * 0.001,
        lng: survivor.lng + Math.cos(time) * 0.001,
      });

      state.updateEnvironment({
        temperature: Math.round((25 + Math.random() * 8) * 10) / 10,
        condition: conditions[Math.floor(Math.random() * conditions.length)],
      });
    }, 2000);

    return () => clearInterval(telemetryInterval);
  }, [wsConnected]);

  useEffect(() => {
    const missionInterval = setInterval(() => {
      useAppStore.getState().incrementMissionTime();
    }, 1000);
    return () => clearInterval(missionInterval);
  }, []);

  useEffect(() => {
    if (modalOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
  }, [modalOpen]);

  return (
    <div className="h-screen w-screen flex text-sm font-sans">
      <Sidebar />
      <main className="flex-1 flex flex-col relative overflow-hidden bg-slate-100">
        <Header />
        <div className="flex-1 overflow-y-auto lg:overflow-hidden p-4 lg:p-6 scroll-smooth">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'livefeed' && <LiveFeedPage />}
          {activeTab === 'detections' && <DetectionsPage />}
          {activeTab === 'map' && <MapPage />}
          {activeTab === 'settings' && <SettingsPage />}
        </div>
      </main>
      <SurvivorModal />
    </div>
  );
}

export default App;
