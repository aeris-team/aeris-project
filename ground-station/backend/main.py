from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List
from collections import deque
import json
import asyncio
import math
import os
import time
import urllib.request
from datetime import datetime
import random

app = FastAPI(title="AERIS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

telemetry_data = {
    "altitude": 120.4,
    "speed": 8.2,
    "heading": 218,
    "battery": 78,
    "lat": 14.2500,
    "lng": 120.7300,
}

survivor_data = {
    "lat": 14.2515,
    "lng": 120.7310,
}

# In-memory detection log (newest first, capped)
DETECTIONS: deque = deque(maxlen=200)

# Monotonic ts of last real drone telemetry (0 = never)
_drone_last_seen = 0.0
DRONE_TELEMETRY_TIMEOUT_S = 5.0


def _drone_is_live() -> bool:
    return _drone_last_seen > 0 and (time.monotonic() - _drone_last_seen) < DRONE_TELEMETRY_TIMEOUT_S


def _normalize_confidence(value) -> float:
    try:
        c = float(value)
    except (TypeError, ValueError):
        return 70.0
    if 0.0 < c <= 1.0:
        c *= 100.0
    return max(0.0, min(100.0, c))


def _apply_telemetry(payload: dict) -> None:
    global _drone_last_seen
    for key in ("altitude", "speed", "heading", "battery", "lat", "lng"):
        if key in payload and payload[key] is not None:
            try:
                telemetry_data[key] = float(payload[key])
            except (TypeError, ValueError):
                pass
    if "lat" in telemetry_data and "lng" in telemetry_data:
        survivor_data["lat"] = telemetry_data["lat"] + 0.0015
        survivor_data["lng"] = telemetry_data["lng"] + 0.0010
    _drone_last_seen = time.monotonic()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                mtype = message.get("type")
                if mtype == "detection":
                    entry = {
                        "type": "detection",
                        "id": f"ALERT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                        "timestamp": datetime.now().isoformat(),
                        "confidence": _normalize_confidence(message.get("confidence", 92)),
                        "lat": float(message.get("lat", survivor_data["lat"])),
                        "lng": float(message.get("lng", survivor_data["lng"])),
                        "altitude": float(message.get("altitude", telemetry_data["altitude"])),
                        "distance": float(message.get("distance", 120)),
                    }
                    DETECTIONS.appendleft(entry)
                    await manager.broadcast(entry)
                elif mtype == "telemetry":
                    _apply_telemetry(message)
                    await manager.broadcast({"type": "telemetry", "source": "drone", **telemetry_data})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/telemetry")
async def get_telemetry():
    return {**telemetry_data, "source": "drone" if _drone_is_live() else "sim"}


@app.post("/api/telemetry")
async def post_telemetry(payload: dict):
    """Drone → GCS: push real telemetry (battery, GPS, etc.)."""
    _apply_telemetry(payload)
    await manager.broadcast({"type": "telemetry", "source": "drone", **telemetry_data})
    return {"status": "ok", "source": "drone"}


@app.get("/api/detections")
async def get_detections():
    return list(DETECTIONS)


@app.post("/api/detection")
async def add_detection(detection: dict):
    """Drone → GCS: push a survivor detection."""
    entry = {
        "type": "detection",
        "id": f"ALERT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "confidence": _normalize_confidence(detection.get("confidence", 92)),
        "lat": float(detection.get("lat", survivor_data["lat"])),
        "lng": float(detection.get("lng", survivor_data["lng"])),
        "altitude": float(detection.get("altitude", telemetry_data["altitude"])),
        "distance": float(detection.get("distance", 120)),
    }
    DETECTIONS.appendleft(entry)
    await manager.broadcast(entry)
    return {"status": "ok"}


@app.get("/api/drone/status")
async def drone_status():
    """Is a real drone currently pushing telemetry?"""
    return {
        "connected": _drone_is_live(),
        "last_seen_age_s": (round(time.monotonic() - _drone_last_seen, 2) if _drone_last_seen else None),
        "video_source": DRONE_VIDEO_URL,
    }

@app.get("/api/mission")
async def get_mission():
    return {
        "id": "mission-001",
        "name": "Local Area Search",
        "startedAt": "07:30 AM",
        "status": "active"
    }

# ── Live video (drone camera MJPEG proxy) ──────────────────────────────────

DRONE_VIDEO_URL = os.getenv("DRONE_VIDEO_URL", "http://127.0.0.1:5000/video_feed")
_video_probe_cache = {"online": False, "ts": 0.0}


def _probe_video(timeout: float = 1.5) -> bool:
    now = time.monotonic()
    if now - _video_probe_cache["ts"] < 1.0:
        return _video_probe_cache["online"]
    online = False
    try:
        with urllib.request.urlopen(DRONE_VIDEO_URL, timeout=timeout) as resp:
            online = getattr(resp, "status", 200) == 200
    except Exception:
        online = False
    _video_probe_cache["online"] = online
    _video_probe_cache["ts"] = now
    return online


@app.get("/video/status")
async def video_status():
    online = await asyncio.to_thread(_probe_video)
    return {"online": online, "source": DRONE_VIDEO_URL}


@app.get("/video/stream")
async def video_stream():
    try:
        resp = await asyncio.to_thread(
            urllib.request.urlopen, DRONE_VIDEO_URL, timeout=10
        )
    except Exception:
        raise HTTPException(status_code=502, detail="Drone camera offline")

    media_type = resp.headers.get("Content-Type") or "multipart/x-mixed-replace; boundary=frame"

    def iter_upstream():
        try:
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                yield chunk
        finally:
            resp.close()

    return StreamingResponse(
        iter_upstream(),
        media_type=media_type,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "X-Accel-Buffering": "no",
        },
    )

async def telemetry_broadcaster():
    while True:
        # Only simulate when no real drone has reported recently
        if not _drone_is_live():
            telemetry_data["altitude"] += (random.random() - 0.5) * 0.5
            telemetry_data["speed"] = max(0, telemetry_data["speed"] + (random.random() - 0.5) * 0.2)
            if random.random() > 0.95:
                telemetry_data["battery"] = max(0, telemetry_data["battery"] - 0.1)
            telemetry_data["heading"] = (telemetry_data["heading"] + 2) % 360

            time_val = datetime.now().timestamp() / 5000
            telemetry_data["lat"] = survivor_data["lat"] + (math.sin(time_val) * 0.001)
            telemetry_data["lng"] = survivor_data["lng"] + (math.cos(time_val) * 0.001)

            await manager.broadcast({"type": "telemetry", "source": "sim", **telemetry_data})
        else:
            await manager.broadcast({"type": "telemetry", "source": "drone", **telemetry_data})
        await asyncio.sleep(1.5)

@app.on_event("startup")
async def startup():
    asyncio.create_task(telemetry_broadcaster())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
