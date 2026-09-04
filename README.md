# AERIS - Off-Grid UAV System for Search and Rescue

A complete drone-based search and rescue system with **decentralized, dual-link communication** and **localized Edge-AI detection** for post-disaster scenarios where conventional infrastructure is compromised.

---

## Abstract

AERIS addresses the critical need for resilient communication and survivor detection in disaster-affected areas where public infrastructure is destroyed. By deploying an **off-grid dual-link architecture** — combining 5GHz Wi-Fi for high-bandwidth video streaming and 915/923MHz LoRa for reliable telemetry — the system maintains operational continuity during the "Golden Hour" when every second counts. **Edge-AI processing** on a Raspberry Pi 5 with **Hailo-8L NPU** reduces end-to-end latency from typical cloud-AI delays (150-200ms) to under 105ms, enabling rapid situational awareness and GPS coordinate dissemination to rescue personnel.

---

## Research Objectives

1. Design a **decentralized, air-gapped dual-link communication architecture** for reliable low-latency transmission of telemetry and video data.
2. Measure **end-to-end latency (ms)**, **Packet Loss Ratio (%)**, and **RSSI (dBm)** across varying distances (10–200m) and altitudes (10–50m).
3. Develop a functional hardware prototype using **Raspberry Pi 5**, **UART LoRa transceivers**, and optimized antenna configurations compliant with SWaP constraints.
4. Evaluate **detection accuracy, precision, recall, latency, and false positive rate** for survivor identification.
5. Measure **power consumption and operational endurance** of the integrated system.
6. Test effectiveness under **NLOS, obstructed environments, and environmental stress factors**.

---

## Project Structure

```
aeris-project/
│
├── ground-station/              # Operator's Command Center (runs on laptop/PC)
│   ├── frontend/                # React + TypeScript Dashboard
│   │   ├── src/
│   │   │   ├── components/     # UI components (LiveFeed, MissionMap, etc.)
│   │   │   ├── pages/          # Page components (Dashboard, Map, Detections, Settings)
│   │   │   ├── stores/         # Zustand state management
│   │   │   ├── hooks/          # useWebSocket, useTelemetrySimulation
│   │   │   ├── types/          # TypeScript types
│   │   │   ├── App.tsx
│   │   │   ├── main.tsx
│   │   │   └── index.css
│   │   ├── public/             # Static assets (AERIS logo)
│   │   ├── package.json
│   │   ├── tailwind.config.js
│   │   ├── vite.config.ts
│   │   └── README.md
│   │
│   └── backend/                 # FastAPI Backend (WebSocket server, port 8000)
│       ├── main.py
│       ├── requirements.txt
│       └── README.md
│
├── drone-onboard/               # Code that runs on Raspberry Pi (mounted on drone)
│   ├── raspberry-pi-4b/         # RPi 4B version (edge-AI)
│   └── raspberry-pi-5/          # RPi 5 version (with Hailo-8L NPU)
│
└── README.md                    # This file
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AERIS OFF-GRID DUAL-LINK SYSTEM                      │
└─────────────────────────────────────────────────────────────────────────────┘

   ┌─────────────┐      USB Camera         ┌──────────────────────────┐
   │   DRONE     │ ──────────────────────▶ │  RASPBERRY PI 5          │
   │  (UAV)      │    RGB + Thermal        │  + Hailo-8L NPU          │
   │             │                         │  (Edge-AI Processing)    │
   └─────────────┘                         └────────┬─────────────────┘
                                                      │
                                                      ▼
                                            ┌─────────────────┐
                                            │  YOLOv8n        │
                                            │  Person         │
                                            │  Detection       │
                                            └────────┬────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │  JSON Packet    │
                                            │  (Detection +   │
                                            │   Vital Signs)  │
                                            └────────┬────────┘
                                                     │
      ┌──────────────────────────────────────────────┼──────────────────────────────────────────────┐
      │                                              │                                              │
      ▼                                              ▼                                              ▼
┌─────────────────┐                        ┌─────────────────┐                          ┌─────────────────┐
│  5GHz Wi-Fi      │                        │  915/923MHz     │                          │   MAVLink       │
│  (Video Stream)  │                        │  LoRa           │                          │   Telemetry     │
│  ~5-6 Mbps       │                        │  (Backup Link)  │                          │                 │
│  <105ms latency  │                        │  <3% PLR        │                          │                 │
│  RSSI ≥ -85 dBm  │                        │  RSSI ≥ -80 dBm │                          │                 │
└────────┬─────────┘                        └────────┬────────┘                          └────────┬────────┘
         │                                            │                                             │
         └──────────────────────────┬────────────────┘                                             │
                                    │                                                            │
                                    ▼                                                            ▼
                          ┌─────────────────────────┐                              ┌──────────────────────┐
                          │  FASTAPI BACKEND        │                              │  Ground Control      │
                          │  WebSocket Server       │ ◀────────────────────────── │  Station (GCS)       │
                          │  Port: 8000             │                              │  Open-source GCS     │
                          └────────────┬────────────┘                              │  + SITL Simulation   │
                                       │                                            └──────────┬───────────┘
                                       ▼                                                       │
                          ┌─────────────────────────┐                                          │
                          │  REACT FRONTEND         │ ◀────────────────────────────────────────┘
                          │  (Vite + TypeScript)    │
                          │  Port: 5173             │
                          │                         │
                          │  - Live Feed Display    │
                          │  - Mission Map         │
                          │  - Detections Table    │
                          │  - UAV Telemetry       │
                          │  - Comm Link Health    │
                          │  - Settings/Config     │
                          └─────────────────────────┘
                                       │
                                       ▼
                          ┌─────────────────────────┐
                          │  OPERATOR (MDRRMO)      │
                          │  Browser-based Console  │
                          └─────────────────────────┘
```

