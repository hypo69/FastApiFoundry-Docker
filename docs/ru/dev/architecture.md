# Архитектура FastAPI Foundry

## Обзор системы

```
Browser / API Client
        │ HTTP
        ▼
┌─────────────────────────────────────────┐
│           FastAPI (port 9696)           │
│  src/api/app.py  ←  create_app()        │
│                                         │
│  /api/v1/health      health.py          │
│  /api/v1/generate    generate.py        │
│  /api/v1/chat        chat_endpoints.py  │
│  /api/v1/rag/*       rag.py             │
│  /api/v1/hf/*        hf_models.py       │
│  /api/v1/llama/*     llama_cpp.py       │
│  /api/v1/foundry/*   foundry*.py        │
│  /api/v1/agent/*     agent.py           │
│  /api/v1/config      config.py          │
│  /static             static/            │
└──────────┬──────────────────────────────┘
           │
    ┌──────┴───────┬──────────────┬──────────────┐
    ▼              ▼              ▼              ▼
Foundry Local  HuggingFace   llama.cpp      Ollama
(port dynamic) Transformers  (port 8080)  (port 11434)
ONNX models    PyTorch/HF    GGUF models   GGUF models
```

---

## Startup workflow

### Полный запуск через start.ps1

```
start.ps1
  │
  ├─[1] venv проверка
  │      ├─ venv\Scripts\python.exe найден → активировать
  │      └─ не найден → запустить install.ps1 → создать venv
  │
  ├─[2] Load-EnvFile ".env"
  │      └─ SetEnvironmentVariable для каждой KEY=VALUE
  │
  ├─[3] Get-FoundryPort()
  │      ├─ Get-Process "Inference.Service.Agent*"
  │      │   ├─ найден → netstat -ano | grep PID | grep LISTENING
  │      │   │            └─ GET /v1/models → HTTP 200 → вернуть порт
  │      │   └─ не найден → foundry service start
  │      │                   └─ опрос 10×2 сек → FOUNDRY_DYNAMIC_PORT=<port>
  │      └─ FOUNDRY_BASE_URL = http://localhost:<port>/v1/
  │
  ├─[4] config.json → docs_server.enabled?
  │      └─ true → mkdocs serve -a 0.0.0.0:<port>  (фоновое окно)
  │
  ├─[5] .env → LLAMA_MODEL_PATH + LLAMA_AUTO_START=true?
  │      └─ true → scripts\llama-start.ps1 -ModelPath ... -Port ...  (фоновое окно)
  │                 └─ LLAMA_BASE_URL = http://127.0.0.1:<port>/v1
  │
  ├─[6] %TEMP%\fastapi-foundry-installer.pid → убить installer-сервер (если жив)
  │
  ├─[6.5] %TEMP%\fastapi-foundry.pid → убить предыдущий процесс FastAPI
  │
  └─[7] venv\Scripts\python.exe run.py  ← блокирующий вызов
          │
          run.py
            ├─ UTF-8 stdout/stderr (Windows)
            ├─ src/utils/env_processor → load_env_variables()
            ├─ Config() singleton → config.json
            ├─ get_server_port():
            │   ├─ port_auto_find_free=false → config.api_port (9696)
            │   └─ port_auto_find_free=true  → scan 9696–9796
            ├─ resolve_foundry_base_url():
            │   1. os.getenv("FOUNDRY_BASE_URL")
            │   2. os.getenv("FOUNDRY_DYNAMIC_PORT")
            │   3. tasklist → Inference.Service.Agent* → netstat → /v1/models
            ├─ config.foundry_base_url = url
            └─ uvicorn.run("src.api.main:app", port=port, ...)
                  │
                  lifespan(app):
                    ├─ await rag_system.initialize()
                    │   └─ загружает FAISS индекс из rag_index/
                    ├─ if auto_load_default and default_model:
                    │   └─ subprocess: foundry model load <model>
                    yield
                    └─ await foundry_client.close()
```

### Прямой запуск (без start.ps1)

```powershell
# Если Foundry уже запущен и venv активирован
venv\Scripts\python.exe run.py
```

`run.py` самостоятельно находит Foundry через `tasklist` + `netstat`.

---

## Reloader (WatchFiles)

Когда в `config.json` включён режим `dev` или явно задан `reload: true`, Uvicorn запускает **два процесса**:

```
Процесс 1 — reloader (WatchFiles)
  └─ Процесс 2 — worker (фактический FastAPI сервер)
```

### Что это значит на практике

```
reloader process [33548] using WatchFiles   ← это нормально
Started server process [33612]              ← это и есть сервер
```

- **Reloader** следит за изменениями файлов `*.py` в `src/` и перезапускает worker при каждом сохранении
- **Worker** — реальный процесс, обрабатывающий HTTP запросы
- Оба процесса видны в `tasklist` / диспетчере задач

### Управляется через config.json

```json
{
  "fastapi_server": {
    "mode": "dev"
  }
}
```

| `mode` | `reload` | Поведение |
|---|---|---|
| `dev` | `true` | Reloader активен — два процесса, hot reload |
| `prod` | `false` | Один процесс, без слежки за файлами |

!!! warning "Workers при reload=true"
    Uvicorn не поддерживает `workers > 1` совместно с `reload=true`.
    `run.py` автоматически форсирует `workers=1` при включённом reload.

### Защита от дублирования вывода

При `reload=true` `run.py` запускается дважды — сначала как reloader, потом как worker.
Чтобы стартовые сообщения не печатались дважды, используется флаг:

