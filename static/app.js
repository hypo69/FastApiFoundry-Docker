// FastAPI Foundry Web Interface with Logging
const API_BASE = window.location.origin + '/api/v1';

console.log('FastAPI Foundry Web Interface loaded');
console.log('API_BASE:', API_BASE);

// Logger для веб-интерфейса
const WebLogger = {
    log: (level, message, data = null) => {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            message,
            data,
            source: 'web-ui'
        };
        
        console.log(`[${timestamp}] [${level}] ${message}`, data || '');
        
        // Отправка логов на сервер
        fetch(`${API_BASE}/logs/web`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(logEntry)
        }).catch(e => console.error('Failed to send log:', e));
    },
    
    info: (msg, data) => WebLogger.log('INFO', msg, data),
    error: (msg, data) => WebLogger.log('ERROR', msg, data),
    warning: (msg, data) => WebLogger.log('WARNING', msg, data),
    debug: (msg, data) => WebLogger.log('DEBUG', msg, data)
};

// Global state
let connectedModels = [];
let chatHistory = [];

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    WebLogger.info('Web interface initialized');
    checkSystemStatus();
    loadConnectedModels();
    loadSystemConfig();
    setInterval(checkSystemStatus, 30000);
    
    // Initialize logs tab
    initializeLogsTab();
    
    // Initialize Foundry tab
    initializeFoundryTab();
});

// System Status
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
            WebLogger.info('System status: healthy');
        } else {
            indicator.innerHTML = '<i class="bi bi-circle-fill text-danger"></i> Offline';
            WebLogger.warning('System status: unhealthy', data);
        }
        
        updateSystemStatus(data);
    } catch (error) {
        document.getElementById('status-indicator').innerHTML = '<i class="bi bi-circle-fill text-danger"></i> Error';
        WebLogger.error('Status check failed', error.message);
    }
}

function updateSystemStatus(data) {
    const statusContainer = document.getElementById('system-status');
    statusContainer.innerHTML = `
        <div class="row">
            <div class="col-6">
                <strong>API Status:</strong><br>
                <span class="badge ${data.status === 'healthy' ? 'bg-success' : 'bg-danger'}">${data.status}</span>
            </div>
            <div class="col-6">
                <strong>Foundry:</strong><br>
                <span class="badge ${data.foundry_status === 'healthy' ? 'bg-success' : 'bg-warning'}">${data.foundry_status === 'healthy' ? 'Connected' : 'Disconnected'}</span>
            </div>
            <div class="col-6 mt-2">
                <strong>RAG System:</strong><br>
                <span class="badge ${data.rag_loaded ? 'bg-success' : 'bg-warning'}">${data.rag_loaded ? 'Loaded' : 'Not Loaded'}</span>
            </div>
            <div class="col-6 mt-2">
                <strong>RAG Chunks:</strong><br>
                <span class="text-muted">${data.rag_chunks || 0}</span>
            </div>
        </div>
        <hr>
        <small class="text-muted">Last updated: ${new Date(data.timestamp).toLocaleString()}</small>
    `;
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    WebLogger.info('Sending message', {length: message.length});
    
    addMessageToChat('user', message);
    input.value = '';
    
    const typingId = addMessageToChat('assistant', '<i class="bi bi-three-dots"></i> Typing...');
    
    try {
        const requestData = {
            prompt: message,
            model: document.getElementById('chat-model').value || undefined,
            temperature: parseFloat(document.getElementById('temperature').value),
            max_tokens: parseInt(document.getElementById('max-tokens').value),
            use_rag: document.getElementById('use-rag').checked
        };
        
        console.log('Request data:', requestData);
        
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(requestData)
        });
        
        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Response data:', data);
        
        document.getElementById(typingId).remove();
        
        if (data.success && data.content) {
            addMessageToChat('assistant', data.content);
            WebLogger.info('Message generated successfully', {
                tokens: data.tokens_used,
                model: data.model
            });
        } else {
            const errorMsg = data.error || 'Failed to generate response';
            if (errorMsg.includes('Foundry') || errorMsg.includes('connection')) {
                addMessageToChat('assistant', `❌ Foundry AI недоступен. Проверьте подключение к серверу Foundry на порту 50477.`);
            } else {
                addMessageToChat('assistant', `❌ Error: ${errorMsg}`);
            }
            WebLogger.error('Message generation failed', data);
        }
    } catch (error) {
        document.getElementById(typingId).remove();
        addMessageToChat('assistant', '❌ Connection error');
        WebLogger.error('Message request failed', error.message);
    }
}

