# API Справочник FastAPI Foundry

Все эндпоинты доступны по базовому префиксу `/api/v1/`. Интерактивная документация: `/docs`.

**Базовый URL:** `http://localhost:9696/api/v1`  
**Формат ответа:** JSON  
**Формат ошибки:** `{"success": false, "error": "описание"}`

---

## Health

### `GET /health`
Проверка состояния сервиса.

```bash
curl http://localhost:9696/api/v1/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "foundry_status": "healthy",
  "foundry_details": {"port": 50477, "url": "http://localhost:50477/v1", "error": null},
  "models_count": 3,
  "timestamp": "..."
}
```

---

## Generate

### `POST /generate`
Генерация текста через Foundry, HuggingFace или llama.cpp.

Маршрутизация по префиксу `model`:
- `hf::<model_id>` → HuggingFace
- `llama::<path>` → llama.cpp
- без префикса → Foundry Local

```bash
curl -X POST http://localhost:9696/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Ваш запрос", "model": "qwen2.5-0.5b-instruct-generic-cpu:4", "temperature": 0.7}'
```

**Тело запроса:**
```json
{
  "prompt": "Ваш запрос",
  "model": "qwen2.5-0.5b-instruct-generic-cpu:4",
  "temperature": 0.7,
  "max_tokens": 1000,
  "use_rag": false,
  "top_k": 5
}
```

**Ответ:**
```json
{
  "success": true,
  "content": "Ответ модели",
  "model": "qwen2.5-0.5b-instruct-generic-cpu:4",
  "usage": {"prompt_tokens": 10, "completion_tokens": 50, "total_tokens": 60}
}
```

---

## Chat

### Workflow диалога: пользователь → перевод → RAG → модель → перевод → пользователь

```
[1] Пользователь отправляет сообщение (на любом языке)
        │  POST /api/v1/chat/message
        │  { message, session_id, source_lang, locale, use_rag, model }
        ▼
[2] Перевод входящего сообщения → English
        │  translator.translate_for_model(message, source_lang)
        │  Включается если: translator.enabled=true И source_lang != "en"
        ▼
[3] RAG поиск (если use_rag=true)
        │  rag_system.search(message_en, top_k=3)
        │  Релевантные фрагменты добавляются в начало промпта
        ▼
[4] Сборка промпта
        │  "Context:\n{rag}\n\nSystem: {system_prompt}\n\n{history}\nUser: {message}"
        ▼
[5] Генерация ответа
        │  foundry_client.generate_text(prompt, model, temperature, max_tokens)
        │  Модель отвечает на English
        ▼
[6] Обратный перевод ответа
        │  translator.translate_response(response_en, locale или source_lang)
        │  Включается если: translator.enabled=true И reply_lang != "en"
        ▼
[7] Ответ пользователю (на его языке)
        { success, response, session_id }
```

!!! info "Приоритет `locale` над `source_lang`"
    Если передан `locale="ru"`, ответ всегда будет на русском — даже если входящее сообщение было на английском.
    Без `locale` ответ переводится на язык `source_lang` (определённый автоматически).

---

### `POST /chat/start`
Начать новую сессию чата.

**Тело:** `{"model": "qwen2.5-0.5b-instruct-generic-cpu:4"}`  
**Ответ:** `{"success": true, "session_id": "uuid", "model": "...", "message": "..."}`

### `POST /chat/message`
Отправить сообщение в сессию.

```bash
curl -X POST http://localhost:9696/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"session_id": "uuid", "message": "Привет", "locale": "ru"}'
```

**Тело:**
```json
{
  "session_id": "uuid",
  "message": "Текст сообщения",
  "model": "...",
  "temperature": 0.7,
  "max_tokens": 2048,
  "source_lang": "auto",
  "locale": "ru"
}
```

| Поле | По умолчанию | Описание |
|---|---|---|
| `session_id` | — | UUID сессии (обязательно) |
| `message` | — | Текст сообщения (обязательно) |
| `model` | из config.json | ID модели |
| `temperature` | `0.7` | Температура |
| `max_tokens` | `2048` | Максимум токенов |
| `source_lang` | `"auto"` | Язык входящего сообщения (`"ru"`, `"he"`, `"auto"`) |
| `locale` | `""` | Язык ответа. Переопределяет `source_lang` для обратного перевода |

