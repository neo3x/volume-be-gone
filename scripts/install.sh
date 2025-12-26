#!/bin/bash
#
# Volume Be Gone v3.0 - Automated Installer
#
# Sistema híbrido: Raspberry Pi + ESP32 BlueJammer
# Incluye servidor web con Access Point para control desde celular.
#
# Run with: sudo bash install.sh
#
# Author: Francisco Ortiz Rojas
# Version: 3.0
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

VERSION="3.0"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════╗"
echo "║      Volume Be Gone v$VERSION - Installer         ║"
echo "║        Hybrid Architecture (RPi + ESP32)       ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"
echo

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Este script debe ejecutarse como root${NC}"
   echo "Uso: sudo bash install.sh"
   exit 1
fi

# Detectar usuario real (no root)
if [ -n "$SUDO_USER" ]; then
    REAL_USER="$SUDO_USER"
else
    REAL_USER=$(logname 2>/dev/null || echo "")
    if [ -z "$REAL_USER" ] || [ "$REAL_USER" = "root" ]; then
        echo -e "${RED}Error: No se puede detectar el usuario${NC}"
        read -p "Ingresa tu nombre de usuario: " REAL_USER
    fi
fi

REAL_HOME=$(eval echo ~$REAL_USER)

# Detectar directorio del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_DIR="$SCRIPT_DIR"

echo -e "${YELLOW}Usuario detectado: $REAL_USER${NC}"
echo -e "${YELLOW}Directorio del proyecto: $INSTALL_DIR${NC}"
echo

# Detectar distribución
echo -e "${BLUE}[1/10] Detectando sistema...${NC}"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    VERSION_NAME=$VERSION_CODENAME
    echo -e "${GREEN}Detectado: $DISTRO $VERSION_NAME${NC}"
fi

# Update system
echo -e "${BLUE}[2/10] Actualizando sistema...${NC}"
apt-get update

# Install system dependencies
echo -e "${BLUE}[3/10] Instalando dependencias del sistema...${NC}"

# Paquetes base
apt-get install -y \
    python3-pip python3-dev python3-numpy python3-scipy \
    bluetooth bluez libbluetooth-dev \
    bluez-tools \
    bluez-hcidump \
    i2c-tools \
    git python3-venv \
    python3-pillow \
    python3-psutil \
    libportaudio2

# Paquetes adicionales para v3.0 (Web Server + AP)
echo -e "${YELLOW}Instalando dependencias web y Access Point...${NC}"
apt-get install -y \
    hostapd \
    dnsmasq \
    iptables

# Verificar herramientas Bluetooth instaladas
echo -e "${YELLOW}Verificando herramientas Bluetooth...${NC}"
MISSING_TOOLS=""

for tool in hcitool l2ping rfcomm sdptool hcidump hciconfig; do
    if command -v "$tool" &> /dev/null; then
        echo -e "${GREEN}  [OK] $tool instalado${NC}"
    else
        echo -e "${RED}  [!] $tool NO encontrado${NC}"
        MISSING_TOOLS="$MISSING_TOOLS $tool"
    fi
done

if [ -n "$MISSING_TOOLS" ]; then
    echo -e "${YELLOW}  [!] Herramientas faltantes:$MISSING_TOOLS${NC}"
    apt-get install -y bluez bluez-tools bluez-hcidump 2>/dev/null || true
fi

# PortAudio dev para compilar
apt-get install -y portaudio19-dev 2>/dev/null || apt-get install -y libportaudio-dev 2>/dev/null || true

# SMBus
apt-get install -y python3-smbus 2>/dev/null || apt-get install -y python3-smbus2 2>/dev/null || true

# BLAS/ATLAS
apt-get install -y libopenblas-dev 2>/dev/null || apt-get install -y libatlas-base-dev 2>/dev/null || true

# GPIO
apt-get install -y python3-rpi.gpio 2>/dev/null || apt-get install -y python3-lgpio python3-gpiod 2>/dev/null || true

# Bluetooth Python desde repos
apt-get install -y python3-bluez 2>/dev/null || true

# Enable interfaces
echo -e "${BLUE}[4/10] Habilitando I2C, SPI y GPIO...${NC}"

# Detectar archivo de configuración de boot
if [ -f /boot/firmware/config.txt ]; then
    BOOT_CONFIG="/boot/firmware/config.txt"
elif [ -f /boot/config.txt ]; then
    BOOT_CONFIG="/boot/config.txt"
else
    BOOT_CONFIG=""
fi

