/**
 * rag.js — Система RAG (Retrieval-Augmented Generation)
 *
 * Содержит:
 *  - refreshRAGStatus()  — обновление статуса RAG системы
 *  - saveRAGConfig()     — сохранение настроек RAG
 *  - ragLoadDirs()       — список директорий для индексации
 *  - ragBuildIndex()     — сборка индекса
 *  - ragClearIndex()     — очистка индекса
 *  - clearRAGChunks()    — алиас ragClearIndex (для кнопки в Settings)
 *  - testRAGSearch()     — тестовый поиск по индексу
 *  - handleRAGToggle()   — обработка чекбокса Enable RAG
 */

import { showAlert } from './ui.js';

// ── Статус ────────────────────────────────────────────────────────────────────

/**
 * Запрашивает статус RAG системы и обновляет блок #rag-status.
 * Также синхронизирует чекбокс #rag-enabled.
 */
export async function refreshRAGStatus() {
    const el = document.getElementById('rag-status');
    if (!el) return;
    try {
        const data = await fetch(`${window.API_BASE}/rag/status`).then(r => r.json());
        if (!data.success) return;

        el.innerHTML = `
            <p><strong>Status:</strong> <span class="badge ${data.enabled ? 'bg-success' : 'bg-secondary'}">${data.enabled ? 'Enabled' : 'Disabled'}</span></p>
            <p><strong>Index:</strong> <code>${data.index_dir}</code></p>
            <p><strong>Chunks:</strong> ${data.total_chunks}</p>
            <p><strong>Model:</strong> ${data.model}</p>
            <p><strong>Chunk size:</strong> ${data.chunk_size} &nbsp;·&nbsp; <strong>Top K:</strong> ${data.top_k}</p>`;

        const cb = document.getElementById('rag-enabled');
        if (cb) cb.checked = data.enabled;
    } catch (e) {
        console.error('RAG status refresh failed:', e);
    }
}

// ── Конфигурация ──────────────────────────────────────────────────────────────

/**
 * Сохраняет настройки RAG через PUT /rag/config.
 * Читает поля формы на вкладке RAG.
 */
export async function saveRAGConfig() {
    try {
        const data = await fetch(`${window.API_BASE}/rag/config`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                enabled:   document.getElementById('rag-enabled')?.checked,
                index_dir: document.getElementById('rag-index-dir')?.value  || './rag_index',
                model:     document.getElementById('rag-model')?.value      || 'sentence-transformers/all-MiniLM-L6-v2',
                top_k:     parseInt(document.getElementById('rag-top-k')?.value    || '5'),
                chunk_size:parseInt(document.getElementById('rag-chunk-size')?.value || '1000'),
            })
        }).then(r => r.json());

        if (data.success) { showAlert('RAG configuration saved', 'success'); refreshRAGStatus(); }
        else showAlert(`Error: ${data.error}`, 'danger');
    } catch (e) {
        showAlert('Error saving RAG config', 'danger');
    }
}

// ── Директории ────────────────────────────────────────────────────────────────

/**
 * Загружает список доступных директорий для индексации в select #rag-docs-dir.
 */
export async function ragLoadDirs() {
    const select = document.getElementById('rag-docs-dir');
    if (!select) return;
    select.innerHTML = '<option value="">Loading...</option>';
    try {
        const data = await fetch(`${window.API_BASE}/rag/dirs`).then(r => r.json());
        select.innerHTML = '<option value="">Select a directory...</option>';
        (data.dirs || []).forEach(dir => {
            const opt = document.createElement('option');
            opt.value = opt.textContent = dir;
            select.appendChild(opt);
        });
        if (!data.dirs?.length) select.innerHTML = '<option value="">No directories found</option>';
    } catch (e) {
        select.innerHTML = '<option value="">Error loading directories</option>';
        console.error('Failed to load RAG directories:', e);
    }
}

// ── Индекс ────────────────────────────────────────────────────────────────────

/**
 * Запускает сборку RAG индекса через POST /rag/build.
 * Показывает прогресс в #rag-build-status.
 */