### `POST /chat/stream`
Стриминговый ответ (SSE). Те же поля что и `/chat/message`.  
**Ответ:** `text/event-stream` — чанки `{"chunk": "..."}`, финал `{"done": true}`.

### `GET /chat/history/{session_id}`
История сессии.  
**Ответ:** `{"success": true, "session_id": "...", "history": [{"role": "user", "content": "..."}]}`

### `DELETE /chat/session/{session_id}`
Удалить сессию.

### `POST /chat/history/save`
Сохранить историю на диск (`~/.ai-assistant-chat-history/`).

**Тело:**
```json
{
  "messages": [{"role": "user", "content": "..."}],
  "session_id": "uuid",
  "model": "...",
  "title": "...",
  "aborted": false
}
```

### `GET /chat/models`
Список моделей доступных для чата (из Foundry).

---

## Models

### `GET /models`
Все доступные модели (Foundry + llama.cpp).

**Ответ:** `{"success": true, "models": [...], "count": 5}`

### `GET /models/connected`
Подключённые модели с деталями (`provider`, `status`, `max_tokens`).

### `GET /models/providers`
Список провайдеров (`foundry`, `ollama`, `openai`) и их статус.

### `POST /models/health-check`
Проверка здоровья всех моделей.

### `POST /batch-generate`
Пакетная генерация текста.

**Тело:** `{"prompts": ["запрос 1", "запрос 2"]}`  
**Ответ:** `{"success": true, "results": [{"success": true, "content": "..."}]}`

---

## Foundry

### `GET /foundry/status`
Статус сервиса Foundry Local.

**Ответ:** `{"success": true, "running": true, "status": "healthy", "port": 50477, "url": "..."}`

### `GET /foundry/models/list`
Список всех моделей через Foundry клиент.

### `GET /foundry/start`
Запустить сервис Foundry через CLI.

### `GET /foundry/stop`
Остановить сервис Foundry через CLI.

---

## Foundry Models

### `GET /foundry/models` / `GET /foundry/models/available`
Список моделей из каталога Foundry (`foundry model ls`). При недоступности CLI — хардкод.

**Ответ:** `{"success": true, "models": [...], "count": 4, "source": "foundry-cli"}`

Поля модели: `id`, `name`, `alias`, `device`, `type`, `task`, `size`, `license`, `cached`.

### `GET /foundry/models/cached`
Модели скачанные в локальный кэш (`~/.foundry/cache/models/Microsoft`).

### `GET /foundry/models/loaded`
Модели загруженные в Foundry сервис (запрос к `/v1/models`).

### `GET /foundry/models/status/{model_id}`
Статус конкретной модели: `loaded`, `cached`, `not_downloaded`.

### `POST /foundry/models/download`
Скачать модель в кэш (фоновый процесс).

**Тело:** `{"model_id": "qwen2.5-0.5b-instruct-generic-cpu:4"}`  
**Ответ:** `{"success": true, "model_id": "...", "status": "downloading", "pid": 1234}`

### `GET /foundry/models/download/status/{pid}`
Статус процесса скачивания по PID.

**Ответ:** `{"success": true, "pid": 1234, "model_id": "...", "status": "done", "cached": true}`

### `POST /foundry/models/load`
Загрузить модель в Foundry сервис.

**Тело:** `{"model_id": "qwen2.5-0.5b-instruct-generic-cpu:4"}`  
**Ответ:** `{"success": true, "model_id": "...", "status": "loading", "pid": 1234}`

### `POST /foundry/models/unload`
Выгрузить модель из Foundry сервиса.

**Тело:** `{"model_id": "qwen2.5-0.5b-instruct-generic-cpu:4"}`

### `POST /foundry/models/auto-load-default`
Загрузить модель по умолчанию из `config.json` (`foundry_ai.default_model`).

---

## HuggingFace

