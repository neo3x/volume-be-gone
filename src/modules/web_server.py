#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Volume Be Gone v3.0 - Servidor Web + API

Proporciona interfaz web para control remoto via WiFi Access Point.

Author: Francisco Ortiz Rojas
License: MIT
"""

import os
import json
import threading
import time
from typing import Optional, Callable, Dict, Any
from pathlib import Path

try:
    from flask import Flask, render_template, jsonify, request, send_from_directory
    from flask_socketio import SocketIO, emit
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("[Web] Flask/SocketIO no disponible")

from .config import config


class WebServer:
    """
    Servidor web con API REST y WebSocket.

    Proporciona interfaz de control accesible desde cualquier navegador.
    """

    def __init__(self):
        self.config = config
        self.running = False

        self.app: Optional[Flask] = None
        self.socketio: Optional[SocketIO] = None

        # Referencias a otros módulos (se inyectan después)
        self._audio_monitor = None
        self._bt_scanner = None
        self._attack_engine = None
        self._esp32_controller = None

        # Thread del servidor
        self._server_thread: Optional[threading.Thread] = None

        # Último estado para broadcasting
        self._last_db_level: float = 0.0

    def set_modules(self, audio_monitor=None, bt_scanner=None,
                    attack_engine=None, esp32_controller=None):
        """Inyecta referencias a otros módulos"""
        self._audio_monitor = audio_monitor
        self._bt_scanner = bt_scanner
        self._attack_engine = attack_engine
        self._esp32_controller = esp32_controller

    def initialize(self) -> bool:
        """
        Inicializa el servidor Flask.

        Returns:
            bool: True si se inicializó correctamente
        """
        if not FLASK_AVAILABLE:
            print("[Web] Flask no disponible, servidor web deshabilitado")
            return False

        if not self.config.web.enabled:
            print("[Web] Servidor web deshabilitado en configuración")
            return False

        try:
            # Crear app Flask
            static_folder = str(Path(__file__).parent.parent / 'static')
            self.app = Flask(__name__,
                           static_folder=static_folder,
                           static_url_path='/static')

            self.app.config['SECRET_KEY'] = 'volumebegone-secret-key'

            # Inicializar SocketIO
            self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')

            # Registrar rutas
            self._register_routes()
            self._register_socketio_events()

            print("[Web] Servidor inicializado")
            return True

        except Exception as e:
            print(f"[Web] Error inicializando: {e}")
            return False

    def _register_routes(self):
        """Registra rutas de la API REST"""

        @self.app.route('/')
        def index():
            """Página principal"""
            return send_from_directory(self.app.static_folder, 'index.html')

        @self.app.route('/api/status')
        def api_status():
            """Estado general del sistema"""
            return jsonify(self._get_full_status())

        @self.app.route('/api/config', methods=['GET'])
        def api_get_config():
            """Obtiene configuración actual"""
            return jsonify(self.config.to_dict())

        @self.app.route('/api/threshold', methods=['GET', 'POST'])
        def api_threshold():
            """Obtiene/establece umbral de dB"""
            if request.method == 'POST':
                data = request.get_json()
                if 'value' in data:
                    self.config.set_threshold(int(data['value']))
                    self.config.save()
                    return jsonify({'success': True, 'threshold': self.config.audio.threshold_db})
                return jsonify({'success': False, 'error': 'Missing value'}), 400

            return jsonify({'threshold': self.config.audio.threshold_db})

        @self.app.route('/api/volume')
        def api_volume():
            """Nivel de volumen actual"""
            level = 0.0
            if self._audio_monitor:
                level = self._audio_monitor.get_current_level()
            return jsonify({
                'level': level,
                'threshold': self.config.audio.threshold_db,
                'exceeded': level > self.config.audio.threshold_db
            })

        @self.app.route('/api/devices')
        def api_devices():
            """Lista de dispositivos detectados"""
            devices = []
            if self._bt_scanner:
                devices = self._bt_scanner.get_all_devices()
            return jsonify({
                'devices': devices,
                'count': len(devices)
            })

        @self.app.route('/api/scan', methods=['POST'])
        def api_scan():
            """Inicia escaneo de dispositivos"""
            if self._bt_scanner:
                # Escaneo en background
                thread = threading.Thread(target=self._bt_scanner.scan_full)
                thread.start()
                return jsonify({'success': True, 'message': 'Escaneo iniciado'})
            return jsonify({'success': False, 'error': 'Scanner no disponible'}), 500

        @self.app.route('/api/attack', methods=['POST'])
        def api_attack():
            """Inicia ataque a dispositivo"""
            data = request.get_json()
            addr = data.get('addr')

            if not addr:
                return jsonify({'success': False, 'error': 'Falta dirección MAC'}), 400

            if self._attack_engine and self._bt_scanner:
                device = self._bt_scanner.get_device(addr)
                if device:
                    thread = threading.Thread(
                        target=self._attack_engine.attack_device,
                        args=(device,)
                    )
                    thread.start()
                    return jsonify({'success': True, 'message': f'Atacando {addr}'})
                return jsonify({'success': False, 'error': 'Dispositivo no encontrado'}), 404

            return jsonify({'success': False, 'error': 'Attack engine no disponible'}), 500

        @self.app.route('/api/attack/start', methods=['POST'])
        def api_attack_start():
            """Inicia ataque continuo"""
            if self._attack_engine:
                self._attack_engine.start_continuous_attack()
                return jsonify({'success': True, 'message': 'Ataque continuo iniciado'})
            return jsonify({'success': False, 'error': 'Attack engine no disponible'}), 500

        @self.app.route('/api/attack/stop', methods=['POST'])
        def api_attack_stop():
            """Detiene todos los ataques"""
            if self._attack_engine:
                self._attack_engine.stop_all_attacks()
                return jsonify({'success': True, 'message': 'Ataques detenidos'})
            return jsonify({'success': False, 'error': 'Attack engine no disponible'}), 500

        @self.app.route('/api/esp32/status')
        def api_esp32_status():
            """Estado del ESP32"""
            if self._esp32_controller:
                return jsonify({
                    'connected': self._esp32_controller.connected,
                    'jamming': self._esp32_controller.jamming,
                    'mode': self._esp32_controller.current_mode.value if self._esp32_controller.current_mode else None
                })
            return jsonify({'connected': False, 'error': 'ESP32 no configurado'})

        @self.app.route('/api/esp32/jam', methods=['POST'])
        def api_esp32_jam():
            """Control de jamming ESP32"""
            data = request.get_json()
            action = data.get('action')

            if not self._esp32_controller or not self._esp32_controller.connected:
                return jsonify({'success': False, 'error': 'ESP32 no conectado'}), 500

            if action == 'start':
                mode = data.get('mode', 'BT')
                self._esp32_controller.start_jamming(mode)
                return jsonify({'success': True, 'message': f'Jamming {mode} iniciado'})
            elif action == 'stop':
                self._esp32_controller.stop_jamming()
                return jsonify({'success': True, 'message': 'Jamming detenido'})

            return jsonify({'success': False, 'error': 'Acción inválida'}), 400

    def _register_socketio_events(self):
        """Registra eventos WebSocket"""

        @self.socketio.on('connect')
        def on_connect():
            print(f"[Web] Cliente conectado")
            emit('status', self._get_full_status())

        @self.socketio.on('disconnect')
        def on_disconnect():
            print(f"[Web] Cliente desconectado")

        @self.socketio.on('get_status')
        def on_get_status():
            emit('status', self._get_full_status())

        @self.socketio.on('set_threshold')
        def on_set_threshold(data):
            if 'value' in data:
                self.config.set_threshold(int(data['value']))
                self.config.save()
                self._broadcast_status()

        @self.socketio.on('start_scan')
        def on_start_scan():
            if self._bt_scanner:
                thread = threading.Thread(target=self._do_scan_and_broadcast)
                thread.start()

        @self.socketio.on('start_attack')
        def on_start_attack(data):
            addr = data.get('addr')
            if addr and self._attack_engine and self._bt_scanner:
                device = self._bt_scanner.get_device(addr)
                if device:
                    thread = threading.Thread(
                        target=self._attack_engine.attack_device,
                        args=(device,)
                    )
                    thread.start()

    def _get_full_status(self) -> Dict[str, Any]:
        """Obtiene estado completo del sistema"""
        status = {
            'audio': {
                'level': self._audio_monitor.get_current_level() if self._audio_monitor else 0,
                'threshold': self.config.audio.threshold_db,
                'running': self._audio_monitor.running if self._audio_monitor else False
            },
            'bluetooth': self._bt_scanner.get_status() if self._bt_scanner else {},
            'attack': self._attack_engine.get_status() if self._attack_engine else {},
            'esp32': {
                'connected': self._esp32_controller.connected if self._esp32_controller else False,
                'jamming': self._esp32_controller.jamming if self._esp32_controller else False
            },
            'config_mode': self.config.config_mode,
            'monitoring': self.config.monitoring
        }
        return status

    def _do_scan_and_broadcast(self):
        """Escanea y broadcast resultados"""
        if self._bt_scanner:
            devices = self._bt_scanner.scan_full()
            if self.socketio:
                self.socketio.emit('devices', {'devices': devices})

    def _broadcast_status(self):
        """Broadcast estado a todos los clientes"""
        if self.socketio:
            self.socketio.emit('status', self._get_full_status())

    def broadcast_volume(self, db_level: float):
        """Broadcast nivel de volumen en tiempo real"""
        self._last_db_level = db_level
        if self.socketio:
            self.socketio.emit('volume', {
                'level': db_level,
                'threshold': self.config.audio.threshold_db,
                'exceeded': db_level > self.config.audio.threshold_db
            })

    def broadcast_device_found(self, device: Dict):
        """Broadcast nuevo dispositivo encontrado"""
        if self.socketio:
            self.socketio.emit('device_found', device)

    def start(self):
        """Inicia el servidor web"""
        if not self.app or not self.socketio:
            print("[Web] Servidor no inicializado")
            return

        self.running = True

        def run_server():
            print(f"[Web] Servidor iniciando en {self.config.web.host}:{self.config.web.port}")
            self.socketio.run(
                self.app,
                host=self.config.web.host,
                port=self.config.web.port,
                debug=False,
                use_reloader=False
            )

        self._server_thread = threading.Thread(target=run_server, daemon=True)
        self._server_thread.start()

        print(f"[Web] Servidor corriendo en http://{self.config.web.ap_ip}:{self.config.web.port}")

    def stop(self):
        """Detiene el servidor web"""
        self.running = False
        print("[Web] Servidor detenido")
