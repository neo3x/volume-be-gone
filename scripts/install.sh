#!/bin/bash
#
# Volume Be Gone - Automated Installer
# Run with: sudo bash install.sh
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Volume Be Gone - Installer${NC}"
echo -e "${GREEN}=====================================${NC}"
echo

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   echo "Please run: sudo bash install.sh"
   exit 1
fi

# Detectar usuario real (no root)
if [ -n "$SUDO_USER" ]; then
    REAL_USER="$SUDO_USER"
else
    REAL_USER=$(logname 2>/dev/null || echo "")
    if [ -z "$REAL_USER" ] || [ "$REAL_USER" = "root" ]; then
        echo -e "${RED}Error: No se puede detectar el usuario${NC}"
        echo "Por favor ejecuta: sudo -u tu_usuario bash install.sh"
        read -p "Ingresa tu nombre de usuario: " REAL_USER
    fi
fi

REAL_HOME=$(eval echo ~$REAL_USER)

# Detectar directorio del proyecto (donde está el script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_DIR="$SCRIPT_DIR"

echo -e "${YELLOW}Usuario detectado: $REAL_USER${NC}"
echo -e "${YELLOW}Directorio del proyecto: $INSTALL_DIR${NC}"
echo

# Detectar distribución
echo -e "${YELLOW}[1/8] Detectando sistema...${NC}"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    VERSION=$VERSION_CODENAME
    echo -e "${GREEN}Detectado: $DISTRO $VERSION${NC}"
fi

# Update system
echo -e "${YELLOW}[2/8] Updating system packages...${NC}"
apt-get update

# Install system dependencies
echo -e "${YELLOW}[3/8] Installing system dependencies...${NC}"

# Paquetes base
apt-get install -y \
    python3-pip python3-dev python3-numpy python3-scipy \
    bluetooth bluez libbluetooth-dev \
    i2c-tools \
    git python3-venv \
    python3-pillow \
    python3-psutil \
    libportaudio2

# PortAudio dev para compilar
apt-get install -y portaudio19-dev 2>/dev/null || apt-get install -y libportaudio-dev 2>/dev/null || true

# SMBus
apt-get install -y python3-smbus 2>/dev/null || apt-get install -y python3-smbus2 2>/dev/null || true

# BLAS/ATLAS
apt-get install -y libopenblas-dev 2>/dev/null || apt-get install -y libatlas-base-dev 2>/dev/null || true

# GPIO - en Trixie puede ser lgpio o gpiod
apt-get install -y python3-rpi.gpio 2>/dev/null || apt-get install -y python3-lgpio python3-gpiod 2>/dev/null || true

# Bluetooth Python desde repos (NO pip)
apt-get install -y python3-bluez 2>/dev/null || true

# Enable interfaces
echo -e "${YELLOW}[4/8] Enabling I2C and SPI interfaces...${NC}"
if command -v raspi-config &> /dev/null; then
    raspi-config nonint do_i2c 0 2>/dev/null || true
    raspi-config nonint do_spi 0 2>/dev/null || true
else
    echo -e "${YELLOW}raspi-config no encontrado, habilitando manualmente...${NC}"
    modprobe i2c-dev 2>/dev/null || true
    modprobe spi-bcm2835 2>/dev/null || true
    # Asegurar que se carguen al inicio
    grep -q "i2c-dev" /etc/modules || echo "i2c-dev" >> /etc/modules
fi

# Install Python dependencies
echo -e "${YELLOW}[5/8] Installing Python dependencies...${NC}"

# Instalar sounddevice y Adafruit con pip (no están en repos de Trixie)
PIP_ARGS=""
if [ -f /usr/lib/python3*/EXTERNALLY-MANAGED ] || [ -f /usr/lib/python3.*/EXTERNALLY-MANAGED ]; then
    echo -e "${YELLOW}Detectado PEP 668, usando --break-system-packages${NC}"
    PIP_ARGS="--break-system-packages"
fi

# sounddevice (no está en repos de Trixie)
pip3 install $PIP_ARGS sounddevice || true

# Adafruit SSD1306 y GPIO
pip3 install $PIP_ARGS Adafruit-SSD1306 Adafruit-GPIO || true

# Setup project directory
echo -e "${YELLOW}[6/8] Setting up project directory...${NC}"

# Create default config if needed
if [ ! -f "$INSTALL_DIR/config.json" ]; then
    echo '{"threshold_db": 70, "calibration_offset": 94, "use_external_adapter": true}' > "$INSTALL_DIR/config.json"
fi
chown -R "$REAL_USER:$REAL_USER" "$INSTALL_DIR"

# Configure permissions
echo -e "${YELLOW}[7/8] Configuring permissions...${NC}"
usermod -a -G bluetooth,audio,i2c,gpio "$REAL_USER" 2>/dev/null || true
usermod -a -G dialout "$REAL_USER" 2>/dev/null || true
setcap 'cap_net_raw,cap_net_admin+eip' $(which python3) 2>/dev/null || true

# Enable Bluetooth service
systemctl enable bluetooth 2>/dev/null || true
systemctl start bluetooth 2>/dev/null || true

# Install systemd service
echo -e "${YELLOW}[8/8] Installing systemd service...${NC}"
SERVICE_FILE="/etc/systemd/system/volumebegone.service"

cat > "$SERVICE_FILE" << SERVICEEOF
[Unit]
Description=Volume Be Gone - Bluetooth Speaker Control by Volume Level
After=bluetooth.target sound.target network.target multi-user.target
Wants=bluetooth.target sound.target

[Service]
Type=simple
User=$REAL_USER
Group=$REAL_USER
WorkingDirectory=$INSTALL_DIR
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
echo -e "${GREEN}Systemd service installed${NC}"

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Installation completed successfully${NC}"
echo -e "${GREEN}=====================================${NC}"
echo
echo "Instalado para usuario: $REAL_USER"
echo "Directorio: $INSTALL_DIR"
echo
echo "Next steps:"
echo "1. Reboot: sudo reboot"
echo "2. Test: python3 $INSTALL_DIR/src/volumeBeGone.py"
echo "3. Auto-start: sudo systemctl enable volumebegone"
echo
