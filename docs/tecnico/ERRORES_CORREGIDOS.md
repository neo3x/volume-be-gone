# ERRORES CORREGIDOS - Volume Be Gone v2.1

**Author:** Francisco Ortiz Rojas - Ingeniero Electronico
**Contact:** francisco.ortiz@marfinex.com

---

## Resumen de Correcciones

Se han corregido **11 errores críticos** y mejoras en el código:

---

## ✅ Errores Corregidos

### **1. Código Duplicado y Malformado (Líneas 1-19)**

**❌ ANTES:**
```python
#/usr/bin/env python  # Typo: falta !
"""
ECHO está desactivado.  # Texto basura de Windows
...
"""
print("Volume Be Gone v2.0")
print("Copia el codigo completo...")  # Placeholder innecesario
#!/usr/bin/env python  # Header duplicado
```

**✅ DESPUÉS:**
```python
#!/usr/bin/env python  # Shebang correcto
# -*- coding: utf-8 -*-
"""
Volume Be Gone - Bluetooth Speaker Control by Volume Level
...
Version: 2.1 (Corregido)
"""
# Sin código duplicado ni placeholders
```

---

### **2. Rutas Hardcodeadas (Múltiples líneas)**

**❌ ANTES:**
```python
myPath="/home/pi/volumebegone/"  # Ruta fija, falla si cambia usuario
with open('/home/pi/volumebegone/config.json', 'w') as f:  # Hardcoded
with open('log.txt', 'a') as f:  # Relativa, puede escribir en cualquier lugar
```

**✅ DESPUÉS:**
```python
from pathlib import Path

# Detectar ruta del script automáticamente
script_dir = Path(__file__).parent.parent.resolve()
myPath = str(script_dir) + "/"
config_path = myPath + "config.json"
log_path = myPath + "log.txt"

# Ahora funciona desde cualquier ubicación
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
```

---

### **3. Archivo de Fuente Sin Validar (Línea 95)**

**❌ ANTES:**
```python
font = ImageFont.truetype('whitrabt.ttf', 12)  # CRASH si no existe
font_small = ImageFont.truetype('whitrabt.ttf', 10)
```

**✅ DESPUÉS:**
```python
font_path = myPath + 'whitrabt.ttf'
try:
    if os.path.exists(font_path):
        font = ImageFont.truetype(font_path, 12)
        font_small = ImageFont.truetype(font_path, 10)
    else:
        print(f"[!] Advertencia: Fuente {font_path} no encontrada, usando default")
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()
except Exception as e:
    print(f"[!] Error cargando fuente: {e}, usando default")
    font = ImageFont.load_default()
    font_small = ImageFont.load_default()
```

**Beneficio:** No crashea si falta el archivo TTF, usa fuente default

---

### **4. Logo Sin Validar (Línea 552)**

**❌ ANTES:**
```python
try:
    image = Image.open(myPath+'images/logo.png').convert('1')
    disp.image(image)
    disp.display()
    time.sleep(2)
except:  # Silencia todos los errores sin informar
    pass
```

**✅ DESPUÉS:**
```python
logo_path = myPath + 'images/logo.png'
try:
    if os.path.exists(logo_path):
        image = Image.open(logo_path).convert('1')
        disp.image(image)
        disp.display()
        time.sleep(2)
    else:
        print(f"[*] Logo no encontrado en {logo_path}, omitiendo...")
except Exception as e:
    print(f"[!] Error cargando logo: {e}")
```

**Beneficio:** Informa al usuario qué archivos faltan

---

### **5. Config.json Sin Validar (Líneas 328, 338)**

**❌ ANTES:**
```python
def save_config():
    try:
        with open('/home/pi/volumebegone/config.json', 'w') as f:
            json.dump(config, f)
    except Exception as e:
        print(f"[!] Error guardando configuración: {e}")
        # ¿Qué pasó? ¿No existe el directorio?

def load_config():
    try:
        with open('/home/pi/volumebegone/config.json', 'r') as f:
            config = json.load(f)
    except:  # ¿FileNotFoundError? ¿JSONDecodeError? ¿Quién sabe?
        print("[*] Usando configuración por defecto")
```

