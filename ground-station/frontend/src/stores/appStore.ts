import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { UAVTelemetry, CommLinks, SurvivorDetection, Mission } from '../types';
import { navigateToTab } from '../lib/navigation';

export interface Settings {
  comm: {
    wifiSSID: string;
    wifiBandwidth: number;
    loraFrequency: number;
    loraSpreadingFactor: number;
    videoBitrate: number;
    autoReconnect: boolean;
  };
  mission: {
    autoAcknowledge: boolean;
    minConfidence: number;
    detectionCooldown: number;
    homeLat: number;
    homeLng: number;
    geofenceRadius: number;
  };
  alerts: {
    lowBatteryThreshold: number;
    lowSignalThreshold: number;
    maxAltitude: number;
    soundAlerts: boolean;
    popupsEnabled: boolean;
  };
}

interface AppState {
  activeTab: 'dashboard' | 'livefeed' | 'detections' | 'map' | 'settings';
  sidebarOpen: boolean;
  modalOpen: boolean;
  alertAcknowledged: boolean;
  missionTimeSeconds: number;

  uav: UAVTelemetry;
  survivor: { lat: number; lng: number };
  home: { lat: number; lng: number };
  hasRealGps: boolean;
  setRealGpsLocation: (lat: number, lng: number) => void;

  link: CommLinks;

  detections: SurvivorDetection[];
  mission: Mission;

  environment: {
    temperature: number;
    condition: string;
  };

  videoStatus: 'connecting' | 'live' | 'offline' | 'denied';
  setVideoStatus: (status: AppState['videoStatus']) => void;

  settings: Settings;
  updateSettings: (section: keyof Settings, data: Partial<Settings[keyof Settings]>) => void;
  setFullSettings: (settings: Settings) => void;
  resetSettings: () => void;
  reconnectNonce: number;
  bumpReconnect: () => void;

  endMission: () => void;
  startMission: (name: string) => void;
  updateEnvironment: (data: Partial<{ temperature: number; condition: string }>) => void;

  setActiveTab: (tab: AppState['activeTab']) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setModalOpen: (open: boolean) => void;
  acknowledgeAlert: () => void;
  incrementMissionTime: () => void;
  updateUAV: (data: Partial<UAVTelemetry>) => void;
  updateLink: (type: 'wifi' | 'lora', data: Partial<CommLinks['wifi']>) => void;
  addDetection: (detection: SurvivorDetection) => void;
}

const defaultSettings: Settings = {
  comm: {
    wifiSSID: 'AERIS_GCS_5GHz',
    wifiBandwidth: 80,
    loraFrequency: 915,
    loraSpreadingFactor: 7,
    videoBitrate: 5.4,
    autoReconnect: true,
  },
  mission: {
    autoAcknowledge: false,
    minConfidence: 75,
    detectionCooldown: 10,
    homeLat: 14.2485,
    homeLng: 120.7290,
    geofenceRadius: 500,
  },
  alerts: {
    lowBatteryThreshold: 30,
    lowSignalThreshold: -80,
    maxAltitude: 150,
    soundAlerts: true,
    popupsEnabled: true,
  },
};

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      activeTab: 'dashboard',
      sidebarOpen: false,
      modalOpen: false,
      alertAcknowledged: false,
      missionTimeSeconds: 5077,

      uav: {
        altitude: 120.4,
        speed: 8.2,
        heading: 218,
        battery: 78,
        lat: 14.2500,
        lng: 120.7300,
      },
      survivor: {
        lat: 14.2515,
        lng: 120.7310,
      },
      home: {
        lat: 14.2485,
        lng: 120.7290,
      },
      hasRealGps: false,
      setRealGpsLocation: (lat, lng) =>
        set((s) => ({
          hasRealGps: true,
          home: { lat, lng },
          ...(s.hasRealGps
            ? {}
            : {
                uav: { ...s.uav, lat, lng },
                survivor: { lat: lat + 0.0008, lng: lng + 0.0008 },
              }),
          settings: {
            ...s.settings,
            mission: { ...s.settings.mission, homeLat: lat, homeLng: lng },
          },
        })),

      link: {
        wifi: { latency: 48, rssi: -62, bitrate: 5.4 },
        lora: { latency: 83, rssi: -75, plr: 0.8 },
      },

      detections: [
        {
          id: 'ALERT-2026-08-27-102436',
          timestamp: '10:24:36 AM',
          confidence: 92,
          lat: 14.2221,
          lng: 120.9345,
          altitude: 120,
          distance: 120,
          status: 'new',
        },
        {
          id: 'ALERT-2026-08-27-094211',
          timestamp: '09:42:11 AM',
          confidence: 89,
          lat: 14.2208,
          lng: 120.9321,
          altitude: 110,
          distance: 210,
          status: 'acknowledged',
        },
      ],

      mission: {
        id: 'mission-001',
        name: 'Local Area Search',
        startedAt: '07:30 AM',
        status: 'active',
      },

      environment: {
        temperature: 28,
        condition: 'Partly Cloudy',
      },

      videoStatus: 'connecting',
      setVideoStatus: (status) => set({ videoStatus: status }),

      settings: defaultSettings,
      reconnectNonce: 0,

      updateSettings: (section, data) =>
        set((s) => ({
          settings: {
            ...s.settings,
            [section]: { ...s.settings[section], ...data },
          },
        })),

      setFullSettings: (settings) => set({ settings }),

      resetSettings: () => set({ settings: defaultSettings }),

      bumpReconnect: () => set((s) => ({ reconnectNonce: s.reconnectNonce + 1 })),

      endMission: () => {
        const now = new Date();
        const endedAt = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        set((s) => ({
          mission: {
            ...s.mission,
            status: 'ended' as const,
            endedAt,
          },
        }));
      },

      startMission: (name: string) => {
        const now = new Date();
        const startedAt = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        set({
          mission: {
            id: `mission-${Date.now()}`,
            name,
            startedAt,
            status: 'active' as const,
          },
        });
      },

      setActiveTab: (tab) => {
        set({ activeTab: tab, sidebarOpen: false });
        navigateToTab(tab);
      },
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      setModalOpen: (open) => set({ modalOpen: open }),
      acknowledgeAlert: () => {
        set((s) => ({
          alertAcknowledged: true,
          detections: s.detections.map((d) =>
            d.status === 'new' ? { ...d, status: 'acknowledged' as const } : d
          ),
        }));
        setTimeout(() => {
          set({ modalOpen: false });
        }, 500);
      },
      incrementMissionTime: () => set((s) => ({ missionTimeSeconds: s.missionTimeSeconds + 1 })),

      updateUAV: (data) => set((s) => ({ uav: { ...s.uav, ...data } })),
      updateLink: (type, data) =>
        set((s) => ({ link: { ...s.link, [type]: { ...s.link[type], ...data } } })),
      addDetection: (detection) => set((s) => ({ detections: [detection, ...s.detections] })),
      updateEnvironment: (data) => set((s) => ({ environment: { ...s.environment, ...data } })),
    }),
    {
      name: 'aeris-settings',
      partialize: (state) => ({ settings: state.settings }),
    }
  )
);
