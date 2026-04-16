# 🏗️ Архитектура Foundry - FastAPI Foundry

## 📋 Обзор архитектуры

FastAPI Foundry использует **Microsoft Foundry Local CLI** как сервис для запуска локальных AI моделей. Это создает многоуровневую архитектуру для работы с AI.

## 🔄 Схема взаимодействия

```
┌─────────────────┐    HTTP REST API    ┌──────────────────┐    CLI Commands    ┌─────────────────┐
│   FastAPI       │ ──────────────────► │  Foundry Local   │ ─────────────────► │   AI Models     │
│   (Port 9696)   │                     │  (Port 50477)    │                    │   (ONNX/Local)  │
└─────────────────┘                     └──────────────────┘                    └─────────────────┘
        │                                        │                                        │
        ▼                                        ▼                                        ▼
┌─────────────────┐                     ┌──────────────────┐                    ┌─────────────────┐
│  Web Interface  │                     │  Model Manager   │                    │  Model Storage  │
│  (Static Files) │                     │  (Load/Unload)   │                    │  (~/.foundry)   │
└─────────────────┘                     └──────────────────┘                    └─────────────────┘
```

## 🧩 Компоненты системы

### 1. FastAPI Server (Port 9696)
- **Роль**: REST API интерфейс для клиентов
- **Функции**: 
  - Обработка HTTP запросов
  - Валидация параметров
  - Маршрутизация к Foundry
  - Веб-интерфейс
- **Файлы**: `src/api/`, `run.py`

### 2. Foundry Local CLI (Port 50477)
- **Роль**: Сервис для запуска AI моделей
- **Функции**:
  - Загрузка/выгрузка моделей
  - Генерация текста
  - Управление ресурсами
- **Команды**: `foundry service start/stop`

### 3. AI Models (Local Storage)
- **Роль**: Локальные AI модели в формате ONNX
- **Расположение**: `~/.foundry/models/`
- **Типы**: Qwen, DeepSeek, Mistral, Llama

### 4. Web Interface (Static Files)
- **Роль**: Пользовательский интерфейс
- **Файлы**: `static/index.html`, `static/chat.html`
- **Функции**: Чат, управление моделями, мониторинг

## 🔌 API Integration

### FastAPI → Foundry Communication

```python
# src/models/foundry_client.py
class FoundryClient:
    def __init__(self, base_url="http://localhost:50477/v1/"):
        self.base_url = base_url
    
    async def generate_text(self, prompt, model, **kwargs):
        """Генерация текста через Foundry API"""
        response = await self.client.post(
            f"{self.base_url}completions",
            json={
                "model": model,
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", 100),
                "temperature": kwargs.get("temperature", 0.7)
            }
        )
        return response.json()
```

### Request Flow

```
1. Client Request → FastAPI Endpoint
   POST /api/v1/generate
   {
     "prompt": "Hello",
     "model": "qwen2.5-0.5b-instruct-generic-cpu:4"
   }

2. FastAPI → Foundry API
   POST http://localhost:50477/v1/completions
   {
     "model": "qwen2.5-0.5b-instruct-generic-cpu:4",
     "prompt": "Hello",
     "max_tokens": 100
   }

3. Foundry → AI Model
   CLI: foundry run qwen2.5-0.5b-instruct-generic-cpu:4

4. Response Chain
   AI Model → Foundry → FastAPI → Client
```

## 🚀 Startup Sequence

### Правильный порядок запуска

```powershell
# 1. СНАЧАЛА - Foundry сервер
foundry service start
# Ожидание: Foundry запустится на порту 50477

# 2. ПОТОМ - FastAPI сервер  
python run.py
# Ожидание: FastAPI запустится на порту 9696
```

### Автоматический запуск (start.ps1)

```powershell
# start.ps1 автоматически:
# 1. Проверяет запущенный Foundry
# 2. Запускает Foundry если нужно
# 3. Определяет порт Foundry
# 4. Передает порт в FastAPI через переменные окружения
# 5. Запускает FastAPI сервер
```

## 🔧 Configuration Integration

### config.json → Environment Variables

```json
{
  "foundry_ai": {
    "base_url": "http://localhost:50477/v1/",
    "default_model": "qwen2.5-0.5b-instruct-generic-cpu:4"
  }
}
```

```powershell
# start.ps1 устанавливает переменные окружения
$env:FOUNDRY_BASE_URL = "http://localhost:50477/v1/"
$env:FOUNDRY_PORT = "50477"
```

