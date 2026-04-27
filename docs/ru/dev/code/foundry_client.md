# Foundry Client

Асинхронный HTTP клиент для работы с Foundry Local API.

## Как Foundry работает с памятью

**Важно:** `.foundry/cache/models` — это **дисковый кэш**, а не preload в RAM.

| Что происходит | Когда |
|---|---|
| Модель скачивается на диск | `foundry model download <id>` |
| Модель загружается в память | `foundry model load <id>` или первый inference-запрос |
| Модель выгружается из памяти | `foundry model unload <id>` или рестарт сервиса |

При старте Foundry **ничего автоматически в RAM не загружается**.
Модель занимает RAM только после явной загрузки.

### Статусы модели в интерфейсе

- **Cached** — модель скачана на диск (`.foundry/cache/models`), RAM не занимает
- **Loaded** — модель загружена в Foundry сервис и готова к inference

### Управление памятью (model_manager в config.json)

```json
"model_manager": {
  "max_loaded_models": 1,
  "ttl_seconds": 600,
  "max_ram_percent": 80.0
}
```

- `max_loaded_models` — максимум одновременно загруженных моделей (LRU eviction)
- `ttl_seconds` — выгрузить модель если не использовалась N секунд
- `max_ram_percent` — порог RAM (%), при превышении выгружать LRU-модель

### Ошибка `model_not_loaded`

Если при генерации Foundry возвращает HTTP 400, клиент возвращает:

```json
{
  "success": false,
  "error_code": "model_not_loaded",
  "model_id": "qwen3-0.6b-generic-cpu:4:4",
  "error": "Модель не загружена. Загрузите её через вкладку Foundry → Downloaded Models → Load & Use."
}
```

Это **не ошибка клиента** — нужно явно загрузить модель перед использованием.

## API Reference

::: src.models.foundry_client.FoundryClient
