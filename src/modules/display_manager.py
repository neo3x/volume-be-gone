#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Volume Be Gone v3.0 - Módulo de Display y Encoder

Gestiona la pantalla OLED y el encoder rotativo.

Author: Francisco Ortiz Rojas
License: MIT
"""

import os
import sys
import time
import threading
import subprocess
from typing import Optional, Callable
from PIL import Image, ImageDraw, ImageFont

try:
    from RPi import GPIO
    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False
    print("[Display] Advertencia: RPi/luma no disponible (modo simulación)")

from .config import config


class DisplayManager:
    """
    Gestor de pantalla OLED y encoder rotativo.

    Maneja la interfaz de usuario física del dispositivo.
    """

    def __init__(self):
        self.config = config
        self.running = False

        # Display
        self.disp = None
        self.width = config.display.width
        self.height = config.display.height

        # Fuentes
        self.font = None
        self.font_small = None

        # Encoder state
        self.encoder_last_clk = True
        self.last_encoder_time = 0
        self.button_press_time = 0

        # Callbacks
        self._on_threshold_change: Optional[Callable[[int], None]] = None
        self._on_button_press: Optional[Callable[[], None]] = None
        self._on_button_long_press: Optional[Callable[[], None]] = None

        # Thread control
        self._encoder_thread: Optional[threading.Thread] = None
        self._display_thread: Optional[threading.Thread] = None

        # Display update queue
        self._pending_db_level: float = 0.0
        self._update_needed: bool = False
        self._display_lock = threading.Lock()

    def initialize(self) -> bool:
        """
        Inicializa el display OLED.

        Returns:
            bool: True si se inicializó correctamente
        """
        if not RPI_AVAILABLE:
            print("[Display] Modo simulación (sin hardware)")
            return True

        try:
            serial = i2c(
                port=self.config.display.i2c_port,
                address=self.config.display.i2c_address
            )
            self.disp = ssd1306(serial, width=self.width, height=self.height)
            print("[Display] OLED inicializado")

            # Cargar fuentes
            self._load_fonts()

            return True

        except Exception as e:
            print(f"[Display] Error inicializando OLED: {e}")
            return False

    def _load_fonts(self):
        """Carga las fuentes para el display"""
        font_path = str(self.config.script_dir / self.config.display.font_path)

        try:
            if os.path.exists(font_path):
                self.font = ImageFont.truetype(font_path, 12)
                self.font_small = ImageFont.truetype(font_path, 10)
            else:
                print(f"[Display] Fuente no encontrada, usando default")
                self.font = ImageFont.load_default()
                self.font_small = ImageFont.load_default()
        except Exception as e:
            print(f"[Display] Error cargando fuente: {e}")
            self.font = ImageFont.load_default()
            self.font_small = ImageFont.load_default()

    def setup_encoder(self) -> bool:
        """
        Configura el encoder rotativo.

        Returns:
            bool: True si se configuró correctamente
        """
        if not RPI_AVAILABLE:
            return True

        try:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)

            GPIO.setup(self.config.encoder.clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.config.encoder.dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.config.encoder.sw_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            # Iniciar thread de polling
            self.running = True
            self._encoder_thread = threading.Thread(target=self._encoder_polling, daemon=True)
            self._encoder_thread.start()

            print("[Display] Encoder configurado")
            return True

        except Exception as e:
            print(f"[Display] Error configurando encoder: {e}")
            return False

    def _encoder_polling(self):
        """Thread de polling del encoder"""
        last_clk = GPIO.input(self.config.encoder.clk_pin)
        last_sw = True

        while self.running:
            try:
                clk = GPIO.input(self.config.encoder.clk_pin)
                dt = GPIO.input(self.config.encoder.dt_pin)
                sw = GPIO.input(self.config.encoder.sw_pin)

                # Detectar rotación
                if clk != last_clk and clk == GPIO.LOW:
                    current_time = time.time()
                    time_diff = current_time - self.last_encoder_time

                    if self.config.config_mode:
                        # Velocidad de rotación
                        step = 5 if time_diff < self.config.encoder.fast_rotation_threshold else 1

                        if dt != clk:
                            # Horario - aumentar
                            new_val = min(
                                self.config.audio.threshold_db + step,
                                self.config.audio.max_threshold_db
                            )
                        else:
                            # Antihorario - disminuir
                            new_val = max(
                                self.config.audio.threshold_db - step,
                                self.config.audio.min_threshold_db
                            )

                        if new_val != self.config.audio.threshold_db:
                            self.config.audio.threshold_db = new_val
                            self.show_config_screen()

                            if self._on_threshold_change:
                                self._on_threshold_change(new_val)

                        self.last_encoder_time = current_time

                    last_clk = clk

                # Detectar botón
                if sw != last_sw:
                    if sw == GPIO.LOW:
                        self.button_press_time = time.time()
                    else:
                        if self.button_press_time > 0:
                            duration = time.time() - self.button_press_time

                            if duration < 2:
                                # Presión corta
                                if self._on_button_press:
                                    self._on_button_press()
                            self.button_press_time = 0

                    last_sw = sw

                # Verificar presión larga
                if sw == GPIO.LOW and self.button_press_time > 0:
                    if time.time() - self.button_press_time > 2:
                        if self._on_button_long_press:
                            self._on_button_long_press()
                        self.button_press_time = 0

                time.sleep(0.002)

            except Exception as e:
                print(f"[Display] Error en encoder: {e}")
                time.sleep(0.1)

    def show_boot_screen(self, step: int, total: int, message: str):
        """Muestra pantalla de carga con progreso"""
        if not self.disp:
            print(f"[Boot] {step}/{total}: {message}")
            return

        image = Image.new('1', (self.width, self.height))
        draw = ImageDraw.Draw(image)

        # Título
        draw.text((0, 2), "Volume BeGone", font=self.font, fill=255)
        draw.text((90, 2), "v3.0", font=self.font_small, fill=255)

        # Progreso
        percent = int((step / total) * 100)
        draw.text((0, 18), f"Cargando... {percent}%", font=self.font, fill=255)
        draw.text((0, 32), message[:21], font=self.font_small, fill=255)

        # Barra
        bar_y, bar_h, bar_w = 46, 10, 120
        draw.rectangle((4, bar_y, 4 + bar_w, bar_y + bar_h), outline=255, fill=0)

        progress = int((step / total) * bar_w)
        if progress > 2:
            draw.rectangle((5, bar_y + 1, 4 + progress - 1, bar_y + bar_h - 1), fill=255)

        self.disp.display(image)

    def show_config_screen(self):
        """Muestra pantalla de configuración de umbral"""
        if not self.disp:
            print(f"[Config] Umbral: {self.config.audio.threshold_db} dB")
            return

        image = Image.new('1', (self.width, self.height))
        draw = ImageDraw.Draw(image)

        draw.text((0, 2), "Volume BeGone", font=self.font, fill=255)
        draw.text((0, 14), "Config. Umbral:", font=self.font, fill=255)
        draw.text((30, 28), f"{self.config.audio.threshold_db} dB", font=self.font, fill=255)

        # Barra
        bar_y, bar_h, bar_w = 45, 8, 120
        draw.rectangle((4, bar_y, 4 + bar_w, bar_y + bar_h), outline=255, fill=0)

        fill = int((self.config.audio.threshold_db - self.config.audio.min_threshold_db) *
                   bar_w / (self.config.audio.max_threshold_db - self.config.audio.min_threshold_db))
        if fill > 2:
            draw.rectangle((6, bar_y + 2, 4 + fill, bar_y + bar_h - 2), fill=255)

        draw.text((0, 56), "Gira:Ajustar OK:Iniciar", font=self.font_small, fill=255)

        self.disp.display(image)

    def show_status_screen(self, status: str, details: str = "", icon: str = ""):
        """Muestra pantalla de estado"""
        if not self.disp:
            print(f"[Status] {status} - {details}")
            return

        image = Image.new('1', (self.width, self.height))
        draw = ImageDraw.Draw(image)

        draw.text((0, 2), "Volume BeGone", font=self.font, fill=255)

        if icon == "ok":
            draw.text((50, 16), "[OK]", font=self.font, fill=255)
        elif icon == "error":
            draw.text((50, 16), "[X]", font=self.font, fill=255)
        elif icon == "warning":
            draw.text((50, 16), "[!]", font=self.font, fill=255)

        draw.text((0, 28), status[:20], font=self.font, fill=255)
        if details:
            draw.text((0, 40), details[:20], font=self.font_small, fill=255)

        self.disp.display(image)

    def show_volume_meter(self, db_level: float, device_count: int = 0):
        """Muestra medidor de volumen en tiempo real"""
        if not self.disp:
            return

        image = Image.new('1', (self.width, self.height))
        draw = ImageDraw.Draw(image)

        # Estado
        status = "ACTIVO!" if db_level > self.config.audio.threshold_db else ""
        draw.text((0, 2), f"VBG {status}", font=self.font, fill=255)

        # Niveles
        draw.text((0, 14), f"Nivel: {db_level:.1f} dB", font=self.font, fill=255)
        draw.text((0, 26), f"Umbral: {self.config.audio.threshold_db} dB", font=self.font, fill=255)

        # Medidor
        bar_y, bar_h, bar_w = 40, 10, 120
        draw.rectangle((4, bar_y, 4 + bar_w, bar_y + bar_h), outline=255, fill=0)

        if db_level > 0:
            level = int(min(db_level, 120) * bar_w / 120)
            if level > 2:
                draw.rectangle((6, bar_y + 2, 4 + level, bar_y + bar_h - 2), fill=255)

        # Línea del umbral
        thresh_x = 4 + int(self.config.audio.threshold_db * bar_w / 120)
        draw.line((thresh_x, bar_y - 2, thresh_x, bar_y + bar_h + 2), fill=255, width=2)

        # Info
        draw.text((0, 54), f"D:{device_count} OK:Config 2s:Reset", font=self.font_small, fill=255)

        self.disp.display(image)

    def show_message(self, line1: str, line2: str, line3: str = "", line4: str = ""):
        """Muestra mensaje en pantalla"""
        if not self.disp:
            print(f"[Display] {line1} | {line2} | {line3} | {line4}")
            return

        image = Image.new('1', (self.width, self.height))
        draw = ImageDraw.Draw(image)

        draw.text((0, 2), "Volume BeGone", font=self.font, fill=255)
        draw.text((0, 16), line1, font=self.font, fill=255)
        draw.text((0, 28), line2, font=self.font, fill=255)
        if line3:
            draw.text((0, 40), line3, font=self.font, fill=255)
        if line4:
            draw.text((0, 52), line4, font=self.font_small, fill=255)

        self.disp.display(image)

    def request_update(self, db_level: float):
        """Solicita actualización asíncrona del display"""
        with self._display_lock:
            self._pending_db_level = db_level
            self._update_needed = True

    def start_update_thread(self, get_device_count: Callable[[], int]):
        """Inicia thread de actualización del display"""
        def update_loop():
            while self.running:
                try:
                    update = False
                    level = 0.0

                    with self._display_lock:
                        if self._update_needed:
                            update = True
                            level = self._pending_db_level
                            self._update_needed = False

                    if update and not self.config.config_mode:
                        self.show_volume_meter(level, get_device_count())

                    time.sleep(0.05)

                except Exception as e:
                    print(f"[Display] Error en update thread: {e}")
                    time.sleep(0.1)

        self._display_thread = threading.Thread(target=update_loop, daemon=True)
        self._display_thread.start()

    def on_threshold_change(self, callback: Callable[[int], None]):
        """Registra callback para cambio de umbral"""
        self._on_threshold_change = callback

    def on_button_press(self, callback: Callable[[], None]):
        """Registra callback para presión corta del botón"""
        self._on_button_press = callback

    def on_button_long_press(self, callback: Callable[[], None]):
        """Registra callback para presión larga del botón"""
        self._on_button_long_press = callback

    def cleanup(self):
        """Limpia recursos"""
        self.running = False

        if self._encoder_thread:
            self._encoder_thread.join(timeout=1)

        if self._display_thread:
            self._display_thread.join(timeout=1)

        if RPI_AVAILABLE:
            try:
                GPIO.cleanup()
            except:
                pass

        print("[Display] Recursos liberados")