### `GET /hf/status`
Статус HuggingFace интеграции: версии `transformers`, `torch`, `huggingface_hub`, наличие `HF_TOKEN`.

### `GET /hf/models`
Список скачанных и загруженных в память HF моделей.

### `GET /hf/hub/models`
Модели пользователя с HuggingFace Hub + список популярных публичных моделей.  
Требует `HF_TOKEN` в `.env`.

### `POST /hf/models/download`
Скачать модель с HuggingFace Hub.

**Тело:** `{"model_id": "google/gemma-2-2b-it", "token": "hf_..."}`

### `POST /hf/models/load`
Загрузить скачанную модель в память.

**Тело:** `{"model_id": "google/gemma-2-2b-it", "device": "auto"}`

### `POST /hf/models/unload`
Выгрузить модель из памяти (освободить RAM/VRAM).

**Тело:** `{"model_id": "google/gemma-2-2b-it"}`

### `POST /hf/generate`
Генерация текста через локальную HF модель.

**Тело:**
```json
{
  "model_id": "google/gemma-2-2b-it",
  "prompt": "Привет",
  "max_new_tokens": 512,
  "temperature": 0.7
}
```

---

## llama.cpp

### `GET /llama/status`
Статус llama.cpp сервера: `running`, `pid`, `url`, `openai_url`, `last_error`.

### `GET /llama/models`
Сканировать `.gguf` файлы в `~/.models`, `~/.lmstudio/models` и опциональном `extra_dir`.

**Query:** `?extra_dir=D:\models`  
**Ответ:** `{"success": true, "models": [{"name": "...", "path": "...", "size_gb": 4.2}], "count": 3}`

### `POST /llama/start`
Запустить llama.cpp сервер.

**Тело:**
```json
{
  "model_path": "D:/models/gemma-2-2b-it-Q6_K.gguf",
  "port": 9780,
  "ctx_size": 4096,
  "threads": 8,
  "n_gpu_layers": 0,
  "host": "127.0.0.1",
  "copy_to_models": true
}
```

**Ответ:** `{"success": true, "pid": 1234, "model": "...", "url": "...", "openai_url": "...", "status": "starting"}`

### `POST /llama/stop`
Остановить llama.cpp сервер.

### `POST /llama/models/copy`
Скопировать `.gguf` файл в `~/.models`.

**Тело:** `{"model_path": "D:/gemma-2-2b-it-Q6_K.gguf"}`

---

## Ollama

### `GET /ollama/status`
Статус Ollama сервера: `running`, `version`, `url`.

### `GET /ollama/models`
Список локально доступных Ollama моделей.

### `POST /ollama/models/pull`
Скачать модель из Ollama Hub.

**Тело:** `{"model": "qwen2.5:0.5b"}`

### `POST /ollama/models/delete`
Удалить локальную Ollama модель.

**Тело:** `{"model": "qwen2.5:0.5b"}`

### `POST /ollama/generate`
Генерация текста через Ollama.

**Тело:** `{"model": "qwen2.5:0.5b", "prompt": "Привет", "max_tokens": 512, "temperature": 0.7}`

---

## RAG

### `GET /rag/status`
Статус RAG системы: `enabled`, `index_dir`, `model`, `chunk_size`, `top_k`, `total_chunks`.

### `PUT /rag/config`
Обновить конфигурацию RAG в `config.json`.

**Тело:**
```json
{
  "enabled": true,
  "index_dir": "./rag_index",
  "model": "sentence-transformers/all-MiniLM-L6-v2",
  "chunk_size": 1000,
  "top_k": 5
}
```

### `POST /rag/search`
Поиск в RAG индексе.

```bash
curl -X POST http://localhost:9696/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query": "текст запроса", "top_k": 5}'
```

**Тело:** `{"query": "текст запроса", "top_k": 5}`  
**Ответ:** `{"success": true, "results": [{"content": "...", "score": 0.95, "metadata": {...}}], "total": 2}`

### `POST /rag/rebuild`
Перестроить RAG индекс.

### `POST /rag/clear`
Удалить все файлы индекса из `index_dir`.

