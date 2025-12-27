# Documentación - Volume Be Gone v3.0

## Índice de Documentos

---

## Para Usuarios

Documentación pensada para usuarios finales, con explicaciones simples y paso a paso.

| Documento | Descripción |
|-----------|-------------|
| [¿Qué es Volume Be Gone?](usuario/QUE_ES_VOLUME_BE_GONE.md) | Explicación simple del proyecto |
| [Inicio Rápido](usuario/INICIO_RAPIDO.md) | Empezar en 5 minutos |
| [Manual de Usuario](usuario/MANUAL_USUARIO.md) | Guía completa paso a paso |

---

## Instalación y Configuración

| Documento | Descripción |
|-----------|-------------|
| [Instalación](INSTALACION.md) | Guía de instalación detallada |
| [Guía de Autostart](GUIA_AUTOSTART.md) | Configurar inicio automático |
| [Instalación (Inglés)](INSTALL.md) | Installation guide |
| [Solución de Problemas](TROUBLESHOOTING.md) | Errores comunes y soluciones |

---

## Documentación Técnica

Para desarrolladores y usuarios avanzados.

| Documento | Descripción |
|-----------|-------------|
| [Arquitectura Híbrida](tecnico/ARQUITECTURA_HIBRIDA.md) | Diseño del sistema RPi + ESP32 |
| [Propuesta Híbrida Completa](tecnico/PROPUESTA_HIBRIDA_COMPLETA.md) | Especificaciones detalladas |
| [Análisis Técnico](tecnico/ANALISIS_TECNICO.md) | Análisis del sistema |
| [Ataque Secuencial](tecnico/ATAQUE_SECUENCIAL.md) | Lógica de ataques |
| [Filtrado de Audio](tecnico/FILTRADO_AUDIO.md) | Sistema de detección |
| [Comparación Jammers ESP32](tecnico/COMPARACION_JAMMERS_ESP32.md) | Análisis de repositorios |
| [RF Jamming Research](tecnico/RF_JAMMING_RESEARCH.md) | Investigación de RF |
| [Mejoras Implementadas](tecnico/MEJORAS_IMPLEMENTADAS.md) | Historial de mejoras |
| [Errores Corregidos](tecnico/ERRORES_CORREGIDOS.md) | Bugs resueltos |

---

## Hardware

Diagramas de conexiones y esquemáticos.

| Documento | Descripción |
|-----------|-------------|
| [README Hardware](hardware/README.md) | Índice de hardware |
| [Conexiones ESP32](hardware/ESP32_WIRING.md) | Cableado del ESP32 |
| [Conexiones nRF24L01](hardware/NRF24L01_WIRING.md) | Cableado de módulos RF |
| [Análisis GPIO](hardware/GPIO_COMPATIBILITY_ANALYSIS.md) | Compatibilidad de pines |

---

## Organización de Carpetas

```
docs/
├── README.md              # Este archivo
├── INSTALACION.md         # Guía de instalación
├── GUIA_AUTOSTART.md      # Inicio automático
├── INSTALL.md             # Installation (English)
├── TROUBLESHOOTING.md     # Solución de problemas
├── usuario/               # Documentación para usuarios
│   ├── QUE_ES_VOLUME_BE_GONE.md
│   ├── INICIO_RAPIDO.md
│   └── MANUAL_USUARIO.md
├── tecnico/               # Documentación técnica
│   ├── ARQUITECTURA_HIBRIDA.md
│   ├── PROPUESTA_HIBRIDA_COMPLETA.md
│   └── ...
└── hardware/              # Diagramas de hardware
    ├── ESP32_WIRING.md
    ├── NRF24L01_WIRING.md
    └── ...
```

---

*Volume Be Gone v3.0 - Diciembre 2025*
