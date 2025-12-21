# 📚 Примеры использования

Практические примеры работы с FastAPI Foundry для различных сценариев использования.

## 🚀 Быстрый старт

### Запуск сервера
```bash
# Простой запуск
python run.py

# С автопоиском портов и HTTPS
python run.py --dev --ssl --auto-port

# Production режим
python run.py --prod --ssl
```

### Первая проверка
```bash
# Проверка здоровья системы
curl http://localhost:8000/api/v1/health

# Список доступных моделей
curl http://localhost:8000/api/v1/models
```

## 🤖 Генерация текста

### Простая генерация
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Объясни что такое FastAPI",
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

### Генерация с RAG контекстом
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Как настроить FastAPI Foundry?",
    "use_rag": true,
    "temperature": 0.6,
    "max_tokens": 1000
  }'
```

### Генерация с конкретной моделью
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Напиши код на Python для работы с API",
    "model": "deepseek-r1-distill-qwen-7b-generic-cpu:3",
    "temperature": 0.3,
    "max_tokens": 800
  }'
```

## 📦 Пакетная обработка

### Обработка нескольких промптов
```bash
curl -X POST http://localhost:8000/api/v1/batch-generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": [
      "Что такое Python?",
      "Что такое Docker?", 
      "Что такое Kubernetes?"
    ],
    "temperature": 0.6,
    "max_tokens": 200,
    "use_rag": true
  }'
```

### Генерация документации
```bash
curl -X POST http://localhost:8000/api/v1/batch-generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": [
      "Создай README для Python проекта",
      "Напиши docstring для функции обработки данных",
      "Создай пример использования API"
    ],
    "temperature": 0.4,
    "max_tokens": 500
  }'
```

## 🔍 RAG система

### Поиск в документации
```bash
curl -X POST http://localhost:8000/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "настройка конфигурации",
    "top_k": 5
  }'
```

### Поиск технической информации
```bash
curl -X POST http://localhost:8000/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "API endpoints FastAPI",
    "top_k": 10
  }'
```

### Перезагрузка RAG индекса
```bash
curl -X POST http://localhost:8000/api/v1/rag/reload \
  -H "Authorization: Bearer your-api-key"
```

## 🔧 Управление моделями

### Подключение OpenAI модели
```bash
curl -X POST http://localhost:8000/api/v1/models/connect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model_id": "gpt-3.5-turbo",
    "provider": "openai",
    "model_name": "GPT-3.5 Turbo",
    "endpoint_url": "https://api.openai.com/v1/",
    "api_key": "your-openai-key"
  }'
```

### Подключение Ollama модели
```bash
curl -X POST http://localhost:8000/api/v1/models/connect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model_id": "llama2:7b",
    "provider": "ollama", 
    "model_name": "Llama 2 7B",
    "endpoint_url": "http://localhost:11434/api/"
  }'
```

### Тестирование модели
```bash
curl -X POST http://localhost:8000/api/v1/models/gpt-3.5-turbo/test \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "test_prompt": "Привет, как дела?"
  }'
```

### Список подключенных моделей
```bash
curl http://localhost:8000/api/v1/models/connected \
  -H "Authorization: Bearer your-api-key"
```

## 🏗️ Foundry управление

### Запуск Foundry сервиса
```bash
curl -X POST http://localhost:8000/api/v1/foundry/service/start \
  -H "Authorization: Bearer your-api-key"
```

### Проверка статуса Foundry
```bash
curl http://localhost:8000/api/v1/foundry/status
```

### Список Foundry моделей
```bash
curl http://localhost:8000/api/v1/foundry/models/list \
  -H "Authorization: Bearer your-api-key"
```

### Скачивание модели
```bash
curl -X POST http://localhost:8000/api/v1/foundry/models/download \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model_name": "deepseek-r1-distill-qwen-7b-generic-cpu:3"
  }'
```

## 🐍 Python клиент

