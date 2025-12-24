# Volume Be Gone

Control automatico de parlantes Bluetooth por nivel de volumen usando Raspberry Pi

**Author:** Francisco Ortiz Rojas - Ingeniero Electronico
**Contact:** francisco.ortiz@marfinex.com
**Version:** 3.0 | **Date:** Diciembre 2025

---

## Descripcion

Volume Be Gone es un sistema híbrido (Raspberry Pi + ESP32) que monitorea el nivel de ruido ambiental y automaticamente intenta desconectar parlantes Bluetooth cercanos cuando el volumen supera un umbral configurable (70-120 dB).

### 🆕 Novedades v3.0 - Arquitectura Híbrida

La versión 3.0 integra un **ESP32 BlueJammer** para ataques RF de capa física, combinando:
- **Raspberry Pi**: Cerebro del sistema (monitoreo, UI, ataques L2CAP/RFCOMM)
- **ESP32 + 2x nRF24L01**: Motor de RF Jamming (interferencia 2.4GHz)

Ver [PROPUESTA_HIBRIDA_COMPLETA.md](PROPUESTA_HIBRIDA_COMPLETA.md) para detalles.

### ✨ Caracteristicas principales:

- 🎚️ **Control preciso** con encoder rotativo
- 📊 **Medidor visual** en pantalla OLED 128x64
- 📡 **Alcance extendido** hasta 50m con adaptador Clase 1
- 🔄 **Busqueda automatica** de dispositivos cada 30 segundos
- 💾 **Configuracion persistente** en JSON
- 🚀 **Inicio automatico** con systemd
- ⚡ **NEW: RF Jamming** con ESP32 + dual nRF24L01 (v3.0)
- 🎯 **NEW: Ataque multicapa** PHY + L2CAP + RFCOMM (v3.0)

## ⚠️ Disclaimer

> **IMPORTANTE**: Este proyecto es solo para fines educativos. Usalo unicamente con tus propios dispositivos o con permiso explicito. El uso indebido puede ser ilegal en tu jurisdiccion.

## 🛠️ Hardware Necesario

### Componentes Raspberry Pi (Base):

- Raspberry Pi 3B+ o 4B (2GB+)
- Pantalla OLED 128x64 I2C SSD1306
- Encoder Rotativo KY-040
- Microfono USB
- Adaptador BT Clase 1 USB (opcional)
- Fuente 5V 3A USB-C

### Componentes ESP32 BlueJammer (v3.0):

- ESP32 DevKit V1 (38 pines)
- 2x nRF24L01+PA+LNA con antena
- 2x Capacitor 100µF/16V
- 2x Capacitor 100nF
- Cable USB para conexión a RPi

### 🔌 Diagrama de conexiones:

- RPi: Ver `hardware/README.md`
- ESP32: Ver `hardware/ESP32_WIRING.md`
- Arquitectura completa: Ver `PROPUESTA_HIBRIDA_COMPLETA.md`

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
- Libreria luma.oled para displays OLED (compatible con Debian Trixie)

## 📂 Estructura del Proyecto v3.0

```
volume-be-gone/
├── src/
│   ├── volumeBeGone.py          # Script principal RPi
│   └── esp32_controller.py      # Controlador serial ESP32
├── firmware/
│   └── esp32_hybrid/
│       └── esp32_hybrid.ino     # Firmware ESP32
├── hardware/
│   ├── ESP32_WIRING.md          # Conexionado ESP32
│   ├── NRF24L01_WIRING.md       # Conexionado nRF24
│   └── GPIO_COMPATIBILITY_ANALYSIS.md
├── PROPUESTA_HIBRIDA_COMPLETA.md  # Documentación completa v3.0
├── ARQUITECTURA_HIBRIDA.md        # Diagramas de arquitectura
└── COMPARACION_JAMMERS_ESP32.md   # Análisis de repos ESP32
```

---
*Volume Be Gone v3.0 - Diciembre 2025*
