# Конфигурация

## Обзор

Вся конфигурация проекта хранится в двух файлах:

| Файл | Назначение |
|---|---|
| `config.json` | Публичные настройки (порты, модели, RAG, логирование) |
| `.env` | Секреты и переопределения (токены, пути, URL) |

Оба файла читаются **один раз при старте** через класс `Config` в `config_manager.py`.
Результат доступен через глобальный синглтон `config`.

---

## Синглтон `Config`

```python
from config_manager import config
```

Или внутри пакета `src/`:

```python
from src.core.config import config   # re-export из config_manager
```

`Config` реализует паттерн **Singleton** через `__new__`:

```python
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
```

`_load_config()` вызывается ровно один раз — при первом обращении к классу.
Все последующие `Config()` возвращают тот же объект.

### Принудительная перезагрузка

```python
config.reload_config()   # перечитывает config.json с диска
```

---

## Структура `config.json`

```json
{
  "fastapi_server":  { "host", "port", "workers", "mode" },
  "foundry_ai":      { "base_url", "default_model", "temperature", "max_tokens", "auto_load_default" },
  "rag_system":      { "enabled", "index_dir", "chunk_size" },
  "security":        { "api_key", "https_enabled" },
  "logging":         { "level", "file" },
  "development":     { "debug", "verbose" },
  "docs_server":     { "enabled", "port" },
  "llama_cpp":       { "port", "host" },
  "directories":     { "models", "rag", "hf_models" },
  "huggingface":     { "models_dir", "device", "default_max_new_tokens" },
  "translator":      { "default_provider", ... },
  "text_extractor":  { "max_file_size_mb", "processing_timeout_seconds", "ocr_languages", ... },
  "app":             { "language" }
}
```

### Доступ к секции

```python
section = config.get_section("text_extractor")
# → {"max_file_size_mb": 20, "ocr_languages": "rus+eng", ...}
```

### Готовые свойства

```python
config.api_port            # fastapi_server.port
config.foundry_base_url    # динамически задаётся в run.py
config.rag_enabled         # rag_system.enabled
config.dir_models          # directories.models (expanduser)
```

---

## Секция `text_extractor`

Настройки модуля `src/rag/text_extractor_4_rag/` читаются через тот же синглтон:

```json
"text_extractor": {
  "max_file_size_mb": 20,
  "processing_timeout_seconds": 300,
  "ocr_languages": "rus+eng",
  "enable_javascript": false,
  "max_images_per_page": 20,
  "web_page_timeout": 30,
  "enable_resource_limits": true
}
```

Класс `Settings` в `src/rag/text_extractor_4_rag/config.py` читает эту секцию через:

```python
from config_manager import config as _project_config

def _cfg(key, default=None):
    return _project_config.get_section("text_extractor").get(key, default)
```

### Приоритет значений

```
env var  >  config.json [text_extractor]  >  встроенный default
```

Пример переопределения через переменную окружения:

```env
OCR_LANGUAGES=deu+eng
MAX_FILE_SIZE=52428800
```

### Использование в коде

```python
from src.rag.text_extractor_4_rag.config import settings

print(settings.OCR_LANGUAGES)       # "rus+eng" (из config.json)
print(settings.MAX_FILE_SIZE)       # 20971520  (20 MB)
print(settings.ENABLE_JAVASCRIPT)   # False
```

---

## Переменные окружения (`.env`)

Ключевые переменные, влияющие на конфигурацию:

```env
FOUNDRY_BASE_URL=http://localhost:50477/v1
HF_TOKEN=hf_...
HF_MODELS_DIR=D:\models
LLAMA_MODEL_PATH=D:\models\model.gguf
LOG_LEVEL=INFO
API_KEY=
```

`.env` загружается через `python-dotenv` в `src/utils/env_processor.py` до инициализации `Config`.

---

## Обновление конфигурации в рантайме

```python
raw = config.get_raw_config()
raw["app"]["language"] = "ru"
config.update_config(raw)   # сохраняет в config.json и обновляет память
```

Endpoint `/api/v1/config` использует этот механизм для изменений через веб-интерфейс.

---

::: config_manager.Config
