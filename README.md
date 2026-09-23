# AERIS - Off-Grid UAV System for Search and Rescue

A complete drone-based search and rescue system with **decentralized, dual-link communication** and **localized Edge-AI detection** for post-disaster scenarios where conventional infrastructure is compromised.

## Abstract

AERIS addresses the critical need for resilient communication and survivor detection in disaster-affected areas where public infrastructure is destroyed. By deploying an **off-grid dual-link architecture** — combining 5GHz Wi-Fi for high-bandwidth video streaming and 915/923MHz LoRa for reliable telemetry — the system maintains operational continuity during the "Golden Hour" when every second counts. **Edge-AI processing** on a Raspberry Pi 5 with **Hailo-8L NPU** reduces end-to-end latency from typical cloud-AI delays (150-200ms) to under 105ms, enabling rapid situational awareness and GPS coordinate dissemination to rescue personnel.

## Research Objectives

1. Design a **decentralized, air-gapped dual-link communication architecture** for reliable low-latency transmission of telemetry and video data.
2. Measure **end-to-end latency (ms)**, **Packet Loss Ratio (%)**, and **RSSI (dBm)** across varying distances (10–200m) and altitudes (10–50m).
3. Develop a functional hardware prototype using **Raspberry Pi 5**, **UART LoRa transceivers**, and optimized antenna configurations compliant with SWaP constraints.
4. Evaluate **detection accuracy, precision, recall, latency, and false positive rate** for survivor identification.
5. Measure **power consumption and operational endurance** of the integrated system.
6. Test effectiveness under **NLOS, obstructed environments, and environmental stress factors**.

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
│   │   ├── vercel.json
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

Flow: **drone (o sim) → FastAPI backend :8000 → dashboard :5173**.
Walang direct drone↔dashboard connection.

### Prerequisites