### Key Design Principles (from paper)

1. **Logical Network Segregation** — High-bandwidth 5GHz video is decoupled from low-bandwidth 915/923MHz LoRa telemetry to mitigate frequency interference.
2. **Edge-AI Processing** — YOLOv8 inference runs on-device (RPi 5 + Hailo-8L) to achieve <105ms latency versus 150-200ms cloud-based.
3. **Multi-Hop Resilient Routing** — Operates at 10 m/s flight speed over 8 km range with no single point of failure.
4. **H.264 Hardware Encoding** — 200 Mbps raw stream compressed to 5-6 Mbps over UDP.
5. **Age of Information (AoI) Optimization** — Decoupled critical navigation data from surveillance streams.

---

## Performance Targets

| Parameter | Target | Source |
|-----------|--------|--------|
| Video latency (5GHz) | < 105 ms | Mahdi et al., 2025 |
| Packet Loss Ratio (LoRa) | < 3% | Arslanbenzer et al., 2023; Bordin et al., 2024 |
| RSSI (video) | ≥ -85 dBm | Zhu et al., 2021 |
| RSSI (telemetry) | ≥ -80 dBm | Zhao et al., 2024 |
| Operational range | 10-200 m | Research specification |
| Altitude envelope | 10-50 m | Research specification |
| Edge-AI latency | < 105 ms | Mahdi et al., 2025; Ntousis et al., 2025 |

---

## Tech Stack

### Frontend (Ground Control Station)
- **Vite** — Build tool
- **React 19** — UI framework
- **TypeScript** — Type safety
- **Zustand** — State management (with localStorage persistence)
- **Tailwind CSS** — Styling
- **Leaflet** — Interactive maps (OpenStreetMap + Esri Satellite)
- **Phosphor Icons** — UI icons
- **FastAPI WebSocket** — Real-time data from backend

### Backend (Ground Station)
- **FastAPI** — Web framework
- **WebSocket** — Real-time telemetry/detection broadcast
- **Uvicorn** — ASGI server

### Onboard (Drone)
- **Python 3.11+** — Main language
- **Raspberry Pi 5** — Companion computer
- **Hailo-8L NPU** — Edge-AI accelerator
- **YOLOv8** — Person detection
- **OpenCV** — Image processing
- **PyTorch** — Deep learning
- **5GHz Wi-Fi** — Video streaming (UDP)
- **915/923MHz LoRa** — Telemetry link
- **MAVLink** — Flight controller telemetry

