# tests/ — Тесты FastAPI Foundry

Директория содержит скрипты для ручного и автоматического тестирования
компонентов FastAPI Foundry.

**Требование:** сервер должен быть запущен (`python run.py`) перед запуском
большинства тестов, так как они обращаются к живому API на `localhost:9696`.

---

## Запуск

```powershell
# Запуск конкретного теста
venv\Scripts\python.exe tests\test_server.py

# Запуск всех тестов системы
venv\Scripts\python.exe tests\test_system.py
```

---

## Файлы

### test_server.py
Быстрая проверка доступности сервера и основных endpoints.
Тестирует: `/`, `/api`, `/api/v1/health`, `/api/v1/models`, `/docs`.
Не требует запущенного Foundry — только сам FastAPI сервер.

```powershell
venv\Scripts\python.exe tests\test_server.py
```

### test_system.py
Комплексное тестирование всех компонентов системы через `aiohttp`.
Тестирует: health, Foundry connection, models endpoint, RAG search, chat, chat+RAG.
Сохраняет результаты в `test_results.json`.
Требует: запущенный сервер + Foundry + загруженная модель.

```powershell
venv\Scripts\python.exe tests\test_system.py
```

### test_foundry_models.py
Прямая проверка подключения к Foundry API через `foundry_client`.
Тестирует: health check, список моделей.
Не требует запущенного FastAPI — обращается к Foundry напрямую.

```powershell
venv\Scripts\python.exe tests\test_foundry_models.py
```

### test_rag.py
Тестирование RAG системы: инициализация, поиск по запросам.
Если индекс не найден — создаёт минимальный тестовый индекс из 4 документов.
Требует: установленные RAG зависимости (`python install_rag_deps.py`).

```powershell
venv\Scripts\python.exe tests\test_rag.py
```

### test_config.py
Проверка загрузки конфигурации из `config.json`.
Показывает все секции конфигурации и тестирует `update_from_args`.
Не требует запущенного сервера.

```powershell
venv\Scripts\python.exe tests\test_config.py
```

### test_config_editor.py
Тестирование API редактора конфигурации через HTTP.
Тестирует: GET `/api/v1/config`, POST `/api/v1/config`, проверку сохранения.
Требует: запущенный сервер.

```powershell
venv\Scripts\python.exe tests\test_config_editor.py
```

### test_default_model.py
Тестирование сохранения модели по умолчанию через API.
Тестирует: получение конфига, смену модели, проверку сохранения, восстановление.
Требует: запущенный сервер + Foundry с загруженными моделями.

```powershell
venv\Scripts\python.exe tests\test_default_model.py
```

### test_chat_implementation.py
Тестирование реализации чата через `enhanced_foundry_client`.
Тестирует: список моделей, создание сессии чата.
Требует: запущенный Foundry.

```powershell
venv\Scripts\python.exe tests\test_chat_implementation.py
```

### test_simplified.py
Тестирование упрощённых моделей ответов (`api/models.py`) без Pydantic.
Тестирует: `create_generate_response`, `create_health_response`, `create_error_response`.
Не требует запущенного сервера.

```powershell
venv\Scripts\python.exe tests\test_simplified.py
```

### test_port.ps1
PowerShell скрипт для поиска порта Foundry через `Inference.Service.Agent*` процесс.
Устанавливает `FOUNDRY_BASE_URL` в переменную окружения текущей сессии.
Использовался для отладки определения динамического порта Foundry.

```powershell
.\tests\test_port.ps1
```

---

## Зависимости тестов

| Тест | Сервер | Foundry | RAG deps |
|------|--------|---------|----------|
| test_server.py | ✅ | — | — |
| test_system.py | ✅ | ✅ | ✅ |
| test_foundry_models.py | — | ✅ | — |
| test_rag.py | — | — | ✅ |
| test_config.py | — | — | — |
| test_config_editor.py | ✅ | — | — |
| test_default_model.py | ✅ | ✅ | — |
| test_chat_implementation.py | — | ✅ | — |
| test_simplified.py | — | — | — |
| test_port.ps1 | — | ✅ | — |
