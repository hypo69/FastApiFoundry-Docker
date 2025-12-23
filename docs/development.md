# 🛠️ Руководство для разработчиков

---
**📚 Навигация:** [🏠 Главная](README.md) | [📦 Установка](installation.md) | [🚀 Запуск](running.md) | [🎯 Лончеры](launchers.md) | [📖 Использование](usage.md) | [⚙️ Настройка](configuration.md) | [📊 Примеры](examples.md) | [🛠️ Рецепты](howto.md) | [🔌 MCP](mcp_integration.md) | [🌍 Туннели](tunnel_guide.md) | [🐳 Docker](docker.md) | [🛠️ Разработка](development.md) | [🚀 Развертывание](deployment.md) | [🔧 cURL](curl_commands.md) | [📋 Проект](project_info.md)
---

## 📁 Архитектура проекта

```
FastApiFoundry/
├── src/                    # Исходный код
│   ├── api/               # FastAPI приложение
│   │   ├── endpoints/     # API endpoints
│   │   ├── middleware/    # Middleware
│   │   ├── app.py        # Фабрика приложения
│   │   ├── main.py       # Точка входа
│   │   └── models.py     # Pydantic модели
│   ├── core/             # Основная логика
│   │   └── config.py     # Конфигурация
│   ├── models/           # AI модели
│   │   ├── foundry_client.py
│   │   └── model_manager.py
│   ├── rag/              # RAG система
│   │   └── rag_system.py
│   └── utils/            # Утилиты
├── docs/                 # Документация
├── static/              # Веб-интерфейс
├── run.py              # Скрипт запуска
└── requirements.txt    # Зависимости
```

## 🔧 Добавление новых endpoints

### 1. Создайте новый роутер
```python
# src/api/endpoints/my_feature.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/my-feature",
    tags=["My Feature"]
)

@router.get("/my-endpoint")
async def my_endpoint():
    """Краткое описание вашего эндпоинта."""
    return {"message": "Hello from My Feature"}
```

### 2. Подключите роутер в `src/api/app.py`
```python
# src/api/app.py
from .endpoints import main, rag, models, health, my_feature # 1. Импортируйте ваш роутер

# ...

def create_app():
    # ...
    app.include_router(main.router)
    app.include_router(rag.router)
    app.include_router(models.router)
    app.include_router(health.router)
    app.include_router(my_feature.router) # 2. Подключите его

    return app
```

## 🧪 Тестирование

Для тестирования используется `pytest`.

### Запуск тестов
```bash
# Убедитесь, что вы в активированном venv
pytest
```

### Создание тестов
Создайте файл `tests/test_my_feature.py`.

```python
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_my_endpoint():
    response = client.get("/api/v1/my-feature/my-endpoint")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from My Feature"}
```

## 📦 Добавление зависимостей

1.  Добавьте новую зависимость в файл `requirements.txt`.
2.  Переустановите зависимости: `pip install -r requirements.txt`.
3.  Если вы используете Docker, пересоберите образ: `docker-compose up --build -d`.
4.  Не забудьте задокументировать новую зависимость и причину ее добавления.

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