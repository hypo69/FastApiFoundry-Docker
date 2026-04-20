/**
 * config.js — Configuration management
 *
 * Handles loading, saving and exchanging settings via /api/v1/config.
 */

import { showAlert } from './ui.js';

// ── Load ──────────────────────────────────────────────────────────────────────

/**
 * Load main config from server and populate global window.CONFIG.
 * Returns the raw response data so app.js can read app.language.
 */
export async function loadConfig() {
    try {
        const response = await fetch(`${window.API_BASE}/config`);
        const data = await response.json();

        if (data.success) {
            window.CONFIG.foundry_url        = data.foundry_ai?.base_url || window.CONFIG.foundry_url;
            window.CONFIG.default_model      = data.foundry_ai?.default_model;
            window.CONFIG.auto_load_default  = data.foundry_ai?.auto_load_default || false;

            // Restore chat settings from config.json
            if (window.applyChatConfig) window.applyChatConfig(data.foundry_ai);

            // Restore llama.cpp port
            const llamaPort = data.config?.llama_cpp?.port || 9780;
            const llamaPortEl = document.getElementById('llama-port');
            if (llamaPortEl) llamaPortEl.value = llamaPort;

            console.log('Config loaded');
            if (window.validateDefaultModel) await window.validateDefaultModel();
        }
        return data;
    } catch (error) {
        console.error('Failed to load config:', error);
        return null;
    }
}

// ── Load fields (Settings tab) ────────────────────────────────────────────────

/**
 * Fill Settings form fields with values from config.json.
 */
export async function loadConfigFields() {
    try {
        const response = await fetch(`${window.API_BASE}/config`);
        const data = await response.json();

        if (!data.success || !data.config) {
            showAlert('Failed to load config fields', 'danger');
            return;
        }

        const { fastapi_server, foundry_ai, docs_server, llama_cpp } = data.config;
        const dirs = data.config?.directories || {};

        const set = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
        const chk = (id, val) => { const el = document.getElementById(id); if (el) el.checked = !!val; };

        // Ports
        set('config-api-port',  fastapi_server?.port || 9696);
        set('config-docs-port', docs_server?.port    || 9697);

        // llama.cpp
        set('config-llama-port',       llama_cpp?.port       || 9780);
        set('config-llama-model-path', llama_cpp?.model_path || '');
        chk('config-llama-autostart',  llama_cpp?.auto_start);

        // Directories
        set('config-dir-models', dirs.models    || '~/.models');
        set('config-dir-rag',    dirs.rag        || '~/.rag');
        set('config-dir-hf',     dirs.hf_models  || '~/.hf_models');

        // FastAPI Server
        set('config-api-host',    fastapi_server?.host || '0.0.0.0');
        set('config-api-mode',    fastapi_server?.mode || 'dev');
        set('config-api-workers', fastapi_server?.workers || 1);
        chk('config-api-auto-port', fastapi_server?.auto_find_free_port);

        // Foundry AI
        set('config-foundry-url',    foundry_ai?.base_url      || '');
        set('config-foundry-model',  foundry_ai?.default_model || '');
        set('config-foundry-temp',   foundry_ai?.temperature   || '');
        set('config-foundry-tokens', foundry_ai?.max_tokens    || '');
        chk('config-foundry-autoload', foundry_ai?.auto_load_default);

        // RAG
        const rag = data.config?.rag_system || {};
        chk('config-rag-enabled', rag.enabled);
        set('config-rag-index', rag.index_dir  || '~/.rag');
        set('config-rag-chunk', rag.chunk_size || 1000);

        // Security
        const sec = data.config?.security || {};
        set('config-security-key', sec.api_key || '');
        chk('config-security-https', sec.https_enabled);

        // Logging
        const log = data.config?.logging || {};
        set('config-log-level', log.level || 'INFO');
        set('config-log-file',  log.file  || '');

        // HuggingFace
        const hf = data.config?.huggingface || {};
        set('config-hf-device',     hf.device     || 'auto');
        set('config-hf-max-tokens', hf.default_max_new_tokens || 512);

        // Docs Server
        chk('config-docs-enabled', docs_server?.enabled);

        // Development
        const dev = data.config?.development || {};
        chk('config-dev-debug',   dev.debug);
        chk('config-dev-verbose', dev.verbose);

        // Text Extractor
        const ext = data.config?.text_extractor || {};
        set('config-extractor-max-size',    ext.max_file_size_mb              ?? 20);
        set('config-extractor-timeout',     ext.processing_timeout_seconds    ?? 300);
        set('config-extractor-ocr-langs',   ext.ocr_languages                 ?? 'rus+eng');
        set('config-extractor-web-timeout', ext.web_page_timeout              ?? 30);
        set('config-extractor-max-images',  ext.max_images_per_page           ?? 20);
        chk('config-extractor-js',          ext.enable_javascript             ?? false);
        chk('config-extractor-limits',      ext.enable_resource_limits        ?? true);

        showAlert('Settings loaded', 'success');
    } catch (error) {
        showAlert('Failed to load config fields', 'danger');
    }
}

// ── Save fields (Settings tab) ────────────────────────────────────────────────

/**
 * Collect all Settings form values and POST to /api/v1/config.
 */
