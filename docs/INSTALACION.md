# INSTALACIÓN - Volume Be Gone 2.1

Guía completa de instalación con todas las nuevas herramientas y mejoras implementadas.

---

## 📋 REQUISITOS

### Hardware
- Raspberry Pi 3/4/5
- Micrófono USB
- Display OLED SSD1306 (128x64, I2C)
- Encoder rotativo KY-040
- **Adaptador Bluetooth Clase 1** (recomendado: CSR8510, alcance 100m)
  - O usar Bluetooth interno de RPi (alcance 10m)

### Software
- Raspberry Pi OS (Debian 12 "Bookworm" o Debian 13 "Trixie")
- Python 3.11+
- BlueZ 5.66+

---

## 🚀 INSTALACIÓN AUTOMÁTICA (RECOMENDADA)

### Paso 1: Clonar el repositorio
```bash
cd ~
git clone https://github.com/neo3x/volume-be-gone.git
cd volume-be-gone
```

### Paso 2: Ejecutar instalador
```bash
sudo bash scripts/install.sh
```

El instalador hace:
1. ✅ Actualiza paquetes del sistema
2. ✅ Instala dependencias Python y sistema
3. ✅ **Instala herramientas Bluetooth nuevas:**
   - `bluez` (hcitool, l2ping, rfcomm, hciconfig)
   - `bluez-tools` (sdptool para enumeración SDP)
   - `bluez-hcidump` (captura de tráfico BT)
4. ✅ **Configura permisos especiales (CAP_NET_RAW, CAP_NET_ADMIN):**
   - hcitool (scanning BLE/Classic)
   - l2ping (ataques L2CAP)
   - rfcomm (ataques RFCOMM)
   - sdptool (enumeración SDP)
   - hcidump (captura tráfico)
   - hciconfig (config adaptador)
   - bccmd (adaptadores CSR)
5. ✅ Habilita I2C, SPI, GPIO
6. ✅ Configura grupos de usuario
7. ✅ Crea servicio systemd
8. ✅ Configura auto-inicio

### Paso 3: Verificar instalación
```bash
bash scripts/verify_installation.sh
```

**Salida esperada:**
```
[1/5] Verificando herramientas Bluetooth...
✓ HCI Tool (scanning Classic/BLE) (hcitool)
✓ L2CAP Ping (ataque L2CAP) (l2ping)
✓ RFCOMM (ataque RFCOMM) (rfcomm)
✓ SDP Tool (enumeración servicios) (sdptool)
✓ HCI Dump (captura tráfico) (hcidump)
✓ HCI Config (configuración adaptador) (hciconfig)
⚠ BCCMD (adaptadores CSR) (bccmd) - OPCIONAL

[2/5] Verificando módulos Python...
✓ PyBluez (Bluetooth Python) (Python: bluetooth)
✓ SoundDevice (captura audio) (Python: sounddevice)
✓ NumPy (procesamiento audio) (Python: numpy)
✓ RPi.GPIO (GPIO control) (Python: RPi.GPIO)
✓ Luma OLED (display SSD1306) (Python: luma.oled)
✓ Pillow (imágenes) (Python: PIL)

[3/5] Verificando permisos de herramientas...
✓ hcitool tiene permisos correctos
✓ l2ping tiene permisos correctos
✓ rfcomm tiene permisos correctos
✓ sdptool tiene permisos correctos
✓ hciconfig tiene permisos correctos
✓ hcidump tiene permisos correctos

[4/5] Verificando adaptadores Bluetooth...
✓ Adaptadores Bluetooth detectados: 2
  - hci0:	Type: Primary  Bus: UART
  - hci1:	Type: Primary  Bus: USB

[5/5] Verificando dispositivos I2C...
✓ /dev/i2c-1 disponible (para display OLED)
  ✓ Display OLED detectado en bus I2C

=====================================
RESUMEN
=====================================
Total de verificaciones: 20
Pasadas: 20

✓ TODAS LAS VERIFICACIONES PASARON
El sistema está listo para funcionar
```

### Paso 4: Reiniciar
```bash
sudo reboot
```

### Paso 5: Habilitar auto-inicio
```bash
sudo systemctl enable volumebegone
sudo systemctl start volumebegone
```

---

## 🔧 INSTALACIÓN MANUAL (AVANZADA)

Si prefieres instalar manualmente:

