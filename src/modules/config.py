#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Volume Be Gone v3.0 - Módulo de Configuración

Gestiona toda la configuración del sistema de forma centralizada.

Author: Francisco Ortiz Rojas
License: MIT
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import threading


@dataclass
class AttackConfig:
    """Configuración de ataques Bluetooth"""
    # L2CAP Ping parameters
    l2ping_threads_per_device: int = 20
    l2ping_package_sizes: List[int] = field(default_factory=lambda: [600, 800])
    l2ping_timeout: int = 1

    # RFCOMM parameters
    rfcomm_max_channels: int = 30
    rfcomm_connections_per_channel: int = 8

    # A2DP/AVDTP parameters
    a2dp_stream_attacks: bool = True
    avdtp_malformed_packets: bool = True

    # SDP enumeration
    sdp_enumerate_before_attack: bool = True
    sdp_timeout: int = 1

    # Filtering
    max_simultaneous_attacks: int = 1
    attack_only_audio_devices: bool = True
    exclude_ble_from_classic_attacks: bool = True
    attack_delay_between_devices: int = 3


@dataclass
class AudioConfig:
    """Configuración de audio"""
    sample_rate: int = 44100
    chunk_size: int = 4096
    calibration_offset: int = 94
    threshold_db: int = 73
    min_threshold_db: int = 70
    max_threshold_db: int = 120


@dataclass
class BluetoothConfig:
    """Configuración de Bluetooth"""
    bt_interface: str = "hci1"
    use_external_adapter: bool = True
    scan_duration: int = 8
    quick_scan_duration: int = 2
    ble_scan_duration: int = 5


@dataclass
class DisplayConfig:
    """Configuración de pantalla OLED"""
    i2c_port: int = 1
    i2c_address: int = 0x3C
    width: int = 128
    height: int = 64
    font_path: str = "whitrabt.ttf"


@dataclass
class EncoderConfig:
    """Configuración del encoder rotativo"""
    clk_pin: int = 19  # GPIO19 - Pin 35
    dt_pin: int = 13   # GPIO13 - Pin 33
    sw_pin: int = 26   # GPIO26 - Pin 37
    fast_rotation_threshold: float = 0.05


@dataclass
class WebConfig:
    """Configuración del servidor web"""
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 80
    ap_ssid: str = "VolumeBeGone"
    ap_password: str = "volumebegone123"
    ap_channel: int = 6
    ap_ip: str = "192.168.4.1"


@dataclass
class ESP32Config:
    """Configuración del ESP32"""
    enabled: bool = True
    port: str = "/dev/ttyUSB0"
    baudrate: int = 115200
    timeout: float = 1.0


