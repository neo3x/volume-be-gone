# Changelog

All notable changes to Volume Be Gone will be documented in this file.

The format is based on Keep a Changelog,
and this project adheres to Semantic Versioning.

**Author:** Francisco Ortiz Rojas - Ingeniero Electronico
**Contact:** francisco.ortiz@marfinex.com

## [Unreleased]

## [2.1.0] - 2025-12-15

### Added
- Compatibilidad completa con Debian Trixie (testing)
- Detección automática de usuario del sistema
- Configuración automática de I2C, SPI y GPIO persistente
- Reglas udev para permisos de hardware
- Soporte para PEP 668 (--break-system-packages)

### Fixed
- Errores de sintaxis en test_encoder.py
- Shebangs incorrectos en scripts de test
- Nombres de paquetes para Debian Trixie
- Referencias a archivos inexistentes en install.sh
- Usuario hardcodeado 'pi' ahora se detecta automáticamente

## [2.0.0] - 2025-10-01

### Added
- Encoder rotativo para control de umbral
- Pantalla OLED 128x64 con medidor visual
- Soporte para adaptador Bluetooth Clase 1
- Configuracion persistente en JSON
- Deteccion automatica de adaptadores BT
- Sistema de logging mejorado
- Tests de componentes

### Changed
- Interfaz completamente rediseñada
- Algoritmo de deteccion de volumen mejorado
- Estructura de proyecto reorganizada

### Fixed
- Problemas de memoria en escaneo continuo
- Compatibilidad con Raspberry Pi 4

## [1.0.0] - 2025-07-01

### Added
- Version inicial basada en Reggaeton Be Gone
- Deteccion por nivel de volumen
- Busqueda automatica de dispositivos
- Ataque a multiples parlantes 
