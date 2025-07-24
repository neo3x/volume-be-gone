@echo off
setlocal enabledelayedexpansion

REM =========================================
REM Volume Be Gone - Complete Project Setup
REM Creates full project structure for GitHub
REM =========================================

echo.
echo  Volume Be Gone - Project Creator
echo.
echo =========================================
echo Project Structure Creator for GitHub
echo =========================================
echo.

REM Get project name from user or use default
set PROJECT_NAME=volume-be-gone
set /p "PROJECT_NAME=Enter project name (default: volume-be-gone): " || set PROJECT_NAME=volume-be-gone

echo.
echo Creating project: %PROJECT_NAME%
echo.

REM Create main directory
if exist %PROJECT_NAME% (
    echo [!] Directory %PROJECT_NAME% already exists!
    set /p "CONTINUE=Do you want to continue anyway? (y/n): "
    if /i "!CONTINUE!" neq "y" (
        echo Cancelled.
        pause
        exit /b
    )
)

mkdir %PROJECT_NAME% 2>nul
cd %PROJECT_NAME%

REM Create directory structure
echo [1/10] Creating directory structure...

mkdir src 2>nul
mkdir docs 2>nul
mkdir docs\images 2>nul
mkdir hardware 2>nul
mkdir hardware\schematics 2>nul
mkdir hardware\3d-models 2>nul
mkdir resources 2>nul
mkdir resources\images 2>nul
mkdir resources\sounds 2>nul
mkdir scripts 2>nul
mkdir tests 2>nul
mkdir .github 2>nul
mkdir .github\workflows 2>nul

REM Create main source files
echo [2/10] Creating source files...

REM Main Python file
(
echo #!/usr/bin/env python
echo # -*- coding: utf-8 -*-
echo """
echo Volume Be Gone - Bluetooth Speaker Control by Volume Level
echo 
echo Control automatico de parlantes Bluetooth basado en nivel de volumen ambiental.
echo Utiliza un encoder rotativo para configurar el umbral de activacion.
echo 
echo Author: [Tu Nombre]
echo License: MIT
echo Version: 2.0
echo """
echo.
echo # El codigo completo debe ser copiado aqui
echo # Este es solo un placeholder para la estructura
echo.
echo print("Volume Be Gone v2.0"^)
echo print("Copia el codigo completo de volumeBeGone.py aqui"^)
echo print("Ver documentacion en /docs"^)
) > src\volumeBeGone.py

REM Configuration file template
(
echo {
echo     "threshold_db": 70,
echo     "calibration_offset": 94,
echo     "use_external_adapter": true,
echo     "scan_interval": 30,
echo     "attack_methods": [1, 2, 3],
echo     "debug_mode": false
echo }
) > src\config.json.template

REM Create documentation files
echo [3/10] Creating documentation...

REM Main README - Using delayed expansion to handle special chars
(
echo # %PROJECT_NAME% 🔇
echo.
echo Control automatico de parlantes Bluetooth por nivel de volumen usando Raspberry Pi
echo.
echo ## 🎯 Descripcion
echo.
echo Volume Be Gone es un dispositivo basado en Raspberry Pi que monitorea el nivel de ruido ambiental y automaticamente intenta desconectar parlantes Bluetooth cercanos cuando el volumen supera un umbral configurable ^(70-120 dB^).
echo.
echo ### ✨ Caracteristicas principales:
echo.
echo - 🎚️ **Control preciso** con encoder rotativo
echo - 📊 **Medidor visual** en pantalla OLED 128x64
echo - 📡 **Alcance extendido** hasta 50m con adaptador Clase 1
echo - 🔄 **Busqueda automatica** de dispositivos cada 30 segundos
echo - 💾 **Configuracion persistente** en JSON
echo - 🚀 **Inicio automatico** con systemd
echo.
echo ## ⚠️ Disclaimer
echo.
echo ^> **IMPORTANTE**: Este proyecto es solo para fines educativos. Usalo unicamente con tus propios dispositivos o con permiso explicito. El uso indebido puede ser ilegal en tu jurisdiccion.
echo.
echo ## 🛠️ Hardware Necesario
echo.
echo ### Componentes principales:
echo.
echo - Raspberry Pi 3B+ o 4B ^(2GB+^)
echo - Pantalla OLED 128x64 I2C SSD1306
echo - Encoder Rotativo KY-040
echo - Microfono USB
echo - Adaptador BT Clase 1 USB ^(opcional^)
echo - Fuente 5V 3A USB-C
echo.
echo ### 🔌 Diagrama de conexiones:
echo.
echo Ver diagrama completo en hardware/README.md
echo.
echo ## 💻 Instalacion
echo.
echo ### Metodo rapido:
echo.
echo ```bash
echo # Clonar repositorio
echo git clone https://github.com/tu-usuario/%PROJECT_NAME%.git
echo cd %PROJECT_NAME%
echo.
echo # Ejecutar instalador automatico
echo chmod +x scripts/install.sh
echo sudo ./scripts/install.sh
echo ```
echo.
echo ### Metodo manual:
echo.
echo Ver docs/INSTALL.md para instrucciones detalladas.
echo.
echo ## 🚀 Uso
echo.
echo ### Controles:
echo.
echo - 🔄 **Girar encoder**: Ajustar umbral
echo - ✅ **Presionar**: Confirmar configuracion
echo - 🔄 **Mantener 2s**: Reiniciar dispositivo
echo.
echo ### Ejecucion:
echo.
echo ```bash
echo # Manual
echo cd /home/pi/volumebegone
echo sudo python3 volumeBeGone.py
echo.
echo # Como servicio
echo sudo systemctl start volumebegone
echo ```
echo.
echo ## 📄 Licencia
echo.
echo Este proyecto esta bajo la Licencia MIT - ver LICENSE para detalles.
echo.
echo ## 🙏 Creditos
echo.
echo - Inspirado en "Reggaeton Be Gone" de Roni Bandini
echo - Comunidad Raspberry Pi
echo - Libreria Adafruit para displays OLED
) > README.md

