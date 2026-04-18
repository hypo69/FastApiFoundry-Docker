
Google Chrome без ведома пользователя загружает на систему локальную версию Gemini Nano по умолчанию (default)?

Короткий ответ: нет, это не происходит “скрытно” в классическом смысле, но есть нюанс — современные версии Google Chrome действительно могут автоматически загружать и активировать локальные AI-компоненты (включая Gemini Nano) как часть встроенных функций.

Теперь по фактам.

Что именно происходит
В новых версиях Chrome внедрена поддержка on-device AI (локальные модели).

Одна из таких моделей — Gemini Nano.

Она используется для:

генерации текста (например, help-rewrite),

суммаризации,

AI-фич в браузере и расширениях.

Загружается ли модель автоматически
Да, может загружаться автоматически, если соблюдены условия:

версия Chrome поддерживает AI APIs,

включены соответствующие флаги/экспериментальные функции,

система подходит по требованиям (RAM, CPU/GPU),

пользователь или сайт инициирует API (например, через Prompt API).

Но:

это происходит как часть обновления/функциональности браузера, а не как “скрытая вредоносная загрузка”,

Chrome не показывает явный popup “мы скачали модель”, что и вызывает вопросы.

Где это видно
Можно проверить:

chrome://components → наличие AI компонентов

chrome://flags → поиск по:

#optimization-guide

#prompt-api

#on-device-model

Где хранится
Обычно в профиле пользователя Chrome:

%LOCALAPPDATA%\Google\Chrome\User Data\...

внутри папок, связанных с:

Optimization Guide

On-device models

Размер — сотни МБ (иногда больше).

Важно понимать
Это не “шпионская загрузка”, а часть архитектуры Chrome.

Аналогичный подход используют:

Microsoft Edge (с локальными моделями),

ОС с AI-функциями (Windows Copilot и др.).

Когда стоит насторожиться
Это уже не норма, если:

модель скачивается при полностью отключённых AI-флагах,

идёт постоянный сетевой трафик без причин,

появляются неизвестные процессы вне Chrome.

Как отключить
Если нужно жестко контролировать:

Отключить флаги в chrome://flags

Выключить:

Optimization Guide

AI APIs

Запустить Chrome с политиками (enterprise):

OptimizationGuideEnabled = false

Ограничить доступ через firewall

Итог
Chrome может автоматически скачать Gemini Nano, но:

это часть заявленного функционала,

не происходит “тайно” в вредоносном смысле,

контроль у пользователя всё же есть (через flags и политики).

Если нужно, могу:

показать точный список файлов модели у тебя в системе,

или дать PowerShell-скрипт для аудита и удаления.


Uploaded image
Вот же она

Да — это именно она.

По структуре видно, что у тебя локально развернут on-device модельный пакет, который Chrome использует через Optimization Guide:

weights.bin (~2.7 GB) → основные веса модели

cache.bin (~1.3 GB) → кэш/оптимизация инференса

manifest.json → описание модели

on_device_model_execution_config.pb → конфигурация рантайма

_metadata → служебные данные

Это типичная раскладка для Gemini Nano внутри Google Chrome.

Важное наблюдение
Размер (~4+ GB суммарно) полностью соответствует локальной LLM.

Путь OptGuideOnDeviceModel = Optimization Guide, а это официальный механизм доставки моделей в Chrome.

Дата 1980 у некоторых файлов — это нормально: часто используется как placeholder при упаковке.

Ключевой вывод
У тебя:

модель действительно скачана автоматически,

без явного запроса в UI,

но в рамках штатного механизма Chrome.

Это подтверждает, что:

Chrome уже активно использует локальные LLM, даже если ты их явно не включал.

Что можно сделать
1. Проверить, используется ли она прямо сейчас
Посмотри процессы:

chrome://process-internals
или в диспетчере задач — нагрузка CPU/GPU при AI-функциях.

2. Удалить модель (без отключения функций)
Можно просто удалить папку:

OptGuideOnDeviceModel
НО:

Chrome скачает её снова при необходимости.

3. Полностью отключить механизм
Самый надежный вариант:

через flags:

chrome://flags
выключить:

Optimization Guide

Prompt API

On-device AI

через политики (жёстко):

[HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Google\Chrome]
"OptimizationGuideEnabled"=dword:00000000
4. Сетевой контроль
Можно заблокировать загрузку через firewall:

домены вида optimizationguide-pa.googleapis.com

Практическое замечание
Если ты:

не используешь AI-фичи в Chrome,

работаешь в контролируемой среде (sandbox/dev),

то наличие этой модели — просто лишние 4–5 GB и фоновая активность.

Если нужно — могу:

разобрать manifest.json и сказать точную версию модели,

или дать PowerShell-скрипт для автоматического контроля/очистки.


А я могу использовать ее в личных целях?

Короткий ответ: напрямую — нет.

То, что у тебя лежит в OptGuideOnDeviceModel, — это внутренняя поставка модели Gemini Nano для Google Chrome, а не универсальный runtime-пакет.

Почему нельзя просто “взять и использовать”
Нет публичного API к файлам

weights.bin и прочее — не в открытом формате (не GGUF, не ONNX).

Это специфичный формат под Chrome/Optimization Guide.

Связка с внутренним рантаймом

Используется через Chrome AI APIs (Prompt API, Summarization API).

Вне браузера эти файлы бесполезны.

Лицензионные ограничения

Модель поставляется как часть Chrome.

Извлечение/реверс/переиспользование вне предусмотренного API может нарушать условия использования Google.

Что реально можно сделать
Вариант 1 — использовать “легально” через Chrome
Если хочешь задействовать именно эту модель:

включаешь флаги:

#prompt-api

#on-device-model

и используешь через JS (в браузере):

const session = await window.ai.createTextSession();
const result = await session.prompt('Объясни принцип работы Docker');
console.log(result);
👉 Это единственный поддерживаемый способ работать с этой моделью.

