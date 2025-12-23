# 📡 Документация по API

Полная документация по REST API FastAPI Foundry.

---
**📚 Навигация:** [🏠 Главная](../README.md) | [📦 Установка](../installation.md) | [🚀 Запуск](../running.md) | [📖 Использование](../usage.md)
---

## 📋 Разделы API

| Раздел | Описание |
| :--- | :--- |
| **Основные** | |
| 🤖 [Генерация текста](generation.md) | `POST /generate`, `POST /batch-generate` |
| 🧠 [Управление моделями](models.md) | `GET /models`, `POST /models/connect` и др. |
| 🔍 [Система RAG](rag.md) | `POST /rag/search`, `POST /rag/reload` и др. |
| **Система и Мониторинг** | |
| 📊 [Мониторинг и Логи](monitoring.md) | `GET /logs/health`, `GET /logs/errors` и др. |
| ⚙️ [Конфигурация](configuration.md) | `GET /config` |
| 🩺 [Статус здоровья](../api.md#health--status) | `GET /health` |
| **Интеграции и Утилиты** | |
| 🎮 [Примеры](examples.md) | `GET /examples/list`, `POST /examples/run` |
| 🌐 [Управление туннелями](tunnel.md) | `GET /tunnel/status`, `POST /tunnel/start` |
| 🔧 [Интеграция с Foundry](foundry.md) | `GET /foundry/status`, `POST /foundry/service/start` |


## 🚀 Быстрый старт

### 1. Проверка здоровья
```bash
curl http://localhost:8000/api/v1/health
```

### 2. Генерация текста
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Привет!", "use_rag": true}'
```

### 3. Поиск в RAG
```bash
curl -X POST http://localhost:8000/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query": "установка", "top_k": 3}'
```

## 📚 Интерактивная документация

Для изучения API в интерактивном режиме используйте один из следующих эндпоинтов, доступных после запуска сервера:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

## 🔧 Python Клиент

Пример использования API через Python находится в `examples/example_client.py`.

```python
from examples.example_client import FastAPIFoundryClient

async with FastAPIFoundryClient() as client:
    # Генерация текста
    result = await client.generate_text("Привет!")
    
    # RAG поиск
    search = await client.rag_search("установка")
    
    # Список моделей
    models = await client.list_models()
```
Подробнее см. в **[документации по примерам](../examples.md)**.

## 📊 Статус коды

| Код | Описание |
| :-- | :--- |
| 200 | `OK` - Запрос успешно выполнен. |
| 400 | `Bad Request` - Некорректный запрос (например, отсутствуют обязательные поля). |
| 401 | `Unauthorized` - Ошибка аутентификации (неверный API ключ). |
| 404 | `Not Found` - Запрашиваемый ресурс не найден. |
| 500 | `Internal Server Error` - Внутренняя ошибка сервера. |
| 503 | `Service Unavailable` - Сервис временно недоступен. |

## 🔐 Аутентификация

Если в файле `.env` включен API ключ, его необходимо передавать в заголовке `Authorization`.

```env
# .env
API_KEY_ENABLED=true
API_KEY=your-secret-key
```

Пример запроса с ключом:
```bash
curl -H "Authorization: Bearer your-secret-key" \
  http://localhost:8000/api/v1/health
```

---
**[⬆️ Назад к главной документации](../README.md)**