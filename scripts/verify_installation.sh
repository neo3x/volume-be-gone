#!/bin/bash
#
# Volume Be Gone - Installation Verification Script
# Verifica que todas las herramientas y dependencias estén instaladas correctamente
#

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Volume Be Gone - Verificación${NC}"
echo -e "${BLUE}=====================================${NC}"
echo

# Contadores
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

check_command() {
    local cmd=$1
    local description=$2
    local required=$3

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $description ($cmd)"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        if [ "$required" = "required" ]; then
            echo -e "${RED}✗${NC} $description ($cmd) - REQUERIDO"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        else
            echo -e "${YELLOW}⚠${NC} $description ($cmd) - OPCIONAL"
        fi
        return 1
    fi
}

check_python_module() {
    local module=$1
    local description=$2
    local required=$3

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if python3 -c "import $module" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description (Python: $module)"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        if [ "$required" = "required" ]; then
            echo -e "${RED}✗${NC} $description (Python: $module) - REQUERIDO"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        else
            echo -e "${YELLOW}⚠${NC} $description (Python: $module) - OPCIONAL"
        fi
        return 1
    fi
}

check_capability() {
    local cmd=$1
    local description=$2

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [ -f "$cmd" ]; then
        caps=$(getcap "$cmd" 2>/dev/null)
        if [[ $caps == *"cap_net_raw"* ]] && [[ $caps == *"cap_net_admin"* ]]; then
            echo -e "${GREEN}✓${NC} $description tiene permisos correctos"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            return 0
        else
            echo -e "${RED}✗${NC} $description sin permisos (necesita cap_net_raw,cap_net_admin)"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            return 1
        fi
    else
        echo -e "${YELLOW}⚠${NC} $description no encontrado"
        return 1
    fi
}

echo -e "${YELLOW}[1/5] Verificando herramientas Bluetooth...${NC}"
check_command "hcitool" "HCI Tool (scanning Classic/BLE)" "required"
check_command "l2ping" "L2CAP Ping (ataque L2CAP)" "required"
check_command "rfcomm" "RFCOMM (ataque RFCOMM)" "required"
check_command "sdptool" "SDP Tool (enumeración servicios)" "required"
check_command "hcidump" "HCI Dump (captura tráfico)" "optional"
check_command "hciconfig" "HCI Config (configuración adaptador)" "required"
check_command "bccmd" "BCCMD (adaptadores CSR)" "optional"
echo

echo -e "${YELLOW}[2/5] Verificando módulos Python...${NC}"
check_python_module "bluetooth" "PyBluez (Bluetooth Python)" "required"
check_python_module "sounddevice" "SoundDevice (captura audio)" "required"
check_python_module "numpy" "NumPy (procesamiento audio)" "required"
check_python_module "RPi.GPIO" "RPi.GPIO (GPIO control)" "required"
check_python_module "luma.oled" "Luma OLED (display SSD1306)" "required"
check_python_module "PIL" "Pillow (imágenes)" "required"
echo

echo -e "${YELLOW}[3/5] Verificando permisos de herramientas...${NC}"
check_capability "/usr/bin/hcitool" "hcitool"
check_capability "/usr/bin/l2ping" "l2ping"
check_capability "/usr/bin/rfcomm" "rfcomm"
check_capability "/usr/bin/sdptool" "sdptool"
check_capability "/usr/bin/hciconfig" "hciconfig"
if [ -f /usr/bin/hcidump ]; then
    check_capability "/usr/bin/hcidump" "hcidump"
fi
echo

echo -e "${YELLOW}[4/5] Verificando adaptadores Bluetooth...${NC}"
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if hciconfig 2>/dev/null | grep -q "hci"; then
    adapters=$(hciconfig 2>/dev/null | grep -c "^hci")
    echo -e "${GREEN}✓${NC} Adaptadores Bluetooth detectados: $adapters"
    hciconfig 2>/dev/null | grep "^hci" | while read line; do
        echo "  - $line"
    done
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${RED}✗${NC} No se detectaron adaptadores Bluetooth"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi
echo

echo -e "${YELLOW}[5/5] Verificando dispositivos I2C...${NC}"
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if [ -e /dev/i2c-1 ]; then
    echo -e "${GREEN}✓${NC} /dev/i2c-1 disponible (para display OLED)"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))

    # Intentar detectar dispositivo en 0x3C (SSD1306)
    if command -v i2cdetect &> /dev/null; then
        i2c_devices=$(i2cdetect -y 1 2>/dev/null | grep -E "3c|3d" | wc -l)
        if [ $i2c_devices -gt 0 ]; then
            echo -e "${GREEN}  ✓${NC} Display OLED detectado en bus I2C"
        else
            echo -e "${YELLOW}  ⚠${NC} No se detectó display OLED (0x3C o 0x3D)"
        fi
    fi
else
    echo -e "${RED}✗${NC} /dev/i2c-1 no disponible - reinicio requerido"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi
echo

# Resumen
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}RESUMEN${NC}"
echo -e "${BLUE}=====================================${NC}"
echo -e "Total de verificaciones: $TOTAL_CHECKS"
echo -e "${GREEN}Pasadas: $PASSED_CHECKS${NC}"
if [ $FAILED_CHECKS -gt 0 ]; then
    echo -e "${RED}Fallidas: $FAILED_CHECKS${NC}"
fi
echo

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}✓ TODAS LAS VERIFICACIONES PASARON${NC}"
    echo -e "${GREEN}El sistema está listo para funcionar${NC}"
    echo
    echo "Siguiente paso:"
    echo "  sudo python3 src/volumeBeGone.py"
    exit 0
else
    echo -e "${RED}✗ HAY VERIFICACIONES FALLIDAS${NC}"
    echo
    echo "Soluciones:"
    echo "  1. Ejecutar instalador: sudo bash scripts/install.sh"
    echo "  2. Verificar adaptador Bluetooth conectado"
    echo "  3. Reiniciar sistema: sudo reboot"
    exit 1
fi
