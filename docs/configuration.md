# ⚙️ Настройка

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

## 📚 Что дальше?

### ✅ Конфигурация настроена! Следующие шаги:

1. **[📊 Примеры](examples.md)** - Готовые примеры кода
2. **[📝 Практические рецепты](howto.md)** - Настройка RAG, подключение моделей
3. **[🌐 Туннели](tunnel_guide.md)** - Публичный доступ
4. **[🚀 Развертывание](deployment.md)** - Production развертывание

### 🔗 Полезные ссылки:
- **[🎯 Лончеры](launchers.md)** - Полное руководство по лончерам
- **[🔧 Разработка](development.md)** - Для разработчиков
- **[📊 Проект](project_info.md)** - Детальная информация

### 🔍 Проверка настроек:
```bash
# Проверка .env файла
cat .env | grep -E "^[A-Z]"

# Проверка config.json
python -c "import json; print(json.load(open('src/config.json'))['fastapi_server']['port'])"

# Тест конфигурации
python -c "from src.core.config import settings; print(f'API Port: {settings.api_port}')"

# Проверка Foundry подключения
curl http://localhost:50477/v1/models
```