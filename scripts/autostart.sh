#!/bin/bash
#
# Volume Be Gone v3.0 - Auto-Start Manager
#
# Facilita habilitar/deshabilitar el inicio automático
# Soporta tanto el servicio nuevo (masterbegone) como el legacy (volumebegone)
#
# Author: Francisco Ortiz Rojas
# Version: 3.0
#

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Servicios disponibles
SERVICE_MASTER="masterbegone.service"
SERVICE_LEGACY="volumebegone.service"
CURRENT_SERVICE=""

# Banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════╗"
echo "║    Volume Be Gone v3.0 - Auto-Start Manager    ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Verificar si se ejecuta como root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Este script debe ejecutarse como root${NC}"
   echo "Usa: sudo bash autostart.sh"
   exit 1
fi

# Función para mostrar el estado actual
show_status() {
    echo -e "${YELLOW}Estado de los servicios:${NC}"
    echo ""

    # MasterBeGone (v3.0)
    echo -e "  ${BLUE}MasterBeGone (v3.0 - Completo):${NC}"
    if [ -f "/etc/systemd/system/$SERVICE_MASTER" ]; then
        echo -e "    Instalado: ${GREEN}SÍ${NC}"
        if systemctl is-enabled $SERVICE_MASTER &>/dev/null; then
            echo -e "    Auto-inicio: ${GREEN}HABILITADO${NC}"
        else
            echo -e "    Auto-inicio: ${RED}DESHABILITADO${NC}"
        fi
        if systemctl is-active $SERVICE_MASTER &>/dev/null; then
            echo -e "    Estado: ${GREEN}EJECUTANDO${NC}"
        else
            echo -e "    Estado: ${RED}DETENIDO${NC}"
        fi
    else
        echo -e "    Instalado: ${RED}NO${NC}"
    fi
    echo ""

    # VolumeBeGone (Legacy)
    echo -e "  ${BLUE}VolumeBeGone (Legacy - Solo OLED):${NC}"
    if [ -f "/etc/systemd/system/$SERVICE_LEGACY" ]; then
        echo -e "    Instalado: ${GREEN}SÍ${NC}"
        if systemctl is-enabled $SERVICE_LEGACY &>/dev/null; then
            echo -e "    Auto-inicio: ${GREEN}HABILITADO${NC}"
        else
            echo -e "    Auto-inicio: ${RED}DESHABILITADO${NC}"
        fi
        if systemctl is-active $SERVICE_LEGACY &>/dev/null; then
            echo -e "    Estado: ${GREEN}EJECUTANDO${NC}"
        else
            echo -e "    Estado: ${RED}DETENIDO${NC}"
        fi
    else
        echo -e "    Instalado: ${RED}NO${NC}"
    fi
    echo ""
}

# Función para seleccionar servicio
select_service() {
    echo -e "${YELLOW}Selecciona el servicio:${NC}"
    echo "  1) MasterBeGone (v3.0 - OLED + Web + ESP32)"
    echo "  2) VolumeBeGone (Legacy - Solo OLED)"
    echo ""
    read -p "Opción [1-2]: " srv_option

    case $srv_option in
        1)
            CURRENT_SERVICE=$SERVICE_MASTER
            echo -e "${GREEN}Servicio seleccionado: MasterBeGone${NC}"
            ;;
        2)
            CURRENT_SERVICE=$SERVICE_LEGACY
            echo -e "${GREEN}Servicio seleccionado: VolumeBeGone (Legacy)${NC}"
            ;;
        *)
            echo -e "${RED}Opción inválida${NC}"
            exit 1
            ;;
    esac
    echo ""
}

# Función para habilitar auto-inicio
enable_autostart() {
    select_service

    echo -e "${YELLOW}Habilitando auto-inicio para $CURRENT_SERVICE...${NC}"

    if [ ! -f "/etc/systemd/system/$CURRENT_SERVICE" ]; then
        echo -e "${RED}Error: Servicio no instalado${NC}"
        echo "Ejecuta 'sudo bash scripts/install.sh' primero"
        exit 1
    fi

    # Deshabilitar el otro servicio para evitar conflictos
    if [ "$CURRENT_SERVICE" = "$SERVICE_MASTER" ]; then
        systemctl disable $SERVICE_LEGACY 2>/dev/null || true
        systemctl stop $SERVICE_LEGACY 2>/dev/null || true
    else
        systemctl disable $SERVICE_MASTER 2>/dev/null || true
        systemctl stop $SERVICE_MASTER 2>/dev/null || true
    fi

    systemctl daemon-reload
    systemctl enable $CURRENT_SERVICE

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Auto-inicio habilitado${NC}"
        echo ""
        echo "El servicio se iniciará automáticamente al encender la Raspberry Pi"
        echo ""
        echo -e "${YELLOW}Comandos útiles:${NC}"
        SERVICE_NAME="${CURRENT_SERVICE%.service}"
        echo "  Iniciar ahora:  sudo systemctl start $SERVICE_NAME"
        echo "  Ver estado:     sudo systemctl status $SERVICE_NAME"
        echo "  Ver logs:       sudo journalctl -u $SERVICE_NAME -f"
    else
        echo -e "${RED}Error al habilitar auto-inicio${NC}"
        exit 1
    fi
}

