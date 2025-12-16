# Guia de Auto-Inicio - Volume Be Gone

**Volume Be Gone v2.1**
**Author:** Francisco Ortiz Rojas - Ingeniero Electronico
**Contact:** francisco.ortiz@marfinex.com

---

## Resumen

Esta guía explica cómo configurar **Volume Be Gone** para que se inicie automáticamente al encender tu Raspberry Pi, mostrando el progreso de carga en la pantalla OLED.

---

## ✨ Características del Auto-Inicio

Cuando habilitas el auto-inicio, al encender tu Raspberry Pi verás:

### **En la Pantalla OLED:**

```
┌─────────────────────────┐
│ Volume BeGone      v2.1 │
│                         │
│ Cargando...       42%   │
│ Check Bluetooth...      │
│                         │
│ ████████░░░░░░░░░░░░    │
└─────────────────────────┘
```

**Progreso de carga (7 pasos):**
1. ✅ Init Display... (14%)
2. ✅ Setup GPIO... (28%)
3. ✅ Load Config... (42%)
4. ✅ Check Bluetooth... (57%)
5. ✅ Check Mic... (71%)
6. ✅ Load Resources... (85%)
7. ✅ System Ready! (100%)

Después muestra la pantalla de configuración de umbral.

---

## 🔧 Instalación del Auto-Inicio

### **Método 1: Script Automático (RECOMENDADO)**

```bash
cd /home/user/volume-be-gone

# Dar permisos de ejecución
sudo chmod +x scripts/autostart.sh

# Ejecutar el gestor de auto-inicio
sudo bash scripts/autostart.sh
```

**Menú interactivo:**
```
========================================
  Volume Be Gone - Auto-Start Manager
========================================

Estado actual:
  Servicio instalado: SÍ
  Auto-inicio: DESHABILITADO
  Estado: DETENIDO

Opciones:
  1) Habilitar auto-inicio al encender
  2) Deshabilitar auto-inicio
  3) Iniciar servicio ahora
  4) Detener servicio
  5) Ver logs en tiempo real
  6) Ver estado del servicio
  0) Salir

Selecciona una opción [0-6]:
```

Selecciona **opción 1** para habilitar.

---

### **Método 2: Manual con systemd**

```bash
# 1. Copiar el servicio a systemd
sudo cp scripts/volumebegone.service /etc/systemd/system/

# 2. Recargar systemd
sudo systemctl daemon-reload

# 3. Habilitar auto-inicio
sudo systemctl enable volumebegone

# 4. Iniciar servicio ahora (opcional)
sudo systemctl start volumebegone
```

---

## 📊 Gestión del Servicio

### **Comandos Útiles:**

```bash
# Ver estado del servicio
sudo systemctl status volumebegone

# Iniciar servicio
sudo systemctl start volumebegone

# Detener servicio
sudo systemctl stop volumebegone

# Reiniciar servicio
sudo systemctl restart volumebegone

# Ver logs en tiempo real
sudo journalctl -u volumebegone -f

# Ver últimas 50 líneas de log
sudo journalctl -u volumebegone -n 50

# Ver logs desde hoy
sudo journalctl -u volumebegone --since today

# Deshabilitar auto-inicio
sudo systemctl disable volumebegone
```

---

## 🔍 Verificar que Funciona

### **Paso 1: Habilitar y verificar**

```bash
# Habilitar auto-inicio
sudo systemctl enable volumebegone

# Verificar que está habilitado
systemctl is-enabled volumebegone
# Debe mostrar: enabled
```

### **Paso 2: Probar sin reiniciar**

```bash
# Iniciar el servicio
sudo systemctl start volumebegone

# Ver si está corriendo
sudo systemctl status volumebegone
```

