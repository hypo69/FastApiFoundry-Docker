# 🚀 AiStros Foundry MCP Server

MCP (Model Context Protocol) сервер для работы с Microsoft Foundry локальными AI моделями.

## 🎯 Возможности

- **Генерация текста** через локальные модели (DeepSeek, Qwen, Mistral, Llama)
- **Генерация гороскопов** с астрологическим контекстом
- **Управление моделями** - список доступных моделей
- **Статус сервиса** - проверка работоспособности Foundry
- **Оценка токенов** - подсчет использования

## 🔧 Установка

```bash
# Установить зависимости
pip install -r requirements.txt

# Скопировать конфигурацию
cp .env.example .env

# Отредактировать настройки
nano .env
```

## ⚙️ Конфигурация

### Переменные окружения (.env):

```env
FOUNDRY_BASE_URL=http://localhost:51601/v1/
FOUNDRY_DEFAULT_MODEL=deepseek-r1-distill-qwen-7b-generic-cpu:3
FOUNDRY_TEMPERATURE=0.6
FOUNDRY_MAX_TOKENS=2048
FOUNDRY_TIMEOUT=30
```

## 🚀 Запуск

### Как MCP сервер:
```bash
python src/server.py
```

### Через Claude Desktop:
Добавить в `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aistros-foundry": {
      "command": "python",
      "args": ["path/to/mcp-servers/aistros-foundry/src/server.py"],
      "env": {
        "FOUNDRY_BASE_URL": "http://localhost:51601/v1/"
      }
    }
  }
}
```

## 🛠️ Доступные инструменты

### generate_text
Генерация текста через Foundry модели:
```python
generate_text(
    prompt="Write a poem about AI",
    model="deepseek-r1-distill-qwen-7b-generic-cpu:3",
    temperature=0.8,
    max_tokens=500
)
```

### generate_horoscope_foundry
Генерация гороскопов:
```python
generate_horoscope_foundry(
    zodiac_sign="Aries",
    date="2025-01-15", 
    horoscope_type="daily",
    language="en"
)
```

### list_foundry_models
Список доступных моделей:
```python
list_foundry_models()
```

### get_foundry_status
Статус Foundry сервиса:
```python
get_foundry_status()
```

## 🔗 Интеграция с FastAPI Foundry

Этот MCP сервер предназначен для работы с [FastAPI Foundry](../../README.md):

```bash
# Запустить FastAPI Foundry с MCP
python run.py --dev --ssl --mcp --auto-port

# MCP сервер будет доступен через FastAPI Foundry
```

## 📋 Требования

- **Python**: 3.8+
- **Foundry CLI**: Установлен и настроен
- **MCP**: Model Context Protocol support

## 🔍 Устранение неполадок

### Foundry не запускается:
```bash
# Проверить статус
foundry service status

# Запустить вручную
foundry service start
```

### Модели не загружаются:
```bash
# Проверить доступные модели
foundry models list

# Скачать модель
foundry models pull deepseek-r1-distill-qwen-7b-generic-cpu:3
```

### Ошибки подключения:
- Проверить `FOUNDRY_BASE_URL` в .env
- Убедиться что Foundry service запущен
- Проверить порт (по умолчанию 51601)

---

**AiStros Foundry MCP Server** - часть экосистемы AiStros  
© 2025 AiStros Team