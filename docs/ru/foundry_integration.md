# 🔧 Foundry Integration Guide

**Версия:** 0.2.1  
**Проект:** FastApiFoundry (Docker)  
**Дата:** 9 декабря 2025  

---

## 🎯 Техническая интеграция с Foundry

Этот документ описывает техническую реализацию интеграции FastAPI с Microsoft Foundry Local CLI.

---

## 📋 Компоненты системы

### 1. FoundryClient (`src/models/foundry_client.py`)

Основной класс для взаимодействия с Foundry API:

```python
class FoundryClient:
    def __init__(self, base_url=None):
        # Автоматическое определение URL Foundry
        self.base_url = self._detect_foundry_url()
        self.timeout = aiohttp.ClientTimeout(total=30)
    
    async def health_check(self):
        """Проверка состояния Foundry сервиса"""
    
    async def generate_text(self, prompt: str, **kwargs):
        """Генерация текста через Foundry"""
    
    async def list_available_models(self):
        """Получить список доступных моделей"""
```

### 2. API Endpoints (`src/api/endpoints/`)

FastAPI endpoints для работы с Foundry:

```python
# models.py
@router.get("/models")
async def get_models():
    """Список моделей из Foundry"""
    return await foundry_client.list_available_models()

# generate.py  
@router.post("/generate")
async def generate_text(request: GenerateRequest):
    """Генерация текста через Foundry"""
    return await foundry_client.generate_text(request.prompt)
```

### 3. Автопоиск портов

```python
def get_foundry_port(self):
    """Автоматический поиск порта Foundry"""
    for port in range(50400, 50800):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                if s.connect_ex(('127.0.0.1', port)) == 0:
                    # Проверяем что это Foundry
                    response = requests.get(f'http://127.0.0.1:{port}/v1/models', timeout=1)
                    if response.status_code == 200:
                        return port
        except:
            continue
    return 50477  # По умолчанию
```

---

## 🔄 Жизненный цикл запроса

### 1. Инициализация клиента

```python
# При старте приложения
foundry_client = FoundryClient()
# → Автоматически ищет Foundry на портах 50400-50800
# → Устанавливает base_url = "http://localhost:{port}/v1"
```

### 2. Health Check

```python
# Перед каждым запросом
health = await foundry_client.health_check()
if health["status"] != "healthy":
    return {"error": "Foundry недоступен"}
```

### 3. Генерация текста

```python
# HTTP запрос к Foundry
url = f"{self.base_url}/chat/completions"
payload = {
    "model": "deepseek-r1:14b",
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 0.7,
    "max_tokens": 2048
}

async with session.post(url, json=payload) as response:
    data = await response.json()
    return data["choices"][0]["message"]["content"]
```

---

## 🌐 HTTP API Mapping

### Foundry → FastAPI

| Foundry Endpoint | FastAPI Endpoint | Описание |
|------------------|------------------|----------|
| `GET /v1/models` | `GET /api/v1/models` | Список моделей |
| `POST /v1/chat/completions` | `POST /api/v1/generate` | Генерация текста |
| `POST /v1/completions` | `POST /api/v1/complete` | Простая генерация |

### Формат запросов

**Foundry (OpenAI-совместимый):**
```json
{
  "model": "deepseek-r1:14b",
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "temperature": 0.7,
  "max_tokens": 2048
}
```

**FastAPI (упрощенный):**
```json
{
  "prompt": "Hello",
  "model": "deepseek-r1:14b",
  "temperature": 0.7,
  "max_tokens": 2048
}
```

---

## ⚙️ Конфигурация

### Переменные окружения

```env
# Foundry подключение
FOUNDRY_BASE_URL=http://localhost:50477/v1/
FOUNDRY_PORT=50477

# Модель по умолчанию
FOUNDRY_DEFAULT_MODEL=deepseek-r1:14b

# Параметры генерации
FOUNDRY_TEMPERATURE=0.7
FOUNDRY_MAX_TOKENS=2048
FOUNDRY_TOP_P=0.9
FOUNDRY_TOP_K=40
```