function addMessageToChat(role, content) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageId = 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    
    if (messagesContainer.children.length === 1 && messagesContainer.children[0].classList.contains('text-muted')) {
        messagesContainer.innerHTML = '';
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `<div class="content">${content}</div>`;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return messageId;
}

function showAlert(message, type = 'info') {
    WebLogger.info(`Alert shown: ${type}`, message);
    
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

async function loadConnectedModels() {
    try {
        const response = await fetch(`${API_BASE}/models`);
        const data = await response.json();
        
        if (data.success && data.models) {
            connectedModels = data.models;
            WebLogger.info('Models loaded', {count: connectedModels.length, models: connectedModels.map(m => m.id)});
            
            // Обновить выпадающий список моделей в чате
            updateModelSelect();
        } else {
            WebLogger.error('Failed to load models', data.error);
            connectedModels = [];
        }
    } catch (error) {
        WebLogger.error('Failed to load models', error.message);
        connectedModels = [];
    }
}

function updateModelSelect() {
    const modelSelect = document.getElementById('chat-model');
    if (modelSelect && connectedModels.length > 0) {
        modelSelect.innerHTML = '<option value="">Auto-select</option>';
        
        connectedModels.forEach(model => {
            const option = document.createElement('option');
            option.value = model.id;
            option.textContent = model.id;
            modelSelect.appendChild(option);
        });
        
        WebLogger.info('Model select updated', {count: connectedModels.length});
    }
}

async function loadSystemConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();
        WebLogger.info('Config loaded', data);
    } catch (error) {
        WebLogger.error('Failed to load config', error.message);
    }
}
// Missing functions for HTML buttons
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
    loadConnectedModels();
}

// ===== FOUNDRY MANAGEMENT =====

function initializeFoundryTab() {
    // Check Foundry status when tab is shown
    document.getElementById('foundry-tab').addEventListener('shown.bs.tab', function() {
        checkFoundryStatus();
    });
    
    // Initial status check
    setTimeout(() => {
        checkFoundryStatus();
    }, 1000);
}

function startFoundryService() {
    const btn = document.getElementById('start-foundry-btn');
    const originalText = btn.innerHTML;
    
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Starting...';
    btn.disabled = true;
    
    addFoundryLog('INFO', 'Starting Foundry service...');
    
    fetch(`${API_BASE}/foundry/start`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addFoundryLog('SUCCESS', 'Foundry service started successfully');
            updateFoundryStatus('running');
            showAlert('Foundry service started', 'success');
        } else {
            addFoundryLog('ERROR', `Failed to start Foundry: ${data.error}`);
            showAlert(`Failed to start Foundry: ${data.error}`, 'danger');
        }
    })
    .catch(error => {
        addFoundryLog('ERROR', `Connection error: ${error.message}`);
        showAlert('Failed to connect to API', 'danger');
    })
    .finally(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
}

function stopFoundryService() {
    const btn = document.getElementById('stop-foundry-btn');
    const originalText = btn.innerHTML;
    
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Stopping...';
    btn.disabled = true;
    
    addFoundryLog('INFO', 'Stopping Foundry service...');
    
    fetch(`${API_BASE}/foundry/stop`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addFoundryLog('SUCCESS', 'Foundry service stopped');
            updateFoundryStatus('stopped');
            showAlert('Foundry service stopped', 'info');
        } else {
            addFoundryLog('ERROR', `Failed to stop Foundry: ${data.error}`);
            showAlert(`Failed to stop Foundry: ${data.error}`, 'danger');
        }
    })
    .catch(error => {
        addFoundryLog('ERROR', `Connection error: ${error.message}`);
        showAlert('Failed to connect to API', 'danger');
    })
    .finally(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
}

function checkFoundryStatus() {
    addFoundryLog('INFO', 'Checking Foundry status...');
    
    fetch(`${API_BASE}/foundry/status`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const status = data.status;
            addFoundryLog('INFO', `Foundry status: ${status}`);
            updateFoundryStatus(status);
            
            if (data.models && data.models.length > 0) {
                addFoundryLog('INFO', `Available models: ${data.models.join(', ')}`);
            }
        } else {
            addFoundryLog('ERROR', `Status check failed: ${data.error}`);
            updateFoundryStatus('error');
        }
    })
    .catch(error => {
        addFoundryLog('ERROR', `Connection error: ${error.message}`);
        updateFoundryStatus('offline');
    });
}

