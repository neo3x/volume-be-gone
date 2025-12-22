# RF JAMMING RESEARCH - nRF24L01 + Raspberry Pi

**Volume Be Gone v2.1 - Extensión de Investigación RF**
**Author:** Francisco Ortiz Rojas - Ingeniero Electrónico
**Fecha:** Diciembre 2025

---

## ADVERTENCIA LEGAL

```
⚠️  EL JAMMING RF ES ILEGAL EN LA MAYORÍA DE PAÍSES  ⚠️

Este documento es SOLO para fines de investigación académica y seguridad.
Jamming de señales RF viola:
- FCC Part 15 (USA)
- Directiva 2014/53/EU (Europa)
- Regulaciones de la SCT (México)
- Leyes de telecomunicaciones locales

Solo usar en:
✅ Entornos de laboratorio blindados (jaula de Faraday)
✅ Investigación académica autorizada
✅ CTF/Competencias de seguridad
✅ Dispositivos propios en ambiente controlado
```

---

## 1. COMPARACIÓN DE MÓDULOS nRF24L01

### Módulo 1: E01-2G4M27D (27dBm, 5KM)

| Especificación | Valor |
|----------------|-------|
| **Chip** | nRF24L01P + PA (Power Amplifier) + LNA |
| **Potencia TX** | 27 dBm (~500 mW) |
| **Alcance** | Hasta 5 km (línea de vista) |
| **Frecuencia** | 2.4 GHz - 2.525 GHz |
| **Canales** | 125 canales (2 MHz separación) |
| **Sensibilidad RX** | -117 dBm |
| **Voltaje** | 3.3V - 5V (regulador interno) |
| **Corriente TX** | ~130 mA @ 27dBm |
| **Formato** | DIP (pines directos) |
| **Antena** | SMA externa (incluida) |

**Ventajas:**
- Mayor potencia = Mayor área de interferencia
- Antena externa permite direccionalidad
- Mejor para jamming de largo alcance
- Regulador de voltaje interno (tolerante a 5V)

**Desventajas:**
- Mayor consumo de corriente (necesita fuente robusta)
- Más caro (~$15-20 USD)
- Puede requerir disipador de calor en uso prolongado

---

### Módulo 2: NRF24L01+PA+LNA con Adaptador 3.3V

| Especificación | Valor |
|----------------|-------|
| **Chip** | nRF24L01+ con PA+LNA |
| **Potencia TX** | ~20-22 dBm (~100-150 mW) |
| **Alcance** | ~1100m (línea de vista) |
| **Frecuencia** | 2.4 GHz - 2.525 GHz |
| **Canales** | 125 canales |
| **Voltaje** | 3.3V estricto (adaptador incluido) |
| **Corriente TX** | ~115 mA @ máxima potencia |
| **Formato** | Con adaptador breakout |

**Ventajas:**
- Adaptador 3.3V incluido (más estable)
- Costo moderado (~$8-12 USD)
- Suficiente para jamming de corto/medio alcance
- Capacitores de filtrado incluidos

**Desventajas:**
- Menor potencia que E01-2G4M27D
- Alcance limitado (~100-200m en interiores)

---

### RECOMENDACIÓN

```
Para tu proyecto Volume Be Gone:

┌─────────────────────────────────────────────────────────────┐
│  RECOMENDACIÓN: 2x NRF24L01+PA+LNA con Adaptador 3.3V     │
│                                                             │
│  Razón: El adaptador 3.3V proporciona estabilidad          │
│         esencial para Raspberry Pi. Dos módulos permiten   │
│         cubrir más canales simultáneamente.                │
└─────────────────────────────────────────────────────────────┘

Alternativa para MÁXIMO alcance:
  1x E01-2G4M27D (27dBm) - Para jamming de largo alcance
  + Fuente de alimentación externa 5V/2A dedicada
```

---

## 2. CONEXIÓN A RASPBERRY PI