### Базовый клиент
```python
import requests
import json

class FastAPIFoundryClient:
    def __init__(self, base_url="http://localhost:8000", api_key=None):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def generate(self, prompt, **kwargs):
        data = {"prompt": prompt, **kwargs}
        response = requests.post(
            f"{self.base_url}/api/v1/generate",
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def batch_generate(self, prompts, **kwargs):
        data = {"prompts": prompts, **kwargs}
        response = requests.post(
            f"{self.base_url}/api/v1/batch-generate", 
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def rag_search(self, query, top_k=5):
        data = {"query": query, "top_k": top_k}
        response = requests.post(
            f"{self.base_url}/api/v1/rag/search",
            headers=self.headers,
            json=data
        )
        return response.json()

# Использование
client = FastAPIFoundryClient()

# Простая генерация
result = client.generate("Объясни машинное обучение")
print(result["content"])

# Генерация с RAG
result = client.generate(
    "Как настроить FastAPI?", 
    use_rag=True, 
    temperature=0.7
)
print(result["content"])

# Пакетная обработка
results = client.batch_generate([
    "Что такое REST API?",
    "Что такое GraphQL?",
    "Что такое WebSocket?"
])

for i, result in enumerate(results["results"]):
    print(f"Ответ {i+1}: {result['content']}")
```

### Асинхронный клиент
```python
import aiohttp
import asyncio

class AsyncFoundryClient:
    def __init__(self, base_url="http://localhost:8000", api_key=None):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    async def generate(self, prompt, **kwargs):
        data = {"prompt": prompt, **kwargs}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/v1/generate",
                headers=self.headers,
                json=data
            ) as response:
                return await response.json()
    
    async def batch_generate_concurrent(self, prompts, **kwargs):
        """Параллельная обработка промптов"""
        tasks = []
        for prompt in prompts:
            task = self.generate(prompt, **kwargs)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results

# Использование
async def main():
    client = AsyncFoundryClient()
    
    # Параллельная генерация
    prompts = [
        "Объясни Python",
        "Объясни JavaScript", 
        "Объясни Go"
    ]
    
    results = await client.batch_generate_concurrent(prompts)
    
    for i, result in enumerate(results):
        print(f"Язык {i+1}: {result['content'][:100]}...")

# Запуск
asyncio.run(main())
```

## 🌐 JavaScript клиент

### Веб-приложение
```html
<!DOCTYPE html>
<html>
<head>
    <title>FastAPI Foundry Client</title>
</head>
<body>
    <div id="app">
        <textarea id="prompt" placeholder="Введите ваш промпт..."></textarea>
        <button onclick="generate()">Генерировать</button>
        <div id="result"></div>
    </div>

    <script>
        const API_BASE = 'http://localhost:8000/api/v1';
        
        async function generate() {
            const prompt = document.getElementById('prompt').value;
            const resultDiv = document.getElementById('result');
            
            if (!prompt) {
                alert('Введите промпт');
                return;
            }
            
            resultDiv.innerHTML = 'Генерация...';
            
            try {
                const response = await fetch(`${API_BASE}/generate`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        prompt: prompt,
                        temperature: 0.7,
                        max_tokens: 500,
                        use_rag: true
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `
                        <h3>Результат:</h3>
                        <p>${data.content}</p>
                        <small>Модель: ${data.model} | Токены: ${data.tokens_used}</small>
                    `;
                } else {
                    resultDiv.innerHTML = `<p style="color: red;">Ошибка: ${data.error}</p>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<p style="color: red;">Ошибка сети: ${error.message}</p>`;
            }
        }
        
        // RAG поиск
        async function ragSearch(query) {
            const response = await fetch(`${API_BASE}/rag/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    top_k: 5
                })
            });
            
            const data = await response.json();
            return data.results;
        }
    </script>
</body>
</html>
```

### Node.js клиент
```javascript
const axios = require('axios');

class FoundryClient {
    constructor(baseURL = 'http://localhost:8000', apiKey = null) {
        this.client = axios.create({
            baseURL: baseURL + '/api/v1',
            headers: {
                'Content-Type': 'application/json',
                ...(apiKey && { 'Authorization': `Bearer ${apiKey}` })
            }
        });
    }
    
