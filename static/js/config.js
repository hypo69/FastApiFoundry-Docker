/**
 * Название процесса: Работа с конфигурацией
 * Описание: Загрузка, сохранение и обмен настройками через API.
 * Version: 0.4.1
 * Date: 17 апреля 2026
 */

import { showAlert } from './ui.js';

// Загрузка основной конфигурации системы
export async function loadConfig() {
    try {
        // Запрос текущих настроек с сервера
        const response = await fetch(`${window.API_BASE}/config`);
        const data = await response.json();

        if (data.success) {
            window.CONFIG.foundry_url = data.foundry_ai?.base_url || window.CONFIG.foundry_url;
            window.CONFIG.default_model = data.foundry_ai?.default_model;
            window.CONFIG.auto_load_default = data.foundry_ai?.auto_load_default || false;

            // Восстановление настроек чата из config.json
            if (window.applyChatConfig) window.applyChatConfig(data.foundry_ai);

            // Поиск порта llama.cpp в конфигурации
            const llamaPort = data.config?.llama_cpp?.port || 9780;
            if (llamaPort) {
                const el = document.getElementById('llama-port');
                if (el) el.value = llamaPort;
            }

            console.log('Конфигурация успешно загружена');
            if (window.validateDefaultModel) await window.validateDefaultModel();
        }
    } catch (error) {
        // Логирование сбоя сетевого запроса
        console.error('Ошибка загрузки конфигурации:', error);
    }
}

// Заполнение полей формы настроек текущими значениями
export async function loadConfigFields() {
    try {
        const response = await fetch(`${window.API_BASE}/config`);
        const data = await response.json();

        if (data.success && data.config) {
            const { fastapi_server, foundry_ai, docs_server, llama_cpp } = data.config;
            
            // Ports
            if (document.getElementById('config-api-port'))   document.getElementById('config-api-port').value   = fastapi_server?.port || 9696;
            if (document.getElementById('config-llama-port')) document.getElementById('config-llama-port').value = llama_cpp?.port      || 9780;
            if (document.getElementById('config-docs-port'))  document.getElementById('config-docs-port').value  = docs_server?.port    || 9697;

            // Заполнение параметров сервера FastAPI
            if (document.getElementById('config-api-host')) document.getElementById('config-api-host').value = fastapi_server?.host || '0.0.0.0';
            
            // Заполнение параметров Foundry AI
            if (document.getElementById('config-foundry-url')) document.getElementById('config-foundry-url').value = foundry_ai?.base_url || '';
            if (document.getElementById('config-foundry-model')) document.getElementById('config-foundry-model').value = foundry_ai?.default_model || '';

            // Docs Server
            if (document.getElementById('config-docs-enabled')) document.getElementById('config-docs-enabled').checked = docs_server?.enabled || false;
            
            showAlert('Поля настроек заполнены', 'success');
        }
    } catch (error) {
        // Уведомление пользователя о неудаче
        showAlert('Failed to load config fields', 'danger');
    }
}

// Сохранение данных из полей формы в конфигурацию
export async function saveConfigFields() {
    try {
        const configStatusEl = document.getElementById('config-status');
        if (configStatusEl) {
            configStatusEl.style.display = 'none';
        }

        const configData = {
            fastapi_server: {
                host: document.getElementById('config-api-host').value,
                port: parseInt(document.getElementById('config-api-port')?.value || '9696'),
                auto_find_free_port: document.getElementById('config-api-auto-port').checked,
                mode: document.getElementById('config-api-mode').value,
                workers: parseInt(document.getElementById('config-api-workers').value)
            },
            foundry_ai: {
                base_url: document.getElementById('config-foundry-url').value,
                default_model: document.getElementById('config-foundry-model').value,
                temperature: parseFloat(document.getElementById('config-foundry-temp').value),
                max_tokens: parseInt(document.getElementById('config-foundry-tokens').value),
                auto_load_default: document.getElementById('config-foundry-autoload').checked
            },
            rag_system: {
                enabled: document.getElementById('config-rag-enabled').checked,
                index_dir: document.getElementById('config-rag-index').value,
                chunk_size: parseInt(document.getElementById('config-rag-chunk').value)
            },
            security: {
                api_key: document.getElementById('config-security-key').value,
                https_enabled: document.getElementById('config-security-https').checked
            },
            logging: {
                level: document.getElementById('config-log-level').value,
                file: document.getElementById('config-log-file').value
            },
            development: {
                debug: document.getElementById('config-dev-debug').checked,
                verbose: document.getElementById('config-dev-verbose').checked
            },
            docs_server: {
                enabled: document.getElementById('config-docs-enabled')?.checked || false,
                port: parseInt(document.getElementById('config-docs-port')?.value || '9697')
            },
            llama_cpp: {
                port: parseInt(document.getElementById('config-llama-port')?.value || '9780'),
                host: '127.0.0.1'
            }
        };

        // Сбор данных HuggingFace (если модуль hf.js загружен)
        if (typeof window.collectHFConfigFields === 'function') {
            configData.huggingface = window.collectHFConfigFields();
        }

        const response = await fetch(`${window.API_BASE}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ config: configData })
        });

        const data = await response.json();
        if (data.success) {
            showAlert('Конфигурация сохранена', 'success');
            await loadConfig(); // Reload global config
            if (window.loadConfigFields) await window.loadConfigFields();
        }
    } catch (error) {
        showAlert(`Save error: ${error.message}`, 'danger');
    }
}

// Экспорт текущей конфигурации в JSON файл
export async function exportConfig() {
    try {
        const response = await fetch(`${window.API_BASE}/config/export`);
        const data = await response.json();
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.setAttribute('href', url);
        a.setAttribute('download', `foundry-config-${new Date().getTime()}.json`);
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showAlert('Конфигурация экспортирована', 'success');
    } catch (error) {
        showAlert('Export failed', 'danger');
    }
}

// Импорт конфигурации
export async function importConfig(event) {
    const file = event.target.files[0];
    if (!file) return;
    event.target.value = '';
    try {
        const text = await file.text();
        const parsed = JSON.parse(text);
        const merge = confirm("Merge with current configuration?");
        const response = await fetch(`${window.API_BASE}/config/import`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ config: parsed, merge })
        });
        const result = await response.json();
        if (result.success) {
            showAlert('Configuration imported successfully', 'success');
            await loadConfigFields();
        } else {
            showAlert(`Import error: ${result.error}`, 'danger');
        }
    } catch (error) {
        showAlert('Invalid config file', 'danger');
    }
}

// Перехватываем loadConfigFields и saveConfigFields из app.js
// Это необходимо, чтобы функции из editor.js могли быть вызваны из Settings
document.addEventListener('DOMContentLoaded', () => {
    const origLoad = window.loadConfigFields;
    if (origLoad) {
        window.loadConfigFields = async function() {
            await origLoad(); // Вызываем оригинальную функцию из config.js
        };
    }
    const origSave = window.saveConfigFields;
    if (origSave) {
        window.saveConfigFields = async function() {
            await origSave(); // Вызываем оригинальную функцию из config.js
        };
    }
});