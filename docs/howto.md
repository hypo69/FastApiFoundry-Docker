# 🛠️ Практические рецепты

---
**📚 Навигация:** [🏠 Главная](README.md) | [📦 Установка](installation.md) | [🚀 Запуск](running.md) | [🎯 Лончеры](launchers.md) | [📖 Использование](usage.md) | [⚙️ Настройка](configuration.md) | [📊 Примеры](examples.md) | [🛠️ Рецепты](howto.md) | [🔌 MCP](mcp_integration.md) | [🌍 Туннели](tunnel_guide.md) | [🐳 Docker](docker.md) | [🛠️ Разработка](development.md) | [🚀 Развертывание](deployment.md) | [🔧 cURL](curl_commands.md) | [📋 Проект](project_info.md)
---

## Настройка RAG системы

### Создание индекса из директории
Вы можете создать или пересоздать RAG-индекс из любой директории с текстовыми файлами (.md, .txt).

```bash
# Замените ../docs на путь к вашей директории
python -c "
from src.rag.rag_system import rag_system
import asyncio
print('Создание индекса из директории ../docs...')
asyncio.run(rag_system.create_index_from_directory('../docs'))
print('Индекс успешно создан.')
"
```

### Перезагрузка индекса через API
Если вы обновили файлы в RAG-индексе, его можно перезагрузить без перезапуска сервера.

```bash
curl -X POST http://localhost:8000/api/v1/rag/reload
```

## Подключение моделей

Вы можете динамически подключать новые AI-модели от разных провайдеров.

### Подключение модели OpenAI (например, GPT-4)

```bash
curl -X POST http://localhost:8000/api/v1/models/connect \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "gpt-4",
    "provider": "openai",
    "model_name": "GPT-4",
    "endpoint_url": "https://api.openai.com/v1/",
    "api_key": "sk-your-openai-api-key"
  }'
```

### Подключение локальной модели Ollama

```bash
curl -X POST http://localhost:8000/api/v1/models/connect \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "llama3",
    "provider": "ollama",
    "model_name": "Llama 3",
    "endpoint_url": "http://localhost:11434"
  }'
```
*Примечание: Убедитесь, что Ollama сервер запущен и доступен по указанному адресу.*

## Автоматизация и автозапуск

### Systemd сервис для автозапуска (Linux)
Создайте файл `/etc/systemd/system/fastapi-foundry.service` для автоматического запуска сервера при старте системы.

```ini
[Unit]
Description=FastAPI Foundry Server
After=network.target

[Service]
Type=simple
User=your_user # Замените на вашего пользователя
Group=your_user # Замените на вашу группу
WorkingDirectory=/path/to/FastApiFoundry-Docker # Путь к проекту
ExecStart=/path/to/FastApiFoundry-Docker/venv/bin/python run.py --prod
Restart=always

[Install]
WantedBy=multi-user.target
```
**Активация:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable fastapi-foundry
sudo systemctl start fastapi-foundry
```

### Docker автозапуск
Для автоматического запуска контейнера при старте системы используйте `restart: unless-stopped` в `docker-compose.yml`.

```yaml
services:
  fastapi-foundry:
    # ...
    restart: unless-stopped
    # ...
```
Запустите командой: `docker-compose up -d`.

## Мониторинг

### Проверка здоровья через cURL
Простой способ проверить, что все компоненты системы работают.

```bash
curl -s http://localhost:8000/api/v1/health | python -m json.tool
```

Ожидаемый ответ:
```json
{
    "status": "healthy",
    "foundry_status": "healthy",
    "rag_loaded": true,
    "rag_chunks": 150,
    "timestamp": "..."
}
```

---
## 🛠️ Навигация по разделу "Практика"

| Документ | Описание |
|----------|----------|
| [📊 Примеры](examples.md) | Готовые примеры кода и сценарии |
| [🛠️ Рецепты](howto.md) | Практические рецепты и настройки |

## 🔗 Другие разделы

| Раздел | Документы |
|--------|-----------|
| **📖 Начало работы** | [📦 Установка](installation.md) • [🚀 Запуск](running.md) • [🎯 Лончеры](launchers.md) • [📖 Использование](usage.md) • [⚙️ Настройка](configuration.md) |
| **🌐 Интеграция** | [🔌 MCP](mcp_integration.md) • [🌍 Туннели](tunnel_guide.md) |
| **🚀 Развертывание** | [🐳 Docker](docker.md) • [🚀 Deployment](deployment.md) |
| **👨‍💻 Разработка** | [🛠️ Development](development.md) • [🔧 cURL](curl_commands.md) • [📋 Проект](project_info.md) |

---

**📚 Быстрые ссылки:** [⬅️ Назад к оглавлению](README.md) | [📖 Все документы](README.md#-документация)

**FastAPI Foundry** - часть экосистемы AiStros  
© 2025 AiStros Team