/**
 * tabs.js — Builds Bootstrap tab UI from steps array
 */

import { t, applyTranslations } from './i18n.js';

// Step descriptions shown in each tab panel
const STEP_DESCRIPTIONS = {
    check_python:  { desc_key: 'steps.check_python_desc',  optional: false },
    venv:          { desc_key: 'steps.venv_desc',          optional: false },
    pip_upgrade:   { desc_key: 'steps.pip_upgrade_desc',   optional: false },
    requirements:  { desc_key: 'steps.requirements_desc',  optional: false },
    rag:           { desc_key: 'steps.rag_desc',           optional: true  },
    env:           { desc_key: 'steps.env_desc',           optional: false },
    foundry:       { desc_key: 'steps.foundry_desc',       optional: true  },
    models:        { desc_key: 'steps.models_desc',        optional: true  },
    shortcuts:     { desc_key: 'steps.shortcuts_desc',     optional: true  },
};

export function buildTabs(steps) {
    const nav     = document.getElementById('installTabs');
    const content = document.getElementById('installTabsContent');
    if (!nav || !content) return;

    // "Run All" header row
    const header = document.createElement('div');
    header.className = 'install-header d-flex align-items-center justify-content-between mb-0 p-3 border-bottom bg-light';
    header.innerHTML = `
        <span class="fw-semibold" data-i18n="ui.title">Installation Wizard</span>
        <button id="btn-run-all" class="btn btn-primary btn-sm">
            <i class="bi bi-play-fill"></i>
            <span data-i18n="ui.run_all">Run All Steps</span>
        </button>`;
    nav.parentElement.insertBefore(header, nav);

    steps.forEach((step, idx) => {
        const isFirst  = idx === 0;
        const meta     = STEP_DESCRIPTIONS[step.id] || {};
        const optional = meta.optional ? `<span class="badge bg-secondary ms-1" data-i18n="ui.optional">optional</span>` : '';

        // Tab button
        const li = document.createElement('li');
        li.className = 'nav-item';
        li.innerHTML = `
            <button class="nav-link ${isFirst ? 'active' : ''} d-flex align-items-center gap-1"
                    id="tab-${step.id}"
                    data-bs-toggle="tab"
                    data-bs-target="#pane-${step.id}"
                    type="button">
                <i class="bi ${step.icon} step-icon" id="icon-${step.id}"></i>
                <span data-i18n="${step.label_key}">${step.id}</span>
                ${optional}
            </button>`;
        nav.appendChild(li);

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
                        <p class="text-muted small mb-0" data-i18n="${meta.desc_key || ''}"></p>
                    </div>
                    <button class="btn btn-primary btn-sm" data-run-step="${step.id}" id="btn-${step.id}">
                        <i class="bi bi-play-fill"></i>
                        <span data-i18n="ui.run">Run</span>
                    </button>
                </div>
                <div id="log-${step.id}" class="step-log"></div>
                <div id="result-${step.id}" class="mt-2"></div>
            </div>`;
        content.appendChild(pane);
    });

    applyTranslations();
}

export function setStepState(stepId, state) {
    // state: 'idle' | 'running' | 'ok' | 'error'
    const icon = document.getElementById(`icon-${stepId}`);
    const btn  = document.getElementById(`btn-${stepId}`);
    if (!icon) return;

    icon.className = 'bi step-icon ' + {
        idle:    'bi-circle text-secondary',
        running: 'bi-arrow-repeat text-warning spin',
        ok:      'bi-check-circle-fill text-success',
        error:   'bi-x-circle-fill text-danger',
    }[state];

    if (btn) {
        btn.disabled = state === 'running';
    }
}
