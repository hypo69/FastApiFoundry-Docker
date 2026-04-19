# Подсистема логирования — документация разработчика

## Архитектура

```
Вызов logger.info(...)  /  logger.error(...)
           │
           ▼
  logging.Logger  (stdlib, name='fastapi-foundry')
           │
    ┌──────┼──────────────┬──────────────────────┐
    ▼      ▼              ▼                      ▼
StreamHandler  RotatingFileHandler  RotatingFileHandler  RotatingFileHandler
(консоль)      (*.log, все уровни)  (*-errors.log)       (*-structured.jsonl)
```

Все handlers подключаются один раз при импорте `src.logger` через `_build_logger()`.
Дочерние логгеры (`logging.getLogger(__name__)`) наследуют handlers автоматически.

---

## Файлы модуля

| Файл | Назначение |
|---|---|
| `src/logger/__init__.py` | Ядро: `_build_logger`, `get_logger`, глобальный `logger` |
| `src/utils/logging_config.py` | Bootstrap: применяет уровень из `LOG_LEVEL`, глушит шумные библиотеки |
| `src/utils/logging_system.py` | Фасад `StructuredLogger` с `timer()` и хелперами |
| `src/utils/log_analyzer.py` | Анализ JSONL-логов: метрики, ошибки, производительность |
| `src/api/endpoints/logs.py` | REST API для просмотрщика логов |
| `static/partials/_tab_logs.html` | HTML вкладки Logs |
| `static/js/ui.js` | Логика просмотрщика (`initLogViewer`, `refreshLogs`) |

---

## Handlers и их назначение

| Handler | Файл | Уровень | Размер | Копий |
|---|---|---|---|---|
| `StreamHandler` | stdout | DEBUG | — | — |
| `RotatingFileHandler` | `fastapi-foundry.log` | DEBUG | 10 МБ | 5 |
| `RotatingFileHandler` | `fastapi-foundry-errors.log` | ERROR | 5 МБ | 3 |
| `RotatingFileHandler` | `fastapi-foundry-structured.jsonl` | INFO | 20 МБ | 3 |

---

## Использование в модулях

### Базовый вариант (рекомендуется)

```python
import logging
logger = logging.getLogger(__name__)

logger.info("✅ Model loaded")
logger.warning("⚠️ Foundry unavailable")
logger.error("❌ Request failed", exc_info=True)
```

### Через get_logger

```python
from src.logger import get_logger
logger = get_logger(__name__)
```

### StructuredLogger с kwargs

```python
from src.utils.logging_system import get_logger
log = get_logger('rag-system')

log.info("Index loaded", chunks=512, vectors=512)
log.error("Search failed", query=query, error=str(e))
```

kwargs сериализуются в JSON и добавляются к строке сообщения — попадают в `.jsonl` файл.

### Timer context manager

```python
with log.timer('rag-search', query=query):
    results = await rag_system.search(query)
# Автоматически логирует: ✅ rag-search | {"duration": 0.123, "query": "..."}
```

### API request logging

```python
log.log_api_request('POST', '/api/v1/generate', 200, duration=0.45)
```

### Model operation logging

```python
log.log_model_operation('qwen3-0.6b', 'load', 'success', duration=3.2)
log.log_model_operation('qwen3-0.6b', 'generate', 'error')
```

---

## Инициализация при старте

В `run.py`:

```python
from src.logger import logger as _root_logger   # triggers _build_logger()
from src.utils.logging_config import setup_logging
setup_logging(os.getenv('LOG_LEVEL', 'INFO'))
```

`_build_logger()` вызывается один раз при импорте `src.logger`.
Повторные вызовы `get_logger(name)` возвращают дочерние логгеры через `logging.getLogger(name)`.

---

## Logs API

Endpoints в `src/api/endpoints/logs.py`:

| Метод | URL | Описание |
|---|---|---|
| `GET` | `/api/v1/logs/files` | Список доступных файлов с размерами |
| `GET` | `/api/v1/logs` | Строки лога с фильтрацией и пагинацией |
| `POST` | `/api/v1/logs/clear` | Очистить файл |
| `GET` | `/api/v1/logs/download` | Скачать файл |

Параметры `GET /api/v1/logs`:

| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `file` | string | `fastapi-foundry.log` | Имя файла |
| `lines` | int | 200 | Макс. строк (1–5000) |
| `level` | string | `""` | Фильтр уровня |
| `search` | string | `""` | Текстовый поиск |
| `offset` | int | 0 | Пагинация (пропустить N строк с хвоста) |

---

## Log Viewer (frontend)

Логика в `static/js/ui.js`, инициализация через `initLogViewer()`.

