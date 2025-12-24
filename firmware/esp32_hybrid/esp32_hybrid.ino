/**
 * ESP32 Hybrid Jammer - Volume Be Gone v3.0
 *
 * Firmware para ESP32 que integra:
 * - Dual nRF24L01+PA+LNA (HSPI + VSPI)
 * - Comunicación serial con Raspberry Pi
 * - 4 modos de jamming (BT/BLE/WiFi/Full)
 * - 4 patrones de transmisión (Continuous/Pulse/Sweep/Burst)
 *
 * Basado en: ESP32-BlueJammer y Bluetooth-jammer-esp32
 * Autor: Francisco Ortiz Rojas
 * Licencia: MIT (Solo para uso educativo)
 */

#include <SPI.h>
#include <RF24.h>

// ═══════════════════════════════════════════════════════════════════════════
// CONFIGURACIÓN DE PINES - DUAL SPI
// ═══════════════════════════════════════════════════════════════════════════

// HSPI - nRF24L01 Módulo #1 (Canales 0-62)
#define HSPI_SCK   14
#define HSPI_MISO  12
#define HSPI_MOSI  13
#define NRF1_CE    16
#define NRF1_CSN   15

// VSPI - nRF24L01 Módulo #2 (Canales 63-124)
#define VSPI_SCK   18
#define VSPI_MISO  19
#define VSPI_MOSI  23
#define NRF2_CE    22
#define NRF2_CSN   21

// LED de estado
#define LED_STATUS 2   // LED interno ESP32
#define LED_EXT    27  // LED externo (opcional)

// ═══════════════════════════════════════════════════════════════════════════
// CONFIGURACIÓN DE JAMMING
// ═══════════════════════════════════════════════════════════════════════════

// Modos de frecuencia
enum JamMode {
  MODE_IDLE = 0,
  MODE_BT   = 1,    // Bluetooth Classic (79 canales)
  MODE_BLE  = 2,    // Bluetooth Low Energy (40 canales)
  MODE_WIFI = 3,    // WiFi 2.4GHz (14 canales)
  MODE_FULL = 4     // Full spectrum (125 canales)
};

// Patrones de transmisión
enum TxPattern {
  PATTERN_CONT  = 0,  // Continuo
  PATTERN_PULSE = 1,  // Pulsos 50ms on/off
  PATTERN_SWEEP = 2,  // Barrido de frecuencia
  PATTERN_BURST = 3   // Ráfagas aleatorias
};

// Niveles de potencia
enum PowerLevel {
  POWER_MIN  = RF24_PA_MIN,
  POWER_LOW  = RF24_PA_LOW,
  POWER_HIGH = RF24_PA_HIGH,
  POWER_MAX  = RF24_PA_MAX
};

// ═══════════════════════════════════════════════════════════════════════════
// RANGOS DE CANALES POR MODO
// ═══════════════════════════════════════════════════════════════════════════

// Bluetooth Classic: 79 canales (2402-2480 MHz)
const uint8_t BT_CH_START = 2;
const uint8_t BT_CH_END = 80;

// BLE: 40 canales (advertising en 37, 38, 39)
const uint8_t BLE_ADV_CHANNELS[] = {37, 38, 39};  // 2402, 2426, 2480 MHz
const uint8_t BLE_CH_START = 0;
const uint8_t BLE_CH_END = 39;

// WiFi: Canales 1, 6, 11 (principales)
const uint8_t WIFI_CHANNELS[] = {1, 6, 11, 14};
const uint8_t WIFI_CH_START = 0;
const uint8_t WIFI_CH_END = 14;

// Full: Todos los canales nRF24
const uint8_t FULL_CH_START = 0;
const uint8_t FULL_CH_END = 124;

// ═══════════════════════════════════════════════════════════════════════════
// VARIABLES GLOBALES
// ═══════════════════════════════════════════════════════════════════════════

// Instancias SPI
SPIClass *hspi = NULL;
SPIClass *vspi = NULL;

// Instancias RF24
RF24 radio1(NRF1_CE, NRF1_CSN);  // HSPI
RF24 radio2(NRF2_CE, NRF2_CSN);  // VSPI

// Estado del sistema
volatile bool jamming = false;
volatile JamMode currentMode = MODE_IDLE;
volatile TxPattern currentPattern = PATTERN_CONT;
volatile PowerLevel currentPower = POWER_MAX;

