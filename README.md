# AERIS - Off-Grid UAV System for Search and Rescue

A complete drone-based search and rescue system with real-time person detection, telemetry monitoring, and ground control dashboard.

---

## Project Structure

```
aerisproject/
│
├── ground-station/              # Operator's Command Center (runs on laptop/PC)
│   ├── frontend/                # React + TypeScript Dashboard
│   │   ├── src/
│   │   │   ├── components/     # UI components
│   │   │   ├── pages/          # Page components
│   │   │   ├── stores/         # State management
│   │   │   ├── hooks/          # Custom hooks
│   │   │   ├── types/          # TypeScript types
│   │   │   ├── App.tsx
│   │   │   ├── main.tsx
│   │   │   └── index.css
│   │   ├── public/             # Static assets
│   │   ├── package.json
│   │   ├── tailwind.config.js
│   │   ├── vite.config.ts
│   │   └── README.md
│   │
│   └── backend/                 # FastAPI Backend
│       ├── main.py
│       ├── requirements.txt
│       └── README.md
│
├── drone-onboard/               # Code that runs on Raspberry Pi (mounted on drone)
│   ├── raspberry-pi-4b/         # RPi 4B version
│   │   ├── main.py
│   │   ├── detector.py
│   │   ├── sender.py
│   │   ├── config.py
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   └── raspberry-pi-5/          # RPi 5 version
│       ├── main.py
│       ├── detector.py
│       ├── sender.py
│       ├── config.py
│       ├── requirements.txt
│       └── README.md
│
├── docs/                        # Documentation
│   ├── system-flow.md
│   ├── api-reference.md
│   └── troubleshooting.md
│
└── README.md                    # This file
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AERIS SYSTEM FLOW                               │
└─────────────────────────────────────────────────────────────────────────────┘

   ┌─────────────┐      USB Camera         ┌─────────────────┐
   │   DRONE     │ ──────────────────────▶ │  RASPBERRY PI   │
   │  (UAV)      │                         │   (Onboard)     │
   └─────────────┘                         └────────┬────────┘
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
                                            │  (Detection)    │
                                            └────────┬────────┘
                                                     │
                    ┌────────────────────────────────┼────────────────────────────────┐
                    │                                │                                │
                    ▼                                ▼                                ▼
         ┌─────────────────┐            ┌─────────────────┐            ┌─────────────────┐
         │  5GHz Wi-Fi      │            │  915MHz LoRa    │            │   Video Stream  │
         │  (Telemetry)     │            │  (Backup Link)  │            │   (RTSP/HLS)   │
         └────────┬────────┘            └────────┬────────┘            └────────┬────────┘
                  │                               │                               │
                  └───────────────────────────────┼───────────────────────────────┘
                                                  │
                                                  ▼
                                    ┌─────────────────────────┐
                                    │   FASTAPI BACKEND       │
                                    │   (WebSocket Server)    │
                                    │   Port: 8000             │
                                    └────────────┬────────────┘
                                                 │
                                                 ▼
                                    ┌─────────────────────────┐
                                    │   REACT FRONTEND        │
                                    │   (Vite + TypeScript)    │
                                    │   Port: 5173             │
                                    │                         │
                                    │   - Live Feed Display    │
                                    │   - Mission Map         │
                                    │   - Detections Table    │
                                    │   - UAV Telemetry       │
                                    │   - Comm Link Health    │
                                    └─────────────────────────┘
                                                  │
                                                  ▼
                                    ┌─────────────────────────┐
                                    │   OPERATOR              │
                                    │   (Browser/Dashboard)   │
                                    └─────────────────────────┘
```

---

## Quick Start

### 1. Setup Ground Control Station (Your Laptop)

#### Install Required Software

| Software | Version | Download |
|----------|---------|----------|
| Node.js | 20+ | https://nodejs.org/ |
| Python | 3.11+ | https://python.org/ |
| Git | Latest | https://git-scm.com/ |
| Chrome/Chromium | Latest | https://www.google.com/chrome/ |

#### Clone and Install

```bash
git clone https://github.com/amblessly/aeris-project.git
cd aeris-project
cd ground-station/frontend
npm install
```