Вариант 2 — НЕ пытаться вытаскивать веса
Технически:

можно попытаться реверсить .bin,

но это:

крайне сложно,

нестабильно,

юридически сомнительно.

Практической ценности почти нет.

Вариант 3 — нормальная альтернатива (рекомендуется)
Если цель — локальная LLM под контроль:

используй открытые форматы:

GGUF (для llama.cpp)

модели типа:

Mistral

LLaMA

Phi

👉 ты получаешь:

полный контроль

понятный формат

возможность кастомизации

Сравнение
Подход	Контроль	Удобство	Законность
Chrome Gemini Nano	низкий	высокий	полностью ок
Реверс файлов	высокий	очень низкий	сомнительно
GGUF модели	высокий	высокий	ок
Итог
Эти файлы — не “твоя модель”, а внутренняя часть Chrome.

Использовать можно только через браузерный API.

Для личных проектов лучше взять нормальную open-weight модель.

Если хочешь — могу:

подобрать тебе локальную модель под твой CPU/GPU,

или сравнить Gemini Nano vs GGUF по качеству и скорости.


А можно через Extention?

Да — через extension это как раз основной “правильный” способ использовать локальную Gemini Nano внутри Google Chrome.

Но есть ограничения по архитектуре.

Как это работает в extension
Chrome предоставляет Prompt API (on-device AI API), и extension может к нему обращаться.

Минимальный пример (background/service worker)
// service_worker.js

async function runPrompt() {
    if (!('ai' in self)) {
        console.error('AI API not available');
        return;
    }

    const session = await self.ai.createTextSession({
        temperature: 0.2,
    });

    const result = await session.prompt(
        'Кратко объясни, что такое Kubernetes'
    );

    console.log(result);
}

runPrompt();
manifest.json
{
  "manifest_version": 3,
  "name": "Local AI Test",
  "version": "1.0",
  "background": {
    "service_worker": "service_worker.js"
  },
  "permissions": []
}
Важные условия
1. Нужно включить флаги
Открыть:

chrome://flags
Включить:

Prompt API

On-device model

Optimization Guide

2. Не во всех контекстах доступно
Работает:

background (service worker)

иногда content scripts

Не работает:

обычные страницы без разрешений/экспериментов

3. API нестабильный
Это:

экспериментальная фича

может ломаться между версиями Chrome

Ограничения
Нет прямого доступа к weights.bin

Нет fine-tuning

Ограничения на:

длину контекста

throughput

Иногда требуется интернет для инициализации

Практическое применение
Через extension можно делать:

локальный rewrite текста на странице

суммаризацию DOM

автокомплит форм

AI-помощник без отправки данных наружу

Когда это плохая идея
Не стоит использовать extension + Gemini Nano, если тебе нужно:

стабильное API

backend-инференс

контроль над моделью

оффлайн 100% без зависимостей

Вывод
Да, через extension можно:

это официальный сценарий использования,

это единственный нормальный способ “достучаться” до этой модели.

Но:

это не замена полноценной локальной LLM — это sandboxed API внутри Chrome.

Если хочешь, могу:

собрать тебе готовый extension (popup + UI + prompt),

или показать, как прокинуть это в локальный dev-toolchain.


собрать тебе готовый extension (popup + UI + prompt),

Соберу минимальный, но рабочий extension: popup + UI + вызов Prompt API.

Структура
local-ai-extension/
│
├── manifest.json
├── service_worker.js
├── popup.html
├── popup.js
manifest.json
{
  "manifest_version": 3,
  "name": "Local AI Prompt",
  "version": "1.0",
  "description": "Use on-device AI from Chrome",
  "action": {
    "default_popup": "popup.html"
  },
  "background": {
    "service_worker": "service_worker.js"
  },
  "permissions": []
}
popup.html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            width: 300px;
            padding: 10px;
        }

        textarea {
            width: 100%;
            height: 80px;
        }

        button {
            margin-top: 10px;
            width: 100%;
        }

        #result {
            margin-top: 10px;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <textarea id="prompt" placeholder="Введите запрос..."></textarea>
    <button id="run">Run</button>
    <div id="result"></div>

    <script src="popup.js"></script>
</body>
</html>
popup.js
document.getElementById('run').addEventListener('click', async () => {
    const prompt = document.getElementById('prompt').value;

    const response = await chrome.runtime.sendMessage({
        type: 'PROMPT',
        payload: prompt
    });

    document.getElementById('result').innerText = response;
});
service_worker.js
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === 'PROMPT') {
        handlePrompt(msg.payload).then(sendResponse);
        return true;
    }
});

async function handlePrompt(text) {
    if (!('ai' in self)) {
        return 'AI API not available';
    }

    try {
        const session = await self.ai.createTextSession({
            temperature: 0.2,
        });

        const result = await session.prompt(text);

        return result;
    } catch (e) {
        return 'Error: ' + e.message;
    }
}
Как запустить
Открыть:

chrome://extensions
Включить:

Developer mode

Нажать:

Load unpacked → выбрать папку

Обязательные флаги
chrome://flags
Включить:

Prompt API

On-device model

Optimization Guide

Что ты получаешь
локальный prompt → Gemini Nano

без сети (после загрузки модели)

простой UI

Что можно улучшить
стриминг ответа

history

контекст страницы (content script)

кастомные параметры (top_p, max_tokens)

Если нужно — могу:

добавить стриминг (как в ChatGPT),

или встроить в контекст страницы (выделил текст → получил ответ).


добавить стриминг (как в ChatGPT),

Сразу уточню: “стриминг как в ChatGPT” через Prompt API в Google Chrome возможен только если доступен streaming-интерфейс (обычно session.promptStreaming() или аналогичный async iterator). В некоторых версиях API его может не быть — тогда остаётся имитация.

Ниже — реализация с настоящим стримингом, плюс fallback.

