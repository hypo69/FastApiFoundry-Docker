# ⚙️ Настройка

---
**📚 Навигация:** [🏠 Главная](README.md) | [📦 Установка](installation.md) | [🚀 Запуск](running.md) | [🎯 Лончеры](launchers.md) | [📖 Использование](usage.md) | [⚙️ Настройка](configuration.md) | [📊 Примеры](examples.md) | [🛠️ Рецепты](howto.md) | [🔌 MCP](mcp_integration.md) | [🌍 Туннели](tunnel_guide.md) | [🐳 Docker](docker.md) | [🛠️ Разработка](development.md) | [🚀 Развертывание](deployment.md) | [🔧 cURL](curl_commands.md) | [📋 Проект](project_info.md)
---

> **Предыдущие шаги**: [📦 Установка](installation.md) → [🚀 Запуск](running.md) → [📖 Использование](usage.md)

## 📁 Структура конфигурации

**FastAPI Foundry использует разделение конфигураций:**

- **`.env`** - чувствительные данные (API ключи, пароли, URL)
- **`src/config.json`** - настройки приложения (порты, параметры, опции)

### Создание конфигурации

```bash
# Основная конфигурация
cp .env.example .env

# Чувствительные данные (опционально)
cp .env.sensitive .env.production
```

## 🔐 Чувствительные данные (.env)

### API безопасность
```env
API_KEY=your-secret-api-key
```

### Foundry подключение
```env
FOUNDRY_BASE_URL=http://localhost:50477/v1/
FOUNDRY_DEFAULT_MODEL=deepseek-r1-distill-qwen-7b-generic-cpu:3
FOUNDRY_TIMEOUT=300
```

### MCP Server
```env
MCP_FOUNDRY_BASE_URL=http://localhost:51601/v1/
MCP_FOUNDRY_DEFAULT_MODEL=deepseek-r1-distill-qwen-7b-generic-cpu:3
MCP_FOUNDRY_TIMEOUT=30
```

### SSL/TLS
```env
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
```

## ⚙️ Настройки приложения (src/config.json)

### FastAPI Server
```json
{
  "fastapi_server": {
    "host": "0.0.0.0",
    "port": 8002,
    "mode": "dev",
    "workers": 1,
    "reload": true
  }
}
```

### Foundry AI параметры
```json
{
  "foundry_ai": {
    "temperature": 0.6,
    "top_p": 0.9,
    "top_k": 40,
    "max_tokens": 2048
  }
}
```

### RAG система
```json
{
  "rag_system": {
    "enabled": true,
    "index_dir": "./rag_index",
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "chunk_size": 1000
  }
}
```

## 🔒 Настройка для продакшн

### Чувствительные данные (.env)
```env
API_KEY=strong-random-key-here
FOUNDRY_BASE_URL=https://your-foundry-server.com/v1/
SSL_CERT_PATH=/etc/ssl/certs/server.crt
SSL_KEY_PATH=/etc/ssl/private/server.key
```

### Настройки приложения (conf.json)
```json
{
  "fastapi_server": {
    "mode": "production",
    "port": 8002,
    "workers": 4,
    "reload": false,
    "cors_origins": ["https://yourdomain.com"]
  }
}
```

## ⚠️ Безопасность

**Никогда не коммитьте чувствительные данные:**

```bash
# Добавьте в .gitignore
echo ".env.production" >> .gitignore
echo ".env.sensitive" >> .gitignore
```

**Безопасно коммитить:**
- `conf.json` - настройки приложения
- `.env.example` - пример конфигурации

## 🔒 HTTPS настройка

### Самоподписанные сертификаты (для разработки)

Сертификаты автоматически создаются в `~/.ssh/`:
- `~/.ssh/server.key` - приватный ключ
- `~/.ssh/server.crt` - публичный сертификат

### Запуск с HTTPS

```bash
# Использовать сертификаты по умолчанию
python run.py --ssl

# Указать свои сертификаты
python run.py --ssl-keyfile server.key --ssl-certfile server.crt
```

### Production сертификаты

Для production используйте сертификаты от авторитетного центра:
- Let's Encrypt (бесплатно)
- DigiCert
- GlobalSign

```bash
python run.py --prod --ssl-keyfile production.key --ssl-certfile production.crt
```

---

## 📖 Навигация по разделу "Начало работы"

| Документ | Описание |
|----------|----------|
| [📦 Установка](installation.md) | Системные требования и установка |
| [🚀 Запуск](running.md) | Основные способы запуска |
| [🎯 Лончеры](launchers.md) | Детальное руководство по лончерам |
| [📖 Использование](usage.md) | Веб-интерфейс и REST API |
| [⚙️ Настройка](configuration.md) | Конфигурация через .env |

## 🔗 Другие разделы

| Раздел | Документы |
|--------|-----------|
| **🛠️ Практика** | [📊 Примеры](examples.md) • [🛠️ Рецепты](howto.md) |
| **🌐 Интеграция** | [🔌 MCP](mcp_integration.md) • [🌍 Туннели](tunnel_guide.md) |
| **🚀 Развертывание** | [🐳 Docker](docker.md) • [🚀 Deployment](deployment.md) |
| **👨‍💻 Разработка** | [🛠️ Development](development.md) • [🔧 cURL](curl_commands.md) • [📋 Проект](project_info.md) |

---

**📚 Быстрые ссылки:** [⬅️ Назад к оглавлению](README.md) | [📖 Все документы](README.md#-документация)

**FastAPI Foundry** - часть экосистемы AiStros  
© 2025 AiStros Team