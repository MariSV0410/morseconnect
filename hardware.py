"""Puente USB-serial entre Flask (PC) y Raspberry Pi Pico W (MicroPython)."""
import os, json, threading, time

class HardwareController:
    def __init__(self, on_morse_input=None):
        self.on_morse_input = on_morse_input
        self.enabled = False
        self.error = None
        self.mode = os.getenv("HARDWARE_MODE", "simulation").lower()
        self.serial = None
        self.lock = threading.Lock()
        self.reader = None
        if self.mode == "pico":
            try:
                import serial
                port = os.getenv("SERIAL_PORT", "COM3")
                baud = int(os.getenv("SERIAL_BAUD", "115200"))
                self.serial = serial.Serial(port, baud, timeout=0.2)
                time.sleep(2)
                self.enabled = True
                self.reader = threading.Thread(target=self._read_loop, daemon=True)
                self.reader.start()
            except Exception as exc:
                self.error = f"No se pudo abrir el puerto serial: {exc}"
        elif self.mode != "simulation":
            self.error = "Modo no reconocido. Usa HARDWARE_MODE=simulation o pico."

    def _read_loop(self):
        while self.enabled and self.serial:
            try:
                line = self.serial.readline().decode("utf-8", "ignore").strip()
                if not line:
                    continue
                data = json.loads(line)
                if data.get("event") == "morse" and self.on_morse_input:
                    self.on_morse_input(data.get("code", ""))
            except Exception:
                # Ignora líneas de arranque/REPL que no sean JSON.
                continue

    def play_morse(self, code):
        if not self.enabled or not self.serial:
            raise RuntimeError("Hardware no conectado. Revisa el modo Pico W y el puerto USB.")
        with self.lock:
            payload = json.dumps({"cmd": "play", "morse": code}) + "\n"
            self.serial.write(payload.encode())

    def close(self):
        self.enabled = False
        try:
            if self.serial:
                self.serial.close()
        except Exception:
            pass
