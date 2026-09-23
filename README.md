# AERIS

Drone (or fake sim) goes to FastAPI backend on port 8000, then to the
React dashboard on port 5173. The drone never talks to the dashboard
directly.

---

## Install

### Prerequisites

| Software | Version | How to install |
|----------|---------|----------------|
| Python | 3.11+ | `sudo apt install python3 python3-venv python3-pip` |
| Node.js | 20+ | https://nodejs.org/ |
| Git | latest | `sudo apt install git` |
| Raspberry Pi Imager | optional, for Pi OS | `sudo apt install rpi-imager`, then run `rpi-imager` |

### 1. Clone the repo

```bash
git clone https://github.com/aeris-team/aeris-project.git
cd aeris-project
```

### 2. Backend (FastAPI, port 8000)

```bash
cd ground-station/backend

# one-time setup: make venv and install packages
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# check if install worked
./venv/bin/python3 -c "import fastapi, requests; print('deps OK')"
```

### 3. Frontend (dashboard, port 5173)

```bash
cd ground-station/frontend
npm install

# check if install worked
npm run build
```

### 4. Optional: Raspberry Pi 5 OS and packages

**Flash the OS to the SD card** with Raspberry Pi Imager (`rpi-imager`):

1. **OS** -> Raspberry Pi OS (64-bit). Lite is fine (headless).
2. **Storage** -> your microSD card.
3. **Gear icon (settings):**
   - hostname: `aeris-pi5`
   - turn on SSH (password login is fine)
   - Wi-Fi -> use the **same network as your laptop**
   - username and password (for example: `pi` / your password)
4. **WRITE**, then put the card in the Pi 5 and power it on.

**Install the software on the Pi** (run from your laptop):

```bash
ssh pi@aeris-pi5.local
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip screen git

git clone https://github.com/aeris-team/aeris-project.git
cd aeris-project/drone-onboard/raspberry-pi-5
python3 -m venv venv
./venv/bin/pip install -r requirements.txt   # opencv, ultralytics, torch, flask, requests

# test the camera (press q to close)
python3 test_cam.py
```

Note: the first run will download `yolov8n.pt` (about 6MB). The Pi
needs internet for that first run.

---

## How to Use

### Start everything (3 terminals)

```bash
# T1 - backend (use 0.0.0.0 so a real Pi can reach it)
cd ground-station/backend
./venv/bin/python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# T2 - frontend
cd ground-station/frontend
npm run dev

# T3 - drone: use the sim (see A) or a real Pi (see B)
cd ground-station/backend
./venv/bin/python3 simulate_drone.py
```

Open **http://localhost:5173**. Pages: `/` `/livefeed` `/detections`
`/map` `/settings`. The LiveFeed bar turns green when a drone is
online. With no drone, the dashboard falls back to simulation mode.

### A. Local fake drone (no hardware)

```bash
cd ground-station/backend
./venv/bin/python3 simulate_drone.py
```

This does three things:
- serves MJPEG video on `:5000/video_feed`
- POSTs telemetry to `/api/telemetry` every 1s
- POSTs detections to `/api/detection` every 8s

**Check that it works:**

```bash
curl http://localhost:8000/video/status     # {"online":true,...}
curl http://localhost:8000/api/drone/status # {"connected":true,...}
curl http://localhost:8000/api/telemetry    # "source":"drone"
curl http://localhost:8000/api/detections   # list is not empty
```

### B. Real Raspberry Pi 5

The Pi and the laptop must be on the **same Wi-Fi network**.

**1 - On the Pi:** connect the onboard code to the backend:

```bash
# find the laptop IP: run "ip addr" (Linux) or "ipconfig" (Windows)
GCS_API_URL=http://<laptop-ip>:8000 ./venv/bin/python3 main.py

# to run it in the background:
screen -S aeris
GCS_API_URL=http://<laptop-ip>:8000 ./venv/bin/python3 main.py
# press Ctrl+A then D to leave. Come back with: screen -r aeris
```

What `main.py` does:
- starts a Flask dashboard on `:5000` with the `/video_feed` MJPEG stream
- runs YOLOv8 person detection on the camera
- POSTs telemetry every ~1s and a detection when it sees a person

**2 - On the laptop:** tell the backend where the video is:

