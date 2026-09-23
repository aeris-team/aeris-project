# AERIS - Raspberry Pi 5 Detection Module

Detection module para sa AERIS (Raspberry Pi 5 version).

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Detection Pipeline                          │
└─────────────────────────────────────────────────────────────────┘

Camera (USB/IP) ──▶ OpenCV ──▶ YOLOv8 ──▶ JSON ──▶ WebSocket ──▶ Dashboard
                                    │
                                    ▼
                            ┌───────────────┐
                            │  Detection     │
                            │  Screenshot    │
                            │  (saved)       │
                            └───────────────┘
```

---

## Hardware Requirements

| Component | Specification |
|-----------|---------------|
| Raspberry Pi | 5 (8GB recommended) |
| Camera | USB webcam or Raspberry Pi Camera Module 3 |
| Storage | 32GB+ microSD (A2 rated recommended) |
| Power | 5V 5A USB-C PD |
| LoRa Module | SX1278/RFM95W (optional) |
| Cooling | Active cooler recommended |

---

## Differences from RPi 4B

| Feature | RPi 4B | RPi 5 |
|---------|--------|-------|
| CPU | Cortex-A72 | Cortex-A76 |
| RAM | 4GB | 8GB |
| Performance | ~3x baseline | ~5x baseline |
| YOLO Model | yolov8n only | yolov8n, yolov8s, yolov8m |
| FPS (yolov8n) | 5-8 FPS | 15-20 FPS |

---

## Software Requirements

### 1. Raspberry Pi OS (64-bit)

Download from: https://www.raspberrypi.com/software/operating-systems/

**Recommended:** Use the "Raspberry Pi OS (64-bit) with desktop" version.

### 2. Python 3.11+

```bash
# Check Python version (Pi 5 comes with Python 3.11+)
python3 --version

# Install pip
sudo apt install -y python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

### 3. Required Python Packages

```bash
# Activate virtual environment
source venv/bin/activate

# Install PyTorch (CPU version - faster on Pi 5)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install OpenCV
pip install opencv-python-headless

# Install Ultralytics (YOLOv8)
pip install ultralytics

# Install other dependencies
pip install numpy pandas requests websocket-client flask
```

### 4. Screen (for background processes)

```bash
sudo apt install -y screen
```

---

## Quick Start

### 1. Flash OS to SD Card

Use Raspberry Pi Imager:
1. Choose OS → Raspberry Pi OS (64-bit)
2. Choose Storage → Your SD card
3. Click the gear icon:
   - Set hostname: `aeris-pi5`
   - Enable SSH
   - Configure Wi-Fi
   - Set username/password
4. Write

### 2. Initial Setup

```bash
# SSH into Pi 5
ssh pi@aeris-pi5.local

# Update system
sudo apt update && sudo apt upgrade -y

# Enable camera (if using Pi Camera Module 3)
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable

# Enable PCIe (if using M.2 HAT)
# Automatic on Pi 5

# Reboot
sudo reboot
```

### 3. Install Detection Software

```bash
# SSH back in
ssh pi@aeris-pi5.local

# Clone project
git clone https://github.com/amblessly/aeris-project.git
cd aeris-project/drone-onboard/raspberry-pi-5

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test YOLOv8
python3 -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt'); print('YOLOv8 OK')"
```

### 4. Run Detection

```bash
# Activate virtual environment
source venv/bin/activate

# Run detection
python main.py

# Press 'q' to quit
```

---

## Using Screen (Background Process)

### Start Detection in Background

```bash
# Create new screen
screen -S aeris

# Activate environment
source venv/bin/activate

# Run detection
python main.py

# Detach: Press Ctrl+A, then D
```

### Reconnect to Screen

```bash
# List all screens
screen -ls

# Reconnect
screen -r aeris

# If already attached, force detach
screen -d -r aeris
```

### Kill Screen

```bash
screen -X -S aeris quit
```

---

## Configuration

Edit `config.py`:

```python
import os

# Device Configuration
DEVICE_NAME = "AERIS RPi 5"
DEVICE_VERSION = "1.0"
CPU_MODEL = "Broadcom BCM2712"
RAM_SIZE = "8GB"
STATUS = "Active"

# Camera Configuration
CAMERA_INDEX = 0  # 0 for USB webcam, or use IP camera URL

# IP Webcam (Android phone as camera)
IP_CAMERA_URL = "http://192.168.1.100:8080/video"

# Detection Settings
CONFIDENCE_THRESHOLD = 0.5
YOLO_MODEL = "yolov8n.pt"  # or yolov8s.pt, yolov8m.pt

# Ground Station backend (drone → FastAPI, via gcs_link.py)
# Same laptop as dashboard: default localhost ok
# Real Pi on same Wi-Fi:     GCS_API_URL=http://<laptop-ip>:8000
GCS_API_URL = os.getenv("GCS_API_URL", "http://localhost:8000")
```

