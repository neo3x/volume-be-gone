# Análisis de Compatibilidad GPIO - nRF24L01 + Sistema Existente

## PINES ACTUALMENTE EN USO

### 1. Pantalla OLED (I2C)
```
Componente          Pin RPi      GPIO        Bus
─────────────────────────────────────────────────
VCC                 Pin 1        3.3V        Power
GND                 Pin 6        GND         Power
SDA                 Pin 3        GPIO2       I2C (SDA1)
SCL                 Pin 5        GPIO3       I2C (SCL1)
```

### 2. Encoder KY-040
```
Componente          Pin RPi      GPIO        Tipo
─────────────────────────────────────────────────
CLK                 Pin 35       GPIO19      Digital
DT                  Pin 33       GPIO13      Digital
SW                  Pin 37       GPIO26      Digital
VCC                 Pin 1        3.3V        Power
GND                 Pin 39       GND         Power
```

---

## PINES REQUERIDOS PARA nRF24L01 (SPI)

### Módulo 1 (Canales 0-62)
```
nRF24L01 Pin        Pin RPi      GPIO        Bus
─────────────────────────────────────────────────
VCC                 Pin 17       3.3V        Power
GND                 Pin 20       GND         Power
CE                  Pin 11       GPIO17      Digital
CSN                 Pin 24       GPIO8       SPI0 CE0
SCK                 Pin 23       GPIO11      SPI0 SCLK
MOSI                Pin 19       GPIO10      SPI0 MOSI
MISO                Pin 21       GPIO9       SPI0 MISO
```

### Módulo 2 (Canales 63-124)
```
nRF24L01 Pin        Pin RPi      GPIO        Bus
─────────────────────────────────────────────────
VCC                 Pin 1        3.3V        Power (compartido)
GND                 Pin 14       GND         Power
CE                  Pin 13       GPIO27      Digital
CSN                 Pin 26       GPIO7       SPI0 CE1
SCK                 Pin 23       GPIO11      SPI0 SCLK (compartido)
MOSI                Pin 19       GPIO10      SPI0 MOSI (compartido)
MISO                Pin 21       GPIO9       SPI0 MISO (compartido)
```

---

## ANÁLISIS DE CONFLICTOS

```
┌─────────────────────────────────────────────────────────────────┐
│                    MAPA DE GPIO EN USO                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   GPIO    Pin     Uso Actual       nRF24L01      ¿Conflicto?   │
│   ─────   ────    ────────────     ──────────    ───────────   │
│   GPIO2   Pin 3   OLED SDA         -             NO            │
│   GPIO3   Pin 5   OLED SCL         -             NO            │
│   GPIO7   Pin 26  -                CSN Mod.2     NO ✓          │
│   GPIO8   Pin 24  -                CSN Mod.1     NO ✓          │
│   GPIO9   Pin 21  -                MISO          NO ✓          │
│   GPIO10  Pin 19  -                MOSI          NO ✓          │
│   GPIO11  Pin 23  -                SCK           NO ✓          │
│   GPIO13  Pin 33  Encoder DT       -             NO            │
│   GPIO17  Pin 11  -                CE Mod.1      NO ✓          │
│   GPIO19  Pin 35  Encoder CLK      -             NO            │
│   GPIO26  Pin 37  Encoder SW       -             NO            │
│   GPIO27  Pin 13  -                CE Mod.2      NO ✓          │
│                                                                 │
│   ═══════════════════════════════════════════════════════════  │
│   RESULTADO: ✅ NO HAY CONFLICTOS DE GPIO                       │
│   ═══════════════════════════════════════════════════════════  │
│                                                                 │
│   RAZÓN: La pantalla OLED usa I2C (GPIO2, GPIO3)               │
│          Los nRF24L01 usan SPI (GPIO7-11, 17, 27)              │
│          Son buses COMPLETAMENTE DIFERENTES                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## DIAGRAMA VISUAL DE PINES

```
                    RASPBERRY PI 3B+/4B - Header 40 pines
                    =====================================

         3V3 [ 1]  ●────────────────────────────●  [ 2] 5V
    OLED SDA [ 3]  ●  ◄─── I2C (OLED) ───────►  ●  [ 4] 5V
    OLED SCL [ 5]  ●                            ●  [ 6] GND ◄── OLED
             [ 7]  ○                            ●  [ 8]
         GND [ 9]  ○                            ●  [10]
  nRF CE #1 [11]  ●  ◄─── SPI (nRF24) ───────► ●  [12]
  nRF CE #2 [13]  ●                            ●  [14] GND ◄── nRF
             [15]  ○                            ●  [16]
         3V3 [17]  ●  ◄── nRF VCC              ●  [18]
   nRF MOSI [19]  ●  ◄─── SPI (nRF24) ───────► ●  [20] GND ◄── nRF
   nRF MISO [21]  ●                            ●  [22]
    nRF SCK [23]  ●                            ●  [24] nRF CSN #1
         GND [25]  ○                            ●  [26] nRF CSN #2
             [27]  ○                            ●  [28]
             [29]  ○                            ●  [30]
             [31]  ○                            ●  [32]
 Encoder DT [33]  ●  ◄─── Encoder ────────────► ●  [34] GND