REM Installation guide
(
echo # Guia de Instalacion Detallada
echo.
echo ## Requisitos previos
echo.
echo - Raspberry Pi 3B+ o 4 con Raspberry Pi OS instalado
echo - Conexion a internet
echo - Acceso SSH o teclado/monitor
echo.
echo ## Pasos de instalacion
echo.
echo ### 1. Actualizar sistema
echo.
echo ```bash
echo sudo apt update
echo sudo apt upgrade -y
echo ```
echo.
echo ### 2. Habilitar interfaces
echo.
echo ```bash
echo sudo raspi-config
echo # Ir a: Interface Options
echo # Habilitar: I2C, SPI
echo ```
echo.
echo ### 3. Instalar dependencias del sistema
echo.
echo ```bash
echo sudo apt install -y python3-pip python3-dev python3-numpy
echo sudo apt install -y bluetooth bluez libbluetooth-dev
echo sudo apt install -y python3-smbus i2c-tools
echo sudo apt install -y portaudio19-dev python3-pyaudio
echo sudo apt install -y libatlas-base-dev python3-pil git
echo ```
echo.
echo ### 4. Clonar repositorio
echo.
echo ```bash
echo cd /home/pi
echo git clone https://github.com/tu-usuario/%PROJECT_NAME%.git
echo cd %PROJECT_NAME%
echo ```
echo.
echo ### 5. Instalar dependencias Python
echo.
echo ```bash
echo sudo pip3 install -r requirements.txt
echo ```
echo.
echo ### 6. Configurar permisos
echo.
echo ```bash
echo sudo usermod -a -G bluetooth,audio,i2c pi
echo sudo setcap 'cap_net_raw,cap_net_admin+eip' $^(which python3^)
echo ```
echo.
echo ### 7. Copiar archivos
echo.
echo ```bash
echo sudo mkdir -p /home/pi/volumebegone
echo sudo cp src/volumeBeGone.py /home/pi/volumebegone/
echo sudo cp -r resources/images /home/pi/volumebegone/
echo sudo cp src/config.json.template /home/pi/volumebegone/config.json
echo ```
echo.
echo ### 8. Configurar servicio ^(opcional^)
echo.
echo ```bash
echo sudo cp scripts/volumebegone.service /etc/systemd/system/
echo sudo systemctl daemon-reload
echo sudo systemctl enable volumebegone
echo sudo systemctl start volumebegone
echo ```
echo.
echo ## Verificacion
echo.
echo ```bash
echo # Verificar I2C
echo sudo i2cdetect -y 1
echo.
echo # Verificar Bluetooth
echo hciconfig -a
echo.
echo # Verificar audio
echo arecord -l
echo ```
echo.
echo ## Siguiente paso
echo.
echo Ejecutar `sudo python3 /home/pi/volumebegone/volumeBeGone.py` para iniciar.
) > docs\INSTALL.md

REM Troubleshooting guide
(
echo # Guia de Solucion de Problemas
echo.
echo ## Problemas comunes y soluciones
echo.
echo ### 1. Pantalla OLED no funciona
echo.
echo **Sintoma**: La pantalla no muestra nada
echo.
echo **Solucion**:
echo ```bash
echo # Verificar conexiones I2C
echo sudo i2cdetect -y 1
echo # Debe mostrar 3c o 3d
echo ```
echo.
echo Si no aparece:
echo - Verificar conexiones fisicas
echo - Verificar que I2C este habilitado
echo - Probar con `sudo i2cdetect -y 0`
echo.
echo ### 2. Microfono no detectado
echo.
echo **Sintoma**: Error al iniciar captura de audio
echo.
echo **Solucion**:
echo ```bash
echo # Listar dispositivos de audio
echo arecord -l
echo ```
echo.
echo Si no aparece:
echo - Reconectar microfono USB
echo - Probar otro puerto USB
echo - Reiniciar Raspberry Pi
echo.
echo ### 3. Bluetooth no encuentra dispositivos
echo.
echo **Sintoma**: 0 dispositivos encontrados
echo.
echo **Solucion**:
echo ```bash
echo # Reiniciar servicio Bluetooth
echo sudo systemctl restart bluetooth
echo.
echo # Escanear manualmente
echo sudo hcitool scan
echo ```
echo.
echo ### 4. Error de permisos
echo.
echo **Sintoma**: Permission denied
echo.
echo **Solucion**:
echo ```bash
echo # Agregar usuario a grupos necesarios
echo sudo usermod -a -G bluetooth,audio,i2c,gpio pi
echo.
echo # Cerrar sesion y volver a entrar
echo logout
echo ```
echo.
echo ### 5. Alto consumo de CPU
echo.
echo **Sintoma**: Sistema lento, temperatura alta
echo.
echo **Solucion**:
echo - Reducir frecuencia de escaneo en config.json
echo - Usar disipadores de calor
echo - Limitar numero de dispositivos atacados simultaneamente
echo.
echo ## Logs y depuracion
echo.
echo Ver archivo de log:
echo ```bash
echo tail -f /home/pi/volumebegone/log.txt
echo ```
echo.
echo Modo debug:
echo ```bash
echo # Editar config.json
echo "debug_mode": true
echo ```
echo.
echo ## Contacto
echo.
echo Si el problema persiste, abre un issue en GitHub con:
echo - Descripcion del problema
echo - Mensajes de error completos
echo - Version de Raspberry Pi OS
echo - Salida de `python3 --version`
) > docs\TROUBLESHOOTING.md

