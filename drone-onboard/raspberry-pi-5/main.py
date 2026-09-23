"""
main.py  (v7 — LoRa + Dashboard) - Raspberry Pi 5
=================================================

Full prototype pipeline running on the Raspberry Pi 5:

   USB Camera (OpenCV VideoCapture)
       ↓
   YOLOv8 Human Detection
       ↓
   Estimated Vital Signs (HR, RR, SpO₂, Temp)
       ↓
   Detection Packet (JSON)
       ↓
   Simulated LoRa Transmission (UDP socket)
       ↓
   Ground Station Dashboard (Flask web UI)

Uses a USB camera connected to the Raspberry Pi 5 via OpenCV
VideoCapture.

Device identity and simulated hardware information are loaded from
config.py (DEVICE_NAME, CPU_MODEL, RAM_SIZE, STATUS, LORA_MODE,
CAMERA_NAME, DEVICE_VERSION).
"""

import cv2
import time
import numpy as np
import warnings
import os
import logging
import threading

# ── Suppress noisy logs ─────────────────────────────────────────────────
os.environ["OPENCV_LOG_LEVEL"] = "SILENT"
os.environ["YOLO_VERBOSE"]     = "False"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
logging.getLogger("ultralytics").setLevel(logging.WARNING)
warnings.filterwarnings("ignore")

from config import (
    DEVICE_NAME, DEVICE_VERSION, CPU_MODEL, RAM_SIZE,
    STATUS, LORA_MODE, CAMERA_NAME, GCS_API_URL,
)
from human_detection import HumanDetection
from vital_signs     import VitalSignsEstimator
from packet          import DetectionPacket
from sender          import LoRaSender
from receiver        import LoRaReceiver
from dashboard       import DashboardState, state as dash_state, run_dashboard
from logger          import DetectionLogger
from hardware_simulator import simulator as hw_simulator
from utils           import (
    timestamp_now, timestamp_short,
    LORA_HOST, LORA_PORT,
    LORA_RSSI_RANGE, LORA_SNR_RANGE, LORA_FREQUENCY_MHZ,
    DASHBOARD_HOST, DASHBOARD_PORT,
)

# Shared drone→GCS bridge (works for both pi-4b and pi-5 layouts)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gcs_link import GCSLink  # noqa: E402


# ── Settings ──────────────────────────────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.25
TARGET_CAPTURE_FPS   = 30
DETECT_INTERVAL_SEC  = 0.3
LOG_COOLDOWN_SEC     = 10.0
LORA_TX_INTERVAL     = 1.0        # send at most one packet per second
CAMERA_INDEX         = 0          # USB camera on the Raspberry Pi 5
INIT_WIN_W           = 640
INIT_WIN_H           = 360


# ── Camera helper ─────────────────────────────────────────────────────────
def open_camera(index=CAMERA_INDEX):
    """Open the USB camera connected to the Raspberry Pi 5."""
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(index)
    return cap


# ── HUD helper ────────────────────────────────────────────────────────────
def hud_text(img, text, y, color):
    font      = cv2.FONT_HERSHEY_SIMPLEX
    scale     = 0.65
    thickness = 2
    pad       = 4
    (tw, th), baseline = cv2.getTextSize(text, font, scale, thickness)
    cv2.rectangle(img,
                  (8, y - th - pad),
                  (8 + tw + pad * 2, y + baseline + pad),
                  (0, 0, 0), cv2.FILLED)
    cv2.putText(img, text, (8 + pad, y), font, scale, color, thickness, cv2.LINE_AA)


# ── Rolling FPS counter ───────────────────────────────────────────────────
class RollingFPS:
    def __init__(self, window=20):
        self._window = window
        self._times  = []
    def tick(self):
        now = time.perf_counter()
        self._times.append(now)
        if len(self._times) > self._window:
            self._times.pop(0)
        if len(self._times) < 2:
            return 0.0
        span = self._times[-1] - self._times[0]
        return (len(self._times) - 1) / span if span > 0 else 0.0