function updateFoundryStatus(status) {
    const statusBadge = document.getElementById('foundry-service-status');
    const infoDiv = document.getElementById('foundry-service-info');
    const startBtn = document.getElementById('start-foundry-btn');
    const stopBtn = document.getElementById('stop-foundry-btn');
    
    let badgeClass, statusText, infoText;
    
    switch (status) {
        case 'running':
        case 'healthy':
            badgeClass = 'bg-success';
            statusText = 'Running';
            infoText = 'Foundry service is running on port 50477';
            startBtn.style.display = 'none';
            stopBtn.style.display = 'block';
            break;
        case 'stopped':
        case 'not_installed':
        default:
            badgeClass = 'bg-secondary';
            statusText = 'Stopped';
            infoText = 'Foundry service is not running';
            startBtn.style.display = 'block';
            stopBtn.style.display = 'none';
            break;
        case 'error':
            badgeClass = 'bg-danger';
            statusText = 'Error';
            infoText = 'Foundry service encountered an error';
            startBtn.style.display = 'block';
            stopBtn.style.display = 'none';
            break;
    }
    
    statusBadge.className = `badge ${badgeClass}`;
    statusBadge.textContent = statusText;
    infoDiv.innerHTML = `<small>${infoText}</small>`;
}

function addFoundryLog(level, message) {
    const logsContainer = document.getElementById('foundry-logs');
    const timestamp = new Date().toLocaleTimeString();
    
    // Clear placeholder if it exists
    if (logsContainer.querySelector('.text-muted.text-center')) {
        logsContainer.innerHTML = '';
    }
    
    const logEntry = document.createElement('div');
    logEntry.className = 'foundry-log-entry';
    
    let levelClass, levelIcon;
    switch (level) {
        case 'SUCCESS':
            levelClass = 'text-success';
            levelIcon = '✅';
            break;
        case 'ERROR':
            levelClass = 'text-danger';
            levelIcon = '❌';
            break;
        case 'WARNING':
            levelClass = 'text-warning';
            levelIcon = '⚠️';
            break;
        default:
            levelClass = 'text-info';
            levelIcon = 'ℹ️';
            break;
    }
    
    logEntry.innerHTML = `
        <span class="text-muted">[${timestamp}]</span>
        <span class="${levelClass}">${levelIcon} ${level}:</span>
        <span>${message}</span>
    `;
    
    logsContainer.appendChild(logEntry);
    logsContainer.scrollTop = logsContainer.scrollHeight;
    
    // Keep only last 100 entries
    const entries = logsContainer.querySelectorAll('.foundry-log-entry');
    if (entries.length > 100) {
        entries[0].remove();
    }
}

function clearFoundryLogs() {
    document.getElementById('foundry-logs').innerHTML = `
        <div class="text-muted text-center mt-5">
            <i class="bi bi-terminal"></i><br>
            Foundry logs cleared
        </div>
    `;
}

function listFoundryModels() {
    loadConnectedModels();
}

function downloadAndRunModel() {
    showAlert('Model download not implemented', 'info');
}

function showModelInfo() {
    showAlert('Model info not implemented', 'info');
}

function loadDocumentation() {
    showAlert('Documentation loading not implemented', 'info');
}

function addModel() {
    showAlert('Add model not implemented', 'info');
}

function updateProviderFields() {
    // Provider field updates not implemented
}

// ===== LOGS FUNCTIONALITY =====

let logsData = [];
let logsAutoRefresh = null;

function initializeLogsTab() {
    // Load logs when tab is shown
    document.getElementById('logs-tab').addEventListener('shown.bs.tab', function() {
        loadLogsData();
        loadSystemHealth();
        loadErrorSummary();
        loadPerformanceMetrics();
        
        // Auto-refresh logs every 10 seconds
        if (logsAutoRefresh) clearInterval(logsAutoRefresh);
        logsAutoRefresh = setInterval(() => {
            refreshLogs();
            loadSystemHealth();
        }, 10000);
    });
    
    // Stop auto-refresh when leaving logs tab
    document.getElementById('logs-tab').addEventListener('hidden.bs.tab', function() {
        if (logsAutoRefresh) {
            clearInterval(logsAutoRefresh);
            logsAutoRefresh = null;
        }
    });
}

