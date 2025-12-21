# 🤖 Text Generation API

## POST `/api/v1/generate`

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

## POST `/api/v1/batch-generate`

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
    }
  ],
  "total_tokens": 157,
  "processing_time": 4.12
}
```