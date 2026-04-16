// =============================================================================
// Название процесса: Веб-интерфейс FastAPI Foundry
// =============================================================================
// Описание:
//   Управление конфигурацией, моделями и чатом через веб-панель.
//   Взаимодействие с API Foundry и HuggingFace.
//
// File: static/app.js
// Project: FastApiFoundry (Docker)
// Version: 0.2.1
// Author: hypo69
// License: CC BY-NC-SA 4.0
// Copyright: © 2025 AiStros
// Date: 9 декабря 2025
// =============================================================================

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
    await checkSystemStatus();
    await loadModels();
    await loadConnectedModels();
    if (typeof hfUpdateChatModelSelect === 'function') hfUpdateChatModelSelect();
    setInterval(checkSystemStatus, 30000);
});

// Загрузка конфигурации
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();
        
        if (data.success) {
            // // Обновление CONFIG с данными из API
            CONFIG.foundry_url = data.foundry_ai.base_url;
            CONFIG.default_model = data.foundry_ai.default_model;
            CONFIG.auto_load_default = data.foundry_ai.auto_load_default || false;

            // Порт llama.cpp из config.json
            const llamaPort = data.config?.llama_cpp?.port;
            if (llamaPort) {
                const el = document.getElementById('llama-port');
                if (el) el.value = llamaPort;
            }
            
            console.log('Config loaded from API:', CONFIG);
            
            // Проверяем доступность модели по умолчанию
            await validateDefaultModel();
        } else {
            console.error('Failed to load config from API:', data.error);
        }
    } catch (error) {
        console.error('Failed to load config:', error);
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

// Обновление бейджа выбранной модели
function updateChatModelBadge(modelId) {
    const badge = document.getElementById('chat-model-badge');
    if (!badge) return;
    if (modelId) {
        // Замена поврежденной кодировки на корректный emoji HuggingFace
        const label = modelId.startsWith('hf::') ? '🤗 ' + modelId.slice(4) : modelId;
        badge.textContent = label;
        badge.style.display = '';
    } else {
        badge.style.display = 'none';
    }
}

// updateModelStatus — заглушка для обратной совместимости
function updateModelStatus(message, type) {}

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
        
        if (response.ok && data.status === 'healthy') {
            if (data.foundry_status === 'healthy') {
                indicator.innerHTML = '<i class="bi bi-circle-fill text-success"></i> Connected';
            } else {
                indicator.innerHTML = '<i class="bi bi-circle-fill text-warning"></i> API Only';
            }
        } else {
            indicator.innerHTML = '<i class="bi bi-circle-fill text-danger"></i> Error';
        }
        
        updateSystemInfo(data);

        // Обновляем UI вкладки Foundry из тех же данных —
        // без отдельного запроса к /foundry/status
        if (data.foundry_status === 'healthy' && data.foundry_details) {
            updateFoundryStatus('running', {
                port: data.foundry_details.port,
                url: data.foundry_details.url
            });
        } else {
            updateFoundryStatus('stopped');
        }

    } catch (error) {
        console.error('System status check failed:', error);
        const indicator = document.getElementById('status-indicator');
        if (indicator) {
            indicator.innerHTML = '<i class="bi bi-circle-fill text-danger"></i> Offline';
        }
        
        const container = document.getElementById('system-status');
        if (container) {
            container.innerHTML = `
                <div class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle"></i><br>
                    <strong>Connection Error</strong><br>
                    <small>Cannot connect to API server</small>
                </div>
            `;
        }

        updateFoundryStatus('error');
    }
}