// Buffer de datos para transmisión (ruido)
uint8_t noiseData[32];

// Canales específicos (para modo targeted)
uint8_t targetChannels[10];
uint8_t numTargetChannels = 0;

// Control de tiempo
unsigned long lastStatusTime = 0;
unsigned long startTime = 0;

// Buffer serial
String serialBuffer = "";

// ═══════════════════════════════════════════════════════════════════════════
// TASK HANDLES (Dual Core)
// ═══════════════════════════════════════════════════════════════════════════

TaskHandle_t Task1;  // Core 0: Serial + Control
TaskHandle_t Task2;  // Core 1: RF Jamming

// ═══════════════════════════════════════════════════════════════════════════
// SETUP
// ═══════════════════════════════════════════════════════════════════════════

void setup() {
  // Inicializar serial
  Serial.begin(115200);
  while (!Serial) delay(10);

  Serial.println("ESP32 Hybrid Jammer v3.0");
  Serial.println("Initializing...");

  // Configurar LEDs
  pinMode(LED_STATUS, OUTPUT);
  pinMode(LED_EXT, OUTPUT);
  digitalWrite(LED_STATUS, LOW);
  digitalWrite(LED_EXT, LOW);

  // Inicializar buses SPI
  hspi = new SPIClass(HSPI);
  vspi = new SPIClass(VSPI);

  hspi->begin(HSPI_SCK, HSPI_MISO, HSPI_MOSI, NRF1_CSN);
  vspi->begin(VSPI_SCK, VSPI_MISO, VSPI_MOSI, NRF2_CSN);

  // Inicializar módulos nRF24L01
  bool nrf1_ok = initRadio(radio1, hspi, "NRF1");
  bool nrf2_ok = initRadio(radio2, vspi, "NRF2");

  if (!nrf1_ok || !nrf2_ok) {
    Serial.println("ERROR: nRF24 initialization failed!");
    blinkError();
  }

  // Generar datos de ruido aleatorio
  generateNoise();

  // Crear tareas en ambos cores
  xTaskCreatePinnedToCore(
    serialTask,     // Función
    "SerialTask",   // Nombre
    10000,          // Stack size
    NULL,           // Parámetros
    1,              // Prioridad
    &Task1,         // Handle
    0               // Core 0
  );

  xTaskCreatePinnedToCore(
    jammingTask,    // Función
    "JammingTask",  // Nombre
    10000,          // Stack size
    NULL,           // Parámetros
    1,              // Prioridad
    &Task2,         // Handle
    1               // Core 1
  );

  Serial.println("OK:READY");
  startTime = millis();
}

void loop() {
  // Loop principal vacío - todo corre en tareas
  vTaskDelay(1000 / portTICK_PERIOD_MS);
}

// ═══════════════════════════════════════════════════════════════════════════
// INICIALIZACIÓN DE RADIO
// ═══════════════════════════════════════════════════════════════════════════

bool initRadio(RF24 &radio, SPIClass *spi, const char* name) {
  Serial.print("Initializing ");
  Serial.print(name);
  Serial.print("... ");

  if (!radio.begin(spi)) {
    Serial.println("FAIL");
    return false;
  }

  // Configuración para jamming
  radio.setAutoAck(false);           // Sin ACK
  radio.setPALevel(RF24_PA_MAX);     // Potencia máxima
  radio.setDataRate(RF24_2MBPS);     // Velocidad máxima
  radio.setCRCLength(RF24_CRC_DISABLED);  // Sin CRC
  radio.setPayloadSize(32);          // Payload máximo
  radio.stopListening();             // Modo TX

  Serial.println("OK");
  return true;
}

// ═══════════════════════════════════════════════════════════════════════════
// GENERADOR DE RUIDO
// ═══════════════════════════════════════════════════════════════════════════

