/**
 * agent.js — AI Агент
 *
 * Содержит:
 *  - agentLoadTools()    — загрузка списка агентов и инструментов
 *  - agentRefreshTools() — обновление инструментов выбранного агента
 *  - agentRun()          — выполнение задачи агентом
 *  - runAgentExample()   — запуск примера агента
 */

import { showAlert } from './ui.js';

const AGENT_API = '/api/v1/agent';

// ── Инструменты ───────────────────────────────────────────────────────────────

/**
 * Загружает список доступных агентов в select #agent-name,
 * затем загружает инструменты выбранного агента.
 */
export async function agentLoadTools() {
    try {
        const dl = await fetch(`${AGENT_API}/list`).then(r => r.json());
        const sel = document.getElementById('agent-name');
        if (sel && dl.success) {
            sel.innerHTML = dl.agents.map(a =>
                `<option value="${a.name}" title="${a.description}">${a.name}</option>`
            ).join('');
        }
    } catch (e) {
        console.error('Failed to load agent list:', e);
    }
    await agentRefreshTools();
}

/**
 * Обновляет список инструментов для выбранного агента.
 * Отображает в #agent-tools-list.
 */
export async function agentRefreshTools() {
    const el   = document.getElementById('agent-tools-list');
    const name = document.getElementById('agent-name')?.value || 'powershell';
    if (!el) return;

    el.innerHTML = '<div class="text-center p-3"><div class="spinner-border spinner-border-sm"></div> Loading tools...</div>';
    try {
        const d = await fetch(`${AGENT_API}/${name}/tools`).then(r => r.json());
        if (!d.success) { el.innerHTML = `<div class="text-danger p-2">Error: ${d.detail || 'Unknown error'}</div>`; return; }

        el.innerHTML = d.tools.map(t => `
            <div class="px-3 py-2 border-bottom">
                <strong style="font-size:.8rem">${t}</strong>
                <div class="text-muted" style="font-size:.75rem">${d.descriptions?.[t] || ''}</div>
            </div>`).join('');
    } catch (e) {
        el.innerHTML = `<div class="text-danger p-2">${e.message}</div>`;
        console.error('Failed to load agent tools:', e);
    }
}

// ── Выполнение ────────────────────────────────────────────────────────────────

/**
 * Отправляет задачу агенту и отображает результат в #agent-messages.
 * Показывает вызовы инструментов и финальный ответ.
 */
export async function agentRun() {
    const input   = document.getElementById('agent-input');
    const btn     = document.getElementById('agent-btn');
    const msgs    = document.getElementById('agent-messages');
    const message = input?.value.trim();
    if (!message) return;

    // Добавляем сообщение пользователя
    if (msgs) {
        msgs.querySelector('.text-muted.text-center')?.remove();
        msgs.innerHTML += `<div class="mb-2"><span class="badge bg-primary">You</span> ${message}</div>`;
    }
    input.value = '';
    if (btn) { btn.disabled = true; btn.innerHTML = '<div class="spinner-border spinner-border-sm"></div>'; }

    // Индикатор "думает"
    const thinkId = `think-${Date.now()}`;
    if (msgs) {
        msgs.innerHTML += `<div id="${thinkId}" class="mb-2 text-muted"><i class="bi bi-gear-fill"></i> Агент думает...</div>`;
        msgs.scrollTop = msgs.scrollHeight;
    }

    try {
        const d = await fetch(`${AGENT_API}/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message,
                agent:          document.getElementById('agent-name')?.value    || 'powershell',
                model:          document.getElementById('agent-model')?.value.trim() || undefined,
                temperature:    parseFloat(document.getElementById('agent-temp')?.value     || '0.3'),
                max_iterations: parseInt(document.getElementById('agent-max-iter')?.value   || '5'),
            })
        }).then(r => r.json());

        document.getElementById(thinkId)?.remove();

        if (msgs) {
            // Показываем вызовы инструментов
            for (const tc of (d.tool_calls || [])) {
                msgs.innerHTML += `
                    <div class="mb-2 p-2 border rounded" style="background:#f0f4ff;font-size:.82rem">
                        <i class="bi bi-gear"></i> <strong>${tc.tool}</strong>
                        <code class="d-block mt-1 text-muted">${JSON.stringify(tc.arguments)}</code>
                        <pre class="mt-1 mb-0" style="font-size:.78rem;max-height:120px;overflow-y:auto;white-space:pre-wrap">${tc.result}</pre>
                    </div>`;
            }
            // Финальный ответ
            msgs.innerHTML += d.success
                ? `<div class="mb-3"><span class="badge bg-success">Agent</span> <span style="white-space:pre-wrap">${d.answer || ''}</span></div>`
                : `<div class="mb-2 text-danger">❌ ${d.error}</div>`;
        }
    } catch (e) {
        document.getElementById(thinkId)?.remove();
        if (msgs) msgs.innerHTML += `<div class="mb-2 text-danger">❌ ${e.message}</div>`;
        console.error('Agent run failed:', e);
    } finally {
        if (btn) { btn.disabled = false; btn.innerHTML = '<i class="bi bi-send"></i> Run'; }
        if (msgs) msgs.scrollTop = msgs.scrollHeight;
    }
}

/** Запускает демонстрационный пример агента */
export async function runAgentExample() {
    const output = document.getElementById('agent-output');
    if (!output) return;
    output.style.display = '';
    output.textContent = '⏳ Running example...';
    try {
        const d = await fetch(`${AGENT_API}/example`, { method: 'POST' }).then(r => r.json());
        output.textContent = d.success ? d.result || d.answer : `❌ ${d.error}`;
    } catch (e) {
        output.textContent = `❌ ${e.message}`;
    }
}
