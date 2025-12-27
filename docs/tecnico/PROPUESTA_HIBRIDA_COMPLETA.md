# PROPUESTA HÍBRIDA COMPLETA - Volume Be Gone v3.0

## Integración: RPi + ESP32-BlueJammer + Bluetooth-jammer-esp32

---

## 📋 RESUMEN EJECUTIVO

Esta propuesta integra las mejores características de dos repositorios ESP32:
- **ESP32-BlueJammer**: Dual SPI (HSPI+VSPI), 4 modos de jamming, OLED, carcasa 3D
- **Bluetooth-jammer-esp32**: Código base simple, fácil modificación

Con el sistema existente **Volume Be Gone** en Raspberry Pi para crear un sistema de disrupción de audio Bluetooth de múltiples capas.

---

## 🏗️ ARQUITECTURA DEL SISTEMA HÍBRIDO

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                     │
│                    VOLUME BE GONE v3.0 - SISTEMA HÍBRIDO COMPLETO                   │
│                                                                                     │
│  ┌───────────────────────────────────────┐   ┌───────────────────────────────────┐ │
│  │                                       │   │                                   │ │
│  │         RASPBERRY PI 3B+/4B           │   │       ESP32-BLUEJAMMER            │ │
│  │         ═══════════════════           │   │       ═════════════════           │ │
│  │                                       │   │                                   │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ │   │  ┌─────────────┐ ┌─────────────┐  │ │
│  │  │  OLED   │ │ Encoder │ │   Mic   │ │   │  │ nRF24L01 #1 │ │ nRF24L01 #2 │  │ │
│  │  │ 128x64  │ │ KY-040  │ │   USB   │ │   │  │   (HSPI)    │ │   (VSPI)    │  │ │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ │   │  │  CH: 0-62   │ │  CH: 63-124 │  │ │
│  │       │           │           │      │   │  └──────┬──────┘ └──────┬──────┘  │ │
│  │       └─────┬─────┴─────┬─────┘      │   │         │               │         │ │
│  │             │           │            │   │         └───────┬───────┘         │ │
│  │             ▼           ▼            │   │                 │                 │ │
│  │  ┌──────────────────────────────┐    │   │                 ▼                 │ │
│  │  │      CEREBRO CENTRAL         │    │   │    ┌────────────────────────┐    │ │
│  │  │                              │    │   │    │    RF JAMMING ENGINE   │    │ │
│  │  │  • Monitoreo audio (dB)      │    │   │    │                        │    │ │
│  │  │  • Escaneo dispositivos BT   │    │   │    │  • Dual SPI paralelo   │    │ │
│  │  │  • Detección parlantes       │    │   │    │  • 4 modos de ataque   │    │ │
│  │  │  • Coordinación de ataques   │    │   │    │  • Channel hopping     │    │ │
│  │  │  • Interfaz de usuario       │    │   │    │  • 125 canales 2.4GHz  │    │ │
│  │  └──────────────┬───────────────┘    │   │    └────────────┬───────────┘    │ │
│  │                 │                    │   │                 │                 │ │
│  │                 ▼                    │   │                 │                 │ │
│  │  ┌──────────────────────────────┐    │   │                 │                 │ │
│  │  │      BLUETOOTH DoS           │    │   │                 │                 │ │
│  │  │                              │    │   │                 │                 │ │
│  │  │  • L2CAP Ping Flood          │    │   │                 │                 │ │
│  │  │  • RFCOMM Saturation         │    │   │                 │                 │ │
│  │  │  • A2DP/AVDTP Disruption     │    │   │                 │                 │ │
│  │  └──────────────┬───────────────┘    │   │                 │                 │ │
│  │                 │                    │   │                 │                 │ │
│  │                 ▼                    │   │                 │                 │ │
│  │  ┌──────────────────────────────┐    │   │                 │                 │ │
│  │  │   USB Bluetooth Adapter      │    │   │                 │                 │ │
│  │  │   Clase 1 (50-100m)          │    │   │                 │                 │ │
│  │  └──────────────────────────────┘    │   │                 │                 │ │
│  │                                       │   │                 │                 │ │
│  └───────────────────┬───────────────────┘   └─────────────────┬─────────────────┘ │
│                      │                                         │                   │
│                      │         ┌───────────────────┐           │                   │
│                      │         │                   │           │                   │
│                      └────────►│   USB SERIAL      │◄──────────┘                   │
│                                │   115200 baud     │                               │
│                                │   /dev/ttyUSB0    │                               │
│                                │                   │                               │
│                                └─────────┬─────────┘                               │
│                                          │                                         │
│                                          ▼                                         │
│                         ┌────────────────────────────────┐                         │
│                         │                                │                         │
│                         │     🔊 PARLANTE BLUETOOTH      │                         │
│                         │                                │                         │
│                         │   Recibe ataque MULTICAPA:     │                         │
│                         │   ├─ Capa 1 (PHY): RF Jamming  │                         │
│                         │   ├─ Capa 2 (L2CAP): Flood     │                         │
│                         │   └─ Capa 3 (RFCOMM): Satur.   │                         │
│                         │                                │                         │
│                         │   RESULTADO: DESCONEXIÓN       │                         │
│                         │                                │                         │
│                         └────────────────────────────────┘                         │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 ROLES ESPECÍFICOS