### Автоматическая настройка

```python
# В start.ps1
$foundryPort = Find-FoundryPort
$env:FOUNDRY_BASE_URL = "http://localhost:$foundryPort/v1/"
$env:FOUNDRY_PORT = $foundryPort

# В Python коде
import os
foundry_url = os.getenv('FOUNDRY_BASE_URL', 'http://localhost:50477/v1/')
```

---

## 🔧 Управление моделями

### Через Foundry CLI

```bash
# Список доступных моделей
foundry model list

# Запуск модели
foundry model run deepseek-r1:14b
# → Модель становится доступна через HTTP API

# Остановка модели  
foundry model stop deepseek-r1:14b

# Статус сервиса
foundry service status
```

### Через FastAPI

```python
# Проверка доступных моделей
models = await foundry_client.list_available_models()
# → Возвращает список из Foundry API

# Автоматическая загрузка модели по умолчанию
if config.foundry_auto_load_default:
    await load_default_model(config.foundry_default_model)
```

---

## 🚨 Обработка ошибок

### Foundry недоступен

```python
async def generate_text(self, prompt: str, **kwargs):
    try:
        health = await self.health_check()
        if health["status"] != "healthy":
            return {
                "success": False,
                "error": f"Foundry недоступен на порту {health['port']}",
                "foundry_status": health["status"]
            }
    except Exception as e:
        return {
            "success": False,
            "error": "Не удается подключиться к Foundry"
        }
```

### Модель не загружена

```python
# HTTP 400 от Foundry
if response.status == 400:
    error_data = await response.json()
    if "model not found" in error_data.get("error", "").lower():
        return {
            "success": False,
            "error": f"Модель {model} не загружена. Запустите: foundry model run {model}"
        }
```

### Автоматическое восстановление

```python
# При ошибке подключения
except aiohttp.ClientError:
    # Пытаемся найти новый порт Foundry
    new_port = self.get_foundry_port()
    if new_port != self.current_port:
        self.base_url = f"http://localhost:{new_port}/v1"
        # Повторяем запрос
        return await self.generate_text(prompt, **kwargs)
```

---

## 📊 Мониторинг и логирование

### Health Check

```python
async def health_check(self):
    """Расширенная проверка здоровья"""
    try:
        start_time = time.time()
        
        # Проверяем доступность API
        async with session.get(f"{self.base_url}/models") as response:
            response_time = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                return {
                    "status": "healthy",
                    "models_count": len(data.get('data', [])),
                    "response_time": response_time,
                    "port": self.get_port_from_url(),
                    "timestamp": datetime.now().isoformat()
                }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

### Логирование

```python
from src.utils.logging_system import get_logger

logger = get_logger("foundry-client")

# Логирование запросов
logger.info("Foundry request", 
           endpoint=url, 
           model=payload.get('model'),
           prompt_length=len(prompt))

# Логирование ответов
logger.info("Foundry response",
           status=response.status,
           response_time=response_time,
           tokens_used=data.get('usage', {}).get('total_tokens'))

# Логирование ошибок
logger.error("Foundry connection failed",
            port=port,
            error=str(e),
            exc_info=True)
```

---

## 🐳 Docker интеграция

### Dockerfile

```dockerfile
# Установка Foundry в контейнер
RUN curl -L https://foundry.paradigm.xyz | bash
ENV PATH="/root/.foundry/bin:${PATH}"

# Копирование приложения
COPY . /app
WORKDIR /app

# Установка Python зависимостей
RUN pip install -r requirements.txt

# Запуск
CMD ["python", "run.py"]
```

### docker-compose.yml

```yaml
services:
  fastapi-foundry:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FOUNDRY_BASE_URL=http://localhost:50477/v1/
      - FOUNDRY_DEFAULT_MODEL=deepseek-r1:14b
    volumes:
      - foundry_models:/root/.foundry
    command: >
      sh -c "
        foundry service start &
        sleep 10 &&
        python run.py
      "