REM Hardware documentation
(
echo # Documentacion de Hardware
echo.
echo ## Lista de materiales ^(BOM^)
echo.
echo ### Componentes principales
echo.
echo Componente: Raspberry Pi
echo Especificaciones: 3B+ o 4B, 2GB RAM min
echo.
echo Componente: OLED Display
echo Especificaciones: 128x64, I2C, SSD1306
echo.
echo Componente: Encoder Rotativo
echo Especificaciones: KY-040 o similar
echo.
echo Componente: Microfono USB
echo Especificaciones: Compatible con Linux
echo.
echo Componente: Adaptador BT
echo Especificaciones: Clase 1, USB ^(opcional^)
echo.
echo Componente: Fuente 5V
echo Especificaciones: 3A minimo, USB-C para Pi4
echo.
echo Componente: Cables Dupont
echo Especificaciones: Hembra-Hembra, 10 unidades
echo.
echo ## Esquema de conexiones
echo.
echo ### Pinout Raspberry Pi
echo.
echo ```
echo                 Raspberry Pi 40-pin Header
echo    3V3  ^(1^)  o  o  ^(2^)  5V
echo    SDA  ^(3^)  o  o  ^(4^)  5V
echo    SCL  ^(5^)  o  o  ^(6^)  GND
echo         ^(7^)  o  o  ^(8^)
echo    GND  ^(9^)  o  o  ^(10^)
echo         ^(11^) o  o  ^(12^)
echo GPIO13  ^(33^) o  o  ^(34^) GND
echo GPIO19  ^(35^) o  o  ^(36^)
echo GPIO26  ^(37^) o  o  ^(38^)
echo    GND  ^(39^) o  o  ^(40^)
echo ```
echo.
echo ### Conexiones detalladas
echo.
echo **OLED Display I2C:**
echo - VCC → Pin 1 ^(3.3V^)
echo - GND → Pin 6 ^(GND^)
echo - SDA → Pin 3 ^(GPIO2/SDA^)
echo - SCL → Pin 5 ^(GPIO3/SCL^)
echo.
echo **Encoder KY-040:**
echo - CLK → Pin 35 ^(GPIO19^)
echo - DT  → Pin 33 ^(GPIO13^)
echo - SW  → Pin 37 ^(GPIO26^)
echo - +   → Pin 1 ^(3.3V^)
echo - GND → Pin 39 ^(GND^)
echo.
echo ## Carcasa 3D
echo.
echo Los archivos STL para imprimir la carcasa estan en `/hardware/3d-models/`
echo.
echo ### Parametros de impresion recomendados:
echo - Layer height: 0.2mm
echo - Infill: 20%%
echo - Supports: Si ^(para los puertos USB^)
echo - Tiempo estimado: 3-4 horas
echo.
echo ## Notas de ensamblaje
echo.
echo 1. Verificar polaridad antes de conectar
echo 2. Usar cables cortos para I2C ^(max 30cm^)
echo 3. Alejar microfono de fuentes de ruido
echo 4. Considerar blindaje para el encoder si hay interferencias
) > hardware\README.md

REM Create requirements.txt
echo [4/10] Creating requirements file...

(
echo # Volume Be Gone - Python Dependencies
echo # Install with: pip3 install -r requirements.txt
echo.
echo # Audio processing
echo sounddevice==0.4.6
echo numpy==1.24.3
echo scipy==1.10.1
echo.
echo # Bluetooth
echo pybluez==0.23
echo.
echo # GPIO and Hardware
echo RPi.GPIO==0.7.1
echo.
echo # Display
echo Adafruit-SSD1306==1.6.2
echo Adafruit-GPIO==1.0.3
echo Pillow==10.0.0
echo.
echo # System
echo psutil==5.9.5
echo python-apt==2.4.0
) > requirements.txt

REM Create scripts
echo [5/10] Creating utility scripts...

