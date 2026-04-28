/**
 * =============================================================================
 * Process Name: API Keys / Providers tab — manage LLM provider keys
 * =============================================================================
 * Description:
 *   Web app UI for managing provider API keys.
 *   Keys are stored in .env via /api/v1/config/provider-keys.
 *   Supports export/import using the shared ai-assistant-config format.
 *
 * File: js/providers.js
 * Project: FastApiFoundry (Docker)
 * Version: 0.6.0
 * Author: hypo69
 * Copyright: © 2026 hypo69
 * =============================================================================
 */

import {
    PROVIDERS,
    CONFIG_SCHEMA_NAME,
    CONFIG_SCHEMA_VERSION,
    validateConfigFile,
    normalizeProviderKeys,
    wrapProviderKeysAsArrays,
} from './providers-registry.js';

// Active provider state (in-memory, cosmetic only — not persisted to server)
let _activeProvider = null;
let _activeModel    = null;

function maskKey(k) {
    if (!k) return '••••••••';
    return k.length > 8 ? k.slice(0, 4) + '…' + k.slice(-4) : '••••••••';
}

// ── Server API ───────────────────────────────────────────────────────────────

async function loadProviderKeys() {
    try {
        const res = await fetch(`${window.API_BASE}/config/provider-keys`).then(r => r.json());
        return res.success ? res.keys : {};
    } catch { return {}; }
}

async function saveProviderKey(provider, value) {
    return fetch(`${window.API_BASE}/config/provider-keys`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ keys: { [provider]: value } }),
    }).then(r => r.json());
}

// ── Build provider card ──────────────────────────────────────────────────────

