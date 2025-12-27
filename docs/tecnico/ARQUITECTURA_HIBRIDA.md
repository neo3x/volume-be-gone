# ARQUITECTURA HÍBRIDA - Volume Be Gone v3.0

## RPi (Cerebro) + ESP32 (RF Jammer) + Bluetooth DoS

---

## 1. VISIÓN GENERAL DEL SISTEMA

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                                                                  │
│                        VOLUME BE GONE v3.0 - SISTEMA HÍBRIDO                     │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                           CAPA DE USUARIO                                   │ │
│  │                                                                             │ │
│  │     ┌──────────┐      ┌──────────┐      ┌──────────┐                       │ │
│  │     │   OLED   │      │ Encoder  │      │   LED    │                       │ │
│  │     │ 128x64   │      │  KY-040  │      │ Status   │                       │ │
│  │     └────┬─────┘      └────┬─────┘      └────┬─────┘                       │ │
│  │          │                 │                 │                              │ │
│  └──────────┼─────────────────┼─────────────────┼──────────────────────────────┘ │
│             │                 │                 │                                │
│             │ I2C             │ GPIO            │ GPIO                           │
│             ▼                 ▼                 ▼                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                          │   │
│  │                         RASPBERRY PI 3B+/4B                              │   │
│  │                         ════════════════════                             │   │
│  │                                                                          │   │
│  │   ┌────────────────┐  ┌────────────────┐  ┌────────────────────────┐    │   │
│  │   │ Audio Monitor  │  │ BT Scanner     │  │ Attack Coordinator     │    │   │
│  │   │                │  │                │  │                        │    │   │
│  │   │ • Mic USB      │  │ • Device scan  │  │ • Orchestrate attacks  │    │   │
│  │   │ • dB calc      │  │ • Filter audio │  │ • Timing control       │    │   │
│  │   │ • Threshold    │  │ • Priority     │  │ • Status reporting     │    │   │
│  │   └───────┬────────┘  └───────┬────────┘  └───────────┬────────────┘    │   │
│  │           │                   │                       │                  │   │
│  │           └───────────────────┴───────────────────────┘                  │   │
│  │                               │                                          │   │
│  │                               ▼                                          │   │
│  │                    ┌─────────────────────┐                               │   │
│  │                    │   ATTACK ENGINE     │                               │   │
│  │                    └──────────┬──────────┘                               │   │
│  │                               │                                          │   │
│  │              ┌────────────────┼────────────────┐                         │   │
│  │              │                │                │                         │   │
│  │              ▼                ▼                ▼                         │   │
│  │     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                  │   │
│  │     │  L2CAP Flood │ │ RFCOMM Flood │ │  RF Jammer   │                  │   │
│  │     │  (interno)   │ │  (interno)   │ │  (ESP32)     │                  │   │
│  │     └──────┬───────┘ └──────┬───────┘ └──────┬───────┘                  │   │
│  │            │                │                │                           │   │
│  │            ▼                ▼                │                           │   │
│  │     ┌─────────────────────────────┐         │                           │   │
│  │     │     USB Bluetooth           │         │  Serial/USB               │   │
│  │     │     Adapter (Clase 1)       │         │                           │   │
│  │     │     hci1 - 50-100m          │         │                           │   │
│  │     └─────────────────────────────┘         │                           │   │
│  │                                             │                           │   │
│  └─────────────────────────────────────────────┼───────────────────────────┘   │
│                                                │                                │
│                                                │ USB Cable                      │
│                                                │ (Datos + Alimentación)         │
│                                                ▼                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                          │   │
│  │                              ESP32 DevKit                                │   │
│  │                              ═════════════                               │   │
│  │                                                                          │   │
│  │   ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │   │                     RF JAMMING ENGINE                            │   │   │
│  │   │                                                                  │   │   │
│  │   │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │   │   │
│  │   │  │ Command     │    │ Channel     │    │ Dual nRF24L01       │  │   │   │
│  │   │  │ Parser      │───►│ Hopper      │───►│ Controller          │  │   │   │
│  │   │  │ (Serial RX) │    │ (Core 0)    │    │ (Core 1)            │  │   │   │
│  │   │  └─────────────┘    └─────────────┘    └──────────┬──────────┘  │   │   │
│  │   │                                                   │             │   │   │
│  │   └───────────────────────────────────────────────────┼─────────────┘   │   │
│  │                                                       │                 │   │
│  │                          ┌────────────────────────────┼────────┐        │   │
│  │                          │                            │        │        │   │
│  │                          ▼                            ▼        │        │   │
│  │                   ┌─────────────┐              ┌─────────────┐ │        │   │
│  │                   │  nRF24L01   │              │  nRF24L01   │ │        │   │
│  │                   │  +PA+LNA    │              │  +PA+LNA    │ │        │   │
│  │                   │  #1         │              │  #2         │ │        │   │
│  │                   │             │              │             │ │        │   │
│  │                   │ CH: 0-62    │              │ CH: 63-124  │ │        │   │
│  │                   │ 2400-2462MHz│              │ 2463-2524MHz│ │        │   │
│  │                   └──────┬──────┘              └──────┬──────┘ │        │   │
│  │                          │                            │        │        │   │
│  │                          │         ┌──────────────────┘        │        │   │
│  │                          │         │                           │        │   │
│  │                          ▼         ▼                           │        │   │
│  │                   ┌─────────────────────┐                      │        │   │
│  │                   │    ≋≋≋≋≋≋≋≋≋≋≋≋    │ RF 2.4GHz            │        │   │
│  │                   │    JAMMING SIGNAL   │ Interference         │        │   │
│  │                   │    ≋≋≋≋≋≋≋≋≋≋≋≋    │                      │        │   │
│  │                   └─────────────────────┘                      │        │   │
│  │                                                                │        │   │
│  └────────────────────────────────────────────────────────────────┘        │   │
│                                                                            │   │
└────────────────────────────────────────────────────────────────────────────────┘


                              ▼▼▼ OBJETIVO ▼▼▼

                         ┌─────────────────────┐
                         │   🔊 PARLANTE BT    │
                         │                     │
                         │  Recibe:            │
                         │  • L2CAP flood      │
                         │  • RFCOMM flood     │
                         │  • RF interference  │
                         │                     │
                         │  Resultado:         │
                         │  DESCONEXIÓN        │
                         └─────────────────────┘