# Función para deshabilitar auto-inicio
disable_autostart() {
    select_service

    echo -e "${YELLOW}Deshabilitando auto-inicio para $CURRENT_SERVICE...${NC}"

    systemctl disable $CURRENT_SERVICE 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Auto-inicio deshabilitado${NC}"
        echo ""
        echo "El servicio NO se iniciará al encender la Raspberry Pi"
    else
        echo -e "${RED}Error al deshabilitar auto-inicio${NC}"
        exit 1
    fi
}

# Función para iniciar el servicio
start_service() {
    select_service

    echo -e "${YELLOW}Iniciando $CURRENT_SERVICE...${NC}"

    # Detener el otro servicio
    if [ "$CURRENT_SERVICE" = "$SERVICE_MASTER" ]; then
        systemctl stop $SERVICE_LEGACY 2>/dev/null || true
    else
        systemctl stop $SERVICE_MASTER 2>/dev/null || true
    fi

    systemctl start $CURRENT_SERVICE

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Servicio iniciado${NC}"
        sleep 3
        systemctl status $CURRENT_SERVICE --no-pager
    else
        echo -e "${RED}Error al iniciar servicio${NC}"
        echo ""
        echo "Ver logs con: sudo journalctl -u ${CURRENT_SERVICE%.service} -n 50"
        exit 1
    fi
}

# Función para detener el servicio
stop_service() {
    select_service

    echo -e "${YELLOW}Deteniendo $CURRENT_SERVICE...${NC}"
    systemctl stop $CURRENT_SERVICE

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Servicio detenido${NC}"
    else
        echo -e "${RED}Error al detener servicio${NC}"
        exit 1
    fi
}

# Función para detener todos los servicios
stop_all() {
    echo -e "${YELLOW}Deteniendo todos los servicios...${NC}"
    systemctl stop $SERVICE_MASTER 2>/dev/null || true
    systemctl stop $SERVICE_LEGACY 2>/dev/null || true

    # Limpiar procesos huérfanos
    pkill -f l2ping 2>/dev/null || true
    pkill -f rfcomm 2>/dev/null || true
    pkill -f hcidump 2>/dev/null || true
    pkill -f masterbegone 2>/dev/null || true
    pkill -f volumeBeGone 2>/dev/null || true

    echo -e "${GREEN}Todos los servicios detenidos${NC}"
}

# Función para ver logs en tiempo real
view_logs() {
    select_service

    echo -e "${YELLOW}Mostrando logs de $CURRENT_SERVICE en tiempo real...${NC}"
    echo -e "${YELLOW}(Presiona Ctrl+C para salir)${NC}"
    echo ""
    sleep 2
    journalctl -u $CURRENT_SERVICE -f
}

# Función para ver el estado detallado
show_detailed_status() {
    echo -e "${YELLOW}Estado detallado de los servicios:${NC}"
    echo ""

    echo -e "${BLUE}=== MasterBeGone ===${NC}"
    systemctl status $SERVICE_MASTER --no-pager 2>/dev/null || echo "No instalado"
    echo ""

    echo -e "${BLUE}=== VolumeBeGone (Legacy) ===${NC}"
    systemctl status $SERVICE_LEGACY --no-pager 2>/dev/null || echo "No instalado"
}

# Función para reiniciar servicio
restart_service() {
    select_service

    echo -e "${YELLOW}Reiniciando $CURRENT_SERVICE...${NC}"

    # Detener el otro servicio
    if [ "$CURRENT_SERVICE" = "$SERVICE_MASTER" ]; then
        systemctl stop $SERVICE_LEGACY 2>/dev/null || true
    else
        systemctl stop $SERVICE_MASTER 2>/dev/null || true
    fi

    systemctl restart $CURRENT_SERVICE

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Servicio reiniciado${NC}"
        sleep 3
        systemctl status $CURRENT_SERVICE --no-pager
    else
        echo -e "${RED}Error al reiniciar servicio${NC}"
        exit 1
    fi
}

# Menú principal
show_status

echo -e "${YELLOW}Opciones:${NC}"
echo "  1) Habilitar auto-inicio al encender"
echo "  2) Deshabilitar auto-inicio"
echo "  3) Iniciar servicio ahora"
echo "  4) Detener servicio"
echo "  5) Reiniciar servicio"
echo "  6) Detener TODOS los servicios"
echo "  7) Ver logs en tiempo real"
echo "  8) Ver estado detallado"
echo "  0) Salir"
echo ""
read -p "Selecciona una opción [0-8]: " option

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
        restart_service
        ;;
    6)
        stop_all
        ;;
    7)
        view_logs
        ;;
    8)
        show_detailed_status
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