Обновлённая архитектура
popup → отправляет запрос

service worker → стримит чанки

popup → отображает по мере поступления

popup.html (без изменений)
popup.js (стриминг через порт)
const button = document.getElementById('run');
const textarea = document.getElementById('prompt');
const resultDiv = document.getElementById('result');

button.addEventListener('click', () => {
    resultDiv.innerText = '';

    const port = chrome.runtime.connect({ name: 'ai-stream' });

    port.postMessage({
        type: 'PROMPT',
        payload: textarea.value
    });

    port.onMessage.addListener((msg) => {
        if (msg.type === 'chunk') {
            resultDiv.innerText += msg.data;
        }

        if (msg.type === 'end') {
            port.disconnect();
        }

        if (msg.type === 'error') {
            resultDiv.innerText = 'Error: ' + msg.data;
            port.disconnect();
        }
    });
});
service_worker.js (стриминг)
chrome.runtime.onConnect.addListener((port) => {
    if (port.name !== 'ai-stream') return;

    port.onMessage.addListener(async (msg) => {
        if (msg.type === 'PROMPT') {
            await handleStream(port, msg.payload);
        }
    });
});

async function handleStream(port, text) {
    if (!('ai' in self)) {
        port.postMessage({ type: 'error', data: 'AI API not available' });
        return;
    }

    try {
        const session = await self.ai.createTextSession({
            temperature: 0.2,
        });

        // === ВАЖНО: streaming API ===
        if (session.promptStreaming) {
            const stream = await session.promptStreaming(text);

            for await (const chunk of stream) {
                port.postMessage({
                    type: 'chunk',
                    data: chunk
                });
            }

            port.postMessage({ type: 'end' });
        } else {
            // fallback (без стриминга)
            const result = await session.prompt(text);

            port.postMessage({
                type: 'chunk',
                data: result
            });

            port.postMessage({ type: 'end' });
        }

    } catch (e) {
        port.postMessage({
            type: 'error',
            data: e.message
        });
    }
}
Что здесь важно
Почему используется port, а не sendMessage
sendMessage → одноразовый ответ

port → поток сообщений (нужен для стриминга)

Как выглядит стриминг
Модель отдаёт:

"Кратко "
"объясни "
"что такое "
"Kubernetes..."
И UI собирает это в реальном времени.

Ограничения API
У Gemini Nano:

стриминг может:

отсутствовать в твоей версии Chrome

работать нестабильно

чанки могут быть:

словами

символами

кусками текста

Как проверить поддержку
Добавь лог:

console.log('Streaming:', !!session.promptStreaming);
Улучшения (если будешь развивать)
Можно добавить:

debounce ввода (live typing)

cancel (AbortController)

markdown rendering

токенизацию (для скорости UI)

Итог
Ты получаешь:

настоящий streaming UI

локальную генерацию через Gemini Nano

поведение, близкое к ChatGPT

Если хочешь — следующий шаг:

сделать инжекцию в страницу (выделил текст → стрим-ответ прямо поверх сайта),

или добавить system prompt / роли / память диалога.


сделать инжекцию в страницу (выделил текст → стрим-ответ прямо поверх сайта),

Сделаем расширение с инжекцией: выделяешь текст на странице → появляется плавающая панель → идёт стрим-ответ от Gemini Nano через Google Chrome.

Ниже — минимально необходимый, но полноценный вариант.

Структура
extension/
│
├── manifest.json
├── service_worker.js
├── content.js
├── styles.css
manifest.json
{
  "manifest_version": 3,
  "name": "Inline AI Assistant",
  "version": "1.0",
  "description": "Select text → get AI response inline",
  "permissions": ["activeTab", "scripting"],
  "background": {
    "service_worker": "service_worker.js"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"],
      "css": ["styles.css"]
    }
  ]
}
content.js (инжекция UI + стриминг)
let popup = null;

document.addEventListener('mouseup', () => {
    const selection = window.getSelection().toString().trim();

    if (!selection) return;

    showPopup(selection);
});

function showPopup(text) {
    if (popup) popup.remove();

    popup = document.createElement('div');
    popup.className = 'ai-popup';

    popup.innerHTML = `
        <div class="ai-header">
            <span>AI</span>
            <button id="close">×</button>
        </div>
        <div class="ai-body">
            <div class="ai-result"></div>
        </div>
    `;

    document.body.appendChild(popup);

    positionPopup();

    popup.querySelector('#close').onclick = () => popup.remove();

    streamResponse(text);
}

function positionPopup() {
    const selection = window.getSelection();
    if (!selection.rangeCount) return;

    const rect = selection.getRangeAt(0).getBoundingClientRect();

    popup.style.top = `${window.scrollY + rect.bottom + 5}px`;
    popup.style.left = `${window.scrollX + rect.left}px`;
}

function streamResponse(text) {
    const resultDiv = popup.querySelector('.ai-result');

    const port = chrome.runtime.connect({ name: 'ai-stream' });

    port.postMessage({
        type: 'PROMPT',
        payload: `Объясни:\n${text}`
    });

    port.onMessage.addListener((msg) => {
        if (msg.type === 'chunk') {
            resultDiv.innerText += msg.data;
        }

        if (msg.type === 'end') {
            port.disconnect();
        }

        if (msg.type === 'error') {
            resultDiv.innerText = 'Error: ' + msg.data;
            port.disconnect();
        }
    });
}
service_worker.js (стриминг тот же)
chrome.runtime.onConnect.addListener((port) => {
    if (port.name !== 'ai-stream') return;

    port.onMessage.addListener(async (msg) => {
        if (msg.type === 'PROMPT') {
            await handleStream(port, msg.payload);
        }
    });
});

