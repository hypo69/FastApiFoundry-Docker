/**
 * models.js — Управление моделями
 *
 * Содержит:
 *  - loadModels()          — загрузка списка моделей из Foundry
 *  - loadConnectedModels() — карточки подключённых моделей (вкладка Models)
 *  - loadCatalog()         — каталог Foundry с кнопками Download/Load/Unload
 *  - saveDefaultModel()    — сохранение модели по умолчанию в config.json
 *  - downloadModel()       — скачать модель через Foundry CLI
 *  - loadModelToService()  — загрузить модель в Foundry сервис
 *  - unloadModel()         — выгрузить модель из Foundry сервиса
 *  - addModel()            — добавить модель через модальное окно
 *  - refreshModels()       — обновить все списки моделей
 */

import { showAlert, updateChatModelBadge } from './ui.js';

// ── Загрузка моделей ──────────────────────────────────────────────────────────

/**
 * Запрашивает список моделей с сервера и обновляет select и список.
 * Вызывается при старте и при нажатии Refresh.
 */
export async function loadModels() {
    try {
        const data = await fetch(`${window.API_BASE}/models`).then(r => r.json());
        if (data.success && data.models) {
            updateModelSelect(data.models);
            updateModelsList(data.models);
        }
    } catch (e) {
        console.error('Failed to load models:', e);
    }
}

/**
 * Заполняет select #chat-model списком моделей.
 * Добавляет эмодзи-префиксы для hf:: и llama:: моделей.
 * @param {Array} models
 */
export function updateModelSelect(models) {
    const select = document.getElementById('chat-model');
    if (!select) return;

    // Сохраняем текущий выбор чтобы восстановить после перезаполнения
    const current = select.value;
    select.innerHTML = '<option value="">Select a model...</option>';

    models.forEach(({ id, name }) => {
        const opt = document.createElement('option');
        opt.value = id;
        if (id.startsWith('hf::'))    { opt.textContent = `🤗 ${name || id.slice(4)}`; opt.dataset.hf = '1'; }
        else if (id.startsWith('llama::')) { opt.textContent = `🦙 ${name || id.slice(7)}`; opt.dataset.llama = '1'; }
        else                          { opt.textContent = name || id; }
        select.appendChild(opt);
    });

    // Восстанавливаем выбор или применяем сохранённую модель из config
    if (current) select.value = current;
    else if (window._savedChatModel) select.value = window._savedChatModel;
}

/**
 * Отрисовывает список моделей в #models-list (вкладка Models).
 * @param {Array} models
 */
export function updateModelsList(models) {
    const list = document.getElementById('models-list');
    if (!list) return;

    if (models?.length) {
        list.innerHTML = models.map(({ id }) => `
            <div class="model-item d-flex justify-content-between align-items-center px-3 py-2 border-bottom">
                <div><strong>${id}</strong><br><small class="text-muted">Available</small></div>
            </div>`).join('');
    } else {
        list.innerHTML = '<div class="text-muted text-center p-4">No models found. Start Foundry first.</div>';
    }

    // Обновляем счётчик моделей в navbar
    const counter = document.getElementById('models-count');
    if (counter) counter.textContent = models?.length || 0;
}

/**
 * Загружает карточки подключённых моделей (вкладка Models).
 */
export async function loadConnectedModels() {
    const container = document.getElementById('models-container');
    if (!container) return;
    try {
        const data = await fetch(`${window.API_BASE}/models/connected`).then(r => r.json());
        if (data.success && data.models?.length) {
            container.innerHTML = data.models.map(({ id, name }) => `
                <div class="col-md-6 mb-3">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5>${name || id}</h5>
                            <p class="small text-muted">ID: ${id}</p>
                            <button class="btn btn-sm btn-primary" onclick="selectModelForChat('${id}')">Use in Chat</button>
                            <button class="btn btn-sm btn-outline-danger" onclick="removeModel('${id}')">Unload</button>
                        </div>
                    </div>
                </div>`).join('');
        } else {
            container.innerHTML = '<div class="col-12"><p class="text-muted text-center">No models connected. Use the Foundry tab to load models.</p></div>';
        }
    } catch (e) {
        console.error('Failed to load connected models:', e);
    }
}

// ── Выбор и сохранение ────────────────────────────────────────────────────────