function buildProviderCard(providerId, cfg, currentKey, customUrl) {
    const hasKey   = !!currentKey;
    const isActive = _activeProvider === providerId;

    const card = document.createElement('div');
    card.className = 'card mb-3 provider-card';
    card.dataset.provider = providerId;

    card.innerHTML = `
        <div class="card-header provider-card-header d-flex align-items-center gap-2"
             style="cursor:pointer;user-select:none">
            <span class="fw-semibold small flex-grow-1">${cfg.label}</span>
            <span class="provider-badge badge ${isActive ? 'bg-success' : 'bg-secondary'}">
                ${isActive ? 'Активен' : 'Не активен'}
            </span>
            <span class="chevron" style="font-size:11px;color:#adb5bd;transition:transform .2s${hasKey || isActive ? ';transform:rotate(180deg)' : ''}">▼</span>
        </div>
        <div class="card-body provider-card-body" style="display:${hasKey || isActive ? '' : 'none'}">
            <div class="form-label small mb-2">
                API ключи${cfg.hint ? ` — <a href="https://${cfg.hint}" target="_blank" class="text-primary">${cfg.hint}</a>` : ''}
            </div>
            <div class="keys-list mb-2"></div>
            <div class="input-group input-group-sm add-key-row">
                <input type="password" class="form-control new-key-input" placeholder="${cfg.placeholder}">
                <button class="btn btn-outline-secondary btn-sm toggle-new-key" type="button">👁</button>
                <button class="btn btn-outline-secondary add-key-btn" type="button">+ Добавить ключ</button>
            </div>
            ${providerId === 'custom' ? `
                <label class="form-label small mt-3 mb-1">Базовый URL</label>
                <input type="text" class="form-control form-control-sm url-input"
                    placeholder="http://localhost:9696/v1"
                    value="${customUrl || 'http://localhost:9696/v1'}">
                <div class="url-status small mt-1"></div>
            ` : ''}
        </div>
    `;

    const header   = card.querySelector('.provider-card-header');
    const body     = card.querySelector('.provider-card-body');
    const chevron  = card.querySelector('.chevron');
    const badge    = card.querySelector('.provider-badge');
    const keysList = card.querySelector('.keys-list');
    const newInput = card.querySelector('.new-key-input');

    header.addEventListener('click', () => {
        const open = body.style.display !== 'none';
        body.style.display = open ? 'none' : '';
        chevron.style.transform = open ? '' : 'rotate(180deg)';
    });

    card.querySelector('.toggle-new-key').addEventListener('click', () => {
        newInput.type = newInput.type === 'password' ? 'text' : 'password';
    });

    if (providerId === 'custom') {
        const urlInput  = card.querySelector('.url-input');
        const urlStatus = card.querySelector('.url-status');
        urlInput.addEventListener('blur', async () => {
            const res = await saveProviderKey('custom_url', urlInput.value.trim());
            if (res.success) showStatus(urlStatus, '✓ Сохранено', 'text-success');
        });
    }

    const keysState = currentKey ? [{ value: currentKey, models: [] }] : [];

    function markAllInactive() {
        document.querySelectorAll('.provider-card .provider-badge').forEach(b => {
            b.className = 'provider-badge badge bg-secondary';
            b.textContent = 'Не активен';
        });
    }

    function renderKeys() {
        keysList.innerHTML = '';
        keysState.forEach((entry, i) => {
            const isThisActive = isActive && i === 0;
            const block = document.createElement('div');
            block.className = 'mb-2';

            block.innerHTML = `
                <div class="key-item d-flex align-items-center gap-2 p-2 border rounded${isThisActive ? ' border-primary bg-light' : ''}" style="font-size:13px">
                    <span class="key-masked text-muted font-monospace" style="font-size:11px;flex-shrink:0">${maskKey(entry.value)}</span>
                    <span class="key-chosen-model flex-grow-1 text-muted small">${entry.chosenModel ? `→ ${entry.chosenModel}` : '— нет модели —'}</span>
                    <button class="btn btn-outline-secondary btn-sm load-models-btn" style="white-space:nowrap">Загрузить модели</button>
                    <button class="btn btn-primary btn-sm set-active-btn"${isThisActive ? ' disabled' : ''} style="white-space:nowrap">
                        ${isThisActive ? 'Активен' : 'Сделать активным'}
                    </button>
                    <button class="btn btn-outline-danger btn-sm remove-key-btn">✕</button>
                </div>
                <div class="models-panel border border-primary rounded p-2 mt-1" style="display:none">
                    <div class="models-list" style="max-height:180px;overflow-y:auto"></div>
                    <div class="fetch-status small mt-1"></div>
                </div>
            `;

            const keyItem      = block.querySelector('.key-item');
            const modelsPanel  = block.querySelector('.models-panel');
            const modelsList   = block.querySelector('.models-list');
            const fetchStatus  = block.querySelector('.fetch-status');
            const chosenEl     = block.querySelector('.key-chosen-model');
            const setActiveBtn = block.querySelector('.set-active-btn');

            block.querySelector('.load-models-btn').addEventListener('click', async () => {
                fetchStatus.textContent = 'Загрузка моделей…';
                fetchStatus.className = 'small text-primary';
                modelsPanel.style.display = '';
                try {
                    const customUrl = providerId === 'custom'
                        ? (card.querySelector('.url-input')?.value || '') : '';
                    const models = await cfg.fetchModels(entry.value, { customUrl });
                    entry.models = models;
                    renderModelsList(models, entry, chosenEl, modelsPanel, setActiveBtn);
                    fetchStatus.textContent = `✓ ${models.length} моделей`;
                    fetchStatus.className = 'small text-success';
                } catch (e) {
                    fetchStatus.textContent = '✗ ' + e.message;
                    fetchStatus.className = 'small text-danger';
                }
                setTimeout(() => { fetchStatus.textContent = ''; }, 5000);
            });

            setActiveBtn.addEventListener('click', () => {
                if (!entry.chosenModel) {
                    fetchStatus.textContent = '✗ Сначала загрузите и выберите модель';
                    fetchStatus.className = 'small text-danger';
                    setTimeout(() => { fetchStatus.textContent = ''; }, 3000);
                    return;
                }
                _activeProvider = providerId;
                _activeModel    = entry.chosenModel;
                markAllInactive();
                badge.className = 'provider-badge badge bg-success';
                badge.textContent = 'Активен';
                keyItem.classList.add('border-primary', 'bg-light');
                setActiveBtn.disabled = true;
                setActiveBtn.textContent = 'Активен';
            });

            block.querySelector('.remove-key-btn').addEventListener('click', async () => {
                keysState.splice(i, 1);
                const newVal = keysState.length ? keysState[0].value : '';
                await saveProviderKey(providerId, newVal);
                renderKeys();
                if (!keysState.length) body.style.display = 'none';
            });

            keysList.appendChild(block);
        });
    }

    function renderModelsList(models, entry, chosenEl, modelsPanel, setActiveBtn) {
        modelsList.innerHTML = '';
        if (!models.length) {
            modelsList.innerHTML = '<div class="text-muted small p-2">Нет моделей</div>';
            return;
        }
        models.forEach(m => {
            const row = document.createElement('div');
            row.className = 'model-item d-flex align-items-center gap-2 px-2 py-1 rounded'
                + (m.id === entry.chosenModel ? ' bg-primary bg-opacity-10' : '');
            row.style.cssText = 'cursor:pointer;font-size:12px';
            row.innerHTML = `<span class="flex-grow-1">${m.label || m.id}</span>`;
            row.addEventListener('click', () => {
                entry.chosenModel = m.id;
                chosenEl.textContent = `→ ${m.label || m.id}`;
                chosenEl.classList.remove('text-muted');
                modelsPanel.style.display = 'none';
                setActiveBtn.disabled = false;
                setActiveBtn.textContent = 'Сделать активным';
                modelsList.querySelectorAll('.model-item').forEach(r => r.classList.remove('bg-primary', 'bg-opacity-10'));
                row.classList.add('bg-primary', 'bg-opacity-10');
            });
            modelsList.appendChild(row);
        });
    }

    renderKeys();

    card.querySelector('.add-key-btn').addEventListener('click', async () => {
        const val = newInput.value.trim();
        if (!val) return;
        keysState.push({ value: val, models: [] });
        await saveProviderKey(providerId, val);
        newInput.value = '';
        body.style.display = '';
        chevron.style.transform = 'rotate(180deg)';
        renderKeys();
    });

    return card;
}

