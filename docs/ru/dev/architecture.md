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

## Управление зависимостями (requirements)

Проект использует **один файл** зависимостей:

| Файл | Назначение |
|---|---|
| `requirements.txt` | Все зависимости: FastAPI, RAG, ML, PDF, OCR, тесты, MkDocs |
| `docs/requirements.txt` | MkDocs плагины (только для сборки документации) |

---

### Пересоздание requirements.txt

Для обновления `requirements.txt` используйте утилиту `scripts/create_requirements.ps1`.

Скрипт поддерживает три режима:

| Режим | Описание | Когда использовать |
|---|---|---|
| `pipreqs` | Только пакеты, реально импортируемые в коде | Рекомендуется — чистый минимальный файл |
| `freeze` | Полный снимок всего venv (`pip freeze`) | Когда нужна точная воспроизводимость |

#### Использование

```powershell
# Рекомендуемый способ — только реально используемые пакеты
powershell -ExecutionPolicy Bypass -File .\scripts\create_requirements.ps1 -Mode pipreqs

# Полный снимок venv
powershell -ExecutionPolicy Bypass -File .\scripts\create_requirements.ps1 -Mode freeze
```

#### Параметры скрипта

| Параметр | По умолчанию | Описание |
|---|---|---|
| `-Mode` | `pipreqs` | Режим: `pipreqs`, `freeze` |
| `-ProjectPath` | корень проекта | Путь к проекту |
| `-VenvPath` | `<корень>\venv` | Путь к виртуальному окружению |

#### Что делает каждый режим

**`pipreqs`** — анализирует импорты в `src/` и генерирует минимальный `requirements.txt`:
```
1. Активирует venv
2. Устанавливает pipreqs (если нет)
3. Запускает: pipreqs <ProjectPath> --force
4. Записывает requirements.txt в корень проекта
```

**`freeze`** — снимок текущего окружения:
```
1. Активирует venv
2. Запускает: pip freeze
3. Записывает вывод в requirements.txt
```

!!! tip "Рекомендуемый workflow при обновлении зависимостей"
    ```powershell
    # 1. Установить новый пакет
    venv\Scripts\pip.exe install some-package

    # 2. Обновить requirements.txt
    powershell -ExecutionPolicy Bypass -File .\scripts\create_requirements.ps1 -Mode freeze

    # 3. Закоммитить
    git add requirements.txt
    git commit -m "deps: add some-package"
    ```

---

## Архитектура

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

# Сервер FastAPI
config.api_host            # str,  хост (default: '0.0.0.0')
config.api_port            # int,  порт (default: 9696)
config.api_workers         # int,  количество воркеров (default: 1)
config.api_reload          # bool, hot reload (default: True)
config.api_log_level       # str,  уровень логов uvicorn (default: 'INFO')

# Foundry AI
config.foundry_base_url              # str,  URL Foundry API (runtime override)
config.foundry_base_url = "http://localhost:50477/v1/"  # setter
config.foundry_default_model         # str,  модель по умолчанию
config.foundry_auto_load_default     # bool, автозагрузка при старте
config.foundry_temperature           # float, температура (default: 0.7)
config.foundry_max_tokens            # int,   максимум токенов (default: 2048)
config.foundry_top_p                 # float, top-p сэмплинг (default: 0.9)
config.foundry_top_k                 # int,   top-k сэмплинг (default: 50)
config.foundry_models_dir            # str,   путь к кэшу Foundry

# llama.cpp
config.llama_model_path    # str, путь к .gguf файлу
config.llama_models_dir    # str, директория GGUF моделей

# RAG
config.rag_enabled         # bool, включена ли RAG
config.rag_index_dir       # str,  путь к FAISS индексу
config.rag_model           # str,  модель эмбеддингов
config.rag_chunk_size      # int,  размер чанка (default: 1000)
config.rag_top_k           # int,  количество результатов поиска (default: 5)

# Директории
config.dir_models          # str, ~/.models  — GGUF модели
config.dir_rag             # str, ~/.rag     — RAG индексы
config.dir_hf_models       # str, ~/.cache/huggingface/hub — HuggingFace модели

