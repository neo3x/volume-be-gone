# Changelog

All notable changes to Volume Be Gone will be documented in this file.

The format is based on Keep a Changelog,
and this project adheres to Semantic Versioning.

**Author:** Francisco Ortiz Rojas - Ingeniero Electronico
**Contact:** francisco.ortiz@marfinex.com

## [Unreleased]

## [3.0.0] - 2025-12-27

### Added

#### Arquitectura Modular
- `masterbegone.py` - Nuevo orquestador principal que coordina todos los módulos
- `modules/config.py` - Configuración centralizada con dataclasses tipo-seguro
- `modules/audio_monitor.py` - Monitoreo de audio con callbacks
- `modules/bluetooth_scanner.py` - Escaneo dual-mode (Classic + BLE)
- `modules/display_manager.py` - Control de OLED SSD1306 + encoder KY-040
- `modules/attack_engine.py` - Motor de ataques coordinados L2CAP + RFCOMM + ESP32
- `modules/esp32_controller.py` - Comunicación serial con ESP32 BlueJammer
- `modules/web_server.py` - Servidor Flask + SocketIO en tiempo real

#### Servidor Web
- Interfaz web responsive mobile-first
- Control completo desde el navegador
- WebSocket para actualizaciones en tiempo real
- API REST para integración externa
- Tema oscuro optimizado para uso nocturno

#### Access Point Mode
- `scripts/setup_ap.sh` - Script para configurar RPi como Access Point WiFi
- Funciona sin router externo
- Red WiFi: VolumeBeGone (contraseña: begone2025)
- DNS local: volumebegone.local

#### Integración ESP32 BlueJammer
- Firmware híbrido para ESP32 con dual nRF24L01
- Protocolo serial para comunicación RPi ↔ ESP32
- 4 modos de jamming: BT, BLE, WiFi, Full
- 4 patrones TX: Continuous, Pulse, Sweep, Burst
- Soporte para antenas externas 12dBi

#### Documentación para Usuarios
- `docs/usuario/QUE_ES_VOLUME_BE_GONE.md` - Explicación simple del proyecto
- `docs/usuario/INICIO_RAPIDO.md` - Guía de inicio en 5 minutos
- `docs/usuario/MANUAL_USUARIO.md` - Manual completo paso a paso
- `docs/README.md` - Índice de toda la documentación

#### Scripts Mejorados
- `start.sh` - Inicio rápido modo completo
- `start-web-only.sh` - Solo interfaz web
- `start-headless.sh` - Sin display
- Argumentos CLI: --headless, --no-esp32, --web-only, --debug

### Changed

#### Instalador (install.sh)
- Ahora instala Flask, Flask-SocketIO, eventlet
- Instala hostapd y dnsmasq para Access Point
- Crea estructura de directorios modular
- Genera `config/settings.json` por defecto
- Crea servicios systemd: masterbegone + volumebegone (legacy)
- Verificación de dependencias al final

#### Autostart (autostart.sh)
- Soporte para ambos servicios (masterbegone y volumebegone)
- Menú mejorado con más opciones
- Opción para detener todos los servicios
- Opción para reiniciar servicios

#### README.md
- Simplificado y más amigable
- Instalación en 3 pasos claros
- Enlaces a documentación para usuarios
- Menos jerga técnica

#### Estructura del Proyecto
- Documentación técnica movida a `docs/tecnico/`
- Documentación de hardware movida a `docs/hardware/`
- Nueva carpeta `docs/usuario/` para guías amigables
- Código fuente modularizado en `src/modules/`
- Frontend web en `src/static/`

### Technical Details

#### API REST Endpoints
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/status` | GET | Estado del sistema |
| `/api/threshold` | POST | Cambiar umbral |
| `/api/devices` | GET | Lista de dispositivos |
| `/api/scan` | POST | Iniciar escaneo |
| `/api/attack` | POST | Atacar dispositivo |
| `/api/attack/start` | POST | Ataque continuo |
| `/api/attack/stop` | POST | Detener ataques |
| `/api/esp32/status` | GET | Estado ESP32 |
| `/api/esp32/jam` | POST | Control jamming |

#### WebSocket Events
| Evento | Dirección | Descripción |
|--------|-----------|-------------|
| `volume` | Server → Client | Nivel de volumen |
| `devices` | Server → Client | Lista dispositivos |
| `status` | Server → Client | Estado completo |
| `set_threshold` | Client → Server | Cambiar umbral |

---

## [2.1.0] - 2025-12-15

### Added
- Compatibilidad completa con Debian Trixie (testing)
- Detección automática de usuario del sistema
- Configuración automática de I2C, SPI y GPIO persistente
- Reglas udev para permisos de hardware
- Soporte para PEP 668 (--break-system-packages)

### Fixed
- Errores de sintaxis en test_encoder.py
- Shebangs incorrectos en scripts de test
- Nombres de paquetes para Debian Trixie
- Referencias a archivos inexistentes en install.sh
- Usuario hardcodeado 'pi' ahora se detecta automáticamente

## [2.0.0] - 2025-10-01

### Added
- Encoder rotativo para control de umbral
- Pantalla OLED 128x64 con medidor visual
- Soporte para adaptador Bluetooth Clase 1
- Configuracion persistente en JSON
- Deteccion automatica de adaptadores BT
- Sistema de logging mejorado
- Tests de componentes

### Changed
- Interfaz completamente rediseñada
- Algoritmo de deteccion de volumen mejorado
- Estructura de proyecto reorganizada

### Fixed
- Problemas de memoria en escaneo continuo
- Compatibilidad con Raspberry Pi 4

## [1.0.0] - 2025-07-01

### Added
- Version inicial basada en Reggaeton Be Gone
- Deteccion por nivel de volumen
- Busqueda automatica de dispositivos
- Ataque a multiples parlantes
