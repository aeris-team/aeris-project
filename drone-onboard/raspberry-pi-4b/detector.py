"""
detector.py  (v6) - Raspberry Pi 4 Model B
-------------------------------------------
YOLOv8n Human Detector

Optimized for:
    - Raspberry Pi 4 Model B (CPU-only, Broadcom BCM2711)
    - USB camera input
    - Real-time person detection on the Pi 4B

Contract with main.py:
    main.py guarantees that every frame arriving here is a clean,
    validated HxWx3 BGR uint8 array (post decode_frame() +
    is_frame_degenerate() guard).  This file's only job is to run
    YOLO inference and draw boxes.
"""

import cv2
import numpy as np
from ultralytics import YOLO


class HumanDetector:

    # COCO class 0 = person
    PERSON_CLASS_ID = 0

    def __init__(self, model_path: str = "yolov8n.pt",
                 confidence_threshold: float = 0.3):
        print(f"[HumanDetector] Loading model '{model_path}'...")
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self._first_frame = True
        print("[HumanDetector] Model loaded successfully.")

    # ─────────────────────────────────────────────────────────────────────
    # INTERNAL
    # ─────────────────────────────────────────────────────────────────────

    def _validate_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Lightweight sanity check.  main.py handles all heavy normalisation;
        this just guards against None or wrong dtype so failures are clear.
        """
        if frame is None:
            raise ValueError("[HumanDetector] detect() received None frame.")

        if frame.dtype != np.uint8:
            frame = np.clip(frame, 0, 255).astype(np.uint8)

        if frame.ndim != 3 or frame.shape[2] != 3:
            raise ValueError(
                f"[HumanDetector] Expected HxWx3 uint8, "
                f"got shape={frame.shape} dtype={frame.dtype}"
            )

        return frame

    # ─────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────

    def detect(self, frame: np.ndarray):
        """
        Run person detection on `frame`.

        Parameters
        ----------
        frame : ndarray
            Clean HxWx3 BGR uint8 image from main.py.

        Returns
        -------
        annotated : ndarray
            BGR frame at original resolution with bounding boxes drawn.
        detections : list[dict]
            [{"confidence": float, "bbox": (x1, y1, x2, y2)}, ...]
        """
        frame = self._validate_frame(frame)

        if self._first_frame:
            h, w, c = frame.shape
            print(f"[HumanDetector] First real frame — shape=({h},{w},{c}), "
                  f"dtype={frame.dtype}")
            self._first_frame = False

        orig_h, orig_w = frame.shape[:2]

        # ── Downscale for fast CPU inference ──────────────────────────────
        infer_w = 320
        scale   = infer_w / orig_w
        infer_h = int(orig_h * scale)
        small   = cv2.resize(frame, (infer_w, infer_h),
                             interpolation=cv2.INTER_LINEAR)

        # ── YOLO inference ────────────────────────────────────────────────
        results = self.model.predict(
            source=small,
            classes=[self.PERSON_CLASS_ID],
            conf=self.confidence_threshold,
            imgsz=320,
            verbose=False,
        )

        detections = []
        annotated  = frame.copy()

        for box in results[0].boxes:
            confidence = float(box.conf[0])

            # Coords in downscaled space
            x1s, y1s, x2s, y2s = map(int, box.xyxy[0])

            # Scale back to original resolution
            x1 = max(0, min(int(x1s / scale), orig_w - 1))
            y1 = max(0, min(int(y1s / scale), orig_h - 1))
            x2 = max(0, min(int(x2s / scale), orig_w - 1))
            y2 = max(0, min(int(y2s / scale), orig_h - 1))

            # Skip degenerate boxes at frame edges after rounding
            if x2 <= x1 or y2 <= y1:
                continue

            detections.append({"confidence": confidence,
                                "bbox": (x1, y1, x2, y2)})

            # Bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Label
            label   = f"Person {confidence * 100:.0f}%"
            label_y = max(20, y1 - 10)
            cv2.putText(
                annotated, label,
                (x1, label_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2,
                cv2.LINE_AA,
            )

        return annotated, detections
