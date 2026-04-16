// =============================================================================
// app.js — Главный модуль веб-интерфейса FastAPI Foundry
//
// Отвечает за:
//  1. Импорт всех JS модулей
//  2. Экспорт функций в window (для onclick в HTML)
//  3. Инициализацию при загрузке DOM
//  4. Подписку на события переключения вкладок
// =============================================================================

import * as ui          from './js/ui.js';
import * as config      from './js/config.js';
import * as models      from './js/models.js';
import * as chat        from './js/chat.js';
import * as foundry     from './js/foundry.js';
import * as rag         from './js/rag.js';
import * as translation from './js/translation.js';
import * as editor      from './js/editor.js';
import * as llama       from './js/llama.js';
import * as hf          from './js/hf.js';
import * as agent       from './js/agent.js';
import * as mcp         from './js/mcp.js';
import * as sdk         from './js/sdk.js';

// ── Глобальные константы ──────────────────────────────────────────────────────

// Базовый URL API — используется во всех модулях через window.API_BASE
window.API_BASE = window.location.origin + '/api/v1';

// Глобальное состояние приложения
window.CONFIG = {
    foundry_url:        'http://localhost:50477/v1/',
    api_url:            window.API_BASE,
    default_model:      null,
    auto_load_default:  false,
    environment:        'development',
};

// ── Экспорт в window ──────────────────────────────────────────────────────────

// Все функции модулей регистрируются в window чтобы onclick-атрибуты в HTML работали.
// Порядок важен: более поздние модули перезаписывают одноимённые функции ранних.
Object.assign(window,
    ui, config, models, chat, foundry, rag,
    translation, editor, llama, hf, agent, mcp, sdk
);

// ── Инициализация ─────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Загружаем конфигурацию с сервера (восстанавливает настройки чата, модель и т.д.)
    await config.loadConfig();

    // 2. Первичная проверка статуса системы (Foundry, модели)
    foundry.checkSystemStatus();

    // 3. Периодическая проверка статуса каждые 30 секунд
    setInterval(foundry.checkSystemStatus, 30_000);

    // 4. Обработка Enter в поле ввода чата
    document.getElementById('chat-input')?.addEventListener('keypress', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            window.sendMessage?.();
        }
    });

    // ── Ленивая загрузка вкладок ──────────────────────────────────────────────
    // Данные загружаются только при первом открытии вкладки, а не при старте.

    // Вкладка Editor — загружаем .env и config.json
    document.getElementById('editor-tab')?.addEventListener('shown.bs.tab', () => {
        window.loadEnv?.();
        window.loadConfigJson?.();
    });

    // Вкладка llama.cpp — статус сервера + список моделей из ~/.models
    document.getElementById('llama-tab')?.addEventListener('shown.bs.tab', () => {
        window.llamaCheckStatus?.();
        window.llamaScanModels?.();
    });

    // Вкладка HuggingFace — статус, список скачанных и Hub моделей
    document.getElementById('hf-tab')?.addEventListener('shown.bs.tab', () => {
        window.hfCheckStatus?.();
        window.hfRefreshModels?.();
        window.hfLoadHubModels?.();
    });

    // Вкладка Agent — список агентов и инструментов
    document.getElementById('agent-tab')?.addEventListener('shown.bs.tab', () => {
        window.agentLoadTools?.();
    });

    // Вкладка MCP — список серверов
    document.getElementById('mcp-tab')?.addEventListener('shown.bs.tab', () => {
        window.mcpLoadServers?.();
    });

    // Вкладка Settings — заполняем поля формы из config.json
    document.getElementById('settings-tab')?.addEventListener('shown.bs.tab', () => {
        window.loadConfigFields?.();
    });

    // Вкладка Logs — загружаем последние логи
    document.getElementById('logs-tab')?.addEventListener('shown.bs.tab', () => {
        window.refreshLogs?.();
    });
});