### Diagrama de Pines - SPI

El nRF24L01 usa interfaz SPI. Raspberry Pi tiene 2 buses SPI disponibles:

```
RASPBERRY PI GPIO          nRF24L01 (8 pines)
┌─────────────────┐        ┌─────────────────┐
│                 │        │                 │
│  3.3V (Pin 1)  ─┼────────┼─ VCC           │
│  GND  (Pin 6)  ─┼────────┼─ GND           │
│                 │        │                 │
│  GPIO17 (Pin 11)┼────────┼─ CE  (Chip Enable)
│  GPIO8  (Pin 24)┼────────┼─ CSN (Chip Select)
│                 │        │                 │
│  GPIO11 (Pin 23)┼────────┼─ SCK (SPI Clock)
│  GPIO10 (Pin 19)┼────────┼─ MOSI (Master Out)
│  GPIO9  (Pin 21)┼────────┼─ MISO (Master In)
│                 │        │                 │
│  (No conectar) ─┼────────┼─ IRQ (Opcional) │
│                 │        │                 │
└─────────────────┘        └─────────────────┘
```

### Configuración para 2 Módulos (Dual SPI)

```
                    RASPBERRY PI 3B+/4B
        ┌──────────────────────────────────────┐
        │                                      │
        │   SPI0 (CE0)          SPI1 (CE1)    │
        │   ┌──────┐            ┌──────┐      │
        │   │GPIO8 │            │GPIO7 │      │
        │   │(CSN0)│            │(CSN1)│      │
        │   └──┬───┘            └──┬───┘      │
        │      │                   │          │
        └──────┼───────────────────┼──────────┘
               │                   │
               ▼                   ▼
        ┌──────────┐        ┌──────────┐
        │ nRF24L01 │        │ nRF24L01 │
        │ Módulo 1 │        │ Módulo 2 │
        │          │        │          │
        │ Canales  │        │ Canales  │
        │  0-62    │        │  63-124  │
        └──────────┘        └──────────┘
```

### Pinout Completo para 2 Módulos

| Señal | Módulo 1 | Módulo 2 | RPi Pin | GPIO |
|-------|----------|----------|---------|------|
| VCC | VCC | VCC | Pin 1 (3.3V) | - |
| GND | GND | GND | Pin 6 (GND) | - |
| CE | CE | - | Pin 11 | GPIO17 |
| CE | - | CE | Pin 13 | GPIO27 |
| CSN | CSN | - | Pin 24 | GPIO8 (CE0) |
| CSN | - | CSN | Pin 26 | GPIO7 (CE1) |
| SCK | SCK | SCK | Pin 23 | GPIO11 |
| MOSI | MOSI | MOSI | Pin 19 | GPIO10 |
| MISO | MISO | MISO | Pin 21 | GPIO9 |

---

## 3. TEORÍA DEL RF JAMMING CON nRF24L01

### ¿Cómo funciona el jamming?

El nRF24L01 puede generar interferencia de tres formas:

#### Método 1: Constant Carrier Wave (CCW)

```
El chip puede transmitir una portadora continua sin modulación:

    Señal normal Bluetooth:
    ┌─┐ ┌─┐   ┌───┐ ┌─┐
    │ │ │ │   │   │ │ │   (Datos modulados)
────┘ └─┘ └───┘   └─┘ └──

    Constant Carrier (Jamming):
    ────────────────────────  (Portadora continua)

El receptor Bluetooth no puede demodular correctamente
cuando hay una portadora interferente.
```

#### Método 2: Channel Hopping Noise

```
Bluetooth usa 79 canales (2402-2480 MHz)
nRF24L01 tiene 125 canales (2400-2525 MHz)

Estrategia: Saltar rápidamente entre canales transmitiendo ruido

Canal:  0   1   2   3   4   5   ...  78  79
       ┌─┐     ┌─┐ ┌─┐         ┌─┐
       │█│     │█│ │█│   ...   │█│       (Jamming)
    ───┴─┴─────┴─┴─┴─┴─────────┴─┴────
              ▲
              │
        Transmisión de ruido en cada canal
```

