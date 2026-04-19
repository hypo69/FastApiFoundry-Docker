/**
 * Модуль редактора конфигурации и переменных окружения
 * Version: 0.4.1
 */
import { showAlert } from './ui.js';

export async function loadEnv() {
    const ta = document.getElementById('env-editor');
    const st = document.getElementById('env-status');
    if (!ta) return;
    try {
        const response = await fetch('/api/v1/config/env-raw');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const d = await response.json();
        ta.value = d.content || '';
        if (st) st.style.display = 'none';
    } catch(e) {
        console.error('❌ Failed to load .env:', e);
        if (st) {
            st.className = 'alert alert-danger py-1 px-2 mb-2';
            st.textContent = '❌ ' + e.message;
            st.style.display = '';
        }
    }
}

export async function saveEnv() {
    const st = document.getElementById('env-status');
    const content = document.getElementById('env-editor')?.value;
    try {
        const response = await fetch('/api/v1/config/env-raw', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ content })
        });
        const d = await response.json();
        if (st) {
            st.className = d.success ? 'alert alert-success py-1 px-2 mb-2' : 'alert alert-danger py-1 px-2 mb-2';
            st.textContent = d.success ? '✅ .env сохранён' : '❌ ' + (d.detail || d.error);
            st.style.display = '';
        }
    } catch(e) {
        console.error('❌ Save .env error:', e);
        if (st) {
            st.className = 'alert alert-danger py-1 px-2 mb-2';
            st.textContent = '❌ ' + e.message;
            st.style.display = '';
        }
    }
}

export async function loadConfigJson() {
    const ta = document.getElementById('config-json-editor');
    const st = document.getElementById('config-json-status');
    if (!ta) return;
    try {
        const response = await fetch('/api/v1/config/raw');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const d = await response.json();
        ta.value = d.content || '';
        if (st) st.style.display = 'none';
    } catch(e) {
        console.error('❌ Failed to load config.json:', e);
        if (st) {
            st.className = 'alert alert-danger py-1 px-2 mb-2';
            st.textContent = '❌ ' + e.message;
            st.style.display = '';
        }
    }
}

export async function saveConfigJson() {
    const st = document.getElementById('config-json-status');
    const content = document.getElementById('config-json-editor')?.value;
    if (!content) {
        if (st) {
            st.className = 'alert alert-warning py-1 px-2 mb-2';
            st.textContent = '⚠️ Content is empty, not saving.';
            st.style.display = '';
        }
        return;
    }
    try {
        // Валидация JSON перед сохранением
        JSON.parse(content);

        const response = await fetch('/api/v1/config/raw', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ content })
        });
        const d = await response.json();
        if (st) {
            st.className = d.success ? 'alert alert-success py-1 px-2 mb-2' : 'alert alert-danger py-1 px-2 mb-2';
            st.textContent = d.success ? '✅ config.json сохранён' : '❌ ' + (d.detail || d.error || JSON.stringify(d));
            st.style.display = '';
        }
        if (d.success && window.loadConfig) await window.loadConfig();
    } catch(e) {
        console.error('❌ Save config.json error:', e);
        if (st) {
            st.className = 'alert alert-danger py-1 px-2 mb-2';
            st.textContent = '❌ ' + (e instanceof SyntaxError ? 'Невалидный JSON: ' + e.message : e.message);
            st.style.display = '';
        }
    }
}

// Перехватываем loadConfigFields и saveConfigFields из app.js
// Это необходимо, чтобы функции из editor.js могли быть вызваны из Settings
document.addEventListener('DOMContentLoaded', () => {
    const origLoad = window.loadConfigFields;
    if (origLoad) {
        window.loadConfigFields = async function() {
            await origLoad(); // Вызываем оригинальную функцию из config.js
            // Здесь можно добавить логику загрузки полей, специфичных для редактора, если нужно
        };
    }
    const origSave = window.saveConfigFields;
    if (origSave) {
        window.saveConfigFields = async function() {
            // Здесь можно добавить логику сохранения полей, специфичных для редактора, если нужно
            await origSave(); // Вызываем оригинальную функцию из config.js
        };
    }
});