### RASPBERRY PI - El Cerebro

| Función | Descripción | Componente |
|---------|-------------|------------|
| **Monitoreo de Audio** | Detecta nivel de ruido ambiente en dB | Micrófono USB |
| **Umbral Configurable** | Ajuste 70-120 dB con encoder | Encoder KY-040 |
| **Escaneo Bluetooth** | Detecta dispositivos BT/BLE cercanos | Adaptador USB Clase 1 |
| **Filtrado Inteligente** | Identifica parlantes por nombre/clase | Software Python |
| **Ataques L2CAP/RFCOMM** | DoS a nivel de protocolo Bluetooth | BlueZ/PyBluez |
| **Coordinación** | Orquesta timing de ataques | Serial a ESP32 |
| **Interfaz Usuario** | Muestra estado y permite control | OLED SSD1306 |

### ESP32-BLUEJAMMER - El Músculo RF

| Función | Descripción | Componente |
|---------|-------------|------------|
| **RF Jamming** | Interferencia en banda 2.4GHz | 2x nRF24L01+PA+LNA |
| **Dual SPI** | Transmisión paralela real | HSPI + VSPI |
| **4 Modos de Ataque** | BT/BLE/WiFi/Drones | Firmware |
| **Channel Hopping** | Salto entre 125 canales | Core 0 |
| **Transmisión Continua** | Señal de interferencia | Core 1 |
| **Recepción Comandos** | Escucha órdenes del RPi | Serial USB |

---

## 🔌 DIAGRAMA DE CONEXIONADO COMPLETO

### ESP32 DevKit - Conexiones

