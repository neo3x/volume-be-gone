#!/bin/bash
#
# Volume Be Gone v3.0 - Setup Access Point
#
# Configura la Raspberry Pi como Access Point WiFi independiente.
# Permite conectarse directamente desde un celular sin router.
#
# Author: Francisco Ortiz Rojas
# Version: 3.0
#

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuración por defecto
AP_SSID="VolumeBeGone"
AP_PASS="begone2025"
AP_CHANNEL="7"
AP_IP="192.168.4.1"
AP_SUBNET="192.168.4.0/24"
DHCP_RANGE_START="192.168.4.10"
DHCP_RANGE_END="192.168.4.50"
WLAN_INTERFACE="wlan0"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════╗"
echo "║     Volume Be Gone v3.0 - Access Point Setup   ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: Este script debe ejecutarse como root${NC}"
    echo "Uso: sudo $0"
    exit 1
fi

# Preguntar configuración
echo -e "${YELLOW}Configuración del Access Point:${NC}"
echo ""

read -p "SSID [$AP_SSID]: " input
AP_SSID="${input:-$AP_SSID}"

read -p "Contraseña [$AP_PASS]: " input
AP_PASS="${input:-$AP_PASS}"

# Validar contraseña (mínimo 8 caracteres para WPA2)
if [ ${#AP_PASS} -lt 8 ]; then
    echo -e "${RED}Error: La contraseña debe tener al menos 8 caracteres${NC}"
    exit 1
fi

read -p "Canal WiFi (1-11) [$AP_CHANNEL]: " input
AP_CHANNEL="${input:-$AP_CHANNEL}"

read -p "IP del AP [$AP_IP]: " input
AP_IP="${input:-$AP_IP}"

echo ""
echo -e "${BLUE}Configuración seleccionada:${NC}"
echo "  SSID: $AP_SSID"
echo "  Pass: $AP_PASS"
echo "  Canal: $AP_CHANNEL"
echo "  IP: $AP_IP"
echo ""

read -p "¿Continuar? (s/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Cancelado."
    exit 0
fi

echo ""
echo -e "${BLUE}[1/6] Instalando paquetes necesarios...${NC}"
apt-get update
apt-get install -y hostapd dnsmasq iptables

echo -e "${BLUE}[2/6] Deteniendo servicios...${NC}"
systemctl stop hostapd 2>/dev/null || true
systemctl stop dnsmasq 2>/dev/null || true

echo -e "${BLUE}[3/6] Configurando interfaz WiFi...${NC}"

# Deshabilitar wpa_supplicant para wlan0
systemctl stop wpa_supplicant 2>/dev/null || true

# Configurar IP estática para wlan0
cat > /etc/dhcpcd.conf.d/ap.conf << EOF
# Volume Be Gone - Access Point Configuration
interface $WLAN_INTERFACE
    static ip_address=$AP_IP/24
    nohook wpa_supplicant
EOF

# Agregar include si no existe
if ! grep -q "include /etc/dhcpcd.conf.d" /etc/dhcpcd.conf 2>/dev/null; then
    echo "" >> /etc/dhcpcd.conf
    echo "# Include additional configs" >> /etc/dhcpcd.conf
    echo "include /etc/dhcpcd.conf.d/*.conf" >> /etc/dhcpcd.conf
fi

# Crear directorio si no existe
mkdir -p /etc/dhcpcd.conf.d

echo -e "${BLUE}[4/6] Configurando hostapd...${NC}"

# Backup de config existente
[ -f /etc/hostapd/hostapd.conf ] && cp /etc/hostapd/hostapd.conf /etc/hostapd/hostapd.conf.bak

cat > /etc/hostapd/hostapd.conf << EOF
# Volume Be Gone v3.0 - hostapd configuration
interface=$WLAN_INTERFACE
driver=nl80211
ssid=$AP_SSID
hw_mode=g
channel=$AP_CHANNEL
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=$AP_PASS
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
country_code=CL
EOF

# Configurar hostapd para usar el archivo de configuración
if ! grep -q "DAEMON_CONF" /etc/default/hostapd 2>/dev/null; then
    echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' >> /etc/default/hostapd
else
    sed -i 's|^#*DAEMON_CONF=.*|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd
fi

echo -e "${BLUE}[5/6] Configurando dnsmasq (DHCP)...${NC}"

# Backup de config existente
[ -f /etc/dnsmasq.conf ] && cp /etc/dnsmasq.conf /etc/dnsmasq.conf.bak

cat > /etc/dnsmasq.conf << EOF
# Volume Be Gone v3.0 - dnsmasq configuration

# Interfaz
interface=$WLAN_INTERFACE

# Rango DHCP
dhcp-range=$DHCP_RANGE_START,$DHCP_RANGE_END,255.255.255.0,24h

# Gateway
dhcp-option=3,$AP_IP

# DNS (usar el mismo AP)
dhcp-option=6,$AP_IP

# Dominio local
domain=volumebegone.local
local=/volumebegone.local/

# Resolver volumebegone.local a la IP del AP
address=/volumebegone.local/$AP_IP

# No leer /etc/resolv.conf
no-resolv

# Servidor DNS upstream (Google)
server=8.8.8.8
server=8.8.4.4

# Logging
log-queries
log-dhcp
EOF

echo -e "${BLUE}[6/6] Habilitando servicios...${NC}"

# Desbloquear WiFi si está bloqueado
rfkill unblock wlan 2>/dev/null || true

# Habilitar IP forwarding (por si se quiere compartir internet en el futuro)
echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/90-ap.conf
sysctl -w net.ipv4.ip_forward=1

# Reiniciar dhcpcd
systemctl restart dhcpcd

# Esperar a que la interfaz esté lista
sleep 2

# Desmascarar y habilitar servicios
systemctl unmask hostapd
systemctl enable hostapd
systemctl enable dnsmasq

# Iniciar servicios
systemctl start hostapd
systemctl start dnsmasq

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗"
echo "║         ¡Access Point Configurado!             ║"
echo "╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Configuración:${NC}"
echo "  Red WiFi: $AP_SSID"
echo "  Contraseña: $AP_PASS"
echo "  IP del servidor: $AP_IP"
echo ""
echo -e "${YELLOW}Para conectar:${NC}"
echo "  1. Busca la red '$AP_SSID' en tu celular"
echo "  2. Conecta con la contraseña '$AP_PASS'"
echo "  3. Abre el navegador en: http://$AP_IP:5000"
echo "     o: http://volumebegone.local:5000"
echo ""
echo -e "${YELLOW}Comandos útiles:${NC}"
echo "  Ver estado:   sudo systemctl status hostapd"
echo "  Ver clientes: cat /var/lib/misc/dnsmasq.leases"
echo "  Reiniciar AP: sudo systemctl restart hostapd dnsmasq"
echo ""
echo -e "${BLUE}Nota: El AP se iniciará automáticamente al encender.${NC}"
echo ""

# Verificar estado
echo -e "${YELLOW}Estado de los servicios:${NC}"
systemctl is-active --quiet hostapd && echo -e "  hostapd: ${GREEN}activo${NC}" || echo -e "  hostapd: ${RED}inactivo${NC}"
systemctl is-active --quiet dnsmasq && echo -e "  dnsmasq: ${GREEN}activo${NC}" || echo -e "  dnsmasq: ${RED}inactivo${NC}"

# Mostrar IP asignada
echo ""
echo -e "${YELLOW}IP asignada a $WLAN_INTERFACE:${NC}"
ip addr show $WLAN_INTERFACE | grep "inet " || echo "  (esperando...)"

echo ""
echo -e "${GREEN}¡Listo! Reinicia para aplicar todos los cambios: sudo reboot${NC}"