/**
 * Выбирает модель для чата и сохраняет как default.
 * @param {string} modelId
 */
export function selectModelForChat(modelId) {
    const select = document.getElementById('chat-model');
    if (select) select.value = modelId;
    saveDefaultModel(modelId);
    updateChatModelBadge(modelId);
    showAlert(`Model ${modelId} selected`, 'success');
}

/**
 * Сохраняет модель по умолчанию в config.json через PATCH.
 * @param {string} modelId
 */
export async function saveDefaultModel(modelId) {
    try {
        await fetch(`${window.API_BASE}/config`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 'foundry_ai.default_model': modelId })
        });
        if (window.CONFIG) window.CONFIG.default_model = modelId;
    } catch (e) {
        console.error('Failed to save default model:', e);
    }
}

// ── Каталог Foundry ───────────────────────────────────────────────────────────

/**
 * Загружает каталог моделей Foundry с состоянием (cached/loaded/not downloaded).
 * Параллельно запрашивает available, cached и loaded модели.
 */
export async function loadCatalog() {
    const list = document.getElementById('catalog-list');
    if (!list) return;
    list.innerHTML = '<div class="text-muted p-2">Loading...</div>';

    try {
        const [availRes, cachedRes, loadedRes] = await Promise.all([
            fetch(`${window.API_BASE}/foundry/models/available`).then(r => r.json()),
            fetch(`${window.API_BASE}/foundry/models/cached`).then(r => r.json()),
            fetch(`${window.API_BASE}/foundry/models/loaded`).then(r => r.json()),
        ]);

        const cachedDirs = new Set(cachedRes.models || []);
        const loadedIds  = new Set((loadedRes.models || []).map(m => m.id));
        const cacheDir   = cachedRes.cache_dir || '';

        list.innerHTML = `<div class="text-muted" style="font-size:.8rem;margin-bottom:8px">Cache: ${cacheDir}</div>`;

        for (const m of (availRes.models || [])) {
            const dirName  = m.id.replace(':', '-');
            const isCached = cachedDirs.has(dirName);
            const isLoaded = loadedIds.has(m.id);

            // Кнопка зависит от состояния модели
            const btn = !isCached && !isLoaded
                ? `<button class="btn btn-sm btn-outline-primary" onclick="downloadModel('${m.id}')">⬇ Download</button>`
                : !isLoaded
                ? `<button class="btn btn-sm btn-success" onclick="loadModelToService('${m.id}')">▶ Load</button>`
                : `<button class="btn btn-sm btn-danger" onclick="unloadModel('${m.id}')">⏹ Unload</button>`;

            const statusBadge = isLoaded
                ? '<span class="badge bg-success">● Loaded</span>'
                : isCached
                ? '<span class="badge bg-secondary">✓ Cached</span>'
                : '<span class="badge bg-light text-dark">○ Not downloaded</span>';

            const item = document.createElement('div');
            item.className = 'd-flex align-items-center justify-content-between px-3 py-2 border-bottom';
            item.id = `catalog-${dirName}`;
            item.innerHTML = `
                <div>
                    <strong style="font-size:.85rem">${m.name}</strong>
                    <small class="text-muted d-block">${m.id} · ${m.size} · ${m.description}</small>
                </div>
                <div class="d-flex align-items-center gap-2">
                    ${statusBadge}
                    <div id="prog-${dirName}" class="progress" style="width:80px;display:none"><div class="progress-bar progress-bar-animated" style="width:100%"></div></div>
                    ${btn}
                </div>`;
            list.appendChild(item);
        }
    } catch (e) {
        list.innerHTML = `<div class="text-danger p-2">Error: ${e.message}</div>`;
        console.error('Catalog load failed:', e);
    }
}

// ── Операции с моделями ───────────────────────────────────────────────────────

