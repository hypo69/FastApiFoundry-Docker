# 📊 Примеры использования FastAPI Foundry

## 🚀 Быстрые примеры

### 1. Простая генерация текста

```bash
curl -X POST "http://localhost:9696/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Напиши короткое стихотворение о зиме",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

**Ответ:**
```json
{
  "text": "Зима пришла с морозами,\nСнег укрыл поля белым покрывалом...",
  "model": "qwen2.5-0.5b-instruct-generic-cpu:4",
  "tokens_used": 45,
  "generation_time": 2.3
}
```

### 2. Чат с AI

```bash
curl -X POST "http://localhost:9696/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Привет! Как дела?",
    "session_id": "user123"
  }'
```

**Ответ:**
```json
{
  "response": "Привет! У меня всё хорошо, спасибо! Как дела у тебя?",
  "session_id": "user123",
  "tokens_used": 15
}
```

### 3. Проверка здоровья

```bash
curl -X GET "http://localhost:9696/api/v1/health"
```

**Ответ:**
```json
{
  "status": "healthy",
  "foundry_status": "connected",
  "foundry_url": "http://localhost:50477/v1/",
  "timestamp": "2025-01-09T12:00:00Z"
}
```

## 🐍 Python примеры

### Простой клиент

```python
# examples/simple_client.py
import requests
import json

