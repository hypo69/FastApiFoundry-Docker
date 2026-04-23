/**
 * runner.js — SSE step runner
 */

import { setStepState } from './tabs.js';

export function runStep(stepId, btn) {
    return new Promise(resolve => {
        const log    = document.getElementById(`log-${stepId}`);
        const result = document.getElementById(`result-${stepId}`);
        if (!log) return resolve(false);

        // Collect skip flag from checkbox
        const skipBox = document.getElementById(`skip-${stepId}`);
        const skip    = skipBox?.checked;
        if (skip) {
            log.textContent = '— skipped —';
            setStepState(stepId, 'ok');
            result.innerHTML = '<span class="text-success small"><i class="bi bi-check-circle-fill"></i> Skipped</span>';
            return resolve(true);
        }

        log.textContent = '';
        result.innerHTML = '';
        setStepState(stepId, 'running');
        if (btn) btn.disabled = true;

        // For huggingface step — pass token as query param
        let url = `${window.API_BASE}/run/${stepId}`;
        if (stepId === 'huggingface') {
            const token = document.getElementById('opt-hf-token-hf')?.value?.trim() || '';
            if (token) url += `?token=${encodeURIComponent(token)}`;
        }
        if (stepId === 'llama') {
            const dir = document.getElementById('opt-llama-models-dir')?.value?.trim() || '';
            if (dir) url += `?models_dir=${encodeURIComponent(dir)}`;
        }

        const es = new EventSource(url);

        es.onmessage = e => {
            const data = JSON.parse(e.data);
            if (data.line) {
                const span = document.createElement('span');
                span.className = data.line.match(/error|fail|ERR/i) ? 'line-err' : '';
                span.textContent = data.line + '\n';
                log.appendChild(span);
                log.scrollTop = log.scrollHeight;
            }
            if (data.done) {
                es.close();
                const ok = data.code === 0;
                setStepState(stepId, ok ? 'ok' : 'error');
                if (btn) btn.disabled = false;
                result.innerHTML = ok
                    ? '<span class="text-success small"><i class="bi bi-check-circle-fill"></i> Done</span>'
                    : `<span class="text-danger small"><i class="bi bi-x-circle-fill"></i> Failed (exit ${data.code})</span>`;
                resolve(ok);
            }
        };

        es.onerror = () => {
            es.close();
            setStepState(stepId, 'error');
            if (btn) btn.disabled = false;
            log.textContent += '\n[connection error]';
            resolve(false);
        };
    });
}
