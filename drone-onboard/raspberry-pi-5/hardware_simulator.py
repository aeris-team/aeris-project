"""
hardware_simulator.py - Raspberry Pi 5 Hardware Simulation Layer
===============================================================

A lightweight, dependency-free simulation of Raspberry Pi 5 system
telemetry. It produces realistic values for:

    - CPU model / device name      (from config.py)
    - CPU usage (%)                 (smooth random walk)
    - RAM usage (used / total)      (smooth random walk)
    - CPU temperature (°C)          (smooth random walk, Pi-like range)
    - System uptime (HH:MM:SS)      (counts from process start)
    - Camera status                 (mirrors DEVICE/CAMERA config)
    - LoRa status                   ("Simulation Mode")
    - Python runtime                ("Running")
    - OpenCV version                (imported from cv2)

Nothing here touches real hardware — no GPIO, no psutil, no OS calls
beyond the process start time. The values are *simulated* so the app
can be demonstrated as if deployed on a real Raspberry Pi 5.

Integration:
    - main.py starts `HardwareSimulator.run()` in a background thread.
    - dashboard.py reads `HardwareSimulator.snapshot()` (or the shared
      dict) to display the "Raspberry Pi 5 System Status" card.
"""

import time
import random
import threading

import cv2

from config import (
    DEVICE_NAME, CPU_MODEL, RAM_SIZE, STATUS,
    LORA_MODE, CAMERA_NAME,
)


class HardwareSimulator:
    """
    Simulates Raspberry Pi 5 hardware telemetry.

    Thread-safe: a single background thread updates an internal dict
    every `interval` seconds; readers call `snapshot()` to get a
    consistent copy at any time.
    """

    # Total RAM parsed from config "8GB" -> bytes-ish figure for display.
    _RAM_TOTAL_GB = 8 if "8" in RAM_SIZE else 4

    def __init__(self, interval: float = 2.0):
        self.interval = interval
        self._lock = threading.Lock()
        self._stop = False
        self._thread: threading.Thread | None = None

        self._start_time = time.time()

        # Smooth random-walk state
        self._cpu_usage = random.uniform(8.0, 28.0)      # %
        self._ram_used_gb = random.uniform(0.8, 1.6)     # GB
        self._cpu_temp = random.uniform(47.0, 54.0)      # °C

        self._state = self._build_state()

    # ── Internal helpers ────────────────────────────────────────────────

    @staticmethod
    def _clamp(value, lo, hi):
        return max(lo, min(hi, value))

    def _uptime_string(self) -> str:
        secs = int(time.time() - self._start_time)
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _step(self):
        """Advance the simulated telemetry one tick (smooth random walk)."""
        # CPU usage: wander within a realistic Pi idle/light-load band.
        self._cpu_usage = self._clamp(
            self._cpu_usage + random.uniform(-3.0, 3.0), 3.0, 65.0
        )
        # RAM usage: slow drift, bounded well under total.
        self._ram_used_gb = self._clamp(
            self._ram_used_gb + random.uniform(-0.08, 0.08),
            0.6, self._RAM_TOTAL_GB * 0.5,
        )
        # CPU temperature: correlates loosely with CPU usage.
        target = 44.0 + self._cpu_usage * 0.25
        self._cpu_temp = self._clamp(
            self._cpu_temp + (target - self._cpu_temp) * 0.15
            + random.uniform(-0.4, 0.4),
            40.0, 70.0,
        )

    def _build_state(self) -> dict:
        try:
            opencv_version = cv2.__version__
        except Exception:
            opencv_version = "unknown"

        return {
            "device_name":    DEVICE_NAME,
            "cpu_model":      CPU_MODEL,
            "cpu_usage_pct":  round(self._cpu_usage, 1),
            "ram_used_gb":    round(self._ram_used_gb, 1),
            "ram_total_gb":   self._RAM_TOTAL_GB,
            "cpu_temp_c":     round(self._cpu_temp, 1),
            "uptime":         self._uptime_string(),
            "camera_status":  "Connected" if "Connected" in CAMERA_NAME else CAMERA_NAME,
            "lora_status":    LORA_MODE,
            "python_runtime": "Running",
            "opencv_version": opencv_version,
            "device_status":  STATUS,
        }

    # ── Public read API ─────────────────────────────────────────────────

    def snapshot(self) -> dict:
        """Return a consistent copy of the current simulated telemetry."""
        with self._lock:
            return dict(self._state)

    # ── Lifecycle (background thread) ───────────────────────────────────

    def _loop(self):
        while not self._stop:
            self._step()
            with self._lock:
                self._state = self._build_state()
            time.sleep(self.interval)

    def start(self):
        """Start the simulation background thread (idempotent)."""
        if self._thread and self._thread.is_alive():
            return
        self._stop = False
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Signal the background thread to stop."""
        self._stop = True
        if self._thread:
            self._thread.join(timeout=2.0)


# ── Module-level singleton ────────────────────────────────────────────────
# Reused across main.py and dashboard.py so both read the same live values.
simulator = HardwareSimulator()