export async function saveConfigFields() {
    try {
        document.getElementById('config-status')?.style && (document.getElementById('config-status').style.display = 'none');

        const get  = id => document.getElementById(id)?.value || '';
        const getN = (id, def) => parseInt(document.getElementById(id)?.value || def);
        const getF = (id, def) => parseFloat(document.getElementById(id)?.value || def);
        const getC = id => document.getElementById(id)?.checked || false;

        const configData = {
            fastapi_server: {
                host:                get('config-api-host') || '0.0.0.0',
                port:                getN('config-api-port', 9696),
                auto_find_free_port: getC('config-api-auto-port'),
                mode:                get('config-api-mode') || 'dev',
                workers:             getN('config-api-workers', 1),
            },
            foundry_ai: {
                base_url:          get('config-foundry-url'),
                default_model:     get('config-foundry-model'),
                temperature:       getF('config-foundry-temp', 0.7),
                max_tokens:        getN('config-foundry-tokens', 2048),
                auto_load_default: getC('config-foundry-autoload'),
            },
            rag_system: {
                enabled:   getC('config-rag-enabled'),
                index_dir: get('config-rag-index') || '~/.rag',
                chunk_size:getN('config-rag-chunk', 1000),
            },
            security: {
                api_key:       get('config-security-key'),
                https_enabled: getC('config-security-https'),
            },
            logging: {
                level: get('config-log-level') || 'INFO',
                file:  get('config-log-file'),
            },
            development: {
                debug:   getC('config-dev-debug'),
                verbose: getC('config-dev-verbose'),
            },
            translator: {
                default_provider:           get('config-translator-provider')       || 'mymemory',
                request_timeout_sec:        getN('config-translator-timeout', 30),
                mymemory_email:             get('config-translator-mymemory-email'),
                libretranslate_url:         get('config-translator-libre-url')      || 'https://libretranslate.com',
                libretranslate_fallback_url:get('config-translator-libre-fallback') || 'https://translate.argosopentech.com',
                libretranslate_api_key:     get('config-translator-libre-key'),
            },
            docs_server: {
                enabled: getC('config-docs-enabled'),
                port:    getN('config-docs-port', 9697),
            },
            llama_cpp: {
                port:       getN('config-llama-port', 9780),
                host:       '127.0.0.1',
                model_path: get('config-llama-model-path'),
                auto_start: getC('config-llama-autostart'),
            },
            directories: {
                models:    get('config-dir-models') || '~/.models',
                rag:       get('config-dir-rag')    || '~/.rag',
                hf_models: get('config-dir-hf')     || '~/.hf_models',
            },
            text_extractor: {
                max_file_size_mb:            getN('config-extractor-max-size', 20),
                processing_timeout_seconds:  getN('config-extractor-timeout', 300),
                ocr_languages:               get('config-extractor-ocr-langs') || 'rus+eng',
                web_page_timeout:            getN('config-extractor-web-timeout', 30),
                max_images_per_page:         getN('config-extractor-max-images', 20),
                enable_javascript:           getC('config-extractor-js'),
                enable_resource_limits:      getC('config-extractor-limits'),
            },
        };

        // Collect HuggingFace fields if module is loaded
        if (typeof window.collectHFConfigFields === 'function') {
            configData.huggingface = window.collectHFConfigFields();
        }

        const response = await fetch(`${window.API_BASE}/config`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ config: configData }),
        });

        const data = await response.json();
        if (data.success) {
            showAlert('Configuration saved', 'success');
            await loadConfig();
        } else {
            showAlert(`Save error: ${data.error || data.detail}`, 'danger');
        }
    } catch (error) {
        showAlert(`Save error: ${error.message}`, 'danger');
    }
}

// ── Export / Import ───────────────────────────────────────────────────────────

export async function exportConfig() {
    // Security warning — the export includes the full .env with all secrets
    const confirmed = confirm(
        '⚠️ ВНИМАНИЕ: Экспорт содержит ПОЛНОЕ содержимое .env файла, включая все токены и ключи API.\n\n' +
        'Храните файл бэкапа в безопасном месте и никому не передавайте.\n\n' +
        'Продолжить экспорт?'
    );
    if (!confirmed) return;

    try {
        const data = await fetch(`${window.API_BASE}/config/export`).then(r => r.json());
        const a = Object.assign(document.createElement('a'), {
            href:     URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })),
            download: `aiassist_config_backup_${new Date().toISOString().slice(2,16).replace(/[-T:]/g, (c) => c === 'T' ? '_' : c === '-' ? '' : '')}.json`,
        });
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
        showAlert('Configuration exported', 'success');
    } catch (e) {
        showAlert('Export failed', 'danger');
    }
}

export async function importConfig(event) {
    const file = event.target.files[0];
    if (!file) return;
    event.target.value = '';
    try {
        const parsed = JSON.parse(await file.text());
        const merge  = confirm('Merge with current configuration?');
        const result = await fetch(`${window.API_BASE}/config/import`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ config: parsed, merge }),
        }).then(r => r.json());

        if (result.success) {
            showAlert('Configuration imported', 'success');
            await loadConfigFields();
        } else {
            showAlert(`Import error: ${result.error}`, 'danger');
        }
    } catch (e) {
        showAlert('Invalid config file', 'danger');
    }
}
