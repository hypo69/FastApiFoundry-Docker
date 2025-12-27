# 🛠️ FastAPI Foundry SDK

Python SDK для работы с FastAPI Foundry API.

## 📦 Установка

```bash
# Скопируйте папку sdk в ваш проект
cp -r SANDBOX/sdk /path/to/your/project/

# Или добавьте в PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/FastApiFoundry-Docker/SANDBOX"
```

## 🚀 Быстрый старт

```python
from sdk import FoundryClient

# Создание клиента
with FoundryClient(base_url="http://localhost:9696") as client:
    
    # Проверка здоровья
    health = client.health()
    print(f"Status: {health.status}")
    
    # Генерация текста
    response = client.generate(
        prompt="Привет, как дела?",
        use_rag=True,
        max_tokens=100
    )
    
    if response.success:
        print(f"Response: {response.content}")
    else:
        print(f"Error: {response.error}")
```

## 📚 Основные функции

### 🔍 Проверка здоровья системы

```python
health = client.health()
print(f"API Status: {health.status}")
print(f"Foundry Status: {health.foundry_status}")
print(f"RAG Chunks: {health.rag_chunks}")
```

### 🤖 Генерация текста

```python
# Простая генерация
response = client.generate("Расскажи о FastAPI")

# С параметрами
response = client.generate(
    prompt="Как установить Docker?",
    model="deepseek-r1-distill-qwen-7b-generic-cpu:3",
    temperature=0.7,
    max_tokens=500,
    use_rag=True,
    system_prompt="Ты - эксперт по DevOps"
)
```

### 📦 Пакетная генерация

```python
prompts = [
    "Что такое FastAPI?",
    "Как работает Docker?",
    "Объясни RAG систему"
]

responses = client.batch_generate(prompts, use_rag=True)
for response in responses:
    print(response.content)
```

### 🔍 RAG поиск

```python
results = client.rag_search("Docker configuration", top_k=5)
for result in results:
    print(f"Source: {result['source']}")
    print(f"Score: {result['score']}")
    print(f"Text: {result['text'][:100]}...")
```

### 📋 Список моделей

```python
models = client.list_models()
for model in models:
    print(f"ID: {model.id}")
    print(f"Provider: {model.provider}")
    print(f"Status: {model.status}")
```

### ⚙️ Конфигурация

```python
config = client.get_config()
foundry_config = config.get("foundry_ai", {})
print(f"Foundry URL: {foundry_config.get('base_url')}")
```

## 🔧 Обработка ошибок

```python
from sdk import FoundryClient, FoundryError, FoundryConnectionError

try:
    with FoundryClient() as client:
        response = client.generate("Test prompt")
        
except FoundryConnectionError:
    print("Не удалось подключиться к API")
except FoundryError as e:
    print(f"SDK Error: {e}")
```

## 📝 Модели данных

### GenerationRequest
- `prompt`: Входной промпт
- `model`: ID модели (опционально)
- `temperature`: Температура генерации (0.0-2.0)
- `max_tokens`: Максимальное количество токенов
- `use_rag`: Использовать RAG контекст
- `system_prompt`: Системный промпт

### GenerationResponse
- `success`: Успешность генерации
- `content`: Сгенерированный текст
- `error`: Ошибка (если есть)
- `model_used`: Использованная модель
- `tokens_used`: Количество использованных токенов
- `rag_sources`: Источники RAG
- `generation_time`: Время генерации

### ModelInfo
- `id`: ID модели
- `name`: Название модели
- `provider`: Провайдер (foundry, ollama, etc.)
- `status`: Статус модели
- `max_tokens`: Максимальное количество токенов

### HealthStatus
- `status`: Статус API
- `foundry_status`: Статус Foundry
- `foundry_url`: URL Foundry
- `rag_loaded`: RAG загружен
- `rag_chunks`: Количество RAG чанков
- `models_count`: Количество моделей

## 🧪 Тестирование

```bash
# Запустить пример
cd SANDBOX/sdk
python example.py
```

## 📄 Лицензия

CC BY-NC-SA 4.0 - https://creativecommons.org/licenses/by-nc-sa/4.0/

---

**FastAPI Foundry SDK** - часть экосистемы AiStros  
© 2025 AiStros Team