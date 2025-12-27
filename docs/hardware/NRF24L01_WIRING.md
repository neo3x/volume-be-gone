# NRF24L01 Wiring Guide - Raspberry Pi

## Esquema de Conexión Detallado

### Configuración de 2 Módulos nRF24L01

```
                        RASPBERRY PI 3B+/4B
    ┌─────────────────────────────────────────────────────────────┐
    │                                                             │
    │   (1)  (2)  (3)  (4)  (5)  (6)  (7)  (8)  (9)  (10)        │
    │    ●────●────●────●────●────●────●────●────●────●          │
    │   3V3  5V  SDA  5V  SCL GND GP4 TXD RXD GP17               │
    │    │                   │               │                    │
    │    │                   │               └─────────┐          │
    │    │                   │                         │          │
    │   (11) (12) (13) (14) (15) (16) (17) (18) (19) (20)        │
    │    ●────●────●────●────●────●────●────●────●────●          │
    │  GP17 GP18 GP27 GND GP22 GP23 3V3 GP24 MOSI GND            │
    │    │        │                          │                    │
    │    │        └──────────────────────────┼────────┐          │
    │    │                                   │        │          │
    │   (21) (22) (23) (24) (25) (26) (27) (28) (29) (30)        │
    │    ●────●────●────●────●────●────●────●────●────●          │
    │  MISO GP25 SCK CE0  GND CE1 ID_SD ID_SC GP5 GND            │
    │    │        │   │        │                                  │
    │    │        │   │        └──────────────────────┐          │
    │    │        │   │                               │          │
    │   (31) (32) (33) (34) (35) (36) (37) (38) (39) (40)        │
    │    ●────●────●────●────●────●────●────●────●────●          │
    │  GP6 GP12 GP13 GND GP19 GP16 GP26 GP20 GND GP21            │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘

CONEXIONES:

┌──────────────────────────────────────────────────────────────────┐
│                     MÓDULO 1 (nRF24L01)                          │
│                     Canales 0-62                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│    nRF24L01 Pin          RPi Pin              GPIO               │
│    ─────────────         ───────              ────               │
│    VCC (3.3V)    ◄────── Pin 1   ──────────► 3.3V               │
│    GND           ◄────── Pin 6   ──────────► GND                │
│    CE            ◄────── Pin 11  ──────────► GPIO17             │
│    CSN           ◄────── Pin 24  ──────────► GPIO8 (CE0)        │
│    SCK           ◄────── Pin 23  ──────────► GPIO11 (SCLK)      │
│    MOSI          ◄────── Pin 19  ──────────► GPIO10 (MOSI)      │
│    MISO          ◄────── Pin 21  ──────────► GPIO9 (MISO)       │
│    IRQ           ◄────── (No conectar)                          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                     MÓDULO 2 (nRF24L01)                          │
│                     Canales 63-124                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│    nRF24L01 Pin          RPi Pin              GPIO               │
│    ─────────────         ───────              ────               │
│    VCC (3.3V)    ◄────── Pin 17  ──────────► 3.3V               │
│    GND           ◄────── Pin 20  ──────────► GND                │
│    CE            ◄────── Pin 13  ──────────► GPIO27             │
│    CSN           ◄────── Pin 26  ──────────► GPIO7 (CE1)        │
│    SCK           ◄────── Pin 23  ──────────► GPIO11 (SCLK) *    │
│    MOSI          ◄────── Pin 19  ──────────► GPIO10 (MOSI) *    │
│    MISO          ◄────── Pin 21  ──────────► GPIO9 (MISO) *     │
│    IRQ           ◄────── (No conectar)                          │
│                                                                  │
│    * Compartidos con Módulo 1 (mismo bus SPI)                   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Diagrama Visual de Conexión

```
                    nRF24L01 Módulo 1                nRF24L01 Módulo 2
                   ┌─────────────────┐              ┌─────────────────┐
                   │  ┌───────────┐  │              │  ┌───────────┐  │
                   │  │  ANTENA   │  │              │  │  ANTENA   │  │
                   │  └─────┬─────┘  │              │  └─────┬─────┘  │
                   │        │        │              │        │        │
                   │ ┌────────────┐  │              │ ┌────────────┐  │
                   │ │ PA + LNA   │  │              │ │ PA + LNA   │  │
                   │ └────────────┘  │              │ └────────────┘  │
                   │                 │              │                 │
                   │ ┌─┐ ┌─┐ ┌─┐ ┌─┐│              │ ┌─┐ ┌─┐ ┌─┐ ┌─┐│
                   │ │1│ │2│ │3│ │4││              │ │1│ │2│ │3│ │4││
                   │ └┬┘ └┬┘ └┬┘ └┬┘│              │ └┬┘ └┬┘ └┬┘ └┬┘│
                   │ ┌─┐ ┌─┐ ┌─┐ ┌─┐│              │ ┌─┐ ┌─┐ ┌─┐ ┌─┐│
                   │ │5│ │6│ │7│ │8││              │ │5│ │6│ │7│ │8││
                   │ └┬┘ └┬┘ └┬┘ └┬┘│              │ └┬┘ └┬┘ └┬┘ └┬┘│
                   └──┼───┼───┼───┼─┘              └──┼───┼───┼───┼─┘
                      │   │   │   │                   │   │   │   │
    Pin 1: GND ───────┘   │   │   │                   │   │   │   │
    Pin 2: VCC ───────────┘   │   │                   │   │   │   │
    Pin 3: CE  ───────────────┘   │                   │   │   │   │
    Pin 4: CSN ───────────────────┘                   │   │   │   │
    Pin 5: SCK ───────────────────────────────────────┼───┼───┘   │
    Pin 6: MOSI ──────────────────────────────────────┼───┘       │
    Pin 7: MISO ──────────────────────────────────────┘           │
    Pin 8: IRQ  ──────────────────────────────────────────────────┘ (NC)


                            RASPBERRY PI
    ┌───────────────────────────────────────────────────────────────┐
    │                                                               │
    │    3.3V ────────┬────────────────────────────┐               │
    │    (Pin 1,17)   │                            │               │
    │                 │                            │               │
    │    GND ─────────┼──────────┬─────────────────┼───────┐       │
    │    (Pin 6,20)   │          │                 │       │       │
    │                 ▼          ▼                 ▼       ▼       │
    │              ┌─────┐    ┌─────┐           ┌─────┐ ┌─────┐   │
    │              │VCC 1│    │GND 1│           │VCC 2│ │GND 2│   │
    │              └─────┘    └─────┘           └─────┘ └─────┘   │
    │                                                               │
    │    GPIO17 ─────────────► CE  (Módulo 1)                      │
    │    (Pin 11)                                                   │
    │                                                               │
    │    GPIO8 ──────────────► CSN (Módulo 1) [SPI CE0]            │
    │    (Pin 24)                                                   │
    │                                                               │
    │    GPIO27 ─────────────► CE  (Módulo 2)                      │
    │    (Pin 13)                                                   │
    │                                                               │
    │    GPIO7 ──────────────► CSN (Módulo 2) [SPI CE1]            │
    │    (Pin 26)                                                   │
    │                                                               │
    │    GPIO11 ─────────────► SCK (Ambos módulos) [SCLK]          │
    │    (Pin 23)                                                   │
    │                                                               │
    │    GPIO10 ─────────────► MOSI (Ambos módulos)                │
    │    (Pin 19)                                                   │
    │                                                               │
    │    GPIO9 ──────────────► MISO (Ambos módulos)                │
    │    (Pin 21)                                                   │
    │                                                               │
    └───────────────────────────────────────────────────────────────┘