export async function ragBuildIndex() {
    const sourceDir = document.getElementById('rag-docs-dir-manual')?.value.trim()
                   || document.getElementById('rag-docs-dir')?.value;
    if (!sourceDir) { showAlert('Please select or enter a directory to index.', 'warning'); return; }

    const statusEl = document.getElementById('rag-build-status');
    const buildBtn = document.getElementById('rag-build-btn');

    if (buildBtn) buildBtn.disabled = true;
    if (statusEl) {
        statusEl.style.display = '';
        statusEl.innerHTML = '<div class="alert alert-info p-2"><div class="spinner-border spinner-border-sm me-2"></div>Building index...</div>';
    }

    try {
        const data = await fetch(`${window.API_BASE}/rag/build`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source_dir:      sourceDir,
                output_dir:      document.getElementById('rag-build-output')?.value || './rag_index',
                chunk_size:      parseInt(document.getElementById('rag-build-chunk')?.value  || '1000'),
                chunk_overlap:   parseInt(document.getElementById('rag-build-overlap')?.value || '50'),
                embedding_model: document.getElementById('rag-build-model')?.value || 'sentence-transformers/all-mpnet-base-v2',
            })
        }).then(r => r.json());

        if (statusEl) statusEl.innerHTML = data.success
            ? `<div class="alert alert-success p-2">✅ Built: ${data.indexed_files} files, ${data.total_chunks} chunks.</div>`
            : `<div class="alert alert-danger p-2">❌ ${data.error}</div>`;

        if (data.success) refreshRAGStatus();
    } catch (e) {
        if (statusEl) statusEl.innerHTML = `<div class="alert alert-danger p-2">❌ ${e.message}</div>`;
        console.error('RAG build index failed:', e);
    } finally {
        if (buildBtn) buildBtn.disabled = false;
    }
}

/**
 * Очищает RAG индекс через POST /rag/clear.
 * Запрашивает подтверждение перед удалением.
 */
export async function ragClearIndex() {
    if (!confirm('Clear the RAG index? This cannot be undone.')) return;

    const statusEl = document.getElementById('rag-build-status');
    if (statusEl) {
        statusEl.style.display = '';
        statusEl.innerHTML = '<div class="alert alert-info p-2"><div class="spinner-border spinner-border-sm me-2"></div>Clearing...</div>';
    }
    try {
        const data = await fetch(`${window.API_BASE}/rag/clear`, { method: 'POST' }).then(r => r.json());
        if (statusEl) statusEl.innerHTML = data.success
            ? '<div class="alert alert-success p-2">✅ RAG index cleared.</div>'
            : `<div class="alert alert-danger p-2">❌ ${data.error}</div>`;
        if (data.success) refreshRAGStatus();
    } catch (e) {
        if (statusEl) statusEl.innerHTML = `<div class="alert alert-danger p-2">❌ ${e.message}</div>`;
        console.error('RAG clear index failed:', e);
    }
}

/** Алиас ragClearIndex — используется кнопкой "Очистить RAG chunks" в Settings */
export async function clearRAGChunks() {
    await ragClearIndex();
}

// ── Поиск ─────────────────────────────────────────────────────────────────────

/**
 * Выполняет тестовый поиск по RAG индексу.
 * Читает запрос из #rag-test-query, результаты выводит в #rag-search-output.
 */
export async function testRAGSearch() {
    const query = document.getElementById('rag-test-query')?.value.trim();
    if (!query) { showAlert('Enter a search query', 'warning'); return; }

    try {
        const data = await fetch(`${window.API_BASE}/rag/search`, {
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
        }
    } catch (e) {
        showAlert('RAG search failed', 'danger');
    }
}

// ── Прочее ────────────────────────────────────────────────────────────────────

/** Показывает уведомление при переключении чекбокса Enable RAG */
export function handleRAGToggle(checkbox) {
    showAlert(`RAG system ${checkbox.checked ? 'enabled' : 'disabled'}. Save configuration to apply.`, 'info');
}

// ── Инициализация ─────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    // Загружаем статус RAG и список директорий при старте
    refreshRAGStatus();
    ragLoadDirs();
});
