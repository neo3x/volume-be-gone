# Comparación de Repositorios ESP32 Jammer

## Tus Dos Repositorios

| Característica | Bluetooth-jammer-esp32 | ESP32-BlueJammer |
|----------------|------------------------|------------------|
| **Módulos nRF24** | 1-2 | 2 (optimizado) |
| **Buses SPI** | VSPI único | HSPI + VSPI simultáneo |
| **Pantalla OLED** | No | Sí (0.96" I2C) |
| **Modos de ataque** | Básico | BT/BLE/WiFi/Drones |
| **Carcasa 3D** | No | Sí (V3 y V4) |
| **WebFlasher** | Sí | Sí |
| **Alcance** | ~10-15m | ~30m+ |
| **Cambio de modo** | Código | Botón BOOT |
| **Documentación** | Básica | Completa |

---

## ESP32-BlueJammer - Características Avanzadas

### 1. Dual SPI Simultáneo (HSPI + VSPI)

```
┌─────────────────────────────────────────────────────────────────┐
│                      ESP32 - DUAL SPI                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   El ESP32 tiene DOS controladores SPI hardware:               │
│                                                                 │
│   ┌─────────────────┐              ┌─────────────────┐         │
│   │     HSPI        │              │     VSPI        │         │
│   │   (SPI Bus 2)   │              │   (SPI Bus 3)   │         │
│   │                 │              │                 │         │
│   │  Clock: 10MHz   │              │  Clock: 10MHz   │         │
│   │  Independiente  │              │  Independiente  │         │
│   └────────┬────────┘              └────────┬────────┘         │
│            │                                │                   │
│            ▼                                ▼                   │
│   ┌─────────────────┐              ┌─────────────────┐         │
│   │   nRF24L01 #1   │              │   nRF24L01 #2   │         │
│   │   Canales 0-62  │              │   Canales 63-124│         │
│   └─────────────────┘              └─────────────────┘         │
│                                                                 │
│   VENTAJA: Ambos módulos transmiten SIMULTÁNEAMENTE            │
│            sin compartir bus = DOBLE rendimiento               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Pinout Optimizado (ESP32-BlueJammer)

```
                         ESP32 DevKit
    ┌─────────────────────────────────────────────────────────────┐
    │                                                             │
    │   HSPI (nRF24L01 #1)              VSPI (nRF24L01 #2)       │
    │   ══════════════════              ══════════════════        │
    │                                                             │
    │   GPIO16 ──► CE                   GPIO22 ──► CE            │
    │   GPIO15 ──► CSN                  GPIO21 ──► CSN           │
    │   GPIO14 ──► SCK                  GPIO18 ──► SCK           │
    │   GPIO13 ──► MOSI                 GPIO23 ──► MOSI          │
    │   GPIO12 ──► MISO                 GPIO19 ──► MISO          │
    │                                                             │
    │   OLED I2C                        LED Status               │
    │   ═════════                       ══════════               │
    │   GPIO21 ──► SDA                  GPIO2  ──► LED (azul)    │
    │   GPIO22 ──► SCL                  + Resistor 4.7kΩ         │
    │                                                             │
    │   Botones                                                   │
    │   ════════                                                  │
    │   EN    ──► Reset                                          │
    │   BOOT  ──► Cambiar modo                                   │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘

    ⚠️ NOTA: GPIO21/22 se comparten entre VSPI y OLED
             Usar configuración alternativa si usas OLED
```

### 3. Modos de Firmware

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODOS DISPONIBLES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   MODO 1: Bluetooth Clásico                                    │
│   ─────────────────────────                                     │
│   • Canales: 79 (2.402 - 2.480 GHz)                            │
│   • Target: Parlantes, auriculares, teclados BT                │
│   • LED: 1 parpadeo                                            │
│                                                                 │
│   MODO 2: BLE (Bluetooth Low Energy)                           │
│   ────────────────────────────────────                          │
│   • Canales: 40 (advertising + data)                           │
│   • Target: Smartwatch, fitness trackers, beacons              │
│   • LED: 2 parpadeos                                           │
│                                                                 │
│   MODO 3: WiFi 2.4GHz                                          │
│   ───────────────────                                           │
│   • Canales: 1-14 (2.400 - 2.4835 GHz)                         │
│   • Target: Routers, cámaras IP, IoT                           │
│   • LED: 3 parpadeos                                           │
│                                                                 │
│   MODO 4: Drones/RC                                            │
│   ─────────────────                                             │
│   • Canales: 1-125 (2.400 - 2.525 GHz)                         │
│   • Target: Drones, controles RC, juguetes                     │
│   • LED: 4 parpadeos                                           │
│                                                                 │
│   MODO COMBO: Cambio con botón BOOT                            │
│   ─────────────────────────────────                             │
│   • Presionar BOOT = siguiente modo                            │
│   • LED indica modo actual                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4. Mapeo de Canales

```
                    ESPECTRO 2.4 GHz - COBERTURA POR MODO
    ═══════════════════════════════════════════════════════════════

    2400 MHz              2450 MHz              2500 MHz   2525 MHz
       │                     │                     │          │
       ├─────────────────────┼─────────────────────┼──────────┤
       │                     │                     │          │
       │◄──────── MODO 1: Bluetooth Clásico ─────►│          │
       │         79 canales (2402-2480)           │          │
       │                                          │          │
       │◄────────── MODO 2: BLE ─────────────────►│          │
       │         40 canales (2400-2483.5)         │          │
       │                                          │          │
       │◄────────── MODO 3: WiFi ────────────────►│          │
       │         14 canales (2400-2483.5)         │          │
       │                                                      │
       │◄──────────────── MODO 4: Drones/RC ─────────────────►│
       │              125 canales (2400-2525)                 │
       │                                                      │


    nRF24L01 #1 (HSPI)                nRF24L01 #2 (VSPI)
    ┌────────────────────┐            ┌────────────────────┐
    │ Canales 0-62       │            │ Canales 63-124     │
    │ 2400-2462 MHz      │            │ 2463-2524 MHz      │
    └────────────────────┘            └────────────────────┘
             │                                 │
             └─────────────┬───────────────────┘
                           │
                           ▼
                 COBERTURA COMPLETA
                    2400-2525 MHz
```

---

## Arquitectura Mejorada para Volume Be Gone v3.0

### Usando ESP32-BlueJammer como base

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                    VOLUME BE GONE v3.0 - ARQUITECTURA FINAL                  │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────┐    ┌─────────────────────────────────┐│
│   │        RASPBERRY PI             │    │      ESP32-BlueJammer           ││
│   │        (CEREBRO)                │    │      (RF JAMMER)                ││
│   │                                 │    │                                 ││
│   │  ┌───────┐ ┌───────┐ ┌───────┐ │    │  ┌─────────┐    ┌─────────┐    ││
│   │  │ OLED  │ │Encoder│ │  Mic  │ │    │  │nRF24 #1 │    │nRF24 #2 │    ││
│   │  │Display│ │KY-040 │ │  USB  │ │    │  │ (HSPI)  │    │ (VSPI)  │    ││
│   │  └───┬───┘ └───┬───┘ └───┬───┘ │    │  └────┬────┘    └────┬────┘    ││
│   │      │         │         │     │    │       │              │         ││
│   │      └────┬────┴────┬────┘     │    │       └──────┬───────┘         ││
│   │           │         │          │    │              │                 ││
│   │           ▼         ▼          │    │              ▼                 ││
│   │  ┌─────────────────────────┐   │    │     ┌───────────────┐         ││
│   │  │   CONTROL PRINCIPAL     │   │    │     │  RF ENGINE    │         ││
│   │  │                         │   │    │     │               │         ││
│   │  │  • Monitor audio (dB)   │   │    │     │ • HSPI+VSPI   │         ││
│   │  │  • Umbral configurable  │   │    │     │ • 4 modos     │         ││
│   │  │  • UI interactiva       │   │    │     │ • Dual TX     │         ││
│   │  └───────────┬─────────────┘   │    │     └───────┬───────┘         ││
│   │              │                 │    │             │                 ││
│   │              ▼                 │    │             │                 ││
│   │  ┌─────────────────────────┐   │    │             │                 ││
│   │  │   BLUETOOTH DoS         │   │    │             │                 ││
│   │  │                         │   │    │             │                 ││
│   │  │  • L2CAP Flood          │   │    │             │                 ││
│   │  │  • RFCOMM Saturation    │   │    │             │                 ││
│   │  │  • A2DP Disruption      │   │    │             │                 ││
│   │  └───────────┬─────────────┘   │    │             │                 ││
│   │              │                 │    │             │                 ││
│   │              │                 │    │             │                 ││
│   │   ┌──────────┴──────────┐      │    │             │                 ││
│   │   │  USB Bluetooth      │      │    │             │                 ││
│   │   │  Adapter (Clase 1)  │      │    │             │                 ││
│   │   └──────────┬──────────┘      │    │             │                 ││
│   │              │                 │    │             │                 ││
│   └──────────────┼─────────────────┘    └─────────────┼─────────────────┘│
│                  │                                    │                  │
│                  │         ┌──────────────┐           │                  │
│                  │         │  USB Serial  │           │                  │
│                  │         │  115200 baud │           │                  │
│                  └─────────┤              ├───────────┘                  │
│                            │  Comandos:   │                              │
│                            │  JAM_START   │                              │
│                            │  JAM_STOP    │                              │
│                            │  MODE:BT     │                              │
│                            │  MODE:BLE    │                              │
│                            │  STATUS      │                              │
│                            └──────────────┘                              │
│                                                                          │
│                                   │                                      │
│                                   ▼                                      │
│                          ┌───────────────┐                               │
│                          │   OBJETIVO    │                               │
│                          │   ──────────  │                               │
│                          │               │                               │
│                          │  ┌─────────┐  │                               │
│                          │  │Parlante │  │                               │
│                          │  │   BT    │  │                               │
│                          │  └─────────┘  │                               │
│                          │               │                               │
│                          │  Recibe:      │                               │
│                          │  • L2CAP DoS  │                               │
│                          │  • RFCOMM DoS │                               │
│                          │  • RF Noise   │                               │
│                          │               │                               │
│                          └───────────────┘                               │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Mejoras de ESP32-BlueJammer vs Jammer Básico

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MEJORAS IDENTIFICADAS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. DUAL SPI INDEPENDIENTE                                                │
│   ═════════════════════════                                                 │
│                                                                             │
│   Básico:                          ESP32-BlueJammer:                       │
│   ┌─────────────┐                  ┌─────────────┐ ┌─────────────┐         │
│   │    VSPI     │                  │    HSPI     │ │    VSPI     │         │
│   │  (compartido)                  │(independiente) │(independiente)        │
│   │      │      │                  │      │      │ │      │      │         │
│   │   ┌──┴──┐   │                  │   ┌──┴──┐   │ │   ┌──┴──┐   │         │
│   │   │nRF1 │   │                  │   │nRF1 │   │ │   │nRF2 │   │         │
│   │   │nRF2 │   │                  │   └─────┘   │ │   └─────┘   │         │
│   │   └─────┘   │                  └─────────────┘ └─────────────┘         │
│   └─────────────┘                                                          │
│                                                                             │
│   Rendimiento: 1x                  Rendimiento: 2x (paralelo real)         │
│                                                                             │
│   ─────────────────────────────────────────────────────────────────────────│
│                                                                             │
│   2. MODOS ESPECIALIZADOS                                                  │
│   ═══════════════════════                                                   │
│                                                                             │
│   Básico:                          ESP32-BlueJammer:                       │
│   • Solo jamming general           • Modo BT Clásico (79 ch)               │
│   • Sin optimización               • Modo BLE (40 ch)                      │
│                                    • Modo WiFi (14 ch)                     │
│                                    • Modo Drones (125 ch)                  │
│                                    • Cambio con botón BOOT                 │
│                                                                             │
│   ─────────────────────────────────────────────────────────────────────────│
│                                                                             │
│   3. ALCANCE                                                               │
│   ══════════                                                                │
│                                                                             │
│   Básico:          ~10-15 metros                                           │
│   BlueJammer:      ~30+ metros (con antenas PA+LNA)                        │
│                                                                             │
│   ─────────────────────────────────────────────────────────────────────────│
│                                                                             │
│   4. INTERFAZ                                                              │
│   ═══════════                                                               │
│                                                                             │
│   Básico:                          ESP32-BlueJammer:                       │
│   • Sin feedback visual            • OLED 0.96" con estado                 │
│   • Sin indicadores                • LED con patrones por modo             │
│   • Ciego                          • Botones accesibles                    │
│                                                                             │
│   ─────────────────────────────────────────────────────────────────────────│
│                                                                             │
│   5. CARCASA 3D                                                            │
│   ═════════════                                                             │
│                                                                             │
│   Básico:          Sin carcasa                                             │
│   BlueJammer:      STL profesional (V3, V4)                                │
│                    • Acceso a USB                                          │
│                    • Acceso a botones                                      │
│                    • Ventilación                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Recomendación Final

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   USAR ESP32-BlueJammer COMO BASE                                          │
│   ════════════════════════════════                                          │
│                                                                             │
│   Razones:                                                                  │
│                                                                             │
│   ✅ Dual SPI (HSPI + VSPI) = 2x rendimiento                               │
│   ✅ 4 modos optimizados de jamming                                        │
│   ✅ Cambio de modo con botón (sin reprogramar)                            │
│   ✅ Carcasa 3D lista para imprimir                                        │
│   ✅ Documentación completa                                                │
│   ✅ WebFlasher disponible                                                 │
│   ✅ Mayor alcance (~30m vs ~15m)                                          │
│                                                                             │
│   Solo necesitas:                                                          │
│   ───────────────                                                          │
│   1. Agregar comunicación serial para recibir comandos de RPi              │
│   2. Crear protocolo de comandos (JAM_START, JAM_STOP, etc.)               │
│   3. Integrar con volumeBeGone.py                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Pinout Final Recomendado (ESP32-BlueJammer)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    ESP32 DevKit - PINOUT BLUEJAMMER                         │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   nRF24L01 #1 (HSPI)               nRF24L01 #2 (VSPI)                      │
│   ══════════════════               ══════════════════                       │
│   VCC  ◄── 3.3V                    VCC  ◄── 3.3V                           │
│   GND  ◄── GND                     GND  ◄── GND                            │
│   CE   ◄── GPIO16                  CE   ◄── GPIO22                         │
│   CSN  ◄── GPIO15                  CSN  ◄── GPIO21                         │
│   SCK  ◄── GPIO14                  SCK  ◄── GPIO18                         │
│   MOSI ◄── GPIO13                  MOSI ◄── GPIO23                         │
│   MISO ◄── GPIO12                  MISO ◄── GPIO19                         │
│                                                                             │
│   LED Status                       Capacitores                             │
│   ══════════                       ════════════                             │
│   GPIO2 ──► LED azul               10-100µF en cada nRF24                  │
│   + Resistor 4.7kΩ                 (entre VCC y GND)                       │
│                                                                             │
│   Comunicación Serial (para RPi)                                           │
│   ══════════════════════════════                                            │
│   GPIO1 (TX) ──► RPi GPIO15 (RX)                                           │
│   GPIO3 (RX) ◄── RPi GPIO14 (TX)                                           │
│   GND ────────── RPi GND                                                   │
│                                                                             │
│   O simplemente usar USB para Serial + Alimentación                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