class FastAPIFoundryClient:
    def __init__(self, base_url="http://localhost:9696"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
    
    def generate_text(self, prompt, **kwargs):
        """Генерация текста"""
        response = requests.post(
            f"{self.api_url}/generate",
            json={
                "prompt": prompt,
                **kwargs
            }
        )
        return response.json()
    
    def chat(self, message, session_id=None, **kwargs):
        """Чат с AI"""
        data = {
            "message": message,
            **kwargs
        }
        if session_id:
            data["session_id"] = session_id
            
        response = requests.post(
            f"{self.api_url}/chat",
            json=data
        )
        return response.json()
    
    def get_models(self):
        """Получить список моделей"""
        response = requests.get(f"{self.api_url}/models")
        return response.json()
    
    def health_check(self):
        """Проверка здоровья"""
        response = requests.get(f"{self.api_url}/health")
        return response.json()

# Использование
if __name__ == "__main__":
    client = FastAPIFoundryClient()
    
    # Проверка здоровья
    health = client.health_check()
    print(f"Status: {health['status']}")
    
    # Генерация текста
    result = client.generate_text(
        "Расскажи интересный факт о космосе",
        max_tokens=150,
        temperature=0.8
    )
    print(f"Generated: {result['text']}")
    
    # Чат
    chat_response = client.chat(
        "Привет! Как дела?",
        session_id="demo_session"
    )
    print(f"AI: {chat_response['response']}")
```

### Асинхронный клиент

```python
# examples/async_client.py
import asyncio
import aiohttp
import json

class AsyncFoundryClient:
    def __init__(self, base_url="http://localhost:9696"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
    
    async def generate_text(self, prompt, **kwargs):
        """Асинхронная генерация текста"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/generate",
                json={"prompt": prompt, **kwargs}
            ) as response:
                return await response.json()
    
    async def batch_generate(self, prompts, **kwargs):
        """Пакетная генерация"""
        tasks = []
        for prompt in prompts:
            task = self.generate_text(prompt, **kwargs)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results

# Использование
async def main():
    client = AsyncFoundryClient()
    
    # Пакетная генерация
    prompts = [
        "Расскажи о Python",
        "Что такое FastAPI?",
        "Объясни машинное обучение"
    ]
    
    results = await client.batch_generate(
        prompts,
        max_tokens=100,
        temperature=0.7
    )
    
    for i, result in enumerate(results):
        print(f"Prompt {i+1}: {result['text'][:100]}...")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🌐 JavaScript примеры

### Веб-клиент

```javascript
// examples/web_client.js
class FoundryWebClient {
    constructor(baseUrl = 'http://localhost:9696') {
        this.baseUrl = baseUrl;
        this.apiUrl = `${baseUrl}/api/v1`;
    }
    
    async generateText(prompt, options = {}) {
        const response = await fetch(`${this.apiUrl}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: prompt,
                ...options
            })
        });
        
        return await response.json();
    }
    
    async chat(message, sessionId = null, options = {}) {
        const data = {
            message: message,
            ...options
        };
        
        if (sessionId) {
            data.session_id = sessionId;
        }
        
        const response = await fetch(`${this.apiUrl}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        return await response.json();
    }
    
    async getModels() {
        const response = await fetch(`${this.apiUrl}/models`);
        return await response.json();
    }
}

// Использование в браузере
const client = new FoundryWebClient();

// Генерация текста
client.generateText('Привет, мир!', {
    max_tokens: 50,
    temperature: 0.7
}).then(result => {
    console.log('Generated:', result.text);
});

// Чат
client.chat('Как дела?', 'web_session').then(response => {
    console.log('AI:', response.response);
});
```

### Node.js клиент

```javascript
// examples/node_client.js
const axios = require('axios');

class NodeFoundryClient {
    constructor(baseUrl = 'http://localhost:9696') {
        this.baseUrl = baseUrl;
        this.apiUrl = `${baseUrl}/api/v1`;
        this.client = axios.create({
            baseURL: this.apiUrl,
            timeout: 30000
        });
    }
    
    async generateText(prompt, options = {}) {
        try {
            const response = await this.client.post('/generate', {
                prompt: prompt,
                ...options
            });
            return response.data;
        } catch (error) {
            console.error('Generation error:', error.message);
            throw error;
        }
    }
    
    async streamChat(message, sessionId, onMessage) {
        // Пример стриминга (если поддерживается)
        const response = await this.client.post('/chat', {
            message: message,
            session_id: sessionId,
            stream: true
        }, {
            responseType: 'stream'
        });
        
        response.data.on('data', (chunk) => {
            const data = chunk.toString();
            onMessage(data);
        });
    }
}

// Использование
async function main() {
    const client = new NodeFoundryClient();
    
    try {
        // Простая генерация
        const result = await client.generateText(
            'Напиши функцию на Python для сортировки списка',
            { max_tokens: 200 }
        );
        console.log('Generated code:', result.text);
        
        // Чат с обработкой ошибок
        const chatResponse = await client.generateText(
            'Объясни этот код простыми словами'
        );
        console.log('Explanation:', chatResponse.text);
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}

main();
```

## 🔧 PowerShell примеры

### Простой PowerShell клиент

```powershell
# examples/powershell_client.ps1

function Invoke-FoundryGenerate {
    param(
        [string]$Prompt,
        [int]$MaxTokens = 100,
        [double]$Temperature = 0.7,
        [string]$BaseUrl = "http://localhost:9696"
    )
    
    $body = @{
        prompt = $Prompt
        max_tokens = $MaxTokens
        temperature = $Temperature
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/v1/generate" `
            -Method POST `
            -ContentType "application/json" `
            -Body $body
        
        return $response
    }
    catch {
        Write-Error "Generation failed: $($_.Exception.Message)"
        return $null
    }
}

function Invoke-FoundryChat {
    param(
        [string]$Message,
        [string]$SessionId = "powershell_session",
        [string]$BaseUrl = "http://localhost:9696"
    )
    
    $body = @{
        message = $Message
        session_id = $SessionId
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/v1/chat" `
            -Method POST `
            -ContentType "application/json" `
            -Body $body
        
        return $response
    }
    catch {
        Write-Error "Chat failed: $($_.Exception.Message)"
        return $null
    }
}

function Get-FoundryHealth {
    param([string]$BaseUrl = "http://localhost:9696")
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/v1/health" -Method GET
        return $response
    }
    catch {
        Write-Error "Health check failed: $($_.Exception.Message)"
        return $null
    }
}

# Использование
Write-Host "🚀 FastAPI Foundry PowerShell Client" -ForegroundColor Cyan

# Проверка здоровья
$health = Get-FoundryHealth
if ($health) {
    Write-Host "✅ Status: $($health.status)" -ForegroundColor Green
} else {
    Write-Host "❌ Service unavailable" -ForegroundColor Red
    exit 1
}

# Генерация текста
Write-Host "`n🎯 Generating text..." -ForegroundColor Yellow
$result = Invoke-FoundryGenerate -Prompt "Напиши функцию PowerShell для работы с файлами" -MaxTokens 200

if ($result) {
    Write-Host "Generated:" -ForegroundColor Green
    Write-Host $result.text -ForegroundColor White
}

# Чат
Write-Host "`n💬 Starting chat..." -ForegroundColor Yellow
$chatResponse = Invoke-FoundryChat -Message "Привет! Как дела?"

if ($chatResponse) {
    Write-Host "AI: $($chatResponse.response)" -ForegroundColor Cyan
}
```

## 🔍 RAG примеры

### Поиск в документации

```python
# examples/rag_client.py
import requests

class RAGClient:
    def __init__(self, base_url="http://localhost:9696"):
        self.api_url = f"{base_url}/api/v1"
    
    def search_docs(self, query, top_k=3):
        """Поиск в документации"""
        response = requests.post(
            f"{self.api_url}/rag/search",
            json={
                "query": query,
                "top_k": top_k
            }
        )
        return response.json()
    
    def generate_with_context(self, query, use_rag=True):
        """Генерация с контекстом из документации"""
        response = requests.post(
            f"{self.api_url}/rag/generate",
            json={
                "query": query,
                "use_rag": use_rag,
                "top_k": 3
            }
        )
        return response.json()

# Использование
client = RAGClient()

# Поиск в документации
search_results = client.search_docs("как запустить FastAPI Foundry")
print("Search results:")
for result in search_results['results']:
    print(f"- {result['source']}: {result['content'][:100]}...")

# Генерация с контекстом
answer = client.generate_with_context("Как настроить автозагрузку модели?")
print(f"\nAnswer: {answer['answer']}")
print(f"Sources: {[s['source'] for s in answer['sources']]}")
```

## 🎯 Специализированные примеры

### Пакетная обработка

```python
# examples/batch_processing.py
import requests
import concurrent.futures
import time

class BatchProcessor:
    def __init__(self, base_url="http://localhost:9696"):
        self.api_url = f"{base_url}/api/v1"
    
    def process_single(self, prompt):
        """Обработка одного запроса"""
        response = requests.post(
            f"{self.api_url}/generate",
            json={
                "prompt": prompt,
                "max_tokens": 100
            }
        )
        return response.json()
    
    def process_batch_sequential(self, prompts):
        """Последовательная обработка"""
        results = []
        start_time = time.time()
        
        for prompt in prompts:
            result = self.process_single(prompt)
            results.append(result)
        
        total_time = time.time() - start_time
        return results, total_time
    
    def process_batch_parallel(self, prompts, max_workers=5):
        """Параллельная обработка"""
        results = []
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_prompt = {
                executor.submit(self.process_single, prompt): prompt 
                for prompt in prompts
            }
            
            for future in concurrent.futures.as_completed(future_to_prompt):
                result = future.result()
                results.append(result)
        
        total_time = time.time() - start_time
        return results, total_time

# Использование
processor = BatchProcessor()

prompts = [
    "Расскажи о Python",
    "Что такое FastAPI?",
    "Объясни машинное обучение",
    "Как работает нейронная сеть?",
    "Что такое API?"
]

# Последовательная обработка
seq_results, seq_time = processor.process_batch_sequential(prompts)
print(f"Sequential processing: {seq_time:.2f} seconds")

# Параллельная обработка
par_results, par_time = processor.process_batch_parallel(prompts)
print(f"Parallel processing: {par_time:.2f} seconds")
print(f"Speedup: {seq_time/par_time:.2f}x")
```

### Мониторинг и метрики

```python
# examples/monitoring_client.py
import requests
import time
import json
from datetime import datetime

class MonitoringClient:
    def __init__(self, base_url="http://localhost:9696"):
        self.api_url = f"{base_url}/api/v1"
        self.metrics = []
    
    def measure_request(self, endpoint, method="GET", data=None):
        """Измерение времени запроса"""
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(f"{self.api_url}/{endpoint}")
        else:
            response = requests.post(f"{self.api_url}/{endpoint}", json=data)
        
        end_time = time.time()
        
        metric = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "response_time": end_time - start_time,
            "status_code": response.status_code,
            "success": response.status_code == 200
        }
        
        self.metrics.append(metric)
        return response.json() if response.status_code == 200 else None
    
    def run_health_monitoring(self, duration_minutes=5):
        """Мониторинг здоровья системы"""
        end_time = time.time() + (duration_minutes * 60)
        
        while time.time() < end_time:
            # Health check
            self.measure_request("health")
            
            # Models check
            self.measure_request("models")
            
            # Simple generation test
            self.measure_request("generate", "POST", {
                "prompt": "Test",
                "max_tokens": 10
            })
            
            time.sleep(30)  # Проверка каждые 30 секунд
    
    def get_statistics(self):
        """Получить статистику"""
        if not self.metrics:
            return {}
        
        response_times = [m["response_time"] for m in self.metrics]
        success_rate = sum(1 for m in self.metrics if m["success"]) / len(self.metrics)
        
        return {
            "total_requests": len(self.metrics),
            "success_rate": success_rate,
            "avg_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times)
        }
    
    def save_metrics(self, filename="metrics.json"):
        """Сохранить метрики в файл"""
        with open(filename, 'w') as f:
            json.dump({
                "metrics": self.metrics,
                "statistics": self.get_statistics()
            }, f, indent=2)

# Использование
monitor = MonitoringClient()

print("Starting monitoring...")
monitor.run_health_monitoring(duration_minutes=1)  # 1 минута для теста

stats = monitor.get_statistics()
print(f"Statistics:")
print(f"- Total requests: {stats['total_requests']}")
print(f"- Success rate: {stats['success_rate']:.2%}")
print(f"- Avg response time: {stats['avg_response_time']:.3f}s")

monitor.save_metrics("foundry_metrics.json")
print("Metrics saved to foundry_metrics.json")
```

## 🔧 Утилиты и инструменты

### Конфигурационный менеджер

```python
# examples/config_manager.py
import json
import requests
from pathlib import Path

class ConfigManager:
    def __init__(self, config_file="config.json", base_url="http://localhost:9696"):
        self.config_file = Path(config_file)
        self.api_url = f"{base_url}/api/v1"
    
    def load_local_config(self):
        """Загрузить локальную конфигурацию"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_local_config(self, config):
        """Сохранить локальную конфигурацию"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_remote_config(self):
        """Получить конфигурацию с сервера"""
        try:
            response = requests.get(f"{self.api_url}/config")
            return response.json()
        except:
            return None
    
    def update_remote_config(self, updates):
        """Обновить конфигурацию на сервере"""
        try:
            response = requests.post(
                f"{self.api_url}/config",
                json=updates
            )
            return response.json()
        except:
            return None
    
    def sync_configs(self):
        """Синхронизировать локальную и удаленную конфигурации"""
        local = self.load_local_config()
        remote = self.get_remote_config()
        
        if remote:
            # Обновить локальную конфигурацию
            self.save_local_config(remote)
            print("Local config updated from server")
        else:
            # Отправить локальную на сервер
            result = self.update_remote_config(local)
            if result:
                print("Server config updated from local")

# Использование
config_manager = ConfigManager()

# Синхронизация конфигураций
config_manager.sync_configs()

# Обновление настроек
updates = {
    "foundry_ai": {
        "temperature": 0.8,
        "max_tokens": 1024
    }
}

result = config_manager.update_remote_config(updates)
if result:
    print("Configuration updated successfully")
```

---

**Предыдущий шаг**: [Устранение неполадок](troubleshooting.md) | **Следующий шаг**: [Docker](docker.md)