if [ -n "$BOOT_CONFIG" ]; then
    echo -e "${YELLOW}Configurando $BOOT_CONFIG...${NC}"

    # Habilitar I2C
    if ! grep -q "^dtparam=i2c_arm=on" "$BOOT_CONFIG"; then
        echo "dtparam=i2c_arm=on" >> "$BOOT_CONFIG"
        echo -e "${GREEN}  [+] I2C habilitado${NC}"
    else
        echo -e "${GREEN}  [OK] I2C ya estaba habilitado${NC}"
    fi

    # Habilitar SPI
    if ! grep -q "^dtparam=spi=on" "$BOOT_CONFIG"; then
        echo "dtparam=spi=on" >> "$BOOT_CONFIG"
        echo -e "${GREEN}  [+] SPI habilitado${NC}"
    else
        echo -e "${GREEN}  [OK] SPI ya estaba habilitado${NC}"
    fi

    # Habilitar I2C baudrate más alto
    if ! grep -q "^dtparam=i2c_arm_baudrate" "$BOOT_CONFIG"; then
        echo "dtparam=i2c_arm_baudrate=400000" >> "$BOOT_CONFIG"
        echo -e "${GREEN}  [+] I2C baudrate 400kHz configurado${NC}"
    fi
else
    echo -e "${YELLOW}Archivo de configuración de boot no encontrado${NC}"
fi

# Configurar módulos del kernel
echo -e "${YELLOW}Configurando módulos del kernel...${NC}"

for module in i2c-dev i2c-bcm2835 spi-bcm2835; do
    if ! grep -q "^$module" /etc/modules; then
        echo "$module" >> /etc/modules
        echo -e "${GREEN}  [+] Módulo $module agregado${NC}"
    fi
done

# Cargar módulos ahora
modprobe i2c-dev 2>/dev/null || true
modprobe i2c-bcm2835 2>/dev/null || true
modprobe spi-bcm2835 2>/dev/null || true

# Verificar I2C
if [ -e /dev/i2c-1 ]; then
    echo -e "${GREEN}  [OK] /dev/i2c-1 disponible${NC}"
else
    echo -e "${YELLOW}  [!] /dev/i2c-1 no disponible - reinicio requerido${NC}"
fi

# Configurar reglas udev
echo -e "${YELLOW}Configurando reglas udev para GPIO e I2C...${NC}"
cat > /etc/udev/rules.d/99-gpio-i2c.rules << 'UDEVEOF'
# Reglas para GPIO
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", MODE="0660", GROUP="gpio"
SUBSYSTEM=="gpio", KERNEL=="gpio*", MODE="0660", GROUP="gpio"

# Reglas para I2C
SUBSYSTEM=="i2c-dev", MODE="0660", GROUP="i2c"

# Reglas para SPI
SUBSYSTEM=="spidev", MODE="0660", GROUP="spi"

# Reglas para serial (ESP32)
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", MODE="0660", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", MODE="0660", GROUP="dialout"
UDEVEOF

# Crear grupos si no existen
for group in gpio i2c spi dialout; do
    getent group $group || groupadd $group
done

udevadm control --reload-rules 2>/dev/null || true
udevadm trigger 2>/dev/null || true

# Install Python dependencies
echo -e "${BLUE}[5/10] Instalando dependencias Python...${NC}"

# Detectar PEP 668
PIP_ARGS=""
if [ -f /usr/lib/python3*/EXTERNALLY-MANAGED ] || [ -f /usr/lib/python3.*/EXTERNALLY-MANAGED ]; then
    echo -e "${YELLOW}Detectado PEP 668, usando --break-system-packages${NC}"
    PIP_ARGS="--break-system-packages"
fi

# Dependencias básicas
pip3 install $PIP_ARGS sounddevice || true
pip3 install $PIP_ARGS luma.oled || true

# Dependencias para v3.0 (Web Server)
echo -e "${YELLOW}Instalando Flask y SocketIO...${NC}"
pip3 install $PIP_ARGS flask flask-socketio eventlet || true
pip3 install $PIP_ARGS pyserial || true

# Setup project directory
echo -e "${BLUE}[6/10] Configurando directorio del proyecto...${NC}"

# Crear estructura de directorios
mkdir -p "$INSTALL_DIR/config"
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/src/static/css"
mkdir -p "$INSTALL_DIR/src/static/js"
mkdir -p "$INSTALL_DIR/src/modules"

