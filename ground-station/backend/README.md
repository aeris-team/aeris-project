# AERIS Backend - FastAPI

WebSocket server for AERIS.

---

## Setup

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running

```bash
# Development (with hot reload)
uvicorn main:app --reload --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Or simply
python main.py
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ws` | WebSocket | Real-time data |
| `/api/telemetry` | GET | Current UAV telemetry |
| `/api/telemetry` | POST | Ingest telemetry from drone (0–1 or 0–100 conf normalized) |
| `/api/drone/status` | GET | Drone connection status (`connected`, `last_seen_age_s`) |
| `/api/detections` | GET | All detections |
| `/api/detection` | POST | Add new detection |
| `/api/mission` | GET | Current mission info |
| `/video/status` | GET | Proxied drone MJPEG feed status |
| `/video/stream` | GET | Proxied drone MJPEG stream |

### Drone link / sim

```bash
# Local fake drone (MJPEG :5000 + telemetry/detection POSTs)
./venv/bin/python3 simulate_drone.py

# Real Pi (same Wi-Fi as laptop; drone Flask dashboard on :5000)
GCS_API_URL=http://<laptop-ip>:8000 python main.py
```

| Env var | Default | Purpose |
|---------|---------|---------|
| `GCS_API_URL` | `http://localhost:8000` | drone → backend |
| `DRONE_VIDEO_URL` | `http://127.0.0.1:5000/video_feed` | backend → drone MJPEG |
| `VIDEO_PORT` | `5000` | sim MJPEG port |
| `TELEMETRY_EVERY_S` / `DETECT_EVERY_S` | — | sim rates |

## WebSocket Messages

**Client → Server:**
```json
{
  "type": "detection",
  "confidence": 0.92,
  "lat": 14.2515,
  "lng": 120.7310,
  "altitude": 120,
  "distance": 120
}
```

**Server → Client (Telemetry):**
```json
{
  "type": "telemetry",
  "altitude": 120.4,
  "speed": 8.2,
  "heading": 218,
  "battery": 78,
  "lat": 14.2500,
  "lng": 120.7300
}
```

**Server → Client (Detection):**
```json
{
  "type": "detection",
  "id": "ALERT-20260904-123456",
  "timestamp": "2026-09-04T12:34:56",
  "confidence": 92,
  "lat": 14.2515,
  "lng": 120.7310,
  "altitude": 120,
  "distance": 120
}
```

## Testing

```bash
# Test WebSocket (kailangan: ./venv/bin/pip install websocket-client)
python -c "
import websocket
import json
ws = websocket.create_connection('ws://localhost:8000/ws')
ws.send(json.dumps({'type': 'detection', 'confidence': 0.95, 'lat': 14.25, 'lng': 120.73, 'altitude': 120, 'distance': 100}))
print(ws.recv())
ws.close()
"

# Test REST API
curl http://localhost:8000/api/telemetry
```
