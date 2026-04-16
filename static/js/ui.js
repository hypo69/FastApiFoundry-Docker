/**
 * ui.js — Вспомогательные функции интерфейса
 *
 * Содержит:
 *  - showAlert()          — всплывающие уведомления
 *  - updateChatModelBadge() — бейдж активной модели в шапке чата
 *  - updateModelStatus()  — заглушка для статуса модели
 *  - hideProgress()       — скрытие прогресс-бара загрузки
 *  - clearFoundryLogs()   — очистка лога Foundry
 *  - addLog()             — добавление записи в системный лог
 *  - refreshLogs()        — обновление логов с сервера
 *  - filterLogs()         — фильтрация логов по уровню
 */

// ── Уведомления ───────────────────────────────────────────────────────────────

/**
 * Показывает всплывающее уведомление Bootstrap.
 * Автоматически исчезает через 5 секунд.
 * @param {string} message - Текст уведомления
 * @param {'info'|'success'|'warning'|'danger'} type
 */
export function showAlert(message, type = 'info') {
    const container = document.getElementById('alert-container');
    if (!container) return;

    const el = document.createElement('div');
    el.className = `alert alert-${type} alert-dismissible fade show`;
    el.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    container.appendChild(el);

    setTimeout(() => {
        el.classList.remove('show');
        setTimeout(() => el.remove(), 150);
    }, 5000);
}

// ── Модель ────────────────────────────────────────────────────────────────────

/**
 * Обновляет бейдж выбранной модели в шапке чата.
 * Для HuggingFace моделей (hf::) добавляет эмодзи 🤗.
 * @param {string} modelId
 */
export function updateChatModelBadge(modelId) {
    const badge = document.getElementById('chat-model-badge');
    if (!badge) return;
    if (modelId) {
        badge.textContent = modelId.startsWith('hf::') ? '🤗 ' + modelId.slice(4) : modelId;
        badge.style.display = '';
    } else {
        badge.style.display = 'none';
    }
}

/** Заглушка — статус модели выводится только в консоль */
export function updateModelStatus(message, type) {
    console.log(`[Status: ${type}] ${message}`);
}

// ── Прогресс ──────────────────────────────────────────────────────────────────

/** Скрывает блок прогресс-бара загрузки модели */
export function hideProgress() {
    const el = document.getElementById('download-progress');
    if (el) el.style.display = 'none';
}

// ── Foundry логи ──────────────────────────────────────────────────────────────

/** Очищает блок логов Foundry на вкладке Foundry */
export function clearFoundryLogs() {
    const el = document.getElementById('foundry-logs');
    if (el) el.innerHTML = '<div class="text-muted text-center mt-5"><i class="bi bi-terminal"></i><br>Foundry logs cleared</div>';
}

// ── Системные логи (вкладка Logs) ─────────────────────────────────────────────

/**
 * Добавляет запись в контейнер системных логов.
 * @param {string} message
 * @param {'info'|'warning'|'error'|'debug'} level
 */
export function addLog(message, level = 'info') {
    const container = document.getElementById('log-output');
    if (!container) return;

    const ts = new Date().toLocaleTimeString();
    // Добавляем строку в конец pre-блока
    container.textContent += `[${ts}] ${message}\n`;
    container.scrollTop = container.scrollHeight;
}

/**
 * Загружает последние логи с сервера и отображает в #log-output.
 * Вызывается кнопкой Refresh на вкладке Logs.
 */
export async function refreshLogs() {
    const container = document.getElementById('log-output');
    if (!container) return;
    try {
        const data = await fetch(`${window.API_BASE}/logs/recent`).then(r => r.json());
        if (data.logs) {
            container.textContent = data.logs.map(l => `[${l.timestamp || ''}] ${l.message}`).join('\n');
            container.scrollTop = container.scrollHeight;
        }
    } catch (e) {
        console.error('Failed to refresh logs:', e);
    }
}

/**
 * Фильтрует строки лога по выбранному уровню.
 * Работает с текстовым содержимым #log-output.
 */
export function filterLogs() {
    const level  = document.getElementById('log-level-filter')?.value?.toUpperCase();
    const output = document.getElementById('log-output');
    if (!output || !level) return;

    const lines = output.textContent.split('\n');
    output.textContent = lines.filter(l => !level || l.includes(level)).join('\n');
}

/**
 * Скачивает содержимое лога как текстовый файл.
 */
export function downloadLogs() {
    const text = document.getElementById('log-output')?.textContent;
    if (!text) { showAlert('No logs to download', 'warning'); return; }

    const a = Object.assign(document.createElement('a'), {
        href: URL.createObjectURL(new Blob([text], { type: 'text/plain' })),
        download: `foundry-logs-${new Date().toISOString().slice(0, 10)}.txt`
    });
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showAlert('Logs downloaded', 'success');
}

/**
 * Очищает файл лога через API.
 */
export async function clearLogFile() {
    try {
        await fetch(`${window.API_BASE}/logs/clear`, { method: 'POST' });
        const output = document.getElementById('log-output');
        if (output) output.textContent = '';
        showAlert('Log cleared', 'success');
    } catch (e) {
        showAlert('Failed to clear log', 'danger');
    }
}
