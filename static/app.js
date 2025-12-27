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
    await loadModels();
    await loadConnectedModels(); // Добавляем загрузку подключенных моделей
    setInterval(checkSystemStatus, 30000);
});

// Загрузка конфигурации
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();
        
        if (data.success && data.config) {
            CONFIG.foundry_url = data.config.foundry_ai.base_url;
            CONFIG.default_model = data.config.foundry_ai.default_model;
            CONFIG.auto_load_default = data.config.foundry_ai.auto_load_default || false;
            
            // Обновляем редактор конфигурации если он существует
            const configEditor = document.getElementById('config-editor');
            if (configEditor) {
                // Форматируем JSON с отступами для лучшей читаемости
                configEditor.value = JSON.stringify(data.config, null, 2);
                console.log('Config editor updated with full config:', Object.keys(data.config));
            }
            
            // Проверяем доступность модели по умолчанию
            await validateDefaultModel();
            
            console.log('Config loaded:', CONFIG);
            console.log('Full config sections:', Object.keys(data.config));
        }
    } catch (error) {
        console.error('Failed to load config:', error);
        const configEditor = document.getElementById('config-editor');
        if (configEditor) {
            configEditor.value = 'Error loading configuration: ' + error.message;
        }
    }
}

// Проверка доступности модели по умолчанию
async function validateDefaultModel() {
    try {
        // Получаем список доступных моделей из Foundry
        const response = await fetch(`${API_BASE}/foundry/models/loaded`);
        const data = await response.json();
        
        if (data.success && data.models) {
            const availableModels = data.models.map(m => m.id);
            
            if (CONFIG.default_model && availableModels.includes(CONFIG.default_model)) {
                // Модель из config.json доступна - используем её
                updateModelStatus(`Модель по умолчанию: ${CONFIG.default_model}`, 'success');
                const chatModelSelect = document.getElementById('chat-model');
                if (chatModelSelect) {
                    chatModelSelect.value = CONFIG.default_model;
                }
            } else if (availableModels.length > 0) {
                // Есть доступные модели, но не та что в config - предлагаем выбрать
                const firstAvailable = availableModels[0];
                updateModelStatus(`Доступные модели найдены. <button class="btn btn-sm btn-primary ms-2" onclick="selectFoundryModel('${firstAvailable}')">${firstAvailable}</button> <button class="btn btn-sm btn-outline-secondary ms-2" onclick="showAvailableModels()">Показать все</button>`, 'info');
                
                // Автоматически заполняем селектор чата доступными моделями
                const chatModelSelect = document.getElementById('chat-model');
                if (chatModelSelect) {
                    chatModelSelect.innerHTML = '<option value="">Выберите модель...</option>';
                    availableModels.forEach(modelId => {
                        const option = document.createElement('option');
                        option.value = modelId;
                        option.textContent = modelId;
                        chatModelSelect.appendChild(option);
                    });
                }
            } else {
                // Нет доступных моделей
                updateModelStatus('Модели не загружены. <button class="btn btn-sm btn-primary ms-2" onclick="showAvailableModels()">Загрузить модель</button>', 'warning');
            }
        } else {
            updateModelStatus('Не удалось проверить доступные модели. Foundry может быть не запущен.', 'warning');
        }
    } catch (error) {
        console.error('Error validating default model:', error);
        updateModelStatus('Ошибка проверки модели по умолчанию. Проверьте подключение к Foundry.', 'danger');
    }
}

// Загрузка модели по умолчанию
async function loadDefaultModel() {
    try {
        showAlert('Начинаем загрузку модели по умолчанию...', 'info');
        
        const response = await fetch(`${API_BASE}/foundry/models/auto-load-default`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            // Обновляем статус через несколько секунд
            setTimeout(() => {
                validateDefaultModel();
                loadModels();
            }, 3000);
        } else {
            showAlert(`Ошибка: ${data.error}`, 'danger');
        }
    } catch (error) {
        showAlert('Ошибка загрузки модели', 'danger');
    }
}