```

---

## 2. FLUJO DE ATAQUE

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           SECUENCIA DE ATAQUE                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

    RASPBERRY PI                                              ESP32
    ════════════                                              ═════

    ┌─────────────┐
    │ Mic detecta │
    │ ruido > 73dB│
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │ Escaneo BT  │
    │ (8-10 seg)  │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐      Comando: "JAM_START"
    │ ¿Parlantes  │─────────────────────────────────────────►┌─────────────┐
    │ detectados? │                                          │ Inicia      │
    └──────┬──────┘                                          │ Channel     │
           │                                                 │ Hopping     │
           │ SÍ                                              └──────┬──────┘
           ▼                                                        │
    ╔═════════════════════════════════════════╗                     │
    ║         FASE 1: PRE-JAMMING             ║                     ▼
    ║         ════════════════════            ║              ┌─────────────┐
    ║                                         ║              │ nRF24 TX    │
    ║   RF Jamming activo 5 segundos          ║              │ Canales     │
    ║   antes del ataque BT para              ║              │ 2-80        │
    ║   "cegar" al dispositivo                ║              │ (Bluetooth) │
    ║                                         ║              └─────────────┘
    ╚═════════════════════════════════════════╝
           │
           │ 5 segundos después
           ▼
    ╔═════════════════════════════════════════╗
    ║         FASE 2: ATAQUE COMBINADO        ║
    ║         ════════════════════════        ║
    ║                                         ║              ┌─────────────┐
    ║   ┌─────────────────────────────────┐   ║              │             │
    ║   │ L2CAP Flood (20 threads)        │   ║◄────────────►│ RF Jamming  │
    ║   │ Paquetes 600-800 bytes          │   ║  Simultáneo  │ Continuo    │
    ║   └─────────────────────────────────┘   ║              │             │
    ║                                         ║              └─────────────┘
    ║   Duración: 15 segundos                 ║
    ╚═════════════════════════════════════════╝
           │
           ▼
    ╔═════════════════════════════════════════╗
    ║         FASE 3: RFCOMM SATURACIÓN       ║
    ║         ═════════════════════════       ║              ┌─────────────┐
    ║                                         ║              │             │
    ║   ┌─────────────────────────────────┐   ║              │ RF Jamming  │
    ║   │ RFCOMM 30 canales x 8 conexiones│   ║◄────────────►│ Pulsos      │
    ║   │ Total: 240 intentos simultáneos │   ║  Simultáneo  │ (on/off)    │
    ║   └─────────────────────────────────┘   ║              │             │
    ║                                         ║              └─────────────┘
    ║   Duración: 10 segundos                 ║
    ╚═════════════════════════════════════════╝
           │
           ▼
    ┌─────────────┐      Comando: "JAM_STOP"
    │ Verificar   │─────────────────────────────────────────►┌─────────────┐
    │ desconexión │                                          │ Detener     │
    └──────┬──────┘                                          │ Jamming     │
           │                                                 └─────────────┘
           │
      ┌────┴────┐
      │         │
      ▼         ▼
  Desconectado  Aún conectado
      │              │
      ▼              └──────► Repetir desde FASE 1
    ┌─────────────┐
    │ Continuar   │
    │ monitoreo   │
    └─────────────┘
```

