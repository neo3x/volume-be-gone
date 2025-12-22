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
    bluez-tools \
    bluez-hcidump \
    i2c-tools \
    git python3-venv \
    python3-pillow \
    python3-psutil \
    libportaudio2

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
    echo -e "${YELLOW}  [*] Intentando instalar paquetes adicionales...${NC}"
    apt-get install -y bluez bluez-tools bluez-hcidump 2>/dev/null || true
fi

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
echo -e "${YELLOW}[4/8] Enabling I2C, SPI and GPIO interfaces...${NC}"

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

    # Habilitar I2C baudrate más alto (opcional, para pantalla OLED)
    if ! grep -q "^dtparam=i2c_arm_baudrate" "$BOOT_CONFIG"; then
        echo "dtparam=i2c_arm_baudrate=400000" >> "$BOOT_CONFIG"
        echo -e "${GREEN}  [+] I2C baudrate 400kHz configurado${NC}"
    fi
else
    echo -e "${YELLOW}Archivo de configuración de boot no encontrado${NC}"
fi

# Configurar módulos del kernel para que carguen al inicio
echo -e "${YELLOW}Configurando módulos del kernel...${NC}"

# I2C
if ! grep -q "^i2c-dev" /etc/modules; then
    echo "i2c-dev" >> /etc/modules
    echo -e "${GREEN}  [+] Módulo i2c-dev agregado${NC}"
fi

if ! grep -q "^i2c-bcm2835" /etc/modules; then
    echo "i2c-bcm2835" >> /etc/modules
    echo -e "${GREEN}  [+] Módulo i2c-bcm2835 agregado${NC}"
fi

# SPI
if ! grep -q "^spi-bcm2835" /etc/modules; then
    echo "spi-bcm2835" >> /etc/modules
    echo -e "${GREEN}  [+] Módulo spi-bcm2835 agregado${NC}"
fi

# GPIO (para el encoder)
if ! grep -q "^gpio-bcm2835" /etc/modules 2>/dev/null; then
    echo "gpio-bcm2835" >> /etc/modules 2>/dev/null || true
fi

# Cargar módulos ahora (sin reiniciar)
echo -e "${YELLOW}Cargando módulos...${NC}"
modprobe i2c-dev 2>/dev/null || true
modprobe i2c-bcm2835 2>/dev/null || true
modprobe spi-bcm2835 2>/dev/null || true

# Verificar que I2C está funcionando
if [ -e /dev/i2c-1 ]; then
    echo -e "${GREEN}  [OK] /dev/i2c-1 disponible${NC}"
else
    echo -e "${YELLOW}  [!] /dev/i2c-1 no disponible - reinicio requerido${NC}"
fi

# Configurar permisos de dispositivos GPIO y I2C
echo -e "${YELLOW}Configurando reglas udev para GPIO e I2C...${NC}"
cat > /etc/udev/rules.d/99-gpio-i2c.rules << 'UDEVEOF'
# Reglas para GPIO
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", MODE="0660", GROUP="gpio"
SUBSYSTEM=="gpio", KERNEL=="gpio*", MODE="0660", GROUP="gpio"

# Reglas para I2C
SUBSYSTEM=="i2c-dev", MODE="0660", GROUP="i2c"

# Reglas para SPI
SUBSYSTEM=="spidev", MODE="0660", GROUP="spi"
UDEVEOF

# Crear grupos si no existen
getent group gpio || groupadd gpio
getent group i2c || groupadd i2c
getent group spi || groupadd spi

# Recargar reglas udev
udevadm control --reload-rules 2>/dev/null || true
udevadm trigger 2>/dev/null || true

# Install Python dependencies
echo -e "${YELLOW}[5/8] Installing Python dependencies...${NC}"

# Instalar dependencias pip (no están en repos de Trixie)
PIP_ARGS=""
if [ -f /usr/lib/python3*/EXTERNALLY-MANAGED ] || [ -f /usr/lib/python3.*/EXTERNALLY-MANAGED ]; then
    echo -e "${YELLOW}Detectado PEP 668, usando --break-system-packages${NC}"
    PIP_ARGS="--break-system-packages"
