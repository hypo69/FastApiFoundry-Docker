/**
 * status.js — Polls /api/status and updates status bar chips
 */

export async function refreshStatus() {
    const res = await fetch(`${window.API_BASE}/status`).catch(() => null);
    if (!res?.ok) return;
    const s = await res.json();

    _chip('status-venv',   s.venv,    'venv');
    _chip('status-env',    s.env,     '.env');
    _chip('status-foundry', s.foundry, 'Foundry');
}

function _chip(id, ok, label) {
    const el = document.getElementById(id);
    if (!el) return;
    el.className = 'status-chip ' + (ok ? 'ok' : '');
    el.innerHTML = `<i class="bi ${ok ? 'bi-check-circle-fill' : 'bi-circle'}"></i> ${label}`;
}
