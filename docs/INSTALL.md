# Guia de Instalacion Detallada

**Volume Be Gone v2.1**
**Author:** Francisco Ortiz Rojas - Ingeniero Electronico
**Contact:** francisco.ortiz@marfinex.com

---

## Requisitos previos

- Raspberry Pi 3B+ o 4 con Raspberry Pi OS instalado
- Conexion a internet
- Acceso SSH o teclado/monitor

## Pasos de instalacion

### 1. Actualizar sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Habilitar interfaces

```bash
sudo raspi-config
# Ir a: Interface Options
# Habilitar: I2C, SPI
```

### 3. Instalar dependencias del sistema

```bash
sudo apt install -y python3-pip python3-dev python3-numpy
sudo apt install -y bluetooth bluez libbluetooth-dev
sudo apt install -y python3-smbus i2c-tools
sudo apt install -y portaudio19-dev python3-pyaudio
sudo apt install -y libatlas-base-dev python3-pil git
```

### 4. Clonar repositorio

```bash
cd /home/pi
git clone https://github.com/tu-usuario/volume-be-gone.git
cd volume-be-gone
```

### 5. Instalar dependencias Python

```bash
sudo pip3 install -r requirements.txt
```

### 6. Configurar permisos

```bash
sudo usermod -a -G bluetooth,audio,i2c pi
sudo setcap 'cap_net_raw,cap_net_admin+eip' $(which python3)
```

### 7. Copiar archivos

```bash
sudo mkdir -p /home/pi/volumebegone
sudo cp src/volumeBeGone.py /home/pi/volumebegone/
sudo cp -r resources/images /home/pi/volumebegone/
sudo cp src/config.json.template /home/pi/volumebegone/config.json
```

### 8. Configurar servicio (opcional)

```bash
sudo cp scripts/volumebegone.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable volumebegone
sudo systemctl start volumebegone
```

## Verificacion

```bash
# Verificar I2C
sudo i2cdetect -y 1

# Verificar Bluetooth
hciconfig -a

# Verificar audio
arecord -l
```

## Siguiente paso

Ejecutar `sudo python3 /home/pi/volumebegone/volumeBeGone.py` para iniciar.
