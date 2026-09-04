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

# ── Device Identity ────────────────────────────────────────────────────────
DEVICE_NAME     = "Raspberry Pi 5"
DEVICE_VERSION  = "1.0"

# ── Simulated Hardware Information ────────────────────────────────────────
CPU_MODEL       = "Broadcom BCM2712"
RAM_SIZE        = "8GB"
STATUS          = "Ready"
LORA_MODE       = "Simulation Mode"
CAMERA_NAME     = "USB Camera (Connected)"