async function handleStream(port, text) {
    if (!('ai' in self)) {
        port.postMessage({ type: 'error', data: 'AI API not available' });
        return;
    }

    try {
        const session = await self.ai.createTextSession({
            temperature: 0.2,
        });

        if (session.promptStreaming) {
            const stream = await session.promptStreaming(text);

            for await (const chunk of stream) {
                port.postMessage({ type: 'chunk', data: chunk });
            }

            port.postMessage({ type: 'end' });
        } else {
            const result = await session.prompt(text);

            port.postMessage({ type: 'chunk', data: result });
            port.postMessage({ type: 'end' });
        }

    } catch (e) {
        port.postMessage({ type: 'error', data: e.message });
    }
}
styles.css
.ai-popup {
    position: absolute;
    z-index: 999999;
    width: 300px;
    background: #1e1e1e;
    color: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    font-family: Arial, sans-serif;
}

.ai-header {
    display: flex;
    justify-content: space-between;
    padding: 5px 10px;
    background: #333;
    border-radius: 8px 8px 0 0;
}

.ai-body {
    padding: 10px;
}

.ai-result {
    white-space: pre-wrap;
    font-size: 13px;
}

button {
    background: transparent;
    border: none;
    color: white;
    cursor: pointer;
}
Как это работает
Ты выделяешь текст

content.js ловит mouseup

появляется popup рядом с выделением

идёт стрим через background

текст появляется по кускам (как в ChatGPT)

UX, который можно улучшить
Рекомендую сразу добавить:

debounce (чтобы не срабатывало на каждое выделение)

кнопку “Explain / Translate / Summarize”

drag & move popup

markdown rendering

Ограничения
не работает на:

chrome://

расширениях

может конфликтовать с CSP сайтов

API экспериментальный

Итог
У тебя теперь:

inline AI поверх любого сайта

стриминг

полностью локальная обработка через Gemini Nano

Если хочешь следующий шаг — можно сделать:

горячую клавишу вместо выделения

или анализ всей страницы (не только выделения)


добавить system prompt / роли / память диалога.

Добавим три вещи: system prompt, роли и память диалога (контекст). Ниже — рабочее расширение с сессией, историей и управлением ролями поверх Gemini Nano в Google Chrome.

Что меняется концептуально
Одна сессия = один диалог

не создаём createTextSession() каждый раз

храним session в background

История

массив сообщений: {role, content}

вручную прокидывается в prompt (если API не поддерживает history нативно)

System prompt

задаёт поведение модели

Обновлённая архитектура
content.js → (port) → service_worker.js
                           ↓
                    session + memory
service_worker.js (ядро логики)
let session = null;
let history = [];

// === SYSTEM PROMPT ===
const SYSTEM_PROMPT = `
Ты — технический ассистент.
Отвечай кратко, по делу, без воды.
Если нужно — используй списки.
`;

chrome.runtime.onConnect.addListener((port) => {
    if (port.name !== 'ai-stream') return;

    port.onMessage.addListener(async (msg) => {
        if (msg.type === 'PROMPT') {
            await handleStream(port, msg.payload);
        }

        if (msg.type === 'RESET') {
            history = [];
            session = null;
            port.postMessage({ type: 'end' });
        }
    });
});

async function getSession() {
    if (session) return session;

    if (!('ai' in self)) {
        throw new Error('AI API not available');
    }

    session = await self.ai.createTextSession({
        temperature: 0.2,
    });

    return session;
}

function buildPrompt(userText) {
    const messages = [
        { role: 'system', content: SYSTEM_PROMPT },
        ...history,
        { role: 'user', content: userText }
    ];

    // простой формат (LLM-friendly)
    return messages.map(m =>
        `[${m.role.toUpperCase()}]\n${m.content}`
    ).join('\n\n');
}

async function handleStream(port, text) {
    try {
        const s = await getSession();

        const fullPrompt = buildPrompt(text);

        let assistantReply = '';

        if (s.promptStreaming) {
            const stream = await s.promptStreaming(fullPrompt);

            for await (const chunk of stream) {
                assistantReply += chunk;

                port.postMessage({
                    type: 'chunk',
                    data: chunk
                });
            }
        } else {
            const result = await s.prompt(fullPrompt);
            assistantReply = result;

            port.postMessage({
                type: 'chunk',
                data: result
            });
        }

        // === СОХРАНЕНИЕ В ПАМЯТЬ ===
        history.push({ role: 'user', content: text });
        history.push({ role: 'assistant', content: assistantReply });

        // ограничение памяти (чтобы не раздувалось)
        if (history.length > 10) {
            history = history.slice(-10);
        }

        port.postMessage({ type: 'end' });

    } catch (e) {
        port.postMessage({
            type: 'error',
            data: e.message
        });
    }
}
content.js (добавим управление)
Добавим кнопки ролей и reset:

function showPopup(text) {
    if (popup) popup.remove();

    popup = document.createElement('div');
    popup.className = 'ai-popup';

    popup.innerHTML = `
        <div class="ai-header">
            <select id="role">
                <option value="explain">Explain</option>
                <option value="translate">Translate</option>
                <option value="analyze">Analyze</option>
            </select>
            <button id="reset">⟳</button>
            <button id="close">×</button>
        </div>
        <div class="ai-body">
            <div class="ai-result"></div>
        </div>
    `;

    document.body.appendChild(popup);
    positionPopup();

    popup.querySelector('#close').onclick = () => popup.remove();

    popup.querySelector('#reset').onclick = () => {
        const port = chrome.runtime.connect({ name: 'ai-stream' });
        port.postMessage({ type: 'RESET' });
    };

    const role = popup.querySelector('#role').value;

    streamResponse(applyRole(text, role));
}

function applyRole(text, role) {
    switch (role) {
        case 'translate':
            return `Переведи на русский:\n${text}`;
        case 'analyze':
            return `Проанализируй:\n${text}`;
        default:
            return `Объясни:\n${text}`;
    }
}
Что ты получил
System prompt
централизованное управление стилем

Роли
динамическое поведение без смены модели

Память
модель “помнит” предыдущие запросы