# ── Shared state (capture / detection threads) ────────────────────────────
class SharedState:
    def __init__(self):
        self.lock        = threading.Lock()
        self.frame       = None
        self.detections  = []
        self.det_age     = 0.0
        self.stop        = False


def capture_loop(state: SharedState, cap: cv2.VideoCapture, target_fps):
    interval = 1.0 / target_fps
    last     = time.perf_counter()
    while not state.stop:
        now     = time.perf_counter()
        elapsed = now - last
        if elapsed < interval:
            time.sleep(interval - elapsed)
        last = time.perf_counter()

        ret, frame = cap.read()
        if not ret or frame is None:
            continue

        # BGR to RGB for dashboard
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        dash_state.update_frame(frame_rgb)

        with state.lock:
            state.frame = frame


def detect_loop(state: SharedState, human_detector: HumanDetection,
                detect_interval):
    while not state.stop:
        with state.lock:
            frame = None if state.frame is None else state.frame.copy()

        if frame is None:
            time.sleep(0.01)
            continue

        try:
            _, detections = human_detector.detect(frame)
        except Exception:
            detections = []

        with state.lock:
            state.detections = detections
            state.det_age    = time.perf_counter()

        time.sleep(detect_interval)


def draw_detections(img, detections):
    for d in detections:
        bbox = d.get("bbox") or d.get("box") or d.get("xyxy")
        if not bbox:
            continue
        try:
            x1, y1, x2, y2 = [int(v) for v in bbox]
            conf = d.get("confidence", 0.0)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"{conf*100:.0f}%", (x1, max(0, y1 - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
        except Exception:
            continue


# ═════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 55)
    print("  Human Detection → LoRa → Ground Station Dashboard")
    print("  DRRM Prototype Pipeline")
    print("=" * 55)

    # ── Device information (Raspberry Pi 5) ───────────────────────────────
    print("\n[Device] Raspberry Pi 5")
    print(f"  Device   : {DEVICE_NAME}")
    print(f"  CPU      : {CPU_MODEL}")
    print(f"  RAM      : {RAM_SIZE}")
    print(f"  Status   : {STATUS}")
    print(f"  LoRa     : {LORA_MODE}")
    print(f"  Camera   : {CAMERA_NAME}")
    print(f"  Version  : {DEVICE_VERSION}")

    # ── Initialise modules ──────────────────────────────────────────────────
    print("\n[1/8] Loading YOLO model...", end=" ", flush=True)
    human_detector = HumanDetection(confidence_threshold=CONFIDENCE_THRESHOLD)
    print("OK")

    print("[2/8] Initialising vital signs estimator...", end=" ", flush=True)
    vital_estimator = VitalSignsEstimator()
    print("OK")

    print("[3/8] Initialising packet module...", end=" ", flush=True)
    packet_builder = DetectionPacket()
    print("OK")

    print("[4/8] Initialising LoRa sender...", end=" ", flush=True)
    lora_sender = LoRaSender(host=LORA_HOST, port=LORA_PORT)
    print("OK" if lora_sender.is_connected else "FAIL")

    print("[5/8] Initialising LoRa receiver...", end=" ", flush=True)
    lora_receiver = LoRaReceiver(host=LORA_HOST, port=LORA_PORT)
    ok = lora_receiver.open()
    print("OK" if ok else "FAIL")
    if ok:
        lora_receiver.start()
        print("  └─ Receiver listening on UDP {}:{}".format(LORA_HOST, LORA_PORT))

    print("[6/8] Starting Ground Station Dashboard...", end=" ", flush=True)
    dash_thread = threading.Thread(
        target=run_dashboard,
        args=(DASHBOARD_HOST, DASHBOARD_PORT),
        daemon=True,
    )
    dash_thread.start()
    time.sleep(1.0)  # let Flask boot
    print("OK")

    print("[6.5/8] Starting Raspberry Pi 5 hardware simulator...", end=" ", flush=True)
    hw_simulator.start()
    print("OK")

    print("[6.7/8] Connecting to Ground Station backend...", end=" ", flush=True)
    gcs = GCSLink(api_url=GCS_API_URL)
    gcs_ok = gcs.health()
    print(f"OK ({GCS_API_URL})" if gcs_ok else f"RETRY ({GCS_API_URL}) — will keep trying")

    print("[7/8] Opening USB camera...", end=" ", flush=True)
    cap = open_camera(CAMERA_INDEX)
    if not cap.isOpened():
        print("\n[ERROR] Could not open USB camera.")
        return
    cam_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cam_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"OK  ({cam_w}x{cam_h})")

    print("[8/8] Starting capture + detection threads...\n")

    # ── Logger (existing) ──────────────────────────────────────────────────
    logger = DetectionLogger()

    # ── Detection window ────────────────────────────────────────────────────
    WIN = "Human Detection — DRRM Prototype (Raspberry Pi 5)"
    cv2.namedWindow(WIN, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WIN, INIT_WIN_W, INIT_WIN_H)

    print("  Camera  : USB camera (Index 0)")
    print("  Detection window: OpenCV window")
    print("  Dashboard: http://{}:{}".format(
        "localhost", DASHBOARD_PORT
    ))
    print("  Press Q in the detection window to quit.")
    print("  ─" * 28)

    # ── Thread state ───────────────────────────────────────────────────────
    thread_state = SharedState()

    # ── Pipeline tracking ──────────────────────────────────────────────────
    frame_count     = 0
    detection_count = 0
    packet_id       = 0
    last_save_time  = 0.0
    last_tx_time    = 0.0
    last_gcs_det_time = 0.0
    fps_counter     = RollingFPS(window=20)

    # ── Capture thread ─────────────────────────────────────────────────────
    cap_thread = threading.Thread(
        target=capture_loop, args=(thread_state, cap, TARGET_CAPTURE_FPS),
        daemon=True,
    )
    det_thread = threading.Thread(
        target=detect_loop, args=(thread_state, human_detector, DETECT_INTERVAL_SEC),
        daemon=True,
    )
    cap_thread.start()
    det_thread.start()

    dash_state.add_log(f"System initialised — {DEVICE_NAME}")
    dash_state.add_log(f"Dashboard: http://localhost:{DASHBOARD_PORT}")

    # ── Main loop ──────────────────────────────────────────────────────────
    try:
        while True:
            with thread_state.lock:
                frame      = None if thread_state.frame is None else thread_state.frame.copy()
                detections = list(thread_state.detections)

            if frame is None:
                time.sleep(0.005)
                continue

            frame_count += 1

            display = frame
            draw_detections(display, detections)

            fps = fps_counter.tick()
            dash_state.fps = fps

            now = time.perf_counter()
            person_detected = bool(detections)

            # ── Screenshot logging (existing) ──────────────────────────────
            if detections and (now - last_save_time) >= LOG_COOLDOWN_SEC:
                best = max(detections, key=lambda d: d["confidence"])
                logger.log_detection(
                    confidence=best["confidence"],
                    frame_number=frame_count,
                    frame_image=display,
                )
                last_save_time = now
                detection_count += 1
                conf_pct = best["confidence"] * 100
                bar = "█" * int(conf_pct / 10)
                print(f"  [SAVED #{detection_count}] {conf_pct:5.1f}%  {bar:<10}  "
                      f"frame={frame_count}  fps={fps:.1f}")

            # ═══════════════════════════════════════════════════════════════
            # LoRa Pipeline (every LORA_TX_INTERVAL seconds)
            # ═══════════════════════════════════════════════════════════════
            if (now - last_tx_time) >= LORA_TX_INTERVAL:
                # 1. Estimate vital signs
                best_conf = max(d["confidence"] for d in detections) if detections else 0.0
                vitals = vital_estimator.estimate(person_detected, best_conf)

                # 2. Build packet
                best_bbox = None
                if detections:
                    best = max(detections, key=lambda d: d["confidence"])
                    best_bbox = best.get("bbox")

                import random
                packet_id += 1
                rssi = random.uniform(*LORA_RSSI_RANGE)
                snr  = random.uniform(*LORA_SNR_RANGE)

                packet = DetectionPacket.build(
                    packet_id=packet_id,
                    person_detected=person_detected,
                    confidence=best_conf,
                    bbox=best_bbox,
                    vital_signs=vitals,
                    rssi=rssi,
                    snr=snr,
                    frequency_mhz=LORA_FREQUENCY_MHZ,
                )

                # 3. Update dashboard state
                dash_state.update_detection(detections, vitals, packet, packet_id)
                dash_state.lora_status = "Transmitting"

                # 4. Transmit over simulated LoRa
                tx_ok = lora_sender.transmit(packet)
                tx_status = "TX OK" if tx_ok else "TX FAIL"
                dash_state.lora_status = "Connected" if tx_ok else "Error"

                # 5. Drone → GCS backend (telemetry every cycle; detection on person)
                sim_snap = hw_simulator.snapshot()
                gcs.send_telemetry(
                    altitude=packet.get("altitude", 80.0),
                    speed=float(sim_snap.get("speed", 6.0)),
                    heading=float(sim_snap.get("heading", packet_id % 360)),
                    battery=float(sim_snap.get("battery", 85.0)),
                    lat=float(sim_snap.get("lat", 14.2500)),
                    lng=float(sim_snap.get("lng", 120.7300)),
                )
                if person_detected and (now - last_gcs_det_time) >= LOG_COOLDOWN_SEC:
                    gcs.send_detection(
                        confidence=best_conf,
                        lat=float(sim_snap.get("lat", 14.2515)),
                        lng=float(sim_snap.get("lng", 120.7310)),
                        altitude=packet.get("altitude", 90.0),
                    )
                    last_gcs_det_time = now

                status_str = (
                    f"DETECTED" if person_detected else "NO TARGET"
                )
                print(f"  [{tx_status}] Packet #{packet_id} | {status_str} | "
                      f"FPS={fps:.1f} | "
                      + (f"HR={vitals['heart_rate']:.0f} SpO₂={vitals['spo2']:.0f}% "
                         if vitals else ""))
                dash_state.add_log(
                    f"Packet #{packet_id} | {tx_status} | {status_str}"
                )

                last_tx_time = now

            # ── HUD ────────────────────────────────────────────────────────
            now2         = time.perf_counter()
            next_save_in = max(0.0, LOG_COOLDOWN_SEC - (now2 - last_save_time))

            hud_text(display, f"FPS: {fps:.1f}",                   28, (255, 255, 255))
            hud_text(display, f"Pkts: {packet_id}",                58, (100, 200, 255))
            hud_text(display, f"Saves: {detection_count}",         88, (255, 255, 255))

            if person_detected:
                hud_text(display, "DETECTED",                     118, (0, 255, 0))
                if next_save_in > 0:
                    hud_text(display, f"Next save: {next_save_in:.1f}s", 144, (0, 200, 255))
                else:
                    hud_text(display, "Saving...",                144, (0, 255, 255))
            else:
                hud_text(display, "No target",                   118, (160, 160, 160))

            hud_text(display, f"LoRa TX: #{packet_id}",          170, (100, 180, 255))

            cv2.imshow(WIN, np.ascontiguousarray(display))

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("\n  [Q] Shutting down...")
                with thread_state.lock:
                    thread_state.stop = True
                break

    finally:
        with thread_state.lock:
            thread_state.stop = True
        cap_thread.join(timeout=1.0)
        det_thread.join(timeout=1.0)
        lora_receiver.stop()
        lora_sender.close()
        try:
            gcs.close()
        except Exception:
            pass
        hw_simulator.stop()
        cap.release()
        cv2.destroyAllWindows()

        dash_state.add_log("System shut down")

        print(f"\n{'─' * 55}")
        print(f"  Device            : {DEVICE_NAME}")
        print(f"  Frames processed  : {frame_count}")
        print(f"  Screenshots saved : {detection_count}")
        print(f"  Packets sent      : {packet_id}")
        print(f"  Packets received  : {lora_receiver.packet_count}")
        print(f"  Logs → detections.csv / detections.json")
        print(f"  Screenshots → detections/")
        print(f"{'─' * 55}")
        print(f"  Dashboard was at http://localhost:{DASHBOARD_PORT}")
        print(f"{'─' * 55}")


if __name__ == "__main__":
    main()