# Model Manager
config.model_manager_max_loaded      # int,   макс одновременно загруженных моделей (default: 1)
config.model_manager_ttl_seconds     # int,   TTL бездействия в секундах (default: 600)
config.model_manager_max_ram_percent # float, порог RAM для LRU вытеснения (default: 80.0)

# Логирование
config.logging_retention_hours  # int, хранение логов в часах (default: 24)
config.history_retention_days   # int, хранение истории чата в днях (default: 7)
config.archive_max_size_gb      # int, макс размер архива в GB (default: 2)

# Методы
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

| Файл | Префикс | Назначение | API |
|---|---|---|---|
| `endpoints/main.py` | `/` | Главная страница, статика | — |
| `endpoints/health.py` | `/api/v1/health` | Проверка здоровья сервиса | [Health](api_reference.md#health) |
| `endpoints/models.py` | `/api/v1/models` | Список всех моделей, пакетная генерация | [Models](api_reference.md#models) |
| `endpoints/generate.py` | `/api/v1/generate` | Генерация текста, маршрутизация по префиксу модели | [Generate](api_reference.md#generate) |
| `endpoints/ai_endpoints.py` | `/api/v1/ai` | Расширенная генерация, стриминг, рекомендации | [AI](api_reference.md#ai) |
| `endpoints/chat_endpoints.py` | `/api/v1/chat` | Чат с историей сессии, SSE стриминг | [Chat](api_reference.md#chat) |
| `endpoints/foundry.py` | `/api/v1/foundry` | Статус Foundry, запуск/остановка сервиса | [Foundry](api_reference.md#foundry) |
| `endpoints/foundry_management.py` | `/api/v1/foundry/service` | Управление сервисом Foundry через CLI | [Foundry](api_reference.md#foundry) |
| `endpoints/foundry_models.py` | `/api/v1/foundry/models` | Скачивание, загрузка, выгрузка моделей Foundry | [Foundry Models](api_reference.md#foundry-models) |
| `endpoints/hf_models.py` | `/api/v1/hf` | HuggingFace: скачивание, загрузка, inference | [HuggingFace](api_reference.md#huggingface) |
| `endpoints/llama_cpp.py` | `/api/v1/llama` | Запуск/остановка llama-server, скан моделей | [llama.cpp](api_reference.md#llamacpp) |
| `endpoints/ollama.py` | `/api/v1/ollama` | Интеграция с Ollama | [Ollama](api_reference.md#ollama) |
| `endpoints/rag.py` | `/api/v1/rag` | Поиск, индексация, профили, извлечение текста | [RAG](api_reference.md#rag) |
| `endpoints/agent.py` | `/api/v1/agent` | Запуск агентов, список инструментов | [Agent](api_reference.md#agent) |
| `endpoints/mcp_powershell.py` | `/api/v1/mcp-powershell` | Управление MCP серверами | [MCP PowerShell](api_reference.md#mcp-powershell) |
| `endpoints/mcp_agent_endpoints.py` | `/api/v1/mcp-agent` | Обнаружение MCP инструментов для агента | [MCP Agent](mcp_agent.md#api-reference) |
| `endpoints/config.py` | `/api/v1/config` | Чтение/запись `config.json` и `.env` | [Config](api_reference.md#config) |
| `endpoints/logs.py` | `/api/v1/logs` | Чтение, фильтрация, очистка логов | [Logs](api_reference.md#logs) |
| `endpoints/converter.py` | `/api/v1/converter` | Конвертация GGUF → ONNX | [Converter](api_reference.md#converter) |
| `endpoints/system_stats.py` | `/api/v1/system` | Статистика RAM/CPU | [System](api_reference.md#system) |
| `endpoints/translator.py` | `/api/v1/translate` | Перевод текста (MyMemory / LibreTranslate) | — |
| `endpoints/support.py` | `/api/v1/support` | Техподдержка | — |
| `endpoints/helpdesk.py` | `/api/v1/helpdesk` | Диалоги HelpDesk бота, RAG профили | [HelpDesk](api_reference.md#helpdesk) |

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
