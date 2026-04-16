# 🧠 RAG Training Guide - Обучение моделей с RAG

**Версия:** 0.2.1  
**Проект:** FastApiFoundry (Docker)  
**Дата:** 9 декабря 2025  

---

## 🎯 Что такое RAG?

**RAG (Retrieval-Augmented Generation)** - это техника, которая позволяет AI моделям использовать внешние знания из документов для генерации более точных и релевантных ответов.

### Как это работает:
1. **Индексация** - документы разбиваются на chunks и индексируются
2. **Поиск** - по запросу находятся релевантные chunks
3. **Генерация** - модель использует найденную информацию для ответа

---

## 🚀 Быстрый старт

### 1. Настройка RAG системы

```python
# SANDBOX/sdk/rag_basic.py
import requests
import json

API_BASE = "http://localhost:9696/api/v1"

# Настройка RAG
config = {
    "enabled": True,
    "index_dir": "./rag_index",
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "chunk_size": 1000,
    "top_k": 5
}

response = requests.put(f"{API_BASE}/rag/config", json=config)
print("RAG настроен:", response.json())
```

### 2. Добавление документов

```python
# SANDBOX/sdk/rag_add_docs.py
import os
from pathlib import Path

def add_documents_to_rag():
    """Добавляем документы в RAG индекс"""
    
    # Создаем директорию для документов
    docs_dir = Path("./rag_docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Пример документа
    doc_content = """
    FastAPI Foundry - это REST API для работы с локальными AI моделями.
    
    Основные возможности:
    - Генерация текста через Foundry
    - RAG система для поиска в документах
    - Веб-интерфейс для управления
    - MCP сервер для интеграции
    
    Для запуска используйте: python run.py
    """
    
    with open(docs_dir / "fastapi_foundry.txt", "w", encoding="utf-8") as f:
        f.write(doc_content)
    
    print("✅ Документы добавлены в ./rag_docs/")

if __name__ == "__main__":
    add_documents_to_rag()
```

### 3. Поиск с RAG

```python
# SANDBOX/sdk/rag_search.py
import requests

def search_with_rag(query):
    """Поиск информации через RAG"""
    
    response = requests.post(
        "http://localhost:9696/api/v1/rag/search",
        json={"query": query, "top_k": 3}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            print(f"🔍 Найдено {len(data['results'])} результатов:")
            for i, result in enumerate(data["results"], 1):
                print(f"\n{i}. Score: {result['score']:.3f}")
                print(f"   Content: {result['content'][:200]}...")
        else:
            print("❌ Ошибка поиска:", data["error"])
    else:
        print("❌ Ошибка запроса:", response.status_code)

# Примеры поиска
search_with_rag("Как запустить FastAPI Foundry?")
search_with_rag("Что такое RAG система?")
```

---

## 🛠️ Продвинутые примеры

### 1. Генерация с контекстом RAG

```python
# SANDBOX/sdk/rag_generate.py
import requests

def generate_with_rag_context(question):
    """Генерация ответа с использованием RAG контекста"""
    
    # 1. Поиск релевантной информации
    search_response = requests.post(
        "http://localhost:9696/api/v1/rag/search",
        json={"query": question, "top_k": 3}
    )
    
    context = ""
    if search_response.status_code == 200:
        search_data = search_response.json()
        if search_data["success"]:
            context = "\n".join([r["content"] for r in search_data["results"]])
    
    # 2. Формируем промпт с контекстом
    prompt = f"""
Контекст из документации:
{context}

Вопрос: {question}

Ответь на вопрос, используя информацию из контекста выше.
"""
    
    # 3. Генерируем ответ
    generate_response = requests.post(
        "http://localhost:9696/api/v1/generate",
        json={
            "prompt": prompt,
            "max_tokens": 500,
            "temperature": 0.7
        }
    )
    
    if generate_response.status_code == 200:
        gen_data = generate_response.json()
        if gen_data["success"]:
            print("🤖 Ответ с RAG контекстом:")
            print(gen_data["content"])
        else:
            print("❌ Ошибка генерации:", gen_data["error"])
    else:
        print("❌ Ошибка запроса генерации")

# Пример использования
generate_with_rag_context("Как настроить RAG в FastAPI Foundry?")
```

### 2. Пакетная обработка документов

