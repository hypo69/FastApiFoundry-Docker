/**
 * tabs.js — Builds Bootstrap tab UI from steps array
 */

import { t, applyTranslations } from './i18n.js';

// Per-step metadata: description key, optional flag, extra options HTML
const STEP_META = {
    requirements: {
        desc: 'steps.requirements_desc',
        optional: false,
    },
    rag: {
        desc: 'steps.rag_desc',
        optional: true,
        options: () => `
            <div class="step-options">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="skip-rag">
                    <label class="form-check-label text-muted small" for="skip-rag"
                           data-i18n="steps.rag_opt_skip">Skip RAG</label>
                </div>
            </div>`,
    },
    extras: {
        desc: 'steps.extras_desc',
        optional: true,
        options: () => `
            <div class="step-options">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="skip-extras">
                    <label class="form-check-label text-muted small" for="skip-extras"
                           data-i18n="steps.extras_opt_skip">Skip text extraction</label>
                </div>
            </div>`,
    },
    dev: {
        desc: 'steps.dev_desc',
        optional: true,
        options: () => `
            <div class="step-options">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="skip-dev">
                    <label class="form-check-label text-muted small" for="skip-dev"
                           data-i18n="steps.dev_opt_skip">Skip docs/SDK/tests</label>
                </div>
            </div>`,
    },
    env: {
        desc: 'steps.env_desc',
        optional: false,
        options: () => `
            <div class="step-options">
                <label class="form-label small fw-semibold">HuggingFace Token <span class="text-muted">(optional)</span></label>
                <input id="opt-hf-token" type="password" class="form-control form-control-sm"
                       placeholder="hf_...">
                <div class="form-text">For gated models (Gemma, Llama). Leave empty to skip.</div>
            </div>`,
    },
    foundry: {
        desc: 'steps.foundry_desc',
        optional: true,
        options: () => `
            <div class="step-options">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="skip-foundry">
                    <label class="form-check-label text-muted small" for="skip-foundry"
                           data-i18n="steps.foundry_opt_skip">Skip Foundry</label>
                </div>
            </div>`,
    },
    models: {
        desc: 'steps.models_desc',
        optional: true,
        options: () => `
            <div class="step-options">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="skip-models">
                    <label class="form-check-label text-muted small" for="skip-models"
                           data-i18n="steps.models_opt_skip">Skip model download</label>
                </div>
            </div>`,
    },
    huggingface: {
        desc: 'steps.huggingface_desc',
        optional: true,
        options: () => `
            <div class="step-options">
                <label class="form-label small fw-semibold">HuggingFace Token <span class="text-muted">(optional)</span></label>
                <div class="input-group input-group-sm">
                    <input id="opt-hf-token-hf" type="password" class="form-control"
                           placeholder="hf_...">
                    <button class="btn btn-outline-secondary" type="button"
                            onclick="const i=document.getElementById('opt-hf-token-hf');i.type=i.type==='password'?'text':'password'">👁</button>
                </div>
                <div class="form-text" data-i18n="steps.huggingface_token_hint">For gated models (Gemma, Llama). Leave empty to skip auth.</div>
                <div class="form-text mt-1">
                    <a href="https://huggingface.co/settings/tokens" target="_blank">huggingface.co/settings/tokens</a>
                </div>
                <div class="form-check mt-2">
                    <input class="form-check-input" type="checkbox" id="skip-huggingface">
                    <label class="form-check-label text-muted small" for="skip-huggingface"
                           data-i18n="steps.huggingface_opt_skip">Skip HuggingFace setup</label>
                </div>
            </div>`,
    },
    llama: {
        desc: 'steps.llama_desc',
        optional: true,
        options: () => `
            <div class="step-options">
                <label class="form-label small fw-semibold" data-i18n="steps.llama_models_dir">Models Directory</label>
                <input id="opt-llama-models-dir" type="text" class="form-control form-control-sm font-monospace"
                       placeholder="~/.models">
                <div class="form-text" data-i18n="steps.llama_models_dir_hint">Default from config.json: directories.models</div>
                <div class="form-check mt-2">
                    <input class="form-check-input" type="checkbox" id="skip-llama">
                    <label class="form-check-label text-muted small" for="skip-llama"
                           data-i18n="steps.llama_opt_skip">Skip llama.cpp setup</label>
                </div>
            </div>`,
    },
    shortcuts: {
        desc: 'steps.shortcuts_desc',
        optional: true,
        options: () => `
            <div class="step-options">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="skip-shortcuts">
                    <label class="form-check-label text-muted small" for="skip-shortcuts"
                           data-i18n="steps.shortcuts_opt_skip">Skip shortcuts</label>
                </div>
            </div>`,
    },
};

