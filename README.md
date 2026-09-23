# AERIS

Drone (o sim) → FastAPI backend `:8000` → React dashboard `:5173`.
Off-grid search & rescue ground station — walang direct drone↔dashboard.

---

## Install

### Prerequisites

| Software | Version | Install |
|----------|---------|---------|
| Python | 3.11+ | `sudo apt install python3 python3-venv python3-pip` |
| Node.js | 20+ | https://nodejs.org/ |
| Git | latest | `sudo apt install git` |
| Raspberry Pi Imager | optional (Pi OS flash) | `sudo apt install rpi-imager` → run `rpi-imager` |

### 1. Clone

```bash
git clone https://github.com/aeris-team/aeris-project.git
cd aeris-project
```

### 2. Backend (FastAPI, port 8000)

```bash
cd ground-station/backend

# one-time: venv + deps (requests kasama — gamit ng sim + gcs_link)
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# verify install
./venv/bin/python3 -c "import fastapi, requests; print('deps OK')"
```

### 3. Frontend (dashboard, port 5173)

```bash
cd ground-station/frontend
npm install

# verify install
npm run build
```

### 4. (Optional) Raspberry Pi 5 onboard — OS + deps

**Flash OS sa SD card** gamit ang Raspberry Pi Imager (`rpi-imager`):

1. **OS** → Raspberry Pi OS (64-bit) — Lite ok (headless)
2. **Storage** → ang microSD card
3. **Gear/settings icon:**
   - hostname: `aeris-pi5`
   - Enable SSH (password auth ok)
   - Wi-Fi → **same network ng laptop**
   - username/password (hal. `pi` / password mo)
4. **WRITE** → isaksak sa Pi 5 at power on.

**Install software sa Pi** (mula sa laptop):

```bash
ssh pi@aeris-pi5.local
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip screen git

git clone https://github.com/aeris-team/aeris-project.git
cd aeris-project/drone-onboard/raspberry-pi-5
python3 -m venv venv
./venv/bin/pip install -r requirements.txt   # opencv, ultralytics, torch, flask, requests

# test camera (q para mag-close)
python3 test_cam.py
```

> Unang run magda-download pa ang ultralytics ng `yolov8n.pt` (~6MB) —
> kailangan internet sa Pi noong unang beses.

---

## How to Use

### Run (3 terminals)

```bash
# T1 — backend (--host 0.0.0.0 para ma-reach ng real Pi)
cd ground-station/backend
./venv/bin/python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# T2 — frontend
cd ground-station/frontend
npm run dev

# T3 — drone: sim (see A) o real Pi (see B)
cd ground-station/backend
./venv/bin/python3 simulate_drone.py
```

Buksan: **http://localhost:5173** — routes: `/` `/livefeed` `/detections`
`/map` `/settings`. Green bar sa LiveFeed pag may online na drone.
Pag wala pang drone, auto-fall back ang dashboard sa simulation mode.

### A. Local fake drone (walang hardware)

```bash
cd ground-station/backend
./venv/bin/python3 simulate_drone.py
```

Ginagawa nito: MJPEG `:5000/video_feed`, POST `/api/telemetry` bawat 1s,
POST `/api/detection` bawat 8s.

**Verify:**

```bash
curl http://localhost:8000/video/status     # {"online":true,...}
curl http://localhost:8000/api/drone/status # {"connected":true,...}
curl http://localhost:8000/api/telemetry    # "source":"drone"
curl http://localhost:8000/api/detections   # may laman
```

### B. Real Raspberry Pi 5

Kailangan **same Wi-Fi** ang Pi at laptop.

**1 — Sa Pi:** i-connect ang onboard pipeline sa backend:

```bash
# laptop IP: ip addr (Linux) o ipconfig (Windows)
GCS_API_URL=http://<laptop-ip>:8000 ./venv/bin/python3 main.py

# background:
screen -S aeris
GCS_API_URL=http://<laptop-ip>:8000 ./venv/bin/python3 main.py
# Ctrl+A, detach — bumalik: screen -r aeris
```

Ang `main.py` ay: (a) Flask dashboard sa `:5000` na may `/video_feed`
MJPEG, (b) YOLOv8 person detection, (c) POST ng telemetry bawat ~1s at
detection kapag may tao — papuntang backend.

**2 — Sa laptop:** sabihan ang backend kung nasaan ang video:

```bash
DRONE_VIDEO_URL=http://<pi-ip>:5000/video_feed \
  ./venv/bin/python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**3 — Verify:**

```bash
curl http://localhost:8000/api/drone/status   # connected:true
curl http://localhost:8000/video/status       # online:true
# dashboard → /livefeed dapat green ang bar
```

### Environment variables

| Env var | Default | Direction | Purpose |
|---------|---------|-----------|---------|
| `GCS_API_URL` | `http://localhost:8000` | drone → backend | saan mag-post ng telemetry/detection |
| `DRONE_VIDEO_URL` | `http://127.0.0.1:5000/video_feed` | backend → drone | MJPEG feed na i-proxy sa dashboard |
| `VIDEO_PORT` | `5000` | sim | port ng fake MJPEG |
| `TELEMETRY_EVERY_S` / `DETECT_EVERY_S` | `1.0` / `8` | sim | rates ng fake drone |

### Network

```
Ground Station (Laptop)          Raspberry Pi 5 (Drone)
IP: 192.168.1.50                 IP: 192.168.1.100
       │                                 │
       │  ┌──────────────────────────┐  │
       └──┤  Same Wi-Fi Network      ├──┘
          └──────────────────────────┘
```

