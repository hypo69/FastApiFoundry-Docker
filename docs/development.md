# 🛠️ Руководство для разработчиков

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

router = APIRouter()

@router.get("/my-endpoint")
async def my_endpoint():
    return {"message": "Hello"}
```

### 2. Подключите в app.py
```python
from .endpoints import my_feature

app.include_router(my_feature.router, prefix="/api/v1")
```

## 🧪 Тестирование

### Запуск тестов
```bash
pytest tests/
```

### Создание тестов
```python
def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
```

## 📦 Добавление зависимостей

1. Добавьте в `requirements.txt`
2. Обновите Docker образ
3. Документируйте изменения