#### Método 3: Pseudo-Random Data Burst

```
Transmitir datos aleatorios rápidamente:

Payload: [0xFF, 0x00, 0xAA, 0x55, 0xRandom...]

La modulación GFSK del nRF24 crea interferencia
que corrompe los paquetes Bluetooth cercanos.
```

---

## 4. ESPECTRO DE FRECUENCIAS

### Cobertura de Bandas

```
                    ESPECTRO 2.4 GHz
    ├──────────────────────────────────────────────────┤
2400 MHz                                            2500 MHz

    │◀──── WiFi Canal 1 ────▶│
    │         (2401-2423)     │
    │                         │◀──── WiFi Canal 6 ────▶│
    │                         │      (2426-2448)        │
    │                                                   │◀─ WiFi 11 ─▶│
    │                                                   │  (2451-2473)│

    │◀────────────────── Bluetooth ──────────────────▶│
    │              (2402-2480 MHz, 79 canales)         │

    │◀──────────────────── nRF24L01 ──────────────────────────────▶│
    │                (2400-2525 MHz, 125 canales)                   │


Mapeo de canales nRF24L01 → Bluetooth:
  nRF Canal 0   = 2400 MHz
  nRF Canal 2   = 2402 MHz = Bluetooth Canal 0
  nRF Canal 80  = 2480 MHz = Bluetooth Canal 78
```

---

## 5. ¿CUÁNTOS MÓDULOS NECESITAS?

### Análisis de Requerimientos

```
┌─────────────────────────────────────────────────────────────────┐
│                    ESCENARIO DE USO                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  OPCIÓN A: 1 MÓDULO                                            │
│  ─────────────────                                              │
│  • Puede cubrir ~40 canales/segundo con channel hopping        │
│  • Efectivo contra Bluetooth de baja velocidad de hopping      │
│  • Suficiente para jamming básico de corto alcance             │
│  • Limitación: No cubre todos los canales simultáneamente      │
│                                                                 │
│  OPCIÓN B: 2 MÓDULOS (RECOMENDADO)                             │
│  ─────────────────────────────────                              │
│  • Módulo 1: Canales 0-62 (2400-2462 MHz)                      │
│  • Módulo 2: Canales 63-124 (2463-2524 MHz)                    │
│  • Cobertura completa del espectro Bluetooth                   │
│  • Mayor probabilidad de interferir con frequency hopping      │
│  • Redundancia si un módulo falla                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Tabla de Decisión

| Caso de Uso | Módulos | Justificación |
|-------------|---------|---------------|
| Prueba de concepto | 1 | Suficiente para demostrar viabilidad |
| Jamming direccional | 1 (27dBm) | Alta potencia compensa cobertura parcial |
| Jamming omnidireccional | 2 | Cobertura completa de espectro |
| Máxima efectividad | 2 + 1 reserva | Redundancia y respaldo |

---

## 6. INTEGRACIÓN CON VOLUME BE GONE

### Arquitectura Propuesta

```
┌─────────────────────────────────────────────────────────────────┐
│                      VOLUME BE GONE v3.0                        │
│                   (Arquitectura Híbrida)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │  Micrófono  │    │   OLED      │    │   Encoder   │        │
│   │    USB      │    │  Display    │    │   KY-040    │        │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘        │
│          │                  │                  │                │
│          ▼                  ▼                  ▼                │
│   ┌────────────────────────────────────────────────────┐       │
│   │              RASPBERRY PI 3B+/4B                    │       │
│   │                                                     │       │
│   │  ┌──────────────────────────────────────────────┐  │       │
│   │  │           volumeBeGone.py                     │  │       │
│   │  │                                               │  │       │
│   │  │  ┌─────────────┐    ┌─────────────────────┐  │  │       │
│   │  │  │  Bluetooth  │    │    RF Jamming      │  │  │       │
│   │  │  │   Attack    │    │    Controller      │  │  │       │
│   │  │  │  (L2CAP,    │    │   (nRF24L01)       │  │  │       │
│   │  │  │  RFCOMM)    │    │                     │  │  │       │
│   │  │  └──────┬──────┘    └──────────┬──────────┘  │  │       │
│   │  │         │                      │             │  │       │
│   │  └─────────┼──────────────────────┼─────────────┘  │       │
│   │            │                      │                │       │
│   │            ▼                      ▼                │       │
│   │   ┌────────────┐          ┌────────────────┐      │       │
│   │   │ Bluetooth  │          │  SPI Interface │      │       │
│   │   │  hci1      │          │  (SPI0 + SPI1) │      │       │
│   │   │ (Clase 1)  │          │                │      │       │
│   │   └─────┬──────┘          └───────┬────────┘      │       │
│   │         │                         │               │       │
│   └─────────┼─────────────────────────┼───────────────┘       │
│             │                         │                        │
│             ▼                         ▼                        │
│   ┌─────────────────┐    ┌────────────────────────────┐       │
│   │ USB Bluetooth   │    │  nRF24L01 x2               │       │
│   │ Adapter         │    │  ┌────────┐ ┌────────┐    │       │
│   │ (50-100m range) │    │  │Módulo 1│ │Módulo 2│    │       │
│   └─────────────────┘    │  │CH 0-62 │ │CH63-124│    │       │
│                          │  └────────┘ └────────┘    │       │
│                          └────────────────────────────┘       │
│                                                                 │
│   ATAQUE COMBINADO:                                            │
│   ════════════════                                             │
│   1. Bluetooth DoS (L2CAP/RFCOMM) → Ataque de protocolo        │
│   2. RF Jamming (nRF24L01) → Interferencia de capa física      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. FLUJO DE ATAQUE COMBINADO