// Обновление информации о системе
function updateSystemInfo(data) {
    const container = document.getElementById('system-status');
    
    // Получаем реальный порт и URL из данных API
    let foundryUrl = 'Not connected';
    let foundryPort = 'Unknown';
    
    if (data.foundry_details) {
        if (data.foundry_details.url) {
            foundryUrl = data.foundry_details.url;
            CONFIG.foundry_url = foundryUrl; // Обновляем глобальную конфигурацию
        }
        if (data.foundry_details.port) {
            foundryPort = data.foundry_details.port;
        }
    }
    
    const foundryStatusText = data.foundry_status === 'healthy' ? 'Connected' : 
                             data.foundry_status === 'disconnected' ? 'Disconnected' :
                             data.foundry_status === 'error' ? 'Error' : 'Unknown';
    
    const foundryBadgeClass = data.foundry_status === 'healthy' ? 'bg-success' : 
                             data.foundry_status === 'disconnected' ? 'bg-warning' : 'bg-danger';
    
    container.innerHTML = `
        <div class="row">
            <div class="col-6">
                <strong>API:</strong><br>
                <span class="badge ${data.status === 'healthy' ? 'bg-success' : 'bg-danger'}">${data.status}</span>
            </div>
            <div class="col-6">
                <strong>Foundry:</strong><br>
                <span class="badge ${foundryBadgeClass}">${foundryStatusText}</span>
            </div>
            <div class="col-12 mt-2">
                <strong>Foundry URL:</strong><br>
                <small class="text-muted">${foundryUrl}</small>
            </div>
            <div class="col-12 mt-1">
                <strong>Port:</strong> <span class="badge bg-info">${foundryPort}</span>
                <strong class="ms-3">Models:</strong> <span class="badge bg-secondary">${data.models_count || 0}</span>
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
                                <button class="btn btn-sm btn-outline-danger" onclick="removeModel('${model.id}')">
                                    <i class="bi bi-trash"></i> Remove
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

// Очистка вывода примеров
function clearExampleOutput() {
    document.getElementById('example-output').innerHTML = `
        <div class="text-muted text-center mt-5">
            <i class="bi bi-play-circle" style="font-size: 2rem;"></i><br>
            Выберите пример SDK для запуска
        </div>
    `;
    document.getElementById('example-status').innerHTML = `
        <div class="text-muted text-center">
            <i class="bi bi-clock"></i><br>
            Ready to run SDK examples
        </div>
    `;
}

// Запуск SDK примеров
async function runSDKExample(type) {
    const outputDiv = document.getElementById('example-output');
    const statusDiv = document.getElementById('example-status');
    
    outputDiv.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><br>Запуск SDK примера...</div>';
    statusDiv.innerHTML = '<div class="text-warning"><i class="bi bi-play-circle"></i> Выполняется...</div>';
    
    try {
        let endpoint = '';
        let description = '';
        
        switch(type) {
            case 'basic':
                endpoint = '/api/v1/examples/sdk-basic';
                description = 'Основное использование SDK';
                break;
            case 'rag':
                endpoint = '/api/v1/examples/sdk-rag';
                description = 'RAG поиск через SDK';
                break;
            case 'batch':
                endpoint = '/api/v1/examples/sdk-batch';
                description = 'Пакетная генерация через SDK';
                break;
            case 'models':
                endpoint = '/api/v1/examples/sdk-models';
                description = 'Работа с моделями через SDK';
                break;
            default:
                throw new Error('Неизвестный тип примера');
        }
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            outputDiv.innerHTML = `
                <div class="mb-2"><strong>${description}</strong></div>
                <div class="mb-2"><small class="text-muted">Время выполнения: ${data.execution_time || 'N/A'}</small></div>
                <pre class="mb-0">${data.output || data.result || 'Пример выполнен успешно'}</pre>
            `;
            statusDiv.innerHTML = '<div class="text-success"><i class="bi bi-check-circle"></i> Выполнено успешно</div>';
        } else {
            outputDiv.innerHTML = `
                <div class="text-danger">
                    <strong>Ошибка выполнения примера:</strong><br>
                    <pre>${data.error || 'Неизвестная ошибка'}</pre>
                </div>
            `;
            statusDiv.innerHTML = '<div class="text-danger"><i class="bi bi-x-circle"></i> Ошибка выполнения</div>';
        }
    } catch (error) {
        outputDiv.innerHTML = `
            <div class="text-danger">
                <strong>Ошибка подключения:</strong><br>
                <pre>${error.message}</pre>
            </div>
        `;
        statusDiv.innerHTML = '<div class="text-danger"><i class="bi bi-x-circle"></i> Ошибка подключения</div>';
    }
}

// Функции для RAG вкладки
async function refreshRAGStatus() {
    try {
        const response = await fetch(`${API_BASE}/rag/status`);
        const data = await response.json();
        
        const statusDiv = document.getElementById('rag-status');
        const statsDiv = document.getElementById('rag-stats');
        
        if (data.success) {
            statusDiv.innerHTML = `
                <div class="row">
                    <div class="col-6">
                        <strong>Status:</strong><br>
                        <span class="badge ${data.enabled ? 'bg-success' : 'bg-secondary'}">${data.enabled ? 'Enabled' : 'Disabled'}</span>
                    </div>
                    <div class="col-6">
                        <strong>Documents:</strong><br>
                        <span class="badge bg-info">${data.total_chunks || 0}</span>
                    </div>
                </div>
            `;
            
            statsDiv.innerHTML = `
                <div class="mb-2">
                    <small>Index Directory:</small><br>
                    <code>${data.index_dir || './rag_index'}</code>
                </div>
                <div class="mb-2">
                    <small>Total Chunks:</small> <strong>${data.total_chunks || 0}</strong>
                </div>
                <div>
                    <small>Model:</small><br>
                    <code>${data.model || 'sentence-transformers/all-MiniLM-L6-v2'}</code>
                </div>
            `;
            
            // Загружаем значения в поля формы
            document.getElementById('rag-enabled').checked = data.enabled || false;
            document.getElementById('rag-index-dir').value = data.index_dir || './rag_index';
            document.getElementById('rag-model').value = data.model || 'sentence-transformers/all-MiniLM-L6-v2';
            document.getElementById('rag-chunk-size').value = data.chunk_size || 1000;
            document.getElementById('rag-top-k').value = data.top_k || 5;
        } else {
            statusDiv.innerHTML = '<div class="text-danger">Error loading RAG status</div>';
        }
    } catch (error) {
        document.getElementById('rag-status').innerHTML = '<div class="text-danger">Connection error</div>';
    }
}

async function saveRAGConfig() {
    const config = {
        enabled: document.getElementById('rag-enabled').checked,
        index_dir: document.getElementById('rag-index-dir').value || './rag_index',
        model: document.getElementById('rag-model').value || 'sentence-transformers/all-MiniLM-L6-v2',
        chunk_size: parseInt(document.getElementById('rag-chunk-size').value) || 1000,
        top_k: parseInt(document.getElementById('rag-top-k').value) || 5
    };
    
    try {
        const response = await fetch(`${API_BASE}/rag/config`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(config)
        });
        
        const data = await response.json();
        if (data.success) {
            showAlert('RAG configuration saved successfully', 'success');
            refreshRAGStatus();
        } else {
            showAlert(`Error: ${data.error}`, 'danger');
        }
    } catch (error) {
        showAlert('Error saving RAG config', 'danger');
        console.error('RAG config save error:', error);
    }
}

async function rebuildRAGIndex() {
    try {
        showAlert('Rebuilding RAG index...', 'info');
        const response = await fetch(`${API_BASE}/rag/rebuild`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.success) {
            showAlert('RAG index rebuilt successfully', 'success');
            refreshRAGStatus();
        } else {
            showAlert(`Error: ${data.error}`, 'danger');
        }
    } catch (error) {
        showAlert('Error rebuilding RAG index', 'danger');
    }
}

async function testRAGSearch() {
    const query = prompt('Enter search query:', 'FastAPI configuration');
    if (!query) return;
    
    try {
        const response = await fetch(`${API_BASE}/rag/search`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query, top_k: 3})
        });
        
        const data = await response.json();
        const resultsDiv = document.getElementById('rag-test-results');
        const outputDiv = document.getElementById('rag-search-output');
        
        if (data.success && data.results) {
            outputDiv.innerHTML = data.results.map((result, i) => `
                <div class="mb-2 p-2 border-bottom">
                    <strong>Result ${i + 1}:</strong> (Score: ${result.score?.toFixed(3) || 'N/A'})<br>
                    <small class="text-muted">${result.content?.substring(0, 200)}...</small>
                </div>
            `).join('');
            resultsDiv.style.display = 'block';
        } else {
            outputDiv.innerHTML = '<div class="text-muted">No results found</div>';
            resultsDiv.style.display = 'block';
        }
    } catch (error) {
        showAlert('Error testing RAG search', 'danger');
    }
}
// Очистка RAG chunks (оставляем для совместимости)
async function clearRAGChunks() {
    if (!confirm('Вы уверены, что хотите удалить все индексированные документы из RAG системы?\n\nЭто действие нельзя отменить.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/rag/clear`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message || 'RAG chunks успешно очищены', 'success');
            // Обновляем статус если находимся на RAG вкладке
            if (document.getElementById('rag-tab').classList.contains('active')) {
                setTimeout(refreshRAGStatus, 1000);
            }
        } else {
            showAlert(`Ошибка: ${data.error}`, 'danger');
        }
    } catch (error) {
        showAlert('Ошибка очистки RAG chunks', 'danger');
        console.error('Clear RAG chunks error:', error);
    }
}
// Обработка переключения RAG в Settings
function handleRAGToggle(checkbox) {
    // Предотвращаем множественные вызовы
    if (checkbox.disabled) return;
    
    checkbox.disabled = true;
    setTimeout(() => {
        checkbox.disabled = false;
    }, 2000);
    
    if (checkbox.checked) {
        showAlert('RAG System enabled. Save configuration to apply changes.', 'info');
    } else {
        showAlert('RAG System disabled. Save configuration to apply changes.', 'warning');
    }
}
// Экспорт конфигурации в JSON-файл
async function exportConfig() {
    try {
        const response = await fetch(`${API_BASE}/config/export`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        const filename = `fastapi-foundry-config-backup-${timestamp}.json`;

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
        // Уведомление об успешном экспорте
        showAlert('Конфигурация экспортирована успешно', 'success');
    } catch (error) {
        // Обработка ошибок экспорта
        console.error('Ошибка экспорта конфигурации:', error);
        showAlert('Ошибка при экспорте файла', 'danger');
    }
}

// Импорт конфигурации из JSON-файл
async function importConfig(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Сбрасываем input чтобы можно было загрузить тот же файл повторно
    event.target.value = '';

    try {
        const text = await file.text();
        const parsed = JSON.parse(text);

        const merge = confirm(
            `Импорт файла: ${file.name}\n\n` +
            `Нажмите OK — слияние с текущей конфигурацией\n` +
            `Нажмите Отмена — полная замена конфигурации`
        );

        const response = await fetch(`${API_BASE}/config/import`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ config: parsed, merge })
        });

        const result = await response.json();

        if (result.success) {
            showAlert(
                `Конфигурация импортирована. Разделы: ${result.sections_imported.join(', ')}`,
                'success'
            );
            loadConfigFields();
        } else {
// Удаление модели
async function removeModel(modelId) {
    if (!confirm(`Remove model ${modelId}?\n\nThis will unload the model from memory.`)) {
        return;
    }
    
    try {
        showAlert(`Removing model ${modelId}...`, 'info');
        
        const response = await fetch(`${API_BASE}/foundry/models/unload`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({model_id: modelId})
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(`Model ${modelId} removed successfully`, 'success');
            loadConnectedModels(); // Refresh models list
        } else {
            showAlert(`Error removing model: ${data.error}`, 'danger');
        }
    } catch (error) {
        showAlert(`Error removing model: ${error.message}`, 'danger');
    }
}


// ── Translation Tab — backed by /api/v1/translation/* ────────────────────────

const TRANS_CACHE = new Map();

const TRANS_PROVIDER_INFO = {
    llm: {
        hint: 'Uses the currently loaded AI model',
        info: '<strong>🤖 LLM Translation</strong><br><small>Sends text to the active AI model. No API key needed.</small><br><br><span class="badge bg-success">Free</span> <span class="badge bg-secondary">Local</span>'
    },
    deepl: {
        hint: 'Requires DeepL API key (free tier: 500K chars/month)',
        info: '<strong>🔵 DeepL API</strong><br><small>High-quality neural translation. Best for European languages.</small><br><br><a href="https://www.deepl.com/pro-api" target="_blank">Get free API key</a><br><br><span class="badge bg-primary">Best quality</span> <span class="badge bg-warning text-dark">API key required</span>'
    },
    google: {
        hint: 'Requires Google Cloud Translation API key',
        info: '<strong>🔴 Google Translate</strong><br><small>Fast, supports 100+ languages.</small><br><br><a href="https://cloud.google.com/translate" target="_blank">Google Cloud Console</a><br><br><span class="badge bg-info">100+ languages</span> <span class="badge bg-warning text-dark">API key required</span>'
    },
    helsinki: {
        hint: 'Helsinki-NLP local model — no API key, runs on CPU',
        info: '<strong>🟢 Helsinki-NLP (local)</strong><br><small>Open-source NMT via HuggingFace transformers. Load model in HuggingFace tab first.</small><br><br><span class="badge bg-success">Free</span> <span class="badge bg-secondary">Local</span>'
    }
};

function transOnProviderChange() {
    const provider = document.getElementById('trans-provider').value;
    const info = TRANS_PROVIDER_INFO[provider];
    document.getElementById('trans-provider-hint').textContent = info.hint;
    document.getElementById('trans-provider-info').innerHTML = info.info;
    document.getElementById('trans-api-key-row').style.display =
        (provider === 'deepl' || provider === 'google') ? '' : 'none';
}

function transSwapLangs() {
    const src = document.getElementById('trans-source-lang');
    const tgt = document.getElementById('trans-target-lang');
    const srcVal = src.value === 'auto' ? 'en' : src.value;
    const tgtVal = tgt.value;
    src.value = tgtVal;
    tgt.value = srcVal;
    const inp = document.getElementById('trans-input');
    const out = document.getElementById('trans-output');
    const tmp = inp.value;
    inp.value = out.value;
    out.value = tmp;
    transUpdateCharCount();
}

function transClear() {
    document.getElementById('trans-input').value = '';
    document.getElementById('trans-output').value = '';
    document.getElementById('trans-detected-lang').textContent = '';
    document.getElementById('trans-time').textContent = '';
    document.getElementById('trans-char-count').textContent = '0 chars';
    document.getElementById('trans-status').style.display = 'none';
}

function transUpdateCharCount() {
    const len = (document.getElementById('trans-input')?.value || '').length;
    const el = document.getElementById('trans-char-count');
    if (el) el.textContent = `${len} chars`;
}

function transCopyOutput() {
    const text = document.getElementById('trans-output').value;
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => showAlert('Copied to clipboard', 'success'));
}

