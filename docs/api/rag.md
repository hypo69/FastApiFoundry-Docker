# 🔍 RAG API

## POST `/api/v1/rag/search`

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

## POST `/api/v1/rag/reload`

Перезагрузка RAG индекса

**Response:**
```json
{
  "success": true,
  "message": "RAG index reloaded",
  "chunks_loaded": 1234,
  "reload_time": 5.67
}
```

## GET `/api/v1/rag/status`

**Response:**
```json
{
  "success": true,
  "loaded": true,
  "chunks_count": 1234,
  "index_size_mb": 45.6,
  "last_updated": "2025-01-09T10:00:00Z"
}
```