// Обновление статуса модели в интерфейсе
function updateModelStatus(message, type) {
    // Обновляем индикатор в чате
    const indicator = document.getElementById('default-model-indicator');
    if (indicator) {
        const colorClass = type === 'success' ? 'text-success' : type === 'warning' ? 'text-warning' : 'text-danger';
        const icon = type === 'success' ? 'bi-check-circle' : type === 'warning' ? 'bi-exclamation-triangle' : 'bi-x-circle';
        indicator.innerHTML = `<i class="bi ${icon} ${colorClass}"></i> ${message}`;
        indicator.className = `${colorClass}`;
    }
    
    // Добавляем статус в системную информацию
    const systemStatus = document.getElementById('system-status');
    if (systemStatus) {
        const statusHtml = systemStatus.innerHTML;
        const modelStatusHtml = `
            <div class="col-12 mt-2">
                <strong>Модель по умолчанию:</strong><br>
                <span class="badge bg-${type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'danger'}">${message}</span>
            </div>
        `;
        
        // Удаляем предыдущий статус модели если есть
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = statusHtml;
        const existingModelStatus = tempDiv.querySelector('.col-12:last-child');
        if (existingModelStatus && existingModelStatus.innerHTML.includes('Модель по умолчанию')) {
            existingModelStatus.remove();
        }
        
        systemStatus.innerHTML = tempDiv.innerHTML + modelStatusHtml;
    }
}

// Загрузка конфигурации в отдельные поля
async function loadConfigFields() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();
        
        if (data.success && data.config) {
            const config = data.config;
            
            // FastAPI Server
            document.getElementById('config-api-host').value = config.fastapi_server?.host || '0.0.0.0';
            document.getElementById('config-api-port').value = config.fastapi_server?.port || 9696;
            document.getElementById('config-api-auto-port').checked = config.fastapi_server?.auto_find_free_port || true;
            document.getElementById('config-api-mode').value = config.fastapi_server?.mode || 'dev';
            document.getElementById('config-api-workers').value = config.fastapi_server?.workers || 1;
            
            // Foundry AI
            document.getElementById('config-foundry-url').value = config.foundry_ai?.base_url || 'http://localhost:50477/v1/';
            document.getElementById('config-foundry-model').value = config.foundry_ai?.default_model || '';
            document.getElementById('config-foundry-temp').value = config.foundry_ai?.temperature || 0.6;
            document.getElementById('config-foundry-tokens').value = config.foundry_ai?.max_tokens || 2048;
            document.getElementById('config-foundry-autoload').checked = config.foundry_ai?.auto_load_default || false;
            
            // RAG System
            document.getElementById('config-rag-enabled').checked = config.rag_system?.enabled || false;
            document.getElementById('config-rag-index').value = config.rag_system?.index_dir || './rag_index';
            document.getElementById('config-rag-chunk').value = config.rag_system?.chunk_size || 1000;
            
            // Security
            document.getElementById('config-security-key').value = config.security?.api_key || '';
            document.getElementById('config-security-https').checked = config.security?.https_enabled || false;
            
            // Logging
            document.getElementById('config-log-level').value = config.logging?.level || 'INFO';
            document.getElementById('config-log-file').value = config.logging?.file || 'logs/fastapi-foundry.log';
            
            // Development
            document.getElementById('config-dev-debug').checked = config.development?.debug || false;
            document.getElementById('config-dev-verbose').checked = config.development?.verbose || false;
            
            // Обновляем глобальную конфигурацию
            CONFIG.foundry_url = config.foundry_ai?.base_url || CONFIG.foundry_url;
            CONFIG.default_model = config.foundry_ai?.default_model || CONFIG.default_model;
            CONFIG.auto_load_default = config.foundry_ai?.auto_load_default || false;
            
            console.log('Config fields loaded successfully');
            showAlert('Configuration loaded', 'success');
        }
    } catch (error) {
        console.error('Failed to load config fields:', error);
        showAlert('Failed to load configuration', 'danger');
    }
}