export function buildTabs(steps) {
    const nav     = document.getElementById('installTabs');
    const content = document.getElementById('installTabsContent');
    if (!nav || !content) return;

    // Header with "Install All" button
    const header = document.createElement('div');
    header.className = 'd-flex align-items-center justify-content-between p-3 bg-white border border-bottom-0 rounded-top';
    header.innerHTML = `
        <span class="fw-semibold fs-6">
            <i class="bi bi-tools me-2 text-primary"></i>
            <span data-i18n="ui.title">Installation Wizard</span>
        </span>
        <button id="btn-run-all" class="btn btn-primary btn-sm">
            <i class="bi bi-play-fill me-1"></i>
            <span data-i18n="ui.run_all">Install All</span>
        </button>`;
    nav.parentElement.insertBefore(header, nav);

    steps.forEach((step, idx) => {
        const isFirst = idx === 0;
        const meta    = STEP_META[step.id] || {};
        const optBadge = meta.optional
            ? `<span class="badge bg-secondary ms-1 fw-normal" style="font-size:.65rem" data-i18n="ui.optional">optional</span>`
            : '';

        // Nav tab button
        const li = document.createElement('li');
        li.className = 'nav-item';
        li.innerHTML = `
            <button class="nav-link ${isFirst ? 'active' : ''} d-flex align-items-center gap-1 py-2 px-3"
                    id="tab-${step.id}"
                    data-bs-toggle="tab"
                    data-bs-target="#pane-${step.id}"
                    type="button">
                <i class="bi ${step.icon} step-icon" id="icon-${step.id}"></i>
                <span data-i18n="${step.label_key}">${step.id}</span>
                ${optBadge}
            </button>`;
        nav.appendChild(li);

        // Options block (checkboxes / inputs)
        const optionsHtml = meta.options ? meta.options() : '';

        // Tab pane
        const pane = document.createElement('div');
        pane.className = `tab-pane fade ${isFirst ? 'show active' : ''}`;
        pane.id = `pane-${step.id}`;
        pane.innerHTML = `
            <div class="step-panel p-4">
                <div class="d-flex align-items-start justify-content-between mb-3">
                    <div>
                        <h5 class="mb-1">
                            <i class="bi ${step.icon} me-2 text-primary"></i>
                            <span data-i18n="${step.label_key}">${step.id}</span>
                        </h5>
                        <p class="text-muted small mb-0" data-i18n="${meta.desc || ''}"></p>
                    </div>
                    <button class="btn btn-primary btn-sm ms-3 flex-shrink-0"
                            data-run-step="${step.id}" id="btn-${step.id}">
                        <i class="bi bi-play-fill me-1"></i>
                        <span data-i18n="ui.run">Run</span>
                    </button>
                </div>
                ${optionsHtml}
                <div id="log-${step.id}" class="step-log"></div>
                <div id="result-${step.id}" class="mt-2 small"></div>
            </div>`;
        content.appendChild(pane);
    });

    // Finish button after last tab pane
    const finish = document.createElement('div');
    finish.className = 'p-3 bg-white border border-top-0 rounded-bottom text-end';
    finish.innerHTML = `
        <button id="btn-finish" class="btn btn-success">
            <i class="bi bi-rocket-takeoff me-1"></i>
            <span data-i18n="ui.finish">Finish &amp; Launch</span>
        </button>`;
    content.after(finish);

    document.getElementById('btn-finish')?.addEventListener('click', async () => {
        await fetch(`${window.API_BASE}/shutdown`, { method: 'POST' }).catch(() => {});
        document.body.innerHTML = `
            <div class="d-flex flex-column align-items-center justify-content-center vh-100 text-center">
                <i class="bi bi-check-circle-fill text-success" style="font-size:4rem"></i>
                <h3 class="mt-3">Installation complete!</h3>
                <p class="text-muted">Run <code>start.ps1</code> to launch FastAPI Foundry.</p>
            </div>`;
    });

    applyTranslations();
}

export function setStepState(stepId, state) {
    const icon = document.getElementById(`icon-${stepId}`);
    const btn  = document.getElementById(`btn-${stepId}`);
    if (!icon) return;

    const map = {
        idle:    'bi-circle text-secondary',
        running: 'bi-arrow-repeat text-warning spin',
        ok:      'bi-check-circle-fill text-success',
        error:   'bi-x-circle-fill text-danger',
    };
    icon.className = `bi step-icon ${map[state] || map.idle}`;
    if (btn) btn.disabled = state === 'running';
}
