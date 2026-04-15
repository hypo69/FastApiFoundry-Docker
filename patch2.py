import re

# ── patch index.html ──────────────────────────────────────────────────────────
with open('static/index.html', 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

old_indicator = '<small id="default-model-indicator" class="text-muted me-2"></small>'
new_indicator = (
    '<span id="chat-timer" class="badge bg-secondary me-1" style="display:none">'
    '<i class="bi bi-stopwatch"></i> <span id="chat-timer-value">0.0s</span>'
    '</span>'
    '<span id="chat-model-badge" class="badge bg-primary me-1" style="display:none"></span>'
)

if old_indicator in html:
    html = html.replace(old_indicator, new_indicator)
    with open('static/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('index.html patched OK')
else:
    print('index.html: indicator not found')

# ── patch app.js ──────────────────────────────────────────────────────────────
with open('static/app.js', 'r', encoding='utf-8', errors='replace') as f:
    js = f.read()

# 1. Убрать вызов updateModelStatus из validateDefaultModel и loadDefaultModel
js = re.sub(r"\s*updateModelStatus\([^)]*\);", "", js)

# 2. Добавить обновление бейджа модели при смене select
old_change = (
    "    const chatModelSelect = document.getElementById('chat-model');\n"
    "    if (chatModelSelect) {\n"
    "        chatModelSelect.addEventListener('change', function() {\n"
    "            const selectedModel = this.value;\n"
    "            if (selectedModel && selectedModel !== CONFIG.default_model) {\n"
    "                saveDefaultModel(selectedModel);\n"
    "            }\n"
    "        });\n"
    "    }"
)
new_change = (
    "    const chatModelSelect = document.getElementById('chat-model');\n"
    "    if (chatModelSelect) {\n"
    "        chatModelSelect.addEventListener('change', function() {\n"
    "            const selectedModel = this.value;\n"
    "            updateChatModelBadge(selectedModel);\n"
    "            if (selectedModel && selectedModel !== CONFIG.default_model) {\n"
    "                saveDefaultModel(selectedModel);\n"
    "            }\n"
    "        });\n"
    "    }"
)
if old_change in js:
    js = js.replace(old_change, new_change)
    print('app.js: change listener patched OK')
else:
    print('app.js: change listener not found')

# 3. Добавить таймер в sendMessage — вокруг блока с ctrl
old_send_start = "    addMessageToChat('user', message);\n    input.value = '';\n\n    const typingId = addMessageToChat('assistant', '<i class=\"bi bi-three-dots\"></i> Typing...');"
new_send_start = (
    "    addMessageToChat('user', message);\n"
    "    input.value = '';\n\n"
    "    const typingId = addMessageToChat('assistant', '<i class=\"bi bi-three-dots\"></i> Typing...');\n"
    "    const _chatStart = Date.now();\n"
    "    const _timerEl = document.getElementById('chat-timer');\n"
    "    const _timerVal = document.getElementById('chat-timer-value');\n"
    "    if (_timerEl) { _timerEl.style.display = ''; }\n"
    "    const _timerInterval = setInterval(() => {\n"
    "        if (_timerVal) _timerVal.textContent = ((Date.now() - _chatStart) / 1000).toFixed(1) + 's';\n"
    "    }, 100);"
)
if old_send_start in js:
    js = js.replace(old_send_start, new_send_start)
    print('app.js: timer start patched OK')
else:
    print('app.js: timer start not found')

# 4. Остановить таймер после получения ответа — после clearTimeout(timer)
old_finally = "        } finally {\n            clearTimeout(timer);\n        }"
new_finally = (
    "        } finally {\n"
    "            clearTimeout(timer);\n"
    "            clearInterval(_timerInterval);\n"
    "            if (_timerEl) _timerEl.style.display = 'none';\n"
    "        }"
)
if old_finally in js:
    js = js.replace(old_finally, new_finally)
    print('app.js: timer stop patched OK')
else:
    print('app.js: timer stop not found')

# 5. Добавить функцию updateChatModelBadge перед updateModelSelect
badge_fn = (
    "\n// Обновление бейджа выбранной модели\n"
    "function updateChatModelBadge(modelId) {\n"
    "    const badge = document.getElementById('chat-model-badge');\n"
    "    if (!badge) return;\n"
    "    if (modelId) {\n"
    "        const label = modelId.startsWith('hf::') ? modelId.slice(4) : modelId;\n"
    "        badge.textContent = label;\n"
    "        badge.style.display = '';\n"
    "    } else {\n"
    "        badge.style.display = 'none';\n"
    "    }\n"
    "}\n\n"
)
target = "// Обновление списка моделей\nfunction updateModelSelect"
if target in js:
    js = js.replace(target, badge_fn + "// Обновление списка моделей\nfunction updateModelSelect")
    print('app.js: badge function added OK')
else:
    print('app.js: updateModelSelect anchor not found')

# 6. Вызывать updateChatModelBadge при автовыборе модели в updateModelSelect
old_auto = (
    "        if (CONFIG.default_model) {\n"
    "        const availableModels = models.map(m => m.id);\n"
    "        if (availableModels.includes(CONFIG.default_model)) {\n"
    "            select.value = CONFIG.default_model;\n"
    "        }\n"
    "    }"
)
new_auto = (
    "        if (CONFIG.default_model) {\n"
    "        const availableModels = models.map(m => m.id);\n"
    "        if (availableModels.includes(CONFIG.default_model)) {\n"
    "            select.value = CONFIG.default_model;\n"
    "            updateChatModelBadge(CONFIG.default_model);\n"
    "        }\n"
    "    }"
)
if old_auto in js:
    js = js.replace(old_auto, new_auto)
    print('app.js: auto-select badge patched OK')
else:
    print('app.js: auto-select anchor not found')

with open('static/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print('app.js written OK')
