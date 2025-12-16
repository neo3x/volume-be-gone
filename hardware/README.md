# Documentacion de Hardware

**Volume Be Gone v2.1**
**Author:** Francisco Ortiz Rojas - Ingeniero Electronico
**Contact:** francisco.ortiz@marfinex.com

---

## Lista de materiales (BOM)

### Componentes principales

Componente: Raspberry Pi
Especificaciones: 3B+ o 4B, 2GB RAM min

Componente: OLED Display
Especificaciones: 128x64, I2C, SSD1306

Componente: Encoder Rotativo
Especificaciones: KY-040 o similar

Componente: Microfono USB
Especificaciones: Compatible con Linux

Componente: Adaptador BT
Especificaciones: Clase 1, USB (opcional)

Componente: Fuente 5V
Especificaciones: 3A minimo, USB-C para Pi4

Componente: Cables Dupont
Especificaciones: Hembra-Hembra, 10 unidades

## Esquema de conexiones

### Pinout Raspberry Pi

```
                Raspberry Pi 40-pin Header
   3V3  (1)  o  o  (2)  5V
   SDA  (3)  o  o  (4)  5V
   SCL  (5)  o  o  (6)  GND
        (7)  o  o  (8)
   GND  (9)  o  o  (10)
        (11) o  o  (12)
GPIO13  (33) o  o  (34) GND
GPIO19  (35) o  o  (36)
GPIO26  (37) o  o  (38)
   GND  (39) o  o  (40)
```

### Conexiones detalladas

**OLED Display I2C:**
- VCC → Pin 1 (3.3V)
- GND → Pin 6 (GND)
- SDA → Pin 3 (GPIO2/SDA)
- SCL → Pin 5 (GPIO3/SCL)

**Encoder KY-040:**
- CLK → Pin 35 (GPIO19)
- DT  → Pin 33 (GPIO13)
- SW  → Pin 37 (GPIO26)
- +   → Pin 1 (3.3V)
- GND → Pin 39 (GND)

## Carcasa 3D

Los archivos STL para imprimir la carcasa estan en `/hardware/3d-models/`

### Parametros de impresion recomendados:
- Layer height: 0.2mm
- Infill: 20%
- Supports: Si (para los puertos USB)
- Tiempo estimado: 3-4 horas

## Notas de ensamblaje

1. Verificar polaridad antes de conectar
2. Usar cables cortos para I2C (max 30cm)
3. Alejar microfono de fuentes de ruido
4. Considerar blindaje para el encoder si hay interferencias
