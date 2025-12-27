# 🏗️ Foundry Architecture Documentation

**Версия:** 0.2.1  
**Проект:** FastApiFoundry (Docker)  
**Дата:** 9 декабря 2025  

---

## 🎯 Что такое наш подход к Foundry

Наш проект использует **Microsoft Foundry Local CLI** как сервис для запуска AI моделей локально, а не как Python библиотеку.

### 🔄 Архитектура системы

```
┌─────────────────┐    HTTP REST API    ┌──────────────────┐    CLI Commands    ┌─────────────────┐
│   FastAPI       │ ──────────────────► │  Foundry Local   │ ─────────────────► │   AI Models     │
│   (Port 8000)   │                     │  (Port 50477)    │                    │   (ONNX/Local)  │
│                 │                     │                  │                    │                 │
│ • Web Interface │                     │ • Model Manager  │                    │ • DeepSeek R1   │
│ • REST API      │                     │ • HTTP Server    │                    │ • Phi-3 Mini    │
│ • RAG System    │                     │ • Auto Port      │                    │ • Llama 3.2     │
└─────────────────┘                     └──────────────────┘                    └─────────────────┘
```

---

## 📚 Используемые библиотеки

### ✅ Что мы используем

```python
# HTTP клиенты для REST API
import aiohttp      # Асинхронные HTTP запросы к Foundry
import requests     # Синхронные HTTP запросы (fallback)

# Системные утилиты
import socket       # Автопоиск портов Foundry (50400-50800)
import psutil       # Мониторинг процессов
import subprocess   # Запуск Foundry CLI команд
```

### ❌ Что мы НЕ используем

```python
# Microsoft Azure AI SDK (не нужен для локального Foundry)
# import azure.ai.ml
# from azure.identity import DefaultAzureCredential

# ONNX Runtime (Foundry управляет моделями сам)
# import onnxruntime as ort
# from optimum.onnxruntime import ORTModelForCausalLM

# Прямая работа с моделями (делегируем Foundry)
# import transformers
# import torch
```

---

## 🔧 Как работает интеграция

### 1. Запуск Foundry сервиса

```bash
# Foundry CLI запускает HTTP сервер
foundry service start
# → Сервер доступен на http://localhost:50477/v1/
```

### 2. Автопоиск порта

```python
def get_foundry_port(self):
    """Автоматически находит порт Foundry"""
    for port in range(50400, 50800):
        try:
            response = requests.get(f'http://127.0.0.1:{port}/v1/models', timeout=1)
            if response.status_code == 200:
                return port  # Найден активный Foundry
        except:
            continue
    return 50477  # Порт по умолчанию
```

### 3. HTTP API взаимодействие

```python
# Список моделей
async def list_available_models(self):
    url = f"{self.base_url}/models"
    async with session.get(url) as response:
        data = await response.json()
        return data.get('data', [])

# Генерация текста (OpenAI-совместимый формат)
async def generate_text(self, prompt: str, **kwargs):
    url = f"{self.base_url}/chat/completions"
    payload = {
        "model": kwargs.get('model', "deepseek-r1:14b"),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": kwargs.get('temperature', 0.7),
        "max_tokens": kwargs.get('max_tokens', 2048)
    }
    async with session.post(url, json=payload) as response:
        return await response.json()
```

---

## 🆚 Сравнение подходов

### Microsoft Foundry Local (официальный)

```python
# 1. Экспорт модели в ONNX
optimum-cli export onnx --model microsoft/phi-2 phi2_onnx

# 2. Загрузка через ONNX Runtime
import onnxruntime as ort
session = ort.InferenceSession('phi2_onnx/model.onnx')

# 3. Инференс
inputs = {'input_ids': np.array([[1, 2, 3]])}
outputs = session.run(None, inputs)

# 4. Azure AI SDK интеграция
from azure.ai.ml import MLClient
client = MLClient(...)
```

### Наш подход (FastAPI Foundry)