volumes:
  foundry_models:
```

---

## 🔄 Автоматизация

### Автозапуск модели

```python
# В config.json
{
  "foundry_ai": {
    "auto_load_default": true,
    "default_model": "deepseek-r1:14b"
  }
}

# В коде
async def startup_event():
    if config.foundry_auto_load_default:
        await ensure_model_loaded(config.foundry_default_model)

async def ensure_model_loaded(model_id: str):
    """Автоматическая загрузка модели если не загружена"""
    models = await foundry_client.list_available_models()
    loaded_models = [m["id"] for m in models.get("models", [])]
    
    if model_id not in loaded_models:
        logger.info(f"Загружаем модель: {model_id}")
        subprocess.run(["foundry", "model", "run", model_id])
        await asyncio.sleep(10)  # Ждем загрузки
```

### Автоматический перезапуск

```python
# В start.ps1
while ($true) {
    try {
        # Проверяем Foundry
        $foundryStatus = foundry service status
        if ($foundryStatus -notmatch "running") {
            Write-Host "Перезапуск Foundry..."
            foundry service start
        }
        
        # Проверяем FastAPI
        $response = Invoke-WebRequest "http://localhost:9696/api/v1/health" -TimeoutSec 5
        if ($response.StatusCode -ne 200) {
            Write-Host "Перезапуск FastAPI..."
            # Restart logic
        }
        
        Start-Sleep 30
    } catch {
        Write-Host "Ошибка мониторинга: $_"
        Start-Sleep 10
    }
}
```

---

## 🎯 Лучшие практики

### 1. Управление соединениями

```python
# Переиспользование HTTP сессий
class FoundryClient:
    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
```

### 2. Retry логика

```python
async def generate_text_with_retry(self, prompt: str, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await self.generate_text(prompt)
        except aiohttp.ClientError as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Retry {attempt + 1}/{max_retries}: {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 3. Кэширование

```python
from functools import lru_cache
import time

@lru_cache(maxsize=1)
def get_cached_models(cache_time=300):  # 5 минут
    """Кэшированный список моделей"""
    return {
        "models": self._fetch_models(),
        "timestamp": time.time()
    }
```

---

## 🔍 Отладка

### Логи Foundry

```bash
# Логи сервиса Foundry
foundry service logs

# Подробные логи
foundry --verbose service start
```

### Тестирование API

```bash
# Прямой тест Foundry API
curl http://localhost:50477/v1/models

# Тест через FastAPI
curl http://localhost:9696/api/v1/models

# Тест генерации
curl -X POST http://localhost:50477/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-r1:14b", "messages": [{"role": "user", "content": "test"}]}'
```

### Debug режим

```python
# В .env
LOG_LEVEL=DEBUG
FOUNDRY_DEBUG=true

# В коде
if os.getenv('FOUNDRY_DEBUG'):
    logger.setLevel(logging.DEBUG)
    # Логируем все HTTP запросы
    aiohttp_logger = logging.getLogger('aiohttp.client')
    aiohttp_logger.setLevel(logging.DEBUG)
```

---

## 📈 Производительность

### Оптимизации

1. **Переиспользование соединений** - один aiohttp.ClientSession
2. **Асинхронные запросы** - все операции через async/await  
3. **Кэширование** - список моделей кэшируется на 5 минут
4. **Connection pooling** - aiohttp автоматически управляет пулом
5. **Таймауты** - разумные таймауты для всех запросов

### Мониторинг производительности

```python
import time
from contextlib import asynccontextmanager

@asynccontextmanager
async def measure_time(operation_name: str):
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        logger.info(f"{operation_name} took {duration:.2f}s")

# Использование
async with measure_time("foundry_generate"):
    result = await foundry_client.generate_text(prompt)
```

---

Эта документация покрывает все аспекты технической интеграции с Foundry в нашем проекте.