async function loadLogsData() {
    try {
        const response = await fetch(`${API_BASE}/logs/recent?limit=100`);
        const data = await response.json();
        
        if (data.success) {
            logsData = data.data.logs || [];
            displayLogs(logsData);
            WebLogger.info('Logs loaded', {count: logsData.length});
        } else {
            showLogsError('Failed to load logs: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        showLogsError('Error loading logs: ' + error.message);
        WebLogger.error('Failed to load logs', error.message);
    }
}

function displayLogs(logs) {
    const container = document.getElementById('logs-container');
    
    if (!logs || logs.length === 0) {
        container.innerHTML = `
            <div class="text-muted text-center p-4">
                <i class="bi bi-file-text"></i><br>
                No logs available
            </div>
        `;
        return;
    }
    
    const logsHtml = logs.map(log => {
        const timestamp = new Date(log.timestamp).toLocaleString();
        const levelClass = `log-${log.level}`;
        
        return `
            <div class="log-entry ${levelClass}">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <span class="log-timestamp">${timestamp}</span>
                        <span class="log-logger ms-2">[${log.logger}]</span>
                        <span class="badge badge-sm bg-${getLevelBadgeColor(log.level)} ms-2">${log.level.toUpperCase()}</span>
                    </div>
                </div>
                <div class="mt-1">${escapeHtml(log.message)}</div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = logsHtml;
    container.scrollTop = container.scrollHeight;
}

function getLevelBadgeColor(level) {
    switch (level) {
        case 'debug': return 'secondary';
        case 'info': return 'primary';
        case 'warning': return 'warning';
        case 'error': return 'danger';
        default: return 'secondary';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function filterLogs() {
    const levelFilter = document.getElementById('log-level-filter').value;
    
    if (!levelFilter) {
        displayLogs(logsData);
        return;
    }
    
    const filteredLogs = logsData.filter(log => log.level === levelFilter);
    displayLogs(filteredLogs);
    
    WebLogger.info('Logs filtered', {level: levelFilter, count: filteredLogs.length});
}

function refreshLogs() {
    loadLogsData();
}

function clearLogsView() {
    document.getElementById('logs-container').innerHTML = `
        <div class="text-muted text-center p-4">
            <i class="bi bi-file-text"></i><br>
            Logs cleared
        </div>
    `;
    logsData = [];
}

async function loadSystemHealth() {
    try {
        const response = await fetch(`${API_BASE}/logs/health`);
        const data = await response.json();
        
        if (data.success) {
            displaySystemHealth(data.data);
        } else {
            showHealthError('Failed to load system health');
        }
    } catch (error) {
        showHealthError('Error loading system health: ' + error.message);
    }
}

function displaySystemHealth(health) {
    const container = document.getElementById('logs-health-status');
    const statusClass = `health-status-${health.status}`;
    const statusIcon = getHealthIcon(health.status);
    
    container.innerHTML = `
        <div class="text-center mb-3">
            <i class="bi ${statusIcon} ${statusClass}" style="font-size: 2rem;"></i>
            <div class="mt-2">
                <span class="badge bg-${getHealthBadgeColor(health.status)} fs-6">${health.status.toUpperCase()}</span>
            </div>
        </div>
        <div class="row text-center">
            <div class="col-6">
                <div class="text-danger fw-bold">${health.metrics.errors_count}</div>
                <small class="text-muted">Errors</small>
            </div>
            <div class="col-6">
                <div class="text-warning fw-bold">${health.metrics.warnings_count}</div>
                <small class="text-muted">Warnings</small>
            </div>
            <div class="col-6 mt-2">
                <div class="text-primary fw-bold">${health.metrics.api_requests}</div>
                <small class="text-muted">API Requests</small>
            </div>
            <div class="col-6 mt-2">
                <div class="text-info fw-bold">${health.metrics.active_models}</div>
                <small class="text-muted">Models</small>
            </div>
        </div>
        <hr>
        <small class="text-muted">Last hour • ${new Date(health.timestamp).toLocaleTimeString()}</small>
    `;
}

function getHealthIcon(status) {
    switch (status) {
        case 'healthy': return 'bi-check-circle-fill';
        case 'warning': return 'bi-exclamation-triangle-fill';
        case 'critical': return 'bi-x-circle-fill';
        default: return 'bi-question-circle-fill';
    }
}

function getHealthBadgeColor(status) {
    switch (status) {
        case 'healthy': return 'success';
        case 'warning': return 'warning';
        case 'critical': return 'danger';
        default: return 'secondary';
    }
}

async function loadErrorSummary() {
    try {
        const response = await fetch(`${API_BASE}/logs/errors?hours=24`);
        const data = await response.json();
        
        if (data.success) {
            displayErrorSummary(data.data);
        } else {
            showErrorSummaryError('Failed to load error summary');
        }
    } catch (error) {
        showErrorSummaryError('Error loading error summary: ' + error.message);
    }
}

function displayErrorSummary(summary) {
    const container = document.getElementById('error-summary');
    
    if (summary.total_errors === 0) {
        container.innerHTML = `
            <div class="text-center text-success">
                <i class="bi bi-check-circle" style="font-size: 2rem;"></i>
                <div class="mt-2">No errors in 24h</div>
            </div>
        `;
        return;
    }
    
    const topErrorTypes = Object.entries(summary.error_types || {})
        .slice(0, 3)
        .map(([type, count]) => `<div class="d-flex justify-content-between"><span>${type}</span><span class="badge bg-danger">${count}</span></div>`)
        .join('');
    
    container.innerHTML = `
        <div class="text-center mb-3">
            <div class="text-danger fw-bold" style="font-size: 1.5rem;">${summary.total_errors}</div>
            <small class="text-muted">Total Errors</small>
        </div>
        <div class="mb-3">
            <h6 class="text-muted mb-2">Top Error Types:</h6>
            ${topErrorTypes || '<div class="text-muted">No error types data</div>'}
        </div>
        <hr>
        <small class="text-muted">Last 24 hours</small>
    `;
}

async function loadPerformanceMetrics() {
    try {
        const response = await fetch(`${API_BASE}/logs/performance?hours=24`);
        const data = await response.json();
        
        if (data.success) {
            displayPerformanceMetrics(data.data);
        } else {
            showPerformanceError('Failed to load performance metrics');
        }
    } catch (error) {
        showPerformanceError('Error loading performance metrics: ' + error.message);
    }
}

function displayPerformanceMetrics(metrics) {
    const container = document.getElementById('performance-metrics');
    const api = metrics.api_performance || {};
    const models = metrics.model_performance || {};
    
    container.innerHTML = `
        <div class="row text-center mb-3">
            <div class="col-6">
                <div class="text-primary fw-bold">${api.total_requests || 0}</div>
                <small class="text-muted">API Requests</small>
            </div>
            <div class="col-6">
                <div class="text-info fw-bold">${(api.avg_response_time || 0).toFixed(3)}s</div>
                <small class="text-muted">Avg Response</small>
            </div>
        </div>
        <div class="mb-3">
            <h6 class="text-muted mb-2">Models:</h6>
            <div class="text-center">
                <div class="text-success fw-bold">${Object.keys(models.models || {}).length}</div>
                <small class="text-muted">Active Models</small>
            </div>
        </div>
        <hr>
        <small class="text-muted">Last 24 hours</small>
    `;
}

function showLogsError(message) {
    document.getElementById('logs-container').innerHTML = `
        <div class="text-danger text-center p-4">
            <i class="bi bi-exclamation-triangle"></i><br>
            ${message}
        </div>
    `;
}

function showHealthError(message) {
    document.getElementById('logs-health-status').innerHTML = `
        <div class="text-danger text-center">
            <i class="bi bi-exclamation-triangle"></i><br>
            <small>${message}</small>
        </div>
    `;
}

function showErrorSummaryError(message) {
    document.getElementById('error-summary').innerHTML = `
        <div class="text-danger text-center">
            <i class="bi bi-exclamation-triangle"></i><br>
            <small>${message}</small>
        </div>
    `;
}

function showPerformanceError(message) {
    document.getElementById('performance-metrics').innerHTML = `
        <div class="text-danger text-center">
            <i class="bi bi-exclamation-triangle"></i><br>
            <small>${message}</small>
        </div>
    `;
}

// ===== EXAMPLES FUNCTIONALITY =====

let currentExampleProcess = null;

async function runExample(exampleType) {
    if (currentExampleProcess) {
        showAlert('Another example is already running', 'warning');
        return;
    }
    
    const outputContainer = document.getElementById('example-output');
    const statusContainer = document.getElementById('example-status');
    
    // Clear output and show loading
    outputContainer.innerHTML = `
        <div class="text-center text-primary">
            <div class="spinner-border" role="status"></div>
            <div class="mt-2">Running ${getExampleName(exampleType)}...</div>
        </div>
    `;
    
    statusContainer.innerHTML = `
        <div class="text-center text-primary">
            <div class="spinner-border spinner-border-sm" role="status"></div>
            <div class="mt-2">Running...</div>
        </div>
    `;
    
    WebLogger.info('Starting example', {type: exampleType});
    
    try {
        const response = await fetch(`${API_BASE}/examples/run`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({example_type: exampleType})
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayExampleOutput(data.output, data.execution_time);
            statusContainer.innerHTML = `
                <div class="text-center text-success">
                    <i class="bi bi-check-circle"></i>
                    <div class="mt-2">Completed in ${data.execution_time.toFixed(2)}s</div>
                </div>
            `;
            WebLogger.info('Example completed', {type: exampleType, time: data.execution_time});
        } else {
            displayExampleError(data.error || 'Unknown error');
            statusContainer.innerHTML = `
                <div class="text-center text-danger">
                    <i class="bi bi-x-circle"></i>
                    <div class="mt-2">Failed</div>
                </div>
            `;
            WebLogger.error('Example failed', {type: exampleType, error: data.error});
        }
    } catch (error) {
        displayExampleError('Connection error: ' + error.message);
        statusContainer.innerHTML = `
            <div class="text-center text-danger">
                <i class="bi bi-x-circle"></i>
                <div class="mt-2">Error</div>
            </div>
        `;
        WebLogger.error('Example request failed', {type: exampleType, error: error.message});
    } finally {
        currentExampleProcess = null;
    }
}

function getExampleName(exampleType) {
    const names = {
        'client': 'API Client Demo',
        'rag': 'RAG Search Demo',
        'mcp': 'MCP Client Demo',
        'model': 'Model Client Demo'
    };
    return names[exampleType] || 'Unknown Example';
}

function displayExampleOutput(output, executionTime) {
    const container = document.getElementById('example-output');
    
    // Format output with timestamps and colors
    const formattedOutput = output
        .split('\n')
        .map(line => {
            if (line.includes('ERROR') || line.includes('❌')) {
                return `<div class="text-danger">${escapeHtml(line)}</div>`;
            } else if (line.includes('WARNING') || line.includes('⚠️')) {
                return `<div class="text-warning">${escapeHtml(line)}</div>`;
            } else if (line.includes('SUCCESS') || line.includes('✅')) {
                return `<div class="text-success">${escapeHtml(line)}</div>`;
            } else if (line.includes('INFO') || line.includes('🔍') || line.includes('📊')) {
                return `<div class="text-info">${escapeHtml(line)}</div>`;
            } else {
                return `<div>${escapeHtml(line)}</div>`;
            }
        })
        .join('');
    
    container.innerHTML = `
        <div class="mb-2">
            <small class="text-muted">Execution time: ${executionTime.toFixed(2)}s</small>
            <hr>
        </div>
        ${formattedOutput}
    `;
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function displayExampleError(error) {
    const container = document.getElementById('example-output');
    container.innerHTML = `
        <div class="text-center text-danger mt-5">
            <i class="bi bi-exclamation-triangle" style="font-size: 2rem;"></i><br>
            <div class="mt-2">Example Failed</div>
            <div class="mt-2"><small>${escapeHtml(error)}</small></div>
        </div>
    `;
}

function clearExampleOutput() {
    document.getElementById('example-output').innerHTML = `
        <div class="text-muted text-center mt-5">
            <i class="bi bi-play-circle" style="font-size: 2rem;"></i><br>
            Выберите пример для запуска
        </div>
    `;
    
    document.getElementById('example-status').innerHTML = `
        <div class="text-muted text-center">
            <i class="bi bi-clock"></i><br>
            Ready to run examples
        </div>
    `;
}