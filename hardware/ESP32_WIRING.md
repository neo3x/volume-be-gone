# ESP32 BlueJammer - Guía de Conexionado

## Diagrama de Pines ESP32 DevKit V1

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
   EN  [●] 1  Reset                                                 38 [●] GPIO23 ──► MOSI (VSPI)
   VP  [○] 2  ADC                                                   37 [●] GPIO22 ──► CE nRF #2
   VN  [○] 3  ADC                                                   36 [○] TX0 (debug)
GPIO34 [○] 4  Input only                                            35 [○] RX0 (debug)
GPIO35 [○] 5  Input only                                            34 [●] GPIO21 ──► CSN nRF #2
GPIO32 [○] 6                                                        33 [●] GPIO19 ──► MISO (VSPI)
GPIO33 [○] 7                                                        32 [●] GPIO18 ──► SCK (VSPI)
GPIO25 [○] 8                                                        31 [○] GPIO5
GPIO26 [○] 9                                                        30 [○] GPIO17
GPIO27 [●]10 ──► LED Status                                         29 [●] GPIO16 ──► CE nRF #1
GPIO14 [●]11 ──► SCK (HSPI)                                         28 [○] GPIO4
GPIO12 [●]12 ──► MISO (HSPI)                                        27 [●] GPIO2 ──► LED interno
GPIO13 [●]13 ──► MOSI (HSPI)                                        26 [●] GPIO15 ──► CSN nRF #1
   GND [●]14 ──► GND común                                          25 [●] GND
   VIN [○]15                                                        24 [●] 3V3 ──► VCC nRF x2
   3V3 [●]16                                                        23 [○] GPIO8
        │                                                               │
        └───────────────────────────────────────────────────────────────┘

        [●] = Pin utilizado
        [○] = Pin libre
```

---

## Conexiones nRF24L01+PA+LNA

### Módulo #1 (HSPI) - Canales 0-62

```
    nRF24L01+PA+LNA                          ESP32
    ┌─────────────────┐                 ┌─────────────┐
    │                 │                 │             │
    │  [Antena SMA]   │                 │             │
    │       │         │                 │             │
    │  ┌────┴────┐    │                 │             │
    │  │ PA+LNA  │    │                 │             │
    │  └─────────┘    │                 │             │
    │                 │                 │             │
    │  ┌───────────┐  │                 │             │
    │  │ 1  2  3  4│  │                 │             │
    │  │ ○  ○  ○  ○│──┼─────────────────┼─────────────┤
    │  │ 5  6  7  8│  │                 │             │
    │  │ ○  ○  ○  ○│──┼─────────────────┼─────────────┤
    │  └───────────┘  │                 │             │
    │                 │                 │             │
    └─────────────────┘                 └─────────────┘

    Pin nRF24    Señal     ESP32 Pin    GPIO
    ─────────    ─────     ─────────    ────
    1 (GND)      GND       Pin 14       GND
    2 (VCC)      3.3V      Pin 24       3V3
    3 (CE)       CE        Pin 29       GPIO16
    4 (CSN)      CSN       Pin 26       GPIO15
    5 (SCK)      SCK       Pin 11       GPIO14
    6 (MOSI)     MOSI      Pin 13       GPIO13
    7 (MISO)     MISO      Pin 12       GPIO12
    8 (IRQ)      ---       No conectar
```

### Módulo #2 (VSPI) - Canales 63-124

```
    Pin nRF24    Señal     ESP32 Pin    GPIO
    ─────────    ─────     ─────────    ────
    1 (GND)      GND       Pin 25       GND
    2 (VCC)      3.3V      Pin 24       3V3 (compartido)
    3 (CE)       CE        Pin 37       GPIO22
    4 (CSN)      CSN       Pin 34       GPIO21
    5 (SCK)      SCK       Pin 32       GPIO18
    6 (MOSI)     MOSI      Pin 38       GPIO23
    7 (MISO)     MISO      Pin 33       GPIO19
    8 (IRQ)      ---       No conectar