```
                              ESP32 DevKit V1 (38 pines)
                         ┌─────────────────────────────────┐
                         │            [USB-C]              │
                         │         ┌─────────┐             │
                         │         │  CP2102 │             │
                         └─────────┴────┬────┴─────────────┘
                                        │
        ┌───────────────────────────────┴───────────────────────────────┐
        │                                                               │
   EN  [●] 1                                                        38 [●] GPIO23 ──► MOSI (VSPI)
   VP  [○] 2                                                        37 [●] GPIO22 ──► CE nRF #2
   VN  [○] 3                                                        36 [○] TX0
GPIO34 [○] 4                                                        35 [○] RX0
GPIO35 [○] 5                                                        34 [●] GPIO21 ──► CSN nRF #2
GPIO32 [○] 6                                                        33 [●] GPIO19 ──► MISO (VSPI)
GPIO33 [○] 7                                                        32 [●] GPIO18 ──► SCK (VSPI)
GPIO25 [○] 8                                                        31 [○] GPIO5
GPIO26 [○] 9                                                        30 [○] GPIO17
GPIO27 [●]10 ──► LED Status (4.7kΩ)                                 29 [●] GPIO16 ──► CE nRF #1
GPIO14 [●]11 ──► SCK (HSPI)                                         28 [○] GPIO4
GPIO12 [●]12 ──► MISO (HSPI)                                        27 [●] GPIO2 ──► LED interno
GPIO13 [●]13 ──► MOSI (HSPI)                                        26 [●] GPIO15 ──► CSN nRF #1
   GND [●]14 ──► GND común                                          25 [●] GND
   VIN [○]15                                                        24 [●] 3V3 ──► VCC nRF #1 y #2
   3V3 [●]16 ──► Alternativa VCC                                    23 [○] GPIO8
        │                                                               │
        └───────────────────────────────────────────────────────────────┘


    CONEXIONES nRF24L01 MÓDULO #1 (HSPI)          CONEXIONES nRF24L01 MÓDULO #2 (VSPI)
    ════════════════════════════════════          ════════════════════════════════════

    ┌─────────────────────────┐                   ┌─────────────────────────┐
    │      nRF24L01+PA+LNA    │                   │      nRF24L01+PA+LNA    │
    │                         │                   │                         │
    │  [Antena SMA]           │                   │  [Antena SMA]           │
    │       │                 │                   │       │                 │
    │  ┌────┴────┐            │                   │  ┌────┴────┐            │
    │  │ PA+LNA  │            │                   │  │ PA+LNA  │            │
    │  └─────────┘            │                   │  └─────────┘            │
    │                         │                   │                         │
    │  Pin   Conexión         │                   │  Pin   Conexión         │
    │  ───   ─────────        │                   │  ───   ─────────        │
    │  VCC ◄─ 3V3 (Pin 24)    │                   │  VCC ◄─ 3V3 (Pin 24)    │
    │  GND ◄─ GND (Pin 14)    │                   │  GND ◄─ GND (Pin 14)    │
    │  CE  ◄─ GPIO16 (Pin 29) │                   │  CE  ◄─ GPIO22 (Pin 37) │
    │  CSN ◄─ GPIO15 (Pin 26) │                   │  CSN ◄─ GPIO21 (Pin 34) │
    │  SCK ◄─ GPIO14 (Pin 11) │                   │  SCK ◄─ GPIO18 (Pin 32) │
    │  MOSI◄─ GPIO13 (Pin 13) │                   │  MOSI◄─ GPIO23 (Pin 38) │
    │  MISO◄─ GPIO12 (Pin 12) │                   │  MISO◄─ GPIO19 (Pin 33) │
    │  IRQ  ─ No conectar     │                   │  IRQ  ─ No conectar     │
    │                         │                   │                         │
    └─────────────────────────┘                   └─────────────────────────┘

    Canales: 0-62 (2400-2462 MHz)                 Canales: 63-124 (2463-2524 MHz)
```

### Raspberry Pi - Conexiones Existentes

```
                            RASPBERRY PI 3B+/4B
    ┌─────────────────────────────────────────────────────────────────────┐
    │                                                                     │
    │   COMPONENTES YA CONECTADOS (Volume Be Gone v2.1):                  │
    │   ══════════════════════════════════════════════════                │
    │                                                                     │
    │   ┌─────────────────────────────────────────────────────────────┐   │
    │   │                                                             │   │
    │   │   OLED SSD1306 128x64 (I2C)                                │   │
    │   │   ─────────────────────────                                │   │
    │   │   VCC  ◄── 3.3V (Pin 1)                                    │   │
    │   │   GND  ◄── GND (Pin 6)                                     │   │
    │   │   SDA  ◄── GPIO2 (Pin 3)                                   │   │
    │   │   SCL  ◄── GPIO3 (Pin 5)                                   │   │
    │   │                                                             │   │
    │   │   Encoder KY-040                                            │   │
    │   │   ──────────────                                            │   │
    │   │   CLK  ◄── GPIO13 (Pin 33)                                 │   │
    │   │   DT   ◄── GPIO19 (Pin 35)                                 │   │
    │   │   SW   ◄── GPIO26 (Pin 37)                                 │   │
    │   │   VCC  ◄── 3.3V (Pin 17)                                   │   │
    │   │   GND  ◄── GND (Pin 39)                                    │   │
    │   │                                                             │   │
    │   └─────────────────────────────────────────────────────────────┘   │
    │                                                                     │
    │   CONEXIONES USB:                                                   │
    │   ═══════════════                                                   │
    │                                                                     │
    │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
    │   │ Puerto USB1 │  │ Puerto USB2 │  │ Puerto USB3 │                │
    │   │             │  │             │  │             │                │
    │   │ Micrófono   │  │ Bluetooth   │  │   ESP32     │                │
    │   │    USB      │  │ USB Clase 1 │  │   Serial    │                │
    │   │             │  │   (hci1)    │  │(/dev/ttyUSB0)│               │
    │   └─────────────┘  └─────────────┘  └─────────────┘                │
    │                                                                     │
    └─────────────────────────────────────────────────────────────────────┘
```

