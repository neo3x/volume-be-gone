"""
Volume Be Gone v3.0 - Módulos

Sistema modular para control de parlantes Bluetooth.
"""

from .config import Config
from .audio_monitor import AudioMonitor
from .bluetooth_scanner import BluetoothScanner
from .display_manager import DisplayManager
from .attack_engine import AttackEngine
from .esp32_controller import ESP32Controller
from .web_server import WebServer

__all__ = [
    'Config',
    'AudioMonitor',
    'BluetoothScanner',
    'DisplayManager',
    'AttackEngine',
    'ESP32Controller',
    'WebServer'
]

__version__ = '3.0'
__author__ = 'Francisco Ortiz Rojas'
