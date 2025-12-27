# Manual de Usuario - Volume Be Gone v3.0

## Guía Completa Paso a Paso

---

## Tabla de Contenidos

1. [Primeros Pasos](#1-primeros-pasos)
2. [Instalación](#2-instalación)
3. [Configuración Inicial](#3-configuración-inicial)
4. [Uso Diario](#4-uso-diario)
5. [Control desde el Celular](#5-control-desde-el-celular)
6. [Ajustes y Personalización](#6-ajustes-y-personalización)
7. [Solución de Problemas](#7-solución-de-problemas)
8. [Consejos y Trucos](#8-consejos-y-trucos)

---

## 1. Primeros Pasos

### ¿Qué viene en el kit?

Si armaste tu propio kit, deberías tener:

| Componente | ¿Para qué sirve? |
|------------|------------------|
| Raspberry Pi | El "cerebro" del sistema |
| Fuente de poder 5V | Alimenta todo |
| Tarjeta microSD | Donde vive el sistema |
| Micrófono USB | Escucha el ruido ambiental |
| Pantalla OLED | Muestra información |
| Encoder (perilla) | Para ajustar configuración |
| Cables dupont | Conectan todo |

### Conexión de componentes

```
                    RASPBERRY PI
                    ┌─────────────────────────────────┐
                    │  [USB]  [USB]  [USB]  [USB]     │
                    │    │                            │
    Micrófono ──────┼────┘                            │
                    │                                 │
                    │         GPIO PINS               │
                    │    ┌─────────────────────┐      │
                    │    │ 1  2  3  4  5  ... │      │
                    │    └──┬──┬──┬──┬──┬─────┘      │
                    │       │  │  │  │  │            │
                    └───────┼──┼──┼──┼──┼────────────┘
                            │  │  │  │  │
                            │  │  │  │  └── Encoder
                            │  │  │  └───── Encoder
                            │  │  └──────── OLED
                            │  └─────────── OLED
                            └────────────── Alimentación

```

**No te preocupes** - El instalador te guiará en cada paso.

---

## 2. Instalación

### Paso 1: Preparar la Raspberry Pi

Si tu Raspberry Pi ya tiene el sistema operativo instalado, salta al Paso 2.

1. Descarga **Raspberry Pi Imager** en tu computadora
2. Inserta la tarjeta microSD
3. Selecciona "Raspberry Pi OS (64-bit)"
4. Escribe la imagen en la tarjeta
5. Inserta la tarjeta en la Raspberry Pi

### Paso 2: Descargar Volume Be Gone

Abre la terminal en tu Raspberry Pi y escribe:

```bash
cd ~
git clone https://github.com/neo3x/volume-be-gone.git
cd volume-be-gone
```

### Paso 3: Ejecutar el instalador

```bash
sudo bash scripts/install.sh
```

**¿Qué hace el instalador?**
- Instala todos los programas necesarios
- Configura los permisos correctos
- Prepara el sistema para iniciar automáticamente

El proceso toma aproximadamente **10-15 minutos**. Verás mensajes de progreso:

```
╔════════════════════════════════════════════════╗
║      Volume Be Gone v3.0 - Installer           ║
╚════════════════════════════════════════════════╝

[1/10] Detectando sistema...
[2/10] Actualizando sistema...
[3/10] Instalando dependencias...
...
```

### Paso 4: Reiniciar

Cuando termine, reinicia:

```bash
sudo reboot
```

---

## 3. Configuración Inicial

### Primera ejecución

Después de reiniciar, inicia Volume Be Gone:

```bash
cd ~/volume-be-gone
./start.sh
```

Verás la pantalla de inicio:

```
╔════════════════════════════════════════════════╗
║           VOLUME BE GONE v3.0                  ║
║              Iniciando...                      ║
╚════════════════════════════════════════════════╝

[■■■■■■■■■■] 100% - Sistema Listo!
```

### Pantalla principal

En la pantalla OLED verás:

```
┌────────────────────────┐
│ VOL: ▓▓▓▓▓░░░░░ 65 dB  │  <- Nivel actual
│ LIM: ████████░░ 75 dB  │  <- Tu límite
│ ──────────────────     │
│ Equipos: 3   [AUTO]    │  <- Dispositivos detectados
└────────────────────────┘
```

### Ajustar el límite de volumen

**Con la perilla (encoder):**
- **Gira a la derecha** → Aumenta el límite (más tolerante)
- **Gira a la izquierda** → Disminuye el límite (más estricto)
- **Presiona** → Guarda la configuración

**Desde el celular:** (ver sección 5)

---

## 4. Uso Diario

### Modo Automático (Recomendado)

Una vez configurado, el sistema funciona solo:

1. **Escucha** constantemente el nivel de ruido
2. **Detecta** parlantes Bluetooth cercanos cada 30 segundos
3. **Actúa** automáticamente cuando el ruido supera tu límite

No necesitas hacer nada más - solo déjalo encendido.

### Iniciar con la Raspberry Pi

Para que inicie automáticamente al encender:

```bash
sudo bash scripts/autostart.sh
```

Selecciona la opción **1) Habilitar auto-inicio**.

### Modos de operación

| Modo | Comando | Descripción |
|------|---------|-------------|
| Completo | `./start.sh` | Pantalla + Web + ESP32 |
| Solo Web | `./start-web-only.sh` | Sin pantalla física |
| Silencioso | `./start-headless.sh` | Sin pantalla ni web |

---

## 5. Control desde el Celular

### Configurar el Access Point

Para controlar desde tu celular sin necesidad de WiFi externo:

```bash
sudo bash scripts/setup_ap.sh
```

Sigue las instrucciones. Los valores por defecto son:
- **Red WiFi:** VolumeBeGone
- **Contraseña:** begone2025

### Conectar tu celular

1. **Abre WiFi** en tu celular
2. **Busca** la red "VolumeBeGone"
3. **Conecta** con la contraseña
4. **Abre el navegador** y ve a: `http://192.168.4.1:5000`

### Interfaz Web

```
┌─────────────────────────────────────────┐
│         VOLUME BE GONE                  │
│                                         │
│    ┌─────────────────────────────┐      │
│    │  ████████████░░░░  78 dB    │      │  <- Medidor en vivo
│    └─────────────────────────────┘      │
│                                         │
│    Umbral: [────●────] 75 dB            │  <- Deslizador
│                                         │
│    ┌─ Dispositivos Detectados ─────┐    │
│    │ 📻 JBL Flip 5        [ATACAR] │    │
│    │ 📻 Sony XB33         [ATACAR] │    │
│    │ 📻 Parlante Vecino   [ATACAR] │    │
│    └───────────────────────────────┘    │
│                                         │
│    [🔍 ESCANEAR]    [⚡ AUTO-ATAQUE]    │
│                                         │
└─────────────────────────────────────────┘
```

### Funciones disponibles

| Botón | Función |
|-------|---------|
| Deslizador | Ajusta el umbral de volumen |
| ESCANEAR | Busca nuevos dispositivos |
| ATACAR | Ataca un dispositivo específico |
| AUTO-ATAQUE | Activa/desactiva modo automático |

---

## 6. Ajustes y Personalización

### Archivo de configuración

La configuración se guarda en `config/settings.json`:

```json
{
    "audio": {
        "threshold": 75        <- Tu límite en dB
    },
    "bluetooth": {
        "scan_duration": 10    <- Segundos de escaneo
    },
    "attack": {
        "auto_attack": false   <- Ataque automático
    }
}
```

**Para editar:**
```bash
nano config/settings.json
```

### Configuraciones recomendadas

| Situación | Umbral sugerido |
|-----------|-----------------|
| Oficina tranquila | 60-65 dB |
| Casa normal | 70-75 dB |
| Zona ruidosa | 80-85 dB |
| Eventos/fiestas | 90+ dB |

---

## 7. Solución de Problemas

### "No detecta ningún dispositivo"

**Posibles causas:**
1. El adaptador Bluetooth no está funcionando
2. No hay dispositivos Bluetooth cerca

**Solución:**
```bash
# Verificar Bluetooth
hciconfig

# Debería mostrar algo como:
# hci0: ... UP RUNNING
```

Si no aparece "UP RUNNING":
```bash
sudo hciconfig hci0 up
```

### "La pantalla no enciende"

**Posibles causas:**
1. Cables mal conectados
2. Dirección I2C incorrecta

**Solución:**
```bash
# Verificar conexión I2C
sudo i2cdetect -y 1

# Debería mostrar "3c" en alguna parte
```

### "El micrófono no funciona"

**Posibles causas:**
1. Micrófono no conectado
2. Permisos incorrectos

**Solución:**
```bash
# Listar dispositivos de audio
arecord -l

# Probar grabación
arecord -d 3 test.wav && aplay test.wav
```

### "Error al iniciar el servicio"

**Ver los logs:**
```bash
sudo journalctl -u masterbegone -n 50
```

**Reiniciar el servicio:**
```bash
sudo systemctl restart masterbegone
```

### "No puedo conectar desde el celular"

**Verificar Access Point:**
```bash
sudo systemctl status hostapd
sudo systemctl status dnsmasq
```

**Reiniciar servicios:**
```bash
sudo systemctl restart hostapd dnsmasq
```

---

## 8. Consejos y Trucos

### Para mejores resultados

1. **Ubicación del micrófono**
   - Colócalo orientado hacia la fuente de ruido
   - Evita que esté cerca de ventiladores o aire acondicionado

2. **Adaptador Bluetooth**
   - Usa un adaptador USB Clase 1 para mayor alcance
   - Colócalo en una posición elevada

3. **Calibración del umbral**
   - Comienza con un valor alto (80 dB)
   - Ve bajando gradualmente hasta encontrar tu punto ideal

### Comandos útiles

| Tarea | Comando |
|-------|---------|
| Ver estado | `sudo systemctl status masterbegone` |
| Ver logs en vivo | `sudo journalctl -u masterbegone -f` |
| Reiniciar | `sudo systemctl restart masterbegone` |
| Detener | `sudo systemctl stop masterbegone` |
| Iniciar | `sudo systemctl start masterbegone` |

### Atajos de teclado (en terminal)

- `Ctrl + C` → Detener el programa
- `Ctrl + Z` → Pausar (no recomendado)

---

## ¿Necesitas más ayuda?

- **Documentación técnica:** `docs/tecnico/`
- **Problemas conocidos:** `docs/TROUBLESHOOTING.md`
- **Reportar errores:** GitHub Issues

---

*Manual de Usuario v3.0 - Diciembre 2025*
*Desarrollado por Francisco Ortiz Rojas*
