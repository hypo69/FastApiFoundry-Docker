# ⚙️ Configuration API

---
**📚 Навигация:** [🏠 Главная](../README.md) | [📡 API](../api.md) | [🤖 Генерация](generation.md) | [🧠 Модели](models.md) | [🔍 RAG](rag.md) | [📊 Мониторинг](monitoring.md)

---

## GET `/api/v1/config`

Возвращает текущую конфигурацию системы, включая настройки сервера, RAG и подключенных сервисов.

**Параметры:** Нет

**Ответ (`200 OK`):**
```json
{
  "success": true,
  "data": {
    "fastapi_server": {
      "host": "0.0.0.0",
      "port": 8000,
      "mode": "dev",
      "workers": 1,
      "reload": true,
      "ssl": false
    },
    "foundry_ai": {
      "base_url": "http://localhost:55581/v1/",
      "default_model": "deepseek-chat",
      "temperature": 0.6,
      "top_p": 0.9,
      "top_k": 40,
      "max_tokens": 2048,
      "timeout": 30
    },
    "rag_system": {
      "available": true,
      "loaded": true,
      "chunks_count": 1234,
      "index_path": "./rag_index",
      "model": "sentence-transformers/all-MiniLM-L6-v2"
    },
    "api_settings": {
      "version": "1.0.0",
      "cors_enabled": true,
      "api_key_enabled": false
    }
  },
  "timestamp": "2025-12-23T12:00:00Z"
}
```

### Поля ответа:
- `fastapi_server`: Настройки веб-сервера FastAPI.
- `foundry_ai`: Параметры для подключения и генерации через Foundry.
- `rag_system`: Статус и конфигурация RAG-системы.
- `api_settings`: Общие настройки API.

---
**[⬆️ Назад к документации по API](../api/README.md)**
