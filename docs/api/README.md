# 📡 API Documentation

Полная документация по REST API FastAPI Foundry.

## 📋 Разделы API

### 🔍 [Health & Status](../api.md#health--status)
- `GET /api/v1/health` - Проверка здоровья системы

### 🤖 [Text Generation](generation.md)
- `POST /api/v1/generate` - Генерация текста
- `POST /api/v1/batch-generate` - Пакетная генерация

### 🧠 [Models Management](models.md)
- `GET /api/v1/models` - Список моделей
- `GET /api/v1/models/connected` - Подключенные модели
- `POST /api/v1/models/connect` - Подключить модель
- `GET /api/v1/models/providers` - Провайдеры

### 🔍 [RAG System](rag.md)
- `POST /api/v1/rag/search` - Поиск в RAG
- `POST /api/v1/rag/reload` - Перезагрузка индекса
- `GET /api/v1/rag/status` - Статус RAG

### 📊 [Monitoring & Logs](monitoring.md)
- `GET /api/v1/logs/health` - Здоровье системы
- `GET /api/v1/logs/errors` - Сводка ошибок
- `GET /api/v1/logs/performance` - Метрики производительности
- `GET /api/v1/logs/recent` - Последние логи

### 🎮 Examples
- `POST /api/v1/examples/run` - Запуск примера
- `GET /api/v1/examples/list` - Список примеров

### 🌐 Tunnel Management
- `POST /api/v1/tunnel/start` - Запуск туннеля
- `POST /api/v1/tunnel/stop` - Остановка туннеля
- `GET /api/v1/tunnel/status` - Статус туннеля

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

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## 🔧 Python Client

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

## 📊 Статус коды

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

## 🔐 Аутентификация

По умолчанию отключена. Для включения:

```bash
# .env
API_KEY_ENABLED=true
API_KEY=your-secret-key
```

```bash
curl -H "Authorization: Bearer your-secret-key" \
  http://localhost:8000/api/v1/health
```