```bash
# 1. Запуск модели через CLI
foundry model run phi-3-mini-4k

# 2. HTTP запрос
curl http://localhost:50477/v1/chat/completions \
  -d '{"model": "phi-3-mini-4k", "messages": [{"role": "user", "content": "Hello"}]}'

# 3. Python интеграция
import aiohttp
async with session.post(url, json=payload) as response:
    result = await response.json()
```

---

## 🎯 Преимущества нашего подхода

| Аспект | Наш подход | Microsoft Foundry Local |
|--------|------------|-------------------------|
| **Простота** | ✅ HTTP API | ❌ ONNX экспорт + SDK |
| **Скорость** | ✅ Foundry CLI управляет всем | ❌ Ручной экспорт моделей |
| **Совместимость** | ✅ OpenAI API формат | ❌ Azure-специфичный |
| **Автоматизация** | ✅ Автопоиск портов | ❌ Ручная настройка |
| **Зависимости** | ✅ Минимальные (aiohttp) | ❌ Много (azure-ai-ml, onnx) |
| **Развертывание** | ✅ Docker ready | ❌ Сложная настройка |

---

## 🔌 API Endpoints

Foundry предоставляет OpenAI-совместимый REST API:

### Модели
```http
GET /v1/models
# Список доступных моделей
```

### Генерация текста
```http
POST /v1/chat/completions
Content-Type: application/json

{
  "model": "deepseek-r1:14b",
  "messages": [{"role": "user", "content": "Hello"}],
  "temperature": 0.7,
  "max_tokens": 2048
}
```

### Простая генерация
```http
POST /v1/completions
Content-Type: application/json

{
  "model": "deepseek-r1:14b",
  "prompt": "Hello",
  "max_tokens": 100
}
```

---

## 🚀 Управление моделями

### Через Foundry CLI

```bash
# Список доступных моделей
foundry model list

# Запуск модели
foundry model run deepseek-r1:14b

# Остановка модели
foundry model stop deepseek-r1:14b

# Статус сервиса
foundry service status

# Остановка сервиса
foundry service stop
```

### Через наш FastAPI

```bash
# Список подключенных моделей
curl http://localhost:8000/api/v1/models

# Проверка здоровья Foundry
curl http://localhost:8000/api/v1/health

# Генерация текста
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello", "model": "deepseek-r1:14b"}'
```

---

## 🔧 Конфигурация

### Переменные окружения

```env
# Foundry настройки
FOUNDRY_BASE_URL=http://localhost:50477/v1/
FOUNDRY_DEFAULT_MODEL=deepseek-r1:14b
FOUNDRY_TEMPERATURE=0.7
FOUNDRY_MAX_TOKENS=2048

# FastAPI настройки
API_HOST=0.0.0.0
API_PORT=8000
```

### Автоматическое определение

```python
# Foundry клиент автоматически:
# 1. Ищет FOUNDRY_BASE_URL в переменных окружения
# 2. Сканирует порты 50400-50800
# 3. Проверяет доступность через /v1/models
# 4. Обновляет base_url с найденным портом
```

---

## 🐳 Docker интеграция

```dockerfile
# Foundry устанавливается в контейнер
RUN curl -L https://foundry.paradigm.xyz | bash
ENV PATH="/root/.foundry/bin:${PATH}"

# FastAPI подключается к Foundry через HTTP
EXPOSE 8000
CMD ["python", "run.py"]
```

---

## 📊 Мониторинг

### Health Check

```python
async def health_check(self):
    """Проверка состояния Foundry"""
    try:
        url = f"{self.base_url}/models"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "status": "healthy",
                    "models_count": len(data.get('data', [])),
                    "port": self.get_foundry_port()
                }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e)
        }
```

### Автоматический перезапуск

```python
# При недоступности Foundry:
# 1. Логируем ошибку
# 2. Пытаемся найти новый порт
# 3. Обновляем base_url
# 4. Повторяем запрос
```

---

## 🎉 Заключение

Наш подход к Foundry:
- **Проще** в использовании
- **Быстрее** в развертывании  
- **Совместимее** с существующими инструментами
- **Автоматизированнее** в настройке

Мы используем Foundry как **сервис**, а не как **библиотеку**, что делает архитектуру более гибкой и масштабируемой.