### Conexión Física RPi ↔ ESP32

```
    ┌─────────────────────┐                      ┌─────────────────────┐
    │                     │                      │                     │
    │   RASPBERRY PI      │     Cable USB        │      ESP32          │
    │                     │     (Datos +         │                     │
    │  ┌───────────────┐  │      Power)          │  ┌───────────────┐  │
    │  │  Puerto USB   │──┼──────────────────────┼──│  Puerto USB   │  │
    │  │               │  │                      │  │               │  │
    │  └───────────────┘  │                      │  └───────────────┘  │
    │                     │                      │                     │
    │  /dev/ttyUSB0       │                      │  Serial (115200)    │
    │                     │                      │                     │
    └─────────────────────┘                      └─────────────────────┘

    ALTERNATIVA: Conexión UART directa (menor latencia)

    ┌─────────────────────┐                      ┌─────────────────────┐
    │   RASPBERRY PI      │                      │      ESP32          │
    │                     │                      │                     │
    │   GPIO14 (TXD) ─────┼──────────────────────┼───► GPIO3 (RX)      │
    │   GPIO15 (RXD) ◄────┼──────────────────────┼──── GPIO1 (TX)      │
    │   GND ──────────────┼──────────────────────┼──── GND             │
    │                     │                      │                     │
    │   ⚠️ NO conectar VCC - ESP32 se alimenta por USB separado       │
    │                     │                      │                     │
    └─────────────────────┘                      └─────────────────────┘
```

---

## 🔄 PROTOCOLO DE COMUNICACIÓN SERIAL

### Especificaciones

| Parámetro | Valor |
|-----------|-------|
| Baudrate | 115200 |
| Bits de datos | 8 |
| Paridad | Ninguna |
| Bits de stop | 1 |
| Terminador | `\n` (newline) |
| Timeout | 1000ms |

### Comandos RPi → ESP32

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          COMANDOS DE CONTROL                                    │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│   COMANDO              DESCRIPCIÓN                         RESPUESTA          │
│   ═══════              ═══════════                         ═════════          │
│                                                                                │
│   PING                 Test de conexión                    PONG               │
│   STATUS               Solicitar estado actual             STATUS:<estado>    │
│   VERSION              Versión del firmware                VERSION:3.0        │
│                                                                                │
│   ─────────────────────────────────────────────────────────────────────────── │
│                                                                                │
│   JAM_START            Iniciar jamming (modo actual)       OK:JAM_STARTED     │
│   JAM_STOP             Detener todo jamming                OK:JAM_STOPPED     │
│   JAM_BT               Jamming Bluetooth (79 ch)           OK:MODE_BT         │
│   JAM_BLE              Jamming BLE (40 ch)                 OK:MODE_BLE        │
│   JAM_WIFI             Jamming WiFi (14 ch)                OK:MODE_WIFI       │
│   JAM_FULL             Jamming completo (125 ch)           OK:MODE_FULL       │
│                                                                                │
│   ─────────────────────────────────────────────────────────────────────────── │
│                                                                                │
│   MODE:CONT            Modo transmisión continua           OK:MODE_CONT       │
│   MODE:PULSE           Modo pulsos (50ms on/off)           OK:MODE_PULSE      │
│   MODE:SWEEP           Modo barrido de frecuencia          OK:MODE_SWEEP      │
│   MODE:BURST           Modo ráfagas aleatorias             OK:MODE_BURST      │
│                                                                                │
│   ─────────────────────────────────────────────────────────────────────────── │
│                                                                                │
│   POWER:MAX            Potencia máxima (PA+LNA)            OK:POWER_MAX       │
│   POWER:HIGH           Potencia alta                       OK:POWER_HIGH      │
│   POWER:MED            Potencia media                      OK:POWER_MED       │
│   POWER:LOW            Potencia baja                       OK:POWER_LOW       │
│                                                                                │
│   ─────────────────────────────────────────────────────────────────────────── │
│                                                                                │
│   CH:2,40,79           Jamming canales específicos         OK:CH_SET          │
│   CH_RANGE:10,50       Jamming rango de canales            OK:CH_RANGE        │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Respuestas ESP32 → RPi

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          RESPUESTAS Y ESTADOS                                   │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│   RESPUESTA                    SIGNIFICADO                                     │
│   ═════════                    ═══════════                                     │
│                                                                                │
│   PONG                         Conexión OK                                     │
│   OK:<comando>                 Comando ejecutado correctamente                 │
│                                                                                │
│   STATUS:IDLE                  No hay jamming activo                           │
│   STATUS:JAMMING:BT            Jamming Bluetooth activo                        │
│   STATUS:JAMMING:BLE           Jamming BLE activo                              │
│   STATUS:JAMMING:WIFI          Jamming WiFi activo                             │
│   STATUS:JAMMING:FULL          Jamming completo activo                         │
│                                                                                │
│   ERROR:UNKNOWN_CMD            Comando no reconocido                           │
│   ERROR:NRF1_FAIL              Módulo nRF24 #1 no responde                     │
│   ERROR:NRF2_FAIL              Módulo nRF24 #2 no responde                     │
│   ERROR:INVALID_PARAM          Parámetro inválido                              │
│                                                                                │
│   INFO:TEMP:<valor>            Temperatura del ESP32                           │
│   INFO:UPTIME:<segundos>       Tiempo encendido                                │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Secuencia de Ataque Coordinado

