/**
 * rag.js — Система RAG
 *
 * Содержит:
 *  - refreshRAGStatus()   — статус активной базы
 *  - ragLoadProfiles()    — список баз в ~/.rag
 *  - ragBrowseHome()      — открыть браузер с домашней директории
 *  - ragBrowse(path)      — навигация по файловой системе
 *  - ragSelectDir(path)   — выбрать директорию и проверить индекс
 *  - ragBuildIndex(force) — собрать индекс для выбранной директории
 *  - testRAGSearch()      — тестовый поиск
 *  - clearRAGChunks()     — очистить активный индекс
 *  - handleRAGToggle()    — переключатель Enable RAG
 */

import { showAlert } from './ui.js';

const RAG_API = `${window.location.origin}/api/v1/rag`;

// ── Статус ────────────────────────────────────────────────────────────────────

/**
 * Обновляет блок #rag-status — показывает активную базу и её параметры.
 */
export async function refreshRAGStatus() {
    const el = document.getElementById('rag-status');
    if (!el) return;
    try {
        const data = await fetch(`${RAG_API}/status`).then(r => r.json());
        if (!data.success) { el.innerHTML = `<div class="text-danger small">${data.error}</div>`; return; }

        el.innerHTML = `
            <table class="table table-sm mb-0">
                <tr><td>Status</td><td><span class="badge ${data.enabled ? 'bg-success' : 'bg-secondary'}">${data.enabled ? 'Enabled' : 'Disabled'}</span></td></tr>
                <tr><td>Index dir</td><td><code style="font-size:.75rem">${data.index_dir}</code></td></tr>
                <tr><td>Chunks</td><td>${data.total_chunks}</td></tr>
                <tr><td>Model</td><td><small>${data.model}</small></td></tr>
            </table>`;
    } catch (e) {
        if (el) el.innerHTML = `<div class="text-danger small">${e.message}</div>`;
    }
}

// ── Профили (базы в ~/.rag) ───────────────────────────────────────────────────

/**
 * Загружает список RAG баз из ~/.rag и отрисовывает в #rag-profiles-list.
 * Каждая база показывает кнопки Load и Delete.
 */
export async function ragLoadProfiles() {
    const list = document.getElementById('rag-profiles-list');
    if (!list) return;
    list.innerHTML = '<div class="text-center p-2"><div class="spinner-border spinner-border-sm"></div></div>';

    try {
        const data = await fetch(`${RAG_API}/profiles`).then(r => r.json());
        if (!data.profiles?.length) {
            list.innerHTML = '<div class="text-muted text-center p-3"><small>No RAG bases yet. Build one →</small></div>';
            return;
        }

        list.innerHTML = data.profiles.map(p => `
            <div class="d-flex align-items-center gap-2 px-3 py-2 border-bottom">
                <div class="flex-grow-1 overflow-hidden">
                    <strong style="font-size:.85rem">${p.name}</strong>
                    <small class="text-muted d-block text-truncate">${p.source_dir || p.index_dir}</small>
                    ${p.chunks ? `<small class="text-muted">${p.chunks} chunks</small>` : ''}
                </div>
                <span class="badge ${p.has_index ? 'bg-success' : 'bg-warning'}">${p.has_index ? '✓' : '!'}</span>
                <button class="btn btn-sm btn-outline-primary" onclick="ragLoadProfile('${p.name}')" title="Activate this base">
                    <i class="bi bi-play-fill"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="ragDeleteProfile('${p.name}')" title="Delete">
                    <i class="bi bi-trash"></i>
                </button>
            </div>`).join('');
    } catch (e) {
        list.innerHTML = `<div class="text-danger p-2 small">${e.message}</div>`;
        console.error('ragLoadProfiles failed:', e);
    }
}

/**
 * Активирует выбранную RAG базу — переключает index_dir в config.json
 * и перезагружает RAG систему.
 * @param {string} name
 */
