#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Volume Be Gone v3.0 - Módulo de Monitoreo de Audio

Gestiona la captura y análisis del nivel de audio ambiente.

Author: Francisco Ortiz Rojas
License: MIT
"""

import numpy as np
import sounddevice as sd
import threading
import time
from typing import Callable, Optional, List
from .config import config


class AudioMonitor:
    """
    Monitor de nivel de audio ambiente.

    Captura audio desde el micrófono USB y calcula el nivel en dB.
    Notifica cuando se supera el umbral configurado.
    """

    def __init__(self):
        self.config = config
        self.running = False
        self.stream: Optional[sd.InputStream] = None

        # Historial para promedio
        self.db_history: List[float] = []
        self.history_size = 10

        # Último nivel calculado
        self.current_db: float = 0.0
        self._db_lock = threading.Lock()

        # Callbacks
        self._on_threshold_exceeded: Optional[Callable[[float], None]] = None
        self._on_level_update: Optional[Callable[[float], None]] = None

        # Información del dispositivo
        self.input_device: Optional[dict] = None

    def check_microphone(self) -> bool:
        """
        Verifica que hay un micrófono disponible.

        Returns:
            bool: True si se detectó micrófono
        """
        try:
            devices = sd.query_devices()
            self.input_device = sd.query_devices(kind='input')
            print(f"[Audio] Micrófono detectado: {self.input_device['name']}")
            return True
        except Exception as e:
            print(f"[Audio] Error: No se detectó micrófono: {e}")
            return False

    def get_device_info(self) -> Optional[dict]:
        """Obtiene información del dispositivo de entrada"""
        return self.input_device

    def calculate_db(self, audio_data: np.ndarray) -> float:
        """
        Calcula el nivel de dB del audio.

        Args:
            audio_data: Array de muestras de audio

        Returns:
            float: Nivel en dB
        """
        # Eliminar valores cero
        audio_data = audio_data[audio_data != 0]
        if len(audio_data) == 0:
            return -np.inf

        # Calcular RMS
        rms = np.sqrt(np.mean(audio_data**2))

        # Convertir a dB
        if rms > 0:
            db = 20 * np.log10(rms) + self.config.audio.calibration_offset
        else:
            db = -np.inf

        return db

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback del stream de audio"""
        if status and status != 'input overflow':
            print(f"[Audio] Status: {status}")

        if self.config.config_mode:
            return

        # Calcular nivel
        db_level = self.calculate_db(indata.flatten())

        if db_level > -np.inf:
            # Actualizar historial
            self.db_history.append(db_level)
            if len(self.db_history) > self.history_size:
                self.db_history.pop(0)

            # Calcular promedio
            avg_db = np.mean(self.db_history)

            with self._db_lock:
                self.current_db = avg_db

            # Notificar actualización
            if self._on_level_update:
                self._on_level_update(avg_db)

            # Verificar umbral
            if avg_db > self.config.audio.threshold_db:
                if self._on_threshold_exceeded:
                    self._on_threshold_exceeded(avg_db)

    def start(self) -> bool:
        """
        Inicia el monitoreo de audio.

        Returns:
            bool: True si se inició correctamente
        """
        if self.running:
            return True

        if not self.check_microphone():
            return False

        try:
            self.stream = sd.InputStream(
                callback=self._audio_callback,
                channels=1,
                samplerate=self.config.audio.sample_rate,
                blocksize=self.config.audio.chunk_size
            )
            self.stream.start()
            self.running = True
            print("[Audio] Monitoreo iniciado")
            return True

        except Exception as e:
            print(f"[Audio] Error iniciando stream: {e}")
            return False

    def stop(self):
        """Detiene el monitoreo de audio"""
        self.running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        print("[Audio] Monitoreo detenido")

    def get_current_level(self) -> float:
        """
        Obtiene el nivel actual de dB.

        Returns:
            float: Nivel actual en dB
        """
        with self._db_lock:
            return self.current_db

    def on_threshold_exceeded(self, callback: Callable[[float], None]):
        """
        Registra callback para cuando se supera el umbral.

        Args:
            callback: Función que recibe el nivel en dB
        """
        self._on_threshold_exceeded = callback

    def on_level_update(self, callback: Callable[[float], None]):
        """
        Registra callback para actualizaciones de nivel.

        Args:
            callback: Función que recibe el nivel en dB
        """
        self._on_level_update = callback

    def get_status(self) -> dict:
        """
        Obtiene el estado actual del monitor.

        Returns:
            dict: Estado del monitor
        """
        return {
            'running': self.running,
            'current_db': self.get_current_level(),
            'threshold_db': self.config.audio.threshold_db,
            'device': self.input_device['name'] if self.input_device else None
        }
