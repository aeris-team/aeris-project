"""
vital_signs.py - Simulated Vital Signs Estimation (Raspberry Pi 4 Model B)

Generates realistic human vital signs data when a person is detected.
Uses a smooth random-walk model so values change gradually and naturally.
"""

import random
import time
from utils import VITAL_SIGNS_RANGE


class VitalSignsEstimator:
    """Simulates estimation of human vital signs from visual/thermal data."""

    def __init__(self):
        # Initialise within normal ranges
        self._last_values = {
            "heart_rate":    random.uniform(*VITAL_SIGNS_RANGE["heart_rate"]),
            "respiration":   random.uniform(*VITAL_SIGNS_RANGE["respiration"]),
            "spo2":          random.uniform(*VITAL_SIGNS_RANGE["spo2"]),
            "temperature":   random.uniform(*VITAL_SIGNS_RANGE["temperature"]),
        }
        self._last_update = 0.0

    def estimate(self, person_detected: bool, confidence: float = 1.0) -> dict | None:
        """
        Estimate vital signs based on detection status.

        Parameters
        ----------
        person_detected : bool
            Whether a person is currently detected by YOLO.
        confidence : float
            Detection confidence (0–1). Higher confidence = less noise in estimates.

        Returns
        -------
        dict | None
            {"heart_rate": float, "respiration": float,
             "spo2": float, "temperature": float}
            Returns None when no person is detected.
        """
        if not person_detected:
            self._last_update = 0.0
            return None

        now = time.monotonic()
        if self._last_update == 0.0:
            self._last_update = now
            return self._current_values()

        dt = min(now - self._last_update, 2.0)  # cap dt to avoid jumps
        self._last_update = now

        # Higher confidence → less random noise in estimates
        noise_scale = max(0.3, 1.5 - confidence)

        for key, (lo, hi) in VITAL_SIGNS_RANGE.items():
            current = self._last_values[key]
            # Gradual random walk
            step = random.uniform(-0.6, 0.6) * noise_scale * dt
            new_value = current + step
            # Clamp to valid physiologic range
            self._last_values[key] = max(lo, min(hi, new_value))

        return self._current_values()

    def _current_values(self) -> dict:
        return {
            "heart_rate":  round(self._last_values["heart_rate"], 1),
            "respiration": round(self._last_values["respiration"], 1),
            "spo2":        round(self._last_values["spo2"], 1),
            "temperature": round(self._last_values["temperature"], 1),
        }
