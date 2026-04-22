# CLI Reference

Справочник по командам командной строки для всех компонентов FastAPI Foundry.

---

## Foundry Local CLI

Foundry Local управляется через команду `foundry`.

### Сервис

```powershell
# Запустить сервис
foundry service start

# Остановить сервис
foundry service stop

# Статус сервиса (показывает URL и порт)
foundry service status
```

Пример вывода `foundry service status`:
```
🟢 Model management service is running on http://127.0.0.1:52632/openai/status
```

!!! tip "Порт динамический"
    Foundry каждый раз может запускаться на другом порту.
    Укажите URL явно в Settings → Foundry URL, чтобы FastAPI Foundry всегда его находил.

### Модели

```powershell
# Список доступных моделей в каталоге
foundry model ls

# Скачать модель в кэш
foundry model download qwen2.5-0.5b-instruct-generic-cpu:4

# Загрузить модель в сервис (inference)
foundry model load qwen2.5-0.5b-instruct-generic-cpu:4

# Выгрузить модель из сервиса
foundry model unload qwen2.5-0.5b-instruct-generic-cpu:4

# Запустить интерактивный чат с моделью
foundry run qwen2.5-0.5b-instruct-generic-cpu:4
```

### Рекомендуемые модели

| Модель | Размер | Тип | Описание |
|---|---|---|---|
| `qwen2.5-0.5b-instruct-generic-cpu:4` | 0.8 GB | CPU | Самая лёгкая |
| `qwen2.5-1.5b-instruct-generic-cpu:4` | 1.78 GB | CPU | Средняя |
| `deepseek-r1-distill-qwen-7b-generic-cpu:3` | 6.43 GB | CPU | С рассуждениями |
| `deepseek-r1-distill-qwen-14b-generic-cpu:4` | ~9 GB | CPU | Продвинутая |
| `phi-3-mini-4k-instruct-openvino-gpu:1` | 2.4 GB | GPU | GPU inference |

---

## llama.cpp

llama.cpp запускается через `llama-server.exe` (бинарники в `bin/`).

### Запуск сервера

```powershell
# Базовый запуск
.\bin\llama-b8802-bin-win-cpu-x64\llama-server.exe `
  --model D:\models\gemma-2-2b-it-Q6_K.gguf `
  --port 9780 `
  --host 127.0.0.1

# С параметрами контекста и потоков
.\bin\llama-b8802-bin-win-cpu-x64\llama-server.exe `
  --model D:\models\model.gguf `
  --port 9780 `
  --ctx-size 4096 `
  --threads 8 `
  --n-gpu-layers 0

# С GPU (если есть CUDA/Vulkan)
.\bin\llama-b8802-bin-win-cpu-x64\llama-server.exe `
  --model D:\models\model.gguf `
  --n-gpu-layers 35
```

### Ключевые параметры

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--model` | — | Путь к `.gguf` файлу (обязательно) |
| `--port` | 8080 | Порт HTTP сервера |
| `--host` | 127.0.0.1 | Хост |
| `--ctx-size` | 512 | Размер контекста в токенах |
| `--threads` | auto | Потоков CPU |
| `--n-gpu-layers` | 0 | Слоёв на GPU (0 = только CPU) |
| `--log-disable` | — | Отключить вывод логов |

### Проверка работы

```powershell
# Статус сервера
curl http://localhost:9780/health

# Список загруженных моделей
curl http://localhost:9780/v1/models
```

### Скачивание GGUF моделей

```powershell
# Установить HuggingFace CLI
pip install huggingface_hub

# Авторизация (нужна для Gemma, Llama)
hf auth login

# Скачать модель (рекомендуется Q4_K_M — лучший баланс)
hf download bartowski/gemma-2-2b-it-GGUF `
  --include "*Q6_K.gguf" `
  --local-dir D:\models

hf download bartowski/Qwen2.5-0.5B-Instruct-GGUF `
  --include "*Q4_K_M.gguf" `
  --local-dir D:\models
```

| Квантование | Размер | Рекомендация |
|---|---|---|
| Q4_K_M | ~4–5 GB | Лучший баланс — по умолчанию |
| Q5_K_M | ~5–6 GB | Лучше качество |
| Q6_K | ~6–7 GB | Высокое качество |
| Q8_0 | ~8–9 GB | Максимальное качество |

---

## HuggingFace CLI

```powershell
# Установка
pip install huggingface_hub

# Авторизация
hf auth login
# или
huggingface-cli login

# Скачать модель целиком
hf download microsoft/Phi-3-mini-4k-instruct `
  --local-dir D:\models\phi3

# Скачать только определённые файлы
hf download bartowski/gemma-2-2b-it-GGUF `
  --include "*Q4_K_M.gguf" `
  --local-dir D:\models

# Список скачанных моделей
huggingface-cli scan-cache

# Удалить модель из кэша
huggingface-cli delete-cache
```

### Переменные окружения

```env
# Токен для закрытых моделей (Gemma, Llama)
HF_TOKEN=hf_ваш_токен

# Директория для моделей
HF_MODELS_DIR=D:\models

# Отключить предупреждения
TRANSFORMERS_VERBOSITY=error
```

---

## FastAPI Foundry — диагностика

```powershell
# Проверить конфигурацию
venv\Scripts\python.exe check_env.py

# Полная диагностика системы
venv\Scripts\python.exe diagnose.py

# Запустить все smoke-тесты
venv\Scripts\python.exe check_engine\smoke_all_endpoints.py

# Проверить здоровье API
curl http://localhost:9696/api/v1/health

# Список загруженных моделей
curl http://localhost:9696/api/v1/foundry/models/loaded

# Статус Foundry сервиса
curl http://localhost:9696/api/v1/foundry/status

# Статус llama.cpp
curl http://localhost:9696/api/v1/llama/status
```

---

## RAG — индексация через API

RAG не имеет отдельного CLI — управляется через REST API или веб-интерфейс.

```powershell
# Статус RAG системы
curl http://localhost:9696/api/v1/rag/status

# Индексировать текст
curl -X POST http://localhost:9696/api/v1/rag/index `
  -H "Content-Type: application/json" `
  -d '{"text": "Текст для индексации", "source": "manual"}'

# Поиск по индексу
curl -X POST http://localhost:9696/api/v1/rag/search `
  -H "Content-Type: application/json" `
  -d '{"query": "поисковый запрос", "top_k": 5}'

# Очистить индекс
curl -X POST http://localhost:9696/api/v1/rag/clear
```

Полный справочник RAG endpoints: [API Reference](../dev/api_reference.md)