function showStatus(el, msg, cls) {
    el.textContent = msg;
    el.className = `small ${cls}`;
    setTimeout(() => { el.textContent = ''; el.className = 'small'; }, 3000);
}

// ── Render all cards ─────────────────────────────────────────────────────────

export async function initProviders() {
    const list = document.getElementById('providers-list');
    if (!list) return;

    list.innerHTML = '<div class="text-muted text-center p-3"><small>Загрузка…</small></div>';

    const keys = await loadProviderKeys();
    list.innerHTML = '';

    for (const [id, cfg] of Object.entries(PROVIDERS)) {
        list.appendChild(buildProviderCard(id, cfg, keys[id] || '', keys['custom_url'] || ''));
    }
}

// ── Export to shared format ──────────────────────────────────────────────────

export async function exportToExtension() {
    const confirmed = confirm(
        '⚠️ Предупреждение безопасности\n\n' +
        'Экспортируемый файл будет содержать ВСЕ ваши API ключи в открытом виде.\n\n' +
        'Не передавайте этот файл третьим лицам и не загружайте в облако.\n\nПродолжить?'
    );
    if (!confirmed) return;

    const res = await fetch(`${window.API_BASE}/config/extension-export`).then(r => r.json());
    if (!res.success) { alert('Export failed'); return; }

    // Upgrade to v2 schema
    const payload = {
        schema:         CONFIG_SCHEMA_NAME,
        version:        CONFIG_SCHEMA_VERSION,
        exportedAt:     new Date().toISOString(),
        exportedFrom:   'app',
        providerKeys:   res.providerKeys   || {},
        customModels:   res.customModels   || {},
        activeProvider: res.activeProvider || null,
        activeModel:    res.activeModel    || null,
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `ai-assistant-config-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// ── Import from shared format ────────────────────────────────────────────────

export async function importFromExtension(file) {
    let cfg;
    try { cfg = JSON.parse(await file.text()); }
    catch { alert('✗ Неверный JSON файл'); return; }

    // Accept both v1 (legacy, no schema field) and v2
    const isLegacyV1 = cfg.version === 1 && typeof cfg.providerKeys === 'object' && !cfg.schema;
    const err = isLegacyV1 ? null : validateConfigFile(cfg);
    if (err) { alert(`✗ Неизвестный формат: ${err}`); return; }

    const confirmed = confirm(
        `Импортировать ключи?\n\nЭкспортировано: ${cfg.exportedAt || 'неизвестно'}\n` +
        `Источник: ${cfg.exportedFrom || 'неизвестно'}\n\nКлючи будут записаны в .env.`
    );
    if (!confirmed) return;

    // Normalize: extension stores arrays, app stores strings
    const normalizedKeys = normalizeProviderKeys(cfg.providerKeys);

    const res = await fetch(`${window.API_BASE}/config/extension-import`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
            providerKeys:   normalizedKeys,
            customModels:   cfg.customModels   || {},
            activeProvider: cfg.activeProvider || null,
            activeModel:    cfg.activeModel    || null,
        }),
    }).then(r => r.json());

    if (res.success) {
        alert(`✓ Импортированы ключи для: ${res.imported.join(', ') || 'нет'}`);
        await initProviders();
    } else {
        alert('✗ Ошибка импорта');
    }
}
