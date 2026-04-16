# 📖 API Reference - FastAPI Foundry

## 🌐 Базовая информация

- **Base URL**: `http://localhost:9696/api/v1`
- **Content-Type**: `application/json`
- **Swagger UI**: http://localhost:9696/docs

## 🏥 Health Check

### GET /api/v1/health
Проверка работоспособности сервиса

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-09T12:00:00Z",
  "foundry_status": "connected",
  "foundry_url": "http://localhost:50477/v1/",
  "version": "1.0.0"
}
```

**cURL:**
```bash
curl -X GET "http://localhost:9696/api/v1/health"
```

## 🤖 Models Management

### GET /api/v1/models
Получить список доступных моделей

**Response:**
```json
{
  "models": [
    {
      "id": "qwen2.5-0.5b-instruct-generic-cpu:4",
      "name": "Qwen 2.5 0.5B Instruct",
      "status": "loaded",
      "size": "0.5B parameters"
    }
  ],
  "total": 1
}
```

**cURL:**
```bash
curl -X GET "http://localhost:9696/api/v1/models"
```

### POST /api/v1/models/load
Загрузить модель в память

**Request:**
```json
{
  "model_id": "qwen2.5-0.5b-instruct-generic-cpu:4"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Model loaded successfully",
  "model_id": "qwen2.5-0.5b-instruct-generic-cpu:4"
}
```

**cURL:**
```bash
curl -X POST "http://localhost:9696/api/v1/models/load" \
  -H "Content-Type: application/json" \
  -d '{"model_id": "qwen2.5-0.5b-instruct-generic-cpu:4"}'
```

### POST /api/v1/models/unload
Выгрузить модель из памяти

**Request:**
```json
{
  "model_id": "qwen2.5-0.5b-instruct-generic-cpu:4"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Model unloaded successfully"
}
```

## 🎯 Text Generation

### POST /api/v1/generate
Генерация текста

**Request:**
```json
{
  "prompt": "Напиши короткое стихотворение о зиме",
  "model": "qwen2.5-0.5b-instruct-generic-cpu:4",
  "max_tokens": 100,
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40,
  "stop": ["\n\n"]
}
```

**Response:**
```json
{
  "text": "Зима пришла с морозами,\nСнег укрыл поля...",
  "model": "qwen2.5-0.5b-instruct-generic-cpu:4",
  "tokens_used": 45,
  "generation_time": 2.3
}
```

**cURL:**
```bash
curl -X POST "http://localhost:9696/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Привет, как дела?",
    "model": "qwen2.5-0.5b-instruct-generic-cpu:4",
    "max_tokens": 50
  }'
```

### POST /api/v1/generate/batch
Пакетная генерация текста

**Request:**
```json
{
  "requests": [
    {
      "prompt": "Первый запрос",
      "max_tokens": 50
    },
    {
      "prompt": "Второй запрос",
      "max_tokens": 100
    }
  ],
  "model": "qwen2.5-0.5b-instruct-generic-cpu:4"
}
```

**Response:**
```json
{
  "results": [
    {
      "text": "Ответ на первый запрос...",
      "tokens_used": 25
    },
    {
      "text": "Ответ на второй запрос...",
      "tokens_used": 67
    }
  ],
  "total_requests": 2,
  "total_time": 4.5
}
```

## 💬 Chat Interface

### POST /api/v1/chat
Чат с AI моделью

**Request:**
```json
{
  "message": "Привет! Как дела?",
  "model": "qwen2.5-0.5b-instruct-generic-cpu:4",
  "session_id": "user123",
  "temperature": 0.7,
  "max_tokens": 200
}
```

**Response:**
```json
{
  "response": "Привет! У меня всё хорошо, спасибо! Как дела у тебя?",
  "model": "qwen2.5-0.5b-instruct-generic-cpu:4",
  "session_id": "user123",
  "tokens_used": 15,
  "generation_time": 1.2
}
```

**cURL:**
```bash
curl -X POST "http://localhost:9696/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Привет!",
    "model": "qwen2.5-0.5b-instruct-generic-cpu:4"
  }'