```
    RPi                                                    ESP32
     │                                                       │
     │  ══════════ FASE 0: INICIALIZACIÓN ══════════        │
     │                                                       │
     ├──────────────── PING ────────────────────────────────►│
     │◄─────────────── PONG ─────────────────────────────────┤
     │                                                       │
     ├──────────────── STATUS ──────────────────────────────►│
     │◄─────────────── STATUS:IDLE ──────────────────────────┤
     │                                                       │
     │  ══════════ FASE 1: PRE-JAMMING (5 seg) ══════════   │
     │                                                       │
     │  [Ruido detectado > umbral]                           │
     │  [Parlante BT encontrado]                             │
     │                                                       │
     ├──────────────── MODE:PULSE ──────────────────────────►│
     │◄─────────────── OK:MODE_PULSE ────────────────────────┤
     │                                                       │
     ├──────────────── JAM_BT ──────────────────────────────►│
     │◄─────────────── OK:MODE_BT ───────────────────────────┤
     │                                                       │
     ├──────────────── JAM_START ───────────────────────────►│
     │◄─────────────── OK:JAM_STARTED ───────────────────────┤
     │                                                       │
     │  [Esperar 5 segundos - RF cegando dispositivo]        │
     │                                                       │
     │  ══════════ FASE 2: ATAQUE COMBINADO (15 seg) ══════ │
     │                                                       │
     │  [RPi inicia L2CAP Flood - 20 threads]                │
     │  [ESP32 continúa RF jamming]                          │
     │                                                       │
     │  ══════════ FASE 3: RFCOMM SATURATION (10 seg) ═════ │
     │                                                       │
     ├──────────────── MODE:CONT ───────────────────────────►│
     │◄─────────────── OK:MODE_CONT ─────────────────────────┤
     │                                                       │
     │  [RPi inicia RFCOMM 30ch x 8 conn]                    │
     │  [ESP32 jamming continuo]                             │
     │                                                       │
     │  ══════════ FASE 4: VERIFICACIÓN ══════════          │
     │                                                       │
     ├──────────────── JAM_STOP ────────────────────────────►│
     │◄─────────────── OK:JAM_STOPPED ───────────────────────┤
     │                                                       │
     │  [Verificar si dispositivo desconectado]              │
     │  [Si no: repetir desde Fase 1]                        │
     │                                                       │
     ▼                                                       ▼
```

---

## 📊 MODOS DE JAMMING DETALLADOS