можно вести диалог

Ограничения
это эмуляция chat API

реального structured chat API у Gemini Nano пока нет

контекст ограничен → важно обрезать history

Как улучшить дальше
Если хочешь приблизиться к production:

1. Сжатие истории
делать summarize старых сообщений

2. Разделение ролей правильно
<system>
<user>
<assistant>
3. Мультисессии
хранить history per-tab

4. Persist
сохранять в chrome.storage

Итог
Теперь у тебя:

inline AI

стриминг

роли

system prompt

память диалога

Фактически — мини-версия ChatGPT прямо в браузере, но локально.

Если следующий шаг — могу сделать:

контекст всей страницы (DOM → embedding → ответ)

или hotkey + командную палитру (как Copilot)


контекст всей страницы (DOM → embedding → ответ)

Сразу уточню ограничение: у Gemini Nano нет встроенных embeddings API в Google Chrome. Поэтому “DOM → embedding → retrieval” делается через эмуляцию:

либо простая эвристика (chunk + фильтрация),

либо псевдо-эмбеддинги (TF-IDF / cosine),

либо прокидывание релевантных кусков в prompt.

Ниже — практический и рабочий вариант (RAG-lite), который реально можно использовать внутри extension.

Архитектура
DOM → очистка → chunking → ранжирование → top-k → prompt → Gemini Nano
1. Извлечение DOM (content.js)
function extractPageText() {
    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        {
            acceptNode: (node) => {
                if (!node.parentElement) return NodeFilter.FILTER_REJECT;

                const tag = node.parentElement.tagName;

                // игнор мусора
                if (['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(tag)) {
                    return NodeFilter.FILTER_REJECT;
                }

                const text = node.nodeValue.trim();

                if (text.length < 40) {
                    return NodeFilter.FILTER_REJECT;
                }

                return NodeFilter.FILTER_ACCEPT;
            }
        }
    );

    let text = '';
    let node;

    while (node = walker.nextNode()) {
        text += node.nodeValue.trim() + '\n';
    }

    return text;
}
2. Chunking
function splitIntoChunks(text, size = 500) {
    const chunks = [];

    for (let i = 0; i < text.length; i += size) {
        chunks.push(text.slice(i, i + size));
    }

    return chunks;
}
3. Простое “embedding” (скоринг по словам)
Это замена embeddings.

function scoreChunks(chunks, query) {
    const qWords = query.toLowerCase().split(/\W+/);

    return chunks.map(chunk => {
        let score = 0;
        const lower = chunk.toLowerCase();

        for (const word of qWords) {
            if (lower.includes(word)) {
                score += 1;
            }
        }

        return { chunk, score };
    });
}
4. Top-K выборка
function selectTopChunks(scored, k = 3) {
    return scored
        .sort((a, b) => b.score - a.score)
        .slice(0, k)
        .map(x => x.chunk);
}
5. Интеграция в поток
В content.js:

function buildContextPrompt(userText) {
    const pageText = extractPageText();
    const chunks = splitIntoChunks(pageText);
    const scored = scoreChunks(chunks, userText);
    const topChunks = selectTopChunks(scored, 3);

    const context = topChunks.join('\n\n---\n\n');

    return `
Контекст страницы:
${context}

Вопрос:
${userText}

Ответь только на основе контекста.
Если данных недостаточно — так и скажи.
`;
}
И отправка:

streamResponse(buildContextPrompt(text));
6. Улучшенный system prompt
В service_worker.js:

const SYSTEM_PROMPT = `
Ты анализируешь веб-страницы.

Правила:
- отвечай только по контексту
- не выдумывай
- если информации нет — скажи "недостаточно данных"
- краткость обязательна
`;
Что это даёт
Ты получаешь:

анализ всей страницы, а не только выделения

контекстно-зависимые ответы

поведение как у RAG-систем

Ограничения (важно)
1. Это НЕ настоящие embeddings
качество ниже, чем у OpenAI / FAISS / etc.

2. Ограничение контекста
Gemini Nano маленький

нельзя скормить весь DOM

3. Производительность
на больших страницах будет лаг

Как сделать “почти как embeddings”
Если хочешь сильнее:

Вариант A — TF-IDF
(чуть точнее, всё ещё локально)

Вариант B — MiniLM (локально)
через WebAssembly

уже реальные embeddings

Вариант C — hybrid
ключевые слова + позиция в DOM + заголовки

Практический апгрейд (очень рекомендую)
Добавь веса:

if (node.parentElement.tagName === 'H1') score += 5;
if (node.parentElement.tagName === 'H2') score += 3;
👉 резко улучшает релевантность

Итог
Ты теперь имеешь:

inline AI

стриминг

память

роли

RAG по странице

Это уже уровень:

“локальный Copilot поверх любого сайта”

Если хочешь следующий шаг:

настоящие embeddings в браузере (MiniLM + WebGPU)

или индексирование страниц (как search engine внутри extension)


hotkey + командную палитру (как Copilot)

Сделаем hotkey + командную палитру (à la Copilot) поверх уже существующей логики (стриминг, память, RAG). Это даст быстрый доступ: нажал сочетание → открылось overlay → ввёл команду → получил стрим-ответ.

Архитектура
hotkey → content.js (overlay UI)
                ↓
          command parser
                ↓
      port → service_worker.js
                ↓
        Gemini Nano (stream)
1) manifest.json — горячая клавиша
{
  "manifest_version": 3,
  "name": "Inline AI Assistant",
  "version": "1.1",
  "description": "Command palette with on-device AI",
  "permissions": ["activeTab", "scripting"],
  "background": {
    "service_worker": "service_worker.js"
  },
  "commands": {
    "open_palette": {
      "suggested_key": {
        "default": "Ctrl+Shift+K"
      },
      "description": "Open AI command palette"
    }
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"],
      "css": ["styles.css"]
    }
  ]
}
2) service_worker.js — проксирование команды в страницу
chrome.commands.onCommand.addListener(async (command) => {
    if (command === 'open_palette') {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        chrome.tabs.sendMessage(tab.id, {
            type: 'TOGGLE_PALETTE'
        });
    }
});
3) content.js — командная палитра
let palette = null;