```

## Circuito de Estabilización (Recomendado)

```
El nRF24L01 es sensible a fluctuaciones de voltaje.
Agregar capacitores de filtrado:

                      ┌─────────────────┐
    VCC (3.3V) ───────┤+               +├──────────► nRF24L01 VCC
                      │   10µF/16V      │
    GND ──────────────┤-               -├──────────► nRF24L01 GND
                      └─────────────────┘

    Alternativa con dos capacitores:

                  ┌──────┐      ┌──────┐
    VCC ──────────┤100µF ├──┬───┤ 100nF├─────────► nRF24L01 VCC
                  └──────┘  │   └──────┘
                            │
    GND ────────────────────┴─────────────────────► nRF24L01 GND

    El 100µF maneja picos de corriente
    El 100nF filtra ruido de alta frecuencia
```

## Habilitación de SPI en Raspberry Pi

```bash
# 1. Abrir raspi-config
sudo raspi-config

# 2. Navegar a:
#    Interface Options → SPI → Enable

# 3. Reiniciar
sudo reboot

# 4. Verificar que SPI está habilitado
ls -la /dev/spi*
# Debe mostrar: /dev/spidev0.0, /dev/spidev0.1

# 5. Verificar permisos
groups
# El usuario debe estar en el grupo 'spi'

# Si no está, agregar:
sudo usermod -aG spi $USER
```

## Instalación de Dependencias

```bash
# Biblioteca RF24 para Python
pip3 install RF24

# O compilar desde fuente (recomendado para mejor rendimiento)
git clone https://github.com/nRF24/RF24.git
cd RF24
./configure --driver=SPIDEV
make
sudo make install

# Wrapper Python
cd pyRF24
pip3 install .
```

## Test de Conexión

```python
#!/usr/bin/env python3
"""Test básico de conexión nRF24L01"""

from RF24 import RF24, RF24_PA_MAX

# Módulo 1: CE=GPIO17, CSN=GPIO8 (CE0)
radio1 = RF24(17, 0)  # (CE_PIN, CSN SPI device)

# Módulo 2: CE=GPIO27, CSN=GPIO7 (CE1)
radio2 = RF24(27, 10) # (CE_PIN, CSN SPI device)

def test_module(radio, name):
    if radio.begin():
        print(f"[OK] {name} conectado correctamente")
        radio.printPrettyDetails()
        return True
    else:
        print(f"[ERROR] {name} no responde - verificar conexiones")
        return False

if __name__ == "__main__":
    print("=== Test de módulos nRF24L01 ===\n")

    result1 = test_module(radio1, "Módulo 1")
    print()
    result2 = test_module(radio2, "Módulo 2")

    print("\n=== Resumen ===")
    if result1 and result2:
        print("Ambos módulos funcionando correctamente")
    else:
        print("Revisar conexiones de los módulos que fallaron")
```

## Notas Importantes

1. **Alimentación**: El nRF24L01+PA+LNA puede consumir hasta 130mA en transmisión.
   Usar el pin de 3.3V de la Raspberry Pi directamente puede causar inestabilidad.
   Se recomienda un regulador 3.3V externo para transmisión prolongada.

2. **Distancia de cables**: Mantener los cables lo más cortos posible (<10cm).
   Cables largos introducen ruido y pueden causar errores de comunicación.

3. **Interferencia**: Alejar los módulos de la antena WiFi de la Raspberry Pi.
   La señal WiFi en 2.4GHz puede interferir con las pruebas.

4. **Orientación de antena**: Las antenas deben estar verticales y paralelas
   entre módulos para máxima eficiencia.
