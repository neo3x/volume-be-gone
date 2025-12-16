# Guia de Solucion de Problemas

**Volume Be Gone v2.1**
**Author:** Francisco Ortiz Rojas - Ingeniero Electronico
**Contact:** francisco.ortiz@marfinex.com

---

## Problemas comunes y soluciones

### 1. Pantalla OLED no funciona

**Sintoma**: La pantalla no muestra nada

**Solucion**:
```bash
# Verificar conexiones I2C
sudo i2cdetect -y 1
# Debe mostrar 3c o 3d
```

Si no aparece:
- Verificar conexiones fisicas
- Verificar que I2C este habilitado
- Probar con `sudo i2cdetect -y 0`

### 2. Microfono no detectado

**Sintoma**: Error al iniciar captura de audio

**Solucion**:
```bash
# Listar dispositivos de audio
arecord -l
```

Si no aparece:
- Reconectar microfono USB
- Probar otro puerto USB
- Reiniciar Raspberry Pi

### 3. Bluetooth no encuentra dispositivos

**Sintoma**: 0 dispositivos encontrados

**Solucion**:
```bash
# Reiniciar servicio Bluetooth
sudo systemctl restart bluetooth

# Escanear manualmente
sudo hcitool scan
```

### 4. Error de permisos

**Sintoma**: Permission denied

**Solucion**:
```bash
# Agregar usuario a grupos necesarios
sudo usermod -a -G bluetooth,audio,i2c,gpio pi

# Cerrar sesion y volver a entrar
logout
```

### 5. Alto consumo de CPU

**Sintoma**: Sistema lento, temperatura alta

**Solucion**:
- Reducir frecuencia de escaneo en config.json
- Usar disipadores de calor
- Limitar numero de dispositivos atacados simultaneamente

## Logs y depuracion

Ver archivo de log:
```bash
tail -f /home/pi/volumebegone/log.txt
```

Modo debug:
```bash
# Editar config.json
"debug_mode": true
```

## Contacto

Si el problema persiste, abre un issue en GitHub con:
- Descripcion del problema
- Mensajes de error completos
- Version de Raspberry Pi OS
- Salida de `python3 --version`