```python
# SANDBOX/sdk/rag_batch_process.py
import requests
import os
from pathlib import Path

def process_directory_to_rag(directory_path):
    """Обрабатываем все файлы в директории для RAG"""
    
    directory = Path(directory_path)
    if not directory.exists():
        print(f"❌ Директория {directory_path} не найдена")
        return
    
    processed_files = []
    
    # Обрабатываем все текстовые файлы
    for file_path in directory.rglob("*.txt"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Здесь можно добавить логику индексации
            # Пока просто сохраняем информацию о файле
            processed_files.append({
                "file": str(file_path),
                "size": len(content),
                "chunks": len(content) // 1000 + 1
            })
            
        except Exception as e:
            print(f"⚠️ Ошибка обработки {file_path}: {e}")
    
    print(f"✅ Обработано {len(processed_files)} файлов:")
    for file_info in processed_files:
        print(f"  📄 {file_info['file']} ({file_info['chunks']} chunks)")

# Обрабатываем документацию проекта
process_directory_to_rag("./docs")
```

### 3. Мониторинг RAG системы

```python
# SANDBOX/sdk/rag_monitor.py
import requests
import time

def monitor_rag_system():
    """Мониторинг состояния RAG системы"""
    
    while True:
        try:
            response = requests.get("http://localhost:9696/api/v1/rag/status")
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    print(f"📊 RAG Status: {'✅ Enabled' if data['enabled'] else '❌ Disabled'}")
                    print(f"📁 Index: {data['index_dir']}")
                    print(f"🤖 Model: {data['model']}")
                    print(f"📄 Chunks: {data['total_chunks']}")
                    print(f"🔍 Top-K: {data['top_k']}")
                else:
                    print("❌ Ошибка получения статуса:", data["error"])
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
        
        print("-" * 50)
        time.sleep(30)  # Проверяем каждые 30 секунд

if __name__ == "__main__":
    monitor_rag_system()
```

---

## 📚 Практические сценарии

### 1. Техническая поддержка

```python
# Создаем базу знаний для поддержки
support_docs = {
    "installation.txt": "Инструкции по установке FastAPI Foundry...",
    "troubleshooting.txt": "Решение типичных проблем...",
    "api_reference.txt": "Документация по API endpoints..."
}

# Пользователь задает вопрос
user_question = "Как исправить ошибку 405 Method Not Allowed?"

# RAG находит релевантную информацию и генерирует ответ
```

### 2. Анализ кода

```python
# Индексируем исходный код проекта
code_files = ["src/api/app.py", "src/models/foundry_client.py", "src/rag/rag_system.py"]

# Вопросы по коду
questions = [
    "Как работает инициализация приложения?",
    "Какие endpoints доступны в API?",
    "Как настроить RAG систему?"
]
```

### 3. Обучение новых сотрудников

```python
# База знаний компании
knowledge_base = [
    "company_policies.txt",
    "development_guidelines.txt", 
    "project_architecture.txt"
]

# Новый сотрудник может задавать вопросы
onboarding_questions = [
    "Какие правила разработки в компании?",
    "Как устроена архитектура проекта?",
    "Где найти документацию по API?"
]
```

---

## ⚙️ Настройка и оптимизация

### Выбор модели эмбеддингов

```python
# Разные модели для разных задач
models = {
    "fast": "sentence-transformers/all-MiniLM-L6-v2",  # Быстрая
    "quality": "sentence-transformers/all-mpnet-base-v2",  # Качественная
    "multilingual": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  # Многоязычная
}
```

### Оптимизация размера chunks

```python
# Разные размеры для разных типов документов
chunk_sizes = {
    "code": 500,      # Код - маленькие chunks
    "docs": 1000,     # Документация - средние
    "articles": 2000  # Статьи - большие
}
```

---

## 🔧 Интеграция с веб-интерфейсом

Все функции RAG доступны через веб-интерфейс:

1. **Вкладка RAG** - настройка системы
2. **Вкладка Chat** - чат с RAG контекстом  
3. **Вкладка Examples** - запуск SDK примеров

---

## 📖 Дополнительные ресурсы

- [API Documentation](../api/) - Полная документация API
- [SDK Examples](../../SANDBOX/sdk/) - Готовые примеры кода
- [Configuration Guide](configuration.md) - Настройка системы

---

**💡 Совет:** Начните с простых примеров из `SANDBOX/sdk/` и постепенно переходите к более сложным сценариям!