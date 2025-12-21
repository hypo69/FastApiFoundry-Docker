# 📡 FastAPI Foundry - API Reference

**Base URL:** `http://localhost:8000`  
**API Version:** v1  
**Content-Type:** `application/json`

---

## 🔍 Health & Status

### GET `/api/v1/health`
Проверка здоровья системы

**Response:**
```json
{
  "status": "healthy",
  "foundry_status": "healthy", 
  "rag_loaded": true,
  "rag_chunks": 1234,
  "timestamp": "2025-01-09T10:30:00Z"
}
```

---

## 🤖 Text Generation

### POST `/api/v1/generate`
Генерация текста с поддержкой RAG

**Request:**
```json
{
  "prompt": "Что такое FastAPI Foundry?",
  "model": "deepseek-chat",
  "temperature": 0.7,
  "max_tokens": 2048,
  "use_rag": true,
  "system_prompt": "Ты помощник разработчика"
}
```

**Response:**
```json
{
  "success": true,
  "content": "FastAPI Foundry - это REST API сервер...",
  "model": "deepseek-chat",
  "tokens_used": 150,
  "rag_context_used": true,
  "generation_time": 2.34
}
```

### POST `/api/v1/batch-generate`
Пакетная генерация текста

**Request:**
```json
{
  "prompts": ["Вопрос 1", "Вопрос 2"],
  "model": "deepseek-chat",
  "temperature": 0.7,
  "max_tokens": 1000,
  "use_rag": true
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "prompt": "Вопрос 1",
      "content": "Ответ 1...",
      "tokens_used": 75
    },
    {
      "prompt": "Вопрос 2", 
      "content": "Ответ 2...",
      "tokens_used": 82
    }
  ],
  "total_tokens": 157,
  "processing_time": 4.12
}
```

---

## 🧠 Models Management

### GET `/api/v1/models`
Список доступных моделей

**Response:**
```json
{
  "success": true,
  "models": [
    {
      "id": "deepseek-chat",
      "name": "DeepSeek Chat",
      "provider": "foundry",
      "status": "online"
    }
  ],
  "total_count": 1,
  "online_count": 1
}
```

### GET `/api/v1/models/connected`
Подключенные модели с детальной информацией

**Response:**
```json
{
  "success": true,
  "models": [
    {
      "model_id": "deepseek-chat",
      "model_name": "DeepSeek Chat",
      "provider": "foundry",
      "status": "online",
      "usage_count": 42,
      "avg_response_time": 1.23,
      "last_check": "2025-01-09T10:25:00Z"
    }
  ],
  "total_count": 1,
  "online_count": 1,
  "default_model": "deepseek-chat"
}
```

### POST `/api/v1/models/connect`
Подключить новую модель

**Request:**
```json
{
  "model_id": "llama-3.2-1b",
  "provider": "foundry",
  "model_name": "Llama 3.2 1B",
  "endpoint_url": "http://localhost:55581/v1/",
  "enabled": true
}
```

### GET `/api/v1/models/providers`
Список доступных провайдеров

**Response:**
```json
{
  "success": true,
  "providers": [
    {
      "provider_id": "foundry",
      "name": "Foundry AI",
      "description": "Локальный AI сервер Foundry",
      "requires_api_key": false,
      "supported_features": ["text_generation", "chat"]
    }
  ]
}
```

### POST `/api/v1/models/health-check`
Проверка здоровья всех моделей

---

## 🔍 RAG System

### POST `/api/v1/rag/search`
Поиск в RAG системе

**Request:**
```json
{
  "query": "как установить FastAPI Foundry",
  "top_k": 5
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "content": "Для установки FastAPI Foundry...",
      "source": "installation.md",
      "section": "Быстрый старт",
      "score": 0.95
    }
  ],
  "query": "как установить FastAPI Foundry",
  "total_results": 5,
  "search_time": 0.12
}
```

### POST `/api/v1/rag/reload`
Перезагрузка RAG индекса

### GET `/api/v1/rag/status`
Статус RAG системы

---

## ⚙️ Configuration

### GET `/api/v1/config`
Получить конфигурацию системы

**Response:**
```json
{
  "foundry": {
    "base_url": "http://localhost:55581/v1/",
    "default_model": "deepseek-chat",
    "timeout": 30
  },
  "rag": {
    "available": true,
    "loaded": true,
    "chunks_count": 1234,
    "index_path": "./rag_index"
  },
  "api": {
    "version": "1.0.0",
    "cors_enabled": true
  }
}
```

---

## 📊 Logging & Monitoring

### GET `/api/v1/logs/health`
Здоровье системы на основе логов

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "period": "1h",
    "metrics": {
      "errors_count": 0,
      "warnings_count": 2,
      "api_requests": 45,
      "avg_response_time": 1.23,
      "active_models": 1
    },
    "timestamp": "2025-01-09T10:30:00Z"
  }
}
```

### GET `/api/v1/logs/errors?hours=24`
Сводка ошибок за период

### GET `/api/v1/logs/performance?hours=24`
Метрики производительности

### GET `/api/v1/logs/recent?level=error&limit=50`
Последние записи логов

### GET `/api/v1/logs/stats`
Статистика файлов логов

### POST `/api/v1/logs/test`
Тестирование системы логирования

---

## 🎮 Examples

### POST `/api/v1/examples/run`
Запуск примера

**Request:**
```json
{
  "example_type": "client"
}
```

**Response:**
```json
{
  "success": true,
  "example_type": "client",
  "output": "🚀 FastAPI Foundry Client Demo\n...",
  "execution_time": 2.34,
  "return_code": 0
}
```

### GET `/api/v1/examples/list`
Список доступных примеров

---

## 🌐 Tunnel Management

### POST `/api/v1/tunnel/start?tunnel_type=ngrok&port=8000`
Запуск туннеля для публичного доступа

### POST `/api/v1/tunnel/stop`
Остановка туннеля

### GET `/api/v1/tunnel/status`
Статус туннеля

---

## 🔧 Foundry Integration

### GET `/api/v1/foundry/status`
Статус Foundry сервера

### GET `/api/v1/foundry/models`
Модели доступные в Foundry

### POST `/api/v1/foundry/service/start`
Запуск Foundry сервиса (если поддерживается)

### POST `/api/v1/foundry/service/stop`
Остановка Foundry сервиса

---

## 📝 Request/Response Format

### Standard Success Response
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-01-09T10:30:00Z"
}
```

### Standard Error Response
```json
{
  "success": false,
  "error": "Error description",
  "detail": "Detailed error message",
  "timestamp": "2025-01-09T10:30:00Z"
}
```

---

## 🔐 Authentication

По умолчанию API не требует аутентификации. Для включения:

```bash
# .env
API_KEY_ENABLED=true
API_KEY=your-secret-key
```

**Header:**
```
Authorization: Bearer your-secret-key
```

---

## 📊 Rate Limiting

- **Default:** 100 requests/minute per IP
- **Burst:** 10 requests/second

---

## 🌍 CORS

Настройка в `.env`:
```bash
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

---

## 📚 Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json