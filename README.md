# 🤖 AI Assistant

![Coverage](docs/ru/assets/coverage.svg)

**Оркестратор локальных AI моделей с богатым REST API**

`ai_assist` — универсальный оркестратор для локальных AI моделей.
Единая точка доступа к Microsoft Foundry Local, HuggingFace Transformers, llama.cpp и Ollama
через стандартизированный REST API с интегрированной RAG-системой, веб-интерфейсом и MCP-серверами.

## ✨ Возможности

- 🎛️ **Оркестрация моделей** — единый API для Foundry, HuggingFace, llama.cpp, Ollama
- 🤖 **Генерация текста** через локальные AI модели (DeepSeek, Qwen, Mistral, Llama, Gemma)
- 💬 **Интерактивный чат** с поддержкой истории сессии и потоковой передачи (SSE)
- ⚙️ **Управление Foundry** — запуск, остановка и мониторинг через веб-интерфейс
- 🤗 **HuggingFace** — работа с моделями и inference Hub
- 🦙 **llama.cpp** — запуск GGUF моделей на CPU/GPU
- 🐋 **Ollama** — интеграция с локальным Ollama-сервисом
- 🔍 **RAG система** — векторный поиск по документации (FAISS + SentenceTransformers)
- 📄 **Извлечение текста** из 40+ форматов (PDF, DOCX, XLSX, изображения OCR, HTML, архивы)
- 📦 **Пакетная обработка** множественных запросов
- 🔐 **Безопасность** через API ключи и CORS защиту
- 📊 **Мониторинг** здоровья сервиса и моделей
- 🐳 **Docker** поддержка
- 🌐 **Веб-интерфейс** (SPA) для управления всеми компонентами
- 🔌 **MCP серверы** для STDIO (PowerShell), HTTP и других протоколов
- 🌍 **i18n** — интерфейс на русском, английском, иврите

## 🏗️ Архитектура оркестратора

```
Browser / API Client / MCP Client
              │ HTTP / SSE / WebSocket
              ▼
    AI Assistant (ai_assist)
       FastAPI — port 9696
              │
   ┌──────────┼──────────────┬──────────────┐
   ▼          ▼              ▼              ▼
Foundry   HuggingFace   llama.cpp       Ollama
Local     Transformers  (GGUF / CPU)    (local)
(ONNX)    (PyTorch)
              │
         ┌────┴────┐
         ▼         ▼
       FAISS     Text
       (RAG)   Extractor
              (40+ formats)
```

### Маршрутизация моделей

Оркестратор выбирает бэкенд по префиксу в поле `model`:

| Префикс | Бэкенд |
|---|---|
| `foundry::model-id` | Microsoft Foundry Local |
| `hf::model-id` | HuggingFace Transformers |
| `llama::path/to/model.gguf` | llama.cpp |
| `ollama::model-name` | Ollama |

Все бэкенды возвращают одинаковый формат ответа.
Без префикса — ошибка (устаревшие bare ID пробрасываются в Foundry с предупреждением).

## 🚀 Быстрый старт

```powershell
# Первый запуск — установит зависимости автоматически
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

После запуска интерфейс доступен по адресу: **http://localhost:9696**

### Что происходит при запуске

`start.ps1` последовательно:

1. Проверяет `venv\` → если нет, запускает `install.ps1`
2. Загружает переменные из `.env`
3. Ищет запущенный Foundry → если не найден, запускает `foundry service start`
4. Опционально запускает MkDocs (`docs_server.enabled` в `config.json`)
5. Опционально запускает llama.cpp (если задан `llama_cpp.model_path`)
6. Запускает `venv\Scripts\python.exe run.py`

Подробный workflow: [Быстрый старт](docs/ru/user/getting_started.md)

### Запуск через Python (если Foundry уже запущен)

```powershell
venv\Scripts\python.exe run.py
```

### Docker

```powershell
docker-compose up
```

## 📁 Структура проекта

```
ai_assist/  (FastApiFoundry-Docker)
├── src/                    # Исходный код Python
│   ├── api/               # FastAPI: app.py, endpoints/
│   ├── models/            # AI клиенты: foundry, hf, llama, ollama
│   ├── rag/               # RAG система (FAISS + text extractor)
│   ├── agents/            # AI агенты
│   ├── converter/         # GGUF → ONNX конвертер
│   └── utils/             # Утилиты (translator, logging, etc.)
├── static/                # Веб-интерфейс (SPA)
├── docs/                  # MkDocs документация
├── extensions/            # Браузерные расширения
├── mcp-powershell-servers/ # MCP серверы (PowerShell STDIO)
├── scripts/               # Операционные скрипты
├── install/               # Скрипты установки
├── check_engine/          # Диагностика и тесты
├── sdk/                   # Python SDK (fastapi_foundry, microsoft_foundry)
├── bin/                   # Нативные бинарники (llama.cpp, Windows x64)
├── rag_index/             # FAISS индекс
├── logs/                  # Логи
├── start.ps1              # Точка входа (Windows)
├── run.py                 # Python точка входа
├── install.ps1            # Установщик
├── config.json            # Конфигурация
├── .env                   # Переменные окружения (секреты)
├── docker-compose.yml     # Docker
└── requirements.txt       # Python зависимости
```

## 🌐 Универсальный доступ: любой клиент, любая сеть

AI Assistant — обычный HTTP-сервер с REST API. К нему подключается любая программа, умеющая делать HTTP-запросы:

| Клиент | Как подключается |
|---|---|
| Браузер | Встроенный веб-интерфейс на `http://localhost:9696` |
| Python / PowerShell скрипт | `requests.post("http://localhost:9696/api/v1/generate", ...)` |
| Go / Java / C++ / Rust / любой язык | Стандартный HTTP-клиент — `net/http`, `HttpClient`, `libcurl` |
| Telegram бот | Встроенный HelpDesk бот или свой через API |
| Браузерное расширение | Встроенное расширение-суммарайзер |
| Claude Desktop | Через MCP сервер (STDIO) |
| Любой другой MCP-клиент | Через MCP STDIO или HTTP протокол |
| Docker-контейнер | `http://host.docker.internal:9696/api/v1/generate` |

