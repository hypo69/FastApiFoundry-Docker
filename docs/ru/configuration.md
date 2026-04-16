# ⚙️ Конфигурация FastAPI Foundry

## 📋 Обзор конфигурации

FastAPI Foundry использует файл `config.json` для всех настроек. Это единый источник конфигурации для всех компонентов системы.

## 📁 Структура config.json

```json
{
  "fastapi_server": { ... },      // Настройки FastAPI сервера
  "foundry_ai": { ... },          // Настройки Foundry AI
  "rag_system": { ... },          // Настройки RAG системы
  "security": { ... },            // Настройки безопасности
  "logging": { ... },             // Настройки логирования
  "mcp_server": { ... },          // Настройки MCP сервера
  "web_interface": { ... },       // Настройки веб-интерфейса
  "port_management": { ... },     // Управление портами
  "development": { ... }          // Настройки разработки
}
```

## 🌐 FastAPI Server

```json
{
  "fastapi_server": {
    "host": "0.0.0.0",              // Хост сервера
    "port": 9696,                   // Порт сервера
    "auto_find_free_port": true,    // Автопоиск свободного порта
    "mode": "dev",                  // Режим: dev/prod
    "workers": 1,                   // Количество воркеров
    "reload": true,                 // Автоперезагрузка при изменениях
    "log_level": "INFO",            // Уровень логирования
    "cors_origins": ["*"]           // CORS origins
  }
}
```

### Параметры
- `host` - IP адрес для привязки (0.0.0.0 для всех интерфейсов)
- `port` - Порт сервера (по умолчанию 9696)
- `auto_find_free_port` - Автоматический поиск свободного порта
- `mode` - Режим работы (dev/prod)
- `workers` - Количество uvicorn воркеров
- `reload` - Автоперезагрузка при изменении кода
- `log_level` - Уровень логирования (DEBUG/INFO/WARNING/ERROR)

## 🤖 Foundry AI

```json
{
  "foundry_ai": {
    "base_url": "http://localhost:50477/v1/",  // URL Foundry API
    "default_model": "qwen2.5-0.5b-instruct-generic-cpu:4",  // Модель по умолчанию
    "auto_load_default": false,               // Автозагрузка модели
    "temperature": 0.7,                       // Температура генерации
    "top_p": 0.9,                            // Nucleus sampling
    "top_k": 40,                             // Top-K sampling
    "max_tokens": 2048,                      // Максимум токенов
    "timeout": 300                           // Таймаут запросов (сек)
  }
}
```

### Параметры генерации
- `temperature` - Креативность (0.0-1.0, где 0.0 = детерминированно)
- `top_p` - Nucleus sampling (0.0-1.0)
- `top_k` - Top-K sampling (количество токенов)
- `max_tokens` - Максимальное количество токенов в ответе
- `timeout` - Таймаут для запросов к Foundry

### Автозагрузка модели
```json
{
  "foundry_ai": {
    "auto_load_default": true,
    "default_model": "deepseek-r1-distill-qwen-7b-generic-cpu:3"
  }
}
```

## 🔍 RAG System

```json
{
  "rag_system": {
    "enabled": true,                          // Включить RAG систему
    "index_dir": "./rag_index",              // Папка индекса
    "model": "sentence-transformers/all-MiniLM-L6-v2",  // Модель эмбеддингов
    "chunk_size": 1000,                      // Размер чанков
    "top_k": 5                               // Количество результатов
  }
}
```

### Параметры
- `enabled` - Включить/выключить RAG систему
- `index_dir` - Папка для хранения FAISS индекса
- `model` - Модель для создания эмбеддингов
- `chunk_size` - Размер текстовых чанков для индексации
- `top_k` - Количество наиболее релевантных результатов

## 🔐 Security

```json
{
  "security": {
    "api_key": null,                         // API ключ (null = отключен)
    "https_enabled": false,                  // HTTPS
    "cors_origins": ["*"],                   // CORS origins
    "ssl_cert_file": "~/.ssl/cert.pem",     // SSL сертификат
    "ssl_key_file": "~/.ssl/key.pem"        // SSL ключ
  }
}
```

### API ключи
```json
{
  "security": {
    "api_key": "your-secret-api-key-here"
  }
}
```

Использование:
```bash
curl -H "X-API-Key: your-secret-api-key-here" \
  http://localhost:9696/api/v1/models
```

### HTTPS настройка
```json
{
  "security": {
    "https_enabled": true,
    "ssl_cert_file": "/path/to/cert.pem",
    "ssl_key_file": "/path/to/key.pem"
  }
}
```

## 📊 Logging

```json
{
  "logging": {
    "level": "INFO",                         // Уровень логирования
    "file": "logs/fastapi-foundry.log"       // Файл логов
  }
}
```

### Уровни логирования
- `DEBUG` - Детальная отладочная информация
- `INFO` - Общая информация о работе
- `WARNING` - Предупреждения
- `ERROR` - Только ошибки

