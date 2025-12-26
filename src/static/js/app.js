/**
 * Volume Be Gone v3.0 - Frontend JavaScript
 *
 * Comunicación WebSocket con el servidor para actualizaciones en tiempo real.
 */

// Estado de la aplicación
const state = {
    socket: null,
    connected: false,
    threshold: 73,
    devices: [],
    attacking: false,
    esp32Connected: false
};

// Elementos del DOM
const elements = {
    volumeValue: document.getElementById('volume-value'),
    volumeBar: document.getElementById('volume-bar'),
    thresholdMarker: document.getElementById('threshold-marker'),
    thresholdSlider: document.getElementById('threshold-slider'),
    thresholdValue: document.getElementById('threshold-value'),
    statusIndicator: document.getElementById('status-indicator'),
    statusText: document.querySelector('.status-text'),

    deviceList: document.getElementById('device-list'),
    statTotal: document.getElementById('stat-total'),
    statAudio: document.getElementById('stat-audio'),
    statBle: document.getElementById('stat-ble'),

    btnScan: document.getElementById('btn-scan'),
    btnAttackStart: document.getElementById('btn-attack-start'),
    btnAttackStop: document.getElementById('btn-attack-stop'),

    esp32Indicator: document.getElementById('esp32-indicator'),
    esp32Status: document.getElementById('esp32-status'),
    jamControls: document.getElementById('jam-controls'),

    attackSection: document.getElementById('attack-section'),
    attackTarget: document.getElementById('attack-target'),
    attackThreads: document.getElementById('attack-threads'),
    attackRf: document.getElementById('attack-rf')
};

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    initSocket();
    initEventListeners();
    updateThresholdMarker();
});

// Inicializar WebSocket
function initSocket() {
    state.socket = io();

    state.socket.on('connect', () => {
        console.log('Conectado al servidor');
        state.connected = true;
        updateConnectionStatus(true);
    });

    state.socket.on('disconnect', () => {
        console.log('Desconectado del servidor');
        state.connected = false;
        updateConnectionStatus(false);
    });

    // Recibir actualizaciones de volumen
    state.socket.on('volume', (data) => {
        updateVolumeMeter(data.level, data.exceeded);
    });

    // Recibir estado completo
    state.socket.on('status', (data) => {
        updateFullStatus(data);
    });

    // Recibir lista de dispositivos
    state.socket.on('devices', (data) => {
        updateDeviceList(data.devices);
    });

    // Nuevo dispositivo encontrado
    state.socket.on('device_found', (device) => {
        addDeviceToList(device);
    });
}

// Event listeners
function initEventListeners() {
    // Slider de umbral
    elements.thresholdSlider.addEventListener('input', (e) => {
        const value = parseInt(e.target.value);
        elements.thresholdValue.textContent = value;
        updateThresholdMarker();
    });

    elements.thresholdSlider.addEventListener('change', (e) => {
        const value = parseInt(e.target.value);
        state.threshold = value;
        state.socket.emit('set_threshold', { value });
    });

    // Botón escanear
    elements.btnScan.addEventListener('click', () => {
        startScan();
    });

    // Botón iniciar ataque
    elements.btnAttackStart.addEventListener('click', () => {
        startAttack();
    });

    // Botón detener ataque
    elements.btnAttackStop.addEventListener('click', () => {
        stopAttack();
    });

    // Controles ESP32
    document.getElementById('btn-jam-bt')?.addEventListener('click', () => {
        sendJamCommand('start', 'BT');
    });

    document.getElementById('btn-jam-ble')?.addEventListener('click', () => {
        sendJamCommand('start', 'BLE');
    });

    document.getElementById('btn-jam-stop')?.addEventListener('click', () => {
        sendJamCommand('stop');
    });
}