### `GET /rag/dirs`
Список директорий проекта пригодных для индексации (содержат `.md`, `.txt`, `.html`, `.rst`).

### `GET /rag/cwd`
Рабочая директория сервера (для разрешения путей).

### `GET /rag/browse`
Браузер файловой системы для выбора папки.

**Query:** `?path=C:\Users\user`  
**Ответ:** `{"success": true, "current": "...", "parent": "...", "dirs": [{"name": "...", "path": "..."}]}`

### `GET /rag/profiles`
Список всех RAG баз в `~/.rag/`.

### `POST /rag/profiles/load`
Переключить активную RAG базу (обновляет `config.json` и перезагружает индекс).

**Тело:** `{"name": "docs"}`

### `DELETE /rag/profiles/{name}`
Удалить RAG базу из `~/.rag/<name>/`.

### `POST /rag/build`
Собрать RAG индекс из директории.

```bash
curl -X POST http://localhost:9696/api/v1/rag/build \
  -H "Content-Type: application/json" \
  -d '{"docs_dir": "./docs", "model": "sentence-transformers/all-mpnet-base-v2", "chunk_size": 1000, "overlap": 50, "force": false}'
```

**Тело:**
```json
{
  "docs_dir": "./docs",
  "model": "sentence-transformers/all-mpnet-base-v2",
  "chunk_size": 1000,
  "overlap": 50,
  "force": false
}
```

**Ответ:** `{"success": true, "chunks": 142, "index_dir": "~/.rag/docs", "name": "docs"}`

### `POST /rag/extract/file`
Извлечь текст из загруженного файла для индексации.

```bash
curl -X POST http://localhost:9696/api/v1/rag/extract/file \
  -F "file=@/path/to/document.pdf"
```

**Тело:** `multipart/form-data` с полем `file`.  
Поддерживаемые форматы: PDF, DOCX, XLSX, PPTX, TXT, HTML, MD, JSON, XML, YAML, изображения (OCR), архивы (ZIP/RAR/7Z/TAR), EML, EPUB, ODT, RTF.

**Ответ:** `{"success": true, "filename": "...", "count": 3, "total_chars": 15000, "files": [...]}`

### `POST /rag/extract/url`
Извлечь текст с веб-страницы для индексации.

```bash
curl -X POST http://localhost:9696/api/v1/rag/extract/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "enable_javascript": false, "process_images": false, "web_page_timeout": 30}'
```

**Тело:**
```json
{
  "url": "https://example.com",
  "enable_javascript": false,
  "process_images": false,
  "web_page_timeout": 30
}
```

### `GET /rag/extract/formats`
Список поддерживаемых форматов файлов для извлечения текста.

---

## Agent

### `GET /agent/list`
Список зарегистрированных агентов.

**Ответ:** `{"success": true, "agents": [{"name": "powershell", "description": "..."}]}`

### `GET /agent/{agent_name}/tools`
Список инструментов агента.

### `POST /agent/run`
Запустить агента.

**Тело:**
```json
{
  "message": "Покажи список процессов",
  "agent": "powershell",
  "model": "qwen2.5-0.5b-instruct-generic-cpu:4",
  "temperature": 0.7,
  "max_tokens": 2048,
  "max_iterations": 5
}
```

**Ответ:**
```json
{
  "success": true,
  "answer": "...",
  "tool_calls": [{"tool": "run_powershell", "arguments": {...}, "result": "..."}],
  "iterations": 2,
  "agent": "powershell"
}
```

---

## MCP PowerShell

### `GET /mcp-powershell/servers`
Список всех MCP серверов из `mcp/settings.json` со статусом.

### `POST /mcp-powershell/servers/{name}/start`
Запустить MCP сервер по имени.

### `POST /mcp-powershell/servers/{name}/stop`
Остановить MCP сервер по имени.

### `GET /mcp-powershell/servers/{name}/status`
Статус конкретного MCP сервера: `running` / `stopped`, `pid`.

### `GET /mcp-powershell/settings`
Содержимое `mcp/settings.json`.

