"""
config.py - Raspberry Pi 5 Device Configuration
================================================

Raspberry Pi-specific values for the AI-powered health monitoring
prototype. Only hardware/device metadata lives here. Functional
pipeline constants (LoRa ports, vital-sign ranges, etc.) remain in
utils.py so the existing workflow is preserved unchanged.

Target Hardware:
    - Raspberry Pi 5
    - Python 3
    - OpenCV
    - USB Camera
    - LoRa Module (future implementation)
"""

import os

# ── Device Identity ────────────────────────────────────────────────────────
DEVICE_NAME     = "Raspberry Pi 5"
DEVICE_VERSION  = "1.0"

# ── Ground Station (FastAPI backend on GCS laptop) ────────────────────────
# Local test (backend same machine): default localhost
# Real Pi on same Wi-Fi: GCS_API_URL=http://192.168.1.50:8000
GCS_API_URL     = os.getenv("GCS_API_URL", "http://localhost:8000")

# ── Simulated Hardware Information ────────────────────────────────────────
CPU_MODEL       = "Broadcom BCM2712"
RAM_SIZE        = "8GB"
STATUS          = "Ready"
LORA_MODE       = "Simulation Mode"
CAMERA_NAME     = "USB Camera (Connected)"
