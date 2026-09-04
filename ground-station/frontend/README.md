# AERIS Dashboard - Frontend

Vite + React + TypeScript dashboard para sa AERIS.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Frontend Architecture                            │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   Vite Dev      │
                    │   Server        │
                    │   Port: 5173    │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
   ┌────────────┐     ┌────────────┐     ┌────────────┐
   │  React     │     │  Zustand   │     │  Leaflet   │
   │  + TypeScript│   │  State     │     │  Maps      │
   └─────┬──────┘     └─────┬──────┘     └────────────┘
         │                  │                  
         ▼                  ▼                  
   ┌─────────────────────────────────────────┐
   │         Components (Sidebar,            │
   │   Header, MissionMap, Detections...)     │
   └─────────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   WebSocket     │
                    │   Connection    │
                    └─────────────────┘
```

---

## Features

- **Real-time Updates** - WebSocket integration for live data
- **Interactive Maps** - Leaflet with custom markers
- **State Management** - Zustand for global state
- **Type Safety** - TypeScript throughout
- **Responsive UI** - Tailwind CSS + custom styles
- **Fast Development** - Vite HMR (Hot Module Replacement)

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Vite | Build tool & dev server |
| React 19 | UI framework |
| TypeScript | Type safety |
| Zustand | State management |
| Tailwind CSS | Styling |
| Leaflet | Maps |
| Phosphor Icons | Icons |

---

## Installation

### Prerequisites

- Node.js 20+ (LTS recommended)
- npm or yarn

### Install Dependencies

```bash
# Using npm
npm install

# Or using yarn
yarn install
```

---

## Running

### Development Mode

```bash
npm run dev
```

Frontend: http://localhost:5173

### With Backend (Full Stack)

Run backend in one terminal, frontend in another:

```bash
# Terminal 1 - Backend
cd ground-station/backend
python main.py

# Terminal 2 - Frontend
cd ground-station/frontend
npm run dev
```

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

Build output: `dist/`

---

## Project Structure

```
aeris-dashboard/
├── public/                      # Static assets
│   └── image/                   # Images
│       └── AERIS.png            # Logo
├── src/
│   ├── components/              # React components
│   │   ├── Sidebar.tsx          # Navigation sidebar
│   │   ├── Header.tsx           # Top header with telemetry
│   │   ├── MissionMap.tsx       # Leaflet map component
│   │   ├── LiveFeed.tsx         # Video feed component
│   │   ├── CommLinkHealth.tsx  # Wi-Fi/LoRa status
│   │   ├── DetectionsTable.tsx  # Detection list
│   │   ├── ActiveMission.tsx    # Mission info panel
│   │   └── SurvivorModal.tsx    # Detection alert modal
│   ├── pages/                   # Page components
│   │   ├── Dashboard.tsx        # Main dashboard
│   │   ├── LiveFeedPage.tsx     # Full video page
│   │   ├── DetectionsPage.tsx   # All detections
│   │   ├── MapPage.tsx          # Full map page
│   │   └── SettingsPage.tsx     # Settings page
│   ├── stores/                  # Zustand state
│   │   └── appStore.ts          # Global state
│   ├── hooks/                   # Custom React hooks
│   │   ├── useWebSocket.ts      # WebSocket connection
│   │   └── useTelemetrySimulation.ts # Telemetry simulation
│   ├── types/                   # TypeScript types
│   │   └── index.ts             # Type definitions
│   ├── App.tsx                  # Main app component
│   ├── main.tsx                 # Entry point
│   └── index.css                # Global styles
├── package.json                 # Dependencies
├── tailwind.config.js          # Tailwind config
├── postcss.config.js           # PostCSS config
├── vite.config.ts              # Vite config
├── tsconfig.json               # TypeScript config
└── README.md                   # This file
```

---

## Component Connection

### State Management (Zustand)

```typescript
// src/stores/appStore.ts
import { create } from 'zustand';

interface AppState {
  // UI State
  activeTab: string;
  sidebarOpen: boolean;
  modalOpen: boolean;
  alertAcknowledged: boolean;
  
  // Data
  uav: UAVTelemetry;
  link: CommLinks;
  detections: SurvivorDetection[];
  
  // Actions
  setActiveTab: (tab: string) => void;
  updateUAV: (data: Partial<UAVTelemetry>) => void;
  addDetection: (detection: SurvivorDetection) => void;
}

const useAppStore = create<AppState>((set) => ({
  // Initial state
  activeTab: 'dashboard',
  uav: { /* ... */ },
  
  // Actions
  setActiveTab: (tab) => set({ activeTab: tab, sidebarOpen: false }),
  updateUAV: (data) => set((s) => ({ uav: { ...s.uav, ...data } })),
}));
```

### WebSocket Hook

```typescript
// src/hooks/useWebSocket.ts
import { useWebSocket } from './hooks/useWebSocket';

function App() {
  const { send } = useWebSocket('ws://localhost:8000/ws');
  
  // Automatically connects on mount
  // Auto-reconnects on disconnect
  // Updates Zustand store on message
}
```

### Map Component

```typescript
// src/components/MissionMap.tsx
import L from 'leaflet';

useEffect(() => {
  const map = L.map(mapRef.current).setView([lat, lng], 16);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
  
  // Add markers
  L.marker([homeLat, homeLng], { icon: homeIcon }).addTo(map);
  L.marker([survivorLat, survivorLng], { icon: survivorIcon }).addTo(map);
  L.marker([uavLat, uavLng], { icon: uavIcon }).addTo(map);
}, []);
```

---

## Configuration

### WebSocket URL

Edit `src/hooks/useWebSocket.ts`:

```typescript
// Local development
const WS_URL = 'ws://localhost:8000/ws';

// Production (change to your backend IP)
const WS_URL = 'ws://192.168.1.100:8000/ws';
```

### Tailwind Theme

Edit `tailwind.config.js`:

```javascript
export default {
  theme: {
    extend: {
      colors: {
        aeris: {
          light: '#d1fae5',
          DEFAULT: '#059669',
          dark: '#047857',
        },
        danger: {
          light: '#fee2e2',
          DEFAULT: '#dc2626',
          dark: '#b91c1c',
        },
      },
    },
  },
};
```

---

## Connecting to Backend

### WebSocket Connection

```
┌─────────────────┐
│   React App     │
│  (Port 5173)    │
└────────┬────────┘
         │
         │ ws://localhost:8000/ws
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│  (Port 8000)    │
└────────┬────────┘
         │
         │ Internal WebSocket
         │
         ▼
┌─────────────────┐
│  Raspberry Pi   │
│  (YOLOv8)       │
└─────────────────┘
```

### Message Flow

1. **RPi detects person** → sends JSON via WebSocket
2. **FastAPI receives** → broadcasts to all connected clients
3. **React receives** → updates Zustand store
4. **Components re-render** → show new detection in UI

---

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

**Recommended:** Chrome/Edge (Chromium-based) for best performance.

---

## Troubleshooting

### WebSocket Connection Failed

```bash
# Check if backend is running
netstat -ano | findstr :8000

# Check WebSocket URL in useWebSocket.ts
# Should match backend address
```

### Map Not Loading

```bash
# Check Leaflet CSS is imported in index.css
# Should have: @import url('...leaflet.css')
```

### Build Errors

```bash
# Clear cache
rm -rf node_modules dist
npm install
npm run build
```

---

## License

MIT License
