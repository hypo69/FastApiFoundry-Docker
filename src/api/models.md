# Model Management API

## Загрузка модели Foundry

Загрузка указанной модели в активный сервис инференса (Foundry Local, llama.cpp или HuggingFace). 

**Обоснование:** Использование POST запроса позволяет передать сложные настройки сэмплинга (temperature, penalty и др.) в теле JSON.

**Endpoint:** `POST /v1/models/load`

**Пример вызова через curl:**

```bash
curl -X POST http://localhost:9696/v1/models/load \
     -H "Content-Type: application/json" \
     -H "X-API-Key: YOUR_API_KEY" \
     -d '{
       "model_id": "llama::models/gemma-7b.gguf",
       "settings": {
         "temperature": 0.7,
         "max_tokens": 2048,
         "top_p": 0.9
       }
     }'
```

## Выгрузка модели

Освобождение оперативной и видеопамяти путем завершения текущего сеанса инференса и выгрузки весов модели.

**Обоснование:** Критически важно для систем с ограниченными ресурсами перед переключением на тяжелые RAG задачи.

**Endpoint:** `POST /v1/models/unload`

**Пример вызова через curl:**

```bash
curl -X POST http://localhost:9696/v1/models/unload \
     -H "X-API-Key: YOUR_API_KEY"
```