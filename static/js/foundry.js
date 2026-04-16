/**
 * Название процесса: Интеграция с Foundry AI
 * Описание: Проверка статуса системы, управление локальными моделями и автозагрузка.
 * Version: 0.4.1
 * Date: 17 апреля 2026
 */

import { showAlert, updateModelStatus, updateChatModelBadge } from './ui.js';

function isGpuFoundryModel(model) {
    const type = String(model?.type || model?.device || '').toLowerCase();
    const modelId = String(model?.id || '').toLowerCase();
    const modelName = String(model?.name || '').toLowerCase();

    // Почему: часть моделей приходит с `type`, часть — только с `device`,
    // а для fallback-описаний надёжнее дополнительно смотреть на `id`/`name`.
    return type.includes('gpu') || modelId.includes('-gpu') || modelName.includes('(gpu)');
}

function getFoundryIncludeGpuFlag() {
    const checkbox = document.getElementById('foundry-include-gpu-models');
    return Boolean(checkbox?.checked);
}

async function waitForFoundryModelLoaded(modelId, timeoutMs = 90000) {
    const startedAt = Date.now();

    // Почему: endpoint `/foundry/models/load` запускает загрузку асинхронно.
    // Ожидание появления модели в `/foundry/models/loaded` делает "Use" реальным,
    // а не только визуальным выбором в UI.
    while (Date.now() - startedAt < timeoutMs) {
        const response = await fetch(`${window.API_BASE}/foundry/models/loaded`);
        const data = await response.json();
        const loadedModels = (data.models || []).map(m => m.id);

        if (data.success && loadedModels.includes(modelId)) {
            return true;
        }

        await new Promise(resolve => setTimeout(resolve, 3000));
    }

    return false;
}

async function ensureFoundryModelLoaded(modelId) {
    const loadedResponse = await fetch(`${window.API_BASE}/foundry/models/loaded`);
    const loadedData = await loadedResponse.json();
    const loadedModels = (loadedData.models || []).map(m => m.id);

    if (loadedData.success && loadedModels.includes(modelId)) {
        return true;
    }

    // Почему: выбор модели из вкладки Foundry должен приводить её в рабочее состояние для чата.
    // Простое сохранение `default_model` недостаточно, если модель ещё не загружена в сервис.
    const loadResponse = await fetch(`${window.API_BASE}/foundry/models/load`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_id: modelId })
    });
    const loadData = await loadResponse.json();

    if (!loadData.success) {
        throw new Error(loadData.error || 'Failed to start Foundry model load');
    }

    return await waitForFoundryModelLoaded(modelId);
}

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
            const includeGpuModels = getFoundryIncludeGpuFlag();
            const models = includeGpuModels
                ? data.models
                : data.models.filter(m => !isGpuFoundryModel(m));
            const listEl = document.getElementById('foundry-models-list');
            if (listEl) {
                if (!models.length) {
                    listEl.innerHTML = `
                        <div class="text-muted text-center p-3">
                            <i class="bi bi-filter"></i><br>
                            No CPU models found with current filter
                        </div>
                    `;
                } else {
                    const esc = (v) => String(v ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
                    const escapeId = (v) => esc(v).replace(/'/g, '&#39;'); // для onclick в атрибуте

                    let tbody = '';
                    let prevAlias = null;
                    models.forEach((m, idx) => {
                        const alias = m.alias || '';
                        const showAlias = alias && alias !== prevAlias;
                        const aliasCell = showAlias ? esc(alias) : '&nbsp;';
                        const isCached = Boolean(m.cached);

                        // "как в foundry model ls": разделитель между блоками alias
                        if (idx > 0 && alias && alias !== prevAlias) {
                            tbody += `
                                <tr class="text-muted">
                                    <td colspan="7" class="py-0 small">--------------------------------------------------------------------------------</td>
                                </tr>
                            `;
                        }
                        prevAlias = alias;

                        tbody += `
                            <tr>
                                <td style="white-space:nowrap; font-weight:${showAlias ? '600' : '400'}">${aliasCell}</td>
                                <td style="white-space:nowrap">${esc(m.device || m.type || '')}</td>
                                <td>${esc(m.task || '')}</td>
                                <td style="white-space:nowrap">${esc(m.size || '')}</td>
                                <td style="white-space:nowrap">${esc(m.license || '')}</td>
                                <td style="white-space:nowrap"><code style="font-size:.75rem">${escapeId(m.id)}</code></td>
                                <td style="width:160px">
                                    ${isCached
                                        ? `<span class="badge bg-success">Downloaded</span>`
                                        : `<button class="btn btn-sm btn-outline-primary" onclick="downloadFoundryModel('${escapeId(m.id)}')">Download</button>`
                                    }
                                </td>
                            </tr>
                        `;
                    });

                    listEl.innerHTML = `
                        <div class="table-responsive">
                            <table class="table table-sm align-middle mb-0">
                                <thead>
                                    <tr>
                                        <th style="white-space:nowrap">Alias</th>
                                        <th style="white-space:nowrap">Device</th>
                                        <th>Task</th>
                                        <th style="white-space:nowrap">File Size</th>
                                        <th style="white-space:nowrap">License</th>
                                        <th style="white-space:nowrap">Model ID</th>
                                        <th style="white-space:nowrap">Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${tbody}
                                </tbody>
                            </table>
                        </div>
                    `;
                }
            }
            showAlert(`Получено моделей: ${models.length}`, 'success');
        } else {
            showAlert(`Ошибка получения моделей: ${data.error || 'Неизвестная ошибка'}`, 'danger');
        }
    } catch (error) {
        console.error('Сбой при запросе списка моделей Foundry:', error);
        showAlert('Не удалось связаться с API Foundry', 'danger');
    }
}