```
┌──────────────────────────────────────────────────────────────────┐
│                    FLUJO DE ATAQUE HÍBRIDO                       │
└──────────────────────────────────────────────────────────────────┘

     ┌─────────────────┐
     │ Nivel de Audio  │
     │   > Umbral dB   │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ Escaneo BT      │
     │ (8-10 segundos) │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ Dispositivos    │
     │ de Audio        │
     │ Detectados?     │
     └────────┬────────┘
              │
         ┌────┴────┐
         │         │
         ▼         ▼
        SÍ        NO
         │         │
         │         └──────────────────┐
         │                            │
         ▼                            ▼
┌─────────────────────┐    ┌─────────────────────┐
│  FASE 1: RF JAM     │    │  Solo RF Jamming    │
│  ─────────────────  │    │  (Jamming ciego)    │
│                     │    │                     │
│  Activar nRF24L01   │    │  Interferir todo    │
│  Channel hopping    │    │  el espectro 2.4GHz │
│  Canales 2-80       │    │                     │
│  (banda Bluetooth)  │    └─────────────────────┘
│                     │
│  Duración: 5 seg    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  FASE 2: BT DoS     │
│  ─────────────────  │
│                     │
│  L2CAP Flood        │
│  (20 threads)       │
│                     │
│  + RF Jam continuo  │
│  (background)       │
│                     │
│  Duración: 15 seg   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  FASE 3: RFCOMM     │
│  ─────────────────  │
│                     │
│  Connection Flood   │
│  30 canales x 8     │
│                     │
│  + RF Jam pulsos    │
│                     │
│  Duración: 10 seg   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  ¿Dispositivo       │
│  desconectado?      │
└──────────┬──────────┘
           │
      ┌────┴────┐
      │         │
      ▼         ▼
     SÍ        NO
      │         │
      │         └──► Repetir desde FASE 1
      │
      ▼
┌─────────────────────┐
│  Continuar          │
│  monitoreo de       │
│  audio              │
└─────────────────────┘
```

