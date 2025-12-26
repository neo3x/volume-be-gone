#!/usr/bin/env python3
"""
MasterBeGone v3.0 - Orquestador Principal

Sistema de control centralizado para Volume Be Gone.
Coordina todos los módulos: Audio, Bluetooth, Display, Ataques, ESP32 y Web.

Author: Francisco Ortiz Rojas
Version: 3.0
"""

import sys
import signal
import time
import threading
import argparse
import logging
from pathlib import Path

# Agregar directorio de módulos al path
sys.path.insert(0, str(Path(__file__).parent))

from modules import (
    Config,
    AudioMonitor,
    BluetoothScanner,
    DisplayManager,
    AttackEngine,
    ESP32Controller,
    WebServer
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('MasterBeGone')


class MasterBeGone:
    """
    Orquestador principal del sistema Volume Be Gone.

    Coordina la inicialización, operación y shutdown de todos los módulos.
    """

    VERSION = "3.0"

    def __init__(self, headless: bool = False, no_esp32: bool = False,
                 web_only: bool = False, debug: bool = False):
        """
        Inicializar el orquestador.

        Args:
            headless: Ejecutar sin display OLED
            no_esp32: Deshabilitar comunicación con ESP32
            web_only: Solo servidor web (sin OLED/encoder)
            debug: Activar modo debug
        """
        self.headless = headless or web_only
        self.no_esp32 = no_esp32
        self.web_only = web_only
        self.debug = debug

        if debug:
            logging.getLogger().setLevel(logging.DEBUG)

        # Estado del sistema
        self.running = False
        self.attacking = False
        self.current_target = None

        # Módulos (se inicializan en start())
        self.config: Config = None
        self.audio: AudioMonitor = None
        self.bluetooth: BluetoothScanner = None
        self.display: DisplayManager = None
        self.attack_engine: AttackEngine = None
        self.esp32: ESP32Controller = None
        self.web_server: WebServer = None

        # Thread principal
        self.main_thread = None

        # Configurar signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info(f"MasterBeGone v{self.VERSION} inicializado")

    def _signal_handler(self, signum, frame):
        """Manejar señales de terminación."""
        logger.info(f"Señal {signum} recibida, deteniendo...")
        self.stop()

    def _update_boot_progress(self, step: int, total: int, message: str):
        """Actualizar progreso de arranque en display."""
        if self.display:
            progress = int((step / total) * 100)
            self.display.show_boot_screen(message, progress)
        logger.info(f"[{step}/{total}] {message}")

    def start(self):
        """Iniciar todos los módulos y el sistema."""
        logger.info("=" * 50)
        logger.info(f"  Volume Be Gone v{self.VERSION}")
        logger.info("  Iniciando sistema...")
        logger.info("=" * 50)

        self.running = True
        total_steps = 8
        current_step = 0

        try:
            # Paso 1: Cargar configuración
            current_step += 1
            self._update_boot_progress(current_step, total_steps, "Cargando config...")
            self.config = Config()
            time.sleep(0.3)

            # Paso 2: Inicializar Display (si no es headless)
            current_step += 1
            if not self.headless:
                self._update_boot_progress(current_step, total_steps, "Init Display...")
                try:
                    self.display = DisplayManager(self.config)
                    self.display.start()
                    # Mostrar progreso en OLED
                    self.display.show_boot_screen("Init Display...",
                                                   int((current_step/total_steps)*100))
                except Exception as e:
                    logger.warning(f"Display no disponible: {e}")
                    self.display = None
            else:
                logger.info("Modo headless - sin display")
            time.sleep(0.3)

            # Paso 3: Configurar GPIO/Encoder
            current_step += 1
            self._update_boot_progress(current_step, total_steps, "Setup GPIO...")
            if self.display:
                # Configurar callback del encoder
                self.display.on_threshold_change = self._on_threshold_change
                self.display.on_button_press = self._on_button_press
            time.sleep(0.3)

            # Paso 4: Inicializar Audio
            current_step += 1
            self._update_boot_progress(current_step, total_steps, "Init Audio...")
            try:
                self.audio = AudioMonitor(self.config)
                self.audio.on_threshold_exceeded = self._on_threshold_exceeded
                self.audio.start()
            except Exception as e:
                logger.error(f"Error iniciando audio: {e}")
                self.audio = None
            time.sleep(0.3)

            # Paso 5: Inicializar Bluetooth
            current_step += 1
            self._update_boot_progress(current_step, total_steps, "Init Bluetooth...")
            try:
                self.bluetooth = BluetoothScanner(self.config)
            except Exception as e:
                logger.error(f"Error iniciando Bluetooth: {e}")
                self.bluetooth = None
            time.sleep(0.3)

            # Paso 6: Inicializar ESP32 (si está habilitado)
            current_step += 1
            self._update_boot_progress(current_step, total_steps, "Init ESP32...")
            if not self.no_esp32:
                try:
                    self.esp32 = ESP32Controller()
                    if not self.esp32.connect():
                        logger.warning("ESP32 no conectado")
                except Exception as e:
                    logger.warning(f"ESP32 no disponible: {e}")
                    self.esp32 = None
            else:
                logger.info("ESP32 deshabilitado por parámetro")
            time.sleep(0.3)

            # Paso 7: Inicializar Attack Engine
            current_step += 1
            self._update_boot_progress(current_step, total_steps, "Init Attack...")
            self.attack_engine = AttackEngine(self.config, self.esp32)
            time.sleep(0.3)

            # Paso 8: Inicializar Web Server
            current_step += 1
            self._update_boot_progress(current_step, total_steps, "Init Web...")
            try:
                self.web_server = WebServer(self.config)
                self._setup_web_callbacks()
                # Iniciar servidor web en thread separado
                self.web_server.start()
            except Exception as e:
                logger.error(f"Error iniciando servidor web: {e}")
                self.web_server = None
            time.sleep(0.3)

            # Sistema listo
            self._update_boot_progress(total_steps, total_steps, "Sistema Listo!")
            time.sleep(1)

            logger.info("=" * 50)
            logger.info("  Sistema iniciado correctamente")
            logger.info(f"  Web UI: http://{self._get_ip()}:5000")
            logger.info("=" * 50)

            # Mostrar pantalla principal
            if self.display:
                self.display.show_main_screen(
                    volume_db=0,
                    threshold=self.config.audio.threshold,
                    device_count=0,
                    attacking=False
                )

            # Iniciar loop principal
            self._main_loop()

        except Exception as e:
            logger.error(f"Error fatal durante inicio: {e}")
            self.stop()
            raise

    def _setup_web_callbacks(self):
        """Configurar callbacks para el servidor web."""
        if not self.web_server:
            return

        # Callback para escaneo
        def on_scan_request():
            if self.bluetooth:
                devices = self.bluetooth.scan_full(duration=10)
                return devices
            return []

        # Callback para cambio de umbral
        def on_threshold_change(value):
            self.config.audio.threshold = value
            self.config.save()
            if self.display:
                self.display.update_threshold(value)

        # Callback para ataque
        def on_attack_request(addr):
            if self.attack_engine:
                device = self.config.get_device(addr)
                if device:
                    self.attack_engine.attack_device(device)
                    return True
            return False

        # Callback para iniciar ataque continuo
        def on_start_continuous():
            self.attacking = True
            if self.attack_engine:
                self.attack_engine.start_continuous_attack()

        # Callback para detener ataque
        def on_stop_attack():
            self.attacking = False
            if self.attack_engine:
                self.attack_engine.stop_attack()

        # Callback para estado ESP32
        def get_esp32_status():
            if self.esp32:
                return {
                    'connected': self.esp32.connected,
                    'jamming': self.esp32.jamming
                }
            return {'connected': False, 'jamming': False}

        # Callback para comando jam ESP32
        def on_jam_command(action, mode=None):
            if self.esp32 and self.esp32.connected:
                if action == 'start' and mode:
                    from modules.esp32_controller import JamMode
                    mode_map = {'BT': JamMode.BT, 'BLE': JamMode.BLE,
                               'WIFI': JamMode.WIFI, 'FULL': JamMode.FULL}
                    if mode in mode_map:
                        self.esp32.start_jam(mode_map[mode])
                        return True
                elif action == 'stop':
                    self.esp32.stop_jam()
                    return True
            return False

        # Registrar callbacks
        self.web_server.on_scan = on_scan_request
        self.web_server.on_threshold_change = on_threshold_change
        self.web_server.on_attack = on_attack_request
        self.web_server.on_start_continuous = on_start_continuous
        self.web_server.on_stop_attack = on_stop_attack
        self.web_server.get_esp32_status = get_esp32_status
        self.web_server.on_jam_command = on_jam_command

    def _main_loop(self):
        """Loop principal del sistema."""
        logger.info("Iniciando loop principal...")

        scan_interval = 30  # segundos entre escaneos
        last_scan = 0

        while self.running:
            try:
                current_time = time.time()

                # Actualizar nivel de audio
                if self.audio:
                    volume_db = self.audio.current_level
                    exceeded = volume_db > self.config.audio.threshold

                    # Actualizar display
                    if self.display:
                        self.display.show_main_screen(
                            volume_db=volume_db,
                            threshold=self.config.audio.threshold,
                            device_count=len(self.config.get_all_devices()),
                            attacking=self.attacking
                        )

                    # Enviar a web
                    if self.web_server:
                        self.web_server.emit_volume(volume_db, exceeded)

                # Escaneo automático periódico
                if current_time - last_scan >= scan_interval:
                    if self.bluetooth and not self.attacking:
                        logger.debug("Escaneo automático...")
                        threading.Thread(
                            target=self._background_scan,
                            daemon=True
                        ).start()
                    last_scan = current_time

                # Pequeña pausa para no saturar CPU
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error en loop principal: {e}")
                time.sleep(1)

    def _background_scan(self):
        """Realizar escaneo en background."""
        try:
            devices = self.bluetooth.quick_scan()
            if devices and self.web_server:
                self.web_server.emit_devices(devices)
        except Exception as e:
            logger.error(f"Error en escaneo background: {e}")

    def _on_threshold_exceeded(self, level: float):
        """Callback cuando el umbral es superado."""
        logger.warning(f"UMBRAL SUPERADO: {level:.1f} dB")

        if self.config.attack.auto_attack and not self.attacking:
            # Buscar dispositivo de audio más cercano y atacar
            audio_devices = [d for d in self.config.get_all_devices()
                           if d.get('is_audio')]

            if audio_devices:
                target = audio_devices[0]
                logger.info(f"Auto-ataque a: {target.get('name', target['addr'])}")
                self.attacking = True

                if self.attack_engine:
                    threading.Thread(
                        target=self._auto_attack,
                        args=(target,),
                        daemon=True
                    ).start()

    def _auto_attack(self, target: dict):
        """Ejecutar ataque automático."""
        try:
            self.attack_engine.attack_device(target)
        finally:
            self.attacking = False

    def _on_threshold_change(self, value: int):
        """Callback cuando cambia el umbral desde encoder."""
        logger.info(f"Umbral cambiado: {value} dB")
        self.config.audio.threshold = value
        if self.web_server:
            self.web_server.emit_threshold(value)

    def _on_button_press(self):
        """Callback cuando se presiona el botón del encoder."""
        logger.info("Botón presionado")
        # Guardar configuración
        self.config.save()
        if self.display:
            self.display.show_message("Config guardada", duration=1)

    def _get_ip(self) -> str:
        """Obtener IP local."""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "192.168.4.1"  # IP por defecto en modo AP

    def stop(self):
        """Detener todos los módulos y el sistema."""
        logger.info("Deteniendo sistema...")
        self.running = False

        # Detener ataques
        if self.attack_engine:
            self.attack_engine.stop_attack()

        # Detener ESP32
        if self.esp32:
            self.esp32.stop_jam()
            self.esp32.disconnect()

        # Detener audio
        if self.audio:
            self.audio.stop()

        # Detener display
        if self.display:
            self.display.show_message("Apagando...", duration=1)
            self.display.stop()

        # Detener web server
        if self.web_server:
            self.web_server.stop()

        # Guardar configuración
        if self.config:
            self.config.save()

        logger.info("Sistema detenido correctamente")


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description='MasterBeGone v3.0 - Control de Parlantes Bluetooth',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos:
  python masterbegone.py              # Modo normal (OLED + Web)
  python masterbegone.py --web-only   # Solo servidor web
  python masterbegone.py --headless   # Sin display OLED
  python masterbegone.py --no-esp32   # Sin ESP32
  python masterbegone.py --debug      # Modo debug
        '''
    )

    parser.add_argument('--headless', action='store_true',
                        help='Ejecutar sin display OLED')
    parser.add_argument('--no-esp32', action='store_true',
                        help='Deshabilitar comunicación con ESP32')
    parser.add_argument('--web-only', action='store_true',
                        help='Solo servidor web (sin OLED/encoder)')
    parser.add_argument('--debug', action='store_true',
                        help='Activar modo debug')
    parser.add_argument('--version', action='version',
                        version=f'MasterBeGone v{MasterBeGone.VERSION}')

    args = parser.parse_args()

    # Crear y ejecutar orquestador
    master = MasterBeGone(
        headless=args.headless,
        no_esp32=args.no_esp32,
        web_only=args.web_only,
        debug=args.debug
    )

    try:
        master.start()
    except KeyboardInterrupt:
        logger.info("Interrupción de teclado")
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)
    finally:
        master.stop()


if __name__ == '__main__':
    main()
