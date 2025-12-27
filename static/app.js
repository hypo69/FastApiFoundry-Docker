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

// Foundry Status Check
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
            badge.textContent = 'Работает';
            info.innerHTML = `<small>Foundry работает на ${foundryUrl}</small>`;
            break;
        case 'disabled':
            badge.className = 'badge bg-info';
            badge.textContent = 'Управляется через start.ps1';
            info.innerHTML = '<small>Используйте start.ps1 для управления Foundry</small>';
            break;
        default:
            badge.className = 'badge bg-secondary';
            badge.textContent = 'Остановлен';
            info.innerHTML = '<small>Foundry сервис не запущен</small>';
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

// Управление моделями Foundry
async function listFoundryModels() {
    try {
        const response = await fetch(`${API_BASE}/foundry/models/loaded`);
        const data = await response.json();
        
        const container = document.getElementById('foundry-models-list');
        
        if (data.success && data.models.length > 0) {
            container.innerHTML = data.models.map(model => `
                <div class="d-flex justify-content-between align-items-center border-bottom py-2">
                    <div>
                        <strong>${model.id}</strong><br>
                        <small class="text-muted">Статус: ${model.status}</small>
                    </div>
                    <button class="btn btn-sm btn-outline-danger" onclick="removeFoundryModel('${model.id}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            `).join('');
        } else {
            container.innerHTML = `
                <div class="text-center text-muted py-3">
                    <i class="bi bi-inbox"></i><br>
                    Модели не загружены<br>
                    <small>Используйте "Загрузить модель" ниже</small>
                </div>
            `;
        }
    } catch (error) {
        console.error('Failed to list Foundry models:', error);
        showAlert('Ошибка получения списка моделей', 'danger');
    }
}

async function downloadAndRunModel() {
    const select = document.getElementById('model-select');
    const modelId = select.value;
    
    if (!modelId) {
        showAlert('Выберите модель для загрузки', 'warning');
        return;
    }
    
    try {
        showAlert(`Началась загрузка модели ${modelId}...`, 'info');
        
        const response = await fetch(`${API_BASE}/foundry/models/pull`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({model_id: modelId})
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            // Обновляем список через несколько секунд
            setTimeout(() => {
                listFoundryModels();
                loadModels(); // Обновляем список в чате
            }, 5000);
        } else {
            showAlert(`Ошибка: ${data.error}`, 'danger');
        }
    } catch (error) {
        showAlert('Ошибка загрузки модели', 'danger');
    }
}

async function removeFoundryModel(modelId) {
    if (!confirm(`Удалить модель ${modelId}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/foundry/models/remove`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({model_id: modelId})
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            listFoundryModels();
            loadModels();
        } else {
            showAlert(`Ошибка: ${data.error}`, 'danger');
        }
    } catch (error) {
        showAlert('Ошибка удаления модели', 'danger');
    }
}

function showModelInfo() {
    const select = document.getElementById('model-select');
    const modelId = select.value;
    
    if (!modelId) {
        showAlert('Выберите модель для получения информации', 'warning');
        return;
    }
    
    const modelInfo = {
        'qwen2.5-0.5b-instruct-generic-cpu:4': 'Самая легкая CPU модель (0.8 GB). Быстрая и эффективная.',
        'qwen2.5-1.5b-instruct-generic-cpu:4': 'Средняя CPU модель (1.78 GB). Хороший баланс скорости и качества.',
        'deepseek-r1-distill-qwen-7b-generic-cpu:3': 'Продвинутая CPU модель (6.43 GB). Высокое качество ответов.',
        'phi-3-mini-4k-instruct-openvino-gpu:1': 'GPU модель (2.4 GB). Требует совместимую видеокарту.'
    };
    
    const info = modelInfo[modelId] || 'Информация о модели недоступна';
    showAlert(info, 'info');
}