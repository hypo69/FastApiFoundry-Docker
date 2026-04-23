// =============================================================================
// app.js — Main web interface module for FastAPI Foundry
// =============================================================================

import * as ui        from './js/ui.js';
import * as config    from './js/config.js';
import * as models    from './js/models.js';
import * as chat      from './js/chat.js';
import * as foundry   from './js/foundry.js';
import * as rag       from './js/rag.js';
import * as editor    from './js/editor.js';
import * as llama     from './js/llama.js';
import * as hf        from './js/hf.js';
import * as ollama    from './js/ollama.js';
import * as agent     from './js/agent.js';
import * as mcp       from './js/mcp.js';
import * as sdk       from './js/sdk.js';
import * as providers from './js/providers.js';
import { initI18n, switchLang } from './js/i18n.js';
import { initModelBanner, refreshModelBanner } from './js/model-badge.js';

window.API_BASE = window.location.origin + '/api/v1';
window.CONFIG   = { foundry_url: 'http://localhost:50477/v1/', default_model: null };

window.switchLang = switchLang;

Object.assign(window, ui, config, models, chat, foundry, rag, editor, llama, hf, ollama, agent, mcp, sdk, providers);

window.providersRefresh = providers.initProviders;
window.systemRestartService = foundry.systemRestartService;
window.providersExport  = providers.exportToExtension;
window.providersImport  = (e) => { const f = e.target.files?.[0]; if (f) providers.importFromExtension(f); e.target.value = ''; };

// ── Partial loader ────────────────────────────────────────────────────────────

async function fetchPartial(path) {
    try {
        const r = await fetch(path);
        return r.ok ? await r.text() : '';
    } catch (e) {
        console.error(`[partials] Failed to load ${path}:`, e);
        return '';
    }
}

async function loadAllPartials() {
    const base = '/static/partials';

    // Slots with their own id (navbar, tabs nav, modals)
    const slots = [
        ['slot-navbar',   `${base}/_navbar.html`],
        ['slot-tabs-nav', `${base}/_tabs_nav.html`],
    ];
    for (const [id, path] of slots) {
        const el = document.getElementById(id);
        if (el) el.innerHTML = await fetchPartial(path);
    }

    // Tab panes — must be direct children of .tab-content
    const tabContent = document.getElementById('mainTabsContent');
    if (tabContent) {
        const tabs = [
            `${base}/_tab_chat.html`,
            `${base}/_tab_models.html`,
            `${base}/_tab_foundry.html`,
            `${base}/_tab_hf.html`,
            `${base}/_tab_llama.html`,
            `${base}/_tab_rag.html`,
            `${base}/_tab_settings_shell.html`,
            `${base}/_tab_editor.html`,
            `${base}/_tab_mcp.html`,
            `${base}/_tab_agent.html`,
            `${base}/_tab_providers.html`,
            `${base}/_tab_logs.html`,
            `${base}/_tab_docs.html`,
        ];
        const htmlParts = await Promise.all(tabs.map(fetchPartial));
        tabContent.innerHTML = htmlParts.join('');
    }

    // Settings sections — injected into #settings-card-body
    const settingsBody = document.getElementById('settings-card-body');
    if (settingsBody) {
        const sections = [
            `${base}/_tab_settings_server.html`,
            `${base}/_tab_settings_dirs.html`,
            `${base}/_tab_settings_foundry.html`,
            `${base}/_tab_settings_models.html`,
            `${base}/_tab_settings_rag.html`,
            `${base}/_tab_settings_security.html`,
            `${base}/_tab_settings_logging.html`,
            `${base}/_tab_settings_dev.html`,
        ];
        const sectionParts = await Promise.all(sections.map(fetchPartial));
        // Insert before the status alert (last child)
        const statusEl = settingsBody.querySelector('#settings-status');
        sectionParts.forEach(html => {
            if (html) statusEl.insertAdjacentHTML('beforebegin', html);
        });
    }

    // Modals — appended to body
    const modals = [
        `${base}/_modal_llama_picker.html`,
        `${base}/_modal_add_model.html`,
    ];
    const modalHtml = await Promise.all(modals.map(fetchPartial));
    modalHtml.forEach(html => { if (html) document.body.insertAdjacentHTML('beforeend', html); });
}