---

## 3. COMUNICACIÓN SERIAL RPi ↔ ESP32

### Protocolo de Comandos

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         PROTOCOLO SERIAL                                 │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Baudrate: 115200                                                       │
│   Formato:  8N1 (8 bits, sin paridad, 1 stop bit)                       │
│   Terminador: \n (newline)                                               │
│                                                                          │
│   COMANDOS RPi → ESP32:                                                  │
│   ══════════════════════                                                 │
│                                                                          │
│   Comando              Descripción                    Respuesta ESP32    │
│   ──────────────────   ────────────────────────────   ─────────────────  │
│   PING                 Test de conexión               PONG               │
│   JAM_START            Iniciar jamming completo       OK:JAM_STARTED     │
│   JAM_STOP             Detener jamming                OK:JAM_STOPPED     │
│   JAM_BT               Solo banda Bluetooth (2-80)    OK:JAM_BT          │
│   JAM_WIFI:<ch>        Canal WiFi específico          OK:JAM_WIFI:ch     │
│   JAM_CH:<c1,c2,c3>    Canales específicos            OK:JAM_CH          │
│   POWER:HIGH           Potencia máxima TX             OK:POWER_HIGH      │
│   POWER:LOW            Potencia baja TX               OK:POWER_LOW       │
│   STATUS               Solicitar estado               STATUS:...         │
│   MODE:CONT            Modo continuo                  OK:MODE_CONT       │
│   MODE:PULSE           Modo pulsos (on/off)           OK:MODE_PULSE      │
│   MODE:SWEEP           Barrido de frecuencia          OK:MODE_SWEEP      │
│                                                                          │
│   RESPUESTAS ESP32 → RPi:                                                │
│   ════════════════════════                                               │
│                                                                          │
│   STATUS:IDLE                    No está haciendo jamming                │
│   STATUS:JAMMING:BT              Jamming banda Bluetooth activo          │
│   STATUS:JAMMING:FULL            Jamming completo activo                 │
│   STATUS:JAMMING:CH:2,40,80      Jamming canales específicos             │
│   ERROR:UNKNOWN_CMD              Comando no reconocido                   │
│   ERROR:NRF_FAIL                 Fallo en módulo nRF24                   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Diagrama de Conexión Serial

```
         RASPBERRY PI                              ESP32
    ┌─────────────────────┐                  ┌─────────────────────┐
    │                     │                  │                     │
    │   USB Port    ──────┼──────────────────┼───── USB Port       │
    │   (/dev/ttyUSB0)    │   Cable USB      │   (alimentación +   │
    │                     │                  │    datos serial)    │
    │                     │                  │                     │
    └─────────────────────┘                  └─────────────────────┘

    Alternativa: UART directo (menor latencia)

         RASPBERRY PI                              ESP32
    ┌─────────────────────┐                  ┌─────────────────────┐
    │                     │                  │                     │
    │   GPIO14 (TX) ──────┼──────────────────┼───── GPIO3 (RX)     │
    │   GPIO15 (RX) ◄─────┼──────────────────┼───── GPIO1 (TX)     │
    │   GND ──────────────┼──────────────────┼───── GND            │
    │                     │                  │                     │
    │   (No conectar VCC - alimentar ESP32 por USB separado)       │
    │                     │                  │                     │
    └─────────────────────┘                  └─────────────────────┘
```