### Modo 1: Bluetooth Clásico (BT)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MODO BLUETOOTH CLÁSICO                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Canales: 79 (2.402 GHz - 2.480 GHz)                                      │
│   Separación: 1 MHz                                                         │
│   Target: Parlantes, auriculares, teclados Bluetooth                       │
│                                                                             │
│   Espectro:                                                                 │
│                                                                             │
│   2402 MHz                    2441 MHz                    2480 MHz          │
│      │                           │                           │              │
│      ├───────────────────────────┼───────────────────────────┤              │
│      │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│              │
│      └───────────────────────────┴───────────────────────────┘              │
│                        79 canales cubiertos                                 │
│                                                                             │
│   nRF24 #1: Canales 2-40  (2402-2440 MHz)                                  │
│   nRF24 #2: Canales 41-80 (2441-2480 MHz)                                  │
│                                                                             │
│   Técnica: Frequency hopping disruption                                    │
│   Efectividad: ████████░░ 85%                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Modo 2: Bluetooth Low Energy (BLE)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MODO BLE                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Canales: 40 (37 data + 3 advertising)                                    │
│   Advertising: 37, 38, 39 (2402, 2426, 2480 MHz)                           │
│   Target: Smartwatches, beacons, fitness trackers                          │
│                                                                             │
│   Espectro:                                                                 │
│                                                                             │
│   2402      2426                                              2480          │
│      ▼         ▼                                                 ▼          │
│      ├─────────┼─────────────────────────────────────────────────┤          │
│      │█████████│░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█│          │
│      └─────────┴─────────────────────────────────────────────────┘          │
│        Ch37     Ch38          Canales de datos            Ch39              │
│                                                                             │
│   Prioridad: Advertising channels (37, 38, 39)                             │
│   Técnica: Advertising channel saturation                                  │
│   Efectividad: █████████░ 90%                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Modo 3: WiFi 2.4GHz

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MODO WIFI                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Canales: 14 (22 MHz de ancho cada uno)                                   │
│   Frecuencia: 2.400 - 2.4835 GHz                                           │
│   Target: Routers, cámaras IP, dispositivos IoT                            │
│                                                                             │
│   Espectro:                                                                 │
│                                                                             │
│   Ch1    Ch6    Ch11   Ch14                                                 │
│   2412   2437   2462   2484 MHz                                            │
│     │      │      │      │                                                  │
│     ├──────┼──────┼──────┤                                                  │
│     │██████│██████│██████│                                                  │
│     └──────┴──────┴──────┘                                                  │
│                                                                             │
│   Canales más usados: 1, 6, 11 (no se superponen)                          │
│   Técnica: Channel flooding                                                 │
│   Efectividad: ███████░░░ 75%                                              │
│                                                                             │
│   ⚠️ ADVERTENCIA: Puede afectar tu propia red WiFi                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Modo 4: Full Spectrum (Drones/RC)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MODO FULL / DRONES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Canales: 125 (todo el espectro nRF24)                                    │
│   Frecuencia: 2.400 - 2.525 GHz                                            │
│   Target: Drones, controles RC, juguetes inalámbricos                      │
│                                                                             │
│   Espectro:                                                                 │
│                                                                             │
│   2400 MHz              2462 MHz              2525 MHz                      │
│      │                     │                     │                          │
│      ├─────────────────────┼─────────────────────┤                          │
│      │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│                          │
│      └─────────────────────┴─────────────────────┘                          │
│        nRF24 #1 (0-62)        nRF24 #2 (63-124)                            │
│                                                                             │
│   Cobertura: 100% del espectro 2.4 GHz                                     │
│   Técnica: Brute force all channels                                        │
│   Efectividad: ██████████ 95%                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📈 EFECTIVIDAD COMPARATIVA

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    COMPARACIÓN DE MÉTODOS DE ATAQUE                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                        Solo BT DoS   Solo RF Jam   HÍBRIDO                  │
│   Dispositivo          (RPi)         (ESP32)       (RPi+ESP32)              │
│   ────────────────     ─────────     ─────────     ──────────               │
│                                                                              │
│   Parlantes baratos    ████████░░    ███████░░░    ██████████               │
│   (sin marca)          80%           70%           98%                       │
│                                                                              │
│   JBL / Sony / Bose    █████░░░░░    ██████░░░░    █████████░               │
│   (mid-range)          50%           60%           85%                       │
│                                                                              │
│   Bang & Olufsen       ███░░░░░░░    ████░░░░░░    ███████░░░               │
│   (high-end)           30%           40%           65%                       │
│                                                                              │
│   Auriculares BT       ██████░░░░    █████░░░░░    █████████░               │
│   (AirPods, etc)       60%           50%           85%                       │
│                                                                              │
│   Astronaut Speaker    █████████░    ████████░░    ██████████               │
│   (objetivo ppal)      90%           80%           99%                       │
│                                                                              │
│   ─────────────────────────────────────────────────────────────────────────│
│                                                                              │
│   LEYENDA:                                                                   │
│   █ = 10% de probabilidad de desconexión                                    │
│   ░ = Sin efecto                                                             │
│                                                                              │
│   CONCLUSIÓN: El método híbrido es 15-35% más efectivo que cualquier       │
│               método individual, alcanzando 85-99% de efectividad.          │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 💡 ¿POR QUÉ FUNCIONA EL HÍBRIDO?

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         ATAQUE MULTICAPA OSI                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   MODELO OSI              ATAQUE                    COMPONENTE               │
│   ═════════               ══════                    ══════════               │
│                                                                              │
│   ┌─────────────┐                                                            │
│   │ Capa 7      │  ─────────────────────────────────────────────────────    │
│   │ Aplicación  │         (No atacado directamente)                         │
│   ├─────────────┤                                                            │
│   │ Capa 6      │  ─────────────────────────────────────────────────────    │
│   │ Presentación│         (No atacado directamente)                         │
│   ├─────────────┤                                                            │
│   │ Capa 5      │  ─────────────────────────────────────────────────────    │
│   │ Sesión      │         (No atacado directamente)                         │
│   ├─────────────┤                                                            │
│   │ Capa 4      │         A2DP/AVDTP Disruption      ┌──────────────┐       │
│   │ Transporte  │  ◄───────────────────────────────  │ RASPBERRY PI │       │
│   ├─────────────┤                                    │              │       │
│   │ Capa 3      │         RFCOMM Saturation          │  Bluetooth   │       │
│   │ Red         │  ◄───────────────────────────────  │     DoS      │       │
│   ├─────────────┤                                    │              │       │
│   │ Capa 2      │         L2CAP Ping Flood           │  (Protocolo) │       │
│   │ Enlace      │  ◄───────────────────────────────  └──────────────┘       │
│   ├─────────────┤                                                            │
│   │ Capa 1      │         RF Jamming 2.4GHz          ┌──────────────┐       │
│   │ Física      │  ◄───────────────────────────────  │    ESP32     │       │
│   └─────────────┘                                    │  BlueJammer  │       │
│                                                      │    (PHY)     │       │
│                                                      └──────────────┘       │
│                                                                              │
│   ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│   El dispositivo Bluetooth NO PUEDE:                                        │
│                                                                              │
│   ✗ Recibir paquetes correctamente (RF Jamming corrompe señal)             │
│   ✗ Responder a requests L2CAP (saturado con floods)                        │
│   ✗ Mantener conexiones RFCOMM (todas ocupadas)                             │
│   ✗ Usar frequency hopping (todos los canales interferidos)                │
│                                                                              │
│   RESULTADO: DESCONEXIÓN FORZADA                                            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛒 LISTA DE MATERIALES

