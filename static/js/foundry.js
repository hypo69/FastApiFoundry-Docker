/**
 * Название процесса: Интеграция с Foundry AI
 * Описание: Проверка статуса системы, управление локальными моделями и автозагрузка.
 * Version: 0.4.1
 * Date: 17 апреля 2026
 */

import { showAlert, updateModelStatus, updateChatModelBadge } from './ui.js';

// Проверка статуса системы (API и Foundry)
export async function checkSystemStatus() {
    try {
        const response = await fetch(`${window.API_BASE}/health`);
        const data = await response.json();
        
        // Update top-right status indicator
        const indicator = document.getElementById('status-indicator');
        if (indicator) {
            if (response.ok && data.status === 'healthy') {
                indicator.innerHTML = data.foundry_status === 'healthy' 
                    ? '<i class="bi bi-circle-fill text-success"></i> Connected'
                    : '<i class="bi bi-circle-fill text-warning"></i> API Only';
                indicator.className = 'navbar-text'; // Reset class
            } else {
                indicator.innerHTML = '<i class="bi bi-circle-fill text-danger"></i> Error';
                indicator.className = 'navbar-text text-danger'; // Add error class
            }
            if (data.foundry_details?.port) {
                indicator.title = `Foundry Port: ${data.foundry_details.port}`;
            }
        }
        
        updateSystemInfo(data);
        
        // Обновление состояния вкладки Foundry
        if (data.foundry_status === 'healthy' && data.foundry_details) {
            updateFoundryStatus('running', {
                port: data.foundry_details.port,
                url: data.foundry_details.url,
                default_model: window.CONFIG?.default_model
            });
        } else {
            updateFoundryStatus('stopped');
        }

        // Update status bar in control.html (if present)
        const apiStatusEl = document.getElementById('api-status');
        if (apiStatusEl) apiStatusEl.className = data.status === 'healthy' ? 'status-value status-online' : 'status-value status-offline';
        const foundryStatusEl = document.getElementById('foundry-status');
        if (foundryStatusEl) foundryStatusEl.className = data.foundry_status === 'healthy' ? 'status-value status-online' : 'status-value status-offline';
        const modelsCountEl = document.getElementById('models-count');
        if (modelsCountEl) modelsCountEl.textContent = data.models_count || 0;

        if (window.addLog) window.addLog(`✅ API: ${data.status}, Foundry: ${data.foundry_status}, Models: ${data.models_count || 0}`);
    } catch (error) {
        // Update top-right status indicator on connection error
        console.error('System status check failed:', error);
        updateFoundryStatus('offline');
    }
}

// Обновление текстовой информации о системе в UI
export function updateSystemInfo(data) {
    const container = document.getElementById('system-status');
    if (!container) return;

    const foundryStatusText = data.foundry_status === 'healthy' ? 'Connected' : 'Disconnected';
    const foundryBadgeClass = data.foundry_status === 'healthy' ? 'bg-success' : 'bg-warning';
    
    container.innerHTML = `
        <div class="row">
            <div class="col-6"><strong>API:</strong> <span class="badge ${data.status === 'healthy' ? 'bg-success' : 'bg-danger'}">${data.status}</span></div>
            <div class="col-6"><strong>Foundry:</strong> <span class="badge ${foundryBadgeClass}">${foundryStatusText}</span></div>
            <div class="col-12 mt-2"><small class="text-muted">URL: ${data.foundry_details?.url || 'N/A'}</small></div>
        </div>
    `;
}

// Проверка доступности модели по умолчанию
export async function validateDefaultModel() {
    try {
        const response = await fetch(`${window.API_BASE}/foundry/models/loaded`);
        const data = await response.json();
        
        if (data.success && data.models) {
            const availableModels = data.models.map(m => m.id);
            const defModel = window.CONFIG.default_model;

            if (defModel && availableModels.includes(defModel)) {
                updateModelStatus(`Модель: ${defModel}`, 'success');
            } else if (availableModels.length > 0) {
                updateModelStatus(`Доступна модель: ${availableModels[0]}`, 'info');
            } else {
                updateModelStatus('Модели не загружены', 'warning');
            }
        }
    } catch (error) {
        console.error('Error validating default model:', error);
    }
}