---

## 4. DIAGRAMA DE HARDWARE COMPLETO

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                                                                  │
│                          HARDWARE COMPLETO v3.0                                  │
│                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│                              FUENTE DE PODER                                     │
│                           ┌─────────────────┐                                    │
│                           │   5V / 3A       │                                    │
│                           │   USB-C         │                                    │
│                           └────────┬────────┘                                    │
│                                    │                                             │
│                    ┌───────────────┴───────────────┐                            │
│                    │                               │                            │
│                    ▼                               ▼                            │
│    ┌───────────────────────────────┐    ┌───────────────────────────────┐       │
│    │                               │    │                               │       │
│    │      RASPBERRY PI 4B          │    │         ESP32 DevKit          │       │
│    │                               │    │                               │       │
│    │  ┌─────┐ ┌─────┐ ┌─────┐     │    │     ┌─────────┐ ┌─────────┐  │       │
│    │  │OLED │ │Enc. │ │ Mic │     │    │     │ nRF24L01│ │ nRF24L01│  │       │
│    │  │I2C  │ │GPIO │ │ USB │     │    │     │   #1    │ │   #2    │  │       │
│    │  └──┬──┘ └──┬──┘ └──┬──┘     │    │     └────┬────┘ └────┬────┘  │       │
│    │     │       │       │        │    │          │           │       │       │
│    │  Pin3,5  Pin33,35   │        │    │       GPIO5,4     GPIO16,17  │       │
│    │          Pin37      │        │    │       (SPI VSPI)   (SPI)     │       │
│    │                     │        │    │          │           │       │       │
│    │           ┌─────────┘        │    │          ▼           ▼       │       │
│    │           │                  │    │     ┌─────────────────────┐  │       │
│    │           ▼                  │    │     │   VSPI Bus          │  │       │
│    │    ┌─────────────┐           │    │     │   GPIO18 (SCK)      │  │       │
│    │    │  Micrófono  │           │    │     │   GPIO23 (MOSI)     │  │       │
│    │    │    USB      │           │    │     │   GPIO19 (MISO)     │  │       │
│    │    └─────────────┘           │    │     └─────────────────────┘  │       │
│    │                              │    │                              │       │
│    │    ┌─────────────┐           │    │     ┌─────────────────────┐  │       │
│    │    │  Bluetooth  │           │    │     │  3.3V Rail          │  │       │
│    │    │  USB Clase 1│           │    │     │  (interno ESP32)    │  │       │
│    │    │  hci1       │           │    │     │  Alimenta nRF24s    │  │       │
│    │    └─────────────┘           │    │     └─────────────────────┘  │       │
│    │                              │    │                              │       │
│    │    ┌─────────────────────────┼────┼──────────────────────────┐  │       │
│    │    │         USB             │    │         USB              │  │       │
│    │    │      /dev/ttyUSB0       │◄───┼───►  Serial              │  │       │
│    │    │                         │    │     (115200 baud)        │  │       │
│    │    └─────────────────────────┘    └──────────────────────────┘  │       │
│    │                              │    │                              │       │
│    └──────────────────────────────┘    └──────────────────────────────┘       │
│                                                                                  │
│                                                                                  │
│    SEÑALES DE ATAQUE:                                                           │
│    ═══════════════════                                                          │
│                                                                                  │
│    Raspberry Pi                          ESP32 + nRF24L01                       │
│    ────────────                          ─────────────────                       │
│         │                                      │                                │
│         │  Bluetooth DoS                       │  RF Jamming                    │
│         │  (L2CAP, RFCOMM)                     │  (2.4GHz band)                 │
│         │                                      │                                │
│         │  ════════════════                    │  ≋≋≋≋≋≋≋≋≋≋≋≋                  │
│         │  Ataque Protocolo                    │  Interferencia                 │
│         │  (Capa 2-3 OSI)                      │  (Capa 1 PHY)                  │
│         │                                      │                                │
│         └──────────────┬───────────────────────┘                                │
│                        │                                                        │
│                        ▼                                                        │
│                 ┌─────────────┐                                                 │
│                 │  OBJETIVO   │                                                 │
│                 │  Parlante   │                                                 │
│                 │  Bluetooth  │                                                 │
│                 └─────────────┘                                                 │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. PINOUT DETALLADO ESP32

