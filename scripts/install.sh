#/bin/bash 
# 
# Volume Be Gone - Automated Installer 
# Run with: sudo bash install.sh 
# 
 
set -e  # Exit on error 
 
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
 
# Update system 
echo -e "${YELLOW}[1/8] Updating system packages...${NC}" 
apt-get update 
apt-get upgrade -y 
 
# Install system dependencies 
echo -e "${YELLOW}[2/8] Installing system dependencies...${NC}" 
apt-get install -y \ 
    python3-pip python3-dev python3-numpy \ 
    bluetooth bluez libbluetooth-dev \ 
    python3-smbus i2c-tools \ 
    portaudio19-dev python3-pyaudio \ 
    libatlas-base-dev python3-pil \ 
    git python3-venv 
 
# Enable interfaces 
echo -e "${YELLOW}[3/8] Enabling I2C and SPI interfaces...${NC}" 
raspi-config nonint do_i2c 0 
raspi-config nonint do_spi 0 
 
# Install Python dependencies 
echo -e "${YELLOW}[4/8] Installing Python dependencies...${NC}" 
pip3 install --upgrade pip 
pip3 install -r requirements.txt 
 
# Create project directory 
echo -e "${YELLOW}[5/8] Creating project directory...${NC}" 
mkdir -p /home/pi/volumebegone 
cp src/volumeBeGone.py /home/pi/volumebegone/ 
cp -r resources/images /home/pi/volumebegone/ 
cp src/config.json.template /home/pi/volumebegone/config.json 
chown -R pi:pi /home/pi/volumebegone 
 
# Configure permissions 
echo -e "${YELLOW}[6/8] Configuring permissions...${NC}" 
usermod -a -G bluetooth,audio,i2c,gpio pi 
setcap 'cap_net_raw,cap_net_admin+eip' $(which python3) 
 
# Enable Bluetooth service 
echo -e "${YELLOW}[7/8] Enabling services...${NC}" 
systemctl enable bluetooth 
systemctl start bluetooth 
 
# Install systemd service 
echo -e "${YELLOW}[8/8] Installing systemd service...${NC}" 
if [ -f "scripts/volumebegone.service" ]; then 
    cp scripts/volumebegone.service /etc/systemd/system/ 
    systemctl daemon-reload 
    echo -e "${GREEN}Systemd service installed${NC}" 
    echo "To enable auto-start: sudo systemctl enable volumebegone" 
fi 
 
echo -e "${GREEN}=====================================${NC}" 
echo -e "${GREEN}Installation completed successfully${NC}" 
echo -e "${GREEN}=====================================${NC}" 
echo 
echo "Next steps:" 
echo "1. Reboot your Raspberry Pi: sudo reboot" 
echo "2. Test the installation: sudo python3 /home/pi/volumebegone/volumeBeGone.py" 
echo "3. Enable auto-start (optional): sudo systemctl enable volumebegone" 
echo 