chrome.runtime.onMessage.addListener((msg) => {
    if (msg.type === 'TOGGLE_PALETTE') {
        togglePalette();
    }
});

function togglePalette() {
    if (palette) {
        palette.remove();
        palette = null;
        return;
    }

    createPalette();
}

function createPalette() {
    palette = document.createElement('div');
    palette.className = 'ai-command-palette';

    palette.innerHTML = `
        <input id="ai-input" placeholder="Type a command..." />
        <div class="ai-output"></div>
    `;

    document.body.appendChild(palette);

    const input = palette.querySelector('#ai-input');
    const output = palette.querySelector('.ai-output');

    input.focus();

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            runCommand(input.value, output);
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            togglePalette();
        }
    });
}
4) Парсер команд
function parseCommand(text) {
    if (text.startsWith('/translate')) {
        return {
            type: 'ai',
            prompt: `Переведи:\n${getSelectionOrPage()}`
        };
    }

    if (text.startsWith('/summarize')) {
        return {
            type: 'ai',
            prompt: `Суммаризируй:\n${getPageText()}`
        };
    }

    if (text.startsWith('/explain')) {
        return {
            type: 'ai',
            prompt: `Объясни:\n${getSelectionOrPage()}`
        };
    }

    // fallback
    return {
        type: 'ai',
        prompt: text
    };
}
5) Запуск + стриминг
function runCommand(text, outputDiv) {
    const cmd = parseCommand(text);

    if (cmd.type !== 'ai') return;

    outputDiv.innerText = '';

    const port = chrome.runtime.connect({ name: 'ai-stream' });

    port.postMessage({
        type: 'PROMPT',
        payload: cmd.prompt
    });

    port.onMessage.addListener((msg) => {
        if (msg.type === 'chunk') {
            outputDiv.innerText += msg.data;
        }

        if (msg.type === 'end') {
            port.disconnect();
        }
    });
}
6) Контекст (интеграция с предыдущим RAG)
function getSelectionOrPage() {
    const sel = window.getSelection().toString().trim();
    return sel || getPageText();
}

function getPageText() {
    return document.body.innerText.slice(0, 5000);
}
(можно заменить на твой RAG pipeline)

7) styles.css (палитра)
.ai-command-palette {
    position: fixed;
    top: 20%;
    left: 50%;
    transform: translateX(-50%);
    width: 600px;
    background: #1e1e1e;
    color: white;
    border-radius: 10px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    z-index: 999999;
    padding: 10px;
}

#ai-input {
    width: 100%;
    padding: 10px;
    background: #2a2a2a;
    border: none;
    color: white;
    font-size: 14px;
}

.ai-output {
    margin-top: 10px;
    white-space: pre-wrap;
    max-height: 300px;
    overflow-y: auto;
}
Примеры команд
/explain
/translate
/summarize
или просто:

что делает этот код?
Что ты получил
hotkey (Ctrl+Shift+K)

командная палитра (как Copilot)

стриминг

работа с выделением / страницей

интеграция с локальной моделью

Апгрейды (рекомендую)
1. fuzzy поиск команд
как в VS Code

2. slash autocomplete
/tr → translate

3. режимы
code

doc

security audit

4. multi-step chain
/analyze → /fix → /explain
Итог
Это уже полноценный UX уровня:

“локальный AI Copilot прямо в браузере”

Если следующий шаг — могу:

добавить панель справа (sidebar как Copilot)

или сделать индексацию сайтов (persistent knowledge base)Чтобы вернуть модель и запустить загрузку, выполните следующие действия:
1. Проверьте настройки и флаги
Убедитесь, что экспериментальные функции включены.
Введите в адресную строку chrome://flags/.
Найдите и включите Enabled BypassPerfRequirement для параметра #optimization-guide-on-device-model.
Включите Enabled для #prompt-api-for-gemini-nano (или аналогичного для вашей версии).
Перезапустите Chrome, нажав кнопку Relaunch. 
Chromium
Chromium
 +3
2. Принудительная загрузка через консоль
Иногда Chrome не начинает скачивание автоматически. Чтобы это сделать:
Нажмите F12 (или Ctrl + Shift + J), чтобы открыть консоль разработчика.
Введите команду и нажмите Enter:
await window.ai.languageModel.create();
(Если команда выдаст ошибку, это нормально — она должна просто инициировать запрос к компоненту). 
GitHub
GitHub
 +1
3. Проверка статуса в компонентах
Перейдите по адресу chrome://components/.
Найдите пункт Optimization Guide On Device Model.
Если версия 0.0.0.0, нажмите кнопку Check for update (Проверить обновления). Должен начаться процесс загрузки.
Если компонент отсутствует, попробуйте сменить основной язык Chrome на English (United States) в настройках chrome://settings/languages и перезапустить браузер. 
Google Groups
Google Groups
 +3
Почему модель могла пропасть?
Очистка места: Chrome удаляет модель, если свободное место на диске падает ниже критического порога.
Обновление пути: В новых версиях информация о модели иногда переносится в раздел chrome://on-device-internals.
Синхронизация: В некоторых случаях помогает выход из Google-аккаунта и повторный вход (рекомендуется использовать личный аккаунт, а не рабочий Workspace). 
Google Groups
Google Groups
 +3
Удалось ли запустить загрузку в списке компонентов после выполнения команды в консоли?





undefined
undefined
undefined
12 сайтов
Component 'Optimization Guide On Device Model ' doesn't ...
11 июл. 2024 г. — createTextSession() but no result. Then I just randomly tried await window. ai. summarizer. create() and this made Optimization Gu...