---

## Quick Start

### Prerequisites

| Software | Version | Download |
|----------|---------|----------|
| Node.js | 20+ | https://nodejs.org/ |
| Python | 3.11+ | https://python.org/ |
| Git | Latest | https://git-scm.com/ |
| Chrome/Chromium | Latest | https://www.google.com/chrome/ |

### 1. Clone the Repository

```bash
git clone https://github.com/amblessly/aeris-project.git
cd aeris-project
```

### 2. Setup Ground Control Station (Laptop/PC)

#### Install Frontend Dependencies

```bash
cd ground-station/frontend
npm install
```

#### Run the Dashboard

```bash
# Terminal 1 — Start backend (WebSocket server, port 8000)
cd ground-station/backend
pip install -r requirements.txt
python main.py

# Terminal 2 — Start frontend (React dashboard, port 5173)
cd ground-station/frontend
npm run dev

# Access dashboard
# Open: http://localhost:5173
```

The frontend will automatically connect to `ws://localhost:8000/ws`. If the backend is not running, the dashboard will fall back to simulation mode for testing.

### 3. Setup Raspberry Pi 5 (Drone Onboard)

#### Flash Raspberry Pi OS

1. Download Raspberry Pi Imager: https://www.raspberrypi.com/software/
2. Flash **Raspberry Pi OS (64-bit)** to SD card
3. Configure Wi-Fi and SSH during flashing

#### Install Detection Software

```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Update system
sudo apt update && sudo apt upgrade -y

# Install screen (for background processes)
sudo apt install -y screen

# Clone project
git clone https://github.com/amblessly/aeris-project.git
cd aeris-project/drone-onboard/raspberry-pi-5

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (includes YOLOv8, OpenCV, MAVLink, etc.)
pip install -r requirements.txt
```

#### Run Detection Pipeline

```bash
# Start in background using screen
screen -S aeris
source venv/bin/activate
python main.py

# Detach: Press Ctrl+A, then D
# Reconnect later: screen -r aeris
```

The onboard pipeline runs:
- USB Camera capture (RGB + Thermal if attached)
- YOLOv8 person detection
- Vital signs estimation
- JSON packet creation
- 5GHz Wi-Fi video transmission
- 915MHz LoRa telemetry link

---

## Network Configuration

### Default Setup

```
Ground Station (Laptop)          Raspberry Pi 5 (Drone)
IP: 192.168.1.50                 IP: 192.168.1.100
       │                                 │
       │  ┌──────────────────────────┐  │
       └──┤  Same Wi-Fi Network      ├──┘
          └──────────────────────────┘
```

### WebSocket Configuration

**For local development** (default):
- Frontend → `ws://localhost:8000/ws`
- Backend → listens on `0.0.0.0:8000`

**For network deployment:**

Edit `ground-station/frontend/src/hooks/useWebSocket.ts`:

```typescript
// Change to your GCS IP address
useWebSocket('ws://192.168.1.50:8000/ws');
```

Or in `App.tsx`:

```typescript
useWebSocket('ws://YOUR_GCS_IP:8000/ws');
```

### Test Distances & Altitudes

Per paper: test at distances of **10, 50, 100, 150, 200 meters** and altitudes of **10, 30, 50 meters**.

---

## Features

### Dashboard
- ✅ **Real-time video feed** from drone camera
- ✅ **Interactive map** with UAV and survivor positions (Streets/Satellite views)
- ✅ **Live person detection** using YOLOv8
- ✅ **Detection alerts** with confidence scores, GPS, and thermal data
- ✅ **UAV telemetry** (altitude, speed, battery, heading, GPS)
- ✅ **Communication link health** (5GHz Wi-Fi + 915MHz LoRa)
- ✅ **Mission management** (start/end tracking, mission time)
- ✅ **Environment monitoring** (temperature, weather)
- ✅ **Notification system** with real-time alerts
- ✅ **Settings page** (comm, mission, alerts, system)