### 1. Dependencias del sistema
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-pip python3-dev \
    python3-numpy python3-scipy \
    bluetooth bluez libbluetooth-dev \
    bluez-tools \
    bluez-hcidump \
    i2c-tools \
    python3-rpi.gpio \
    python3-bluez \
    python3-pillow \
    python3-psutil \
    portaudio19-dev
```

### 2. Dependencias Python (vía pip)
```bash
# Si tienes PEP 668 (Debian 12+)
sudo pip3 install --break-system-packages -r requirements.txt

# O si no tienes PEP 668
sudo pip3 install -r requirements.txt
```

### 3. Configurar permisos Bluetooth
```bash
# Dar permisos CAP_NET_RAW y CAP_NET_ADMIN a herramientas BT
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/hcitool
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/l2ping
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/rfcomm
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/sdptool
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/hciconfig
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/hcidump
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/python3

# Verificar
getcap /usr/bin/hcitool
# Salida: /usr/bin/hcitool = cap_net_admin,cap_net_raw+eip
```

### 4. Habilitar I2C
```bash
sudo raspi-config
# Interface Options -> I2C -> Enable

# O manualmente:
echo "dtparam=i2c_arm=on" | sudo tee -a /boot/firmware/config.txt
echo "i2c-dev" | sudo tee -a /etc/modules
sudo reboot
```

### 5. Agregar usuario a grupos
```bash
sudo usermod -a -G bluetooth,audio,i2c,gpio,spi,dialout $USER
```

---

## 🧪 PRUEBAS POST-INSTALACIÓN

### Test 1: Verificar herramientas Bluetooth
```bash
# Verificar que todas las herramientas estén instaladas
which hcitool l2ping rfcomm sdptool hcidump hciconfig

# Test hcitool (scanning)
sudo hcitool scan

# Test BLE scanning
sudo hcitool lescan
```

### Test 2: Verificar adaptadores Bluetooth
```bash
hciconfig
# Deberías ver hci0 (interno) y/o hci1 (USB externo)

# Configurar TX Power (debe funcionar sin errores)
sudo hciconfig hci1 inqtpl 4
```

### Test 3: Verificar I2C y display
```bash
# Detectar dispositivos I2C
sudo i2cdetect -y 1

# Deberías ver algo así:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:          -- -- -- -- -- -- -- -- -- -- -- -- --
# 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 30: -- -- -- -- -- -- -- -- -- -- -- -- 3c -- -- --
#                                         ^^
#                                    Display OLED
```

### Test 4: Ejecutar Volume Be Gone
```bash
cd ~/volume-be-gone
sudo python3 src/volumeBeGone.py
```

**Salida esperada:**
```
[*] Adaptadores encontrados: ['hci0', 'hci1']
[*] Usando adaptador externo (hci1) - Clase 1
[*] Configurando hci1 para máximo rendimiento...
[+] TX Power configurado al máximo (nivel 4)
[*] Optimizando scan window/interval...
[+] Adaptador configurado exitosamente
[*] Encoder configurado (modo polling)
[*] Configuración cargada: Umbral=70dB
```

---

## 🔍 SOLUCIÓN DE PROBLEMAS

### Problema: "hcitool: command not found"
```bash
# Instalar bluez
sudo apt-get install bluez bluez-tools

# Verificar instalación
which hcitool
```

### Problema: "sdptool: command not found"
```bash
# Instalar bluez-tools
sudo apt-get install bluez-tools

# Verificar
which sdptool
```

### Problema: "Operation not permitted" con hcitool
```bash
# Configurar permisos
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/hcitool

# Verificar
getcap /usr/bin/hcitool
```

### Problema: No detecta adaptador Bluetooth USB
```bash
# Verificar que está conectado
lsusb | grep -i bluetooth

# Verificar status
hciconfig -a

# Activar adaptador
sudo hciconfig hci1 up
```

### Problema: No detecta display OLED
```bash
# Verificar que I2C esté habilitado
ls /dev/i2c-1

# Si no existe:
sudo raspi-config
# -> Interface Options -> I2C -> Enable
sudo reboot

# Verificar dirección I2C del display
sudo i2cdetect -y 1
```

### Problema: Error "cap_net_raw: permission denied"
```bash
# Ejecutar script de instalación completo
sudo bash scripts/install.sh

