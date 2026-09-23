"""
gcs_link.py - Drone → Ground Station link
==========================================

Sends real telemetry + detections from the onboard pipeline to the
AERIS FastAPI backend (ground-station/backend/main.py).

Local (same laptop as dashboard):
    GCS_API_URL = "http://localhost:8000"

Network (Pi on same Wi-Fi as GCS laptop):
    GCS_API_URL = "http://192.168.1.50:8000"   # GCS laptop IP
"""

from __future__ import annotations

import logging
import os
import time

import requests

logger = logging.getLogger(__name__)

DEFAULT_API = os.getenv("GCS_API_URL", "http://localhost:8000")


class GCSLink:
    """HTTP client: drone → FastAPI backend."""

    def __init__(self, api_url: str | None = None, timeout: float = 2.0):
        self.api_url = (api_url or DEFAULT_API).rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self.sent_telemetry = 0
        self.sent_detections = 0
        self.last_error: str | None = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def health(self) -> bool:
        """Ping backend. True if reachable."""
        try:
            r = self._session.get(f"{self.api_url}/api/mission", timeout=self.timeout)
            self._connected = r.ok
            self.last_error = None if r.ok else f"HTTP {r.status_code}"
        except requests.RequestException as e:
            self._connected = False
            self.last_error = str(e)
        return self._connected

    def send_telemetry(
        self,
        *,
        altitude: float,
        speed: float,
        heading: float,
        battery: float,
        lat: float,
        lng: float,
    ) -> bool:
        payload = {
            "type": "telemetry",
            "altitude": altitude,
            "speed": speed,
            "heading": heading,
            "battery": battery,
            "lat": lat,
            "lng": lng,
        }
        return self._post("/api/telemetry", payload, counter="telemetry")

    def send_detection(
        self,
        *,
        confidence: float,
        lat: float | None = None,
        lng: float | None = None,
        altitude: float | None = None,
        distance: float | None = None,
    ) -> bool:
        payload: dict = {"type": "detection", "confidence": confidence}
        if lat is not None:
            payload["lat"] = lat
        if lng is not None:
            payload["lng"] = lng
        if altitude is not None:
            payload["altitude"] = altitude
        if distance is not None:
            payload["distance"] = distance
        return self._post("/api/detection", payload, counter="detections")

    def _post(self, path: str, payload: dict, counter: str) -> bool:
        try:
            r = self._session.post(
                f"{self.api_url}{path}", json=payload, timeout=self.timeout
            )
            ok = r.ok
            self._connected = True
            self.last_error = None if ok else f"HTTP {r.status_code}"
            if ok:
                setattr(self, f"sent_{counter}", getattr(self, f"sent_{counter}") + 1)
            return ok
        except requests.RequestException as e:
            self._connected = False
            self.last_error = str(e)
            logger.debug("[GCSLink] %s failed: %s", path, e)
            return False

    def close(self) -> None:
        self._session.close()


def backoff_sleep(attempt: int, base: float = 0.5, cap: float = 5.0) -> None:
    time.sleep(min(cap, base * (2 ** min(attempt, 4))))