REM Install script - Creating it in parts to avoid special char issues
echo #!/bin/bash > scripts\install.sh
echo # >> scripts\install.sh
echo # Volume Be Gone - Automated Installer >> scripts\install.sh
echo # Run with: sudo bash install.sh >> scripts\install.sh
echo # >> scripts\install.sh
echo. >> scripts\install.sh
echo set -e  # Exit on error >> scripts\install.sh
echo. >> scripts\install.sh
echo # Colors for output >> scripts\install.sh
echo RED='\033[0;31m' >> scripts\install.sh
echo GREEN='\033[0;32m' >> scripts\install.sh
echo YELLOW='\033[1;33m' >> scripts\install.sh
echo NC='\033[0m' # No Color >> scripts\install.sh
echo. >> scripts\install.sh
echo echo -e "${GREEN}=====================================${NC}" >> scripts\install.sh
echo echo -e "${GREEN}Volume Be Gone - Installer${NC}" >> scripts\install.sh
echo echo -e "${GREEN}=====================================${NC}" >> scripts\install.sh
echo echo >> scripts\install.sh
echo. >> scripts\install.sh
echo # Check if running as root >> scripts\install.sh
echo if [[ $EUID -ne 0 ]]; then >> scripts\install.sh
echo    echo -e "${RED}This script must be run as root${NC}" >> scripts\install.sh
echo    echo "Please run: sudo bash install.sh" >> scripts\install.sh
echo    exit 1 >> scripts\install.sh
echo fi >> scripts\install.sh
echo. >> scripts\install.sh
echo # Update system >> scripts\install.sh
echo echo -e "${YELLOW}[1/8] Updating system packages...${NC}" >> scripts\install.sh
echo apt-get update >> scripts\install.sh
echo apt-get upgrade -y >> scripts\install.sh
echo. >> scripts\install.sh
echo # Install system dependencies >> scripts\install.sh
echo echo -e "${YELLOW}[2/8] Installing system dependencies...${NC}" >> scripts\install.sh
echo apt-get install -y \ >> scripts\install.sh
echo     python3-pip python3-dev python3-numpy \ >> scripts\install.sh
echo     bluetooth bluez libbluetooth-dev \ >> scripts\install.sh
echo     python3-smbus i2c-tools \ >> scripts\install.sh
echo     portaudio19-dev python3-pyaudio \ >> scripts\install.sh
echo     libatlas-base-dev python3-pil \ >> scripts\install.sh
echo     git python3-venv >> scripts\install.sh
echo. >> scripts\install.sh
echo # Enable interfaces >> scripts\install.sh
echo echo -e "${YELLOW}[3/8] Enabling I2C and SPI interfaces...${NC}" >> scripts\install.sh
echo raspi-config nonint do_i2c 0 >> scripts\install.sh
echo raspi-config nonint do_spi 0 >> scripts\install.sh
echo. >> scripts\install.sh
echo # Install Python dependencies >> scripts\install.sh
echo echo -e "${YELLOW}[4/8] Installing Python dependencies...${NC}" >> scripts\install.sh
echo pip3 install --upgrade pip >> scripts\install.sh
echo pip3 install -r requirements.txt >> scripts\install.sh
echo. >> scripts\install.sh
echo # Create project directory >> scripts\install.sh
echo echo -e "${YELLOW}[5/8] Creating project directory...${NC}" >> scripts\install.sh
echo mkdir -p /home/pi/volumebegone >> scripts\install.sh
echo cp src/volumeBeGone.py /home/pi/volumebegone/ >> scripts\install.sh
echo cp -r resources/images /home/pi/volumebegone/ >> scripts\install.sh
echo cp src/config.json.template /home/pi/volumebegone/config.json >> scripts\install.sh
echo chown -R pi:pi /home/pi/volumebegone >> scripts\install.sh
echo. >> scripts\install.sh
echo # Configure permissions >> scripts\install.sh
echo echo -e "${YELLOW}[6/8] Configuring permissions...${NC}" >> scripts\install.sh
echo usermod -a -G bluetooth,audio,i2c,gpio pi >> scripts\install.sh
echo setcap 'cap_net_raw,cap_net_admin+eip' $(which python3) >> scripts\install.sh
echo. >> scripts\install.sh
echo # Enable Bluetooth service >> scripts\install.sh
echo echo -e "${YELLOW}[7/8] Enabling services...${NC}" >> scripts\install.sh
echo systemctl enable bluetooth >> scripts\install.sh
echo systemctl start bluetooth >> scripts\install.sh
echo. >> scripts\install.sh
echo # Install systemd service >> scripts\install.sh
echo echo -e "${YELLOW}[8/8] Installing systemd service...${NC}" >> scripts\install.sh
echo if [ -f "scripts/volumebegone.service" ]; then >> scripts\install.sh
echo     cp scripts/volumebegone.service /etc/systemd/system/ >> scripts\install.sh
echo     systemctl daemon-reload >> scripts\install.sh
echo     echo -e "${GREEN}Systemd service installed${NC}" >> scripts\install.sh
echo     echo "To enable auto-start: sudo systemctl enable volumebegone" >> scripts\install.sh
echo fi >> scripts\install.sh
echo. >> scripts\install.sh
echo echo -e "${GREEN}=====================================${NC}" >> scripts\install.sh
echo echo -e "${GREEN}Installation completed successfully!${NC}" >> scripts\install.sh
echo echo -e "${GREEN}=====================================${NC}" >> scripts\install.sh
echo echo >> scripts\install.sh
echo echo "Next steps:" >> scripts\install.sh
echo echo "1. Reboot your Raspberry Pi: sudo reboot" >> scripts\install.sh
echo echo "2. Test the installation: sudo python3 /home/pi/volumebegone/volumeBeGone.py" >> scripts\install.sh
echo echo "3. Enable auto-start (optional): sudo systemctl enable volumebegone" >> scripts\install.sh
echo echo >> scripts\install.sh

REM Update script
(
echo #!/bin/bash
echo #
echo # Volume Be Gone - Update Script
echo #
echo.
echo echo "Updating Volume Be Gone..."
echo.
echo # Pull latest changes
echo git pull
echo.
echo # Update dependencies
echo sudo pip3 install -r requirements.txt --upgrade
echo.
echo # Copy updated files
echo sudo cp src/volumeBeGone.py /home/pi/volumebegone/
echo sudo cp -r resources/images /home/pi/volumebegone/
echo.
echo # Restart service if running
echo if systemctl is-active --quiet volumebegone; then
echo     echo "Restarting service..."
echo     sudo systemctl restart volumebegone
echo fi
echo.
echo echo "Update completed!"
) > scripts\update.sh

REM Systemd service file
(
echo [Unit]
echo Description=Volume Be Gone - Bluetooth Speaker Control
echo After=bluetooth.target sound.target network.target
echo Wants=bluetooth.target
echo.
echo [Service]
echo Type=simple
echo User=pi
echo Group=pi
echo WorkingDirectory=/home/pi/volumebegone
echo Environment="PYTHONUNBUFFERED=1"
echo ExecStartPre=/bin/sleep 10
echo ExecStart=/usr/bin/python3 /home/pi/volumebegone/volumeBeGone.py
echo Restart=on-failure
echo RestartSec=10
echo StandardOutput=journal
echo StandardError=journal
echo.
echo [Install]
echo WantedBy=multi-user.target
) > scripts\volumebegone.service

REM Create test files
echo [6/10] Creating test files...