### `POST /mcp-powershell/settings`
Сохранить `mcp/settings.json`.

**Тело:** `{"settings": {"mcpServers": {...}}}`

---

## Local Models MCP Server

> Файл: `mcp/src/servers/local_models_mcp.py`  
> Транспорт: STDIO (JSON-RPC 2.0)  
> Требует: FastAPI Foundry запущен на `localhost:9696`

MCP сервер для подключения Claude Desktop и других MCP клиентов к локальным AI моделям.

### Маршрутизация моделей

Выбор бэкенда определяется префиксом в поле `model`:

| Префикс | Бэкенд |
|---|---|
| без префикса | Foundry Local (ONNX) |
| `llama::<path>` | llama.cpp |
| `ollama::<name>` | Ollama |
| `hf::<model_id>` | HuggingFace Transformers |

### `generate` — Генерация текста

**Аргументы:**
```json
{
  "prompt": "Ваш запрос",
  "model": "",
  "max_tokens": 512,
  "temperature": 0.7
}
```

**Ответ:** строка с ответом модели или `❌ <описание ошибки>`.

### `chat` — Чат с историей

**Аргументы:**
```json
{
  "message": "Сообщение пользователя",
  "model": "",
  "session_id": "mcp-default",
  "max_tokens": 512
}
```

Поле `session_id` обеспечивает непрерывность истории между запросами. По умолчанию `mcp-default`.

### `list_models` — Список моделей

Аргументы не требуются. Возвращает JSON со всеми доступными моделями изо всех бэкендов.

### `rag_search` — Поиск по RAG

**Аргументы:**
```json
{
  "query": "Текст запроса",
  "top_k": 3
}
```

**Ответ:** JSON со списком релевантных чанков с полями `content`, `score`, `metadata`.

### `health` — Статус сервиса

Аргументы не требуются. Возвращает JSON со статусом FastAPI Foundry и Foundry Local.

### Переменные окружения

