"""
config.py - Raspberry Pi 4 Model B Device Configuration
=======================================================

Raspberry Pi-specific values for the AI-powered health monitoring
prototype. Only hardware/device metadata lives here. Functional
pipeline constants (LoRa ports, vital-sign ranges, etc.) remain in
utils.py so the existing workflow is preserved unchanged.

Target Hardware:
    - Raspberry Pi 4 Model B
    - Python 3
    - OpenCV
    - USB Camera
    - LoRa Module (future implementation)
"""

import os

# ── Device Identity ────────────────────────────────────────────────────────
DEVICE_NAME     = "Raspberry Pi 4 Model B"
DEVICE_VERSION  = "1.0"

# ── Ground Station (FastAPI backend on GCS laptop) ────────────────────────
GCS_API_URL     = os.getenv("GCS_API_URL", "http://localhost:8000")

# ── Simulated Hardware Information ────────────────────────────────────────
CPU_MODEL       = "Broadcom BCM2711"
RAM_SIZE        = "4GB"
STATUS          = "Ready"
LORA_MODE       = "Simulation Mode"
CAMERA_NAME     = "USB Camera (Connected)"
