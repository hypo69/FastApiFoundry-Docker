/**
 * app.js — FastAPI Foundry Installer SPA entry point
 *
 * Loads steps from API, builds tab UI, handles SSE streaming per step.
 */

import { initI18n, t, switchLang } from './js/i18n.js';
import { buildTabs, setStepState } from './js/tabs.js';
import { runStep } from './js/runner.js';
import { refreshStatus } from './js/status.js';

window.API_BASE  = window.location.origin + '/api';
window.switchLang = switchLang;

// ── Boot ──────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
    const savedLang = localStorage.getItem('installer_lang') || 'en';
    await initI18n(savedLang);

    // Sync lang selector
    const sel = document.getElementById('lang-selector');
    if (sel) sel.value = savedLang;

    // Load steps from server
    const res   = await fetch(`${window.API_BASE}/steps`).catch(() => null);
    const steps = res?.ok ? await res.json() : [];

    buildTabs(steps);
    refreshStatus();

    // Wire "Run" buttons
    document.getElementById('installTabsContent').addEventListener('click', e => {
        const btn = e.target.closest('[data-run-step]');
        if (!btn) return;
        const stepId = btn.dataset.runStep;
        runStep(stepId, btn);
    });

    // Wire "Run All" button
    document.getElementById('btn-run-all')?.addEventListener('click', () => runAll(steps));
});

async function runAll(steps) {
    for (const step of steps) {
        const btn = document.querySelector(`[data-run-step="${step.id}"]`);
        if (!btn) continue;
        // Switch to that tab
        const tabEl = document.getElementById(`tab-${step.id}`);
        if (tabEl) bootstrap.Tab.getOrCreateInstance(tabEl).show();
        const ok = await runStep(step.id, btn);
        if (!ok) break;
    }
}