// Сохранение конфигурации из отдельных полей
async function saveConfigFields() {
    const statusDiv = document.getElementById('config-status');
    
    try {
        // Функция для безопасного получения значения
        const getValue = (id, defaultValue = null) => {
            const element = document.getElementById(id);
            if (!element) return defaultValue;
            const value = element.value;
            return (value === '') ? null : value;
        };
        
        const getIntValue = (id, defaultValue = null) => {
            const value = getValue(id);
            if (value === null || value === '') return defaultValue;
            const parsed = parseInt(value);
            return isNaN(parsed) ? defaultValue : parsed;
        };
        
        const getFloatValue = (id, defaultValue = null) => {
            const value = getValue(id);
            if (value === null || value === '') return defaultValue;
            const parsed = parseFloat(value);
            return isNaN(parsed) ? defaultValue : parsed;
        };
        
        const getBoolValue = (id, defaultValue = false) => {
            const element = document.getElementById(id);
            return element ? element.checked : defaultValue;
        };
        
        // Собираем конфигурацию из полей с валидацией
        const configData = {
            fastapi_server: {
                host: getValue('config-api-host') || '0.0.0.0',
                port: getIntValue('config-api-port') || 9696,
                auto_find_free_port: getBoolValue('config-api-auto-port', true),
                mode: getValue('config-api-mode') || 'dev',
                workers: getIntValue('config-api-workers') || 1,
                reload: true,
                cors_origins: ["*"]
            },
            foundry_ai: {
                base_url: getValue('config-foundry-url') || 'http://localhost:50477/v1/',
                default_model: getValue('config-foundry-model'),
                auto_load_default: getBoolValue('config-foundry-autoload', false),
                temperature: getFloatValue('config-foundry-temp') || 0.6,
                top_p: 0.9,
                top_k: 40,
                max_tokens: getIntValue('config-foundry-tokens') || 2048,
                timeout: 300
            },
            rag_system: {
                enabled: getBoolValue('config-rag-enabled', false),
                index_dir: getValue('config-rag-index') || './rag_index',
                model: "sentence-transformers/all-MiniLM-L6-v2",
                chunk_size: getIntValue('config-rag-chunk') || 1000,
                top_k: 5
            },
            security: {
                api_key: getValue('config-security-key'),
                https_enabled: getBoolValue('config-security-https', false),
                cors_origins: ["*"],
                ssl_cert_file: "~/.ssl/cert.pem",
                ssl_key_file: "~/.ssl/key.pem"
            },
            logging: {
                level: getValue('config-log-level') || 'INFO',
                file: getValue('config-log-file') || 'logs/fastapi-foundry.log'
            },
            development: {
                debug: getBoolValue('config-dev-debug', false),
                verbose: getBoolValue('config-dev-verbose', false),
                temp_dir: "./temp"
            }
        };
        
        // Получаем полную текущую конфигурацию и обновляем только измененные поля
        const currentResponse = await fetch(`${API_BASE}/config`);
        const currentData = await currentResponse.json();
        
        if (currentData.success && currentData.config) {
            // Объединяем с существующими данными
            const fullConfig = { ...currentData.config };
            
            // Обновляем только измененные поля
            Object.keys(configData).forEach(section => {
                if (fullConfig[section]) {
                    fullConfig[section] = { ...fullConfig[section], ...configData[section] };
                } else {
                    fullConfig[section] = configData[section];
                }
            });
            
            console.log('Saving config fields:', Object.keys(configData));
            
            const response = await fetch(`${API_BASE}/config`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({config: fullConfig})
            });
            
            const result = await response.json();
            
            if (result && result.success) {
                statusDiv.className = 'alert alert-success';
                statusDiv.innerHTML = `<i class="bi bi-check-circle"></i> ${result.message || 'Configuration saved'}`;
                if (result.backup_created) {
                    statusDiv.innerHTML += `<br><small>Backup: ${result.backup_created}</small>`;
                }
                statusDiv.style.display = 'block';
                
                // Обновляем глобальную конфигурацию
                CONFIG.foundry_url = configData.foundry_ai.base_url;
                CONFIG.default_model = configData.foundry_ai.default_model;
                CONFIG.auto_load_default = configData.foundry_ai.auto_load_default;
                
                showAlert('Configuration saved successfully', 'success');
                
                // Перепроверяем модель по умолчанию
                setTimeout(() => {
                    validateDefaultModel();
                }, 1000);
            } else {
                statusDiv.className = 'alert alert-danger';
                statusDiv.innerHTML = `<i class="bi bi-exclamation-triangle"></i> Error: ${result?.error || 'Unknown error'}`;
                statusDiv.style.display = 'block';
                showAlert(`Error: ${result?.error || 'Unknown error'}`, 'danger');
            }
        } else {
            throw new Error('Failed to load current configuration');
        }
    } catch (error) {
        console.error('Save config error:', error);
        console.error('Error details:', {
            message: error.message,
            stack: error.stack
        });
        
        statusDiv.className = 'alert alert-danger';
        statusDiv.innerHTML = `<i class="bi bi-exclamation-triangle"></i> Error: ${error.message}`;
        statusDiv.style.display = 'block';
        showAlert(`Error: ${error.message}`, 'danger');
    }
    
    // Скрыть статус через 10 секунд
    setTimeout(() => {
        if (statusDiv) {
            statusDiv.style.display = 'none';
        }
    }, 10000);
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
    
    // Получаем реальный порт из данных API
    let foundryUrl = CONFIG.foundry_url;
    if (data.foundry_details && data.foundry_details.url) {
        foundryUrl = data.foundry_details.url;
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

// Загрузка подключенных моделей для таба Models
async function loadConnectedModels() {
    try {
        const response = await fetch(`${API_BASE}/models/connected`);
        const data = await response.json();
        
        const container = document.getElementById('models-container');
        
        if (data.success && data.models && data.models.length > 0) {
            container.innerHTML = data.models.map(model => `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card model-card h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h6 class="card-title mb-0">${model.name}</h6>
                                <span class="badge ${
                                    model.status === 'connected' ? 'bg-success' : 
                                    model.status === 'offline' ? 'bg-danger' : 'bg-secondary'
                                }">${model.status}</span>
                            </div>
                            <p class="card-text">
                                <small class="text-muted">ID: ${model.id}</small><br>
                                <small class="text-muted">Provider: ${model.provider}</small><br>
                                <small class="text-muted">Max tokens: ${model.max_tokens || 'N/A'}</small>
                            </p>
                            <div class="form-check mb-2">
                                <input class="form-check-input" type="radio" name="default-model" id="default-${model.id}" value="${model.id}" ${CONFIG.default_model === model.id ? 'checked' : ''} onchange="setDefaultModel('${model.id}')">
                                <label class="form-check-label" for="default-${model.id}">
                                    <small>Use as default model</small>
                                </label>
                            </div>
                        </div>
                        <div class="card-footer bg-transparent">
                            <div class="btn-group w-100" role="group">
                                <button class="btn btn-sm btn-primary" onclick="selectModelForChat('${model.id}')">
                                    <i class="bi bi-chat"></i> Use in Chat
                                </button>
                                <button class="btn btn-sm btn-outline-secondary" onclick="testModel('${model.id}')">
                                    <i class="bi bi-play"></i> Test
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = `
                <div class="col-12">
                    <div class="text-center text-muted py-5">
                        <i class="bi bi-cpu" style="font-size: 3rem;"></i><br>
                        <h5>No Connected Models</h5>
                        <p>No models are currently connected. ${data.error ? `Error: ${data.error}` : 'Start Foundry and load a model to see it here.'}</p>
                        <button class="btn btn-primary" onclick="refreshModels()">
                            <i class="bi bi-arrow-clockwise"></i> Refresh
                        </button>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Failed to load connected models:', error);
        document.getElementById('models-container').innerHTML = `
            <div class="col-12">
                <div class="text-center text-danger py-5">
                    <i class="bi bi-exclamation-triangle" style="font-size: 3rem;"></i><br>
                    <h5>Error Loading Models</h5>
                    <p>Failed to connect to the API. Make sure the server is running.</p>
                    <button class="btn btn-outline-primary" onclick="refreshModels()">
                        <i class="bi bi-arrow-clockwise"></i> Try Again
                    </button>
                </div>
            </div>
        `;
    }
}

// Выбор модели для чата
function selectModelForChat(modelId) {
    const chatModelSelect = document.getElementById('chat-model');
    if (chatModelSelect) {
        // Проверяем есть ли такая опция
        let optionExists = false;
        for (let option of chatModelSelect.options) {
            if (option.value === modelId) {
                optionExists = true;
                break;
            }
        }
        
        // Если опции нет, добавляем
        if (!optionExists) {
            const option = document.createElement('option');
            option.value = modelId;
            option.textContent = modelId;
            chatModelSelect.appendChild(option);
        }
        
        // Выбираем модель
        chatModelSelect.value = modelId;
        
        // Сохраняем как модель по умолчанию
        saveDefaultModel(modelId);
        
        showAlert(`Model ${modelId} selected for chat`, 'success');
        
        // Переключаемся на вкладку чата
        const chatTab = document.getElementById('chat-tab');
        if (chatTab) {
            chatTab.click();
        }
    }
}

// Тест модели
async function testModel(modelId) {
    try {
        showAlert(`Testing model ${modelId}...`, 'info');
        
        // Получаем актуальный статус Foundry для правильного URL
        const healthResponse = await fetch(`${API_BASE}/health`);
        const healthData = await healthResponse.json();
        
        let foundryUrl = CONFIG.foundry_url;
        if (healthData.foundry_details && healthData.foundry_details.url) {
            foundryUrl = healthData.foundry_details.url;
        }
        
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                prompt: 'Hello! Please respond with a short greeting.',
                model: modelId,
                max_tokens: 50
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(`Model ${modelId} test successful: "${data.content.substring(0, 100)}..."`, 'success');
        } else {
            showAlert(`Model ${modelId} test failed: ${data.error}`, 'danger');
        }
    } catch (error) {
        showAlert(`Model ${modelId} test error: ${error.message}`, 'danger');
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
        
        // Автоматически выбираем модель по умолчанию если она доступна
        if (CONFIG.default_model) {
            const availableModels = models.map(m => m.id);
            if (availableModels.includes(CONFIG.default_model)) {
                select.value = CONFIG.default_model;
                console.log(`Default model "${CONFIG.default_model}" selected automatically`);
            } else {
                console.warn(`Default model "${CONFIG.default_model}" not available in current models`);
            }
        }
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
    loadConnectedModels(); // Добавляем загрузку подключенных моделей
}

// Функции для вкладки Logs
async function refreshLogs() {
    try {
        console.log('Загружаем логи...');
        const response = await fetch('/logs/recent');
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Logs data:', data);
        
        const container = document.getElementById('logs-container');
        
        if (data.success && data.data.logs.length > 0) {
            container.innerHTML = data.data.logs.map(log => `
                <div class="log-entry log-${log.level}">
                    <span class="log-timestamp">${log.timestamp}</span>
                    <span class="log-logger">[${log.logger}]</span>
                    <span class="log-message">${log.message}</span>
                </div>
            `).join('');
        } else {
            container.innerHTML = `
                <div class="text-center text-muted p-4">
                    <i class="bi bi-file-text"></i><br>
                    ${data.data?.message || 'Логи не найдены'}
                </div>
            `;
        }
        
        // Обновляем статистику
        updateLogsStats(data.data.logs);
        
    } catch (error) {
        console.error('Failed to refresh logs:', error);
        document.getElementById('logs-container').innerHTML = `
            <div class="text-center text-danger p-4">
                <i class="bi bi-exclamation-triangle"></i><br>
                Ошибка загрузки логов
            </div>
        `;
    }
}

function updateLogsStats(logs) {
    const healthContainer = document.getElementById('logs-health-status');
    const errorContainer = document.getElementById('error-summary');
    const perfContainer = document.getElementById('performance-metrics');
    
    // Подсчет по уровням
    const stats = {
        error: logs.filter(l => l.level === 'error').length,
        warning: logs.filter(l => l.level === 'warning').length,
        info: logs.filter(l => l.level === 'info').length,
        debug: logs.filter(l => l.level === 'debug').length
    };
    
    // Статус системы
    const healthStatus = stats.error > 0 ? 'critical' : (stats.warning > 0 ? 'warning' : 'healthy');
    const healthColor = healthStatus === 'critical' ? 'danger' : (healthStatus === 'warning' ? 'warning' : 'success');
    
    healthContainer.innerHTML = `
        <div class="text-center">
            <i class="bi bi-heart-fill text-${healthColor}" style="font-size: 2rem;"></i><br>
            <strong class="text-${healthColor}">${healthStatus.toUpperCase()}</strong><br>
            <small>Всего записей: ${logs.length}</small>
        </div>
    `;
    
    // Ошибки
    errorContainer.innerHTML = `
        <div class="mb-2">
            <span class="badge bg-danger">${stats.error}</span> Ошибок
        </div>
        <div class="mb-2">
            <span class="badge bg-warning">${stats.warning}</span> Предупреждений
        </div>
        <div>
            <span class="badge bg-info">${stats.info}</span> Информационных
        </div>
    `;
    
    // Производительность
    perfContainer.innerHTML = `
        <div class="mb-2">
            <small>Последние записи:</small><br>
            <strong>${logs.length}</strong>
        </div>
        <div>
            <small>Статус:</small><br>
            <span class="badge bg-${healthColor}">${healthStatus}</span>
        </div>
    `;
}

function filterLogs() {
    const filter = document.getElementById('log-level-filter').value;
    const entries = document.querySelectorAll('.log-entry');
    
    entries.forEach(entry => {
        if (!filter || entry.classList.contains(`log-${filter}`)) {
            entry.style.display = 'block';
        } else {
            entry.style.display = 'none';
        }
    });
}

function clearLogsView() {
    document.getElementById('logs-container').innerHTML = `
        <div class="text-muted text-center p-4">
            <i class="bi bi-file-text"></i><br>
            Логи очищены. Нажмите "Обновить" для загрузки.
        </div>
    `;
}

// Автообновление логов каждые 30 секунд
document.addEventListener('DOMContentLoaded', function() {
    // При переключении на вкладку Models
    const modelsTab = document.getElementById('models-tab');
    if (modelsTab) {
        modelsTab.addEventListener('click', function() {
            setTimeout(loadConnectedModels, 100); // Небольшая задержка
        });
    }
    
    // При переключении на вкладку Logs
    const logsTab = document.getElementById('logs-tab');
    if (logsTab) {
        logsTab.addEventListener('click', function() {
            setTimeout(refreshLogs, 100); // Небольшая задержка
        });
    }
    
    // При переключении на вкладку Settings
    const settingsTab = document.getElementById('settings-tab');
    if (settingsTab) {
        settingsTab.addEventListener('click', function() {
            setTimeout(loadConfigFields, 100); // Загружаем конфигурацию в поля
        });
    }
    
    // Обработчик изменения модели в чате
    const chatModelSelect = document.getElementById('chat-model');
    if (chatModelSelect) {
        chatModelSelect.addEventListener('change', function() {
            const selectedModel = this.value;
            if (selectedModel && selectedModel !== CONFIG.default_model) {
                saveDefaultModel(selectedModel);
            }
        });
    }
});

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
                    <div>
                        <button class="btn btn-sm btn-primary me-2" onclick="selectFoundryModel('${model.id}')">
                            <i class="bi bi-check-circle"></i> Использовать
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="removeFoundryModel('${model.id}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
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
    
    const progressDiv = document.getElementById('download-progress');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    
    try {
        // Показываем прогресс
        progressDiv.style.display = 'block';
        progressBar.style.width = '10%';
        progressText.textContent = `Начинаем загрузку ${modelId}...`;
        
        showAlert(`Началась загрузка модели ${modelId}...`, 'info');
        
        const response = await fetch(`${API_BASE}/foundry/models/load`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({model_id: modelId})
        });
        
        const data = await response.json();
        
        if (data.success) {
            progressBar.style.width = '30%';
            progressText.textContent = `Загрузка ${modelId} в процессе...`;
            
            showAlert(data.message, 'success');
            
            // Начинаем отслеживание прогресса
            monitorModelDownload(modelId, progressBar, progressText, progressDiv);
        } else {
            progressDiv.style.display = 'none';
            showAlert(`Ошибка: ${data.error}`, 'danger');
        }
    } catch (error) {
        progressDiv.style.display = 'none';
        showAlert('Ошибка загрузки модели', 'danger');
        console.error('Download error:', error);
    }
}

// Отслеживание прогресса загрузки модели
async function monitorModelDownload(modelId, progressBar, progressText, progressDiv) {
    let attempts = 0;
    const maxAttempts = 60; // 5 минут (по 5 секунд)
    let currentProgress = 30;
    
    const checkInterval = setInterval(async () => {
        attempts++;
        
        try {
            // Проверяем статус модели
            const response = await fetch(`${API_BASE}/foundry/models/status/${modelId}`);
            const data = await response.json();
            
            if (data.success) {
                if (data.status === 'loaded') {
                    // Модель загружена!
                    clearInterval(checkInterval);
                    progressBar.style.width = '100%';
                    progressText.textContent = `Модель ${modelId} успешно загружена!`;
                    
                    setTimeout(() => {
                        progressDiv.style.display = 'none';
                        showAlert(`Модель ${modelId} готова к использованию!`, 'success');
                        
                        // Обновляем списки
                        listFoundryModels();
                        loadModels();
                    }, 2000);
                    
                    return;
                } else {
                    // Модель еще загружается
                    currentProgress = Math.min(currentProgress + 2, 90);
                    progressBar.style.width = currentProgress + '%';
                    progressText.textContent = `Загрузка ${modelId}... (${attempts}/${maxAttempts})`;
                }
            }
            
            // Проверяем таймаут
            if (attempts >= maxAttempts) {
                clearInterval(checkInterval);
                progressBar.classList.add('bg-warning');
                progressText.textContent = `Загрузка ${modelId} занимает больше времени чем ожидалось...`;
                
                showAlert(`Загрузка ${modelId} продолжается в фоне. Проверьте логи Foundry.`, 'warning');
                
                setTimeout(() => {
                    progressDiv.style.display = 'none';
                }, 5000);
            }
            
        } catch (error) {
            console.error('Error checking model status:', error);
            // Продолжаем проверку несмотря на ошибку
        }
    }, 5000); // Проверяем каждые 5 секунд
}

async function removeFoundryModel(modelId) {
    if (!confirm(`Удалить модель ${modelId}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/foundry/models/unload`, {
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

function selectFoundryModel(modelId) {
    // Устанавливаем модель в чате
    const chatModelSelect = document.getElementById('chat-model');
    if (chatModelSelect) {
        // Проверяем есть ли такая опция
        let optionExists = false;
        for (let option of chatModelSelect.options) {
            if (option.value === modelId) {
                optionExists = true;
                break;
            }
        }
        
        // Если опции нет, добавляем
        if (!optionExists) {
            const option = document.createElement('option');
            option.value = modelId;
            option.textContent = modelId;
            chatModelSelect.appendChild(option);
        }
        
        // Выбираем модель
        chatModelSelect.value = modelId;
        
        // Сохраняем как модель по умолчанию
        saveDefaultModel(modelId);
        
        showAlert(`Модель ${modelId} выбрана как модель по умолчанию`, 'success');
        
        // Переключаемся на вкладку чата
        const chatTab = document.getElementById('chat-tab');
        if (chatTab) {
            chatTab.click();
        }
    }
}

// Установка модели по умолчанию через radio кнопку
function setDefaultModel(modelId) {
    saveDefaultModel(modelId);
    showAlert(`Модель ${modelId} установлена как модель по умолчанию`, 'success');
    
    // Обновляем глобальную конфигурацию
    CONFIG.default_model = modelId;
    
    // Обновляем селектор в чате
    const chatModelSelect = document.getElementById('chat-model');
    if (chatModelSelect) {
        chatModelSelect.value = modelId;
    }
    
    // Обновляем статус модели
    updateModelStatus(`Модель по умолчанию: ${modelId}`, 'success');
}

// Сохранение модели по умолчанию в config.json
async function saveDefaultModel(modelId) {
    try {
        // Получаем текущую конфигурацию
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();
        
        if (data.success && data.config) {
            // Обновляем модель по умолчанию
            data.config.foundry_ai.default_model = modelId;
            
            // Сохраняем конфигурацию
            const saveResponse = await fetch(`${API_BASE}/config`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({config: data.config})
            });
            
            const saveResult = await saveResponse.json();
            if (saveResult.success) {
                console.log(`Default model saved: ${modelId}`);
                // Обновляем глобальную конфигурацию
                CONFIG.default_model = modelId;
            } else {
                console.error('Failed to save default model:', saveResult.error);
            }
        }
    } catch (error) {
        console.error('Error saving default model:', error);
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
        'deepseek-r1-distill-qwen-7b-generic-cpu:3': 'Продвинутая CPU модель (6.43 GB). Высокое качество ответов. (Недоступна)',
        'phi-3-mini-4k-instruct-openvino-gpu:1': 'GPU модель (2.4 GB). Требует совместимую видеокарту.'
    };
    
    const info = modelInfo[modelId] || 'Информация о модели недоступна';
    showAlert(info, 'info');
}

// Пропустить автозагрузку
function skipAutoLoad() {
    const modelName = CONFIG.default_model.split(':')[0];
    updateModelStatus(`Модель "${modelName}" недоступна. <button class="btn btn-sm btn-primary ms-2" onclick="loadDefaultModel()">Загрузить</button> <button class="btn btn-sm btn-outline-secondary ms-2" onclick="showAvailableModels()">Показать доступные</button>`, 'warning');
}

// Показать доступные модели
function showAvailableModels() {
    // Переключаемся на вкладку Foundry
    const foundryTab = document.getElementById('foundry-tab');
    if (foundryTab) {
        foundryTab.click();
        // Показываем список моделей
        setTimeout(() => {
            listFoundryModels();
        }, 100);
    }
    showAlert('Переключились на вкладку Foundry для просмотра доступных моделей', 'info');
}

// Скрыть прогресс-бар
function hideProgress() {
    const progressDiv = document.getElementById('download-progress');
    if (progressDiv) {
        progressDiv.style.display = 'none';
    }
}