Encoder CLK [35]  ●                            ●  [36]
 Encoder SW [37]  ●                            ●  [38]
         GND [39]  ●  ◄── Encoder GND          ●  [40]


LEYENDA:
  ● = Pin en uso
  ○ = Pin disponible
```

---

## ANÁLISIS DE CORRIENTE (CRÍTICO)

### Consumo del Rail de 3.3V

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONSUMO DE CORRIENTE 3.3V                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Componente              Consumo Típico    Consumo Máximo     │
│   ──────────────────────  ──────────────    ──────────────     │
│   OLED SSD1306            ~20 mA            30 mA              │
│   Encoder KY-040          ~5 mA             10 mA              │
│   nRF24L01+PA+LNA #1      ~15 mA (RX)       130 mA (TX max)    │
│   nRF24L01+PA+LNA #2      ~15 mA (RX)       130 mA (TX max)    │
│   ──────────────────────  ──────────────    ──────────────     │
│   TOTAL                   ~55 mA            300 mA             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

LÍMITE DEL RAIL 3.3V DE RASPBERRY PI:
┌─────────────────────────────────────────────────────────────────┐
│  RPi 3B+:  ~500 mA máximo (regulador interno)                  │
│  RPi 4B:   ~500 mA máximo (regulador interno)                  │
│                                                                 │
│  300 mA < 500 mA  ──►  ⚠️ FUNCIONA, PERO EN EL LÍMITE          │
└─────────────────────────────────────────────────────────────────┘
```

### ⚠️ PROBLEMA POTENCIAL

```
El nRF24L01+PA+LNA tiene PICOS de corriente al transmitir:

    Corriente
    (mA)
     │
 150─┤        ┌───┐     ┌───┐
     │        │   │     │   │    ← Picos de 130-150mA
 100─┤        │   │     │   │
     │   ┌────┤   │     │   │
  50─┤   │    │   │     │   │
     │   │    │   │     │   │
  15─┤───┘    └───┴─────┴───┴───  ← Modo RX/Idle
     │
   0─┼────────────────────────────► Tiempo
         TX    TX      TX

Estos picos pueden causar:
  - Inestabilidad del regulador 3.3V
  - Reinicios del nRF24L01
  - Corrupción de paquetes
  - En casos extremos, reinicio de la RPi
```

---

## SOLUCIONES RECOMENDADAS

### Opción A: Capacitores de Desacoplo (MÍNIMO)

```
Agregar capacitores en cada módulo nRF24L01:

                    ┌─────────────────┐
    VCC (3.3V) ─────┤                 │
                    │  Capacitor      │
                    │  100µF/16V      │──────► nRF24L01 VCC
                    │  (electrolítico)│
    GND ────────────┤                 │──────► nRF24L01 GND
                    └─────────────────┘

    TAMBIÉN agregar 100nF cerámico en paralelo para filtrado HF.

    Esto absorbe los picos de corriente y estabiliza el voltaje.
```

**Costo:** ~$1-2 USD

---

### Opción B: Alimentación Externa 3.3V (RECOMENDADO)

```
Usar un regulador 3.3V externo alimentado desde 5V de la RPi:

         RPi 5V (Pin 2 o 4)
              │
              ▼
    ┌─────────────────────┐
    │   AMS1117-3.3V      │
    │   (o similar)       │
    │                     │
    │  IN    GND    OUT   │
    └──┬──────┬──────┬────┘
       │      │      │
       │      │      └────────────► nRF24L01 VCC (ambos módulos)
       │      │
       │      └───────────────────► GND común
       │
    RPi 5V ───┘

    El regulador AMS1117-3.3V puede entregar hasta 800mA.
    Más que suficiente para los picos.
```