**Salida esperada:**
```
● volumebegone.service - Volume Be Gone - Bluetooth Speaker Control
   Loaded: loaded (/etc/systemd/system/volumebegone.service; enabled)
   Active: active (running) since Sat 2025-11-02 10:30:15 UTC; 5s ago
 Main PID: 1234 (python3)
   CGroup: /system.slice/volumebegone.service
           └─1234 /usr/bin/python3 /home/pi/volumebegone/volumeBeGone.py

Nov 02 10:30:15 raspberrypi systemd[1]: Started Volume Be Gone...
Nov 02 10:30:20 raspberrypi volumebegone[1234]: [1/7] Pantalla OLED inicializada
Nov 02 10:30:21 raspberrypi volumebegone[1234]: [2/7] Configurando encoder
...
```

### **Paso 3: Ver la pantalla OLED**

Observa tu pantalla OLED, deberías ver:
1. Barra de progreso cargando (7 pasos)
2. Logo (si existe el archivo)
3. Pantalla de configuración de umbral

### **Paso 4: Probar con reinicio completo**

```bash
# Reiniciar Raspberry Pi
sudo reboot
```

Al encender:
- El servicio inicia automáticamente después de ~15 segundos
- La pantalla OLED muestra el progreso de carga
- Después muestra la configuración de umbral

---

## 🐛 Solución de Problemas

### **Problema: El servicio no inicia**

```bash
# Ver errores específicos
sudo journalctl -u volumebegone -n 50 --no-pager

# Verificar que Python encuentra las librerías
sudo -u pi python3 -c "import bluetooth, sounddevice, Adafruit_SSD1306"

# Verificar permisos
ls -la /home/pi/volumebegone/volumeBeGone.py
```

---

### **Problema: Error "No Bluetooth"**

```bash
# Verificar adaptadores Bluetooth
sudo hciconfig

# Debe mostrar hci0 (y hci1 si tienes adaptador externo)
# Si no aparece:
sudo systemctl status bluetooth
sudo systemctl restart bluetooth
```

---

### **Problema: Error "No Microfono"**

```bash
# Listar dispositivos de audio
python3 -c "import sounddevice as sd; print(sd.query_devices())"

# Verificar que el micrófono USB está conectado
lsusb | grep -i audio

# Verificar ALSA
arecord -l
```

---

### **Problema: Pantalla OLED en blanco**

```bash
# Verificar I2C
sudo i2cdetect -y 1

# Debe mostrar dispositivo en 0x3C o 0x3D
# Si no aparece, revisar conexiones físicas
```

---

### **Problema: El servicio se reinicia constantemente**

```bash
# Ver logs de fallos
sudo journalctl -u volumebegone | grep -i error

# Deshabilitar temporalmente para debugging
sudo systemctl stop volumebegone
sudo systemctl disable volumebegone

# Ejecutar manualmente para ver errores
cd /home/pi/volumebegone
sudo python3 volumeBeGone.py
```

---

## ⚙️ Configuración del Servicio

El archivo `/etc/systemd/system/volumebegone.service` contiene:

```ini
[Unit]
Description=Volume Be Gone - Bluetooth Speaker Control
After=bluetooth.target sound.target network.target multi-user.target
Wants=bluetooth.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/volumebegone
Environment="PYTHONUNBUFFERED=1"
ExecStartPre=/bin/sleep 15          # Espera 15s a que hardware esté listo
ExecStart=/usr/bin/python3 /home/pi/volumebegone/volumeBeGone.py
Restart=on-failure                   # Reinicia si falla
RestartSec=30                        # Espera 30s antes de reiniciar
StandardOutput=journal               # Logs a systemd journal

[Install]
WantedBy=multi-user.target
```

**Parámetros ajustables:**
- `ExecStartPre=/bin/sleep 15` → Tiempo de espera inicial (aumentar si falla al iniciar)
- `RestartSec=30` → Tiempo entre reintentos (si falla)
- `StartLimitBurst=5` → Máximo 5 intentos de reinicio

---

## 📝 Indicadores Visuales en OLED

### **Durante el Arranque:**