export async function ragLoadProfile(name) {
    try {
        const data = await fetch(`${RAG_API}/profiles/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        }).then(r => r.json());

        if (data.success) {
            showAlert(`✅ RAG base '${name}' activated`, 'success');
            refreshRAGStatus();
        } else {
            showAlert(`❌ ${data.error}`, 'danger');
        }
    } catch (e) {
        showAlert(`❌ ${e.message}`, 'danger');
    }
}

/**
 * Удаляет RAG базу из ~/.rag/<name>/.
 * @param {string} name
 */
export async function ragDeleteProfile(name) {
    if (!confirm(`Delete RAG base '${name}'?`)) return;
    try {
        const data = await fetch(`${RAG_API}/profiles/${encodeURIComponent(name)}`, { method: 'DELETE' }).then(r => r.json());
        if (data.success) { showAlert(`✅ Deleted '${name}'`, 'success'); ragLoadProfiles(); }
        else showAlert(`❌ ${data.error}`, 'danger');
    } catch (e) {
        showAlert(`❌ ${e.message}`, 'danger');
    }
}

// ── Браузер файловой системы ──────────────────────────────────────────────────

/**
 * Открывает браузер с домашней директории пользователя.
 */
export async function ragBrowseHome() {
    await ragBrowse('~');
}

/**
 * Загружает содержимое директории и отрисовывает в #rag-browser.
 * @param {string} path — абсолютный путь или ~
 */
export async function ragBrowse(path) {
    const browser = document.getElementById('rag-browser');
    if (!browser) return;
    browser.innerHTML = '<div class="text-center p-2"><div class="spinner-border spinner-border-sm"></div></div>';

    try {
        const data = await fetch(`${RAG_API}/browse?path=${encodeURIComponent(path)}`).then(r => r.json());
        if (!data.success) { browser.innerHTML = `<div class="text-danger p-2 small">${data.error}</div>`; return; }

        let html = '';

        // Кнопка "вверх"
        if (data.parent) {
            html += `<div class="px-3 py-1 border-bottom" style="cursor:pointer;background:#f8f9fa"
                         onclick="ragBrowse('${data.parent.replace(/\\/g, '\\\\')}')">
                        <i class="bi bi-arrow-up text-muted"></i>
                        <small class="text-muted ms-1">..</small>
                     </div>`;
        }

        // Текущий путь
        html += `<div class="px-3 py-1 border-bottom bg-light">
                    <small class="text-muted font-monospace">${data.current}</small>
                    <button class="btn btn-sm btn-success float-end py-0" style="font-size:.75rem"
                            onclick="ragSelectDir('${data.current.replace(/\\/g, '\\\\')}')">
                        Select this
                    </button>
                 </div>`;

        if (!data.dirs.length) {
            html += '<div class="text-muted text-center p-2 small">No subdirectories</div>';
        } else {
            html += data.dirs.map(d => `
                <div class="d-flex align-items-center px-3 py-1 border-bottom"
                     style="cursor:pointer" onmouseover="this.style.background='#f0f4ff'" onmouseout="this.style.background=''">
                    <i class="bi bi-folder text-warning me-2"></i>
                    <span class="flex-grow-1 text-truncate" style="font-size:.85rem"
                          onclick="ragBrowse('${d.path.replace(/\\/g, '\\\\')}')">
                        ${d.name}
                    </span>
                    <button class="btn btn-sm btn-outline-success py-0" style="font-size:.75rem"
                            onclick="ragSelectDir('${d.path.replace(/\\/g, '\\\\')}')">
                        Select
                    </button>
                </div>`).join('');
        }

        browser.innerHTML = html;
    } catch (e) {
        browser.innerHTML = `<div class="text-danger p-2 small">${e.message}</div>`;
        console.error('ragBrowse failed:', e);
    }
}

/**
 * Выбирает директорию и проверяет — есть ли уже индекс для неё.
 * @param {string} path
 */
export async function ragSelectDir(path) {
    const input  = document.getElementById('rag-selected-dir');
    const status = document.getElementById('rag-dir-status');
    if (input) input.value = path;

    if (!status) return;
    status.style.display = '';
    status.innerHTML = '<div class="spinner-border spinner-border-sm me-1"></div><small>Checking...</small>';

    try {
        // Проверяем через /build с force=false — если already_indexed вернёт true
        const data = await fetch(`${RAG_API}/build`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                docs_dir: path,
                output_dir: '',   // игнорируется на сервере
                model: document.getElementById('rag-build-model')?.value || 'sentence-transformers/all-mpnet-base-v2',
                chunk_size: 1,    // минимум — только для проверки
                overlap: 0,
            })
        }).then(r => r.json());

        if (data.already_indexed) {
            status.innerHTML = `<div class="alert alert-warning p-2 mb-0 small">
                ⚠️ Index already exists for this directory (<strong>${data.name}</strong>).
                Use <strong>Rebuild (force)</strong> to re-index, or <strong>Load</strong> it from the list.
            </div>`;
        } else {
            status.innerHTML = `<div class="alert alert-success p-2 mb-0 small">
                ✅ No index yet — ready to build.
            </div>`;
        }
    } catch (e) {
        status.innerHTML = `<div class="text-danger small">${e.message}</div>`;
    }
}

// ── Сборка индекса ────────────────────────────────────────────────────────────

/**
 * Собирает RAG индекс для выбранной директории.
 * Сохраняет в ~/.rag/<dir_name>/.
 * @param {boolean} force — пересобрать даже если индекс уже есть
 */
export async function ragBuildIndex(force = false) {
    const sourceDir = document.getElementById('rag-selected-dir')?.value.trim();
    if (!sourceDir) { showAlert('Select a source directory first', 'warning'); return; }

    const statusEl = document.getElementById('rag-build-status');
    const buildBtn = document.getElementById('rag-build-btn');

    if (buildBtn) buildBtn.disabled = true;
    if (statusEl) {
        statusEl.style.display = '';
        statusEl.innerHTML = '<div class="alert alert-info p-2"><div class="spinner-border spinner-border-sm me-2"></div>Building index... This may take a few minutes.</div>';
    }

    try {
        const data = await fetch(`${RAG_API}/build`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                docs_dir:   sourceDir,
                output_dir: '',  // сервер сам определяет ~/.rag/<name>/
                model:      document.getElementById('rag-build-model')?.value || 'sentence-transformers/all-mpnet-base-v2',
                chunk_size: parseInt(document.getElementById('rag-build-chunk')?.value  || '1000'),
                overlap:    parseInt(document.getElementById('rag-build-overlap')?.value || '50'),
                force,
            })
        }).then(r => r.json());

        if (data.already_indexed && !force) {
            if (statusEl) statusEl.innerHTML = `<div class="alert alert-warning p-2">
                ⚠️ Index already exists for <strong>${data.name}</strong>.
                Use <strong>Rebuild (force)</strong> to re-index.
            </div>`;
        } else if (data.success) {
            if (statusEl) statusEl.innerHTML = `<div class="alert alert-success p-2">
                ✅ Built <strong>${data.name}</strong>: ${data.chunks} chunks → <code>${data.index_dir}</code>
            </div>`;
            ragLoadProfiles();
            refreshRAGStatus();
        } else {
            if (statusEl) statusEl.innerHTML = `<div class="alert alert-danger p-2">❌ ${data.error}</div>`;
        }
    } catch (e) {
        if (statusEl) statusEl.innerHTML = `<div class="alert alert-danger p-2">❌ ${e.message}</div>`;
        console.error('ragBuildIndex failed:', e);
    } finally {
        if (buildBtn) buildBtn.disabled = false;
    }
}

// ── Поиск ─────────────────────────────────────────────────────────────────────

/**
 * Тестовый поиск по активной RAG базе.
 * Читает запрос из #rag-test-query.
 */
export async function testRAGSearch() {
    const query = document.getElementById('rag-test-query')?.value.trim();
    if (!query) { showAlert('Enter a search query', 'warning'); return; }

    try {
        const data = await fetch(`${RAG_API}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, top_k: 3 })
        }).then(r => r.json());

        const outputEl  = document.getElementById('rag-search-output');
        const resultsEl = document.getElementById('rag-test-results');
        if (outputEl && resultsEl && data.success) {
            resultsEl.style.display = '';
            outputEl.innerHTML = data.results.map(r =>
                `<p><strong>Score:</strong> ${r.score.toFixed(3)}<br><strong>Content:</strong> ${r.content}</p>`
            ).join('<hr>');
            showAlert(`Found ${data.results.length} results`, 'success');
        } else if (!data.success) {
            showAlert(`❌ ${data.error}`, 'danger');
        }
    } catch (e) {
        showAlert('RAG search failed', 'danger');
    }
}

// ── Прочее ────────────────────────────────────────────────────────────────────

/** Очищает активный RAG индекс (кнопка в Settings) */
export async function clearRAGChunks() {
    if (!confirm('Clear the active RAG index? This cannot be undone.')) return;
    try {
        const data = await fetch(`${RAG_API}/clear`, { method: 'POST' }).then(r => r.json());
        showAlert(data.success ? '✅ RAG index cleared' : `❌ ${data.error}`, data.success ? 'success' : 'danger');
        if (data.success) refreshRAGStatus();
    } catch (e) {
        showAlert(`❌ ${e.message}`, 'danger');
    }
}

/** Уведомление при переключении чекбокса Enable RAG */
export function handleRAGToggle(checkbox) {
    showAlert(`RAG system ${checkbox.checked ? 'enabled' : 'disabled'}. Save configuration to apply.`, 'info');
}

// ── Инициализация ─────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    refreshRAGStatus();
    ragLoadProfiles();
});
