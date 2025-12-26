# Volume Be Gone v3.0

Control automatico de parlantes Bluetooth por nivel de volumen usando Raspberry Pi + ESP32

**Author:** Francisco Ortiz Rojas - Ingeniero Electronico
**Contact:** francisco.ortiz@marfinex.com
**Version:** 3.0 | **Date:** Diciembre 2025

---

## Descripcion

Volume Be Gone es un sistema híbrido (Raspberry Pi + ESP32) que monitorea el nivel de ruido ambiental y automaticamente intenta desconectar parlantes Bluetooth cercanos cuando el volumen supera un umbral configurable (70-120 dB).

### Novedades v3.0 - Arquitectura Modular + Web

La versión 3.0 introduce una arquitectura completamente modular con servidor web integrado:

**Nuevas Características:**
- **Arquitectura Modular**: Código dividido en módulos independientes para fácil mantenimiento
- **Servidor Web**: Interfaz responsive accesible desde cualquier dispositivo
- **Access Point Mode**: La RPi crea su propia red WiFi (no necesita router)
- **Control desde Celular**: Monitoreo y control completo desde el navegador
- **ESP32 BlueJammer**: Integración con ESP32 para RF Jamming de capa física
- **Ataque Multicapa**: Combina PHY (RF) + L2CAP + RFCOMM simultáneamente

### Características principales:

- **Control preciso** con encoder rotativo + interfaz web
- **Medidor visual** en pantalla OLED 128x64 + navegador web
- **Alcance extendido** hasta 50m con adaptador Clase 1
- **Busqueda automatica** de dispositivos cada 30 segundos
- **Configuracion persistente** en JSON
- **Inicio automatico** con systemd
- **RF Jamming** con ESP32 + dual nRF24L01
- **Ataque multicapa** PHY + L2CAP + RFCOMM

## Disclaimer

> **IMPORTANTE**: Este proyecto es solo para fines educativos. Usalo unicamente con tus propios dispositivos o con permiso explicito. El uso indebido puede ser ilegal en tu jurisdiccion.

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    VOLUME BE GONE v3.0                          │
│                   Arquitectura Híbrida                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │                  RASPBERRY PI (Cerebro)                   │ │
│   ├──────────────────────────────────────────────────────────┤ │
│   │                                                          │ │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │ │
│   │  │   Audio     │  │  Bluetooth  │  │   Display   │      │ │
│   │  │  Monitor    │  │   Scanner   │  │   Manager   │      │ │
│   │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘      │ │
│   │         │                │                │              │ │
│   │         └────────────────┼────────────────┘              │ │
│   │                          │                               │ │
│   │                   ┌──────┴──────┐                        │ │
│   │                   │  MASTER     │                        │ │
│   │                   │  BEGONE     │                        │ │
│   │                   │ (Orquesta)  │                        │ │
│   │                   └──────┬──────┘                        │ │
│   │                          │                               │ │
│   │         ┌────────────────┼────────────────┐              │ │
│   │         │                │                │              │ │
│   │  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐      │ │
│   │  │   Attack    │  │    Web      │  │   ESP32     │      │ │
│   │  │   Engine    │  │   Server    │  │ Controller  │      │ │
│   │  └─────────────┘  └─────────────┘  └──────┬──────┘      │ │
│   │                                           │ Serial      │ │
│   └───────────────────────────────────────────┼──────────────┘ │
│                                               │                │
│   ┌───────────────────────────────────────────┼──────────────┐ │
│   │                    ESP32 (Músculo RF)     │              │ │
│   ├───────────────────────────────────────────┼──────────────┤ │
│   │                                           ▼              │ │
│   │              ┌─────────────────────────────┐             │ │
│   │              │    ESP32 BlueJammer         │             │ │
│   │              │    (Dual nRF24L01)          │             │ │
│   │              └──────────┬──────────────────┘             │ │
│   │                         │                                │ │
│   │              ┌──────────┴──────────┐                     │ │
│   │              │                     │                     │ │
│   │        ┌─────┴─────┐         ┌─────┴─────┐              │ │
│   │        │ nRF24 #1  │         │ nRF24 #2  │              │ │
│   │        │ (CH 0-62) │         │ (CH 63-124)│              │ │
│   │        └───────────┘         └───────────┘              │ │
│   └─────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Hardware Necesario

