# 🔧 FastAPI Foundry - Полезные cURL команды

**Версия:** 1.0.0  
**Дата:** 20 декабря 2025  

---
**📚 Навигация:** [🏠 Главная](README.md) | [📦 Установка](installation.md) | [🚀 Запуск](running.md) | [🎯 Лончеры](launchers.md) | [📚 Использование](usage.md) | [⚙️ Настройка](configuration.md) | [📊 Примеры](examples.md) | [🛠️ Рецепты](howto.md) | [🔌 MCP](mcp_integration.md) | [🌍 Туннели](tunnel_guide.md) | [🐳 Docker](docker.md) | [🛠️ Разработка](development.md) | [🚀 Развертывание](deployment.md) | [🔧 cURL](curl_commands.md) | [📋 Проект](project_info.md)

---

## 📋 Основные API endpoints

### 🔍 Health Check
```bash
# Проверка здоровья системы
curl -s http://localhost:8002/api/v1/health | python -m json.tool

# Быстрая проверка статуса
curl -s http://localhost:8002/api/v1/health | grep -o '"status":"[^"]*"'
```

### 🤖 Модели

```bash
# Получить список доступных моделей
curl -s http://localhost:8002/api/v1/models | python -m json.tool

# Проверить количество моделей
curl -s http://localhost:8002/api/v1/models | python -c "import sys, json; data=json.load(sys.stdin); print('Models:', len(data.get('models', [])))"
```

### 💬 Генерация текста

```bash
# Простая генерация без RAG
curl -X POST http://localhost:8002/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Привет! Как дела?",
    "model": "deepseek-r1-distill-qwen-7b-generic-cpu:3",
    "use_rag": false,
    "max_tokens": 100
  }' | python -m json.tool

# Генерация с RAG контекстом
curl -X POST http://localhost:8002/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Как настроить FastAPI Foundry?",
    "use_rag": true,
    "temperature": 0.7
  }' | python -m json.tool

# Короткий ответ для тестирования
curl -X POST http://localhost:8002/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hi",
    "use_rag": false,
    "max_tokens": 50
  }'
```

### 🔍 RAG поиск

```bash
# Поиск в документации
curl -X POST http://localhost:8002/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "FastAPI configuration",
    "top_k": 3
  }' | python -m json.tool

# Поиск по установке
curl -X POST http://localhost:8002/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "installation requirements",
    "top_k": 5
  }'
```

---

## 🛠️ Foundry API (прямые вызовы)

### Проверка Foundry сервиса
```bash
# Список моделей в Foundry
curl -s http://localhost:50477/v1/models | python -m json.tool

# Количество моделей
curl -s http://localhost:50477/v1/models | python -c "import sys, json; data=json.load(sys.stdin); print('Foundry models:', len(data.get('data', [])))"

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
curl -I http://localhost:8002/

# Проверка CORS
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS http://localhost:8002/api/v1/generate

# Проверка статических файлов
curl -I http://localhost:8002/static/simple.html
```

### Нагрузочное тестирование
```bash
# Простой тест производительности (требует apache2-utils)
ab -n 10 -c 2 http://localhost:8002/api/v1/health

# Тест генерации (осторожно - может быть медленным)
for i in {1..3}; do
  echo "Test $i:"
  time curl -X POST http://localhost:8002/api/v1/generate \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Test '$i'", "max_tokens": 20}' \
    -w "\nTime: %{time_total}s\n"
done
```

### Мониторинг логов
```bash
# Отслеживание логов сервера (если запущен в фоне)
tail -f logs/app.log

# Поиск ошибок в логах
grep -i error logs/app.log | tail -10
```

---

## 📊 Полезные однострочники

```bash
# Проверить все сервисы одной командой
echo "FastAPI:" && curl -s http://localhost:8002/api/v1/health | grep -o '"status":"[^"]*"' && \
echo "Foundry:" && curl -s http://localhost:50477/v1/models | python -c "import sys, json; print('OK' if json.load(sys.stdin).get('data') else 'FAIL')" 2>/dev/null || echo "FAIL"

# Быстрый тест чата
curl -s -X POST http://localhost:8002/api/v1/generate -H "Content-Type: application/json" -d '{"prompt":"test","max_tokens":20}' | python -c "import sys, json; data=json.load(sys.stdin); print('✅ OK' if data.get('success') else '❌ FAIL:', data.get('error', 'Unknown'))"

# Проверка RAG индекса
curl -s http://localhost:8002/api/v1/health | python -c "import sys, json; data=json.load(sys.stdin); print(f'RAG: {data.get(\"rag_chunks\", 0)} chunks')"
```