# O configurar permisos manualmente (ver sección 3)
```

---

## 📊 VERIFICACIÓN DE MEJORAS IMPLEMENTADAS

### Escaneo Dual-Mode (Classic + BLE)
```bash
# En el log.txt deberías ver:
tail -f log.txt | grep "BLE:"
# [+] BLE: AA:BB:CC:DD:EE:FF - Device Name

# Y también Classic:
tail -f log.txt | grep "INQ:"
# [+] INQ: AA:BB:CC:DD:EE:FF - Speaker Name
```

### Ataques Paralelos
```bash
# Verificar procesos l2ping activos (deberían ser 40+)
watch -n 1 'ps aux | grep l2ping | wc -l'
```

### Captura hcidump
```bash
# Verificar archivos de captura
ls -lh bt_capture_*.dump

# Analizar con Wireshark (en PC)
wireshark bt_capture_20251222_123456.dump
```

### TX Power Máximo
```bash
# Verificar configuración
hciconfig hci1 inqtpl
# Current inquiry transmit power level: 4
```

---

## 🎯 CONFIGURACIÓN ÓPTIMA

### Adaptador Bluetooth Clase 1 (Recomendado)

**Adaptadores probados:**
- CSR8510 (~$10 USD) - ✅ Excelente
- Broadcom BCM20702 (~$15 USD) - ✅ Muy bueno
- Intel AX200/210 (~$20 USD) - ✅ Profesional

**Configuración:**
```python
# En src/volumeBeGone.py (líneas 84-85)
bt_interface = "hci1"  # Adaptador USB externo
use_external_adapter = True
```

### Parámetros de Ataque Ajustables

```python
# L2CAP Ping (líneas 59-61)
l2ping_threads_per_device = 40  # Aumentar a 50-60 para más agresividad
l2ping_package_sizes = [600, 800, 1200]  # MTU sizes
l2ping_timeout = 2

# RFCOMM (líneas 64-65)
rfcomm_max_channels = 30  # Canales a probar
rfcomm_connections_per_channel = 5  # Conexiones por canal

# A2DP/AVDTP (líneas 68-69)
a2dp_stream_attacks = True  # Ataques específicos parlantes
avdtp_malformed_packets = True

# SDP (línea 72)
sdp_enumerate_before_attack = True  # Enumerar servicios primero
```

---

## 📝 LOGS Y MONITOREO

### Ver logs en tiempo real
```bash
# Log del sistema
tail -f ~/volume-be-gone/log.txt

# Log de systemd
sudo journalctl -u volumebegone -f

# Log de Bluetooth
sudo journalctl -u bluetooth -f
```

### Analizar capturas hcidump
```bash
# Convertir dump a texto legible
hcidump -r bt_capture_20251222_123456.dump

# O usar Wireshark en PC
scp pi@raspberrypi:~/volume-be-gone/bt_capture_*.dump .
wireshark bt_capture_*.dump
```

---

## ✅ CHECKLIST DE INSTALACIÓN

- [ ] Sistema actualizado (`sudo apt-get update && upgrade`)
- [ ] Dependencias instaladas (`bluez bluez-tools bluez-hcidump`)
- [ ] Permisos configurados (CAP_NET_RAW, CAP_NET_ADMIN)
- [ ] I2C habilitado (`/dev/i2c-1` existe)
- [ ] Display OLED conectado (detectado en `i2cdetect`)
- [ ] Adaptador Bluetooth detectado (`hciconfig`)
- [ ] Usuario en grupos correctos (`bluetooth audio i2c gpio`)
- [ ] Script de verificación pasado (`verify_installation.sh`)
- [ ] Test manual exitoso (`sudo python3 src/volumeBeGone.py`)
- [ ] Servicio systemd funcional (`systemctl status volumebegone`)

---

## 🚀 PRÓXIMOS PASOS

1. Configurar umbral de volumen con el encoder
2. Probar detección con parlante real
3. Verificar ataques efectivos
4. Habilitar auto-inicio: `sudo systemctl enable volumebegone`
5. Analizar capturas hcidump para optimizar

---

## 📚 DOCUMENTACIÓN ADICIONAL

- **Mejoras implementadas:** Ver `MEJORAS_IMPLEMENTADAS.md`
- **Manual de uso:** Ver `README.md`
- **Troubleshooting:** Esta guía, sección "Solución de problemas"

---

**Autor:** Francisco Ortiz Rojas
**Versión:** 2.1 Enhanced
**Fecha:** Diciembre 2025