```

### GET /api/v1/chat/history/{session_id}
Получить историю чата

**Response:**
```json
{
  "session_id": "user123",
  "messages": [
    {
      "role": "user",
      "content": "Привет!",
      "timestamp": "2025-01-09T12:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Привет! Как дела?",
      "timestamp": "2025-01-09T12:00:01Z"
    }
  ],
  "total_messages": 2
}
```

### DELETE /api/v1/chat/history/{session_id}
Очистить историю чата

**Response:**
```json
{
  "status": "success",
  "message": "Chat history cleared",
  "session_id": "user123"
}
```

## 🔍 RAG System

### POST /api/v1/rag/search
Поиск в документации

**Request:**
```json
{
  "query": "как запустить FastAPI Foundry",
  "top_k": 3
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "Для запуска FastAPI Foundry используйте команду...",
      "score": 0.95,
      "source": "docs/getting-started.md"
    }
  ],
  "total_results": 1,
  "query": "как запустить FastAPI Foundry"
}
```

### POST /api/v1/rag/generate
Генерация с контекстом из RAG

**Request:**
```json
{
  "query": "Как настроить автозагрузку модели?",
  "model": "qwen2.5-0.5b-instruct-generic-cpu:4",
  "use_rag": true,
  "top_k": 3
}
```

**Response:**
```json
{
  "answer": "Для настройки автозагрузки модели установите в config.json...",
  "sources": [
    {
      "content": "Контекст из документации...",
      "source": "docs/configuration.md"
    }
  ],
  "model": "qwen2.5-0.5b-instruct-generic-cpu:4"
}
```

## ⚙️ Foundry Management

### GET /api/v1/foundry/status
Статус Foundry сервиса

**Response:**
```json
{
  "status": "running",
  "url": "http://localhost:50477/v1/",
  "port": 50477,
  "version": "1.0.0",
  "uptime": "2h 30m",
  "models_loaded": 1
}
```

### POST /api/v1/foundry/start
Запуск Foundry сервиса

**Response:**
```json
{
  "status": "success",
  "message": "Foundry service started",
  "port": 50477
}
```

### POST /api/v1/foundry/stop
Остановка Foundry сервиса

**Response:**
```json
{
  "status": "success",
  "message": "Foundry service stopped"
}
```

## 📊 Configuration

### GET /api/v1/config
Получить текущую конфигурацию

**Response:**
```json
{
  "fastapi_server": {
    "port": 9696,
    "host": "0.0.0.0"
  },
  "foundry_ai": {
    "base_url": "http://localhost:50477/v1/",
    "default_model": "qwen2.5-0.5b-instruct-generic-cpu:4"
  }
}
```

### POST /api/v1/config
Обновить конфигурацию

**Request:**
```json
{
  "foundry_ai": {
    "temperature": 0.8,
    "max_tokens": 1024
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Configuration updated",
  "updated_fields": ["foundry_ai.temperature", "foundry_ai.max_tokens"]
}
```

## 📋 Logging

### GET /logs/api
Получить логи API

**Query Parameters:**
- `level` - Уровень логов (INFO, ERROR, DEBUG)
- `limit` - Количество записей (по умолчанию 100)
- `format` - Формат (json, text)

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2025-01-09T12:00:00Z",
      "level": "INFO",
      "message": "Request processed successfully",
      "module": "fastapi-foundry"
    }
  ],
  "total": 1,
  "level": "INFO"
}
```

## 🔧 Examples

### GET /examples/client
Пример клиента

**Response:**
```json
{
  "example": "client_demo",
  "code": "import requests...",
  "description": "Пример использования API клиента"
}
```

## ❌ Error Responses

### Стандартный формат ошибок
```json
{
  "error": "Model not found",
  "detail": "Model 'invalid-model' is not available",
  "status_code": 404,
  "timestamp": "2025-01-09T12:00:00Z"
}
```

### Коды ошибок
- `400` - Bad Request (неверные параметры)
- `404` - Not Found (ресурс не найден)
- `422` - Validation Error (ошибка валидации)
- `500` - Internal Server Error (внутренняя ошибка)
- `503` - Service Unavailable (Foundry недоступен)

## 📊 Rate Limiting

По умолчанию ограничений нет, но можно настроить в config.json:

```json
{
  "security": {
    "rate_limit": {
      "requests_per_minute": 60,
      "burst_size": 10
    }
  }
}
```

---

**Следующий шаг**: [Конфигурация](configuration.md)