// Actualizar medidor de volumen
function updateVolumeMeter(level, exceeded) {
    const displayLevel = Math.max(0, Math.min(level, 120));
    const percentage = (displayLevel / 120) * 100;

    elements.volumeValue.textContent = displayLevel.toFixed(1);
    elements.volumeBar.style.width = percentage + '%';

    if (exceeded) {
        elements.volumeValue.classList.add('exceeded');
        elements.statusIndicator.classList.add('attacking');
        elements.statusText.textContent = '¡UMBRAL SUPERADO!';
    } else {
        elements.volumeValue.classList.remove('exceeded');
        elements.statusIndicator.classList.remove('attacking');
        elements.statusText.textContent = 'Monitoreando...';
    }
}

// Actualizar marcador de umbral
function updateThresholdMarker() {
    const value = parseInt(elements.thresholdSlider.value);
    const percentage = ((value - 0) / 120) * 100;
    elements.thresholdMarker.style.left = percentage + '%';
}

// Actualizar estado completo
function updateFullStatus(data) {
    // Audio
    if (data.audio) {
        updateVolumeMeter(data.audio.level, data.audio.level > data.audio.threshold);
        elements.thresholdSlider.value = data.audio.threshold;
        elements.thresholdValue.textContent = data.audio.threshold;
        state.threshold = data.audio.threshold;
        updateThresholdMarker();
    }

    // Bluetooth
    if (data.bluetooth) {
        elements.statTotal.textContent = data.bluetooth.total_devices || 0;
        elements.statAudio.textContent = data.bluetooth.audio_devices || 0;
        elements.statBle.textContent = data.bluetooth.ble_devices || 0;
    }

    // ESP32
    if (data.esp32) {
        updateESP32Status(data.esp32.connected, data.esp32.jamming);
    }

    // Ataque
    if (data.attack) {
        updateAttackStatus(data.attack);
    }
}

// Actualizar lista de dispositivos
function updateDeviceList(devices) {
    state.devices = devices;

    if (devices.length === 0) {
        elements.deviceList.innerHTML = `
            <div class="empty-state">
                <span>Sin dispositivos detectados</span>
                <small>Presiona Escanear para buscar</small>
            </div>
        `;
        return;
    }

    let html = '';
    devices.forEach(device => {
        html += createDeviceHTML(device);
    });

    elements.deviceList.innerHTML = html;

    // Agregar event listeners a los botones de ataque
    document.querySelectorAll('.btn-attack-device').forEach(btn => {
        btn.addEventListener('click', () => {
            attackDevice(btn.dataset.addr);
        });
    });

    // Actualizar estadísticas
    elements.statTotal.textContent = devices.length;
    elements.statAudio.textContent = devices.filter(d => d.is_audio).length;
    elements.statBle.textContent = devices.filter(d => d.is_ble).length;
}

// Crear HTML de dispositivo
function createDeviceHTML(device) {
    const name = device.name || 'Desconocido';
    const isAudio = device.is_audio;
    const isBLE = device.is_ble;

    let badges = '';
    if (isAudio) badges += '<span class="device-badge audio">Audio</span>';
    if (isBLE) badges += '<span class="device-badge ble">BLE</span>';

    return `
        <div class="device-item fade-in">
            <div class="device-info">
                <div class="device-name">${escapeHtml(name)}${badges}</div>
                <div class="device-addr">${device.addr}</div>
            </div>
            <div class="device-actions">
                <button class="btn btn-small btn-primary btn-attack-device" data-addr="${device.addr}">
                    ⚡
                </button>
            </div>
        </div>
    `;
}

// Agregar dispositivo a la lista
function addDeviceToList(device) {
    // Verificar si ya existe
    if (state.devices.find(d => d.addr === device.addr)) {
        return;
    }

    state.devices.push(device);

    // Si estaba vacía, limpiar mensaje
    const emptyState = elements.deviceList.querySelector('.empty-state');
    if (emptyState) {
        elements.deviceList.innerHTML = '';
    }

    // Agregar nuevo dispositivo
    elements.deviceList.insertAdjacentHTML('beforeend', createDeviceHTML(device));

    // Actualizar estadísticas
    elements.statTotal.textContent = state.devices.length;
}