### Componentes Raspberry Pi (Base):

| Componente | Descripción | Cantidad |
|------------|-------------|----------|
| Raspberry Pi 3B+/4B | 2GB+ RAM | 1 |
| Pantalla OLED | 128x64 I2C SSD1306 | 1 |
| Encoder Rotativo | KY-040 | 1 |
| Microfono USB | Cualquiera compatible | 1 |
| Adaptador BT | Clase 1 USB (opcional) | 1 |
| Fuente 5V | 3A USB-C | 1 |

### Componentes ESP32 BlueJammer (v3.0):

| Componente | Descripción | Cantidad |
|------------|-------------|----------|
| ESP32 DevKit V1 | 38 pines | 1 |
| nRF24L01+PA+LNA | Con antena externa | 2 |
| Antena 12dBi | 2400-2500MHz | 2 |
| Capacitor 100µF/16V | Electrolítico | 2 |
| Capacitor 100nF | Cerámico | 2 |
| Cable USB | Para conexión a RPi | 1 |

### Diagrama de Conexiones:

- RPi: Ver `hardware/README.md`
- ESP32: Ver `hardware/ESP32_WIRING.md`
- Arquitectura completa: Ver `PROPUESTA_HIBRIDA_COMPLETA.md`

## Instalacion

### Metodo rapido:

```bash
# Clonar repositorio
git clone https://github.com/neo3x/volume-be-gone.git
cd volume-be-gone

# Ejecutar instalador automatico
chmod +x scripts/install.sh
sudo ./scripts/install.sh

# (Opcional) Configurar Access Point para control desde celular
sudo ./scripts/setup_ap.sh
```

### Metodo manual:

Ver `docs/INSTALL.md` para instrucciones detalladas.

## Uso

### Modos de Ejecución:

```bash
# Modo completo (OLED + Web + ESP32)
./start.sh

# Solo servidor web (sin OLED/encoder)
./start-web-only.sh

# Sin display (headless)
./start-headless.sh

# Con opciones específicas
cd src && python3 masterbegone.py --help
```

### Opciones de Línea de Comando:

```
python3 masterbegone.py [opciones]

Opciones:
  --headless    Ejecutar sin display OLED
  --no-esp32    Deshabilitar comunicación con ESP32
  --web-only    Solo servidor web (sin OLED/encoder)
  --debug       Activar modo debug
  --version     Mostrar versión
```

### Acceso Web:

1. **Con Access Point (recomendado):**
   - Conecta a la red WiFi `VolumeBeGone`
   - Contraseña: `begone2025`
   - Abre: `http://192.168.4.1:5000`

2. **En red existente:**
   - Abre: `http://<IP-de-la-RPi>:5000`

### Controles Físicos:

- **Girar encoder**: Ajustar umbral
- **Presionar encoder**: Guardar configuración
- **Mantener 2s**: Reiniciar sistema

### Como Servicio:

```bash
# Iniciar
sudo systemctl start masterbegone

# Detener
sudo systemctl stop masterbegone

# Ver logs
sudo journalctl -u masterbegone -f

# Habilitar auto-inicio
sudo systemctl enable masterbegone
```

### Gestor de Auto-Inicio:

```bash
sudo bash scripts/autostart.sh
```

## Estructura del Proyecto v3.0