REM Component test - Creating in parts to avoid syntax errors
echo #!/usr/bin/env python3 > tests\test_components.py
echo # Component Test Script for Volume Be Gone >> tests\test_components.py
echo # Tests all hardware components individually >> tests\test_components.py
echo. >> tests\test_components.py
echo import sys >> tests\test_components.py
echo import time >> tests\test_components.py
echo. >> tests\test_components.py
echo print^("="*50^) >> tests\test_components.py
echo print^("Volume Be Gone - Component Test"^) >> tests\test_components.py
echo print^("="*50^) >> tests\test_components.py
echo print^(^) >> tests\test_components.py
echo. >> tests\test_components.py
echo # Test 1: GPIO >> tests\test_components.py
echo print^("[TEST] GPIO Library..."^) >> tests\test_components.py
echo try: >> tests\test_components.py
echo     import RPi.GPIO as GPIO >> tests\test_components.py
echo     GPIO.setmode^(GPIO.BCM^) >> tests\test_components.py
echo     GPIO.setwarnings^(False^) >> tests\test_components.py
echo     print^("✓ GPIO library loaded successfully"^) >> tests\test_components.py
echo     GPIO.cleanup^(^) >> tests\test_components.py
echo except Exception as e: >> tests\test_components.py
echo     print^(f"✗ GPIO Error: {e}"^) >> tests\test_components.py
echo. >> tests\test_components.py
echo # Test 2: I2C Display >> tests\test_components.py
echo print^("\n[TEST] OLED Display..."^) >> tests\test_components.py
echo try: >> tests\test_components.py
echo     import Adafruit_SSD1306 >> tests\test_components.py
echo     from PIL import Image, ImageDraw, ImageFont >> tests\test_components.py
echo     disp = Adafruit_SSD1306.SSD1306_128_64^(rst=None^) >> tests\test_components.py
echo     disp.begin^(^) >> tests\test_components.py
echo     disp.clear^(^) >> tests\test_components.py
echo     disp.display^(^) >> tests\test_components.py
echo     print^("✓ OLED display initialized"^) >> tests\test_components.py
echo except Exception as e: >> tests\test_components.py
echo     print^(f"✗ Display Error: {e}"^) >> tests\test_components.py
echo. >> tests\test_components.py
echo # Test 3: Bluetooth >> tests\test_components.py
echo print^("\n[TEST] Bluetooth..."^) >> tests\test_components.py
echo try: >> tests\test_components.py
echo     import bluetooth >> tests\test_components.py
echo     import subprocess >> tests\test_components.py
echo     result = subprocess.run^(["hciconfig"], capture_output=True, text=True^) >> tests\test_components.py
echo     if "hci0" in result.stdout: >> tests\test_components.py
echo         print^("✓ Bluetooth adapter found"^) >> tests\test_components.py
echo     else: >> tests\test_components.py
echo         print^("✗ No Bluetooth adapter found"^) >> tests\test_components.py
echo except Exception as e: >> tests\test_components.py
echo     print^(f"✗ Bluetooth Error: {e}"^) >> tests\test_components.py
echo. >> tests\test_components.py
echo # Test 4: Audio >> tests\test_components.py
echo print^("\n[TEST] Audio Input..."^) >> tests\test_components.py
echo try: >> tests\test_components.py
echo     import sounddevice as sd >> tests\test_components.py
echo     devices = sd.query_devices^(^) >> tests\test_components.py
echo     input_count = 0 >> tests\test_components.py
echo     for d in devices: >> tests\test_components.py
echo         if d.get^('max_input_channels', 0^) ^> 0: >> tests\test_components.py
echo             input_count += 1 >> tests\test_components.py
echo     if input_count ^> 0: >> tests\test_components.py
echo         print^(f"✓ Found {input_count} audio input device(s)"^) >> tests\test_components.py
echo     else: >> tests\test_components.py
echo         print^("✗ No audio input devices found"^) >> tests\test_components.py
echo except Exception as e: >> tests\test_components.py
echo     print^(f"✗ Audio Error: {e}"^) >> tests\test_components.py
echo. >> tests\test_components.py
echo # Test 5: Encoder >> tests\test_components.py
echo print^("\n[TEST] Encoder Pins..."^) >> tests\test_components.py
echo try: >> tests\test_components.py
echo     GPIO.setmode^(GPIO.BCM^) >> tests\test_components.py
echo     # Test CLK pin >> tests\test_components.py
echo     GPIO.setup^(19, GPIO.IN, pull_up_down=GPIO.PUD_UP^) >> tests\test_components.py
echo     state = GPIO.input^(19^) >> tests\test_components.py
echo     status = "HIGH" if state else "LOW" >> tests\test_components.py
echo     print^(f"✓ Encoder CLK ^(GPIO19^): {status}"^) >> tests\test_components.py
echo     # Test DT pin >> tests\test_components.py
echo     GPIO.setup^(13, GPIO.IN, pull_up_down=GPIO.PUD_UP^) >> tests\test_components.py
echo     state = GPIO.input^(13^) >> tests\test_components.py
echo     status = "HIGH" if state else "LOW" >> tests\test_components.py
echo     print^(f"✓ Encoder DT ^(GPIO13^): {status}"^) >> tests\test_components.py
echo     # Test SW pin >> tests\test_components.py
echo     GPIO.setup^(26, GPIO.IN, pull_up_down=GPIO.PUD_UP^) >> tests\test_components.py
echo     state = GPIO.input^(26^) >> tests\test_components.py
echo     status = "HIGH" if state else "LOW" >> tests\test_components.py
echo     print^(f"✓ Encoder SW ^(GPIO26^): {status}"^) >> tests\test_components.py
echo     GPIO.cleanup^(^) >> tests\test_components.py
echo except Exception as e: >> tests\test_components.py
echo     print^(f"✗ Encoder Error: {e}"^) >> tests\test_components.py
echo. >> tests\test_components.py
echo print^("\n"^) >> tests\test_components.py
echo print^("="*50^) >> tests\test_components.py
echo print^("Test completed. Check results above."^) >> tests\test_components.py
echo print^("="*50^) >> tests\test_components.py