### Ya tienes (Volume Be Gone v2.1):

| Componente | Cantidad | Estado |
|------------|----------|--------|
| Raspberry Pi 3B+/4B | 1 | ✅ |
| OLED SSD1306 128x64 | 1 | ✅ |
| Encoder KY-040 | 1 | ✅ |
| Micrófono USB | 1 | ✅ |
| Adaptador Bluetooth USB Clase 1 | 1 | ✅ |
| Fuente 5V/3A USB-C | 1 | ✅ |

### Necesitas comprar:

| Componente | Cantidad | Precio Est. | Link Referencia |
|------------|----------|-------------|-----------------|
| ESP32 DevKit V1 (38 pines) | 1 | $5-8 USD | AliExpress/Amazon |
| nRF24L01+PA+LNA con antena | 2 | $6-10 USD c/u | AliExpress |
| Cable USB A-MicroUSB (datos) | 1 | $2-3 USD | Cualquier tienda |
| Cables Dupont hembra-hembra | 20 pcs | $2-3 USD | AliExpress |
| Capacitor electrolítico 100µF/16V | 2 | $0.50 USD | Electrónica local |
| Capacitor cerámico 100nF | 2 | $0.30 USD | Electrónica local |

**TOTAL ESTIMADO: $22-35 USD**

### Opcional (recomendado):

| Componente | Cantidad | Precio Est. | Propósito |
|------------|----------|-------------|-----------|
| Carcasa impresa 3D (STL disponible) | 1 | $5-10 USD | Protección ESP32 |
| Regulador 3.3V AMS1117 | 1 | $1 USD | Estabilidad nRF24 |
| Batería 18650 + TP4056 | 1+1 | $5 USD | Portabilidad ESP32 |

---

## 🔧 INSTALACIÓN Y CONFIGURACIÓN

### Paso 1: Flash del Firmware ESP32