```
volume-be-gone/
├── src/
│   ├── masterbegone.py           # Orquestador principal v3.0
│   ├── volumeBeGone.py           # Script legacy (solo OLED)
│   ├── modules/
│   │   ├── __init__.py           # Exports de módulos
│   │   ├── config.py             # Configuración centralizada
│   │   ├── audio_monitor.py      # Monitoreo de audio
│   │   ├── bluetooth_scanner.py  # Escaneo BT/BLE
│   │   ├── display_manager.py    # OLED + Encoder
│   │   ├── attack_engine.py      # Motor de ataques
│   │   ├── esp32_controller.py   # Control ESP32 serial
│   │   └── web_server.py         # Servidor Flask + SocketIO
│   └── static/
│       ├── index.html            # UI web principal
│       ├── css/style.css         # Estilos dark theme
│       └── js/app.js             # Cliente WebSocket
├── firmware/
│   └── esp32_hybrid/
│       └── esp32_hybrid.ino      # Firmware ESP32
├── hardware/
│   ├── ESP32_WIRING.md           # Conexionado ESP32
│   ├── NRF24L01_WIRING.md        # Conexionado nRF24
│   └── GPIO_COMPATIBILITY_ANALYSIS.md
├── scripts/
│   ├── install.sh                # Instalador v3.0
│   ├── autostart.sh              # Gestor de auto-inicio
│   └── setup_ap.sh               # Configurar Access Point
├── config/
│   └── settings.json             # Configuración por defecto
├── PROPUESTA_HIBRIDA_COMPLETA.md # Documentación arquitectura
├── ARQUITECTURA_HIBRIDA.md       # Diagramas
├── COMPARACION_JAMMERS_ESP32.md  # Análisis repos ESP32
└── README.md                     # Este archivo
```

## Módulos del Sistema

### MasterBeGone (masterbegone.py)
Orquestador principal que coordina todos los módulos.

### Config (modules/config.py)
Configuración centralizada con dataclasses para tipo-seguro.

### AudioMonitor (modules/audio_monitor.py)
Monitoreo de nivel de audio ambiental con callbacks.

### BluetoothScanner (modules/bluetooth_scanner.py)
Escaneo dual-mode (Classic + BLE) con detección de dispositivos de audio.

### DisplayManager (modules/display_manager.py)
Control de pantalla OLED SSD1306 y encoder rotativo.

### AttackEngine (modules/attack_engine.py)
Motor de ataques coordinados L2CAP + RFCOMM + ESP32.

### ESP32Controller (modules/esp32_controller.py)
Comunicación serial con ESP32 BlueJammer.

### WebServer (modules/web_server.py)
Servidor Flask + SocketIO para interfaz web en tiempo real.

## API REST

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/status` | GET | Estado completo del sistema |
| `/api/threshold` | POST | Cambiar umbral de volumen |
| `/api/devices` | GET | Lista de dispositivos detectados |
| `/api/scan` | POST | Iniciar escaneo Bluetooth |
| `/api/attack` | POST | Atacar dispositivo específico |
| `/api/attack/start` | POST | Iniciar ataque continuo |
| `/api/attack/stop` | POST | Detener ataques |
| `/api/esp32/status` | GET | Estado del ESP32 |
| `/api/esp32/jam` | POST | Control de jamming |

## WebSocket Events

| Evento | Dirección | Descripción |
|--------|-----------|-------------|
| `volume` | Server → Client | Nivel de volumen actual |
| `devices` | Server → Client | Lista de dispositivos |
| `device_found` | Server → Client | Nuevo dispositivo detectado |
| `status` | Server → Client | Estado completo |
| `set_threshold` | Client → Server | Cambiar umbral |

## Solución de Problemas

### El servidor web no inicia
```bash
# Verificar dependencias
python3 -c "import flask_socketio"

# Reinstalar si es necesario
pip3 install flask flask-socketio eventlet --break-system-packages
```

### ESP32 no detectado
```bash
# Verificar conexión serial
ls -la /dev/ttyUSB*

# Verificar permisos
sudo usermod -a -G dialout $USER
# (requiere logout/login)
```

### OLED no muestra nada
```bash
# Verificar I2C
sudo i2cdetect -y 1
# Debe mostrar dirección 3C
```

### Access Point no funciona
```bash
# Verificar servicios
sudo systemctl status hostapd
sudo systemctl status dnsmasq

# Reiniciar
sudo systemctl restart hostapd dnsmasq
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
- Repositorios ESP32-BlueJammer analizados para integración

---
*Volume Be Gone v3.0 - Diciembre 2025*