#### Run the Dashboard

```bash
# Start backend first (Terminal 1)
cd ground-station/backend
python main.py

# Start frontend (Terminal 2)
cd ground-station/frontend
npm run dev

# Access dashboard
# Open: http://localhost:5173
```

---

### 2. Setup Raspberry Pi (Drone Onboard)

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

# Install Chromium (optional, for browser)
sudo apt install -y chromium-browser

# Clone project
git clone https://github.com/amblessly/aeris-project.git
cd aeris-project/drone-onboard/raspberry-pi-5

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Run Detection in Background

```bash
# Start in screen session
screen -S aeris
source venv/bin/activate
python main.py

# Detach: Press Ctrl+A, then D

# Reconnect later:
screen -r aeris
```

---

## Connecting Everything

### Network Setup

```
Ground Station (Laptop)          Raspberry Pi (Drone)
IP: 192.168.1.50                 IP: 192.168.1.100
       │                                 │
       │  ┌──────────────────────────┐  │
       └──┤  Same Wi-Fi Network      ├──┘
          └──────────────────────────┘
```

### WebSocket Connection

The frontend automatically connects to `ws://localhost:8000/ws` when the backend is running.

**For local development:**
- Frontend: `ws://localhost:8000/ws` (default)
- Backend: `ws://localhost:8000/ws`

**For network deployment:**

Edit `ground-station/frontend/src/hooks/useWebSocket.ts`:

```typescript
// Change to your GCS IP address
useWebSocket('ws://192.168.1.50:8000/ws');
```

### Update RPi Backend URL

Edit `drone-onboard/raspberry-pi-5/config.py`:

```python
# Change to your GCS IP address
BACKEND_WS_URL = "ws://192.168.1.50:8000/ws"
```

---

## Folder Organization Explained

| Folder | Purpose | Runs On |
|--------|---------|---------|
| `ground-station/frontend/` | Web dashboard (UI) | Laptop/PC |
| `ground-station/backend/` | API server (WebSocket) | Laptop/PC |
| `drone-onboard/raspberry-pi-4b/` | Detection code | RPi 4B |
| `drone-onboard/raspberry-pi-5/` | Detection code | RPi 5 |

**Why this structure?**
- **Separation of concerns** - Frontend, backend, and onboard code are clearly separated
- **Easy deployment** - Each folder is independent
- **Clear purpose** - `ground-station` = operator side, `drone-onboard` = drone side

---

## Tech Stack

### Frontend
- **Vite** - Build tool
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Zustand** - State management
- **Tailwind CSS** - Styling
- **Leaflet** - Maps

### Backend
- **FastAPI** - API framework
- **WebSocket** - Real-time communication
- **Pydantic** - Data validation

### Onboard
- **Python 3.11+** - Main language
- **OpenCV** - Image processing
- **YOLOv8** - Person detection
- **PyTorch** - Deep learning

---

## Features

- ✅ **Real-time video feed** from drone camera
- ✅ **Live person detection** using YOLOv8
- ✅ **Interactive map** with UAV and survivor positions
- ✅ **Telemetry monitoring** (altitude, speed, battery, GPS)
- ✅ **Communication link health** (5GHz Wi-Fi + 915MHz LoRa)
- ✅ **Detection alerts** with confidence scores
- ✅ **Mission management** (start/end tracking)
- ✅ **Multi-device support** (RPi 4B and RPi 5)
- ✅ **WebSocket integration** - real-time data from backend
- ✅ **Background processing** with screen

---

## Component Documentation

| Component | README |
|-----------|--------|
| Frontend | `ground-station/frontend/README.md` |
| Backend | `ground-station/backend/README.md` |
| RPi 4B | `drone-onboard/raspberry-pi-4b/README.md` |
| RPi 5 | `drone-onboard/raspberry-pi-5/README.md` |

---

## Troubleshooting

### Frontend won't start
```bash
# Delete node_modules and reinstall
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
# Check USB devices
lsusb

# Check video devices
ls /dev/video*

# Test camera
python test_cam.py
```

---

## License

MIT License - Educational prototype project.

---

## Support

For issues, check individual component READMEs for detailed troubleshooting.