/** Скачивает модель через Foundry CLI (фоновый процесс) */
export async function downloadModel(modelId) {
    const prog = document.getElementById(`prog-${modelId.replace(':', '-')}`);
    if (prog) prog.style.display = '';

    try {
        const data = await fetch(`${window.API_BASE}/foundry/models/download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_id: modelId })
        }).then(r => r.json());

        if (data.status === 'already_cached') {
            showAlert(`Model ${modelId} already cached.`, 'info');
        } else if (data.success) {
            showAlert(`Downloading ${modelId}. Check Foundry logs for progress.`, 'info');
        } else {
            showAlert(`Download failed: ${data.error}`, 'danger');
        }
        loadCatalog();
    } catch (e) {
        showAlert(`Download error: ${e.message}`, 'danger');
        console.error('Download model failed:', e);
    } finally {
        if (prog) prog.style.display = 'none';
    }
}

/** Загружает скачанную модель в Foundry сервис */
export async function loadModelToService(modelId) {
    try {
        const data = await fetch(`${window.API_BASE}/foundry/models/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_id: modelId })
        }).then(r => r.json());

        showAlert(data.success ? `Load of ${modelId} started.` : `Failed: ${data.error}`, data.success ? 'success' : 'danger');
        if (data.success) setTimeout(loadCatalog, 5000);
    } catch (e) {
        showAlert(`Error: ${e.message}`, 'danger');
        console.error('Load model to service failed:', e);
    }
}

/** Выгружает модель из Foundry сервиса */
export async function unloadModel(modelId) {
    try {
        const data = await fetch(`${window.API_BASE}/foundry/models/unload`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_id: modelId })
        }).then(r => r.json());

        showAlert(data.success ? `Model ${modelId} unloaded.` : `Failed: ${data.error}`, data.success ? 'success' : 'danger');
        if (data.success) { loadCatalog(); refreshModels(); }
    } catch (e) {
        showAlert(`Error: ${e.message}`, 'danger');
        console.error('Unload model failed:', e);
    }
}

/** Выгружает модель (алиас для removeModel из карточек) */
export async function removeModel(modelId) {
    if (!confirm(`Unload ${modelId}?`)) return;
    await unloadModel(modelId);
    loadConnectedModels();
}

/** Тестирует модель коротким запросом */
export async function testModel(modelId) {
    showAlert(`Testing ${modelId}...`, 'info');
    try {
        const data = await fetch(`${window.API_BASE}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: 'Ping', model: modelId, max_tokens: 10 })
        }).then(r => r.json());
        showAlert(data.success ? 'Model is active' : 'Test failed', data.success ? 'success' : 'danger');
    } catch (e) {
        showAlert('Network error during test', 'danger');
    }
}

/** Обновляет все списки моделей */
export async function refreshModels() {
    await loadModels();
    await loadConnectedModels();
}

// ── Добавление модели ─────────────────────────────────────────────────────────

/**
 * Добавляет новую модель через модальное окно #addModelModal.
 * Читает поля формы и отправляет POST /models/add.
 */
export async function addModel() {
    const modelId = document.getElementById('model-id')?.value.trim();
    if (!modelId) { showAlert('Model ID is required.', 'warning'); return; }

    try {
        const data = await fetch(`${window.API_BASE}/models/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                provider: document.getElementById('model-provider')?.value,
                id:       modelId,
                name:     document.getElementById('model-name')?.value.trim() || modelId,
                endpoint: document.getElementById('endpoint-url')?.value.trim() || undefined,
                api_key:  document.getElementById('api-key')?.value.trim()     || undefined,
            })
        }).then(r => r.json());

        if (data.success) {
            showAlert(`Model ${modelId} added.`, 'success');
            bootstrap.Modal.getInstance(document.getElementById('addModelModal'))?.hide();
            refreshModels();
        } else {
            showAlert(`Failed: ${data.error}`, 'danger');
        }
    } catch (e) {
        showAlert(`Error: ${e.message}`, 'danger');
    }
}

/**
 * Показывает/скрывает поля endpoint и api_key в зависимости от провайдера.
 */
export function updateProviderFields() {
    const provider = document.getElementById('model-provider')?.value;
    const endpointField = document.getElementById('endpoint-field');
    const apiKeyField   = document.getElementById('api-key-field');
    if (endpointField) endpointField.style.display = ['custom', 'ollama'].includes(provider) ? '' : 'none';
    if (apiKeyField)   apiKeyField.style.display   = ['openai', 'anthropic', 'custom'].includes(provider) ? '' : 'none';
}

// ── Инициализация ─────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    // Загружаем модели и каталог при старте страницы
    loadModels();
    loadConnectedModels();
    loadCatalog();
});
