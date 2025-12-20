#!/usr/bin/env python3
# Component Test Script for Volume Be Gone
# Tests all hardware components individually

import sys
import time

print("="*50)
print("Volume Be Gone - Component Test")
print("="*50)
print()

# Test 1: GPIO
print("[TEST] GPIO Library...")
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    print("[OK] GPIO library loaded successfully")
    GPIO.cleanup()
except Exception as e:
    print(f"[X] GPIO Error: {e}")

# Test 2: I2C Display (usando luma.oled - compatible con Debian Trixie)
print("\n[TEST] OLED Display...")
try:
    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306
    from PIL import Image, ImageDraw

    # Conectar al display via I2C
    serial = i2c(port=1, address=0x3C)
    disp = ssd1306(serial, width=128, height=64)

    # Crear imagen de prueba
    image = Image.new('1', (128, 64))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 127, 63), outline=0, fill=0)
    draw.text((10, 25), "Test OK!", fill=255)
    disp.display(image)

    print("[OK] OLED display initialized (luma.oled)")
except Exception as e:
    print(f"[X] Display Error: {e}")
    print("    Verifica: I2C habilitado, direccion 0x3C o 0x3D")

# Test 3: Bluetooth
print("\n[TEST] Bluetooth...")
try:
    import bluetooth
    import subprocess
    result = subprocess.run(["hciconfig"], capture_output=True, text=True)
    if "hci0" in result.stdout:
        print("[OK] Bluetooth adapter found")
    else:
        print("[X] No Bluetooth adapter found")
except Exception as e:
    print(f"[X] Bluetooth Error: {e}")

# Test 4: Audio
print("\n[TEST] Audio Input...")
try:
    import sounddevice as sd
    devices = sd.query_devices()
    input_count = 0
    for d in devices:
        if d.get('max_input_channels', 0) > 0:
            input_count += 1
    if input_count > 0:
        print(f"[OK] Found {input_count} audio input device(s)")
    else:
        print("[X] No audio input devices found")
except Exception as e:
    print(f"[X] Audio Error: {e}")

# Test 5: Encoder
print("\n[TEST] Encoder Pins...")
try:
    GPIO.setmode(GPIO.BCM)
    # Test CLK pin
    GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    state = GPIO.input(19)
    status = "HIGH" if state else "LOW"
    print(f"[OK] Encoder CLK (GPIO19): {status}")
    # Test DT pin
    GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    state = GPIO.input(13)
    status = "HIGH" if state else "LOW"
    print(f"[OK] Encoder DT (GPIO13): {status}")
    # Test SW pin
    GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    state = GPIO.input(26)
    status = "HIGH" if state else "LOW"
    print(f"[OK] Encoder SW (GPIO26): {status}")
    GPIO.cleanup()
except Exception as e:
    print(f"[X] Encoder Error: {e}")

print("\n")
print("="*50)
print("Test completed. Check results above.")
print("="*50)
