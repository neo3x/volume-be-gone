# Volume Be Gone v3.0

### Tu solución inteligente para el ruido excesivo

---

## ¿Qué es esto?

**Volume Be Gone** es un dispositivo que detecta cuando hay demasiado ruido de parlantes Bluetooth y automáticamente intenta silenciarlos.

**Ideal para:**
- Mantener la paz en tu hogar u oficina
- Ambientes donde necesitas tranquilidad
- Cualquier lugar con ruido excesivo de parlantes

---

## Instalación en 3 Pasos

```bash
# 1. Descargar
git clone https://github.com/neo3x/volume-be-gone.git && cd volume-be-gone

# 2. Instalar
sudo bash scripts/install.sh

# 3. Ejecutar
./start.sh
```

**¿Necesitas más ayuda?** Ver [Guía de Inicio Rápido](docs/usuario/INICIO_RAPIDO.md)

---

## Control desde tu Celular

```bash
sudo bash scripts/setup_ap.sh
```

Luego:
1. Conecta a WiFi **VolumeBeGone** (contraseña: `begone2025`)
2. Abre en el navegador: `http://192.168.4.1:5000`

---

## Documentación

### Para Usuarios

| Documento | ¿Qué encontrarás? |
|-----------|-------------------|
| [¿Qué es Volume Be Gone?](docs/usuario/QUE_ES_VOLUME_BE_GONE.md) | Explicación simple y clara |
| [Inicio Rápido](docs/usuario/INICIO_RAPIDO.md) | Empezar en 5 minutos |
| [Manual de Usuario](docs/usuario/MANUAL_USUARIO.md) | Guía completa paso a paso |

### Para Técnicos

| Documento | Contenido |
|-----------|-----------|
| [Instalación Detallada](docs/INSTALACION.md) | Instalación manual |
| [Solución de Problemas](docs/TROUBLESHOOTING.md) | Errores comunes |
| [Arquitectura](docs/tecnico/ARQUITECTURA_HIBRIDA.md) | Diseño del sistema |
| [Hardware](docs/hardware/) | Diagramas de conexiones |

---

## Hardware Necesario

### Versión Básica (~$60)

| Componente | Descripción |
|------------|-------------|
| Raspberry Pi 3B+/4 | El cerebro |
| Micrófono USB | Para escuchar |
| Pantalla OLED | Para ver el estado |
| Encoder (perilla) | Para ajustar |

### Versión Avanzada (~$100)

Agrega mayor alcance con:
- ESP32 + 2x nRF24L01 + antenas

---

## Comandos Útiles

```bash
./start.sh                              # Iniciar
./start-web-only.sh                     # Solo interfaz web
sudo systemctl status masterbegone      # Ver estado
sudo journalctl -u masterbegone -f      # Ver logs
sudo bash scripts/autostart.sh          # Configurar inicio automático
```

---

## Estructura del Proyecto

```
volume-be-gone/
├── docs/
│   ├── usuario/          # Manuales para usuarios
│   ├── tecnico/          # Documentación técnica
│   └── hardware/         # Diagramas de conexiones
├── src/
│   ├── masterbegone.py   # Programa principal
│   ├── modules/          # Módulos del sistema
│   └── static/           # Interfaz web
├── scripts/              # Scripts de instalación
├── firmware/             # Código para ESP32
└── config/               # Configuración
```

---

## Disclaimer

> **IMPORTANTE**: Este proyecto es **solo para fines educativos**.
> Úsalo únicamente con tus propios dispositivos o con permiso explícito.
> El uso indebido puede ser ilegal.

---

## Créditos

**Desarrollado por:** Francisco Ortiz Rojas - Ingeniero Electrónico

**Contacto:** francisco.ortiz@marfinex.com

**Inspirado en:** "Reggaeton Be Gone" de Roni Bandini

---

## Licencia

MIT License - Ver [LICENSE](LICENSE)

---

<p align="center">
  <b>Volume Be Gone v3.0</b> | Diciembre 2025<br>
  <i>"Porque todos merecemos un poco de paz y tranquilidad"</i>
</p>
