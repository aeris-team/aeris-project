"""
receiver.py - Simulated LoRa Receiver (Raspberry Pi 5)

Listens for UDP packets simulating the LoRa downlink on the ground station.
Stores received packets in a thread-safe buffer that the dashboard reads.

Designed so that swapping to real LoRa hardware (e.g. SX1278 via SPI on a
Raspberry Pi 5) only requires replacing the socket layer while keeping the
packet storage and dashboard interface identical.
"""

import socket
import json
import threading
import logging
from utils import LORA_HOST, LORA_PORT, timestamp_short

logger = logging.getLogger(__name__)


class LoRaReceiver:
    """Simulated LoRa receiver — UDP socket with thread-safe packet store."""

    def __init__(self, host: str = LORA_HOST, port: int = LORA_PORT):
        self.host = host
        self.port = port
        self._sock: socket.socket | None = None
        self._running = False
        self._thread: threading.Thread | None = None

        # Thread-safe storage
        self._lock = threading.Lock()
        self._packets: list[dict] = []
        self._latest_packet: dict | None = None
        self._packet_count = 0
        self._logs: list[str] = []

    # ── Internal ─────────────────────────────────────────────────────────

    def _log(self, message: str):
        entry = f"[{timestamp_short()}] {message}"
        self._logs.append(entry)
        if len(self._logs) > 300:
            self._logs.pop(0)

    def _listen_loop(self):
        self._log("Receiver started — listening for packets")
        while self._running:
            try:
                data, addr = self._sock.recvfrom(65535)
                if not data:
                    continue

                packet = json.loads(data.decode("utf-8"))
                pkt_id = packet.get("packet_id", "?")

                detected = bool(
                    packet.get("detection", {}).get("person_detected", False)
                )
                confidence = packet.get("detection", {}).get("confidence", 0)
                status = (
                    f"DETECTED ({confidence*100:.0f}%)"
                    if detected else "NO TARGET"
                )

                with self._lock:
                    self._packets.append(packet)
                    self._latest_packet = packet
                    self._packet_count += 1

                self._log(
                    f"Packet #{pkt_id} | {status} | "
                    f"{addr[0]}:{addr[1]} | "
                    f"{len(data)} bytes"
                )

            except socket.timeout:
                continue
            except json.JSONDecodeError:
                self._log("WARN: Received malformed packet (invalid JSON)")
                continue
            except OSError as e:
                if self._running:
                    self._log(f"ERROR: Socket error — {e}")
                break

        self._log("Receiver stopped")

    # ── Lifecycle ────────────────────────────────────────────────────────

    def open(self) -> bool:
        """Bind the UDP socket."""
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.bind((self.host, self.port))
            self._sock.settimeout(0.5)
            self._log(f"Socket bound to {self.host}:{self.port}")
            logger.info("[LoRaReceiver] Bound to %s:%s", self.host, self.port)
            return True
        except OSError as e:
            logger.error("[LoRaReceiver] Bind failed: %s", e)
            self._log(f"ERROR: Bind failed — {e}")
            return False

    def start(self):
        """Start the receiver background thread."""
        if self._running:
            return
        if self._sock is None:
            if not self.open():
                return
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the receiver and clean up."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
        self._log("Receiver shut down")

    # ─── Public read interface (thread-safe) ────────────────────────────

    @property
    def packet_count(self) -> int:
        with self._lock:
            return self._packet_count

    @property
    def latest_packet(self) -> dict | None:
        with self._lock:
            return self._latest_packet

    @property
    def all_packets(self) -> list[dict]:
        with self._lock:
            return list(self._packets)

    @property
    def logs(self) -> list[str]:
        return list(self._logs)

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def connection_status(self) -> str:
        return "Connected" if self._running else "Disconnected"
