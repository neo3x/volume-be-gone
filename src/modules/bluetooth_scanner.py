#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Volume Be Gone v3.0 - Módulo de Escaneo Bluetooth

Gestiona el escaneo de dispositivos Bluetooth Classic y BLE.

Author: Francisco Ortiz Rojas
License: MIT
"""

import os
import subprocess
import threading
import time
import re
from typing import Dict, List, Optional, Callable
import bluetooth
from .config import config


class BluetoothScanner:
    """
    Scanner de dispositivos Bluetooth.

    Soporta escaneo dual (Classic + BLE) y mantiene un caché
    de dispositivos detectados.
    """

    def __init__(self):
        self.config = config
        self.scanning = False
        self.ble_scanning = False

        # Caché de dispositivos
        self.devices_cache: Dict[str, Dict] = {}
        self.ble_devices: Dict[str, Dict] = {}

        # Proceso de captura hcidump
        self.hcidump_process: Optional[subprocess.Popen] = None

        # Callbacks
        self._on_device_found: Optional[Callable[[Dict], None]] = None
        self._on_scan_complete: Optional[Callable[[List[Dict]], None]] = None

        # Lock para acceso thread-safe
        self._lock = threading.Lock()

    def check_adapters(self) -> bool:
        """
        Verifica y configura adaptadores Bluetooth.

        Returns:
            bool: True si hay adaptadores disponibles
        """
        try:
            result = subprocess.run(['hciconfig'], capture_output=True, text=True)
            adapters = []

            for line in result.stdout.split('\n'):
                if line.startswith('hci'):
                    adapter = line.split(':')[0]
                    adapters.append(adapter)

            print(f"[BT] Adaptadores encontrados: {adapters}")

            # Seleccionar adaptador
            if self.config.bluetooth.use_external_adapter and 'hci1' in adapters:
                self.config.bluetooth.bt_interface = "hci1"
                print("[BT] Usando adaptador externo (hci1) - Clase 1")
            else:
                self.config.bluetooth.bt_interface = "hci0"
                print("[BT] Usando adaptador interno (hci0)")

            # Configurar adaptador
            self._configure_adapter()

            return True

        except Exception as e:
            print(f"[BT] Error verificando adaptadores: {e}")
            return False

    def _configure_adapter(self):
        """Configura el adaptador Bluetooth para máximo rendimiento"""
        bt = self.config.bluetooth.bt_interface

        print(f"[BT] Configurando {bt}...")

        # Activar adaptador
        os.system(f"sudo hciconfig {bt} up")

        # Configurar clase de dispositivo
        os.system(f"sudo hciconfig {bt} class 0x000100")

        # Modo master
        os.system(f"sudo hciconfig {bt} lm master")
        os.system(f"sudo hciconfig {bt} lp active,master")

        # TX Power máximo
        os.system(f"sudo hciconfig {bt} inqtpl 4 2>/dev/null")

        # Modo piscan
        os.system(f"sudo hciconfig {bt} piscan")

        # Optimizar scan window
        os.system(f"sudo hcitool -i {bt} cmd 0x08 0x000b 0x00 0x12 0x00 0x12 0x00 0x00 0x00 2>/dev/null")

        print("[BT] Adaptador configurado")

    def scan_with_inquiry(self, quick_mode: bool = False) -> Dict[str, Dict]:
        """
        Escanea usando hcitool inq (más agresivo).

        Args:
            quick_mode: Si True, escaneo de 2 segundos

        Returns:
            Dict con dispositivos encontrados
        """
        bt = self.config.bluetooth.bt_interface
        devices_found = {}

        length = 2 if quick_mode else self.config.bluetooth.scan_duration
        timeout = length + 3

        try:
            result = subprocess.run(
                ['hcitool', '-i', bt, 'inq', f'--length={length}', '--flush'],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            for line in result.stdout.splitlines():
                line = line.strip()
                if not line or line.startswith('Inquiring'):
                    continue

                parts = line.split()
                if len(parts) >= 1:
                    addr = parts[0]
                    if re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', addr):
                        device_class = None
                        for i, part in enumerate(parts):
                            if part == 'class:' and i + 1 < len(parts):
                                try:
                                    device_class = int(parts[i + 1], 16)
                                except ValueError:
                                    pass

                        devices_found[addr] = {
                            'addr': addr,
                            'name': None,
                            'class': device_class,
                            'is_ble': False,
                            'services': []
                        }

            if devices_found:
                print(f"[BT] Inquiry encontró: {len(devices_found)} dispositivos")

        except subprocess.TimeoutExpired:
            print("[BT] Inquiry timeout")
        except Exception as e:
            print(f"[BT] Error en inquiry: {e}")

        return devices_found

    def get_device_name(self, addr: str) -> Optional[str]:
        """Obtiene el nombre de un dispositivo por MAC"""
        bt = self.config.bluetooth.bt_interface
        try:
            result = subprocess.run(
                ['hcitool', '-i', bt, 'name', addr],
                capture_output=True,
                text=True,
                timeout=5
            )
            name = result.stdout.strip()
            if name and name != addr:
                return name
        except:
            pass
        return None

    def scan_ble(self) -> Dict[str, Dict]:
        """
        Escanea dispositivos BLE.

        Returns:
            Dict con dispositivos BLE encontrados
        """
        if self.ble_scanning:
            return {}

        self.ble_scanning = True
        bt = self.config.bluetooth.bt_interface
        new_devices = {}

        print("[BT] Iniciando escaneo BLE...")

        try:
            process = subprocess.Popen(
                ['hcitool', '-i', bt, 'lescan', '--passive', '--duplicates'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )

            start_time = time.time()

            while time.time() - start_time < self.config.bluetooth.ble_scan_duration:
                line = process.stdout.readline()
                if line:
                    parts = line.strip().split(None, 1)
                    if len(parts) >= 1:
                        addr = parts[0]
                        name = parts[1] if len(parts) > 1 and parts[1] != '(unknown)' else None

                        if re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', addr):
                            if addr not in self.devices_cache and addr not in self.ble_devices:
                                device = {
                                    'addr': addr,
                                    'name': name,
                                    'class': None,
                                    'is_ble': True,
                                    'services': []
                                }
                                new_devices[addr] = device
                                self.ble_devices[addr] = device
                                print(f"[BT] BLE: {addr} - {name or 'Sin nombre'}")

            process.terminate()
            process.wait(timeout=2)

            if new_devices:
                print(f"[BT] BLE Scan: +{len(new_devices)} nuevos dispositivos")

        except Exception as e:
            print(f"[BT] Error en BLE scan: {e}")

        self.ble_scanning = False
        return new_devices

    def scan_full(self) -> List[Dict]:
        """
        Escaneo completo dual (Classic + BLE).

        Returns:
            Lista de todos los dispositivos encontrados
        """
        if self.scanning:
            return list(self.devices_cache.values())

        self.scanning = True
        bt = self.config.bluetooth.bt_interface
        new_devices = 0

        print(f"[BT] Escaneo dual usando {bt}...")

        try:
            # Hacer adaptador descubrible
            os.system(f"hciconfig {bt} piscan 2>/dev/null")

            # Método 1: hcitool inq
            print("[BT] Método 1: Inquiry...")
            inq_devices = self.scan_with_inquiry()

            for addr, device in inq_devices.items():
                if addr not in self.devices_cache:
                    name = self.get_device_name(addr)
                    device['name'] = name

                    with self._lock:
                        self.devices_cache[addr] = device
                        self.config.add_known_device(addr, device)

                    new_devices += 1
                    print(f"[BT] INQ: {addr} - {name or 'Sin nombre'}")

                    if self._on_device_found:
                        self._on_device_found(device)

            # Método 2: PyBluez discover
            print("[BT] Método 2: Discovery estándar...")
            try:
                device_id = 1 if bt == "hci1" else 0
                nearby = bluetooth.discover_devices(
                    duration=self.config.bluetooth.scan_duration,
                    lookup_names=True,
                    flush_cache=True,
                    lookup_class=True,
                    device_id=device_id
                )

                for addr, name, device_class in nearby:
                    if addr not in self.devices_cache:
                        device = {
                            'addr': addr,
                            'name': name,
                            'class': device_class,
                            'is_ble': False,
                            'services': []
                        }

                        with self._lock:
                            self.devices_cache[addr] = device
                            self.config.add_known_device(addr, device)

                        new_devices += 1
                        print(f"[BT] Discovery: {addr} - {name}")

                        if self._on_device_found:
                            self._on_device_found(device)

            except Exception as e:
                print(f"[BT] Error en discovery: {e}")

            # Método 3: BLE Scan
            print("[BT] Método 3: BLE Scan...")
            ble_devices = self.scan_ble()

            with self._lock:
                self.devices_cache.update(ble_devices)

            new_devices += len(ble_devices)

            # Guardar configuración
            if new_devices > 0:
                self.config.save()

            print(f"[BT] Nuevos: {new_devices}, Total: {len(self.devices_cache)}")

        except Exception as e:
            print(f"[BT] Error en escaneo: {e}")

        self.scanning = False

        devices = list(self.devices_cache.values())

        if self._on_scan_complete:
            self._on_scan_complete(devices)

        return devices

    def quick_scan(self) -> List[Dict]:
        """
        Escaneo rápido de 2 segundos.

        Returns:
            Lista de dispositivos
        """
        if self.scanning:
            return list(self.devices_cache.values())

        self.scanning = True

        try:
            inq_devices = self.scan_with_inquiry(quick_mode=True)

            for addr, device in inq_devices.items():
                if addr not in self.devices_cache:
                    with self._lock:
                        self.devices_cache[addr] = device
                        self.config.add_known_device(addr, device)

                    if self._on_device_found:
                        self._on_device_found(device)

        except Exception as e:
            pass

        self.scanning = False
        return list(self.devices_cache.values())

    def enumerate_sdp_services(self, addr: str) -> List[int]:
        """
        Enumera servicios SDP y retorna canales RFCOMM.

        Args:
            addr: Dirección MAC del dispositivo

        Returns:
            Lista de canales RFCOMM
        """
        rfcomm_channels = []

        try:
            print(f"[BT] Enumerando SDP de {addr}...")
            result = subprocess.run(
                ['sdptool', 'browse', '--tree', addr],
                capture_output=True,
                text=True,
                timeout=10
            )

            for line in result.stdout.splitlines():
                if 'channel' in line.lower():
                    match = re.search(r'(\d+)', line)
                    if match:
                        channel = int(match.group(1))
                        if 1 <= channel <= 30 and channel not in rfcomm_channels:
                            rfcomm_channels.append(channel)

            if rfcomm_channels:
                print(f"[BT] SDP: {len(rfcomm_channels)} canales RFCOMM")
            else:
                rfcomm_channels = list(range(1, 31))

        except Exception as e:
            rfcomm_channels = list(range(1, 31))

        return rfcomm_channels

    def filter_audio_devices(self, devices: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Filtra solo dispositivos de audio.

        Args:
            devices: Lista de dispositivos (usa caché si None)

        Returns:
            Lista filtrada de dispositivos de audio
        """
        if devices is None:
            devices = list(self.devices_cache.values())

        audio_devices = []

        for device in devices:
            # Filtrar solo audio
            if self.config.attack.attack_only_audio_devices:
                if not self.config.is_audio_device(device):
                    continue

            # Excluir BLE de ataques Classic
            if self.config.attack.exclude_ble_from_classic_attacks:
                if device.get('is_ble', False):
                    continue

            audio_devices.append(device)

        # Ordenar por prioridad
        def priority_score(dev):
            score = 0
            name = (dev.get('name') or '').lower()

            if 'astronaut' in name:
                score += 1000
            if dev.get('name', 'Unknown') != 'Unknown':
                score += 100
            if not dev.get('is_ble', False):
                score += 50
            if dev.get('class') in self.config.AUDIO_DEVICE_CLASSES:
                score += 25

            return score

        audio_devices.sort(key=priority_score, reverse=True)

        return audio_devices[:self.config.attack.max_simultaneous_attacks]

    def get_all_devices(self) -> List[Dict]:
        """Obtiene todos los dispositivos en caché"""
        with self._lock:
            return list(self.devices_cache.values())

    def get_device(self, addr: str) -> Optional[Dict]:
        """Obtiene un dispositivo por MAC"""
        with self._lock:
            return self.devices_cache.get(addr)

    def start_hcidump(self) -> bool:
        """Inicia captura de tráfico Bluetooth"""
        try:
            import datetime
            dump_file = str(self.config.script_dir / f"bt_capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.dump")

            self.hcidump_process = subprocess.Popen(
                ['hcidump', '-i', self.config.bluetooth.bt_interface, '-w', dump_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            print(f"[BT] Captura hcidump iniciada: {dump_file}")
            return True

        except Exception as e:
            print(f"[BT] Error iniciando hcidump: {e}")
            return False

    def stop_hcidump(self):
        """Detiene captura hcidump"""
        if self.hcidump_process:
            try:
                self.hcidump_process.terminate()
                self.hcidump_process.wait(timeout=5)
            except:
                self.hcidump_process.kill()
            self.hcidump_process = None
            print("[BT] Captura hcidump detenida")

    def on_device_found(self, callback: Callable[[Dict], None]):
        """Registra callback para dispositivo encontrado"""
        self._on_device_found = callback

    def on_scan_complete(self, callback: Callable[[List[Dict]], None]):
        """Registra callback para escaneo completado"""
        self._on_scan_complete = callback

    def get_status(self) -> dict:
        """Obtiene estado del scanner"""
        with self._lock:
            classic = sum(1 for d in self.devices_cache.values() if not d.get('is_ble', False))
            ble = sum(1 for d in self.devices_cache.values() if d.get('is_ble', False))
            audio = sum(1 for d in self.devices_cache.values() if self.config.is_audio_device(d))

            return {
                'scanning': self.scanning,
                'ble_scanning': self.ble_scanning,
                'total_devices': len(self.devices_cache),
                'classic_devices': classic,
                'ble_devices': ble,
                'audio_devices': audio,
                'interface': self.config.bluetooth.bt_interface
            }