- **Frontend → backend:** laging `ws://localhost:8000/ws` — parehong
  nasa laptop, walang binabago sa `App.tsx`.
- **Backend:** `--host 0.0.0.0` para ma-reach ng Pi (HTTP, hindi WS).
- **Pi → backend:** `GCS_API_URL=http://<laptop-ip>:8000`.

---

## Project Structure

```
aeris-project/
│
├── ground-station/              # Operator's Command Center (laptop/PC)
│   ├── frontend/                # React + TypeScript Dashboard (:5173)
│   │   ├── src/
│   │   │   ├── components/     # LiveVideoPane, MissionMap, etc.
│   │   │   ├── pages/          # Dashboard, Map, Detections, Settings
│   │   │   ├── stores/         # Zustand state
│   │   │   ├── hooks/          # useWebSocket, useVideoStream, useGeolocation
│   │   │   ├── lib/            # navigation helper
│   │   │   ├── types/
│   │   │   ├── App.tsx
│   │   │   └── main.tsx
│   │   └── package.json
│   │
│   └── backend/                 # FastAPI (:8000)
│       ├── main.py              # API + WS + video proxy
│       ├── simulate_drone.py    # local fake drone
│       ├── requirements.txt
│       └── README.md
│
├── drone-onboard/               # Code sa Raspberry Pi (naka-mount sa drone)
│   ├── gcs_link.py              # drone → backend HTTP client
│   ├── raspberry-pi-4b/         # RPi 4B version
│   └── raspberry-pi-5/          # RPi 5 version (Hailo-8L)
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

### Key Design Principles

1. **Logical Network Segregation** — High-bandwidth 5GHz video decoupled from low-bandwidth 915/923MHz LoRa telemetry.
2. **Edge-AI Processing** — YOLOv8 on-device (RPi 5 + Hailo-8L), <105ms vs 150-200ms cloud.
3. **Multi-Hop Resilient Routing** — 10 m/s flight speed, 8 km range, no single point of failure.
4. **H.264 Hardware Encoding** — 200 Mbps raw → 5-6 Mbps over UDP.
5. **Age of Information (AoI) Optimization** — Critical navigation data decoupled from surveillance streams.

---

## Features

### Dashboard
- ✅ **Real-time video feed** from drone camera (MJPEG proxy)
- ✅ **Interactive map** — UAV/survivor positions (Streets/Satellite, offline badge)
- ✅ **Live person detection** via YOLOv8 (WebSocket push + sound alert)
- ✅ **Detection alerts** — confidence, GPS (N/S/E/W), thermal, cooldown/min-confidence settings
- ✅ **UAV telemetry** (altitude, speed, battery, heading, GPS)
- ✅ **Comm link health** (5GHz Wi-Fi + 915MHz LoRa)
- ✅ **Mission management** (start/end, timer, auto GPS lock via browser)
- ✅ **Settings** — save/discard, diagnostics, CSV export, factory reset
- ✅ **Routing** — shareable URLs (`/livefeed`, `/map`, ...)

### Real-Time Data Flow
1. RPi 5 captures frames from USB camera
2. YOLOv8 detects humans on-device
3. `gcs_link.py` POSTs telemetry/detection → backend `:8000`
4. Backend broadcasts via WebSocket + stores detections
5. Frontend updates Zustand store → dashboard re-renders

---

## Tech Stack

### Frontend
- Vite, React 19, TypeScript, Zustand (localStorage persist), Tailwind CSS, Leaflet, Phosphor Icons, react-router-dom

### Backend
- FastAPI, Uvicorn, WebSocket, HTTP proxy (MJPEG)

### Onboard (Drone)
- Python 3.11+, Raspberry Pi 5 (Hailo-8L), YOLOv8/Ultralytics, OpenCV, PyTorch, Flask (video), requests (GCS link)

---

## Component Documentation

| Component | README |
|-----------|--------|
| Frontend (Dashboard) | [`ground-station/frontend/README.md`](./ground-station/frontend/README.md) |
| Backend (FastAPI) | [`ground-station/backend/README.md`](./ground-station/backend/README.md) |
| RPi 4B (Detection) | [`drone-onboard/raspberry-pi-4b/README.md`](./drone-onboard/raspberry-pi-4b/README.md) |
| RPi 5 (Detection + Hailo) | [`drone-onboard/raspberry-pi-5/README.md`](./drone-onboard/raspberry-pi-5/README.md) |

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
ss -ltnp | grep :8000          # kung busy ang port
pkill -f "uvicorn main:app"    # kill kung kailangan
```

### Drone not connecting
```bash
# sa laptop — backend buhay?
curl http://localhost:8000/api/mission          # dapat 200
curl http://localhost:8000/api/drone/status     # connected:true?

# sa Pi — naaabot ang laptop? (same Wi-Fi dapat)
ping <laptop-ip>
curl http://<laptop-ip>:8000/api/mission
```

### Camera not detected on RPi
```bash
lsusb
ls /dev/video*
python test_cam.py
```

### Hailo-8L not detected
```bash
hailortcli scan
sudo dmesg | grep hailo
```

---

## Performance Targets

| Parameter | Target |
|-----------|--------|
| Video latency (5GHz) | < 105 ms |
| Packet Loss Ratio (LoRa) | < 3% |
| RSSI (video) | ≥ -85 dBm |
| RSSI (telemetry) | ≥ -80 dBm |
| Operational range | 10-200 m |
| Altitude envelope | 10-50 m |
| Edge-AI latency | < 105 ms |

---

## License

MIT License — Educational prototype project.

---

## Repository

🔗 https://github.com/aeris-team/aeris-project

For issues, check individual component READMEs for detailed troubleshooting.