# Crear configuración por defecto si no existe
if [ ! -f "$INSTALL_DIR/config/settings.json" ]; then
    cat > "$INSTALL_DIR/config/settings.json" << 'CONFIGEOF'
{
    "audio": {
        "threshold": 73,
        "calibration_offset": 94,
        "sample_rate": 44100,
        "channels": 1,
        "duration": 0.1
    },
    "bluetooth": {
        "scan_duration": 10,
        "auto_scan_interval": 30,
        "use_external_adapter": true
    },
    "display": {
        "enabled": true,
        "i2c_address": "0x3C",
        "contrast": 255
    },
    "encoder": {
        "enabled": true,
        "clk_pin": 17,
        "dt_pin": 18,
        "sw_pin": 27
    },
    "attack": {
        "auto_attack": false,
        "l2cap_threads": 4,
        "rfcomm_threads": 2,
        "attack_duration": 30
    },
    "esp32": {
        "enabled": true,
        "port": "/dev/ttyUSB0",
        "baudrate": 115200
    },
    "web": {
        "host": "0.0.0.0",
        "port": 5000,
        "debug": false
    }
}
CONFIGEOF
fi

chown -R "$REAL_USER:$REAL_USER" "$INSTALL_DIR"

# Configure permissions
echo -e "${BLUE}[7/10] Configurando permisos...${NC}"
usermod -a -G bluetooth,audio,i2c,gpio,spi,dialout "$REAL_USER" 2>/dev/null || true
setcap 'cap_net_raw,cap_net_admin+eip' $(which python3) 2>/dev/null || true

# Permisos para herramientas Bluetooth
echo -e "${YELLOW}Configurando permisos para herramientas Bluetooth...${NC}"
for tool in hcitool l2ping rfcomm hcidump sdptool hciconfig bccmd; do
    if [ -f /usr/bin/$tool ]; then
        setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/$tool
        echo -e "${GREEN}  [+] $tool configurado${NC}"
    fi
done

echo -e "${GREEN}Usuario $REAL_USER agregado a grupos: bluetooth, audio, i2c, gpio, spi, dialout${NC}"

# Configurar sudoers
echo -e "${YELLOW}Configurando permisos de reinicio del servicio...${NC}"
SUDOERS_FILE="/etc/sudoers.d/volumebegone"
cat > "$SUDOERS_FILE" << SUDOERSEOF
# Permitir control del servicio volumebegone sin contraseña
$REAL_USER ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart volumebegone
$REAL_USER ALL=(ALL) NOPASSWD: /usr/bin/systemctl start volumebegone
$REAL_USER ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop volumebegone
$REAL_USER ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart masterbegone
$REAL_USER ALL=(ALL) NOPASSWD: /usr/bin/systemctl start masterbegone
$REAL_USER ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop masterbegone
$REAL_USER ALL=(ALL) NOPASSWD: /usr/bin/python3
SUDOERSEOF
chmod 440 "$SUDOERS_FILE"

# Enable Bluetooth service
systemctl enable bluetooth 2>/dev/null || true
systemctl start bluetooth 2>/dev/null || true

# Install systemd service
echo -e "${BLUE}[8/10] Instalando servicio systemd...${NC}"

# Servicio principal (masterbegone)
cat > /etc/systemd/system/masterbegone.service << SERVICEEOF
[Unit]
Description=MasterBeGone v3.0 - Hybrid Bluetooth Speaker Control
After=bluetooth.target sound.target network.target multi-user.target
Wants=bluetooth.target sound.target

[Service]
Type=simple
User=$REAL_USER
Group=$REAL_USER
WorkingDirectory=$INSTALL_DIR/src
Environment="PYTHONUNBUFFERED=1"
Environment="HOME=$REAL_HOME"
ExecStartPre=/bin/sleep 10
ExecStart=/usr/bin/python3 $INSTALL_DIR/src/masterbegone.py
ExecStopPost=-/usr/bin/pkill -f l2ping
ExecStopPost=-/usr/bin/pkill -f rfcomm
ExecStopPost=-/usr/bin/pkill -f hcidump
ExecStopPost=-/usr/bin/pkill -f hcitool
Restart=on-failure
RestartSec=30
StandardOutput=journal
StandardError=journal
SyslogIdentifier=masterbegone
TimeoutStartSec=120
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Servicio legacy (volumebegone) - para compatibilidad
cat > /etc/systemd/system/volumebegone.service << SERVICEEOF
[Unit]
Description=Volume Be Gone (Legacy) - Bluetooth Speaker Control
After=bluetooth.target sound.target network.target multi-user.target
Wants=bluetooth.target sound.target

[Service]
Type=simple
User=$REAL_USER
Group=$REAL_USER
WorkingDirectory=$INSTALL_DIR/src
Environment="PYTHONUNBUFFERED=1"
Environment="HOME=$REAL_HOME"
ExecStartPre=/bin/sleep 15
ExecStart=/usr/bin/python3 $INSTALL_DIR/src/volumeBeGone.py
ExecStopPost=-/usr/bin/pkill -f l2ping
ExecStopPost=-/usr/bin/pkill -f rfcomm
Restart=on-failure
RestartSec=30
StandardOutput=journal
StandardError=journal
SyslogIdentifier=volumebegone
TimeoutStartSec=60
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
SERVICEEOF

