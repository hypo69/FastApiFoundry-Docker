# 🔌 MCP Интеграция

FastAPI Foundry включает встроенный MCP (Model Context Protocol) сервер для интеграции с Claude Desktop и другими MCP клиентами.

## 🚀 Что такое MCP?

MCP (Model Context Protocol) - это протокол для подключения AI ассистентов к внешним инструментам и данным. Позволяет Claude Desktop и другим AI клиентам использовать ваши локальные модели Foundry.

## 📦 Встроенный MCP сервер

FastAPI Foundry включает готовый MCP сервер: `mcp-servers/aistros-foundry/`

### 🛠️ Возможности:
- **generate_text** - генерация текста через Foundry модели
- **generate_horoscope_foundry** - создание гороскопов
- **list_foundry_models** - список доступных моделей
- **get_foundry_status** - статус Foundry сервиса

## ⚙️ Настройка Claude Desktop

### 1. Найти конфигурационный файл:
```bash
# Windows
%APPDATA%\Claude\claude_desktop_config.json

# macOS
~/Library/Application Support/Claude/claude_desktop_config.json

# Linux
~/.config/Claude/claude_desktop_config.json
```

### 2. Добавить MCP сервер:
```json
{
  "mcpServers": {
    "aistros-foundry": {
      "command": "python",
      "args": ["mcp-servers/aistros-foundry/src/server.py"],
      "cwd": "C:/path/to/FastApiFoundry",
      "env": {
        "FOUNDRY_BASE_URL": "http://localhost:51601/v1/",
        "FOUNDRY_DEFAULT_MODEL": "deepseek-r1-distill-qwen-7b-generic-cpu:3"
      }
    }
  }
}
```

### 3. Перезапустить Claude Desktop

## 🚀 Использование в Claude

После настройки в Claude Desktop будут доступны инструменты:

```
Привет! Можешь сгенерировать текст через мою локальную Foundry модель?

Claude будет использовать:
- generate_text() для генерации
- get_foundry_status() для проверки статуса
- list_foundry_models() для выбора модели
```

## 🔧 Запуск MCP сервера отдельно

```bash
# Установить зависимости
cd mcp-servers/aistros-foundry
pip install -r requirements.txt

# Настроить конфигурацию
cp .env.example .env

# Запустить MCP сервер
python src/server.py
```

## 🌐 Интеграция с FastAPI Foundry

MCP сервер автоматически запускается вместе с FastAPI Foundry:

```bash
# Запуск с MCP
python run.py --dev --ssl --mcp --auto-port

# FastAPI: https://localhost:8443
# MCP Console: https://localhost:8765
# MCP Server: доступен через stdio для Claude Desktop
```

## 📋 Преимущества MCP интеграции

- **Локальные модели** в Claude Desktop
- **Приватность** - данные не покидают ваш компьютер
- **Бесплатно** - нет затрат на API
- **Кастомизация** - настройка под ваши задачи
- **Интеграция** с другими MCP серверами (WordPress, MariaDB, SSH)

---

**MCP Integration** - часть экосистемы AiStros  
© 2025 AiStros Team