```bash
DRONE_VIDEO_URL=http://<pi-ip>:5000/video_feed \
  ./venv/bin/python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**3 - Check that it works:**

```bash
curl http://localhost:8000/api/drone/status   # connected:true
curl http://localhost:8000/video/status       # online:true
# open the dashboard /livefeed page: the bar should be green
```

### Environment variables

| Variable | Default | Direction | What it does |
|----------|---------|-----------|--------------|
| `GCS_API_URL` | `http://localhost:8000` | drone -> backend | where the drone sends telemetry and detections |
| `DRONE_VIDEO_URL` | `http://127.0.0.1:5000/video_feed` | backend -> drone | video URL that the backend proxies |
| `VIDEO_PORT` | `5000` | sim | port of the fake video server |
| `TELEMETRY_EVERY_S` / `DETECT_EVERY_S` | `1.0` / `8` | sim | how often the fake drone sends data |

### Network

```
Ground Station (Laptop)          Raspberry Pi 5 (Drone)
IP: 192.168.1.50                 IP: 192.168.1.100
       |                                 |
       |  +--------------------------+  |
       +--+  Same Wi-Fi Network      --+
          +--------------------------+
```

- **Frontend -> backend:** always `ws://localhost:8000/ws`. Both run on
  the laptop, so you never change `App.tsx`.
- **Backend:** start it with `--host 0.0.0.0` so the Pi can reach it
  (the Pi uses HTTP, not WebSocket).
- **Pi -> backend:** set `GCS_API_URL=http://<laptop-ip>:8000`.

---

## Project Structure

```
aeris-project/
|
+-- ground-station/              # runs on the laptop
|   +-- frontend/                # React dashboard (:5173)
|   |   +-- src/
|   |   |   +-- components/     # LiveVideoPane, MissionMap, etc.
|   |   |   +-- pages/          # Dashboard, Map, Detections, Settings
|   |   |   +-- stores/         # Zustand state
|   |   |   +-- hooks/          # useWebSocket, useVideoStream, useGeolocation
|   |   |   +-- lib/            # navigation helper
|   |   |   +-- types/
|   |   |   +-- App.tsx
|   |   |   +-- main.tsx
|   |   +-- package.json
|   |
|   +-- backend/                 # FastAPI (:8000)
|       +-- main.py              # API, WebSocket, video proxy
|       +-- simulate_drone.py    # local fake drone
|       +-- requirements.txt
|       +-- README.md
|
+-- drone-onboard/               # code for the Raspberry Pi on the drone
|   +-- gcs_link.py              # drone -> backend HTTP client
|   +-- raspberry-pi-4b/         # RPi 4B version
|   +-- raspberry-pi-5/          # RPi 5 version (with Hailo-8L)
|
+-- README.md                    # this file
```

---

## System Architecture

```
+------------------------------- AERIS -----------------------------------------------+

   +-------------+   USB camera      +--------------------------+
   |   DRONE     | -----------------> |  RASPBERRY PI 5          |
   |   (UAV)     |   RGB + thermal    |  + Hailo-8L NPU          |
   +-------------+                   |  (edge-AI processing)    |
                                     +------------+-------------+
                                                  |
                                                  v
                                        +-----------------+
                                        |  YOLOv8n        |
                                        |  person         |
                                        |  detection      |
                                        +--------+--------+
                                                 |
                                                 v
                                        +-----------------+
                                        |  JSON packet    |
                                        |  detection +    |
                                        |  vital signs    |
                                        +--------+--------+
                                                 |
        +----------------------+----------------+----------------------+
        |                      |                                       |
        v                      v                                       v
+-----------------+    +-----------------+                     +-----------------+
|  5GHz Wi-Fi     |    |  915/923MHz     |                     |   MAVLink       |
|  video stream   |    |  LoRa           |                     |   telemetry     |
|  ~5-6 Mbps      |    |  backup link    |                     |                 |
|  <105ms latency |    |  <3% PLR        |                     |                 |
+--------+--------+    +--------+--------+                     +--------+--------+
         |                      |                                       |
         +----------+-----------+                                       |
                    |                                                   |
                    v                                                   v
          +---------------------+                            +--------------------+
          |  FASTAPI BACKEND    |                            |  Ground Control    |
          |  WebSocket server   | <------------------------ |  Station (GCS)     |
          |  port 8000          |                            |  + SITL sim        |
          +----------+----------+                            +---------+----------+
                     |                                                 |
                     v                                                 |
          +---------------------+                                     |
          |  REACT FRONTEND     | <------------------------------------+
          |  Vite + TypeScript  |
          |  port 5173          |
          |  - live feed        |
          |  - mission map      |
          |  - detections table |
          |  - UAV telemetry    |
          |  - link health      |
          |  - settings         |
          +----------+----------+
                     |
                     v
          +---------------------+
          |  OPERATOR (MDRRMO)  |
          |  browser console    |
          +---------------------+
```