// Iniciar escaneo
async function startScan() {
    elements.btnScan.disabled = true;
    elements.btnScan.innerHTML = '<span class="spinner"></span> Escaneando...';

    try {
        const response = await fetch('/api/scan', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            // El servidor enviará los dispositivos por WebSocket
        }
    } catch (error) {
        console.error('Error en escaneo:', error);
    }

    setTimeout(() => {
        elements.btnScan.disabled = false;
        elements.btnScan.innerHTML = '🔍 Escanear';
    }, 10000);
}

// Atacar dispositivo específico
async function attackDevice(addr) {
    try {
        const response = await fetch('/api/attack', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ addr })
        });

        const data = await response.json();
        if (data.success) {
            showAttackStatus(addr);
        }
    } catch (error) {
        console.error('Error iniciando ataque:', error);
    }
}

// Iniciar ataque continuo
async function startAttack() {
    elements.btnAttackStart.disabled = true;
    elements.btnAttackStop.disabled = false;

    try {
        const response = await fetch('/api/attack/start', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            state.attacking = true;
            elements.attackSection.style.display = 'block';
        }
    } catch (error) {
        console.error('Error iniciando ataque:', error);
        elements.btnAttackStart.disabled = false;
        elements.btnAttackStop.disabled = true;
    }
}

// Detener ataque
async function stopAttack() {
    try {
        const response = await fetch('/api/attack/stop', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            state.attacking = false;
            elements.attackSection.style.display = 'none';
        }
    } catch (error) {
        console.error('Error deteniendo ataque:', error);
    }

    elements.btnAttackStart.disabled = false;
    elements.btnAttackStop.disabled = true;
}

// Mostrar estado de ataque
function showAttackStatus(addr) {
    const device = state.devices.find(d => d.addr === addr);
    const name = device ? device.name : 'Desconocido';

    elements.attackSection.style.display = 'block';
    elements.attackTarget.innerHTML = `
        <span class="target-name">${escapeHtml(name)}</span>
        <span class="target-addr">${addr}</span>
    `;
}

// Actualizar estado de ataque
function updateAttackStatus(attack) {
    if (attack.attacking) {
        elements.attackSection.style.display = 'block';
        elements.attackThreads.textContent = attack.active_threads || 0;
        elements.attackRf.textContent = attack.esp32_jamming ? 'ON' : 'OFF';

        if (attack.current_target) {
            const name = attack.current_target.name || 'Desconocido';
            elements.attackTarget.innerHTML = `
                <span class="target-name">${escapeHtml(name)}</span>
                <span class="target-addr">${attack.current_target.addr}</span>
            `;
        }
    } else {
        elements.attackSection.style.display = 'none';
    }
}

// Actualizar estado ESP32
function updateESP32Status(connected, jamming) {
    state.esp32Connected = connected;

    if (connected) {
        elements.esp32Indicator.classList.add('connected');
        elements.esp32Status.textContent = jamming ? 'Jamming' : 'Conectado';
        elements.jamControls.style.display = 'flex';
    } else {
        elements.esp32Indicator.classList.remove('connected');
        elements.esp32Status.textContent = 'Desconectado';
        elements.jamControls.style.display = 'none';
    }
}

// Enviar comando de jamming
async function sendJamCommand(action, mode = null) {
    try {
        const body = { action };
        if (mode) body.mode = mode;

        const response = await fetch('/api/esp32/jam', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        await response.json();
    } catch (error) {
        console.error('Error enviando comando jam:', error);
    }
}

// Actualizar estado de conexión
function updateConnectionStatus(connected) {
    if (connected) {
        elements.statusText.textContent = 'Conectado';
    } else {
        elements.statusText.textContent = 'Desconectado';
    }
}

// Escapar HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