```

---

## Pinout nRF24L01+PA+LNA

```
    Vista superior del módulo nRF24L01+PA+LNA:

    ┌─────────────────────────────────────────┐
    │                                         │
    │              [ANTENA SMA]               │
    │                  │                      │
    │            ┌─────┴─────┐                │
    │            │  PA+LNA   │                │
    │            │  Chip     │                │
    │            └───────────┘                │
    │                                         │
    │    ┌───┐                                │
    │    │   │  nRF24L01+                     │
    │    │   │  Chip                          │
    │    └───┘                                │
    │                                         │
    │    ┌─────────────────────────┐          │
    │    │  1   2   3   4         │          │
    │    │  ○   ○   ○   ○         │          │
    │    │ GND VCC CE  CSN        │          │
    │    │                        │          │
    │    │  5   6   7   8         │          │
    │    │  ○   ○   ○   ○         │          │
    │    │ SCK MOSI MISO IRQ      │          │
    │    └─────────────────────────┘          │
    │                                         │
    └─────────────────────────────────────────┘

    Vista de pines (desde arriba):

         ┌─────────────────┐
         │ 1   2   3   4   │
    ─────┤ ●   ●   ●   ●   ├─────
         │GND VCC CE  CSN  │
         │                 │
         │ 5   6   7   8   │
    ─────┤ ●   ●   ●   ●   ├─────
         │SCK MOSI MISO IRQ│
         └─────────────────┘
```

---

## Circuito de Estabilización

**IMPORTANTE**: Los módulos nRF24L01+PA+LNA son muy sensibles a fluctuaciones de voltaje.

```
    Agregar capacitores entre VCC y GND de cada módulo:

                    ┌──────────────────────────────────────┐
                    │                                      │
    3.3V ───────────┼───┬────────────────┬─────────────────┼──► nRF24 VCC
                    │   │                │                 │
                    │  ─┴─              ─┴─                │
                    │  ───  100µF       ───  100nF         │
                    │   │                │                 │
    GND ────────────┼───┴────────────────┴─────────────────┼──► nRF24 GND
                    │                                      │
                    └──────────────────────────────────────┘

    Electrolítico    Cerámico
    100µF/16V        100nF
    (picos de        (ruido de
    corriente)       alta freq)
```

---

## Diagrama de Conexión Completo

```
                                    ESP32 DevKit V1
                            ┌─────────────────────────────┐
                            │                             │
                            │   ┌─────────────────────┐   │
                            │   │       USB-C         │   │
                            │   └──────────┬──────────┘   │
                            │              │              │
                            │     (Alimentación +         │
                            │      Serial a RPi)          │
                            │                             │
    ┌───────────────────────┤                             ├───────────────────────┐
    │                       │                             │                       │
    │   nRF24L01 #1         │                             │         nRF24L01 #2   │
    │   ═══════════         │                             │         ═══════════   │
    │                       │                             │                       │
    │   ┌─────────┐         │                             │         ┌─────────┐   │
    │   │ ANTENA  │         │                             │         │ ANTENA  │   │
    │   └────┬────┘         │                             │         └────┬────┘   │
    │        │              │                             │              │        │
    │   ┌────┴────┐         │                             │         ┌────┴────┐   │
    │   │ PA+LNA  │         │                             │         │ PA+LNA  │   │
    │   └─────────┘         │                             │         └─────────┘   │
    │        │              │                             │              │        │
    │   GND ─┼──────────────┼── GPIO14 (Pin 14) ──────────┼──────────────┼─ GND   │
    │   VCC ─┼──────────────┼── 3V3 (Pin 24) ─────────────┼──────────────┼─ VCC   │
    │   CE  ─┼──────────────┼── GPIO16 (Pin 29) ──────────┼──            │        │
    │   CSN ─┼──────────────┼── GPIO15 (Pin 26) ──────────┼──            │        │
    │   SCK ─┼──────────────┼── GPIO14 (Pin 11) ──────────┼──            │        │
    │   MOSI─┼──────────────┼── GPIO13 (Pin 13) ──────────┼──            │        │
    │   MISO─┼──────────────┼── GPIO12 (Pin 12) ──────────┼──            │        │
    │        │              │                             │              │        │
    │        │              │                             │  ────────────┼─ CE    │
    │        │              │              GPIO22 (Pin 37)┼──────────────┼─ CSN   │
    │        │              │              GPIO21 (Pin 34)┼──────────────┼─ SCK   │
    │        │              │              GPIO18 (Pin 32)┼──────────────┼─ MOSI  │
    │        │              │              GPIO23 (Pin 38)┼──────────────┼─ MISO  │
    │        │              │              GPIO19 (Pin 33)┼──            │        │
    │        │              │                             │              │        │
    │   ┌────┴────┐         │                             │         ┌────┴────┐   │
    │   │ 100µF + │         │                             │         │ 100µF + │   │
    │   │  100nF  │         │                             │         │  100nF  │   │
    │   └─────────┘         │                             │         └─────────┘   │
    │                       │                             │                       │
    │   HSPI Bus            │                             │            VSPI Bus   │
    │   Canales 0-62        │                             │         Canales 63-124│
    │   (2400-2462 MHz)     │                             │        (2463-2524 MHz)│
    │                       │                             │                       │
    └───────────────────────┤                             ├───────────────────────┘
                            │         ┌───────┐           │
                            │         │GPIO27 │───► LED   │
                            │         │       │   (4.7kΩ) │
                            │         │GPIO2  │───► LED   │
                            │         │       │  (interno)│
                            │         └───────┘           │
                            │                             │
                            └─────────────────────────────┘
