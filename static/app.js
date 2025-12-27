// FastAPI Foundry Web Interface
const API_BASE = window.location.origin + '/api/v1';

// Глобальная конфигурация
let CONFIG = {
    foundry_url: 'http://localhost:50477/v1/',
    api_url: API_BASE
};

// Инициализация
document.addEventListener('DOMContentLoaded', async function() {
    await loadConfig();
    checkSystemStatus();
    loadModels();
    setInterval(checkSystemStatus, 30000);
});

// Загрузка конфигурации
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();
        
        if (data.success && data.config) {
            CONFIG.foundry_url = data.config.foundry_ai.base_url;
            console.log('Config loaded:', CONFIG);
        }
    } catch (error) {
        console.error('Failed to load config:', error);
    }
}

// Проверка статуса системы
async function checkSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        const indicator = document.getElementById('status-indicator');
        if (data.status === 'healthy') {
            if (data.foundry_status === 'healthy') {
                indicator.innerHTML = '<i class="bi bi-circle-fill text-success"></i> Online';
            } else {
                indicator.innerHTML = '<i class="bi bi-circle-fill text-warning"></i> Foundry недоступен';
            }
        } else {
            indicator.innerHTML = '<i class="bi bi-circle-fill text-danger"></i> Offline';
        }
        
        updateSystemInfo(data);
    } catch (error) {
        document.getElementById('status-indicator').innerHTML = '<i class="bi bi-circle-fill text-danger"></i> Error';
    }
}

// Обновление информации о системе
function updateSystemInfo(data) {
    const container = document.getElementById('system-status');
    
    // Получаем реальный порт из данных
    let foundryUrl = CONFIG.foundry_url;
    if (data.foundry_details && data.foundry_details.port) {
        foundryUrl = `http://localhost:${data.foundry_details.port}/v1/`;
        CONFIG.foundry_url = foundryUrl; // Обновляем глобальную конфигурацию
    }
    
    container.innerHTML = `
        <div class="row">
            <div class="col-6">
                <strong>API:</strong><br>
                <span class="badge ${data.status === 'healthy' ? 'bg-success' : 'bg-danger'}">${data.status}</span>
            </div>
            <div class="col-6">
                <strong>Foundry:</strong><br>
                <span class="badge ${data.foundry_status === 'healthy' ? 'bg-success' : 'bg-warning'}">${data.foundry_status === 'healthy' ? 'Connected' : 'Disconnected'}</span>
            </div>
            <div class="col-12 mt-2">
                <strong>Foundry URL:</strong><br>
                <small class="text-muted">${foundryUrl}</small>
            </div>
        </div>
    `;
}

// Загрузка моделей
async function loadModels() {
    try {
        const response = await fetch(`${API_BASE}/models`);
        const data = await response.json();
        
        if (data.success && data.models) {
            updateModelSelect(data.models);
        }
    } catch (error) {
        console.error('Failed to load models:', error);
    }
}

// Обновление списка моделей
function updateModelSelect(models) {
    const select = document.getElementById('chat-model');
    if (select) {
        select.innerHTML = '<option value="">Auto-select</option>';
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model.id;
            option.textContent = model.id;
            select.appendChild(option);
        });
    }
}

// Отправка сообщения
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    addMessageToChat('user', message);
    input.value = '';
    
    const typingId = addMessageToChat('assistant', '<i class="bi bi-three-dots"></i> Typing...');
    
    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                prompt: message,
                model: document.getElementById('chat-model').value || undefined,
                temperature: parseFloat(document.getElementById('temperature').value),
                max_tokens: parseInt(document.getElementById('max-tokens').value)
            })
        });
        
        const data = await response.json();
        document.getElementById(typingId).remove();
        
        if (data.success && data.content) {
            addMessageToChat('assistant', data.content);
        } else {
            addMessageToChat('assistant', `❌ Error: ${data.error || 'Failed to generate response'}`);
        }
    } catch (error) {
        document.getElementById(typingId).remove();
        addMessageToChat('assistant', '❌ Connection error');
    }
}

// Добавление сообщения в чат
function addMessageToChat(role, content) {
    const container = document.getElementById('chat-messages');
    const messageId = 'msg-' + Date.now();
    
    if (container.children.length === 1 && container.children[0].classList.contains('text-muted')) {
        container.innerHTML = '';
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `<div class="content">${content}</div>`;
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
    
    return messageId;
}

// Foundry Management
async function startFoundryService() {
    const btn = document.getElementById('start-foundry-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Starting...';
    
    try {
        const response = await fetch(`${API_BASE}/foundry/start`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Foundry started successfully', 'success');
            await loadConfig(); // Перезагружаем конфигурацию
            checkSystemStatus();
        } else {
            showAlert(`Failed to start Foundry: ${data.error}`, 'danger');
        }
    } catch (error) {
        showAlert('Failed to connect to API', 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-play-fill"></i> Start Foundry';
    }
}

async function stopFoundryService() {
    const btn = document.getElementById('stop-foundry-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Stopping...';
    
    try {
        const response = await fetch(`${API_BASE}/foundry/stop`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Foundry stopped', 'info');
            checkSystemStatus();
        } else {
            showAlert(`Failed to stop Foundry: ${data.error}`, 'danger');
        }
    } catch (error) {
        showAlert('Failed to connect to API', 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-stop-fill"></i> Stop Foundry';
    }
}

async function checkFoundryStatus() {
    try {
        const response = await fetch(`${API_BASE}/foundry/status`);
        const data = await response.json();
        
        if (data.success) {
            updateFoundryStatus(data.status, data);
        }
    } catch (error) {
        updateFoundryStatus('error');
    }
}

function updateFoundryStatus(status, data = {}) {
    const badge = document.getElementById('foundry-service-status');
    const info = document.getElementById('foundry-service-info');
    
    // Получаем реальный URL
    let foundryUrl = CONFIG.foundry_url;
    if (data.port) {
        foundryUrl = `http://localhost:${data.port}/v1/`;
        CONFIG.foundry_url = foundryUrl;
    }
    
    switch (status) {
        case 'running':
        case 'healthy':
            badge.className = 'badge bg-success';
            badge.textContent = 'Running';
            info.innerHTML = `<small>Foundry running on ${foundryUrl}</small>`;
            break;
        default:
            badge.className = 'badge bg-secondary';
            badge.textContent = 'Stopped';
            info.innerHTML = '<small>Foundry service is not running</small>';
            break;
    }
}

// Утилиты
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 5000);
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function updateTempValue(value) {
    document.getElementById('temp-value').textContent = value;
}

function clearChat() {
    document.getElementById('chat-messages').innerHTML = `
        <div class="text-muted text-center">
            <i class="bi bi-chat-square-dots"></i><br>
            Start a conversation with AI
        </div>
    `;
}

function refreshModels() {
    loadModels();
}