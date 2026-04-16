# 🧠 Models API

---
**📚 Навигация:** [🏠 Главная](../README.md) | [📡 API](README.md) | [🤖 Генерация](generation.md) | [🧠 Модели](models.md) | [🔍 RAG](rag.md) | [📊 Мониторинг](monitoring.md)
---

## GET `/api/v1/models`

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

## GET `/api/v1/models/connected`

**Response:**
```json
{
  "success": true,
  "models": [
    {
      "model_id": "deepseek-chat",
      "provider": "foundry",
      "status": "online",
      "usage_count": 42,
      "avg_response_time": 1.23
    }
  ],
  "total_count": 1,
  "online_count": 1
}
```

## POST `/api/v1/models/connect`

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

## GET `/api/v1/models/providers`

**Response:**
```json
{
  "success": true,
  "providers": [
    {
      "provider_id": "foundry",
      "name": "Foundry AI",
      "requires_api_key": false,
      "supported_features": ["text_generation", "chat"]
    }
  ]
}
```

---
**[⬆️ Назад к документации по API](README.md)**