**Costo:** ~$2-3 USD

---

### Opción C: Adaptador nRF24L01 con Regulador (MÁS FÁCIL)

```
El módulo "NRF24L01+PA+LNA con Adaptador Breakout 3.3V" que mencionaste
YA INCLUYE un regulador y capacitores:

    ┌─────────────────────────────────────────┐
    │                                         │
    │   ┌─────────────────────────────────┐   │
    │   │     ADAPTADOR BREAKOUT          │   │
    │   │   ┌───────────┐                 │   │
    │   │   │ Regulador │  ┌──────────┐   │   │
    │   │   │  3.3V     │  │ 100µF    │   │   │
    │   │   └───────────┘  │ Capacitor│   │   │
    │   │                  └──────────┘   │   │
    │   │     ● ● ● ● ● ● ● ●             │   │
    │   │    VCC                          │   │
    │   │    (5V tolerante)               │   │
    │   └─────────────────────────────────┘   │
    │                 ↑                       │
    │        NRF24L01+PA+LNA                  │
    │                                         │
    └─────────────────────────────────────────┘

    VENTAJA: Puedes alimentar con 5V directamente desde la RPi.
    El adaptador regula a 3.3V internamente.
```

**ESTA ES LA OPCIÓN QUE RECOMIENDO** - Ya la tienes considerada.

---

## RESUMEN FINAL

```
┌─────────────────────────────────────────────────────────────────┐
│                       COMPATIBILIDAD                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ✅ GPIO:     NO HAY CONFLICTOS                                │
│               I2C (OLED) y SPI (nRF24) son independientes       │
│                                                                 │
│   ✅ PINES:   SUFICIENTES                                       │
│               Todos los pines necesarios están disponibles      │
│                                                                 │
│   ⚠️ CORRIENTE: LÍMITE, PERO MANEJABLE                          │
│               Con el adaptador 3.3V incluido = OK               │
│               Sin adaptador = Agregar capacitores grandes       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   RECOMENDACIÓN FINAL:                                          │
│   ═══════════════════                                           │
│                                                                 │
│   Comprar: 2x "NRF24L01+PA+LNA con Adaptador Breakout 3.3V"    │
│                                                                 │
│   Razones:                                                      │
│   1. Regulador 3.3V integrado (maneja picos de corriente)       │
│   2. Capacitores de filtrado incluidos                          │
│   3. Puedes alimentar desde 5V de la RPi (más estable)          │
│   4. Plug & play, sin componentes adicionales                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## CONEXIÓN FINAL PROPUESTA

```
                         RASPBERRY PI
    ┌───────────────────────────────────────────────────────────┐
    │                                                           │
    │   SISTEMA EXISTENTE              NUEVOS MÓDULOS nRF24L01  │
    │   ─────────────────              ──────────────────────── │
    │                                                           │
    │   ┌──────────┐                   ┌──────────────────────┐ │
    │   │  OLED    │◄── I2C            │  nRF24L01 #1        │ │
    │   │ SSD1306  │    (Pin 3,5)      │  + Adaptador 3.3V   │ │
    │   └──────────┘                   │                      │ │
    │                                  │  VCC ◄── 5V (Pin 2)  │ │
    │   ┌──────────┐                   │  CE  ◄── GPIO17      │ │
    │   │ Encoder  │◄── GPIO           │  CSN ◄── GPIO8       │ │
    │   │  KY-040  │   (13,19,26)      │  SCK/MOSI/MISO ◄─┐  │ │
    │   └──────────┘                   └──────────────────┼──┘ │
    │                                                     │    │
    │   ┌──────────┐                   ┌──────────────────┼──┐ │
    │   │ Mic USB  │◄── USB            │  nRF24L01 #2     │  │ │
    │   └──────────┘                   │  + Adaptador 3.3V│  │ │
    │                                  │                  │  │ │
    │   ┌──────────┐                   │  VCC ◄── 5V (Pin4)  │ │
    │   │ BT USB   │◄── USB            │  CE  ◄── GPIO27  │  │ │
    │   │ Clase 1  │                   │  CSN ◄── GPIO7   │  │ │
    │   └──────────┘                   │  SCK/MOSI/MISO ◄─┘  │ │
    │                                  └──────────────────────┘ │
    │                                                           │
    └───────────────────────────────────────────────────────────┘
```