| Переменная | По умолчанию | Описание |
|---|---|---|
| `FASTAPI_BASE_URL` | `http://localhost:9696` | Базовый URL FastAPI Foundry |
| `MCP_HTTP_TIMEOUT` | `120` | Таймаут HTTP запросов (сек) |`

---

## Config

### `GET /config`
Полная конфигурация из `config.json` + runtime значения Foundry.

### `PATCH /config`
Частичное обновление конфигурации. Поддерживает dot-notation.

**Тело:** `{"foundry_ai.default_model": "qwen2.5-0.5b-instruct-generic-cpu:4"}`

### `POST /config`
Полная замена `config.json` (создаёт бэкап).

**Тело:** `{"config": {...полный объект конфигурации...}}`

### `GET /config/raw`
Содержимое `config.json` как сырой текст (для редактора).

### `POST /config/raw`
Запись `config.json` из редактора (валидирует JSON).

**Тело:** `{"content": "{...}"}`

### `GET /config/env-raw`
Содержимое `.env` как сырой текст.

### `POST /config/env-raw`
Запись `.env` из редактора.

**Тело:** `{"content": "KEY=value\n..."}`

### `POST /config/env`
Сохранить одну переменную окружения в `.env`.

**Тело:** `{"key": "HF_TOKEN", "value": "hf_..."}`

### `GET /config/provider-keys`
Ключи API провайдеров из `.env` (Gemini, OpenAI, Anthropic, Mistral, Groq и др.).

### `POST /config/provider-keys`
Сохранить ключи провайдеров в `.env`.

**Тело:** `{"keys": {"openai": "sk-...", "gemini": "AIza..."}}`

### `GET /config/export`
Экспорт всех настроек в один JSON: `config.json` + `.env` + MCP конфиги.  
Возвращает файл для скачивания.

### `POST /config/import`
Импорт полного бэкапа настроек.

**Тело:** `{"config": {...экспортированный объект...}, "merge": false}`

### `GET /config/extension-export`
Экспорт ключей провайдеров в формат браузерного расширения.

### `POST /config/extension-import`
Импорт ключей из формата браузерного расширения (v1/v2).

---

## Logs

### `GET /logs`
Отфильтрованные строки лога.

**Query параметры:**
- `file` — имя файла (default: `fastapi-foundry.log`)
- `lines` — количество строк (default: 200, max: 5000)
- `level` — фильтр уровня: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- `search` — текстовый поиск (case-insensitive)
- `offset` — пропустить последние N строк (пагинация)

**Ответ:** `{"success": true, "lines": [...], "returned": 50, "filtered_total": 200, "total_lines": 1500, "has_more": true}`

### `GET /logs/files`
Список доступных лог-файлов с размерами.

### `POST /logs/clear`
Очистить лог-файл.

**Query:** `?file=fastapi-foundry.log`

### `GET /logs/download`
Скачать лог-файл.

**Query:** `?file=fastapi-foundry.log`

### `GET /logs/recent`
Последние 100 записей из всех лог-файлов (парсинг формата `timestamp | level | logger | message`).

### `POST /logs/web`
Записать сообщение с веб-интерфейса в лог.

**Тело:** `{"message": "...", "level": "info"}`

---

## Converter

### `GET /converter/status`
Доступность зависимостей конвертера (`optimum`, `onnxruntime-tools`).

### `POST /converter/convert`
Конвертировать `.gguf` файл в ONNX.

**Тело:**
```json
{
  "gguf_path": "D:/models/model.gguf",
  "output_dir": "./artifacts/onnx",
  "model_type": "gpt2",
  "opset": 17,
  "optimize": true
}
```

---

## AI (расширенные)

### `POST /ai/generate`
Генерация с расширенными параметрами (`top_p`, `top_k`, `presence_penalty`, `frequency_penalty`, `stop`, `use_rag`).

### `POST /ai/generate/stream`
Стриминговая генерация (SSE).

### `GET /ai/models`
Список моделей с детальной информацией.

### `GET /ai/models/recommended`
Рекомендуемые модели по категориям: `reasoning`, `coding`, `general`, `fast`, `quality`.

### `POST /ai/models/{model_id}/load`
Загрузить модель в память.

### `POST /ai/models/{model_id}/unload`
Выгрузить модель из памяти.

### `GET /ai/health`
Проверка здоровья AI сервиса.

### `POST /ai/chat`
Чат с историей сообщений (OpenAI-совместимый формат ответа).

**Тело:** `{"messages": [{"role": "user", "content": "..."}], "model": "...", "temperature": 0.7}`

### `POST /ai/optimize`
Подбор оптимальной модели и параметров для задачи.

**Тело:** `{"task_type": "coding", "model_preference": "balanced"}`

---

## System

### `GET /system/stats`
Использование RAM и CPU (требует `psutil`).

**Ответ:** `{"success": true, "ram_used_mb": 4096.0, "ram_total_mb": 16384.0, "cpu_pct": 12.5}`

---

## HelpDesk

### `GET /helpdesk/dialogs`
Диалоги HelpDesk бота, сгруппированные по `chat_id`.

**Ответ:**
```json
{
  "success": true,
  "dialogs": {
    "123456789": [
      {"role": "user", "text": "Как запустить?", "ts": "2025-...", "username": "ivan"},
      {"role": "assistant", "text": "Запустите start.ps1...", "ts": "2025-...", "username": "ivan"}
    ]
  }
}
```

### `GET /helpdesk/rag-profiles`
Список RAG профилей из `~/.rag/`.

**Ответ:** `{"success": true, "profiles": [{"name": "support", "path": "...", "has_index": true, "description": "..."}]}`

### `POST /helpdesk/rag-profiles`
Создать новый RAG профиль.

**Тело:** `{"name": "support", "description": "Project documentation"}`  
**Ответ:** `{"success": true, "path": "C:/Users/user/.rag/support"}`

### `DELETE /helpdesk/rag-profiles/{name}`
Soft-delete профиля (переименование в `<name>~`).

**Ответ:** `{"success": true, "error": null}`

### `GET /helpdesk/config`
Статус HelpDesk бота и активный RAG профиль.

**Ответ:** `{"success": true, "enabled": true, "rag_profile": "support"}`