systemctl daemon-reload
echo -e "${GREEN}Servicios systemd instalados${NC}"

# Crear script de inicio rápido
echo -e "${BLUE}[9/10] Creando scripts auxiliares...${NC}"

cat > "$INSTALL_DIR/start.sh" << 'STARTEOF'
#!/bin/bash
# Quick start script
cd "$(dirname "$0")/src"
sudo python3 masterbegone.py "$@"
STARTEOF
chmod +x "$INSTALL_DIR/start.sh"

cat > "$INSTALL_DIR/start-web-only.sh" << 'STARTEOF'
#!/bin/bash
# Start in web-only mode (no OLED/encoder)
cd "$(dirname "$0")/src"
sudo python3 masterbegone.py --web-only "$@"
STARTEOF
chmod +x "$INSTALL_DIR/start-web-only.sh"

cat > "$INSTALL_DIR/start-headless.sh" << 'STARTEOF'
#!/bin/bash
# Start without display
cd "$(dirname "$0")/src"
sudo python3 masterbegone.py --headless "$@"
STARTEOF
chmod +x "$INSTALL_DIR/start-headless.sh"

chown -R "$REAL_USER:$REAL_USER" "$INSTALL_DIR"

# Resumen final
echo -e "${BLUE}[10/10] Verificación final...${NC}"

echo ""
echo -e "${YELLOW}Verificando componentes instalados:${NC}"

# Python
python3 --version && echo -e "  ${GREEN}[OK] Python3${NC}" || echo -e "  ${RED}[!] Python3${NC}"

# Flask
python3 -c "import flask" 2>/dev/null && echo -e "  ${GREEN}[OK] Flask${NC}" || echo -e "  ${RED}[!] Flask${NC}"

# SocketIO
python3 -c "import flask_socketio" 2>/dev/null && echo -e "  ${GREEN}[OK] Flask-SocketIO${NC}" || echo -e "  ${RED}[!] Flask-SocketIO${NC}"

# luma.oled
python3 -c "from luma.oled.device import ssd1306" 2>/dev/null && echo -e "  ${GREEN}[OK] luma.oled${NC}" || echo -e "  ${RED}[!] luma.oled${NC}"

# sounddevice
python3 -c "import sounddevice" 2>/dev/null && echo -e "  ${GREEN}[OK] sounddevice${NC}" || echo -e "  ${RED}[!] sounddevice${NC}"

# pyserial
python3 -c "import serial" 2>/dev/null && echo -e "  ${GREEN}[OK] pyserial${NC}" || echo -e "  ${RED}[!] pyserial${NC}"

# hostapd
command -v hostapd &>/dev/null && echo -e "  ${GREEN}[OK] hostapd${NC}" || echo -e "  ${RED}[!] hostapd${NC}"

# dnsmasq
command -v dnsmasq &>/dev/null && echo -e "  ${GREEN}[OK] dnsmasq${NC}" || echo -e "  ${RED}[!] dnsmasq${NC}"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗"
echo "║         ¡Instalación Completada!               ║"
echo "╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Instalado para usuario:${NC} $REAL_USER"
echo -e "${YELLOW}Directorio:${NC} $INSTALL_DIR"
echo ""
echo -e "${YELLOW}Próximos pasos:${NC}"
echo ""
echo "  1. Reiniciar para aplicar cambios de kernel:"
echo "     ${BLUE}sudo reboot${NC}"
echo ""
echo "  2. Configurar Access Point (opcional):"
echo "     ${BLUE}sudo bash $INSTALL_DIR/scripts/setup_ap.sh${NC}"
echo ""
echo "  3. Probar el sistema:"
echo "     ${BLUE}cd $INSTALL_DIR && ./start.sh${NC}"
echo ""
echo "  4. Habilitar inicio automático:"
echo "     ${BLUE}sudo systemctl enable masterbegone${NC}"
echo ""
echo -e "${YELLOW}Modos de ejecución:${NC}"
echo "  Normal (OLED + Web):  ./start.sh"
echo "  Solo Web:             ./start-web-only.sh"
echo "  Sin display:          ./start-headless.sh"
echo ""
echo -e "${YELLOW}Servicios systemd:${NC}"
echo "  masterbegone  - Sistema completo v3.0"
echo "  volumebegone  - Modo legacy (solo OLED)"
echo ""