---

## 🔧 Отладка проблем

### Проблемы с подключением
```bash
# Проверить, запущен ли сервер
netstat -ano | findstr :8002

# Проверить Foundry
netstat -ano | findstr :50477

# Проверить процессы Python
tasklist | findstr python.exe
```

### Проблемы с моделями
```bash
# Детальная информация о моделях
curl -s http://localhost:8002/api/v1/models | python -c "
import sys, json
data = json.load(sys.stdin)
if data.get('success'):
    for model in data.get('models', []):
        print(f'Model: {model.get(\"id\", \"unknown\")}')
        print(f'  Owner: {model.get(\"owned_by\", \"unknown\")}')
        print(f'  Max tokens: {model.get(\"maxInputTokens\", \"unknown\")}')
        print()
else:
    print('Error:', data.get('error', 'Unknown'))
"
```

### Проблемы с RAG
```bash
# Тест RAG поиска
curl -X POST http://localhost:8002/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 1}' | python -c "
import sys, json
data = json.load(sys.stdin)
results = data.get('results', [])
print(f'RAG results: {len(results)}')
if results:
    print(f'First result: {results[0].get(\"source\", \"unknown\")}')
"
```

---

## 📝 Примеры для разработки

### Тестирование новых функций
```bash
# Шаблон для тестирования нового endpoint
curl -X POST http://localhost:8002/api/v1/NEW_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{"param": "value"}' \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"

# Сохранение ответа в файл для анализа
curl -s http://localhost:8002/api/v1/health > health_response.json
```

### Автоматизация тестов
```bash
# Создать простой тест-скрипт
cat > test_api.sh << 'EOF'
#!/bin/bash
echo "Testing FastAPI Foundry..."
echo "1. Health check:"
curl -s http://localhost:8002/api/v1/health | grep -o '"status":"[^"]*"'
echo "2. Models count:"
curl -s http://localhost:8002/api/v1/models | python -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('models', [])))"
echo "3. Simple generation:"
curl -s -X POST http://localhost:8002/api/v1/generate -H "Content-Type: application/json" -d '{"prompt":"Hi","max_tokens":10}' | python -c "import sys, json; data=json.load(sys.stdin); print('✅' if data.get('success') else '❌')"
echo "Done!"
EOF

chmod +x test_api.sh
./test_api.sh
```

---

**💡 Совет:** Используйте `| python -m json.tool` для красивого форматирования JSON ответов, или `| jq` если установлен jq.

**⚠️ Внимание:** Некоторые запросы к генерации могут занимать до 60 секунд, особенно при первом запуске модели.

---

## 👨💻 Навигация по разделу "Разработка"

| Документ | Описание |
|----------|----------|
| [🛠️ Разработка](development.md) | Архитектура и добавление функций |
| [🔧 cURL команды](curl_commands.md) | API тестирование и отладка |
| [📋 Информация о проекте](project_info.md) | Детальная информация |

## 🔗 Другие разделы

| Раздел | Документы |
|--------|-----------||
| **📚 Начало работы** | [📦 Установка](installation.md) • [🚀 Запуск](running.md) • [🎯 Лончеры](launchers.md) • [📚 Использование](usage.md) • [⚙️ Настройка](configuration.md) |
| **🛠️ Практика** | [📊 Примеры](examples.md) • [🛠️ Рецепты](howto.md) |
| **🌐 Интеграция** | [🔌 MCP](mcp_integration.md) • [🌍 Туннели](tunnel_guide.md) |
| **🚀 Развертывание** | [🐳 Docker](docker.md) • [🚀 Deployment](deployment.md) |

---

**📚 Быстрые ссылки:** [⬅️ Назад к оглавлению](README.md) | [📚 Все документы](README.md#-документация)

**FastAPI Foundry** - часть экосистемы AiStros  
© 2025 AiStros Team