class Config:
    """
    Gestor de configuración centralizada para Volume Be Gone.

    Singleton que mantiene toda la configuración del sistema.
    Thread-safe para acceso concurrente.
    """

    _instance = None
    _lock = threading.Lock()

    # Keywords para identificar dispositivos de audio
    AUDIO_DEVICE_KEYWORDS = [
        # Palabras generales de audio
        'speaker', 'parlante', 'altavoz', 'soundbar', 'sound bar', 'audio',
        'boom', 'blast', 'play', 'music', 'wireless speaker', 'bluetooth speaker',

        # Marcas premium de audio
        'jbl', 'bose', 'sony', 'samsung', 'lg', 'philips', 'marshall',
        'harman', 'kardon', 'harman/kardon', 'beats', 'dr. beats', 'dre',
        'klipsch', 'yamaha', 'pioneer', 'denon', 'onkyo', 'marantz',

        # Marcas populares
        'anker', 'soundcore', 'ultimate ears', 'ue', 'tribit', 'doss',
        'oontz', 'wonderboom', 'megaboom', 'hyperboom', 'soundlink',
        'flip', 'charge', 'xtreme', 'pulse', 'go', 'clip', 'mini',

        # Marcas chinas comunes
        'xiaomi', 'mi speaker', 'redmi', 'huawei', 'honor', 'oppo',
        'realme', 'oneplus', 'vivo', 'tecno', 'infinix', 'itel',
        'tronsmart', 'bluedio', 'zealot', 'w-king', 'mifa', 'ggmm',
        'edifier', 'creative', 'musky', 'sanag', 'hopestar', 'toproad',

        # Nombres genéricos de parlantes chinos
        'bt speaker', 'bt-speaker', 'wireless', 'portable speaker',
        'mini speaker', 'outdoor speaker', 'waterproof speaker',
        'astronaut', 'robot', 'alien', 'spaceman',

        # Soundbars y home theater
        'soundbar', 'sound bar', 'home theater', 'tv speaker', 'subwoofer',
        'surround', '5.1', '7.1', 'dolby', 'atmos',

        # Smart speakers
        'alexa', 'echo', 'google home', 'nest audio', 'homepod', 'siri',

        # Modelos específicos
        'flip3', 'flip4', 'flip5', 'flip6', 'charge3', 'charge4', 'charge5',
        'xtreme2', 'xtreme3', 'pulse4', 'pulse5', 'boombox', 'partybox',
        'soundlink mini', 'soundlink color', 'soundlink revolve',
        'srs-xb', 'extra bass', 'megaboom 3', 'wonderboom 2',
    ]

    # Clases de dispositivos Bluetooth que son de audio
    AUDIO_DEVICE_CLASSES = [
        0x240400,  # Loudspeaker
        0x240404,  # Wearable Headset Device
        0x240408,  # Hands-free Device
        0x24040C,  # Microphone
        0x240410,  # Loudspeaker
        0x240414,  # Headphones
        0x240418,  # Portable Audio
        0x24041C,  # Car Audio
        0x240420,  # Set-top box
        0x240424,  # HiFi Audio Device
        0x240428,  # VCR
        0x24042C,  # Video Camera
    ]

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Detectar rutas
        self.script_dir = Path(__file__).parent.parent.parent.resolve()
        self.config_dir = self.script_dir / "config"
        self.config_path = self.config_dir / "settings.json"
        self.log_path = self.script_dir / "log.txt"

        # Crear directorio de config si no existe
        self.config_dir.mkdir(exist_ok=True)

        # Inicializar configuraciones
        self.attack = AttackConfig()
        self.audio = AudioConfig()
        self.bluetooth = BluetoothConfig()
        self.display = DisplayConfig()
        self.encoder = EncoderConfig()
        self.web = WebConfig()
        self.esp32 = ESP32Config()

        # Caché de dispositivos conocidos
        self.known_devices: Dict[str, Dict] = {}

        # Estado del sistema
        self.config_mode: bool = True
        self.monitoring: bool = False
        self.scanning: bool = False

        # Cargar configuración guardada
        self.load()

        self._initialized = True

    def load(self) -> bool:
        """Carga la configuración desde el archivo JSON"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    data = json.load(f)

                # Cargar configuración de audio
                if 'audio' in data:
                    for key, value in data['audio'].items():
                        if hasattr(self.audio, key):
                            setattr(self.audio, key, value)

                # Cargar configuración de bluetooth
                if 'bluetooth' in data:
                    for key, value in data['bluetooth'].items():
                        if hasattr(self.bluetooth, key):
                            setattr(self.bluetooth, key, value)

                # Cargar configuración de ataques
                if 'attack' in data:
                    for key, value in data['attack'].items():
                        if hasattr(self.attack, key):
                            setattr(self.attack, key, value)

                # Cargar configuración web
                if 'web' in data:
                    for key, value in data['web'].items():
                        if hasattr(self.web, key):
                            setattr(self.web, key, value)

                # Cargar configuración ESP32
                if 'esp32' in data:
                    for key, value in data['esp32'].items():
                        if hasattr(self.esp32, key):
                            setattr(self.esp32, key, value)

                # Cargar dispositivos conocidos
                self.known_devices = data.get('known_devices', {})

                print(f"[Config] Configuración cargada: Umbral={self.audio.threshold_db}dB")
                return True
            else:
                print("[Config] Archivo no encontrado, usando valores por defecto")
                return False

        except Exception as e:
            print(f"[Config] Error cargando configuración: {e}")
            return False

    def save(self) -> bool:
        """Guarda la configuración actual al archivo JSON"""
        try:
            data = {
                'audio': asdict(self.audio),
                'bluetooth': asdict(self.bluetooth),
                'attack': asdict(self.attack),
                'web': asdict(self.web),
                'esp32': asdict(self.esp32),
                'known_devices': self.known_devices
            }

            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"[Config] Configuración guardada")
            return True

        except Exception as e:
            print(f"[Config] Error guardando configuración: {e}")
            return False

    def get_threshold(self) -> int:
        """Obtiene el umbral actual de dB"""
        return self.audio.threshold_db

    def set_threshold(self, value: int) -> None:
        """Establece el umbral de dB"""
        self.audio.threshold_db = max(
            self.audio.min_threshold_db,
            min(value, self.audio.max_threshold_db)
        )

    def add_known_device(self, addr: str, device_info: Dict) -> None:
        """Agrega un dispositivo conocido al caché"""
        with self._lock:
            self.known_devices[addr] = device_info

    def get_known_devices(self) -> Dict[str, Dict]:
        """Obtiene todos los dispositivos conocidos"""
        with self._lock:
            return self.known_devices.copy()

    def is_audio_device(self, device: Dict) -> bool:
        """
        Determina si un dispositivo es de audio.

        Args:
            device: Diccionario con información del dispositivo

        Returns:
            bool: True si es dispositivo de audio
        """
        # Verificar nombre
        device_name = (device.get('name') or '').lower()
        if device_name:
            for keyword in self.AUDIO_DEVICE_KEYWORDS:
                if keyword.lower() in device_name:
                    return True

        # Verificar clase
        device_class = device.get('class')
        if device_class is not None:
            if device_class in self.AUDIO_DEVICE_CLASSES:
                return True

            # Verificar major device class
            major_class = (device_class >> 8) & 0x1F
            if major_class == 0x04:  # Audio/Video
                return True

        # Verificar servicios SDP
        services = device.get('services', [])
        audio_uuids = ['0000110b', '0000110a', '0000110d', '0000110e', '00001108', '0000111e']

        for service in services:
            service_lower = service.lower()
            for uuid in audio_uuids:
                if uuid in service_lower:
                    return True

        return False

    def to_dict(self) -> Dict[str, Any]:
        """Exporta toda la configuración como diccionario"""
        return {
            'audio': asdict(self.audio),
            'bluetooth': asdict(self.bluetooth),
            'attack': asdict(self.attack),
            'display': asdict(self.display),
            'encoder': asdict(self.encoder),
            'web': asdict(self.web),
            'esp32': asdict(self.esp32),
            'known_devices_count': len(self.known_devices)
        }


# Instancia global (singleton)
config = Config()
