from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
import asyncio
import math
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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "detection":
                    await manager.broadcast({
                        "type": "detection",
                        "id": f"ALERT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                        "timestamp": datetime.now().isoformat(),
                        "confidence": message.get("confidence", 0.92),
                        "lat": message.get("lat", survivor_data["lat"]),
                        "lng": message.get("lng", survivor_data["lng"]),
                        "altitude": message.get("altitude", telemetry_data["altitude"]),
                        "distance": message.get("distance", 120),
                    })
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/telemetry")
async def get_telemetry():
    return telemetry_data

@app.get("/api/detections")
async def get_detections():
    return []

@app.post("/api/detection")
async def add_detection(detection: dict):
    await manager.broadcast({
        "type": "detection",
        "id": f"ALERT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        **detection
    })
    return {"status": "ok"}

@app.get("/api/mission")
async def get_mission():
    return {
        "id": "mission-001",
        "name": "Maragondon, Cavite Search",
        "startedAt": "07:30 AM",
        "status": "active"
    }

async def telemetry_broadcaster():
    while True:
        telemetry_data["altitude"] += (random.random() - 0.5) * 0.5
        telemetry_data["speed"] = max(0, telemetry_data["speed"] + (random.random() - 0.5) * 0.2)
        if random.random() > 0.95:
            telemetry_data["battery"] = max(0, telemetry_data["battery"] - 0.1)
        telemetry_data["heading"] = (telemetry_data["heading"] + 2) % 360
        
        time_val = datetime.now().timestamp() / 5000
        telemetry_data["lat"] = survivor_data["lat"] + (math.sin(time_val) * 0.001)
        telemetry_data["lng"] = survivor_data["lng"] + (math.cos(time_val) * 0.001)
        
        await manager.broadcast({"type": "telemetry", **telemetry_data})
        await asyncio.sleep(1.5)

@app.on_event("startup")
async def startup():
    asyncio.create_task(telemetry_broadcaster())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