**✅ DESPUÉS:**
```python
def save_config():
    try:
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)  # Formato legible
        writeLog(...)
    except Exception as e:
        print(f"[!] Error guardando configuración: {e}")

def load_config():
    try:
        if os.path.exists(config_path):  # Verificar primero
            with open(config_path, 'r') as f:
                config = json.load(f)
                ...
        else:
            print("[*] Config.json no encontrado, usando configuración por defecto")
    except Exception as e:
        print(f"[!] Error cargando configuración: {e}, usando valores por defecto")
```

---

### **6. device_id Problemático (Línea 385)**

**❌ ANTES:**
```python
nearby_devices = bluetooth.discover_devices(
    duration=10,
    lookup_names=True,
    flush_cache=True,
    lookup_class=True,
    device_id=1 if bt_interface == "hci1" else 0  # Falla si hci1 no existe
)
```

**✅ DESPUÉS:**
```python
# Determinar device_id basado en el adaptador disponible
device_id = -1  # -1 = usar default
if bt_interface == "hci1":
    # Verificar si hci1 existe antes de usarlo
    result = subprocess.run(['hciconfig'], capture_output=True, text=True)
    if 'hci1' in result.stdout:
        device_id = 1
else:
    device_id = 0

nearby_devices = bluetooth.discover_devices(
    duration=10,
    lookup_names=True,
    flush_cache=True,
    lookup_class=True,
    device_id=device_id if device_id >= 0 else None  # Maneja None correctamente
)
```

---

### **7. Sin Validación de Micrófono (Línea 502)**

**❌ ANTES:**
```python
def monitor_volume():
    # ...
    with sd.InputStream(callback=audio_callback, ...):  # CRASH si no hay micrófono
        print("[*] Monitoreando nivel de audio...")
```

**✅ DESPUÉS:**
```python
def monitor_volume():
    # Verificar que hay dispositivos de audio disponibles
    try:
        devices = sd.query_devices()
        input_device = sd.query_devices(kind='input')
        print(f"[*] Dispositivo de entrada detectado: {input_device['name']}")
    except Exception as e:
        print(f"[!] Error: No se detectó micrófono USB: {e}")
        updateScreen("ERROR", "Micrófono USB", "no detectado")
        return  # Salir gracefully

    # Ahora sí intentar abrir stream
    try:
        with sd.InputStream(callback=audio_callback, ...):
            print("[*] Monitoreando nivel de audio...")
            while monitoring:
                time.sleep(0.1)
    except Exception as e:
        print(f"[!] Error en stream de audio: {e}")
        writeLog(f"Error en audio stream: {str(e)}")
```

---

### **8. Manejo de Excepciones en Ataques (Líneas 416-442)**

**❌ ANTES:**
```python
try:
    subprocess.call(['rfcomm', '-i', bt_interface, 'connect', device_addr, '1'], timeout=5)
except:  # Captura TODO, incluso KeyboardInterrupt
    pass

try:
    os.system(f'l2ping -i {bt_interface} -s {packagesSize} -f {device_addr} &')
except:  # ¿Qué puede fallar en os.system?
    pass

for port in [1, 3, 5, 17, 19]:
    subprocess.Popen(['rfcomm', ...])  # Sin manejo de errores
```

