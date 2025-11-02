#!/bin/bash
#
# Volume Be Gone - Auto-Start Manager
# Facilita habilitar/deshabilitar el inicio automático
#

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SERVICE_NAME="volumebegone.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"

# Banner
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Volume Be Gone - Auto-Start Manager${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Verificar si se ejecuta como root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Este script debe ejecutarse como root${NC}"
   echo "Usa: sudo bash autostart.sh"
   exit 1
fi

# Función para mostrar el estado actual
show_status() {
    echo -e "${YELLOW}Estado actual:${NC}"

    if [ -f "$SERVICE_FILE" ]; then
        echo -e "  Servicio instalado: ${GREEN}SÍ${NC}"

        if systemctl is-enabled $SERVICE_NAME &>/dev/null; then
            echo -e "  Auto-inicio: ${GREEN}HABILITADO${NC}"
        else
            echo -e "  Auto-inicio: ${RED}DESHABILITADO${NC}"
        fi

        if systemctl is-active $SERVICE_NAME &>/dev/null; then
            echo -e "  Estado: ${GREEN}EJECUTANDO${NC}"
        else
            echo -e "  Estado: ${RED}DETENIDO${NC}"
        fi
    else
        echo -e "  Servicio instalado: ${RED}NO${NC}"
        echo -e "  ${YELLOW}Ejecuta 'sudo bash install.sh' primero${NC}"
    fi
    echo ""
}

# Función para habilitar auto-inicio
enable_autostart() {
    echo -e "${YELLOW}Habilitando auto-inicio...${NC}"

    if [ ! -f "$SERVICE_FILE" ]; then
        echo -e "${RED}Error: Servicio no instalado${NC}"
        echo "Ejecuta 'sudo bash install.sh' primero"
        exit 1
    fi

    systemctl daemon-reload
    systemctl enable $SERVICE_NAME

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Auto-inicio habilitado${NC}"
        echo ""
        echo "El servicio se iniciará automáticamente al encender la Raspberry Pi"
        echo ""
        echo "Comandos útiles:"
        echo "  Iniciar ahora:  sudo systemctl start volumebegone"
        echo "  Ver estado:     sudo systemctl status volumebegone"
        echo "  Ver logs:       sudo journalctl -u volumebegone -f"
    else
        echo -e "${RED}✗ Error al habilitar auto-inicio${NC}"
        exit 1
    fi
}

# Función para deshabilitar auto-inicio
disable_autostart() {
    echo -e "${YELLOW}Deshabilitando auto-inicio...${NC}"

    systemctl disable $SERVICE_NAME

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Auto-inicio deshabilitado${NC}"
        echo ""
        echo "El servicio NO se iniciará al encender la Raspberry Pi"
        echo "Puedes iniciarlo manualmente con:"
        echo "  sudo python3 /home/pi/volumebegone/volumeBeGone.py"
    else
        echo -e "${RED}✗ Error al deshabilitar auto-inicio${NC}"
        exit 1
    fi
}

# Función para iniciar el servicio
start_service() {
    echo -e "${YELLOW}Iniciando servicio...${NC}"
    systemctl start $SERVICE_NAME

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Servicio iniciado${NC}"
        sleep 2
        systemctl status $SERVICE_NAME --no-pager
    else
        echo -e "${RED}✗ Error al iniciar servicio${NC}"
        exit 1
    fi
}

# Función para detener el servicio
stop_service() {
    echo -e "${YELLOW}Deteniendo servicio...${NC}"
    systemctl stop $SERVICE_NAME

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Servicio detenido${NC}"
    else
        echo -e "${RED}✗ Error al detener servicio${NC}"
        exit 1
    fi
}

# Función para ver logs en tiempo real
view_logs() {
    echo -e "${YELLOW}Mostrando logs en tiempo real...${NC}"
    echo -e "${YELLOW}(Presiona Ctrl+C para salir)${NC}"
    echo ""
    sleep 2
    journalctl -u $SERVICE_NAME -f
}

# Menú principal
show_status

echo "Opciones:"
echo "  1) Habilitar auto-inicio al encender"
echo "  2) Deshabilitar auto-inicio"
echo "  3) Iniciar servicio ahora"
echo "  4) Detener servicio"
echo "  5) Ver logs en tiempo real"
echo "  6) Ver estado del servicio"
echo "  0) Salir"
echo ""
read -p "Selecciona una opción [0-6]: " option

case $option in
    1)
        enable_autostart
        ;;
    2)
        disable_autostart
        ;;
    3)
        start_service
        ;;
    4)
        stop_service
        ;;
    5)
        view_logs
        ;;
    6)
        systemctl status $SERVICE_NAME --no-pager
        ;;
    0)
        echo -e "${GREEN}Saliendo...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Operación completada${NC}"