```
initLogViewer()
    │
    ├── _loadFileList()   → GET /logs/files  → заполняет <select>
    ├── refreshLogs()     → GET /logs?...    → рендерит строки
    │
    └── event listeners:
        ├── file/level/lines change  → resetAndRefresh()
        ├── search input             → debounce 400ms → resetAndRefresh()
        ├── auto-refresh toggle      → setInterval 5s
        ├── load-more button         → _logOffset += lines → refreshLogs(append=true)
        ├── download button          → window.open /logs/download
        └── clear button             → POST /logs/clear
```

Цветовая схема строк:

| Уровень | Цвет |
|---|---|
| DEBUG | серый `#6e7681` |
| INFO | голубой `#79c0ff` |
| WARNING | жёлтый `#e3b341` |
| ERROR / CRITICAL | красный `#ff7b72` |

---

## Конфигурация

| Параметр | Где задаётся | По умолчанию |
|---|---|---|
| Уровень логирования | `.env` → `LOG_LEVEL` | `INFO` |
| Директория логов | `src/logger/__init__.py` → `log_dir` | `logs/` |
| Размер основного лога | `_build_logger()` → `maxBytes` | 10 МБ |
| Размер errors лога | `_build_logger()` → `maxBytes` | 5 МБ |
| Размер JSONL лога | `_build_logger()` → `maxBytes` | 20 МБ |

---

## Добавление нового handler

```python
# В src/logger/__init__.py, внутри _build_logger():
custom_handler = MyCustomHandler(...)
custom_handler.setLevel(logging.ERROR)
log.addHandler(custom_handler)
```

---

## Структура файлов логов

```
logs/
├── fastapi-foundry.log           # Все события (ротация 10MB × 5)
├── fastapi-foundry.log.1         # Предыдущая версия
├── fastapi-foundry-errors.log    # Только ERROR+ (ротация 5MB × 3)
├── fastapi-foundry-structured.jsonl  # SIEM JSON (ротация 20MB × 3)
└── app.log                       # Uvicorn startup log
```

---

## Политика обработки ошибок (try/except)

### Принципы

Каждый `except` блок в проекте следует трём правилам:

1. **Комментарий — почему упал.** Объясняет конкретную причину исключения, а не просто "что-то пошло не так".
2. **Логирование через `logger`.** Уровень зависит от серьёзности: `error` — функция не выполнена, `warning` — деградация, но работа продолжается.
3. **Возврат безопасного значения.** API-методы возвращают `{"success": False, "error": "..."}`, утилиты возвращают `None` / `False` / `[]`.

### Шаблон

```python
try:
    result = do_something()
except SpecificError as e:
    # SpecificError happens when <конкретная причина>
    logger.error(f'❌ Operation failed: {e}')
    return {"success": False, "error": str(e)}
```

### Что покрыто в каждом модуле

| Модуль | Покрытые сценарии |
|---|---|
| `config_manager.py` | Отсутствие `config.json`, невалидный JSON, ошибка записи на диск |
| `src/utils/env_processor.py` | Ошибка парсинга `.env`, невалидный JSON конфига, отсутствие обязательной переменной окружения |
| `src/utils/foundry_finder.py` | Невалидный `FOUNDRY_DYNAMIC_PORT`, `ConnectionError`, `Timeout`, неожиданные сетевые ошибки |
| `src/rag/rag_system.py` | Ошибка загрузки модели эмбеддингов, повреждённый FAISS индекс, невалидный `chunks.json`, GPU OOM при поиске, ошибка удаления файлов |
| `src/rag/indexer.py` | Ошибка загрузки модели, `UnicodeDecodeError` при чтении файлов, ошибка батч-эмбеддинга, ошибка записи индекса на диск |
| `src/models/model_manager.py` | Невалидный `models_config.json`, ошибка записи конфига, отсутствующие поля в `model_data`, сетевые ошибки всех провайдеров |
| `src/models/foundry_client.py` | Недоступность Foundry, HTTP ошибки, ошибки JSON парсинга стриминга |
| `src/models/hf_client.py` | Ошибки доступа к HuggingFace Hub (401/403), ошибки загрузки модели в память, GPU OOM при инференсе |

### Уровни логирования при ошибках

| Ситуация | Уровень | Пример |
|---|---|---|
| Функция не выполнена, данные потеряны | `ERROR` | Не удалось записать конфиг на диск |
| Функция деградировала, но работает | `WARNING` | Файл не в UTF-8, пропущен при индексации |
| Ожидаемое отсутствие ресурса | `WARNING` | Foundry не найден на известных портах |
| Детали для отладки | `DEBUG` | Порт X: connection refused |