### Detection Modal
- RGB + Thermal image visualization
- GPS coordinates with ±3m accuracy
- Altitude, distance, and timestamp
- Heat range analysis
- AI confidence score
- One-click acknowledgment

### Real-Time Data Flow
1. RPi 5 captures frames from USB camera
2. YOLOv8 detects humans (Edge-AI, <105ms)
3. Detection packets sent via dual-link (5GHz video + 915MHz LoRa telemetry)
4. Backend broadcasts via WebSocket
5. Frontend updates Zustand store
6. Dashboard re-renders with new data

---

## Component Documentation

| Component | README |
|-----------|--------|
| Frontend (Dashboard) | [`ground-station/frontend/README.md`](./ground-station/frontend/README.md) |
| Backend (WebSocket) | [`ground-station/backend/README.md`](./ground-station/backend/README.md) |
| RPi 4B (Detection) | [`drone-onboard/raspberry-pi-4b/README.md`](./drone-onboard/raspberry-pi-4b/README.md) |
| RPi 5 (Detection + Hailo) | [`drone-onboard/raspberry-pi-5/README.md`](./drone-onboard/raspberry-pi-5/README.md) |

---

## Folder Organization

| Folder | Purpose | Runs On |
|--------|---------|---------|
| `ground-station/frontend/` | Web dashboard (React UI) | Laptop/PC |
| `ground-station/backend/` | API server (FastAPI WebSocket) | Laptop/PC |
| `drone-onboard/raspberry-pi-4b/` | Detection code (CPU only) | RPi 4B |
| `drone-onboard/raspberry-pi-5/` | Detection code (with Hailo-8L NPU) | RPi 5 |

**Why this structure?**
- **Separation of concerns** — Frontend, backend, and onboard code are independent
- **SWaP optimization** — Each layer optimized for its deployment target
- **Independent deployment** — Each folder can be deployed/tested separately
- **Clear purpose** — `ground-station` = operator side, `drone-onboard` = drone side

---

## Testing Methodology

Per research paper, the system is evaluated at:
- **Distances**: 10, 50, 100, 150, 200 meters (Line-of-Sight)
- **Altitudes**: 10, 30, 50 meters
- **Conditions**: NLOS, obstructed (debris, vegetation), environmental stress

Measured parameters:
- End-to-end transmission latency (ms)
- Received Signal Strength Indicator (RSSI in dBm)
- Packet Loss Ratio (%)
- Detection accuracy, precision, recall
- False positive rate
- Power consumption and operational endurance

---

## Troubleshooting

### Frontend won't start
```bash
cd ground-station/frontend
rm -rf node_modules package-lock.json
npm install
```

### Backend connection refused
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <PID> /F
```

### RPi can't connect to GCS
```bash
# Test network connection
ping 192.168.1.50

# Check WebSocket
python -c "import websocket; ws = websocket.create_connection('ws://192.168.1.50:8000/ws'); print('OK')"
```

### Camera not detected on RPi
```bash
lsusb
ls /dev/video*
python test_cam.py
```

### Hailo-8L not detected
```bash
# Check NPU
hailortcli scan

# Verify driver
sudo dmesg | grep hailo
```

---

## References (per research paper)

- Saraereh et al. (2020) — UAV-enabled LoRa networks for disaster management
- Abro et al. (2025) — Pixhawk + Raspberry Pi companion computer architecture
- Aizat et al. (2023) — Directional antenna tracker (Haversine-based)
- Mahdi et al. (2025) — Video latency benchmarks (105ms)
- Bordin et al. (2024) — Ground reflection effects (up to 830ms delay)
- Arslanbenzer et al. (2023) — LoRa PLR benchmarks (3%)
- Zhu et al. (2021), Zhao et al. (2024) — RSSI standards
- Lyu et al. (2023) — UAV SAR operational challenges

---

## License

MIT License — Educational prototype project.

---

## Repository

🔗 https://github.com/amblessly/aeris-project

For issues, check individual component READMEs for detailed troubleshooting.
