# Volume Be Gone

## Tu Aliado Contra el Ruido Excesivo

---

### El Problema

Todos hemos estado ahí: es un día tranquilo, estás disfrutando de tu tiempo libre, y de repente... **BOOM** - tu vecino decide que todo el barrio necesita escuchar su música a todo volumen.

Los parlantes Bluetooth portátiles son geniales, pero cuando alguien abusa de ellos, pueden convertirse en una verdadera molestia.

---

### La Solución

**Volume Be Gone** es un dispositivo inteligente que:

1. **Escucha** el nivel de ruido ambiental
2. **Detecta** cuando el volumen supera un límite que tú configuras
3. **Actúa** automáticamente para silenciar parlantes Bluetooth cercanos

Es como tener un "control remoto universal" para los parlantes molestos de tu entorno.

---

### ¿Cómo Funciona? (Versión Simple)

```
    TU DISPOSITIVO                    PARLANTE MOLESTO
    ┌──────────────┐                  ┌──────────────┐
    │              │                  │   ♪♫♪♫♪♫    │
    │  Raspberry   │  ~~~~ señal ~~~> │              │
    │     Pi       │                  │   Bluetooth  │
    │              │                  │              │
    └──────────────┘                  └──────────────┘
          │                                  │
          │                                  │
          ▼                                  ▼
    "Detecté ruido                    "Perdí conexión,
     muy alto..."                      me desconecto"
```

**En palabras simples:**
- Tu dispositivo "habla" con el parlante usando el mismo idioma (Bluetooth)
- Le envía muchas solicitudes de conexión a la vez
- El parlante se confunde y pierde su conexión actual
- Resultado: silencio

---

### ¿Qué Necesitas?

#### Versión Básica (Solo Raspberry Pi)
- 1 Raspberry Pi (3B+ o 4)
- 1 Micrófono USB
- 1 Pantallita OLED (opcional pero recomendada)
- 1 Perilla/Encoder (para ajustar el volumen límite)

#### Versión Avanzada (Con ESP32)
Todo lo anterior, más:
- 1 ESP32 (microcontrolador pequeño)
- 2 Módulos de radio nRF24L01
- Mayor alcance y efectividad

---

### Formas de Usarlo

#### Opción 1: Con Pantallita y Perilla
La forma clásica. Ves el nivel de volumen en la pantalla y ajustas el límite girando la perilla.

```
  ┌─────────────────────┐
  │  VOLUME BE GONE     │
  │  ▓▓▓▓▓▓▓░░░  73 dB  │
  │  Umbral: 75 dB      │
  │  Dispositivos: 3    │
  └─────────────────────┘
```

#### Opción 2: Desde tu Celular
Conectas tu celular a la red WiFi del dispositivo y lo controlas desde el navegador.

```
  Tu Celular                    Volume Be Gone
  ┌─────────┐                   ┌─────────┐
  │         │    WiFi           │         │
  │ 📱      │ <──────────────>  │   🔊❌   │
  │         │                   │         │
  └─────────┘                   └─────────┘
```

**Para conectar:**
1. Busca la red WiFi "VolumeBeGone" en tu celular
2. Contraseña: `begone2025`
3. Abre el navegador y ve a: `192.168.4.1:5000`

---

### Niveles de Ruido - ¿Qué Significan?

| Nivel (dB) | Ejemplo | ¿Es Molesto? |
|------------|---------|--------------|
| 30-40 | Biblioteca silenciosa | No |
| 50-60 | Conversación normal | No |
| 65-70 | Tráfico de ciudad | Algo |
| 75-85 | Parlante a volumen alto | Sí |
| 85-95 | Concierto / Fiesta | Muy molesto |
| 100+ | Daño auditivo | Peligroso |

**Recomendación:** Configura el umbral entre **70-80 dB** para un balance entre tolerancia y tranquilidad.

---

### Preguntas Frecuentes

#### ¿Es legal?
Este proyecto es **solo para fines educativos**. Úsalo únicamente con tus propios dispositivos o con permiso explícito. El uso indebido puede ser ilegal en tu país.

#### ¿Funciona con todos los parlantes?
Funciona con la mayoría de parlantes Bluetooth. Algunos dispositivos más modernos pueden ser más resistentes.

#### ¿A qué distancia funciona?
- **Versión básica:** Hasta 10-15 metros
- **Con adaptador Clase 1:** Hasta 50 metros
- **Con ESP32 + antenas:** Hasta 100+ metros

#### ¿Afecta otros dispositivos?
El sistema intenta detectar y atacar solo parlantes de audio. Otros dispositivos Bluetooth (teclados, mouse, auriculares personales) generalmente no se ven afectados.

#### ¿Cuánto cuesta armarlo?
- **Versión básica:** ~$50-70 USD
- **Versión completa con ESP32:** ~$80-120 USD

---

### Antes de Empezar

1. **Lee la guía de usuario** - Tiene instrucciones paso a paso
2. **Ten paciencia** - La primera instalación puede tomar 1-2 horas
3. **Pide ayuda si la necesitas** - Hay una comunidad dispuesta a ayudar

---

### Créditos

**Desarrollado por:** Francisco Ortiz Rojas
**Inspirado en:** "Reggaeton Be Gone" de Roni Bandini

---

*"Porque todos merecemos un poco de paz y tranquilidad"*