```python
_in_reloader_child = os.getenv('_UVICORN_CHILD') == '1'
if not _in_reloader_child:
    os.environ['_UVICORN_CHILD'] = '1'
    # Вывод только в основном процессе
```

### Отключение reloader

Если reloader мешает (например, в Docker или при профилировании):

```json
{
  "fastapi_server": {
    "mode": "prod"
  }
}
```

Или напрямую через переменную окружения:

```env
FASTAPI_RELOAD=false
```

---

## Конфигурация

### Приоритет источников

```
.env (секреты, токены, пути)
  └─ переопределяет →
config.json (публичные настройки)
  └─ читается через →
Config singleton (config_manager.py)
  └─ доступен везде как →
from src.core.config import config
```

### Секции config.json

```json
{
  "fastapi_server": {
    "host": "0.0.0.0",
    "port": 9696,
    "auto_find_free_port": false,
    "mode": "dev",
    "workers": 1
  },
  "foundry_ai": {
    "default_model": "qwen3-0.6b-generic-cpu:4",
    "auto_load_default": true,
    "temperature": 0.7,
    "max_tokens": 2048
  },
  "rag_system": {
    "enabled": true,
    "index_dir": "rag_index",
    "chunk_size": 1000
  },
  "docs_server": {
    "enabled": false,
    "port": 9697
  },
  "llama_cpp": {
    "port": 9780,
    "host": "127.0.0.1"
  },
  "huggingface": {
    "models_dir": "./models/hf",
    "device": "auto",
    "default_max_new_tokens": 512,
    "default_temperature": 0.7
  }
}
```

### Config singleton

```python
from src.core.config import config

config.api_port            # int, порт FastAPI
config.api_host            # str, хост
config.api_reload          # bool, hot reload
config.foundry_base_url    # str | None, URL Foundry API
config.foundry_base_url = "http://localhost:50477/v1/"  # setter
config.foundry_default_model   # str
config.foundry_auto_load_default  # bool
config.rag_enabled         # bool
config.rag_index_dir       # str, путь к индексу
config.rag_model           # str, модель эмбеддингов
config.rag_top_k           # int
config.dir_models          # str, ~/.models
config.dir_hf_models       # str, ~/.hf_models

config.get_section("huggingface")   # dict секции
config.get_raw_config()             # весь config.json
config.update_config(new_dict)      # сохранить в файл
config.reload_config()              # перечитать файл
```

---

## Модули src/

### src/api/

| Файл | Назначение |
|---|---|
| `app.py` | `create_app()` — фабрика FastAPI, регистрация роутеров, lifespan, CORS, middleware |
| `main.py` | `app = create_app()` — точка входа для Uvicorn |
| `models.py` | Pydantic модели запросов/ответов |
| `endpoints/` | Роутеры по функциональным областям |

Все роутеры подключаются с префиксом `/api/v1`:

```python
app.include_router(health.router,        prefix="/api/v1")
app.include_router(generate.router,      prefix="/api/v1")
app.include_router(chat_router,          prefix="/api/v1")
app.include_router(rag.router,           prefix="/api/v1")
app.include_router(hf_router,            prefix="/api/v1")
app.include_router(llama_router,         prefix="/api/v1")
app.include_router(foundry_mgmt_router,  prefix="/api/v1")
app.include_router(agent_router,         prefix="/api/v1")
app.include_router(converter_router,     prefix="/api/v1")
```

### src/models/

| Файл | Назначение |
|---|---|
| `foundry_client.py` | Async HTTP клиент к Foundry API (aiohttp, singleton) |
| `enhanced_foundry_client.py` | Расширенный клиент с дополнительными методами |
| `hf_client.py` | HuggingFace: скачивание, загрузка в память, inference |
| `model_manager.py` | Унифицированный менеджер всех бэкендов |

### src/rag/

| Файл | Назначение |
|---|---|
| `rag_system.py` | `RAGSystem` — FAISS поиск, singleton `rag_system` |
| `indexer.py` | Индексация документов, генерация эмбеддингов |

### src/agents/

| Файл | Назначение |
|---|---|
| `base.py` | `BaseAgent` — абстрактный класс агента |
| `powershell_agent.py` | `PowerShellAgent` — выполнение команд через MCP |

### src/utils/

| Файл | Назначение |
|---|---|
| `env_processor.py` | Загрузка `.env`, обработка переменных |
| `foundry_finder.py` | Поиск порта Foundry |
| `logging_config.py` | Настройка логирования |
| `logging_system.py` | Структурированное логирование (JSONL) |
| `log_analyzer.py` | Анализ лог-файлов |

---

## Паттерны кода

### Singleton (Config, FoundryClient, RAGSystem)

```python
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

config = Config()  # глобальный экземпляр
```

### Async HTTP клиент (FoundryClient)

```python
class FoundryClient:
    def __init__(self):
        self.session = None

    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=...)
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
```

### Ответы API

Все endpoints возвращают единый формат:

```python
# Успех
{"success": True, "data": ..., "count": N}

# Ошибка
{"success": False, "error": "Human-readable message"}
```

### CPU-bound операции в async контексте

```python
# FAISS, SentenceTransformer, HF inference — блокирующие операции
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, blocking_function, arg1, arg2)
```

### Префиксы моделей

```python
if model_id.startswith("hf::"):
    # HuggingFace Transformers
elif model_id.startswith("llama::"):
    # llama.cpp
else:
    # Foundry Local
```