| Software | Version | Install |
|----------|---------|---------|
| Python | 3.11+ | `sudo apt install python3 python3-venv python3-pip` |
| Node.js | 20+ | https://nodejs.org/ |
| Git | latest | `sudo apt install git` |
| Raspberry Pi Imager | for flashing Pi OS | Linux: `sudo apt install rpi-imager` → run `rpi-imager` (or https://www.raspberrypi.com/software/) |

### 1. Clone

```bash
git clone https://github.com/amblessly/aeris-project.git
cd aeris-project
```

### 2. Install + run backend (FastAPI, port 8000)

```bash
cd ground-station/backend

# one-time: venv + deps (requests kasama — ginagamit ng sim + gcs_link)
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# run (use --host 0.0.0.0 para ma-reach ng real Pi sa network)
./venv/bin/python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# verify
curl http://localhost:8000/api/mission          # → 200
curl http://localhost:8000/video/status         # → {"online":false/true,...}
```

### 3. Install + run frontend (dashboard, port 5173)

```bash
cd ground-station/frontend
npm install
npm run dev

# open http://localhost:5173  (routes: / /livefeed /detections /map /settings)
```

Pag hindi pa nagco-connect ang drone, auto-fall back ang dashboard sa
simulation mode. Green bar sa LiveFeed pag may luma online na drone.

### 4. Connect a drone

#### A. Local fake drone (walang hardware, same laptop)

```bash
# terminal 3 — kailangan buhay ang backend
cd ground-station/backend
./venv/bin/python3 simulate_drone.py
```

Ito ang gumagawa ng: MJPEG `:5000/video_feed`, POST `/api/telemetry`
bawat 1s, POST `/api/detection` bawat 8s. Smoke test:

```bash
curl http://localhost:8000/video/status     # {"online":true,...}
curl http://localhost:8000/api/drone/status # {"connected":true,...}
curl http://localhost:8000/api/telemetry    # "source":"drone"
```

#### B. Real Raspberry Pi 5 (onboard code)

**1 — Flash OS sa SD card** (gamit ang Raspberry Pi Imager):

```bash
rpi-imager        # o pindutin sa app menu
```

Sa Imager GUI:
1. **OS** → Raspberry Pi OS (64-bit) — Lite ok lang (headless)
2. **Storage** → ang microSD card
3. **Gear/settings icon** (Next page):
   - hostname: `aeris-pi5`
   - Enable SSH (password auth ok)
   - Configure Wi-Fi → **same SSID/2.4-or-5GHz network ng laptop**
   - username/password (hal. `pi` / password mo)
4. **WRITE** → tapos na, isaksak sa Pi 5 at power on.

**2 — Setup sa Pi** (mula sa laptop):

```bash
ssh pi@aeris-pi5.local
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip screen git

git clone https://github.com/amblessly/aeris-project.git
cd aeris-project/drone-onboard/raspberry-pi-5
python3 -m venv venv
./venv/bin/pip install -r requirements.txt   # opencv, ultralytics, torch, flask, requests

# test camera (q para mag-close)
python3 test_cam.py
```

> Note: unang run ng detection magda-download pa ang ultralytics ng
> `yolov8n.pt` (~6MB) — kailangan internet sa Pi noong unang beses.

**3 — I-connect sa backend** (nasa same Wi-Fi dapat ang Pi at laptop):

```bash
# sa Pi — hanapin ang laptop IP:  ip addr  (laptop) o  hostname -I  (din)
GCS_API_URL=http://<laptop-ip>:8000 ./venv/bin/python3 main.py
# o persistent:  export GCS_API_URL=http://<laptop-ip>:8000  sa ~/.bashrc

# background sa Pi:
screen -S aeris
GCS_API_URL=http://<laptop-ip>:8000 ./venv/bin/python3 main.py
# Ctrl+A, detach — bumalik: screen -r aeris
```

Ang `main.py` ay: (a) nagbo-boot ng Flask dashboard sa `:5000` na may
`/video_feed` MJPEG, (b) nagde-detect ng tao via YOLOv8, (c) nagpo-post
ng telemetry bawat ~1s at detection kapag may tao papuntang backend.

**4 — Sabihan ang backend kung nasaan ang drone video** (sa laptop,
bago o habang tumatakbo ang backend):

```bash
DRONE_VIDEO_URL=http://<pi-ip>:5000/video_feed \
  ./venv/bin/python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**5 — Verify:**

```bash
curl http://localhost:8000/api/drone/status   # connected:true
curl http://localhost:8000/video/status       # online:true
# dashboard → /livefeed dapat green ang bar
```

### 5. Environment variables

| Env var | Default | Direction | Purpose |
|---------|---------|-----------|---------|
| `GCS_API_URL` | `http://localhost:8000` | drone → backend | saan mag-post ng telemetry/detection |
| `DRONE_VIDEO_URL` | `http://127.0.0.1:5000/video_feed` | backend → drone | MJPEG feed na i-proxy sa dashboard |
| `VIDEO_PORT` | `5000` | sim | port ng fake MJPEG |
| `TELEMETRY_EVERY_S` / `DETECT_EVERY_S` | `1.0` / `8` | sim | rates ng fake drone |

### 6. Run order (tuwing mag-start from scratch)

```bash
# T1 — backend
cd ground-station/backend && ./venv/bin/python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
# T2 — frontend
cd ground-station/frontend && npm run dev
# T3 — drone: sim O real Pi (see step 4)
cd ground-station/backend && ./venv/bin/python3 simulate_drone.py
```

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

### Link Configuration

- **Frontend → backend:** laging `ws://localhost:8000/ws` — pareho
  itong tumatakbo sa laptop, walang binabago sa `App.tsx`.
- **Backend:** patakbuing `--host 0.0.0.0 --port 8000` para ma-reach
  ng Pi sa network (HTTP, hindi WebSocket).
- **Pi → backend:** `GCS_API_URL=http://<laptop-ip>:8000` (tingnan
  Quick Start step 4B). Hanapin ang laptop IP sa `ip addr` (Linux) o
  `ipconfig` (Windows).

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
# Check kung busy ang port 8000
ss -ltnp | grep :8000

# Kill kung kailangan
pkill -f "uvicorn main:app"
```

### RPi can't connect to GCS
```bash
# Sa Pi — test kung naaabot ang laptop backend (HTTP, hindi WS)
ping <laptop-ip>
curl http://<laptop-ip>:8000/api/mission     # dapat 200

# Sa backend logs (laptop)
grep "POST /api" /tmp/opencode/backend.log | tail
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