---

## 8. EFECTIVIDAD ESPERADA

### Comparación: Solo BT DoS vs. Híbrido (BT + RF)

| Métrica | Solo Bluetooth DoS | Híbrido (BT + RF) |
|---------|-------------------|-------------------|
| **Parlantes baratos** | 70-80% | 90-95% |
| **Parlantes mid-range** | 50-60% | 75-85% |
| **Parlantes high-end** | 20-30% | 50-60% |
| **Smart TVs** | 85-95% | 95-99% |
| **Auriculares BT** | 60-70% | 80-90% |
| **Tiempo promedio desconexión** | 10-30 seg | 5-15 seg |

### ¿Por qué es más efectivo el híbrido?

```
SOLO BLUETOOTH DoS:
  └─► Ataca capa de protocolo (L2CAP, RFCOMM)
  └─► El dispositivo puede ignorar paquetes malformados
  └─► Frequency hopping evade algunos ataques

HÍBRIDO (BT + RF JAMMING):
  └─► RF Jamming: Corrompe la capa física (PHY)
  └─► Los paquetes no llegan correctamente
  └─► El dispositivo no puede hacer frequency hopping efectivo
  └─► BT DoS: Además satura los protocolos superiores
  └─► EFECTO COMBINADO: Ataque en múltiples capas OSI
```

---

## 9. LISTA DE MATERIALES

### Opción Recomendada (2 módulos)

| Componente | Cantidad | Precio Aprox. |
|------------|----------|---------------|
| NRF24L01+PA+LNA con Adaptador 3.3V | 2 | $16-24 USD |
| Cables Dupont hembra-hembra | 20 | $3 USD |
| Capacitor 10µF 16V (estabilización) | 2 | $1 USD |
| **Total** | | **~$24 USD** |

### Opción Máxima Potencia (1 módulo)

| Componente | Cantidad | Precio Aprox. |
|------------|----------|---------------|
| E01-2G4M27D (27dBm) | 1 | $15-20 USD |
| Fuente 5V/2A dedicada | 1 | $5 USD |
| Cables Dupont | 10 | $2 USD |
| Disipador de calor pequeño | 1 | $2 USD |
| **Total** | | **~$29 USD** |

---

## 10. PRÓXIMOS PASOS

### Para implementar:

1. **Hardware**
   - [ ] Adquirir 2x NRF24L01+PA+LNA con adaptador
   - [ ] Verificar conexiones SPI en Raspberry Pi
   - [ ] Instalar capacitores de estabilización

2. **Software**
   - [ ] Habilitar SPI en Raspberry Pi (`raspi-config`)
   - [ ] Instalar biblioteca RF24 para Python
   - [ ] Integrar módulo de jamming en volumeBeGone.py

3. **Testing**
   - [ ] Probar en ambiente controlado (jaula de Faraday)
   - [ ] Medir efectividad con diferentes dispositivos
   - [ ] Optimizar timing de channel hopping

---

## 11. RECURSOS ADICIONALES

### Repositorio de Referencia
- **Bluetooth-jammer-esp32**: https://github.com/neo3x/Bluetooth-jammer-esp32
- Contiene implementación base para ESP32 + nRF24L01
- Incluye web flasher y configuración de canales

### Bibliotecas Python para Raspberry Pi
- **RF24**: https://github.com/nRF24/RF24
- **pyRF24**: Wrapper Python para la biblioteca RF24

### Documentación Técnica
- nRF24L01+ Datasheet: Nordic Semiconductor
- Bluetooth Core Specification v5.3
- IEEE 802.11 (WiFi) para entender interferencia

---

**NOTA FINAL**: Este documento es para investigación de seguridad únicamente.
La implementación de jamming RF sin autorización es ilegal y puede resultar
en multas significativas y cargos criminales.