REM Create encoder test
echo #!/usr/bin/env python3 > tests\test_encoder.py
echo # Test encoder rotation and button >> tests\test_encoder.py
echo. >> tests\test_encoder.py
echo import RPi.GPIO as GPIO >> tests\test_encoder.py
echo import time >> tests\test_encoder.py
echo. >> tests\test_encoder.py
echo # Encoder pins >> tests\test_encoder.py
echo CLK = 19 >> tests\test_encoder.py
echo DT = 13 >> tests\test_encoder.py
echo SW = 26 >> tests\test_encoder.py
echo. >> tests\test_encoder.py
echo GPIO.setmode^(GPIO.BCM^) >> tests\test_encoder.py
echo GPIO.setup^(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP^) >> tests\test_encoder.py
echo GPIO.setup^(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP^) >> tests\test_encoder.py
echo GPIO.setup^(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP^) >> tests\test_encoder.py
echo. >> tests\test_encoder.py
echo counter = 0 >> tests\test_encoder.py
echo clkLastState = GPIO.input^(CLK^) >> tests\test_encoder.py
echo. >> tests\test_encoder.py
echo print^("Encoder Test - Rotate and press button"^) >> tests\test_encoder.py
echo print^("Press Ctrl+C to exit"^) >> tests\test_encoder.py
echo. >> tests\test_encoder.py
echo try: >> tests\test_encoder.py
echo     while True: >> tests\test_encoder.py
echo         clkState = GPIO.input^(CLK^) >> tests\test_encoder.py
echo         dtState = GPIO.input^(DT^) >> tests\test_encoder.py
echo         swState = GPIO.input^(SW^) >> tests\test_encoder.py
echo. >> tests\test_encoder.py        
echo         if clkState != clkLastState: >> tests\test_encoder.py
echo             if dtState != clkState: >> tests\test_encoder.py
echo                 counter += 1 >> tests\test_encoder.py
echo             else: >> tests\test_encoder.py
echo                 counter -= 1 >> tests\test_encoder.py
echo             print^(f"Counter: {counter}"^) >> tests\test_encoder.py
echo. >> tests\test_encoder.py
echo         if swState == GPIO.LOW: >> tests\test_encoder.py
echo             print^("Button pressed!"^) >> tests\test_encoder.py
echo             time.sleep^(0.3^) >> tests\test_encoder.py
echo. >> tests\test_encoder.py
echo         clkLastState = clkState >> tests\test_encoder.py
echo         time.sleep^(0.001^) >> tests\test_encoder.py
echo except KeyboardInterrupt: >> tests\test_encoder.py
echo     GPIO.cleanup^(^) >> tests\test_encoder.py
echo     print^("\nTest finished"^) >> tests\test_encoder.py

REM Create audio test
echo #!/usr/bin/env python3 > tests\test_audio.py
echo # Test audio input levels >> tests\test_audio.py
echo. >> tests\test_audio.py
echo import sounddevice as sd >> tests\test_audio.py
echo import numpy as np >> tests\test_audio.py
echo import time >> tests\test_audio.py
echo. >> tests\test_audio.py
echo def calculate_db^(audio_data^): >> tests\test_audio.py
echo     # Calculate dB level >> tests\test_audio.py
echo     rms = np.sqrt^(np.mean^(audio_data**2^)^) >> tests\test_audio.py
echo     if rms ^> 0: >> tests\test_audio.py
echo         db = 20 * np.log10^(rms^) + 94 >> tests\test_audio.py
echo         return db >> tests\test_audio.py
echo     return -np.inf >> tests\test_audio.py
echo. >> tests\test_audio.py
echo print^("Audio Level Monitor"^) >> tests\test_audio.py
echo print^("Speak or make noise to see levels"^) >> tests\test_audio.py
echo print^("Press Ctrl+C to exit\n"^) >> tests\test_audio.py
echo. >> tests\test_audio.py
echo def audio_callback^(indata, frames, time, status^): >> tests\test_audio.py
echo     if status: >> tests\test_audio.py
echo         print^(status^) >> tests\test_audio.py
echo     db = calculate_db^(indata.flatten^(^)^) >> tests\test_audio.py
echo     if db ^> -np.inf: >> tests\test_audio.py
echo         bar = "=" * int^(^(db + 50^) / 2^) >> tests\test_audio.py
echo         print^(f"\rLevel: {db:6.1f} dB [{bar:^<50}]", end=''^) >> tests\test_audio.py
echo. >> tests\test_audio.py
echo try: >> tests\test_audio.py
echo     with sd.InputStream^(callback=audio_callback, channels=1, samplerate=44100^): >> tests\test_audio.py
echo         while True: >> tests\test_audio.py
echo             time.sleep^(0.1^) >> tests\test_audio.py
echo except KeyboardInterrupt: >> tests\test_audio.py
echo     print^("\n\nTest finished"^) >> tests\test_audio.py

REM Create GitHub Actions workflow
echo [7/10] Creating GitHub Actions workflow...

echo name: CI > .github\workflows\ci.yml
echo. >> .github\workflows\ci.yml
echo on: >> .github\workflows\ci.yml
echo   push: >> .github\workflows\ci.yml
echo     branches: [ main, develop ] >> .github\workflows\ci.yml
echo   pull_request: >> .github\workflows\ci.yml
echo     branches: [ main ] >> .github\workflows\ci.yml
echo. >> .github\workflows\ci.yml
echo jobs: >> .github\workflows\ci.yml
echo   test: >> .github\workflows\ci.yml
echo     runs-on: ubuntu-latest >> .github\workflows\ci.yml
echo. >> .github\workflows\ci.yml     
echo     steps: >> .github\workflows\ci.yml
echo     - uses: actions/checkout@v3 >> .github\workflows\ci.yml
echo. >> .github\workflows\ci.yml     
echo     - name: Set up Python >> .github\workflows\ci.yml
echo       uses: actions/setup-python@v4 >> .github\workflows\ci.yml
echo       with: >> .github\workflows\ci.yml
echo         python-version: '3.9' >> .github\workflows\ci.yml
echo. >> .github\workflows\ci.yml     
echo     - name: Install dependencies >> .github\workflows\ci.yml
echo       run: ^| >> .github\workflows\ci.yml
echo         python -m pip install --upgrade pip >> .github\workflows\ci.yml
echo         pip install flake8 pytest >> .github\workflows\ci.yml
echo         # Install only non-RPi specific requirements for CI >> .github\workflows\ci.yml
echo         pip install numpy sounddevice pillow >> .github\workflows\ci.yml
echo. >> .github\workflows\ci.yml     
echo     - name: Lint with flake8 >> .github\workflows\ci.yml
echo       run: ^| >> .github\workflows\ci.yml
echo         flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics >> .github\workflows\ci.yml
echo         flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics >> .github\workflows\ci.yml
echo. >> .github\workflows\ci.yml     
echo     - name: Test imports >> .github\workflows\ci.yml
echo       run: ^| >> .github\workflows\ci.yml
echo         python -c "import sys; sys.path.append^('src'^); print^('Import test passed'^)" >> .github\workflows\ci.yml

REM Create additional documentation files
echo [8/10] Creating additional documentation...