| Paso | Mensaje en OLED | Duración |
|------|----------------|----------|
| 1 | Init Display... | 0.5s |
| 2 | Setup GPIO... | 0.5s |
| 3 | Load Config... | 0.5s |
| 4 | Check Bluetooth... | 0.5s |
| 5 | Check Mic... | 0.5s |
| 6 | Load Resources... | 0.3s |
| 7 | System Ready! | 1.0s |

**Total:** ~4 segundos de animación de carga

### **Errores Visibles:**

```
┌─────────────────────────┐
│ Volume BeGone           │
│         [X]             │  ← Icono de error
│ ERROR                   │
│ No Bluetooth            │
└─────────────────────────┘
```

---

## 🎯 Mejores Prácticas

### **1. Probar antes de habilitar auto-inicio**

```bash
# Siempre probar manualmente primero
sudo python3 /home/pi/volumebegone/volumeBeGone.py

# Si funciona correctamente, entonces habilitar auto-inicio
sudo systemctl enable volumebegone
```

### **2. Monitorear los primeros arranques**

```bash
# Después de habilitar, reinicia y monitorea logs
sudo reboot

# Después del reinicio (vía SSH):
sudo journalctl -u volumebegone -f
```

### **3. Configurar umbral antes de auto-inicio**

El umbral guardado en `config.json` se usará al arrancar automáticamente.

```bash
# Ejecutar una vez manualmente, configurar umbral, presionar OK
sudo python3 /home/pi/volumebegone/volumeBeGone.py

# Esto guarda el umbral en config.json
# Ahora al arrancar automáticamente usará ese umbral
```

---

## 🔄 Deshabilitar Auto-Inicio

### **Método 1: Script**

```bash
sudo bash scripts/autostart.sh
# Seleccionar opción 2
```

### **Método 2: Manual**

```bash
sudo systemctl stop volumebegone
sudo systemctl disable volumebegone
```

---

## 📱 Control Remoto (SSH)

Puedes controlar el servicio vía SSH:

```bash
# Conectar por SSH
ssh pi@<IP_de_tu_raspberry>

# Ver estado
sudo systemctl status volumebegone

# Reiniciar
sudo systemctl restart volumebegone

# Ver logs
sudo journalctl -u volumebegone -f
```

---

## ✅ Checklist de Verificación

Antes de habilitar auto-inicio, verifica:

- [ ] El script funciona correctamente al ejecutarlo manualmente
- [ ] La pantalla OLED muestra información
- [ ] El encoder rotativo responde
- [ ] El adaptador Bluetooth es detectado
- [ ] El micrófono USB es reconocido
- [ ] El umbral está configurado correctamente
- [ ] Los logs no muestran errores críticos

---

## 🎓 Preguntas Frecuentes

**Q: ¿Cuánto tarda en iniciar al encender la RPi?**
A: Aproximadamente 20-25 segundos después del boot (15s de espera + 4s de carga)

**Q: ¿Puedo cambiar el umbral después de que inicia automáticamente?**
A: Sí, gira el encoder y presiona el botón para confirmar. Se guarda en config.json.

**Q: ¿Qué pasa si falla el micrófono al arrancar?**
A: El servicio muestra error en OLED y se detiene. Se reintentará en 30 segundos.

**Q: ¿Puedo ver qué está haciendo sin pantalla?**
A: Sí, vía logs: `sudo journalctl -u volumebegone -f`

**Q: ¿Cómo detengo el servicio temporalmente?**
A: `sudo systemctl stop volumebegone`

---

## 📚 Referencias

- [Systemd Service Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Journalctl Guide](https://www.freedesktop.org/software/systemd/man/journalctl.html)
- [Raspberry Pi Auto-Start Guide](https://www.raspberrypi.org/documentation/linux/usage/systemd.md)

---

---
**Version:** 2.1
**Ultima actualizacion:** 2025-12-15
**Author:** Francisco Ortiz Rojas - Ingeniero Electronico
**Auto-inicio implementado con systemd**
