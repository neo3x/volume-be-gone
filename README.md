# Volume Be Gone

Control automatico de parlantes Bluetooth por nivel de volumen usando Raspberry Pi

**Author:** Francisco Ortiz Rojas - Ingeniero Electronico
**Contact:** francisco.ortiz@marfinex.com
**Version:** 2.1 | **Date:** Diciembre 2025

---

## Descripcion

Volume Be Gone es un dispositivo basado en Raspberry Pi que monitorea el nivel de ruido ambiental y automaticamente intenta desconectar parlantes Bluetooth cercanos cuando el volumen supera un umbral configurable (70-120 dB).

### ✨ Caracteristicas principales:

- 🎚️ **Control preciso** con encoder rotativo
- 📊 **Medidor visual** en pantalla OLED 128x64
- 📡 **Alcance extendido** hasta 50m con adaptador Clase 1
- 🔄 **Busqueda automatica** de dispositivos cada 30 segundos
- 💾 **Configuracion persistente** en JSON
- 🚀 **Inicio automatico** con systemd

## ⚠️ Disclaimer

> **IMPORTANTE**: Este proyecto es solo para fines educativos. Usalo unicamente con tus propios dispositivos o con permiso explicito. El uso indebido puede ser ilegal en tu jurisdiccion.

## 🛠️ Hardware Necesario

### Componentes principales:

- Raspberry Pi 3B+ o 4B (2GB+)
- Pantalla OLED 128x64 I2C SSD1306
- Encoder Rotativo KY-040
- Microfono USB
- Adaptador BT Clase 1 USB (opcional)
- Fuente 5V 3A USB-C

### 🔌 Diagrama de conexiones:

Ver diagrama completo en hardware/README.md

## 💻 Instalacion

### Metodo rapido:

```bash
# Clonar repositorio
git clone https://github.com/neo3x/volume-be-gone.git
cd volume-be-gone

# Ejecutar instalador automatico
chmod +x scripts/install.sh
sudo ./scripts/install.sh
#setup.bat hara la estructura completa del proyecto.
```

### Metodo manual:

Ver docs/INSTALL.md para instrucciones detalladas.

## 🚀 Uso

### Controles:

- 🔄 **Girar encoder**: Ajustar umbral
- ✅ **Presionar**: Confirmar configuracion
- 🔄 **Mantener 2s**: Reiniciar dispositivo

### Ejecucion:

```bash
# Manual
cd /home/pi/volumebegone
sudo python3 volumeBeGone.py

# Como servicio
sudo systemctl start volumebegone
```

### 🔄 Auto-Inicio al Encender

Habilita el inicio automatico para que se ejecute al encender la Raspberry Pi:

```bash
# Metodo facil - Script interactivo
sudo bash scripts/autostart.sh

# O manualmente
sudo systemctl enable volumebegone
sudo systemctl start volumebegone
```

**Pantalla de carga en OLED:**
Al encender, veras una barra de progreso en la pantalla OLED mostrando:
- Init Display... (14%)
- Setup GPIO... (28%)
- Load Config... (42%)
- Check Bluetooth... (57%)
- Check Mic... (71%)
- Load Resources... (85%)
- System Ready! (100%)

Ver **GUIA_AUTOSTART.md** para instrucciones detalladas.

### Comandos utiles:

```bash
# Ver estado del servicio
sudo systemctl status volumebegone

# Ver logs en tiempo real
sudo journalctl -u volumebegone -f

# Detener servicio
sudo systemctl stop volumebegone

# Deshabilitar auto-inicio
sudo systemctl disable volumebegone
```

## Licencia

Este proyecto esta bajo la Licencia MIT - ver LICENSE para detalles.

## Creditos

**Desarrollado por:**
- **Francisco Ortiz Rojas** - Ingeniero Electronico
- **Email:** francisco.ortiz@marfinex.com

**Agradecimientos:**
- Inspirado en "Reggaeton Be Gone" de Roni Bandini
- Comunidad Raspberry Pi
- Libreria Adafruit para displays OLED

---
*Volume Be Gone v2.1 - Diciembre 2025*