Сервер не привязан к языку или платформе клиента — если есть HTTP, есть доступ.

## 🔧 Технологии

| Компонент | Технология |
|---|---|
| Web framework | FastAPI + Uvicorn |
| AI: Foundry | Microsoft Foundry Local CLI (ONNX) |
| AI: HuggingFace | transformers + huggingface_hub (PyTorch) |
| AI: GGUF | llama.cpp (CPU/GPU) |
| AI: Ollama | Ollama HTTP API |
| RAG | FAISS + sentence-transformers |
| OCR | Tesseract + pytesseract + Pillow |
| PDF | pdfplumber + PyPDF2 |
| Office документы | python-docx + python-pptx + openpyxl |
| HTML/XML | BeautifulSoup4 + lxml |
| Контейнеризация | Docker |
| Язык | Python 3.11+ |

## ⚙️ Конфигурация

### Файлы настроек

| Файл | Назначение |
|---|---|
| `config.json` | Публичные настройки (порты, модели, RAG) |
| `.env` | Секреты (токены, ключи, пути) |
| `docker-compose.yml` | Docker настройки |

### Настройка .env

```powershell
Copy-Item .env.example .env
notepad .env
```

Ключевые переменные:

```env
# Foundry (если не определяется автоматически)
FOUNDRY_BASE_URL=http://localhost:50477/v1

# HuggingFace (для закрытых моделей: Gemma, Llama)
HF_TOKEN=hf_ваш_токен
HF_MODELS_DIR=D:\models

# llama.cpp (опционально)
LLAMA_MODEL_PATH=D:\models\qwen2.5-0.5b-q4_k_m.gguf
```

### Автозагрузка модели при старте

```json
{
  "foundry_ai": {
    "auto_load_default": true,
    "default_model": "qwen3-0.6b-generic-cpu:4"
  }
}
```

## 🗂️ Скачивание GGUF моделей

```powershell
pip install huggingface_hub
hf auth login
hf download bartowski/gemma-7b-it-GGUF --include "*Q4_K_M.gguf" --local-dir D:\models
```

| Квантование | Размер | Рекомендация |
|---|---|---|
| Q4_K_M | ~4–5 GB | Лучший баланс — по умолчанию |
| Q5_K_M | ~5–6 GB | Лучше качество при достаточной RAM |
| Q8_0 | ~8–9 GB | Максимальное качество |

## 🔍 Диагностика

```powershell
venv\Scripts\python.exe check_env.py
venv\Scripts\python.exe diagnose.py
venv\Scripts\python.exe check_engine\smoke_all_endpoints.py
```

## 📚 Документация

**Онлайн документация:** **https://davidka.net/ai_assist/site/**

| Раздел | Описание |
|---|---|
| [Быстрый старт](docs/ru/user/getting_started.md) | Запуск и startup workflow |
| [Установка](docs/ru/user/installation.md) | install.ps1, зависимости |
| [Работа с моделями](docs/ru/user/models_guide.md) | Foundry, HuggingFace, llama.cpp, Ollama |
| [Веб-интерфейс](docs/ru/user/web_interface.md) | Описание всех вкладок |
| [Архитектура](docs/ru/dev/architecture.md) | Структура кода, паттерны |
| [API Reference](docs/ru/dev/api_reference.md) | Все REST endpoints |
| [RAG система](docs/ru/dev/rag_system.md) | FAISS, индексация, поиск |
| [Агенты](docs/ru/dev/agents.md) | Создание AI агентов |
| [CI/CD](docs/ru/dev/cicd_docs.md) | GitHub Actions, MkDocs |

## 📞 Поддержка

- **Swagger UI**: http://localhost:9696/docs
- **Health Check**: http://localhost:9696/api/v1/health
- **GitHub**: https://github.com/hypo69/FastApiFoundry-Docker

## 📄 Лицензия

MIT License — https://opensource.org/licenses/MIT

---

**AI Assistant (ai_assist) v0.7.0** | Python 3.11+ | Windows
