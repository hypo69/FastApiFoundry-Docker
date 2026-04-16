// =============================================================================
// app.js — Main web interface module for FastAPI Foundry
// =============================================================================

import * as ui      from './js/ui.js';
import * as config  from './js/config.js';
import * as models  from './js/models.js';
import * as chat    from './js/chat.js';
import * as foundry from './js/foundry.js';
import * as rag     from './js/rag.js';
import * as editor  from './js/editor.js';
import * as llama   from './js/llama.js';
import * as hf      from './js/hf.js';
import * as agent   from './js/agent.js';
import * as mcp     from './js/mcp.js';
import * as sdk     from './js/sdk.js';
import { initI18n, switchLang } from './js/i18n.js';

window.API_BASE = window.location.origin + '/api/v1';
window.CONFIG   = { foundry_url: 'http://localhost:50477/v1/', default_model: null };

// switchLang must be on window before i18n init since navbar calls it
window.switchLang = switchLang;

Object.assign(window, ui, config, models, chat, foundry, rag, editor, llama, hf, agent, mcp, sdk);

document.addEventListener('DOMContentLoaded', async () => {
    const cfg  = await config.loadConfig();
    // Empty string triggers browser language auto-detection
    const lang = cfg?.config?.app?.language || '';
    await initI18n(lang);

    foundry.checkSystemStatus();
    setInterval(foundry.checkSystemStatus, 30_000);

    document.getElementById('chat-input')?.addEventListener('keypress', e => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); window.sendMessage?.(); }
    });

    // Lazy tab loading — data loads only when tab is first opened
    document.getElementById('editor-tab')?.addEventListener('shown.bs.tab',   () => { window.loadEnv?.(); window.loadConfigJson?.(); });
    document.getElementById('llama-tab')?.addEventListener('shown.bs.tab',    () => { window.llamaCheckStatus?.(); window.llamaScanModels?.(); });
    document.getElementById('hf-tab')?.addEventListener('shown.bs.tab',       () => { window.hfCheckStatus?.(); window.hfRefreshModels?.(); window.hfLoadHubModels?.(); });
    document.getElementById('rag-tab')?.addEventListener('shown.bs.tab',      () => { window.refreshRAGStatus?.(); window.ragLoadProfiles?.(); });
    document.getElementById('agent-tab')?.addEventListener('shown.bs.tab',    () => { window.agentLoadTools?.(); });
    document.getElementById('mcp-tab')?.addEventListener('shown.bs.tab',      () => { window.mcpLoadServers?.(); });
    document.getElementById('settings-tab')?.addEventListener('shown.bs.tab', () => { window.loadConfigFields?.(); });
    document.getElementById('logs-tab')?.addEventListener('shown.bs.tab',     () => { window.refreshLogs?.(); });
});
