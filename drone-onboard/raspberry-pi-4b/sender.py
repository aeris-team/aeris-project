"""
sender.py - Simulated LoRa Sender (Raspberry Pi 4 Model B)

Transmits detection packets via UDP sockets, simulating a LoRa radio link.
Designed so that replacing the socket with real LoRa hardware (e.g. SX1278
via SPI on a Raspberry Pi 4 Model B) requires minimal changes — just swap the
transport layer while keeping the packet interface identical.
"""

import socket
import json
import time
import random
import logging
from utils import LORA_HOST, LORA_PORT, LORA_RSSI_RANGE, LORA_SNR_RANGE

logger = logging.getLogger(__name__)


class LoRaSender:
    """Simulated LoRa transmitter using UDP as a stand-in for the radio link."""

    def __init__(self, host: str = LORA_HOST, port: int = LORA_PORT):
        self.host = host
        self.port = port
        self._sock: socket.socket | None = None
        self._last_transmission_time = 0.0
        self._packets_sent = 0
        self._open()

    # ── Internal ─────────────────────────────────────────────────────────

    def _open(self):
        """Open a UDP socket for simulated LoRa transmission."""
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sock.settimeout(2.0)
            logger.info("[LoRaSender] Socket opened → %s:%s", self.host, self.port)
        except OSError as e:
            logger.error("[LoRaSender] Failed to open socket: %s", e)
            self._sock = None

    # ── Properties ───────────────────────────────────────────────────────

    @property
    def is_connected(self) -> bool:
        return self._sock is not None

    @property
    def packets_sent(self) -> int:
        return self._packets_sent

    @property
    def last_transmission_time(self) -> float:
        return self._last_transmission_time

    # ── Public API ───────────────────────────────────────────────────────

    def transmit(self, packet: dict) -> bool:
        """
        Transmit a packet over the simulated LoRa link.

        Parameters
        ----------
        packet : dict
            Detection packet (see packet.DetectionPacket.build).

        Returns
        -------
        bool
            True if the packet was sent successfully.
        """
        if self._sock is None:
            logger.warning("[LoRaSender] Socket not available — packet dropped.")
            return False

        try:
            # Simulate LoRa airtime delay (100–350 ms depending on payload)
            payload_len = len(json.dumps(packet))
            delay = random.uniform(0.08, 0.15) + payload_len * 0.00005
            time.sleep(delay)

            data = json.dumps(packet).encode("utf-8")
            self._sock.sendto(data, (self.host, self.port))

            self._packets_sent += 1
            self._last_transmission_time = time.time()

            logger.debug(
                "[LoRaSender] Packet #%s transmitted (%d bytes)",
                packet.get("packet_id", "?"), len(data),
            )
            return True

        except socket.timeout:
            logger.warning("[LoRaSender] Transmission timeout.")
            return False
        except OSError as e:
            logger.error("[LoRaSender] Transmission failed: %s", e)
            return False

    def close(self):
        """Close the socket."""
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
            logger.info("[LoRaSender] Socket closed.")