function transUseinChat() {
    const text = document.getElementById('trans-output').value.trim();
    if (!text) { showAlert('No translation to use', 'warning'); return; }
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.value = text;
        document.getElementById('chat-tab')?.click();
        showAlert('Translation sent to Chat input', 'success');
    }
}

async function transDetectLang() {
    const text = document.getElementById('trans-input').value.trim();
    if (!text) { showAlert('Enter text first', 'warning'); return; }

    const cacheKey = 'detect:' + text.slice(0, 100);
    if (TRANS_CACHE.has(cacheKey)) {
        document.getElementById('trans-detected-lang').textContent = 'Detected: ' + TRANS_CACHE.get(cacheKey);
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/translation/detect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const data = await res.json();
        if (data.success) {
            const label = `${data.language_name} (${data.language})`;
            TRANS_CACHE.set(cacheKey, label);
            document.getElementById('trans-detected-lang').textContent = 'Detected: ' + label;
        } else {
            showAlert('Detection failed: ' + data.error, 'warning');
        }
    } catch (e) {
        showAlert('Detection failed: ' + e.message, 'danger');
    }
}

async function transTranslate() {
    const text = document.getElementById('trans-input').value.trim();
    if (!text) { showAlert('Enter text to translate', 'warning'); return; }

    const provider = document.getElementById('trans-provider').value;
    const srcLang  = document.getElementById('trans-source-lang').value;
    const tgtLang  = document.getElementById('trans-target-lang').value;
    const apiKey   = document.getElementById('trans-api-key')?.value?.trim() || '';
    const useCache = document.getElementById('trans-cache-enabled').checked;

    const cacheKey = `${provider}:${srcLang}:${tgtLang}:${text}`;
    if (useCache && TRANS_CACHE.has(cacheKey)) {
        document.getElementById('trans-output').value = TRANS_CACHE.get(cacheKey);
        document.getElementById('trans-time').textContent = 'cached';
        return;
    }

    const btn = document.getElementById('trans-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Translating...';
    document.getElementById('trans-status').style.display = 'none';

    try {
        const res = await fetch(`${API_BASE}/translation/translate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, provider, source_lang: srcLang, target_lang: tgtLang, api_key: apiKey })
        });
        const data = await res.json();

        if (data.success) {
            document.getElementById('trans-output').value = data.translated;
            document.getElementById('trans-time').textContent = (data.elapsed_ms / 1000).toFixed(2) + 's';
            if (useCache) TRANS_CACHE.set(cacheKey, data.translated);
        } else {
            const st = document.getElementById('trans-status');
            st.className = 'alert alert-danger p-2 mt-2';
            st.textContent = data.error;
            st.style.display = '';
        }
    } catch (e) {
        const st = document.getElementById('trans-status');
        st.className = 'alert alert-danger p-2 mt-2';
        st.textContent = e.message;
        st.style.display = '';
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-translate"></i> Translate';
    }
}

async function transSaveApiKey() {
    const provider = document.getElementById('trans-provider').value;
    const key = document.getElementById('trans-api-key').value.trim();
    if (!key) { showAlert('Enter API key first', 'warning'); return; }
    const envKey = provider === 'deepl' ? 'DEEPL_API_KEY' : 'GOOGLE_TRANSLATE_API_KEY';
    try {
        const res = await fetch('/api/v1/config/env', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key: envKey, value: key })
        });
        const data = await res.json();
        showAlert(data.success ? `${envKey} saved to .env` : data.error, data.success ? 'success' : 'danger');
    } catch (e) {
        showAlert('Error saving key: ' + e.message, 'danger');
    }
}

async function transBatch() {
    const lines = document.getElementById('trans-batch-input').value
        .split('\n').map(l => l.trim()).filter(Boolean);
    if (!lines.length) { showAlert('Enter lines to translate', 'warning'); return; }

    const btn = document.getElementById('trans-batch-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Translating...';

    try {
        const res = await fetch(`${API_BASE}/translation/batch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                texts:       lines,
                provider:    document.getElementById('trans-provider').value,
                source_lang: document.getElementById('trans-source-lang').value,
                target_lang: document.getElementById('trans-target-lang').value,
                api_key:     document.getElementById('trans-api-key')?.value?.trim() || '',
            })
        });
        const data = await res.json();

        const resDiv = document.getElementById('trans-batch-results');
        resDiv.innerHTML = (data.results || []).map((r, i) =>
            `<div class="mb-2 pb-2 border-bottom">
                <div class="text-muted" style="font-size:.8rem">${lines[i] || ''}</div>
                <div class="${r.success ? '' : 'text-danger'}">${r.success ? r.translated : r.error}</div>
            </div>`
        ).join('');
        document.getElementById('trans-batch-output').style.display = '';

        const msg = data.failed > 0
            ? `Batch done: ${data.total - data.failed}/${data.total} succeeded`
            : `Batch done: ${data.total} translated in ${(data.elapsed_ms / 1000).toFixed(1)}s`;
        showAlert(msg, data.failed > 0 ? 'warning' : 'success');

    } catch (e) {
        showAlert('Batch error: ' + e.message, 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-layers"></i> Translate All';
    }
}

