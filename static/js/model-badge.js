/**
 * model-badge.js — Global active model banner with resource monitor
 *
 * Polls loaded models (Foundry, llama.cpp, HF) every 10 s.
 * Updates #active-model-banner above the tab bar.
 *
 * File: js/model-badge.js
 * Project: FastApiFoundry (Docker)
 * Version: 0.6.0
 * Author: hypo69
 * Copyright: © 2026 hypo69
 */

let _bannerTimer = null;

/**
 * Fetch the currently active model info from all backends.
 * Returns { name, size, backend, ram_mb, cpu_pct } or null.
 */
async function _fetchActiveModel() {
    const base = window.API_BASE;

    // Run all probes in parallel; ignore individual failures
    const [foundry, llama, hf, health] = await Promise.allSettled([
        fetch(`${base}/foundry/models/loaded`).then(r => r.json()),
        fetch(`${base}/llama/status`).then(r => r.json()),
        fetch(`${base}/hf/models`).then(r => r.json()),
        fetch(`${base}/health`).then(r => r.json()),
    ]);

    // Foundry loaded model — only show if Foundry service is actually reachable
    const foundryData = foundry.status === 'fulfilled' ? foundry.value : null;
    if (foundryData?.success && foundryData.models?.length) {
        const m = foundryData.models[0];
        const size = _lookupSize(m.id);
        return { name: m.id, size, backend: 'Foundry', ...await _sysStats(health) };
    }

    // llama.cpp running — check before falling through
    const llamaData = llama.status === 'fulfilled' ? llama.value : null;
    if (llamaData?.running) {
        // Get model name from llama /v1/models
        let llamaName = 'llama.cpp model';
        try {
            const lm = await fetch(`${llamaData.openai_url}/models`).then(r => r.json());
            if (lm.data?.[0]?.id) llamaName = lm.data[0].id;
        } catch (_) {}
        return { name: llamaName, size: null, backend: 'llama.cpp', ...await _sysStats(health) };
    }

    // HuggingFace loaded model
    const hfData = hf.status === 'fulfilled' ? hf.value : null;
    if (hfData?.loaded?.length) {
        const m = hfData.loaded[0];
        return { name: m.id || m.name, size: null, backend: 'HuggingFace 🤗', ...await _sysStats(health) };
    }

    return null;
}

/** Extract RAM / CPU from health response (if psutil data present). */
async function _sysStats(healthSettled) {
    // health endpoint doesn't expose psutil yet — try /api/v1/system/stats if available
    try {
        const s = await fetch(`${window.API_BASE}/system/stats`).then(r => r.json());
        if (s.success) {
            return { ram_mb: s.ram_used_mb, ram_total_mb: s.ram_total_mb, cpu_pct: s.cpu_pct };
        }
    } catch (_) {}
    return { ram_mb: null, ram_total_mb: null, cpu_pct: null };
}

/** Look up model size from the Foundry available list (window._foundryModels cache). */
function _lookupSize(modelId) {
    const list = window._foundryModelsCache || [];
    return list.find(m => m.id === modelId)?.size || null;
}

/** Render the banner content. */
function _renderBanner(info) {
    const banner = document.getElementById('active-model-banner');
    if (!banner) return;

    if (!info) {
        banner.innerHTML = `
            <span class="text-muted small">
                <i class="bi bi-cpu me-1"></i>
                <span data-i18n="banner.no_model">No model loaded</span>
            </span>`;
        banner.className = 'active-model-banner active-model-banner--idle';
        return;
    }

    const sizePart  = info.size  ? ` <span class="badge bg-secondary ms-1">${info.size}</span>` : '';
    const backendPart = `<span class="badge bg-primary ms-2">${info.backend}</span>`;

    let statsPart = '';
    if (info.ram_mb != null) {
        const ramGb = (info.ram_mb / 1024).toFixed(1);
        const totalGb = info.ram_total_mb ? ` / ${(info.ram_total_mb / 1024).toFixed(1)} GB` : '';
        statsPart += `<span class="active-model-stat"><i class="bi bi-memory me-1"></i>${ramGb}${totalGb} GB RAM</span>`;
    }
    if (info.cpu_pct != null) {
        statsPart += `<span class="active-model-stat ms-3"><i class="bi bi-speedometer2 me-1"></i>${info.cpu_pct.toFixed(1)}% CPU</span>`;
    }

    banner.innerHTML = `
        <span class="active-model-label">
            <i class="bi bi-robot me-2"></i>
            <strong>${info.name}</strong>${sizePart}${backendPart}
        </span>
        ${statsPart ? `<span class="active-model-stats ms-4">${statsPart}</span>` : ''}`;
    banner.className = 'active-model-banner active-model-banner--active';
}

/** Poll and update the banner. */
async function _poll() {
    try {
        const info = await _fetchActiveModel();
        _renderBanner(info);
    } catch (e) {
        console.warn('[model-badge] poll error:', e);
    }
}

/** Start polling. Call once after DOM is ready. */
export function initModelBanner() {
    _poll();
    _bannerTimer = setInterval(_poll, 10_000);
}

/**
 * Force immediate refresh.
 * If modelInfo is provided, renders it directly without polling.
 * @param {{ name: string, backend: string, size?: string }|null} [modelInfo]
 */
export function refreshModelBanner(modelInfo) {
    if (modelInfo) {
        _renderBanner(modelInfo);
        return;
    }
    _poll();
}