    async generate(prompt, options = {}) {
        try {
            const response = await this.client.post('/generate', {
                prompt,
                ...options
            });
            return response.data;
        } catch (error) {
            throw new Error(`Generation failed: ${error.response?.data?.error || error.message}`);
        }
    }
    
    async batchGenerate(prompts, options = {}) {
        try {
            const response = await this.client.post('/batch-generate', {
                prompts,
                ...options
            });
            return response.data;
        } catch (error) {
            throw new Error(`Batch generation failed: ${error.response?.data?.error || error.message}`);
        }
    }
    
    async ragSearch(query, topK = 5) {
        try {
            const response = await this.client.post('/rag/search', {
                query,
                top_k: topK
            });
            return response.data;
        } catch (error) {
            throw new Error(`RAG search failed: ${error.response?.data?.error || error.message}`);
        }
    }
}

// Использование
async function example() {
    const client = new FoundryClient();
    
    try {
        // Простая генерация
        const result = await client.generate('Объясни Node.js', {
            temperature: 0.7,
            max_tokens: 300
        });
        
        console.log('Ответ:', result.content);
        
        // RAG поиск
        const searchResults = await client.ragSearch('FastAPI configuration');
        console.log('Найдено документов:', searchResults.results.length);
        
    } catch (error) {
        console.error('Ошибка:', error.message);
    }
}

example();
```

## 🔐 Работа с аутентификацией

### Настройка API ключа
```bash
# В .env файле
API_KEY=your-secret-api-key-here

# Использование в запросах
curl -H "Authorization: Bearer your-secret-api-key-here" \
  http://localhost:8000/api/v1/models/connected
```

### Python с аутентификацией
```python
import requests

# Настройка клиента с API ключом
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-secret-api-key-here"
}

# Защищенный запрос
response = requests.post(
    "http://localhost:8000/api/v1/generate",
    headers=headers,
    json={
        "prompt": "Создай безопасный API endpoint",
        "temperature": 0.5
    }
)

result = response.json()
print(result["content"])
```

## 🚀 Продвинутые сценарии

### Создание чат-бота
```python
class ChatBot:
    def __init__(self, foundry_client):
        self.client = foundry_client
        self.conversation_history = []
    
    def chat(self, user_message):
        # Добавляем сообщение пользователя в историю
        self.conversation_history.append(f"Пользователь: {user_message}")
        
        # Формируем контекст из истории
        context = "\n".join(self.conversation_history[-10:])  # Последние 10 сообщений
        
        prompt = f"""Контекст разговора:
{context}

Ответь на последнее сообщение пользователя как дружелюбный помощник."""
        
        result = self.client.generate(
            prompt,
            temperature=0.7,
            max_tokens=300,
            use_rag=True
        )
        
        if result["success"]:
            bot_response = result["content"]
            self.conversation_history.append(f"Бот: {bot_response}")
            return bot_response
        else:
            return "Извините, произошла ошибка."

# Использование
client = FastAPIFoundryClient()
bot = ChatBot(client)

print("Чат-бот запущен! Введите 'выход' для завершения.")
while True:
    user_input = input("Вы: ")
    if user_input.lower() == 'выход':
        break
    
    response = bot.chat(user_input)
    print(f"Бот: {response}")
```

### Анализ документов
```python
def analyze_document(client, document_text, analysis_type="summary"):
    """Анализ документа с помощью AI"""
    
    analysis_prompts = {
        "summary": "Создай краткое резюме следующего документа:",
        "keywords": "Извлеки ключевые слова и фразы из документа:",
        "sentiment": "Определи тональность и эмоциональную окраску документа:",
        "questions": "Создай список вопросов, на которые отвечает этот документ:"
    }
    
    prompt = f"{analysis_prompts.get(analysis_type, analysis_prompts['summary'])}\n\n{document_text}"
    
    result = client.generate(
        prompt,
        temperature=0.3,
        max_tokens=500
    )
    
    return result["content"] if result["success"] else None

