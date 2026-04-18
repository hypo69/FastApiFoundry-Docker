# 🚀 FastAPI Foundry

**REST API для локальных AI моделей с поддержкой RAG**

FastAPI Foundry — современный REST API сервер для работы с локальными AI моделями
через Microsoft Foundry Local, HuggingFace Transformers и llama.cpp,
с интегрированной системой поиска и извлечения контекста (RAG).

## ✨ Возможности

- 🤖 **Генерация текста** через локальные AI модели (DeepSeek, Qwen, Mistral, Llama)
- 💬 **Интерактивный чат** с поддержкой истории сессии
- 🤗 **HuggingFace** — скачивание и inference моделей с Hub
- 🦙 **llama.cpp** — запуск GGUF моделей на CPU/GPU
- 🔍 **RAG система** — векторный поиск по документации (FAISS)
- 📦 **Пакетная обработка** множественных запросов
- 🔐 **Безопасность** через API ключи и CORS защиту
- 📊 **Мониторинг** здоровья сервиса и моделей
- 🐳 **Docker** поддержка
- 🌐 **Веб-интерфейс** для управления моделями и чата
- 🔌 **MCP сервер** для интеграции с Claude Desktop
- ⚙️ **Управление Foundry** — запуск, остановка и мониторинг через веб-интерфейс

## 🏗️ Архитектура

```
Browser / API Client
        │ HTTP
        ▼
FastAPI (port 9696)
        │
   ┌────┴────┬──────────────┬──────────┐
   ▼         ▼              ▼          ▼
Foundry   HuggingFace   llama.cpp   Ollama
Local     Transformers  (GGUF)
(ONNX)    (PyTorch)
```

## 🚀 Быстрый старт

```powershell
# Первый запуск — установит зависимости автоматически
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

После запуска: **http://localhost:9696**

### Что происходит при запуске

`start.ps1` последовательно:

1. Проверяет `venv\` → если нет, запускает `install.ps1`
2. Загружает переменные из `.env`
3. Ищет запущенный Foundry → если не найден, запускает `foundry service start`
4. Опционально запускает MkDocs (`docs_server.enabled` в `config.json`)
5. Опционально запускает llama.cpp (`LLAMA_AUTO_START=true` в `.env`)
6. Запускает `venv\Scripts\python.exe run.py`

Подробный workflow: [Быстрый старт](docs/ru/user/getting_started.md)

### Прямой запуск (если Foundry уже запущен)

```powershell
venv\Scripts\python.exe run.py
```

### Docker

```powershell
docker-compose up
```

## 📁 Структура проекта

```
FastApiFoundry-Docker/
├── src/                    # Исходный код Python
│   ├── api/               # FastAPI: app.py, endpoints/
│   ├── models/            # AI клиенты: foundry, hf, llama
│   ├── rag/               # RAG система (FAISS)
│   ├── agents/            # AI агенты
│   ├── converter/         # GGUF → ONNX конвертер
│   ├── translator/        # Модуль перевода
│   └── utils/             # Утилиты
├── static/                # Веб-интерфейс (SPA)
├── docs/                  # MkDocs документация
├── extensions/            # Браузерное расширение
├── mcp-powershell-servers/ # MCP серверы (PowerShell)
├── scripts/               # Операционные скрипты
├── install/               # Скрипты установки
├── check_engine/          # Диагностика и тесты
├── SANDBOX/               # SDK и эксперименты
├── utils/                 # Standalone утилиты
├── bin/                   # llama.cpp бинарники (Windows x64)
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

## 🔧 Технологии

| Компонент | Технология |
|---|---|
| Web framework | FastAPI + Uvicorn |
| AI: Foundry | Microsoft Foundry Local CLI |
| AI: HuggingFace | transformers + huggingface_hub |
| AI: GGUF | llama.cpp |
| RAG | FAISS + sentence-transformers |
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
# Скопировать пример
Copy-Item .env.example .env
# Отредактировать
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
LLAMA_AUTO_START=false
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

### Локальный сервер документации

```json
{
  "docs_server": {
    "enabled": true,
    "port": 9697
  }
}
```

## 🗂️ Скачивание GGUF моделей

```powershell
# Установить HuggingFace CLI
pip install huggingface_hub

# Авторизоваться (нужно для Gemma, Llama)
hf auth login

# Скачать квантованную модель (рекомендуется Q4_K_M)
hf download bartowski/gemma-7b-it-GGUF `
  --include "*Q4_K_M.gguf" `
  --local-dir D:\models
```

| Квантование | Размер | Рекомендация |
|---|---|---|
| Q4_K_M | ~4–5 GB | Лучший баланс — по умолчанию |
| Q5_K_M | ~5–6 GB | Лучше качество при достаточной RAM |
| Q8_0 | ~8–9 GB | Максимальное качество |

Проверенные кураторы: **bartowski**, **unsloth**, **TheBloke**

## 🔍 Диагностика

```powershell
# Проверить конфигурацию
venv\Scripts\python.exe check_env.py

# Диагностика системы
venv\Scripts\python.exe diagnose.py

# Запустить все тесты
venv\Scripts\python.exe check_engine\smoke_all_endpoints.py
```

## 📚 Документация

| Раздел | Описание |
|---|---|
| [Быстрый старт](docs/ru/user/getting_started.md) | Запуск и startup workflow |
| [Установка](docs/ru/user/installation.md) | install.ps1, зависимости |
| [Работа с моделями](docs/ru/user/models_guide.md) | Foundry, HuggingFace, llama.cpp |
| [Веб-интерфейс](docs/ru/user/web_interface.md) | Описание всех вкладок |
| [Архитектура](docs/ru/dev/architecture.md) | Структура кода, паттерны |
| [API Reference](docs/ru/dev/api_reference.md) | Все REST endpoints |
| [RAG система](docs/ru/dev/rag_system.md) | FAISS, индексация, поиск |
| [Агенты](docs/ru/dev/agents.md) | Создание AI агентов |
| [CI/CD](docs/ru/dev/cicd_docs.md) | GitHub Actions, MkDocs |

Онлайн документация: **https://hypo69.github.io/FastApiFoundry-Docker/**

## 📞 Поддержка

- **Swagger UI**: http://localhost:9696/docs
- **Health Check**: http://localhost:9696/api/v1/health
- **GitHub**: https://github.com/hypo69/FastApiFoundry-Docker

## 📄 Лицензия

CC BY-NC-SA 4.0 — https://creativecommons.org/licenses/by-nc-sa/4.0/

---

**FastAPI Foundry v0.6.0** | Python 3.11+ | Windows