fi

# sounddevice (no está en repos de Trixie)
pip3 install $PIP_ARGS sounddevice || true

# luma.oled para display SSD1306 (reemplaza Adafruit-SSD1306, compatible con Trixie)
pip3 install $PIP_ARGS luma.oled || true

# Setup project directory
echo -e "${YELLOW}[6/8] Setting up project directory...${NC}"

# Create default config if needed
if [ ! -f "$INSTALL_DIR/config.json" ]; then
    echo '{"threshold_db": 70, "calibration_offset": 94, "use_external_adapter": true}' > "$INSTALL_DIR/config.json"
fi
chown -R "$REAL_USER:$REAL_USER" "$INSTALL_DIR"

# Configure permissions
echo -e "${YELLOW}[7/8] Configuring permissions...${NC}"
usermod -a -G bluetooth,audio,i2c,gpio,spi,dialout "$REAL_USER" 2>/dev/null || true
setcap 'cap_net_raw,cap_net_admin+eip' $(which python3) 2>/dev/null || true

# Configurar permisos para herramientas Bluetooth (requieren CAP_NET_RAW y CAP_NET_ADMIN)
echo -e "${YELLOW}Configurando permisos para herramientas Bluetooth...${NC}"

# hcitool (para scanning BLE y Classic)
if [ -f /usr/bin/hcitool ]; then
    setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/hcitool
    echo -e "${GREEN}  [+] hcitool configurado${NC}"
fi

# l2ping (para ataques L2CAP)
if [ -f /usr/bin/l2ping ]; then
    setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/l2ping
    echo -e "${GREEN}  [+] l2ping configurado${NC}"
fi

# rfcomm (para ataques RFCOMM)
if [ -f /usr/bin/rfcomm ]; then
    setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/rfcomm
    echo -e "${GREEN}  [+] rfcomm configurado${NC}"
fi

# hcidump (para captura de tráfico)
if [ -f /usr/bin/hcidump ]; then
    setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/hcidump
    echo -e "${GREEN}  [+] hcidump configurado${NC}"
fi

# sdptool (para enumeración de servicios)
if [ -f /usr/bin/sdptool ]; then
    setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/sdptool
    echo -e "${GREEN}  [+] sdptool configurado${NC}"
fi

# hciconfig (para configuración de adaptadores)
if [ -f /usr/bin/hciconfig ]; then
    setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/hciconfig
    echo -e "${GREEN}  [+] hciconfig configurado${NC}"
fi

# bccmd (para adaptadores CSR - opcional)
if [ -f /usr/bin/bccmd ]; then
    setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/bccmd
    echo -e "${GREEN}  [+] bccmd configurado (adaptadores CSR)${NC}"
fi

echo -e "${GREEN}Usuario $REAL_USER agregado a grupos: bluetooth, audio, i2c, gpio, spi, dialout${NC}"

# Configurar sudoers para permitir reinicio del servicio sin contraseña
echo -e "${YELLOW}Configurando permisos para reinicio del servicio...${NC}"
SUDOERS_FILE="/etc/sudoers.d/volumebegone"
cat > "$SUDOERS_FILE" << SUDOERSEOF
# Permitir reinicio del servicio volumebegone sin contraseña
$REAL_USER ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart volumebegone
$REAL_USER ALL=(ALL) NOPASSWD: /usr/bin/systemctl start volumebegone
$REAL_USER ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop volumebegone
$REAL_USER ALL=(ALL) NOPASSWD: /usr/bin/python3
SUDOERSEOF
chmod 440 "$SUDOERS_FILE"
echo -e "${GREEN}  [+] Permisos de reinicio configurados${NC}"

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
ExecStopPost=-/usr/bin/pkill -f hcidump
ExecStopPost=-/usr/bin/pkill -f hcitool
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