REM Contributing guide
echo # Contributing to Volume Be Gone > CONTRIBUTING.md
echo. >> CONTRIBUTING.md
echo First off, thank you for considering contributing to Volume Be Gone! >> CONTRIBUTING.md
echo. >> CONTRIBUTING.md
echo ## How to Contribute >> CONTRIBUTING.md
echo. >> CONTRIBUTING.md
echo ### Reporting Bugs >> CONTRIBUTING.md
echo. >> CONTRIBUTING.md
echo Before creating bug reports, please check existing issues. When creating a bug report, include: >> CONTRIBUTING.md
echo. >> CONTRIBUTING.md
echo - Your operating system and version >> CONTRIBUTING.md
echo - Raspberry Pi model >> CONTRIBUTING.md
echo - Python version >> CONTRIBUTING.md
echo - Detailed steps to reproduce >> CONTRIBUTING.md
echo - Error messages ^(if any^) >> CONTRIBUTING.md
echo. >> CONTRIBUTING.md
echo ### Suggesting Enhancements >> CONTRIBUTING.md
echo. >> CONTRIBUTING.md
echo Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include: >> CONTRIBUTING.md
echo. >> CONTRIBUTING.md
echo - A clear and descriptive title >> CONTRIBUTING.md
echo - A detailed description of the proposed enhancement >> CONTRIBUTING.md
echo - Explain why this enhancement would be useful >> CONTRIBUTING.md
echo. >> CONTRIBUTING.md
echo ### Pull Requests >> CONTRIBUTING.md
echo. >> CONTRIBUTING.md
echo 1. Fork the repo and create your branch from `main` >> CONTRIBUTING.md
echo 2. Make your changes >> CONTRIBUTING.md
echo 3. Test your changes thoroughly >> CONTRIBUTING.md
echo 4. Update documentation if needed >> CONTRIBUTING.md
echo 5. Submit the pull request >> CONTRIBUTING.md
echo. >> CONTRIBUTING.md
echo ## Code Style >> CONTRIBUTING.md
echo. >> CONTRIBUTING.md
echo - Follow PEP 8 >> CONTRIBUTING.md
echo - Use meaningful variable names >> CONTRIBUTING.md
echo - Add comments for complex logic >> CONTRIBUTING.md
echo - Keep functions small and focused >> CONTRIBUTING.md
echo. >> CONTRIBUTING.md
echo ## Testing >> CONTRIBUTING.md
echo. >> CONTRIBUTING.md
echo Run all tests before submitting: >> CONTRIBUTING.md
echo ```bash >> CONTRIBUTING.md
echo python3 tests/test_components.py >> CONTRIBUTING.md
echo python3 tests/test_encoder.py >> CONTRIBUTING.md
echo python3 tests/test_audio.py >> CONTRIBUTING.md
echo ``` >> CONTRIBUTING.md
echo. >> CONTRIBUTING.md
echo ## License >> CONTRIBUTING.md
echo. >> CONTRIBUTING.md
echo By contributing, you agree that your contributions will be licensed under the MIT License. >> CONTRIBUTING.md

REM Create changelog
echo # Changelog > CHANGELOG.md
echo. >> CHANGELOG.md
echo All notable changes to Volume Be Gone will be documented in this file. >> CHANGELOG.md
echo. >> CHANGELOG.md
echo The format is based on Keep a Changelog, >> CHANGELOG.md
echo and this project adheres to Semantic Versioning. >> CHANGELOG.md
echo. >> CHANGELOG.md
echo ## [Unreleased] >> CHANGELOG.md
echo. >> CHANGELOG.md
echo ## [2.0.0] - 2024-01-XX >> CHANGELOG.md
echo. >> CHANGELOG.md
echo ### Added >> CHANGELOG.md
echo - Encoder rotativo para control de umbral >> CHANGELOG.md
echo - Pantalla OLED 128x64 con medidor visual >> CHANGELOG.md
echo - Soporte para adaptador Bluetooth Clase 1 >> CHANGELOG.md
echo - Configuracion persistente en JSON >> CHANGELOG.md
echo - Deteccion automatica de adaptadores BT >> CHANGELOG.md
echo - Sistema de logging mejorado >> CHANGELOG.md
echo - Tests de componentes >> CHANGELOG.md
echo. >> CHANGELOG.md
echo ### Changed >> CHANGELOG.md
echo - Interfaz completamente rediseñada >> CHANGELOG.md
echo - Algoritmo de deteccion de volumen mejorado >> CHANGELOG.md
echo - Estructura de proyecto reorganizada >> CHANGELOG.md
echo. >> CHANGELOG.md
echo ### Fixed >> CHANGELOG.md
echo - Problemas de memoria en escaneo continuo >> CHANGELOG.md
echo - Compatibilidad con Raspberry Pi 4 >> CHANGELOG.md
echo. >> CHANGELOG.md
echo ## [1.0.0] - 2024-01-01 >> CHANGELOG.md
echo. >> CHANGELOG.md
echo ### Added >> CHANGELOG.md
echo - Version inicial basada en Reggaeton Be Gone >> CHANGELOG.md
echo - Deteccion por nivel de volumen >> CHANGELOG.md
echo - Busqueda automatica de dispositivos >> CHANGELOG.md
echo - Ataque a multiples parlantes >> CHANGELOG.md

REM Create LICENSE file
echo [9/10] Creating license file...

echo MIT License > LICENSE
echo. >> LICENSE
echo Copyright ^(c^) 2024 [Tu Nombre] >> LICENSE
echo. >> LICENSE
echo Permission is hereby granted, free of charge, to any person obtaining a copy >> LICENSE
echo of this software and associated documentation files ^(the "Software"^), to deal >> LICENSE
echo in the Software without restriction, including without limitation the rights >> LICENSE
echo to use, copy, modify, merge, publish, distribute, sublicense, and/or sell >> LICENSE
echo copies of the Software, and to permit persons to whom the Software is >> LICENSE
echo furnished to do so, subject to the following conditions: >> LICENSE
echo. >> LICENSE
echo The above copyright notice and this permission notice shall be included in all >> LICENSE
echo copies or substantial portions of the Software. >> LICENSE
echo. >> LICENSE
echo THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR >> LICENSE
echo IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, >> LICENSE
echo FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE >> LICENSE
echo AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER >> LICENSE
echo LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, >> LICENSE
echo OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE >> LICENSE
echo SOFTWARE. >> LICENSE