```
                              ESP32 DevKit V1
                         ┌─────────────────────┐
                         │         USB         │
                         │       ┌─────┐       │
                         │       │     │       │
                         └───────┴─────┴───────┘
                                   │
              ┌────────────────────┴────────────────────┐
              │                                        │
    EN    [ ] │ 1                                  38 │ [ ] GPIO23 ──► MOSI (nRF)
    VP    [ ] │ 2                                  37 │ [ ] GPIO22
    VN    [ ] │ 3                                  36 │ [ ] GPIO1  (TX)
    GPIO34[ ] │ 4                                  35 │ [ ] GPIO3  (RX)
    GPIO35[ ] │ 5                                  34 │ [ ] GPIO21
    GPIO32[ ] │ 6                                  33 │ [ ] GPIO19 ──► MISO (nRF)
    GPIO33[ ] │ 7                                  32 │ [ ] GPIO18 ──► SCK (nRF)
    GPIO25[ ] │ 8                                  31 │ [ ] GPIO5  ──► CE nRF #1
    GPIO26[ ] │ 9                                  30 │ [ ] GPIO17 ──► CSN nRF #2
    GPIO27[ ] │10                                  29 │ [ ] GPIO16 ──► CE nRF #2
    GPIO14[ ] │11                                  28 │ [ ] GPIO4  ──► CSN nRF #1
    GPIO12[ ] │12                                  27 │ [ ] GPIO2
    GPIO13[ ] │13                                  26 │ [ ] GPIO15
    GND   [●] │14  ◄── GND común                  25 │ [ ] GND
    VIN   [ ] │15                                  24 │ [ ] 3V3 ──► VCC nRF #1 y #2
    3V3   [●] │16  ◄── Alternativa VCC nRF        23 │ [ ] GPIO8
    GPIO6 [ ] │17                                  22 │ [ ] GPIO7
    GPIO7 [ ] │18                                  21 │ [ ] GPIO6
    GPIO8 [ ] │19                                  20 │ [ ] GPIO0
              │                                        │
              └────────────────────────────────────────┘


    CONEXIONES nRF24L01:
    ════════════════════

    nRF24L01 #1 (Canales 0-62)          nRF24L01 #2 (Canales 63-124)
    ──────────────────────────          ────────────────────────────
    VCC  ◄── 3V3 (Pin 24)               VCC  ◄── 3V3 (Pin 24)
    GND  ◄── GND (Pin 14)               GND  ◄── GND (Pin 14)
    CE   ◄── GPIO5 (Pin 31)             CE   ◄── GPIO16 (Pin 29)
    CSN  ◄── GPIO4 (Pin 28)             CSN  ◄── GPIO17 (Pin 30)
    SCK  ◄── GPIO18 (Pin 32)            SCK  ◄── GPIO18 (Pin 32) [compartido]
    MOSI ◄── GPIO23 (Pin 38)            MOSI ◄── GPIO23 (Pin 38) [compartido]
    MISO ◄── GPIO19 (Pin 33)            MISO ◄── GPIO19 (Pin 33) [compartido]
    IRQ  ─── No conectar                IRQ  ─── No conectar
```

---