// Загрузка модели по умолчанию через Foundry
export async function loadDefaultModel() {
    try {
        showAlert('Загрузка модели по умолчанию...', 'info');
        const response = await fetch(`${window.API_BASE}/foundry/models/auto-load-default`, { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            showAlert(data.message, 'success');
            setTimeout(() => { validateDefaultModel(); }, 3000);
        }
    } catch (error) {
        showAlert('Ошибка загрузки модели', 'danger');
    }
}

// Переход к списку доступных моделей
export function showAvailableModels() {
    const foundryTab = document.getElementById('foundry-tab');
    if (foundryTab) {
        foundryTab.click();
        setTimeout(() => listFoundryModels(), 100);
    }
}

// Запрос списка моделей от Foundry
export async function listFoundryModels() {
    try {
        showAlert('Запрос списка моделей Foundry...', 'info');
        const response = await fetch(`${window.API_BASE}/foundry/models`);
        const data = await response.json();
        
        if (data.success && data.models) {
            const listEl = document.getElementById('foundry-models-list');
            if (listEl) {
                listEl.innerHTML = data.models.map(m => `
                    <div class="d-flex align-items-center justify-content-between px-3 py-2 border-bottom">
                        <div>
                            <strong style="font-size:.85rem">${m.name || m.id}</strong>
                            <small class="text-muted d-block">${m.description || ''}</small>
                        </div>
                        <button class="btn btn-sm btn-outline-success" onclick="selectFoundryModel('${m.id}')">
                            Use
                        </button>
                    </div>
                `).join('');
            }
            showAlert(`Получено моделей: ${data.models.length}`, 'success');
        } else {
            showAlert(`Ошибка получения моделей: ${data.error || 'Неизвестная ошибка'}`, 'danger');
        }
    } catch (error) {
        console.error('Сбой при запросе списка моделей Foundry:', error);
        showAlert('Не удалось связаться с API Foundry', 'danger');
    }
}

// Обновление индикатора статуса Foundry
export function updateFoundryStatus(status, details = {}) {
    // Navbar info
    const el = document.getElementById('foundry-status-info');
    if (el) {
        switch(status) {
            case 'running':
                el.innerHTML = `<span class="text-success"><i class="bi bi-play-fill"></i> Running on ${details.url}</span>`;
                break;
            case 'stopped':
                el.innerHTML = `<span class="text-warning"><i class="bi bi-stop-fill"></i> Stopped</span>`;
                break;
            default:
                el.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-triangle"></i> Offline</span>`;
        }
    }

    // Foundry Service card badges
    const badge = document.getElementById('foundry-service-status');
    const portBadge = document.getElementById('foundry-port-indicator');
    const infoEl = document.getElementById('foundry-service-info');

    if (status === 'running') {
        if (badge) { badge.className = 'badge bg-success'; badge.textContent = 'Running'; }
        if (portBadge) { portBadge.className = 'badge bg-info me-2'; portBadge.textContent = `Port: ${details.port || '?'}`; }
        if (infoEl) infoEl.innerHTML = `
            <div class="d-flex flex-column gap-1">
                <span><i class="bi bi-circle-fill text-success"></i> <strong>Foundry запущен</strong></span>
                <span class="text-muted"><small>URL: ${details.url || 'N/A'}</small></span>
                <span class="text-muted"><small>Port: ${details.port || 'N/A'}</small></span>
                ${details.default_model ? `<span class="text-muted"><small>Model: ${details.default_model}</small></span>` : ''}
            </div>`;
    } else if (status === 'stopped') {
        if (badge) { badge.className = 'badge bg-warning'; badge.textContent = 'Stopped'; }
        if (portBadge) { portBadge.className = 'badge bg-secondary me-2'; portBadge.textContent = 'Port: N/A'; }
        if (infoEl) infoEl.innerHTML = `<span class="text-warning"><i class="bi bi-stop-fill"></i> Foundry не запущен. Нажмите Start Foundry.</span>`;
    } else {
        if (badge) { badge.className = 'badge bg-danger'; badge.textContent = 'Offline'; }
        if (portBadge) { portBadge.className = 'badge bg-secondary me-2'; portBadge.textContent = 'Port: N/A'; }
        if (infoEl) infoEl.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-triangle"></i> Нет связи с Foundry.</span>`;
    }
}

// Выбор и активация модели Foundry
export async function selectFoundryModel(modelId) {
    // Добавляем в chat-model select
    const chatModelSelect = document.getElementById('chat-model');
    if (chatModelSelect) {
        if (![...chatModelSelect.options].some(o => o.value === modelId)) {
            const opt = document.createElement('option');
            opt.value = modelId;
            opt.textContent = modelId;
            chatModelSelect.appendChild(opt);
        }
        chatModelSelect.value = modelId;
    }

    // Сохраняем как модель по умолчанию
    if (window.saveDefaultModel) {
        await window.saveDefaultModel(modelId);
    }
    if (window.CONFIG) window.CONFIG.default_model = modelId;
    updateChatModelBadge(modelId);

    // Визуальный фидбек в списке моделей Foundry
    const listEl = document.getElementById('foundry-models-list');
    if (listEl) {
        listEl.querySelectorAll('button').forEach(btn => {
            btn.classList.remove('btn-success');
            btn.classList.add('btn-outline-success');
            btn.textContent = 'Use';
        });
        const activeBtn = [...listEl.querySelectorAll('button')]
            .find(btn => btn.getAttribute('onclick')?.includes(modelId));
        if (activeBtn) {
            activeBtn.classList.remove('btn-outline-success');
            activeBtn.classList.add('btn-success');
            activeBtn.textContent = '✓ Active';
        }
    }

    showAlert(`Модель ${modelId} выбрана как активная`, 'success');
}

// Запуск Foundry сервиса
export async function startFoundryService() {
    const btn = document.getElementById('foundry-start-btn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Starting...';
    }
    if (window.addLog) window.addLog('▶ Starting Foundry service...');

    try {
        const response = await fetch(`${window.API_BASE}/foundry/start`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        const data = await response.json();
        
        if (data.success) {
            if (window.addLog) window.addLog('✅ Foundry started successfully');
            showAlert('Foundry started successfully', 'success');
            setTimeout(() => {
                checkSystemStatus();
                if (window.loadModels) window.loadModels();
            }, 3000);
        } else {
            if (window.addLog) window.addLog(`❌ Failed to start Foundry: ${data.error}`);
            showAlert(`Failed to start Foundry: ${data.error}`, 'danger');
        }
    } catch (error) {
        if (window.addLog) window.addLog(`❌ Start request failed: ${error.message}`);
        showAlert(`Start request failed: ${error.message}`, 'danger');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-play-fill"></i> Start Foundry';
        }
    }
}

// Остановка Foundry сервиса
export async function stopFoundryService() {
    const btn = document.getElementById('foundry-stop-btn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Stopping...';
    }
    if (window.addLog) window.addLog('⏹ Stopping Foundry service...');

    try {
        const response = await fetch(`${window.API_BASE}/foundry/stop`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        const data = await response.json();
        
        if (data.success) {
            if (window.addLog) window.addLog('✅ Foundry stopped');
            showAlert('Foundry stopped', 'success');
            checkSystemStatus();
        } else {
            if (window.addLog) window.addLog(`❌ Failed to stop Foundry: ${data.error}`);
            showAlert(`Failed to stop Foundry: ${data.error}`, 'danger');
        }
    } catch (error) {
        if (window.addLog) window.addLog(`❌ Stop request failed: ${error.message}`);
        showAlert(`Stop request failed: ${error.message}`, 'danger');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-stop-fill"></i> Stop Foundry';
        }
    }
}

// Проверка статуса Foundry (вызывает checkSystemStatus)
export async function checkFoundryStatus() {
    if (window.addLog) window.addLog('🔍 Checking Foundry status...');
    await checkSystemStatus();
}

// Загрузка и запуск модели через Foundry
export async function downloadAndRunModel() {
    const modelSelect = document.getElementById('model-select');
    const modelId = modelSelect?.value;
    if (!modelId) {
        showAlert('Please select a model to download and run.', 'warning');
        return;
    }

    const downloadProgressEl = document.getElementById('download-progress');
    const progressBarEl = document.getElementById('progress-bar');
    const progressTextEl = document.getElementById('progress-text');

    if (downloadProgressEl) downloadProgressEl.style.display = 'block';
    if (progressBarEl) progressBarEl.style.width = '0%';
    if (progressTextEl) progressTextEl.textContent = 'Starting download...';

    if (window.addLog) window.addLog(`⬇ Downloading and running model: ${modelId}`);

    try {
        const response = await fetch(`${window.API_BASE}/foundry/models/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_id: modelId })
        });
        const data = await response.json();

        if (data.success) {
            if (window.addLog) window.addLog(`✅ Model ${modelId} download/load initiated.`);
            showAlert(`Model ${modelId} download/load initiated. Check Foundry logs for progress.`, 'info');
            // In a real scenario, you'd poll for progress here.
            if (progressTextEl) progressTextEl.textContent = 'Download/Load initiated. Check logs.';
            if (progressBarEl) progressBarEl.style.width = '100%'; // Simulate completion
            if (window.loadModels) setTimeout(window.loadModels, 5000); // Refresh models after some time
        } else {
            if (window.addLog) window.addLog(`❌ Failed to download/run model: ${data.error}`);
            showAlert(`Failed to download/run model: ${data.error}`, 'danger');
            if (progressTextEl) progressTextEl.textContent = `Error: ${data.error}`;
        }
    } catch (error) {
        if (window.addLog) window.addLog(`❌ Download/run request failed: ${error.message}`);
        showAlert(`Download/run request failed: ${error.message}`, 'danger');
        if (progressTextEl) progressTextEl.textContent = `Connection error: ${error.message}`;
    }
}

export function showModelInfo() {
    showAlert('Model info feature not yet implemented.', 'info');
}

export function hideProgress() {
    const downloadProgressEl = document.getElementById('download-progress');
    if (downloadProgressEl) downloadProgressEl.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    // Initial check on load
    checkSystemStatus();
    // Set interval for periodic checks
    setInterval(checkSystemStatus, 30000);
});