// ── Boot ──────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
    await loadAllPartials();

    const cfg  = await config.loadConfig();
    const lang = cfg?.config?.app?.language || '';
    await initI18n(lang);

    // Show/hide custom model input when radio changes
    document.addEventListener('change', e => {
        if (e.target.name === 'startup-model-mode') {
            const row = document.getElementById('startup-custom-model-row');
            if (row) row.style.display = e.target.value === 'custom' ? '' : 'none';
        }
    });

    foundry.checkSystemStatus();
    setInterval(foundry.checkSystemStatus, 30_000);

    initModelBanner();
    window.refreshModelBanner = refreshModelBanner;

    models.loadModels().then(async () => {
        // Determine which model to select based on startup_model_mode
        const startupMode = cfg?.config?.foundry_ai?.startup_model_mode || 'default';
        if (startupMode === 'active') {
            await models.syncChatModelToActive();
        } else if (startupMode === 'custom') {
            const customId = cfg?.config?.foundry_ai?.startup_custom_model || '';
            const select = document.getElementById('chat-model');
            if (customId && select && [...select.options].some(o => o.value === customId)) {
                select.value = customId;
                window._savedChatModel = customId;
            } else {
                await models.syncChatModelToActive();
            }
        } else {
            // 'default' — use saved default_model from config, already set by applyChatConfig
            // but still sync to active if nothing is selected
            const select = document.getElementById('chat-model');
            if (!select?.value) await models.syncChatModelToActive();
        }
        // Refresh banner AFTER dropdown is fully populated and synced
        refreshModelBanner();
    });
    models.loadConnectedModels();
    models.initModelSelectListener();

    document.getElementById('mainTabsContent')?.addEventListener('keypress', e => {
        if (e.target.id === 'chat-input' && e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            window.sendMessage?.();
        }
        if (e.target.id === 'agent-input' && e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            window.agentRun?.();
        }
    });

    // Lazy tab loading
    document.getElementById('foundry-tab')?.addEventListener('shown.bs.tab',     () => { window.listCachedFoundryModels?.(); });
    document.getElementById('editor-tab')?.addEventListener('shown.bs.tab',    () => { window.loadEnv?.(); window.loadConfigJson?.(); });
    document.getElementById('llama-tab')?.addEventListener('shown.bs.tab',     () => { window.llamaCheckStatus?.(); window.llamaScanModels?.(); window.ollamaCheckStatus?.(); window.ollamaLoadModels?.(); });
    document.getElementById('hf-tab')?.addEventListener('shown.bs.tab',        () => { window.hfCheckStatus?.(); window.hfRefreshModels?.(); window.hfLoadHubModels?.(); });
    document.getElementById('rag-tab')?.addEventListener('shown.bs.tab',       () => { window.refreshRAGStatus?.(); window.ragLoadProfiles?.(); });
    document.getElementById('agent-tab')?.addEventListener('shown.bs.tab',     () => { window.agentLoadTools?.(); });
    document.getElementById('mcp-tab')?.addEventListener('shown.bs.tab',       () => { window.mcpLoadServers?.(); });
    document.getElementById('settings-tab')?.addEventListener('shown.bs.tab',  () => { window.loadConfigFields?.(); window.refreshLogHealth?.(); });
    document.getElementById('providers-tab')?.addEventListener('shown.bs.tab', () => { window.providersRefresh?.(); });
    let _logViewerInited = false;
    document.getElementById('logs-tab')?.addEventListener('shown.bs.tab', () => {
        if (!_logViewerInited) { window.initLogViewer?.(); _logViewerInited = true; }
        else { window.refreshLogs?.(); }
    });
});