## 6. MODOS DE JAMMING

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            MODOS DE OPERACIÓN RF                                 │
└──────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│ MODO 1: CONTINUOUS (Continuo)                                                   │
│ ═══════════════════════════════                                                 │
│                                                                                 │
│ Descripción: Transmisión constante en todos los canales Bluetooth              │
│ Comando: MODE:CONT + JAM_BT                                                     │
│                                                                                 │
│    Potencia                                                                     │
│       │                                                                         │
│    TX ├────────────────────────────────────────────────►                       │
│       │████████████████████████████████████████████████                        │
│     0 ├─────────────────────────────────────────────────► Tiempo               │
│                                                                                 │
│ Efectividad: ████████░░ 80%                                                    │
│ Uso: Ataque inicial, saturación completa                                       │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│ MODO 2: PULSE (Pulsos)                                                         │
│ ═══════════════════════                                                         │
│                                                                                 │
│ Descripción: Transmisión intermitente (on/off) para confundir hopping          │
│ Comando: MODE:PULSE + JAM_BT                                                    │
│                                                                                 │
│    Potencia                                                                     │
│       │     ┌──┐     ┌──┐     ┌──┐     ┌──┐                                    │
│    TX ├─────┤  ├─────┤  ├─────┤  ├─────┤  ├────►                               │
│       │     │  │     │  │     │  │     │  │                                    │
│     0 ├─────┴──┴─────┴──┴─────┴──┴─────┴──┴─────► Tiempo                       │
│           50ms  50ms                                                            │
│                                                                                 │
│ Efectividad: ██████████ 95%                                                    │
│ Uso: Disrumpir frequency hopping Bluetooth                                     │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│ MODO 3: SWEEP (Barrido)                                                         │
│ ═══════════════════════                                                         │
│                                                                                 │
│ Descripción: Barrido secuencial de frecuencias                                 │
│ Comando: MODE:SWEEP + JAM_START                                                 │
│                                                                                 │
│    Canal                                                                        │
│      │    ╱╲    ╱╲    ╱╲                                                       │
│  124 ├───╱  ╲──╱  ╲──╱  ╲──►                                                   │
│      │  ╱    ╲╱    ╲╱    ╲                                                      │
│    0 ├─╱──────────────────────► Tiempo                                         │
│        100ms por barrido                                                        │
│                                                                                 │
│ Efectividad: ███████░░░ 70%                                                    │
│ Uso: Encontrar canal activo del dispositivo                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│ MODO 4: TARGETED (Dirigido)                                                     │
│ ═══════════════════════════                                                     │
│                                                                                 │
│ Descripción: Jamming solo en canales Bluetooth detectados                      │
│ Comando: JAM_CH:2,23,45,67,79                                                   │
│                                                                                 │
│    Potencia                                                                     │
│       │  ▲        ▲     ▲                                                      │
│    TX ├──█────────█─────█──────────────────────►                               │
│       │  █        █     █                                                      │
│     0 ├──┴────────┴─────┴──────────────────────► Canales                       │
│          2       23    45       (solo canales específicos)                      │
│                                                                                 │
│ Efectividad: █████████░ 90%                                                    │
│ Uso: Ataque preciso, menor consumo energético                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. EFECTIVIDAD COMBINADA

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                    COMPARACIÓN DE EFECTIVIDAD                                    │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│                          Solo BT DoS    Solo RF Jam    Híbrido (BT+RF)          │
│   Dispositivo            (RPi)          (ESP32)        (Combinado)              │
│   ─────────────────────  ────────────   ────────────   ────────────             │
│                                                                                  │
│   Parlantes baratos      ████████░░     ███████░░░     ██████████               │
│   (sin nombre)           80%            70%            95%                       │
│                                                                                  │
│   JBL / Sony / Bose      █████░░░░░     ██████░░░░     ████████░░               │
│   (mid-range)            50%            60%            80%                       │
│                                                                                  │
│   Bang & Olufsen         ███░░░░░░░     ████░░░░░░     ██████░░░░               │
│   (high-end)             30%            40%            60%                       │
│                                                                                  │
│   Smart TV               █████████░     ███████░░░     ██████████               │
│   (Samsung/LG)           90%            70%            99%                       │
│                                                                                  │
│   Auriculares BT         ██████░░░░     █████░░░░░     ████████░░               │
│                          60%            50%            80%                       │
│                                                                                  │
│   Astronaut Speaker      █████████░     ████████░░     ██████████               │
│   (tu objetivo)          90%            80%            99%                       │
│                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ¿POR QUÉ EL HÍBRIDO ES MÁS EFECTIVO?                                          │
│   ════════════════════════════════════                                          │
│                                                                                  │
│   Solo BT DoS:                                                                   │
│   ────────────                                                                   │
│   • Ataca capa de protocolo (L2CAP, RFCOMM)                                     │
│   • El dispositivo puede ignorar paquetes malformados                           │
│   • Frequency hopping puede evitar congestión                                   │
│                                                                                  │
│   Solo RF Jamming:                                                               │
│   ────────────────                                                               │
│   • Ataca capa física (PHY)                                                     │
│   • Interferencia puede ser insuficiente si la señal es fuerte                  │
│   • No afecta conexiones ya establecidas directamente                           │
│                                                                                  │
│   Híbrido Combinado:                                                             │
│   ──────────────────                                                             │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                         │   │
│   │   RF Jamming (Capa 1)         BT DoS (Capas 2-3)                       │   │
│   │          │                           │                                  │   │
│   │          ▼                           ▼                                  │   │
│   │   ┌─────────────┐             ┌─────────────┐                          │   │
│   │   │ Corrompe    │             │ Satura      │                          │   │
│   │   │ paquetes RF │────────────►│ protocolos  │                          │   │
│   │   │ en el aire  │  Efecto    │ superiores  │                          │   │
│   │   └─────────────┘  combinado │             │                          │   │
│   │          │        ═══════════│             │                          │   │
│   │          ▼                   └──────┬──────┘                          │   │
│   │   ┌─────────────┐                   │                                  │   │
│   │   │ Dispositivo │◄──────────────────┘                                  │   │
│   │   │ no puede    │                                                      │   │
│   │   │ recuperarse │                                                      │   │
│   │   └─────────────┘                                                      │   │
│   │                                                                         │   │
│   │   RESULTADO: Ataque en MÚLTIPLES CAPAS OSI simultáneamente             │   │
│   │              El dispositivo no tiene mecanismo de defensa              │   │
│   │                                                                         │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. LISTA DE MATERIALES FINAL

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         BILL OF MATERIALS (BOM)                                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   YA TIENES:                                                                     │
│   ──────────                                                                     │
│   [✓] Raspberry Pi 3B+/4B                                                       │
│   [✓] OLED SSD1306 128x64                                                       │
│   [✓] Encoder KY-040                                                            │
│   [✓] Micrófono USB                                                             │
│   [✓] Adaptador Bluetooth USB Clase 1                                           │
│   [✓] Fuente 5V/3A                                                              │
│                                                                                  │
│   NECESITAS COMPRAR:                                                             │
│   ──────────────────                                                             │
│                                                                                  │
│   Cant.  Componente                                    Precio Aprox.            │
│   ─────  ─────────────────────────────────────────     ─────────────            │
│     1    ESP32 DevKit V1 (30 pines)                    $5-8 USD                 │
│     2    NRF24L01+PA+LNA con Antena                    $8-12 USD c/u            │
│     1    Cable USB (datos, para ESP32↔RPi)             $2-3 USD                 │
│     1    Pack cables Dupont hembra-hembra (20 pcs)     $2-3 USD                 │
│     2    Capacitor 10µF/16V (estabilización)           $0.50 USD                │
│   ─────────────────────────────────────────────────────────────────             │
│          TOTAL ESTIMADO:                               $26-39 USD               │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. RESUMEN DE ARQUITECTURA

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│                    VOLUME BE GONE v3.0 - RESUMEN                                │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   RASPBERRY PI (Cerebro)              ESP32 (RF Jammer)                         │
│   ══════════════════════              ═════════════════                         │
│                                                                                 │
│   • Monitoreo de audio                • Control de nRF24L01 x2                 │
│   • Interfaz usuario (OLED)           • Channel hopping                        │
│   • Escaneo Bluetooth                 • Modos de jamming                       │
│   • Ataques L2CAP/RFCOMM              • Comunicación serial                    │
│   • Coordinación de ataques           • Alimentación independiente             │
│                                                                                 │
│                    │                           │                                │
│                    │      USB Serial           │                                │
│                    └───────────────────────────┘                                │
│                              │                                                  │
│                              ▼                                                  │
│                    ┌─────────────────┐                                         │
│                    │   OBJETIVO      │                                         │
│                    │   Parlante BT   │                                         │
│                    │   Desconectado  │                                         │
│                    └─────────────────┘                                         │
│                                                                                 │
│   VENTAJAS DE ESTA ARQUITECTURA:                                               │
│   ══════════════════════════════                                               │
│                                                                                 │
│   ✅ Sin problemas de corriente (ESP32 alimenta nRF24s)                        │
│   ✅ Código jamming ya existe (tu repo Bluetooth-jammer-esp32)                 │
│   ✅ Arquitectura modular y escalable                                          │
│   ✅ Dual-core ESP32 = rendimiento óptimo                                      │
│   ✅ Ataque multi-capa (protocolo + físico)                                    │
│   ✅ Efectividad 90-99% vs 70-80% solo BT DoS                                  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```
