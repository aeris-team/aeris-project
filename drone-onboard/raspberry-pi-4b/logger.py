"""
logger.py  (v5) - Raspberry Pi 4 Model B
----------------------------------------
Detection event logger.

Saves:
    1. Detection events to CSV   — detections.csv
       (columns: timestamp, confidence, frame_number)
    2. Detection history to JSON — detections.json
       (same fields, structured for future dashboard use)
    3. Detection screenshots     — detections/<timestamp>.jpg
       (the annotated frame at the moment of detection)

Changes in v5:
    - No logic changes; version label updated to match main.py / detector.py.
"""

import os
import csv
import json
from datetime import datetime

import cv2


class DetectionLogger:

    def __init__(
        self,
        csv_path:       str = "detections.csv",
        json_path:      str = "detections.json",
        screenshot_dir: str = "detections",
    ):
        self.csv_path       = csv_path
        self.json_path      = json_path
        self.screenshot_dir = screenshot_dir

        os.makedirs(self.screenshot_dir, exist_ok=True)

        self.all_detections: list[dict] = []
        self._init_csv()
        self._init_json()

    # ─────────────────────────────────────────────────────────────────────
    # INITIALISATION
    # ─────────────────────────────────────────────────────────────────────

    def _init_csv(self):
        """Create CSV with header row if it does not already exist."""
        if not os.path.exists(self.csv_path):
            try:
                with open(self.csv_path, "w", newline="",
                          encoding="utf-8") as f:
                    csv.writer(f).writerow(
                        ["timestamp", "confidence", "frame_number"]
                    )
            except OSError as e:
                print(f"[Logger] Could not create CSV: {e}")

    def _init_json(self):
        """Load existing JSON log if present; otherwise create an empty one."""
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.all_detections = data if isinstance(data, list) else []
            except (json.JSONDecodeError, OSError):
                print("[Logger] Could not parse existing JSON — starting fresh.")
                self.all_detections = []
        else:
            try:
                with open(self.json_path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)
            except OSError as e:
                print(f"[Logger] Could not create JSON log: {e}")

    # ─────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────

    def log_detection(
        self,
        confidence:   float,
        frame_number: int,
        frame_image:  "np.ndarray | None" = None,
    ) -> dict:
        """
        Record one detection event.

        Parameters
        ----------
        confidence   : YOLO confidence score (0–1)
        frame_number : current frame index from the main loop
        frame_image  : annotated BGR frame to save as screenshot (optional)

        Returns
        -------
        record : dict — {"timestamp", "confidence", "frame_number"}
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ── CSV ────────────────────────────────────────────────────────────
        try:
            with open(self.csv_path, "a", newline="",
                      encoding="utf-8") as f:
                csv.writer(f).writerow(
                    [timestamp, round(confidence, 2), frame_number]
                )
        except OSError as e:
            print(f"[Logger] CSV write failed: {e}")

        # ── JSON ───────────────────────────────────────────────────────────
        record = {
            "timestamp":    timestamp,
            "confidence":   round(confidence, 2),
            "frame_number": frame_number,
        }
        self.all_detections.append(record)
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self.all_detections, f, indent=4,
                          ensure_ascii=False)
        except OSError as e:
            print(f"[Logger] JSON write failed: {e}")

        # ── Screenshot ─────────────────────────────────────────────────────
        if frame_image is not None:
            ts_ms    = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
            filename = f"person_{ts_ms}.jpg"
            path     = os.path.join(self.screenshot_dir, filename)
            try:
                ok = cv2.imwrite(path, frame_image)
                if ok:
                    print(f"[Logger] Screenshot saved → {path}")
                else:
                    print(f"[Logger] cv2.imwrite returned False for {path}")
            except Exception as e:
                print(f"[Logger] Screenshot save failed: {e}")

        return record