---

## Project Structure

```
raspberry-pi-5/
├── main.py              # Main entry point
├── config.py            # Configuration
├── detector.py          # YOLOv8 detector
├── human_detection.py   # Detection wrapper
├── vital_signs.py       # Simulated vital signs
├── packet.py            # JSON packet builder
├── sender.py            # LoRa/WebSocket sender
├── receiver.py          # LoRa/WebSocket receiver
├── logger.py            # CSV/JSON logging
├── dashboard.py         # Flask dashboard (optional)
├── utils.py             # Utilities
├── test_cam.py          # Camera test
├── requirements.txt     # Python dependencies
├── yolov8n.pt           # YOLOv8 Nano weights
├── detections/          # Auto-saved detection screenshots
└── README.md            # This file
```

---

## Performance Tuning for Pi 5

### Using YOLOv8s (Small) - Better Accuracy

```bash
# Download YOLOv8s weights
wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8s.pt

# Update config.py
YOLO_MODEL = "yolov8s.pt"
```

### Using YOLOv8m (Medium) - Best Accuracy

```bash
# Download YOLOv8m weights
wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8m.pt

# Update config.py
YOLO_MODEL = "yolov8m.pt"

# Expected FPS: 8-12 on Pi 5
```

### Enable Hardware Acceleration

```bash
# Install OpenCV with GStreamer support
sudo apt install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev

# Reinstall OpenCV
pip install opencv-python-headless --no-cache-dir
```

---

## Testing

### Test Camera

```bash
# Quick camera test
python test_cam.py

# Should show preview window, press 'q' to quit
```

### Test Detection Only

```bash
# Run without sending to backend
python main.py
```

---

## Sending Data to Dashboard

### WebSocket Method (Recommended)

```python
# In sender.py
import websocket
import json

def send_detection(data):
    ws = websocket.WebSocket()
    ws.connect("ws://192.168.1.100:8000/ws")
    ws.send(json.dumps(data))
    ws.close()

def send_telemetry(data):
    ws = websocket.WebSocket()
    ws.connect("ws://192.168.1.100:8000/ws")
    ws.send(json.dumps(data))
    ws.close()
```

### REST API Method

```python
import requests

def send_detection(data):
    response = requests.post(
        "http://192.168.1.100:8000/api/detection",
        json=data
    )
    return response.json()
```

---

## Network Setup

### Static IP on Raspberry Pi 5

```bash
# Edit dhcpcd.conf
sudo nano /etc/dhcpcd.conf

# Add at the bottom:
interface wlan0
    static ip_address=192.168.1.100/24
    static routers=192.168.1.1
    static domain_name_servers=192.168.1.1

# Restart networking
sudo systemctl restart dhcpcd
```

### Find GCS IP Address

On Ground Control Station (Windows):

```powershell
# Open Command Prompt
ipconfig

# Look for IPv4 Address under Wi-Fi adapter
# Example: 192.168.1.50
```

---

## Troubleshooting

### Camera Not Detected

```bash
# Check USB
lsusb

# Check video devices
ls -la /dev/video*

# Test with VLC
cvlc v4l2:///dev/video0
```

### YOLOv8 Download Failed

```bash
# Manually download weights
wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt

# Place in project folder
mv yolov8n.pt .
```

### WebSocket Connection Failed

```bash
# Test connection manually
pip install websocket-client

python -c "
import websocket
ws = websocket.create_connection('ws://192.168.1.100:8000/ws')
ws.send('test')
print(ws.recv())
ws.close()
"

# Check firewall
sudo ufw status
sudo ufw allow 8000
```

### Memory Issues

```bash
# Check memory
free -h

# Clear memory
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches

# Monitor
htop
```

### Thermal Throttling

```bash
# Check temperature
vcgencmd measure_temp

# If > 80°C, add active cooler
# Pi 5 has built-in temperature monitoring
```

---

## Production Deployment

### Auto-start on Boot

```bash
# Create service
sudo nano /etc/systemd/system/aeris.service

# Add:
[Unit]
Description=AERIS Detection Service (RPi 5)
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/AERIS/raspberry-pi-5
ExecStart=/home/pi/AERIS/raspberry-pi-5/venv/bin/python main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target

# Enable service
sudo systemctl enable aeris.service

# Start service
sudo systemctl start aeris.service

# Check status
sudo systemctl status aeris.service
```

---

## Security

### Change Default Password

```bash
passwd
```

### Disable Password SSH

```bash
# Generate SSH key on GCS
ssh-keygen -t rsa
ssh-copy-id pi@aeris-pi5.local

# Disable password authentication
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd
```

---

## Support

For issues, check:
1. Camera connection
2. Network connectivity (ping test)
3. Python dependencies installed
4. YOLOv8 model downloaded
5. WebSocket port not blocked
6. SD card speed class (use A2 or higher for better performance)