export async function listCachedFoundryModels() {
    try {
        const response = await fetch(`${window.API_BASE}/foundry/models/cached`);
        const data = await response.json();
        const selectEl = document.getElementById('foundry-downloaded-model-select');
        const listEl = document.getElementById('foundry-downloaded-models-list');

        if (!data.success) {
            showAlert(`Ошибка получения скачанных моделей: ${data.error || 'Неизвестная ошибка'}`, 'danger');
            return;
        }

        const models = Array.isArray(data.models) ? data.models : [];
        const items = Array.isArray(data.items) ? data.items : [];

        if (selectEl) {
            selectEl.innerHTML = '<option value="">Select a downloaded model...</option>';
            models.forEach(modelId => {
                const option = document.createElement('option');
                option.value = modelId;
                option.textContent = modelId;
                selectEl.appendChild(option);
            });
        }

        if (listEl) {
            if (!models.length) {
                listEl.innerHTML = `
                    <div class="text-muted text-center p-3">
                        <i class="bi bi-inbox"></i><br>
                        No downloaded models found in Foundry cache
                    </div>
                `;
            } else {
                listEl.innerHTML = (items.length ? items : models.map(modelId => ({ id: modelId }))).map(model => `
                    <div class="d-flex align-items-center justify-content-between px-3 py-2 border-bottom">
                        <div class="me-3">
                            <strong style="font-size:.85rem">${model.alias || model.name || model.id}</strong>
                            <small class="text-muted d-block">${model.device || model.type || 'n/a'}${model.size ? ` · ${model.size}` : ''}</small>
                            <code style="font-size:.75rem">${model.id}</code>
                        </div>
                        <button class="btn btn-sm btn-outline-success" onclick="selectFoundryModel('${String(model.id).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;')}')">
                            Load &amp; Use
                        </button>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Failed to load cached Foundry models:', error);
        showAlert('Не удалось получить список скачанных моделей', 'danger');
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
    try {
        showAlert(`Подключение модели ${modelId}...`, 'info');

        // Выгружаем все остальные загруженные модели, чтобы в памяти была только одна.
        const loadedResponse = await fetch(`${window.API_BASE}/foundry/models/loaded`);
        const loadedData = await loadedResponse.json();
        const loadedModels = (loadedData.models || []).map(m => m.id);

        for (const loadedModelId of loadedModels) {
            if (loadedModelId === modelId) continue;
            const unloadResponse = await fetch(`${window.API_BASE}/foundry/models/unload`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model_id: loadedModelId })
            });
            const unloadData = await unloadResponse.json();
            if (!unloadData.success) {
                // Не прерываемся полностью — иногда unload может вернуть ошибку, если модель уже выгружена.
                if (window.addLog) window.addLog(`⚠ Unload failed for ${loadedModelId}: ${unloadData.error || 'unknown error'}`);
            }
        }

        const isLoaded = await ensureFoundryModelLoaded(modelId);
        if (!isLoaded) {
            showAlert(`Модель ${modelId} не появилась в списке loaded за отведённое время`, 'warning');
            return;
        }

        // Добавление модели в chat-model select
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

        // Сохранение модели как default_model
        if (window.saveDefaultModel) {
            await window.saveDefaultModel(modelId);
        }
        if (window.CONFIG) window.CONFIG.default_model = modelId;
        window._savedChatModel = modelId;
        updateChatModelBadge(modelId);

        const downloadedSelect = document.getElementById('foundry-downloaded-model-select');
        if (downloadedSelect) {
            downloadedSelect.value = modelId;
        }

        // Визуальный фидбек в списке скачанных моделей
        const listEl = document.getElementById('foundry-downloaded-models-list');
        if (listEl) {
            listEl.querySelectorAll('button').forEach(btn => {
                btn.classList.remove('btn-success');
                btn.classList.add('btn-outline-success');
                btn.textContent = 'Load & Use';
            });
            const activeBtn = [...listEl.querySelectorAll('button')]
                .find(btn => btn.getAttribute('onclick')?.includes(modelId));
            if (activeBtn) {
                activeBtn.classList.remove('btn-outline-success');
                activeBtn.classList.add('btn-success');
                activeBtn.textContent = '✓ Loaded & Active';
            }
        }

        showAlert(`Модель ${modelId} загружена и выбрана как активная`, 'success');
    } catch (error) {
        console.error('Сбой активации модели Foundry:', error);
        showAlert(`Не удалось активировать модель: ${error.message}`, 'danger');
    }
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

async function pollFoundryDownloadStatus(pid, modelId, progressBarEl, progressTextEl) {
    const startedAt = Date.now();
    const timeoutMs = 30 * 60 * 1000;

    while (Date.now() - startedAt < timeoutMs) {
        const response = await fetch(`${window.API_BASE}/foundry/models/download/status/${pid}`);
        const data = await response.json();

        if (data.success && data.status === 'downloading') {
            if (progressTextEl) progressTextEl.textContent = `Downloading ${modelId}...`;
            if (progressBarEl) progressBarEl.style.width = '50%';
            await new Promise(resolve => setTimeout(resolve, 3000));
            continue;
        }

        if (data.success && data.status === 'done') {
            if (progressTextEl) progressTextEl.textContent = `Download completed for ${modelId}.`;
            if (progressBarEl) progressBarEl.style.width = '100%';
            return;
        }

        throw new Error(data.error || `Download failed for ${modelId}`);
    }

    throw new Error(`Timed out waiting for ${modelId} download to finish`);
}

async function pollFoundryModelReady(modelId, progressBarEl, progressTextEl) {
    const startedAt = Date.now();
    const timeoutMs = 90 * 1000;

    while (Date.now() - startedAt < timeoutMs) {
        const response = await fetch(`${window.API_BASE}/foundry/models/loaded`);
        const data = await response.json();
        const loadedModels = (data.models || []).map(model => model.id);

        if (data.success && loadedModels.includes(modelId)) {
            if (progressTextEl) progressTextEl.textContent = `Model ${modelId} is ready in Foundry.`;
            if (progressBarEl) progressBarEl.style.width = '100%';
            return true;
        }

        if (progressTextEl) progressTextEl.textContent = `Waiting for ${modelId} to become ready...`;
        if (progressBarEl) progressBarEl.style.width = '90%';
        await new Promise(resolve => setTimeout(resolve, 3000));
    }

    return false;
}

export async function downloadFoundryModel(modelId) {
    if (!modelId) {
        showAlert('Выберите модель для скачивания.', 'warning');
        return;
    }

    if (window.addLog) window.addLog(`⬇ Downloading model via Foundry: ${modelId}`);
    showAlert(`Скачивание модели ${modelId} запущено...`, 'info');

    try {
        const downloadResponse = await fetch(`${window.API_BASE}/foundry/models/download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_id: modelId })
        });
        const downloadData = await downloadResponse.json();

        if (!downloadData.success) {
            throw new Error(downloadData.error || 'Failed to start download');
        }

        if (downloadData.status === 'already_cached') {
            if (window.addLog) window.addLog(`ℹ Model ${modelId} already exists in cache.`);
            showAlert(`Модель ${modelId} уже скачана.`, 'info');
        } else {
            await pollFoundryDownloadStatus(downloadData.pid, modelId);
            if (window.addLog) window.addLog(`✅ Model ${modelId} downloaded.`);
            showAlert(`Модель ${modelId} успешно скачана.`, 'success');
        }

        await listCachedFoundryModels();
        await listFoundryModels();
    } catch (error) {
        if (window.addLog) window.addLog(`❌ Download request failed: ${error.message}`);
        showAlert(`Не удалось скачать модель: ${error.message}`, 'danger');
    }
}

export async function loadSelectedFoundryModel() {
    const selectEl = document.getElementById('foundry-downloaded-model-select');
    const modelId = selectEl?.value;

    if (!modelId) {
        showAlert('Выберите уже скачанную модель для подключения.', 'warning');
        return;
    }

    await selectFoundryModel(modelId);
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

    const gpuCheckbox = document.getElementById('foundry-include-gpu-models');
    if (gpuCheckbox) {
        gpuCheckbox.checked = false;
        gpuCheckbox.addEventListener('change', () => {
            listFoundryModels();
        });
    }

    listCachedFoundryModels();
});