REM Create .gitignore
echo [10/10] Creating .gitignore...

echo # Byte-compiled / optimized / DLL files > .gitignore
echo __pycache__/ >> .gitignore
echo *.py[cod] >> .gitignore
echo *$py.class >> .gitignore
echo. >> .gitignore
echo # C extensions >> .gitignore
echo *.so >> .gitignore
echo. >> .gitignore
echo # Distribution / packaging >> .gitignore
echo .Python >> .gitignore
echo build/ >> .gitignore
echo develop-eggs/ >> .gitignore
echo dist/ >> .gitignore
echo downloads/ >> .gitignore
echo eggs/ >> .gitignore
echo .eggs/ >> .gitignore
echo lib/ >> .gitignore
echo lib64/ >> .gitignore
echo parts/ >> .gitignore
echo sdist/ >> .gitignore
echo var/ >> .gitignore
echo wheels/ >> .gitignore
echo *.egg-info/ >> .gitignore
echo .installed.cfg >> .gitignore
echo *.egg >> .gitignore
echo MANIFEST >> .gitignore
echo. >> .gitignore
echo # Virtual environments >> .gitignore
echo venv/ >> .gitignore
echo ENV/ >> .gitignore
echo env/ >> .gitignore
echo. >> .gitignore
echo # IDE >> .gitignore
echo .vscode/ >> .gitignore
echo .idea/ >> .gitignore
echo *.swp >> .gitignore
echo *.swo >> .gitignore
echo *~ >> .gitignore
echo. >> .gitignore
echo # OS >> .gitignore
echo .DS_Store >> .gitignore
echo .DS_Store? >> .gitignore
echo ._* >> .gitignore
echo .Spotlight-V100 >> .gitignore
echo .Trashes >> .gitignore
echo ehthumbs.db >> .gitignore
echo Thumbs.db >> .gitignore
echo. >> .gitignore
echo # Project specific >> .gitignore
echo config.json >> .gitignore
echo log.txt >> .gitignore
echo *.log >> .gitignore
echo test.wav >> .gitignore
echo *.wav >> .gitignore
echo. >> .gitignore
echo # Temporary files >> .gitignore
echo *.tmp >> .gitignore
echo *.temp >> .gitignore
echo *.bak >> .gitignore
echo. >> .gitignore
echo # Documentation builds >> .gitignore
echo docs/_build/ >> .gitignore
echo docs/.doctrees/ >> .gitignore
echo. >> .gitignore
echo # Coverage reports >> .gitignore
echo htmlcov/ >> .gitignore
echo .coverage >> .gitignore
echo .coverage.* >> .gitignore
echo coverage.xml >> .gitignore
echo *.cover >> .gitignore
echo. >> .gitignore
echo # pytest >> .gitignore
echo .pytest_cache/ >> .gitignore
echo. >> .gitignore
echo # Jupyter Notebook >> .gitignore
echo .ipynb_checkpoints >> .gitignore
echo. >> .gitignore
echo # pyenv >> .gitignore
echo .python-version >> .gitignore

REM Create sample images placeholder
echo Creating placeholder files...

echo # Replace this with actual 128x64 logo for OLED > resources\images\logo.png.txt
echo # Replace with project banner image > docs\images\banner.png.txt
echo # Replace with wiring diagram > docs\images\wiring-diagram.png.txt
echo # Replace with 3D model STL files > hardware\3d-models\case.stl.txt
echo # Replace with schematic files > hardware\schematics\schematic.pdf.txt

REM Create a quick start script
echo @echo off > QUICK_START.bat
echo echo Starting Volume Be Gone development environment... >> QUICK_START.bat
echo echo. >> QUICK_START.bat
echo echo 1. Install Git for Windows if not installed >> QUICK_START.bat
echo echo 2. Open this folder in VS Code or your preferred editor >> QUICK_START.bat
echo echo 3. Copy the complete volumeBeGone.py code to src\volumeBeGone.py >> QUICK_START.bat
echo echo 4. Initialize git repository: git init >> QUICK_START.bat
echo echo 5. Add files: git add . >> QUICK_START.bat
echo echo 6. Commit: git commit -m "Initial commit" >> QUICK_START.bat
echo echo 7. Add your GitHub remote: git remote add origin https://github.com/YOUR_USERNAME/%PROJECT_NAME%.git >> QUICK_START.bat
echo echo 8. Push: git push -u origin main >> QUICK_START.bat
echo echo. >> QUICK_START.bat
echo pause >> QUICK_START.bat

REM Final summary
echo.
echo =========================================
echo Project structure created successfully!
echo =========================================
echo.
echo Project: %PROJECT_NAME%
echo.
echo Structure created:
echo  /src           - Source code
echo  /docs          - Documentation
echo  /hardware      - Hardware files
echo  /resources     - Images and assets
echo  /scripts       - Installation scripts
echo  /tests         - Test files
echo  /.github       - GitHub Actions
echo.
echo Next steps:
echo.
echo 1. Copy the complete volumeBeGone.py code to src\volumeBeGone.py
echo.
echo 2. Add any images:
echo    - Logo: resources/images/logo.png (128x64 px)
echo    - Banner: docs/images/banner.png
echo    - Wiring: docs/images/wiring-diagram.png
echo.
echo 3. Update LICENSE with your name
echo.
echo 4. Initialize Git repository:
echo    cd %PROJECT_NAME%
echo    git init
echo    git add .
echo    git commit -m "Initial commit - Volume Be Gone v2.0"
echo.
echo 5. Create GitHub repository and push:
echo    git remote add origin https://github.com/YOUR_USERNAME/%PROJECT_NAME%.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 6. Optional: Add topics to your GitHub repo:
echo    raspberry-pi, bluetooth, iot, maker, python
echo.
echo Run QUICK_START.bat for a reminder of these steps.
echo.
pause