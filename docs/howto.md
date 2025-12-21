# 🛠️ Практические рецепты

---
**📚 Навигация:** [🏠 Главная](README.md) | [📦 Установка](installation.md) | [🚀 Запуск](running.md) | [🎯 Лончеры](launchers.md) | [📚 Использование](usage.md) | [⚙️ Настройка](configuration.md) | [📊 Примеры](examples.md) | [🛠️ Рецепты](howto.md) | [🔌 MCP](mcp_integration.md) | [🌍 Туннели](tunnel_guide.md) | [🐳 Docker](docker.md) | [🛠️ Разработка](development.md) | [🚀 Развертывание](deployment.md) | [🔧 cURL](curl_commands.md) | [📋 Проект](project_info.md)

---

## Настройка RAG системы

### Создание индекса из документации
```bash
# Создать RAG индекс из папки с документами
python -c "
from src.rag.rag_system import rag_system
import asyncio
asyncio.run(rag_system.create_index_from_directory('../docs'))
"
```

### Добавление новых документов
```python
from src.rag.rag_system import rag_system

# Добавить документ в индекс
await rag_system.add_document(
    text="Содержимое документа",
    source="manual.md",
    section="Раздел 1"
)
```

## Подключение моделей

### Foundry модель
```python
model_data = {
    "model_id": "deepseek-r1-distill-qwen-7b-generic-cpu:3",
    "provider": "foundry",
    "model_name": "DeepSeek R1 Distill",
    "endpoint_url": "http://localhost:51601/v1/"
}
```

### OpenAI модель
```python
model_data = {
    "model_id": "gpt-3.5-turbo",
    "provider": "openai",
    "model_name": "GPT-3.5 Turbo",
    "endpoint_url": "https://api.openai.com/v1/",
    "api_key": "your-openai-key"
}
```

### Ollama модель
```python
model_data = {
    "model_id": "llama2:7b",
    "provider": "ollama",
    "model_name": "Llama 2 7B",
    "endpoint_url": "http://localhost:11434/api/"
}
```

## Автоматизация

### Автозапуск с системой (Windows)
```batch
# Создать bat файл для автозапуска
@echo off
cd /d "C:\path\to\FastApiFoundry"
call venv\Scripts\activate
python run.py --prod
```

### Systemd сервис (Linux)
```ini
[Unit]
Description=FastAPI Foundry
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/fastapi-foundry
ExecStart=/opt/fastapi-foundry/venv/bin/python run.py --prod
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker автозапуск
```bash
# Автоматический запуск при старте системы
docker-compose up -d

# Или через скрипт
.\docker-manager.ps1 run
```

### Тестирование клиентов
```bash
# Основной API клиент
python example_client.py

# Клиент управления моделями
python example_model_client.py

# Системные тесты
python test_system.py
```

## Мониторинг

### Проверка здоровья
```bash
# Простая проверка
curl http://localhost:8000/api/v1/health

# Детальная проверка с jq
curl -s http://localhost:8000/api/v1/health | jq .
```

### Логирование
```python
# Настройка уровня логирования
import logging
logging.getLogger("fastapi-foundry").setLevel(logging.DEBUG)
```

## Производительность

### Оптимизация для продакшн
```env
# Увеличить количество workers
API_WORKERS=4

# Отключить debug режим
DEFAULT_MODE=prod
LOG_LEVEL=WARNING

# Настроить таймауты
FOUNDRY_TIMEOUT=60
```

### Кэширование RAG результатов
```python
# Включить кэширование в RAG системе
RAG_CACHE_ENABLED=true
RAG_CACHE_SIZE=1000
```

---

## 🛠️ Навигация по разделу "Практика"

| Документ | Описание |
|----------|----------|
| [📊 Примеры](examples.md) | Готовые примеры кода и сценарии |
| [🛠️ Рецепты](howto.md) | Практические рецепты и настройки |

## 🔗 Другие разделы

| Раздел | Документы |
|--------|-----------||
| **📚 Начало работы** | [📦 Установка](installation.md) • [🚀 Запуск](running.md) • [🎯 Лончеры](launchers.md) • [📚 Использование](usage.md) • [⚙️ Настройка](configuration.md) |
| **🌐 Интеграция** | [🔌 MCP](mcp_integration.md) • [🌍 Туннели](tunnel_guide.md) |
| **🚀 Развертывание** | [🐳 Docker](docker.md) • [🚀 Deployment](deployment.md) |
| **👨💻 Разработка** | [🛠️ Development](development.md) • [🔧 cURL](curl_commands.md) • [📋 Проект](project_info.md) |

---

**📚 Быстрые ссылки:** [⬅️ Назад к оглавлению](README.md) | [📚 Все документы](README.md#-документация)

**FastAPI Foundry** - часть экосистемы AiStros  
© 2025 AiStros Team