### Design rules

1. **Split the links** - Video uses 5GHz Wi-Fi. Telemetry uses
   915/923MHz LoRa. They do not interfere with each other.
2. **Edge-AI** - YOLOv8 runs on the Pi 5 itself (under 105ms), not in
   the cloud (150-200ms).
3. **No single point of failure** - Multi-hop routing up to 8 km range.
4. **Compress the video** - H.264 turns 200 Mbps into 5-6 Mbps over UDP.
5. **Navigation first** - Position data is sent more often than video.

---

## Features

### Dashboard
- Real-time video feed from the drone camera (MJPEG proxy)
- Interactive map with UAV and survivor markers (street and satellite
  view, offline badge when tiles fail)
- Live person detection with YOLOv8 (pushed over WebSocket, with sound)
- Detection alerts: confidence, GPS (N/S/E/W), thermal, plus
  cooldown and min-confidence settings
- UAV telemetry: altitude, speed, battery, heading, GPS
- Comm link health: 5GHz Wi-Fi and 915MHz LoRa
- Mission control: start/end, timer, auto GPS lock from the browser
- Settings: save/discard, diagnostics, CSV export, factory reset
- URL routing: `/livefeed`, `/map`, and the rest are shareable

### Data flow
1. The Pi 5 captures frames from the USB camera.
2. YOLOv8 detects people on the Pi itself.
3. `gcs_link.py` POSTs telemetry and detections to the backend on
   port 8000.
4. The backend stores the detections and broadcasts them over
   WebSocket.
5. The frontend updates the store and the page re-renders.

---

## Tech Stack

### Frontend
Vite, React 19, TypeScript, Zustand (with localStorage), Tailwind CSS,
Leaflet, Phosphor Icons, react-router-dom.

### Backend
FastAPI, Uvicorn, WebSocket, HTTP video proxy.

### Onboard (drone)
Python 3.11+, Raspberry Pi 5 (Hailo-8L), YOLOv8 (ultralytics), OpenCV,
PyTorch, Flask (video), requests (GCS link).

---

## Component Docs

| Component | README |
|-----------|--------|
| Frontend (dashboard) | [`ground-station/frontend/README.md`](./ground-station/frontend/README.md) |
| Backend (FastAPI) | [`ground-station/backend/README.md`](./ground-station/backend/README.md) |
| RPi 4B (detection) | [`drone-onboard/raspberry-pi-4b/README.md`](./drone-onboard/raspberry-pi-4b/README.md) |
| RPi 5 (detection + Hailo) | [`drone-onboard/raspberry-pi-5/README.md`](./drone-onboard/raspberry-pi-5/README.md) |

---

## Troubleshooting

### Frontend will not start
```bash
cd ground-station/frontend
rm -rf node_modules package-lock.json
npm install
```

### Backend refuses connections
```bash
ss -ltnp | grep :8000          # is the port busy?
pkill -f "uvicorn main:app"    # kill the old process if needed
```

### Drone not connecting
```bash
# on the laptop - is the backend up?
curl http://localhost:8000/api/mission          # should be 200
curl http://localhost:8000/api/drone/status     # should say connected:true

# on the Pi - can it reach the laptop? (same Wi-Fi required)
ping <laptop-ip>
curl http://<laptop-ip>:8000/api/mission
```

### Camera not detected on the Pi
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
| Video latency (5GHz) | under 105 ms |
| Packet loss ratio (LoRa) | under 3% |
| RSSI (video) | -85 dBm or better |
| RSSI (telemetry) | -80 dBm or better |
| Operational range | 10-200 m |
| Altitude envelope | 10-50 m |
| Edge-AI latency | under 105 ms |

---

## License

MIT License. Educational prototype.

---

## Repository

https://github.com/aeris-team/aeris-project

For problems, check the component READMEs above.