void generateNoise() {
  for (int i = 0; i < 32; i++) {
    noiseData[i] = random(256);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// TAREA SERIAL (Core 0)
// ═══════════════════════════════════════════════════════════════════════════

void serialTask(void *parameter) {
  for (;;) {
    // Leer comandos serial
    while (Serial.available()) {
      char c = Serial.read();
      if (c == '\n' || c == '\r') {
        if (serialBuffer.length() > 0) {
          processCommand(serialBuffer);
          serialBuffer = "";
        }
      } else {
        serialBuffer += c;
      }
    }

    // Parpadeo LED según estado
    if (jamming) {
      digitalWrite(LED_STATUS, (millis() / 100) % 2);
    } else {
      digitalWrite(LED_STATUS, LOW);
    }

    vTaskDelay(10 / portTICK_PERIOD_MS);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// PROCESADOR DE COMANDOS
// ═══════════════════════════════════════════════════════════════════════════

void processCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();

  // Comandos básicos
  if (cmd == "PING") {
    Serial.println("PONG");
  }
  else if (cmd == "STATUS") {
    sendStatus();
  }
  else if (cmd == "VERSION") {
    Serial.println("VERSION:3.0");
  }

  // Control de jamming
  else if (cmd == "JAM_START") {
    jamming = true;
    Serial.println("OK:JAM_STARTED");
  }
  else if (cmd == "JAM_STOP") {
    jamming = false;
    currentMode = MODE_IDLE;
    Serial.println("OK:JAM_STOPPED");
  }
  else if (cmd == "JAM_BT") {
    currentMode = MODE_BT;
    jamming = true;
    Serial.println("OK:MODE_BT");
  }
  else if (cmd == "JAM_BLE") {
    currentMode = MODE_BLE;
    jamming = true;
    Serial.println("OK:MODE_BLE");
  }
  else if (cmd == "JAM_WIFI") {
    currentMode = MODE_WIFI;
    jamming = true;
    Serial.println("OK:MODE_WIFI");
  }
  else if (cmd == "JAM_FULL") {
    currentMode = MODE_FULL;
    jamming = true;
    Serial.println("OK:MODE_FULL");
  }

  // Patrones de transmisión
  else if (cmd == "MODE:CONT") {
    currentPattern = PATTERN_CONT;
    Serial.println("OK:MODE_CONT");
  }
  else if (cmd == "MODE:PULSE") {
    currentPattern = PATTERN_PULSE;
    Serial.println("OK:MODE_PULSE");
  }
  else if (cmd == "MODE:SWEEP") {
    currentPattern = PATTERN_SWEEP;
    Serial.println("OK:MODE_SWEEP");
  }
  else if (cmd == "MODE:BURST") {
    currentPattern = PATTERN_BURST;
    Serial.println("OK:MODE_BURST");
  }

  // Control de potencia
  else if (cmd == "POWER:MAX") {
    currentPower = POWER_MAX;
    radio1.setPALevel(RF24_PA_MAX);
    radio2.setPALevel(RF24_PA_MAX);
    Serial.println("OK:POWER_MAX");
  }
  else if (cmd == "POWER:HIGH") {
    currentPower = POWER_HIGH;
    radio1.setPALevel(RF24_PA_HIGH);
    radio2.setPALevel(RF24_PA_HIGH);
    Serial.println("OK:POWER_HIGH");
  }
  else if (cmd == "POWER:MED") {
    currentPower = POWER_LOW;  // RF24 no tiene MED, usamos LOW
    radio1.setPALevel(RF24_PA_LOW);
    radio2.setPALevel(RF24_PA_LOW);
    Serial.println("OK:POWER_MED");
  }
  else if (cmd == "POWER:LOW") {
    currentPower = POWER_MIN;
    radio1.setPALevel(RF24_PA_MIN);
    radio2.setPALevel(RF24_PA_MIN);
    Serial.println("OK:POWER_LOW");
  }

  // Canales específicos
  else if (cmd.startsWith("CH:")) {
    parseChannels(cmd.substring(3));
    Serial.println("OK:CH_SET");
  }

  // Comando no reconocido
  else {
    Serial.println("ERROR:UNKNOWN_CMD");
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// ENVIAR ESTADO
// ═══════════════════════════════════════════════════════════════════════════

void sendStatus() {
  String status = "STATUS:";

  if (!jamming) {
    status += "IDLE";
  } else {
    status += "JAMMING:";
    switch (currentMode) {
      case MODE_BT:   status += "BT"; break;
      case MODE_BLE:  status += "BLE"; break;
      case MODE_WIFI: status += "WIFI"; break;
      case MODE_FULL: status += "FULL"; break;
      default:        status += "UNKNOWN"; break;
    }
  }

  Serial.println(status);
}

// ═══════════════════════════════════════════════════════════════════════════
// PARSER DE CANALES
// ═══════════════════════════════════════════════════════════════════════════

void parseChannels(String chStr) {
  numTargetChannels = 0;
  int idx = 0;

  while (chStr.length() > 0 && numTargetChannels < 10) {
    int commaIdx = chStr.indexOf(',');
    String chNum;

    if (commaIdx == -1) {
      chNum = chStr;
      chStr = "";
    } else {
      chNum = chStr.substring(0, commaIdx);
      chStr = chStr.substring(commaIdx + 1);
    }

    int ch = chNum.toInt();
    if (ch >= 0 && ch <= 124) {
      targetChannels[numTargetChannels++] = ch;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// TAREA DE JAMMING (Core 1)
// ═══════════════════════════════════════════════════════════════════════════

void jammingTask(void *parameter) {
  uint8_t ch1 = 0;
  uint8_t ch2 = 63;
  unsigned long pulseTimer = 0;
  bool pulseState = true;

  for (;;) {
    if (!jamming) {
      vTaskDelay(10 / portTICK_PERIOD_MS);
      continue;
    }

    // Obtener rangos según modo
    uint8_t start1, end1, start2, end2;
    getChannelRanges(start1, end1, start2, end2);

    // Aplicar patrón de transmisión
    switch (currentPattern) {
      case PATTERN_CONT:
        // Transmisión continua
        transmitNoise(ch1, ch2);
        break;

      case PATTERN_PULSE:
        // Pulsos 50ms on/off
        if (millis() - pulseTimer > 50) {
          pulseTimer = millis();
          pulseState = !pulseState;
        }
        if (pulseState) {
          transmitNoise(ch1, ch2);
        }
        break;

      case PATTERN_SWEEP:
        // Barrido de frecuencia
        transmitNoise(ch1, ch2);
        ch1++;
        ch2++;
        if (ch1 > end1) ch1 = start1;
        if (ch2 > end2) ch2 = start2;
        delayMicroseconds(100);  // Más lento para barrido
        break;

      case PATTERN_BURST:
        // Ráfagas aleatorias
        if (random(100) < 70) {  // 70% probabilidad
          ch1 = random(start1, end1 + 1);
          ch2 = random(start2, end2 + 1);
          transmitNoise(ch1, ch2);
        }
        break;
    }

    // Channel hopping (excepto en sweep)
    if (currentPattern != PATTERN_SWEEP) {
      ch1 = random(start1, end1 + 1);
      ch2 = random(start2, end2 + 1);
    }

    // Regenerar ruido periódicamente
    if (random(1000) < 10) {
      generateNoise();
    }

    // Pequeño delay para no saturar CPU
    delayMicroseconds(50);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// OBTENER RANGOS DE CANALES
// ═══════════════════════════════════════════════════════════════════════════

void getChannelRanges(uint8_t &s1, uint8_t &e1, uint8_t &s2, uint8_t &e2) {
  switch (currentMode) {
    case MODE_BT:
      s1 = BT_CH_START;
      e1 = 40;
      s2 = 41;
      e2 = BT_CH_END;
      break;

    case MODE_BLE:
      s1 = BLE_CH_START;
      e1 = 20;
      s2 = 21;
      e2 = BLE_CH_END;
      break;

    case MODE_WIFI:
      s1 = WIFI_CH_START;
      e1 = 7;
      s2 = 8;
      e2 = WIFI_CH_END;
      break;

    case MODE_FULL:
    default:
      s1 = FULL_CH_START;
      e1 = 62;
      s2 = 63;
      e2 = FULL_CH_END;
      break;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// TRANSMITIR RUIDO
// ═══════════════════════════════════════════════════════════════════════════

void transmitNoise(uint8_t ch1, uint8_t ch2) {
  // Módulo 1
  radio1.setChannel(ch1);
  radio1.writeFast(noiseData, 32, false);

  // Módulo 2
  radio2.setChannel(ch2);
  radio2.writeFast(noiseData, 32, false);
}

// ═══════════════════════════════════════════════════════════════════════════
// INDICADOR DE ERROR
// ═══════════════════════════════════════════════════════════════════════════

void blinkError() {
  for (int i = 0; i < 10; i++) {
    digitalWrite(LED_STATUS, HIGH);
    delay(100);
    digitalWrite(LED_STATUS, LOW);
    delay(100);
  }
}