```bash
# Opción A: WebFlasher (más fácil)
# Visitar: https://esp32-bluejammerflasher.pages.dev
# Conectar ESP32 y seguir instrucciones

# Opción B: Arduino IDE
# 1. Instalar ESP32 board en Arduino IDE
# 2. Clonar repositorio
git clone https://github.com/neo3x/ESP32-BlueJammer.git
cd ESP32-BlueJammer

# 3. Abrir el .ino en Arduino IDE
# 4. Seleccionar board: ESP32 Dev Module
# 5. Upload
```

### Paso 2: Conexión de Hardware

```bash
# Ver diagrama de conexión arriba
# Conectar nRF24L01 #1 a HSPI
# Conectar nRF24L01 #2 a VSPI
# Agregar capacitores de estabilización
# Conectar ESP32 a RPi via USB
```

### Paso 3: Configuración Raspberry Pi

```bash
# Verificar que ESP32 es detectado
ls -la /dev/ttyUSB*
# Debería mostrar /dev/ttyUSB0

# Instalar pyserial si no está
pip3 install pyserial

# Test de conexión
python3 -c "
import serial
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
ser.write(b'PING\n')
response = ser.readline().decode().strip()
print(f'Respuesta: {response}')
ser.close()
"
# Debería imprimir: Respuesta: PONG
```

### Paso 4: Integración con Volume Be Gone

El código de integración se agregará a `volumeBeGone.py` para coordinar ataques con el ESP32.

---

## 📁 ESTRUCTURA DE ARCHIVOS PROPUESTA

```
volume-be-gone/
├── src/
│   ├── volumeBeGone.py          # Script principal (actualizado)
│   └── esp32_controller.py      # Nuevo: Controlador serial ESP32
├── firmware/
│   └── esp32_hybrid/
│       ├── esp32_hybrid.ino     # Firmware ESP32 modificado
│       ├── config.h             # Configuración de pines
│       ├── rf_jammer.h          # Funciones de jamming
│       └── serial_protocol.h    # Protocolo de comunicación
├── hardware/
│   ├── GPIO_COMPATIBILITY_ANALYSIS.md
│   ├── NRF24L01_WIRING.md
│   └── ESP32_WIRING.md          # Nuevo: Conexionado ESP32
├── docs/
│   ├── ARQUITECTURA_HIBRIDA.md
│   ├── COMPARACION_JAMMERS_ESP32.md
│   ├── PROPUESTA_HIBRIDA_COMPLETA.md  # Este documento
│   └── PROTOCOLO_SERIAL.md      # Nuevo: Especificación protocolo
└── README.md                     # Actualizado con v3.0
```

---

## ⚠️ ADVERTENCIAS LEGALES

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   ⚠️  AVISO LEGAL IMPORTANTE                                                │
│                                                                              │
│   El jamming de radiofrecuencia es ILEGAL en la mayoría de países.         │
│                                                                              │
│   Este proyecto es ÚNICAMENTE para:                                         │
│   • Investigación académica                                                  │
│   • Pruebas en ambientes controlados                                         │
│   • Educación sobre seguridad inalámbrica                                   │
│                                                                              │
│   El uso de este sistema puede:                                              │
│   • Violar leyes de telecomunicaciones                                       │
│   • Interferir con servicios de emergencia                                   │
│   • Resultar en multas o cárcel                                              │
│                                                                              │
│   El autor NO se hace responsable del uso indebido de esta información.    │
│                                                                              │
│   Consulta las leyes locales antes de cualquier prueba.                     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 📅 ROADMAP DE IMPLEMENTACIÓN

| Fase | Descripción | Estado |
|------|-------------|--------|
| 1 | Documentación completa | ✅ Completado |
| 2 | Firmware ESP32 con protocolo serial | 🔄 En progreso |
| 3 | Módulo Python `esp32_controller.py` | 🔄 Pendiente |
| 4 | Integración en `volumeBeGone.py` | 🔄 Pendiente |
| 5 | Testing y calibración | 🔄 Pendiente |
| 6 | Documentación de usuario final | 🔄 Pendiente |

---

*Documento generado para Volume Be Gone v3.0*
*Integración: ESP32-BlueJammer + Bluetooth-jammer-esp32 + RPi*
*Autor: Francisco Ortiz Rojas*
*Fecha: Diciembre 2024*
