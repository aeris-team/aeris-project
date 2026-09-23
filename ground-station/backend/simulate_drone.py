"""
simulate_drone.py - Local fake drone for the AERIS dashboard
=============================================================

Run on the SAME machine as the ground-station backend (no hardware needed):

  1. Serves MJPEG on http://127.0.0.1:5000/video_feed
     → backend /video/status online → dashboard green "Drone connected"
  2. POSTs telemetry to http://localhost:8000/api/telemetry
  3. Occasionally POSTs detections to /api/detection

Usage:
  python simulate_drone.py
  GCS_API_URL=http://localhost:8000 VIDEO_PORT=5000 python simulate_drone.py
"""

from __future__ import annotations

import math
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

sys.stdout.reconfigure(line_buffering=True)  # logs visible when redirected

GCS_API_URL = os.getenv("GCS_API_URL", "http://localhost:8000").rstrip("/")
VIDEO_HOST = os.getenv("VIDEO_HOST", "127.0.0.1")
VIDEO_PORT = int(os.getenv("VIDEO_PORT", "5000"))
TELEMETRY_EVERY_S = float(os.getenv("TELEMETRY_EVERY_S", "1.0"))
DETECT_EVERY_S = float(os.getenv("DETECT_EVERY_S", "8"))

# Minimal valid JPEG (8x8 solid gray) — enough for MJPEG probe/stream
_JPEG = bytes.fromhex(
    "ffd8ffe000104a46494600010100000100010000"
    "ffdb004300ff0b0d0d0d0d0d0d0d0d0d0d0d0d0d"
    "0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d"
    "0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d"
    "0d0d0d0d0d0d0d0d0d0d0d0d0d0d0dffc0000b08"
    "0008000801011100ffc4001f0000010501010101"
    "010100000000000000000102030405060708090a"
    "0bffc400b5100002010303020403050504040000"
    "017d010203000411051221314106135161072271"
    "14328191a1082342b1c11552d1f0243362728209"
    "0a161718191a25262728292a3435363738393a43"
    "4445464748494a535455565758595a6364656667"
    "68696a737475767778797a838485868788898a92"
    "939495969798999aa2a3a4a5a6a7a8a9aab2b3b4"
    "b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6"
    "d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6"
    "f7f8f9faffda0008010100003f00f9fe828a28a0"
    "0fffd9"
)


class _State:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.t0 = time.time()
        self.detections = 0

    def frame_jpeg(self) -> bytes:
        # Animate brightness via comment APP0 padding is overkill —
        # same JPEG is fine for connectivity; dashboards only need bytes.
        return _JPEG


STATE = _State()


class VideoHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # quiet
        pass

    def do_GET(self) -> None:
        if self.path.startswith("/video_feed"):
            self.send_response(200)
            self.send_header(
                "Content-Type", "multipart/x-mixed-replace; boundary=frame"
            )
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            try:
                while True:
                    jpeg = STATE.frame_jpeg()
                    self.wfile.write(
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
                    )
                    self.wfile.flush()
                    time.sleep(0.04)  # ~25 fps
            except (BrokenPipeError, ConnectionResetError):
                return
        elif self.path in ("/", "/health"):
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()


def serve_video() -> None:
    server = ThreadingHTTPServer((VIDEO_HOST, VIDEO_PORT), VideoHandler)
    print(f"[video] MJPEG → http://{VIDEO_HOST}:{VIDEO_PORT}/video_feed")
    server.serve_forever()


def telemetry_loop() -> None:
    lat0, lng0 = 14.2500, 120.7300
    i = 0
    while True:
        i += 1
        t = time.time() - STATE.t0
        payload = {
            "type": "telemetry",
            "altitude": 80 + 10 * math.sin(t / 15),
            "speed": 6 + 2 * math.sin(t / 10),
            "heading": (t * 4) % 360,
            "battery": max(20.0, 95 - t * 0.02),
            "lat": lat0 + 0.0008 * math.sin(t / 20),
            "lng": lng0 + 0.0008 * math.cos(t / 20),
        }
        try:
            requests.post(f"{GCS_API_URL}/api/telemetry", json=payload, timeout=2)
        except requests.RequestException as e:
            print(f"[telemetry] backend down? {e}")
        time.sleep(TELEMETRY_EVERY_S)


def detection_loop() -> None:
    while True:
        time.sleep(DETECT_EVERY_S)
        with STATE.lock:
            STATE.detections += 1
            n = STATE.detections
        t = time.time() - STATE.t0
        payload = {
            "type": "detection",
            "confidence": 80 + (n % 15),
            "lat": 14.2515 + 0.0005 * math.sin(t / 25),
            "lng": 120.7310 + 0.0005 * math.cos(t / 25),
            "altitude": 90,
            "distance": 60 + (n % 40),
        }
        try:
            r = requests.post(f"{GCS_API_URL}/api/detection", json=payload, timeout=2)
            print(f"[detection] #{n} → {r.status_code}")
        except requests.RequestException as e:
            print(f"[detection] backend down? {e}")


def main() -> None:
    print("=" * 50)
    print("  AERIS local drone simulator")
    print(f"  Video : http://{VIDEO_HOST}:{VIDEO_PORT}/video_feed")
    print(f"  GCS   : {GCS_API_URL}")
    print("  Ctrl+C to stop")
    print("=" * 50)
    threading.Thread(target=serve_video, daemon=True).start()
    threading.Thread(target=telemetry_loop, daemon=True).start()
    detection_loop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nstopped")