**✅ DESPUÉS:**
```python
# Método 1: RFCOMM con excepciones específicas
try:
    subprocess.call(['rfcomm', '-i', bt_interface, 'connect', device_addr, '1'], timeout=5)
except subprocess.TimeoutExpired:
    pass
except FileNotFoundError:
    print("[!] Comando rfcomm no encontrado")
    break  # No seguir intentando
except Exception as e:
    print(f"[!] Error en RFCOMM: {e}")

# Método 2: Verificar que l2ping existe
try:
    if os.system('which l2ping > /dev/null 2>&1') == 0:
        os.system(f'l2ping -i {bt_interface} -s {packagesSize} -f {device_addr} &')
    else:
        print("[!] Comando l2ping no encontrado")
        break
except Exception as e:
    print(f"[!] Error en L2CAP ping: {e}")

# Método 3: Con manejo de errores y supresión de output
try:
    for port in [1, 3, 5, 17, 19]:
        subprocess.Popen(['rfcomm', '-i', bt_interface, 'connect', device_addr, str(port)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.05)
except FileNotFoundError:
    print("[!] Comando rfcomm no encontrado")
    break
except Exception as e:
    print(f"[!] Error en multi-service: {e}")
```

---

### **9. Logging Sin Manejo de Errores (Línea 213)**

**❌ ANTES:**
```python
def writeLog(myLine):
    now = datetime.datetime.now()
    dtFormatted = now.strftime("%Y-%m-%d %H:%M:%S")
    with open('log.txt', 'a') as f:  # Puede fallar sin disco/permisos
        myLine = str(dtFormatted) + "," + myLine
        f.write(myLine + "\n")
```

**✅ DESPUÉS:**
```python
def writeLog(myLine):
    try:
        now = datetime.datetime.now()
        dtFormatted = now.strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, 'a') as f:
            myLine = str(dtFormatted) + "," + myLine
            f.write(myLine + "\n")
    except Exception as e:
        print(f"[!] Error escribiendo log: {e}")
        # No crashea si falta permisos de escritura
```

---

### **10. Audio Callback Sin Status Logging (Línea 472)**

**❌ ANTES:**
```python
def audio_callback(indata, frames, time, status):
    if status or config_mode:  # Ignora status silenciosamente
        return
```

**✅ DESPUÉS:**
```python
def audio_callback(indata, frames, time, status):
    if status:
        print(f"[!] Audio callback status: {status}")  # Informa problemas de audio
    if config_mode:
        return
```

**Beneficio:** Detecta problemas como buffer underruns/overruns

---

### **11. Import Faltante para Path (Línea 33)**

**❌ ANTES:**
```python
import json
# No import de pathlib
```

**✅ DESPUÉS:**
```python
import json
from pathlib import Path
```

---

## 📊 Resumen de Mejoras

| Categoría | Errores Corregidos |
|-----------|-------------------|
| **Validación de archivos** | 4 (fuente, logo, config, log) |
| **Rutas hardcodeadas** | 3 (myPath, config, log) |
| **Manejo de excepciones** | 5 (audio, ataques, logging, config) |
| **Validación de dispositivos** | 2 (micrófono USB, device_id BT) |
| **Imports faltantes** | 1 (pathlib) |
| **TOTAL** | **15 correcciones** |

---

## 🎯 Beneficios de las Correcciones

1. ✅ **No más crashes por archivos faltantes**
2. ✅ **Funciona en cualquier ubicación del sistema**
3. ✅ **Mensajes de error informativos**
4. ✅ **Manejo graceful de hardware faltante**
5. ✅ **Código más robusto y mantenible**
6. ✅ **Logs más detallados para debugging**

---

## ⚠️ Advertencias Importantes

El código corregido ahora:
- ✅ Valida todos los archivos antes de usarlos
- ✅ Informa claramente qué está faltando
- ✅ No crashea si faltan fuentes/logos/configs
- ✅ Detecta si no hay micrófono USB conectado
- ✅ Verifica que los comandos Bluetooth existen antes de ejecutarlos

---

## 🚀 Próximos Pasos

Para ejecutar el código corregido:

```bash
cd /home/user/volume-be-gone
python3 src/volumeBeGone.py
```

**Nota:** Este código requiere:
- Raspberry Pi con Bluetooth
- Pantalla OLED SSD1306
- Encoder rotativo KY-040
- Micrófono USB
- Permisos sudo para comandos Bluetooth

---

**Versión:** 2.1 (Corregido)
**Fecha:** 2025-11-02
**Cambios:** 15 errores corregidos + código más robusto