## 🔌 MCP Server

```json
{
  "mcp_server": {
    "name": "aistros-foundry",
    "version": "1.0.0",
    "description": "AiStros Foundry MCP Server",
    "base_url": "http://localhost:51601/v1/",
    "default_model": "deepseek-r1-distill-qwen-7b-generic-cpu:3",
    "timeout": 30,
    "capabilities": {
      "tools": [
        "generate_text",
        "list_foundry_models",
        "get_foundry_status"
      ]
    }
  }
}
```

## 🌐 Web Interface

```json
{
  "web_interface": {
    "api_base": "http://localhost:9696/api/v1",  // Базовый URL API
    "auto_refresh_interval": 30000,             // Интервал обновления (мс)
    "logs_refresh_interval": 10000,             // Интервал обновления логов (мс)
    "max_chat_history": 100                     // Максимум сообщений в чате
  }
}
```

## 🔧 Port Management

```json
{
  "port_management": {
    "conflict_resolution": "kill_process",      // Стратегия разрешения конфликтов
    "auto_find_free_port": true,               // Автопоиск свободного порта
    "port_range_start": 9696,                  // Начало диапазона портов
    "port_range_end": 9796,                    // Конец диапазона портов
    "foundry_port": 50477                      // Порт Foundry
  }
}
```

### Стратегии разрешения конфликтов
- `kill_process` - Завершить процесс, занимающий порт
- `find_alternative` - Найти альтернативный порт
- `fail` - Завершить с ошибкой

## 🛠️ Development

```json
{
  "development": {
    "debug": true,                             // Режим отладки
    "verbose": true,                           // Подробные логи
    "temp_dir": "./temp"                       // Временная папка
  }
}
```

## 🐳 Docker

```json
{
  "docker": {
    "image": "fastapi-foundry:0.2.1",
    "container_name": "fastapi-foundry-docker",
    "network": "fastapi-foundry-network",
    "foundry_host": "localhost",
    "foundry_port": 8008,
    "rag_enabled": true,
    "healthcheck": {
      "interval": "30s",
      "timeout": "10s",
      "retries": 3
    }
  }
}
```

## 📊 Examples Configuration

```json
{
  "examples": {
    "client_demo": {
      "enabled": true,
      "timeout": 30
    },
    "rag_demo": {
      "enabled": true,
      "query": "WordPress плагины AiStros",
      "top_k": 3
    }
  }
}
```

## 🔧 Управление конфигурацией

### Через API
```bash
# Получить конфигурацию
curl http://localhost:9696/api/v1/config

# Обновить конфигурацию
curl -X POST http://localhost:9696/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{"foundry_ai": {"temperature": 0.8}}'
```

### Через Python
```python
import json

# Загрузить конфигурацию
with open('config.json', 'r') as f:
    config = json.load(f)

# Изменить настройки
config['foundry_ai']['temperature'] = 0.8

# Сохранить конфигурацию
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)
```

### Через веб-интерфейс
1. Откройте http://localhost:9696/static/control.html
2. Перейдите в раздел "Configuration"
3. Измените нужные параметры
4. Нажмите "Save Configuration"

## 🔄 Применение изменений

После изменения конфигурации:

```powershell
# Перезапуск сервера
python stop.py
.\start.ps1

# Или только FastAPI (если изменения не касаются Foundry)
Ctrl+C  # Остановить run.py
python run.py  # Запустить заново
```

## ✅ Валидация конфигурации

```powershell
# Проверить конфигурацию
python test_config.py

# Проверить с подробностями
python -c "
import json
from pathlib import Path
config = json.loads(Path('config.json').read_text())
print('Config loaded successfully!')
print(f'FastAPI port: {config[\"fastapi_server\"][\"port\"]}')
print(f'Foundry URL: {config[\"foundry_ai\"][\"base_url\"]}')
"
```

## 🔧 Примеры конфигураций

### Минимальная конфигурация
```json
{
  "fastapi_server": {
    "port": 9696
  },
  "foundry_ai": {
    "base_url": "http://localhost:50477/v1/"
  }
}
```

### Production конфигурация
```json
{
  "fastapi_server": {
    "host": "0.0.0.0",
    "port": 8000,
    "mode": "prod",
    "workers": 4,
    "reload": false,
    "log_level": "WARNING"
  },
  "security": {
    "api_key": "production-secret-key",
    "https_enabled": true,
    "cors_origins": ["https://yourdomain.com"]
  },
  "logging": {
    "level": "WARNING"
  }
}
```

### Development конфигурация
```json
{
  "fastapi_server": {
    "reload": true,
    "log_level": "DEBUG"
  },
  "development": {
    "debug": true,
    "verbose": true
  },
  "logging": {
    "level": "DEBUG"
  }
}
```

---

**Следующий шаг**: [Архитектура Foundry](foundry-architecture.md)