# Использование
document = """
FastAPI Foundry - это REST API сервер для работы с локальными AI моделями.
Он поддерживает генерацию текста, RAG систему и управление моделями.
Сервер написан на Python с использованием FastAPI фреймворка.
"""

client = FastAPIFoundryClient()

# Различные виды анализа
summary = analyze_document(client, document, "summary")
keywords = analyze_document(client, document, "keywords") 
sentiment = analyze_document(client, document, "sentiment")

print("Резюме:", summary)
print("Ключевые слова:", keywords)
print("Тональность:", sentiment)
```

### Генерация кода
```python
def generate_code(client, description, language="python"):
    """Генерация кода по описанию"""
    
    prompt = f"""Создай {language} код для следующей задачи:
{description}

Требования:
- Код должен быть чистым и читаемым
- Добавь комментарии
- Включи обработку ошибок
- Добавь пример использования

Код:"""

    result = client.generate(
        prompt,
        temperature=0.2,  # Низкая температура для более точного кода
        max_tokens=1000
    )
    
    return result["content"] if result["success"] else None

# Использование
client = FastAPIFoundryClient()

# Генерация различного кода
api_code = generate_code(
    client, 
    "REST API endpoint для загрузки файлов с валидацией",
    "python"
)

js_code = generate_code(
    client,
    "Функция для асинхронной загрузки данных с сервера",
    "javascript"
)

print("Python код:")
print(api_code)
print("\nJavaScript код:")
print(js_code)
```

## 🌐 Публичный доступ через туннели

### Запуск с ngrok
```bash
# Простой запуск
python start_with_tunnel.py

# С кастомным поддоменом
python start_with_tunnel.py --tunnel ngrok --subdomain myapi

# На кастомном порту
python start_with_tunnel.py --port 8080
```

### Запуск с Cloudflare
```bash
# Cloudflare Tunnel
python start_with_tunnel.py --tunnel cloudflared --port 8000
```

### Запуск с LocalTunnel
```bash
# LocalTunnel
python start_with_tunnel.py --tunnel localtunnel --port 8000

# С поддоменом
python start_with_tunnel.py --tunnel localtunnel --subdomain myapp
```

### Только туннель (если FastAPI уже запущен)
```bash
# Запустить FastAPI отдельно
python run.py --dev &

# Затем запустить только туннель
python start_with_tunnel.py --tunnel-only --port 8000
```

### Установка туннельных сервисов

```bash
# ngrok
choco install ngrok
# или скачать с https://ngrok.com/download

# Cloudflare
winget install Cloudflare.cloudflared
# или скачать с GitHub

# LocalTunnel
npm install -g localtunnel

# Serveo (встроенный SSH)
# Ничего устанавливать не нужно
```

## 📊 Мониторинг и отладка

### Проверка состояния системы
```bash
# Полная диагностика
curl -s http://localhost:8000/api/v1/health | jq .

# Конфигурация системы
curl -s http://localhost:8000/api/v1/config | jq .

# Статус Foundry
curl -s http://localhost:8000/api/v1/foundry/status | jq .
```

### Логирование запросов
```python
import logging
import time

class LoggingFoundryClient(FastAPIFoundryClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        
    def generate(self, prompt, **kwargs):
        start_time = time.time()
        self.logger.info(f"Generating response for prompt: {prompt[:50]}...")
        
        try:
            result = super().generate(prompt, **kwargs)
            duration = time.time() - start_time
            
            if result.get("success"):
                self.logger.info(f"Generation successful in {duration:.2f}s, tokens: {result.get('tokens_used', 0)}")
            else:
                self.logger.error(f"Generation failed: {result.get('error')}")
                
            return result
            
        except Exception as e:
            self.logger.error(f"Generation error: {e}")
            raise

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Использование с логированием
client = LoggingFoundryClient()
result = client.generate("Объясни логирование в Python")
```

Эти примеры покрывают основные сценарии использования FastAPI Foundry от простых запросов до сложных интеграций.