```

---

## Conexión a Raspberry Pi

### Opción 1: USB (Recomendada)

```
    RASPBERRY PI                           ESP32
    ════════════                           ═════

    ┌─────────────────┐                   ┌─────────────────┐
    │                 │                   │                 │
    │   Puerto USB    │═══════════════════│   Puerto USB    │
    │                 │   Cable USB       │                 │
    │  /dev/ttyUSB0   │   (Datos+Power)   │   Serial        │
    │                 │                   │   115200 baud   │
    └─────────────────┘                   └─────────────────┘

    Ventajas:
    ✅ Simple - solo un cable
    ✅ Alimentación incluida
    ✅ Plug and play
```

### Opción 2: UART Directo (Menor latencia)

```
    RASPBERRY PI                           ESP32
    ════════════                           ═════

    ┌─────────────────┐                   ┌─────────────────┐
    │                 │                   │                 │
    │   GPIO14 (TXD) ─┼───────────────────┼─► GPIO3 (RX)   │
    │   GPIO15 (RXD) ◄┼───────────────────┼── GPIO1 (TX)   │
    │   GND ──────────┼───────────────────┼── GND          │
    │                 │                   │                 │
    │   NO conectar   │                   │   Alimentar    │
    │   VCC           │                   │   por USB      │
    │                 │                   │   separado     │
    └─────────────────┘                   └─────────────────┘

    Ventajas:
    ✅ Menor latencia
    ✅ Comunicación directa

    Desventajas:
    ❌ Requiere alimentación separada
    ❌ Más cables
```

---

## Lista de Materiales

| Componente | Cantidad | Notas |
|------------|----------|-------|
| ESP32 DevKit V1 (38 pines) | 1 | CP2102 USB |
| nRF24L01+PA+LNA | 2 | Con antena SMA |
| Capacitor 100µF/16V | 2 | Electrolítico |
| Capacitor 100nF | 2 | Cerámico |
| LED 3mm | 1 | Color a elección |
| Resistor 4.7kΩ | 1 | Para LED |
| Cables Dupont H-H | 20 | Para conexiones |
| Cable USB A-MicroUSB | 1 | Con datos |

---

## Verificación de Conexiones

```bash
# En el ESP32, después de flashear el firmware:

# 1. Conectar por serial
screen /dev/ttyUSB0 115200

# 2. Enviar comando PING
PING
# Respuesta esperada: PONG

# 3. Verificar estado
STATUS
# Respuesta esperada: STATUS:IDLE

# 4. Verificar módulos nRF24
# (Los errores aparecerán durante el boot si hay problemas)
# ERROR:NRF1_FAIL  = Módulo 1 no detectado
# ERROR:NRF2_FAIL  = Módulo 2 no detectado
```

---

## Solución de Problemas

| Problema | Posible Causa | Solución |
|----------|---------------|----------|
| ESP32 no aparece en /dev/ttyUSB0 | Driver CH340/CP2102 | Instalar driver |
| ERROR:NRF1_FAIL | Conexión HSPI incorrecta | Verificar pines 11-13, 26, 29 |
| ERROR:NRF2_FAIL | Conexión VSPI incorrecta | Verificar pines 32-34, 37, 38 |
| Módulos inestables | Falta capacitores | Agregar 100µF + 100nF |
| Alcance reducido | Antena mal conectada | Verificar conector SMA |
| Reset aleatorio | Consumo excesivo | Usar fuente externa 3.3V |

---

*Documento de conexionado para ESP32 BlueJammer - Volume Be Gone v3.0*
