# 🔧 FastAPI Foundry - Полезные cURL команды

**Версия:** 1.0.0  
**Дата:** 23 декабря 2025  

---
**📚 Навигация:** [🏠 Главная](README.md) | [📦 Установка](installation.md) | [🚀 Запуск](running.md) | [🎯 Лончеры](launchers.md) | [📖 Использование](usage.md) | [⚙️ Настройка](configuration.md) | [📊 Примеры](examples.md) | [🛠️ Рецепты](howto.md) | [🔌 MCP](mcp_integration.md) | [🌍 Туннели](tunnel_guide.md) | [🐳 Docker](docker.md) | [🛠️ Разработка](development.md) | [🚀 Развертывание](deployment.md) | [🔧 cURL](curl_commands.md) | [📋 Проект](project_info.md)
---

## 📋 Основные API endpoints

### 🔍 Health Check
```bash
# Проверка здоровья системы
curl -s http://localhost:9696/api/v1/health | python -m json.tool

# Быстрая проверка статуса
curl -s http://localhost:9696/api/v1/health | grep -o '"status":"[^"]*"'
```

### 🤖 Модели

```bash
# Получить список доступных моделей
curl -s http://localhost:9696/api/v1/models | python -m json.tool

# Проверить количество моделей
curl -s http://localhost:9696/api/v1/models | python -c "import sys, json; data=json.load(sys.stdin); print('Models:', len(data.get('models', [])))"
```

### 💬 Генерация текста

```bash
# Простая генерация без RAG
curl -X POST http://localhost:9696/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Привет! Как дела?",
    "model": "deepseek-r1-distill-qwen-7b-generic-cpu:3",
    "use_rag": false,
    "max_tokens": 100
  }' | python -m json.tool

# Генерация с RAG контекстом
curl -X POST http://localhost:9696/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Как настроить FastAPI Foundry?",
    "use_rag": true,
    "temperature": 0.7
  }' | python -m json.tool
```

### 🔍 RAG поиск

```bash
# Поиск в документации
curl -X POST http://localhost:9696/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "FastAPI configuration",
    "top_k": 3
  }' | python -m json.tool
```

---

## 🛠️ Foundry API (прямые вызовы)

### Проверка Foundry сервиса
```bash
# Список моделей в Foundry
curl -s http://localhost:50477/v1/models | python -m json.tool

# Прямой вызов модели через Foundry
curl -X POST http://localhost:50477/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-r1-distill-qwen-7b-generic-cpu:3",
    "messages": [{"role": "user", "content": "Привет"}],
    "max_tokens": 100
  }'
```

---

## 🧪 Тестирование и отладка

### Быстрые проверки
```bash
# Проверка доступности сервера
curl -I http://localhost:9696/

# Проверка CORS
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS http://localhost:9696/api/v1/generate

# Проверка статических файлов
curl -I http://localhost:9696/static/simple.html
```

---
## 👨‍💻 Навигация по разделу "Разработка"

| Документ | Описание |
|----------|----------|
| [🛠️ Разработка](development.md) | Архитектура и добавление функций |
| [🔧 cURL команды](curl_commands.md) | API тестирование и отладка |
| [📋 Информация о проекте](project_info.md) | Детальная информация |

## 🔗 Другие разделы

| Раздел | Документы |
|--------|-----------|
| **📖 Начало работы** | [📦 Установка](installation.md) • [🚀 Запуск](running.md) • [🎯 Лончеры](launchers.md) • [📖 Использование](usage.md) • [⚙️ Настройка](configuration.md) |
| **🛠️ Практика** | [📊 Примеры](examples.md) • [🛠️ Рецепты](howto.md) |
| **🌐 Интеграция** | [🔌 MCP](mcp_integration.md) • [🌍 Туннели](tunnel_guide.md) |
| **🚀 Развертывание** | [🐳 Docker](docker.md) • [🚀 Deployment](deployment.md) |

---

**📚 Быстрые ссылки:** [⬅️ Назад к оглавлению](README.md) | [📖 Все документы](README.md#-документация)

**FastAPI Foundry** - часть экосистемы AiStros  
© 2025 AiStros Team