```python
# src/core/config.py использует переменные
import os
foundry_url = os.getenv('FOUNDRY_BASE_URL', config['foundry_ai']['base_url'])
```

## 📊 Model Management

### Model Lifecycle

```
1. Model Discovery
   foundry models list → Available models

2. Model Loading  
   foundry models load <model_id> → Model in memory

3. Model Usage
   FastAPI → Foundry API → Loaded model

4. Model Unloading
   foundry models unload <model_id> → Free memory
```

### Model Storage Structure

```
~/.foundry/
├── models/
│   ├── qwen2.5-0.5b-instruct-generic-cpu:4/
│   │   ├── model.onnx
│   │   ├── tokenizer.json
│   │   └── config.json
│   └── deepseek-r1-distill-qwen-7b-generic-cpu:3/
│       ├── model.onnx
│       └── ...
├── cache/
└── logs/
```

## 🔍 Health Monitoring

### Multi-level Health Checks

```python
# 1. FastAPI Health
GET /api/v1/health
{
  "status": "healthy",
  "foundry_status": "connected"
}

# 2. Foundry Health  
GET http://localhost:50477/v1/models
{
  "models": [...]
}

# 3. Model Health
POST http://localhost:50477/v1/completions
{
  "model": "test-model",
  "prompt": "test"
}
```

### Health Check Flow

```
Client → FastAPI Health Endpoint
         ↓
FastAPI → Foundry API Check
         ↓  
Foundry → Model Availability Check
         ↓
Response Chain: Model → Foundry → FastAPI → Client
```

## 🛠️ Error Handling

### Error Propagation

```
AI Model Error → Foundry Error Response → FastAPI Error Handler → Client Error
```

### Common Error Scenarios

1. **Foundry Not Running**
   ```json
   {
     "error": "Foundry service unavailable",
     "detail": "Connection refused to http://localhost:50477",
     "status_code": 503
   }
   ```

2. **Model Not Loaded**
   ```json
   {
     "error": "Model not available",
     "detail": "Model 'qwen2.5-0.5b' is not loaded",
     "status_code": 404
   }
   ```

3. **Generation Timeout**
   ```json
   {
     "error": "Generation timeout",
     "detail": "Request timed out after 300 seconds",
     "status_code": 408
   }
   ```

## 🔄 Port Management

### Dynamic Port Discovery

```powershell
# start.ps1 автоматически находит порт Foundry
$foundryProcesses = Get-Process -Name "foundry"
$netstatOutput = netstat -ano | Select-String "$($foundryProcesses[0].Id)"
# Парсинг порта из netstat
```

### Port Conflict Resolution

```json
{
  "port_management": {
    "conflict_resolution": "kill_process",
    "auto_find_free_port": true,
    "port_range_start": 9696,
    "port_range_end": 9796
  }
}
```

## 🔐 Security Architecture

### API Security Layers

```
1. CORS Protection (FastAPI level)
2. API Key Authentication (Optional)
3. Rate Limiting (Configurable)
4. Input Validation (Pydantic models)
5. Foundry Internal Security
```

### Secure Communication

```
Client → HTTPS (Optional) → FastAPI → HTTP (Local) → Foundry → Local Models
```

## 📈 Performance Considerations

### Optimization Points

1. **Connection Pooling**: FastAPI → Foundry
2. **Model Caching**: Keep models loaded in Foundry
3. **Request Batching**: Multiple prompts in one request
4. **Async Processing**: Non-blocking I/O

### Resource Management

```
FastAPI Memory: ~100MB (Base)
Foundry Memory: ~500MB (Service)
Model Memory: 500MB - 8GB (Per model)
Total: 1GB - 16GB (Depending on models)
```

## 🔧 Development Architecture

### Code Organization

```
src/
├── api/                 # FastAPI application
│   ├── app.py          # Application factory
│   ├── main.py         # Entry point
│   └── endpoints/      # API routes
├── models/             # Foundry integration
│   ├── foundry_client.py
│   └── model_manager.py
├── core/               # Configuration
└── utils/              # Utilities
```

### Extension Points

1. **Custom Endpoints**: Add new API routes
2. **Model Adapters**: Support new model types
3. **Middleware**: Add custom processing
4. **Plugins**: Extend functionality

---

**Следующий шаг**: [Управление моделями](models-management.md)