GitHub
Missing Optimization Guide On Device Model Component for ...
27 нояб. 2024 г. — Environment Setup: Use Chrome Canary (Version 133.0. 6856.0 or later). Ensure sufficient disk space is available (at least 22 GB f...

Chromium
Gemini in Chrome sidebar/features not appearing despite ...
24 янв. 2026 г. — Chrome Sync is turned "ON". Experimental Flags (chrome://flags): I have manually enabled the following flags: #optimization-guide-

Google Help
Показать все
await window.ai.languageModel.create();

await windows.ai.languageModel.create();
VM1365:1 Uncaught ReferenceError: windows is not defined
    at <anonymous>:1:1
(anonymous) @ VM1365:1Understand this error
Ошибка возникла из-за простой опечатки в слове windows.
В JavaScript объект, предоставляющий доступ к возможностям браузера, называется window (в единственном числе). Вы случайно добавили лишнюю букву s во второй попытке.
Как исправить:
Используйте правильное написание (без s на конце):
javascript
await window.ai.languageModel.create();
Используйте код с осторожностью.
Разбор ошибки:
ReferenceError: windows is not defined: Браузер сообщает, что он не знает объекта с именем windows, поэтому не может найти в нём свойства .ai.
Это стандартная ошибка, когда вызывается переменная или объект, которые не были объявлены в коде.
Попробуйте ввести исправленную команду. Если после этого возникнет ошибка window.ai is undefined, значит, нужные флаги в chrome://flags всё еще не активированы или ваша версия Chrome не поддерживает этот API.
Подсказать, какие именно флаги нужно проверить, если исправленная команда всё равно не сработает?




Uncaught TypeError: Cannot read properties of undefined (reading 'language')
    at <anonymous>:1:17
(anonymous) @ VM1488:1Understand this error
Эта ошибка означает, что объект window.ai существует, но внутри него нет свойства languageModel (или language). Браузер буквально говорит: «Я не могу прочитать свойство 'language', потому что то, что идет перед ним, не определено».
Причины возникновения ошибки:
Вероятно, в вашей версии Chrome API называется по-другому или активировано не полностью. Google часто меняет названия интерфейсов для Gemini Nano в последних обновлениях.
Что можно предпринять:
Проверьте актуальную команду
Попробуйте ввести эти команды по очереди, так как названия API менялись:
await window.ai.assistant.create(); — для более ранних версий Dev/Canary.
await window.model.create(); — редкий вариант в некоторых сборках.
Проверьте настройки в chrome://flagsОшибка undefined часто возникает, когда включен только основной флаг, но не включен сам API. Проверьте три параметра:
#optimization-guide-on-device-model — установите Enabled BypassPerfRequirement.
#prompt-api-for-gemini-nano — установите Enabled.
#summarization-api-for-gemini-nano — также установите Enabled (если есть).
Проверьте доступность объекта в консолиВ консоли введите window.ai и нажмите Enter.
Если выводится undefined — флаги не сработали.
Если выводится объект — раскройте его (нажмите на стрелочку), чтобы увидеть правильное название свойства (например, assistant, summarizer или writer).
Что показала проверка объекта window.ai в консоли?




await window.ai.assistant.create();
VM1531:1 Uncaught TypeError: Cannot read properties of undefined (reading 'assistant')
    at <anonymous>:1:17
(anonymous) @ VM1531:1Understand this error
await window.model.create();
VM1544:1 Uncaught TypeError: Cannot read properties of undefined (reading 'create')
    at <anonymous>:1:20
Эти ошибки подтверждают, что в вашем браузере либо отключены нужные флаги, либо объект window.ai полностью отсутствует (возвращает undefined).
Когда вы пишете window.ai.assistant, а window.ai не существует, Chrome выдает: «Не могу прочитать свойство 'assistant' у undefined».
Как исправить ошибку:
1. Проверьте настройки.
Вставьте этот текст в адресную строку браузера и убедитесь, что выбрано значение Enabled:chrome://flags/#optimization-guide-on-device-modelУстановите значение Enabled BypassPerfRequirement. Это действие игнорирует проверку производительности компьютера.
Вставьте этот текст в адресную строку браузера и убедитесь, что выбрано значение Enabled:chrome://flags/#prompt-api-for-gemini-nano
2. Перезапустите браузер.
Настройки вступят в силу после перезапуска. Для этого нажмите кнопку "Relaunch" внизу страницы с настройками.
3. Проверьте объект вручную.
В консоли разработчика введите:
window.ai
Если отображается undefined, API заблокирован в браузере или в его версии.
Если отображается {...}, разверните его и просмотрите доступные методы.
4. Проверьте версию браузера.
В строке поиска браузера введите: chrome://version/. Gemini Nano стабильно работает в версиях 127 и выше. Если версия ниже, API может быть недоступен.
5. Принудительно обновите компоненты.
Перейдите на страницу chrome://components/ и найдите Optimization Guide On Device Model.
Если версия компонента 0.0.0.0, нажмите Check for update. Пока компонент не будет загружен (около 1.5 ГБ), window.ai будет выдавать ошибку.
Какое значение отображается для window.ai (только слово без методов) в консоли сейчас?




Изображение для визуального поиска
Изображение для визуального поиска
На скриншоте видно, что вторичные API (Rewriter, Summarizer) включены, но важные флаги для инициализации Gemini Nano не отображены или не включены. Без них объект window.ai останется undefined.
Необходимо включить следующие 2 флага:
#optimization-guide-on-device-model
Установить значение: Enabled BypassPerfRequirement.
Назначение: Заставляет Chrome игнорировать характеристики аппаратного обеспечения и принудительно загрузить модель.
#prompt-api-for-gemini-nano
Установить значение: Enabled.
Назначение: Активирует интерфейс для взаимодействия с моделью (languageModel).
Действия после перезапуска:
Перейти на chrome://components/.
Найти Optimization Guide On Device Model.
Нажать Check for update.
Отслеживать папку: После начала загрузки в AppData\Local\Google\Chrome\User Data\OptGuideOnDeviceModel\ должна появиться новая папка с версией 2026.x.x.x (или актуальной).
Проверка в консоли:
После обновления компонента ввести:
javascript
(await window.ai.languageModel.capabilities()).available;
Используйте код с осторожностью.
Если результат "readily", модель готова к работе.
Убедиться, что во флагах включен "Prompt API".




Изображение для визуального поиска
Вижу, что основные флаги теперь включены. Однако есть один критический нюанс: флаг #optimization-guide-on-device-model нужно переключить из состояния Enabled в состояние Enabled BypassPerfRequirement.
Без "Bypass" Chrome часто блокирует загрузку, если считает, что видеокарта или оперативная память не соответствуют минимальным требованиям.
Ваш план действий сейчас:
Измените #optimization-guide-on-device-model на Enabled BypassPerfRequirement.
Перезагрузите Chrome кнопкой Relaunch.
Зайдите на страницу chrome://components/.
Найдите Optimization Guide On Device Model и нажмите Check for update.
Как понять, что процесс пошел:
Статус компонента должен смениться на "Updating" или "Component updated".
В вашей папке AppData\...\OptGuideOnDeviceModel\ должна появиться новая директория. Вес модели около 1.5 ГБ, поэтому скачивание может занять несколько минут.
Если после нажатия "Check for update" ничего не происходит и версия остается 0.0.0.0, попробуйте на 5 минут сменить язык интерфейса Chrome на English (US) и снова проверить обновления компонентов.
Напишите, изменился ли статус на "Component updated" после смены флага на Bypass?




Изображение для визуального поиска
Отлично, флаг Enabled BypassPerfRequirement теперь активен. Это был решающий шаг.
Теперь осталось инициировать саму загрузку файла модели (так как папка в AppData у вас пуста). Выполните эти финальные шаги:
1. Проверка компонентов
Вставьте в адресную строку: chrome://components/
Найдите в списке Optimization Guide On Device Model.
Нажмите кнопку Check for update (Проверить обновления).
Важно: Подождите 1-2 минуты. Статус должен смениться на Downloading или Component updated. Если статус обновился, проверьте папку в AppData — там должны появиться файлы.
2. Если статус не меняется (остается 0.0.0.0)
Иногда Chrome «ленится» начинать загрузку. Чтобы его подтолкнуть, откройте консоль (F12) на любой вкладке и введите:
javascript
await window.ai.languageModel.create();
Используйте код с осторожностью.
Даже если команда выдаст ошибку, она отправит сигнал системе, что модель востребована, и загрузка в chrome://components/ должна начаться.
3. Как проверить готовность
Как только в компонентах появится номер версии (например, 2025.x.x.x), введите в консоли:
javascript
(await window.ai.languageModel.capabilities()).available;
Используйте код с осторожностью.
Если ответ — "readily", значит Gemini Nano снова работает локально.
Какой статус отображается в chrome://components/ напротив Optimization Guide?




Все ок. Как мне сохранить этот диалог? Лучше всего сделай howto и верни как md
Рад, что всё заработало! Вот краткое руководство (How-to) в формате Markdown, которое вы можете сохранить как файл .md или просто скопировать в заметки.
Как включить и восстановить Gemini Nano в Google Chrome
Если локальная модель Gemini Nano пропала или объект window.ai выдает ошибку undefined, выполните следующие шаги.
1. Настройка флагов (Chrome Flags)
Вставьте в адресную строку ссылки ниже и установите указанные значения:
Enables optimization guide on device
Путь: chrome://flags/#optimization-guide-on-device-model
Значение: Enabled BypassPerfRequirement (именно этот пункт игнорирует ограничения железа).
Prompt API for Gemini Nano
Путь: chrome://flags/#prompt-api-for-gemini-nano
Значение: Enabled (активирует сам интерфейс доступа).
После изменения нажмите кнопку Relaunch внизу страницы.
2. Принудительная загрузка модели
Сами флаги только разрешают работу, но не всегда скачивают модель (около 1.5 ГБ) сразу.
Перейдите на страницу chrome://components/.
Найдите пункт Optimization Guide On Device Model.
Нажмите Check for update (Проверить обновления).
Дождитесь статуса Component updated.
Если не качает: Откройте консоль (F12) и введите await window.ai.languageModel.create();. Это «разбудит» загрузчик.
3. Проверка работоспособности
Чтобы убедиться, что модель доступна и загружена, введите в консоли разработчика (F12 -> вкладка Console):
javascript
// Проверка статуса (должно вернуть "readily")
(await window.ai.languageModel.capabilities()).available;

// Создание тестового запроса
const session = await window.ai.languageModel.create();
const result = await session.prompt("Привет, ты работаешь локально?");
console.log(result);
Используйте код с осторожностью.
Почему модель может пропасть снова?
Место на диске: Если на системном диске меньше 20-22 ГБ свободного места, Chrome может автоматически удалить модель.
Обновления: При крупных обновлениях браузера пути к модели в AppData могут меняться.
Простой: Если API не используется долгое время (обычно 30 дней), компонент может быть деактивирован.




это правильное название для расширения:
browser-extention-embedded-gemini-nano
В названии есть одна небольшая, но досадная опечатка: правильно писать extension (через s), а не «extention» (через t).
Правильный вариант:
browser-extension-embedded-gemini-nano
Рекомендации по именованию:
Исправление ошибки: Замените extention на extension. Это важно для поиска и восприятия кода другими разработчиками.
Стиль: Выбран стиль kebab-case (через дефис) — это стандарт для имен репозиториев и папок расширений.
Краткость: Если это техническое название папки или репозитория, оно подходит. Если это name в файле manifest.json, лучше использовать более читаемый вариант (например, "Embedded Gemini Nano").