function transClearBatch() {
    document.getElementById('trans-batch-input').value = '';
    document.getElementById('trans-batch-output').style.display = 'none';
}

// Init Translation tab + chat injection
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('trans-input')?.addEventListener('input', transUpdateCharCount);

    document.getElementById('translation-tab')?.addEventListener('shown.bs.tab', async () => {
        transOnProviderChange();
        // Загружаем статус провайдеров с бэкенда
        try {
            const d = await fetch(`${API_BASE}/translation/providers`).then(r => r.json());
            if (d.success) {
                const sel = document.getElementById('trans-provider');
                d.providers.forEach(p => {
                    const opt = sel.querySelector(`option[value="${p.id}"]`);
                    if (!opt) return;
                    // Убираем старые маркеры
                    opt.textContent = opt.textContent.replace(' (key missing)', '').replace(' \u2713', '');
                    if (p.requires_key && !p.available)
                        opt.textContent += ' (key missing)';
                    else if (p.available && !p.requires_key)
                        opt.textContent += ' \u2713';
                });
            }
        } catch (_) {}
    });

    // Patch sendMessage: translate chat input to EN via backend before sending
    const origSend = window.sendMessage;
    if (origSend) {
        window.sendMessage = async function() {
            const inject = document.getElementById('trans-chat-inject')?.checked;
            if (!inject) return origSend();
            const input = document.getElementById('chat-input');
            const text = input?.value?.trim();
            if (!text) return origSend();
            try {
                const res = await fetch(`${API_BASE}/translation/translate-for-model`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text,
                        provider:    document.getElementById('trans-provider')?.value || 'llm',
                        source_lang: 'auto',
                    })
                });
                const data = await res.json();
                if (data.success && data.was_translated && input)
                    input.value = data.translated;
            } catch (e) {
                console.warn('Translation injection failed:', e.message);
            }
            return origSend();
        };
    }
});
