# ⚙️ Настройка

> **Предыдущие шаги**: [📦 Установка](installation.md) → [🚀 Запуск](running.md) → [📖 Использование](usage.md)

## Создание конфигурации

```bash
cp .env.example .env
```

## Основные параметры

### Режим работы
```env
# Режим по умолчанию (dev/prod)
DEFAULT_MODE=dev
```

### Foundry настройки
```env
FOUNDRY_BASE_URL=http://localhost:51601/v1/
FOUNDRY_DEFAULT_MODEL=deepseek-r1-distill-qwen-7b-generic-cpu:3
FOUNDRY_TEMPERATURE=0.6
FOUNDRY_MAX_TOKENS=2048
```

### API настройки
```env
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1
API_KEY=your-secret-key
```

### RAG система
```env
RAG_ENABLED=true
RAG_INDEX_DIR=./rag_index
RAG_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### CORS и безопасность
```env
CORS_ORIGINS=["*"]
LOG_LEVEL=INFO
LOG_FILE=logs/fastapi-foundry.log
```

## Настройка для продакшн

```env
DEFAULT_MODE=prod
API_KEY=strong-random-key-here
CORS_ORIGINS=["https://yourdomain.com"]
LOG_LEVEL=WARNING
```

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

# Тест конфигурации
python -c "from src.core.config import settings; print(f'API Port: {settings.api_port}')"

# Проверка Foundry подключения
curl http://localhost:51601/v1/models
```