/**
 * translation.js — Модуль перевода текста
 *
 * Содержит:
 *  - translateText()             — перевод введённого текста
 *  - translateFile()             — перевод загруженного файла
 *  - saveTranslationSettings()   — сохранение настроек перевода
 *  - downloadTranslationModel()  — скачать модель перевода
 */

import { showAlert } from './ui.js';

// ── Перевод текста ────────────────────────────────────────────────────────────

/**
 * Переводит текст из #text-to-translate и выводит результат в #translated-text.
 * Использует настройки из полей source-lang, target-lang.
 */
export async function translateText() {
    const text = document.getElementById('text-to-translate')?.value.trim();
    if (!text) { showAlert('Enter text to translate', 'warning'); return; }

    const statusEl = document.getElementById('translation-status');
    if (statusEl) {
        statusEl.style.display = '';
        statusEl.innerHTML = '<div class="alert alert-info p-2"><div class="spinner-border spinner-border-sm me-2"></div>Translating...</div>';
    }

    try {
        const data = await fetch(`${window.API_BASE}/translation/translate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text,
                source_lang: document.getElementById('source-lang')?.value || 'en',
                target_lang: document.getElementById('target-lang')?.value || 'ru',
                api_key:     document.getElementById('translation-api-key')?.value.trim() || undefined,
            })
        }).then(r => r.json());

        if (data.success) {
            const out = document.getElementById('translated-text');
            if (out) out.value = data.translated;
            if (statusEl) statusEl.style.display = 'none';
        } else {
            if (statusEl) statusEl.innerHTML = `<div class="alert alert-danger p-2">❌ ${data.error}</div>`;
        }
    } catch (e) {
        if (statusEl) statusEl.innerHTML = `<div class="alert alert-danger p-2">❌ ${e.message}</div>`;
        console.error('Translation failed:', e);
    }
}

// ── Перевод файла ─────────────────────────────────────────────────────────────

/**
 * Переводит загруженный файл через POST /translation/translate-file.
 * Читает файл из input #file-to-translate.
 */
export async function translateFile() {
    const fileInput = document.getElementById('file-to-translate');
    const file = fileInput?.files?.[0];
    if (!file) { showAlert('Select a file first', 'warning'); return; }

    const statusEl = document.getElementById('file-translation-status');
    if (statusEl) {
        statusEl.style.display = '';
        statusEl.innerHTML = '<div class="alert alert-info p-2"><div class="spinner-border spinner-border-sm me-2"></div>Translating file...</div>';
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_lang', document.getElementById('source-lang')?.value || 'en');
    formData.append('target_lang', document.getElementById('target-lang')?.value || 'ru');

    try {
        const data = await fetch(`${window.API_BASE}/translation/translate-file`, {
            method: 'POST',
            body: formData
        }).then(r => r.json());

        if (statusEl) statusEl.innerHTML = data.success
            ? `<div class="alert alert-success p-2">✅ File translated: <code>${data.output_file}</code></div>`
            : `<div class="alert alert-danger p-2">❌ ${data.error}</div>`;
    } catch (e) {
        if (statusEl) statusEl.innerHTML = `<div class="alert alert-danger p-2">❌ ${e.message}</div>`;
        console.error('File translation failed:', e);
    }
}

// ── Настройки ─────────────────────────────────────────────────────────────────

/**
 * Сохраняет настройки перевода (API ключ) в .env через PATCH /config/env.
 */
export async function saveTranslationSettings() {
    const apiKey = document.getElementById('translation-api-key')?.value.trim();
    if (!apiKey) { showAlert('Enter API key', 'warning'); return; }

    try {
        await fetch(`${window.API_BASE}/config/env`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key: 'TRANSLATION_API_KEY', value: apiKey })
        });
        showAlert('Settings saved', 'success');
    } catch (e) {
        showAlert('Failed to save settings', 'danger');
    }
}

// ── Модели перевода ───────────────────────────────────────────────────────────

/**
 * Скачивает выбранную модель перевода через HuggingFace.
 * Читает model ID из select #translation-model-select.
 */
export async function downloadTranslationModel() {
    const modelId = document.getElementById('translation-model-select')?.value;
    if (!modelId) { showAlert('Select a model first', 'warning'); return; }

    const statusEl = document.getElementById('translation-download-status');
    if (statusEl) {
        statusEl.style.display = '';
        statusEl.innerHTML = '<div class="alert alert-info p-2"><div class="spinner-border spinner-border-sm me-2"></div>Downloading...</div>';
    }

    try {
        const data = await fetch(`${window.API_BASE}/hf/models/download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_id: modelId })
        }).then(r => r.json());

        if (statusEl) statusEl.innerHTML = data.success
            ? `<div class="alert alert-success p-2">✅ Downloaded: <code>${data.path}</code></div>`
            : `<div class="alert alert-danger p-2">❌ ${data.error}</div>`;
    } catch (e) {
        if (statusEl) statusEl.innerHTML = `<div class="alert alert-danger p-2">❌ ${e.message}</div>`;
        console.error('Translation model download failed:', e);
    }
}
