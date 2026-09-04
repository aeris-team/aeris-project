"""
human_detection.py - Human Detection Interface (Raspberry Pi 5)

Provides a clean interface wrapping the YOLOv8-based HumanDetector
from detector.py for use in the main pipeline running on the
Raspberry Pi 5.
"""

import numpy as np
from detector import HumanDetector


class HumanDetection:
    """
    Unified detection interface for the main pipeline.

    Delegates to HumanDetector (detector.py) for actual inference,
    and exposes a consistent API for the rest of the system.
    """

    def __init__(self, model_path: str = "yolov8n.pt",
                 confidence_threshold: float = 0.3):
        self._detector = HumanDetector(
            model_path=model_path,
            confidence_threshold=confidence_threshold,
        )

    def detect(self, frame: np.ndarray) -> tuple[np.ndarray, list[dict]]:
        """
        Run person detection on a frame.

        Parameters
        ----------
        frame : np.ndarray
            H×W×3 BGR uint8 image.

        Returns
        -------
        annotated_frame : np.ndarray
            Frame with bounding boxes drawn.
        detections : list[dict]
            [{"confidence": float, "bbox": (x1, y1, x2, y2)}, ...]
        """
        return self._detector.detect(frame)

    @property
    def detector(self) -> HumanDetector:
        return self._detector
