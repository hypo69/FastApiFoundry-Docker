# 💡 Примеры использования SDK

Практические примеры работы с FastAPI Foundry SDK.

---

## 🚀 Базовые примеры

### Простая генерация текста

```python
from sdk import FoundryClient

with FoundryClient("http://localhost:9696") as client:
    response = client.generate("Расскажи о FastAPI")
    
    if response.success:
        print("Ответ:", response.content)
        print("Модель:", response.model_used)
        print("Токенов:", response.tokens_used)
    else:
        print("Ошибка:", response.error)
```

### Проверка системы перед работой

```python
with FoundryClient() as client:
    # Проверяем доступность
    if not client.is_alive():
        print("API недоступен")
        exit(1)
    
    # Ждем готовности
    if not client.wait_for_ready(max_wait=30):
        print("API не готов к работе")
        exit(1)
    
    # Проверяем здоровье
    health = client.health()
    print(f"Статус: {health.status}")
    print(f"Foundry: {health.foundry_status}")
    print(f"Моделей: {health.models_count}")
```

---

## 🤖 Работа с моделями

### Выбор и загрузка модели

```python
with FoundryClient() as client:
    # Список всех моделей
    all_models = client.list_models()
    print("Доступные модели:")
    for model in all_models:
        print(f"  {model.id} - {model.status}")
    
    # Подключенные модели
    connected = client.get_connected_models()
    if not connected:
        print("Нет подключенных моделей")
        
        # Загружаем первую доступную
        if all_models:
            model_to_load = all_models[0].id
            print(f"Загружаем модель: {model_to_load}")
            
            if client.load_model(model_to_load):
                print("Модель загружена успешно")
            else:
                print("Ошибка загрузки модели")
```

### Генерация с конкретной моделью

```python
with FoundryClient() as client:
    response = client.generate(
        prompt="Объясни машинное обучение простыми словами",
        model="deepseek-r1-distill-qwen-7b-generic-cpu:3",
        temperature=0.7,
        max_tokens=300,
        system_prompt="Ты - учитель, объясняющий сложные темы простым языком"
    )
    
    if response.success:
        print("Объяснение ML:")
        print(response.content)
```

---

## 💬 Чат с сессиями

### Простой чат

```python
import uuid

with FoundryClient() as client:
    session_id = str(uuid.uuid4())
    
    # Первое сообщение
    response1 = client.chat(
        message="Привет! Меня зовут Алекс",
        conversation_id=session_id
    )
    print("AI:", response1.content)
    
    # Продолжение разговора
    response2 = client.chat(
        message="Как меня зовут?",
        conversation_id=session_id
    )
    print("AI:", response2.content)  # Должен помнить имя
```

### Чат с RAG контекстом

```python
with FoundryClient() as client:
    # Поиск в документации
    rag_results = client.rag_search("Docker installation", top_k=3)
    print(f"Найдено {len(rag_results)} релевантных документов")
    
    # Вопрос с использованием RAG
    response = client.chat(
        message="Как установить Docker согласно документации?",
        use_rag=True
    )
    
    if response.success:
        print("Ответ с RAG:", response.content)
        if response.rag_sources:
            print("Источники:", ", ".join(response.rag_sources))
```

---

## 📦 Пакетная обработка

### Обработка множественных запросов

```python
with FoundryClient() as client:
    questions = [
        "Что такое FastAPI?",
        "Как работает Docker?",
        "Объясни REST API",
        "Что такое микросервисы?",
        "Как настроить CI/CD?"
    ]
    
    print("Обрабатываем пакет вопросов...")
    responses = client.batch_generate(
        prompts=questions,
        max_tokens=150,
        temperature=0.5,
        use_rag=True
    )
    
    for i, (question, response) in enumerate(zip(questions, responses), 1):
        print(f"\n{i}. {question}")
        if response.success:
            print(f"Ответ: {response.content}")
        else:
            print(f"Ошибка: {response.error}")
```

### Параллельная обработка с разными параметрами

```python
import concurrent.futures

def process_prompt(client, prompt, **kwargs):
    return client.generate(prompt, **kwargs)

with FoundryClient() as client:
    tasks = [
        ("Техническое объяснение AI", {"temperature": 0.3, "max_tokens": 200}),
        ("Креативная история о роботах", {"temperature": 0.9, "max_tokens": 300}),
        ("Краткое резюме по ML", {"temperature": 0.1, "max_tokens": 100})
    ]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(process_prompt, client, prompt, **kwargs)
            for prompt, kwargs in tasks
        ]
        
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            response = future.result()
            print(f"\nЗадача {i}:")
            print(response.content if response.success else response.error)
```

---

## 🔍 RAG система

### Поиск и анализ документации

```python
with FoundryClient() as client:
    # Поиск по ключевым словам
    search_queries = [
        "Docker configuration",
        "FastAPI setup",
        "API endpoints",
        "error handling"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Поиск: '{query}'")
        results = client.rag_search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['source']} (релевантность: {result['score']:.3f})")
            print(f"     {result['text'][:100]}...")
```

### Очистка и перезагрузка RAG

```python
with FoundryClient() as client:
    # Проверяем статус RAG
    rag_status = client.rag_status()
    print(f"RAG загружен: {rag_status.get('loaded', False)}")
    print(f"Количество чанков: {rag_status.get('chunks_count', 0)}")
    
    # Очищаем индекс
    if client.rag_clear():
        print("✅ RAG индекс очищен")
        
        # Перезагружаем
        if client.rag_reload():
            print("✅ RAG индекс перезагружен")
        else:
            print("❌ Ошибка перезагрузки RAG")
    else:
        print("❌ Ошибка очистки RAG")
```

---

## ⚙️ Конфигурация и мониторинг

### Управление конфигурацией

```python
with FoundryClient() as client:
    # Получаем текущую конфигурацию
    config = client.get_config()
    print("Текущая конфигурация:")
    print(f"  Foundry URL: {config.get('foundry_ai', {}).get('base_url')}")
    print(f"  RAG включен: {config.get('rag_system', {}).get('enabled')}")
    
    # Устанавливаем модель по умолчанию
    new_model = "deepseek-r1-distill-qwen-7b-generic-cpu:3"
    if client.set_default_model(new_model):
        print(f"✅ Модель по умолчанию: {new_model}")
    
    # Обновляем конфигурацию
    updated_config = config.copy()
    updated_config.setdefault("custom_settings", {})["my_param"] = "my_value"
    
    if client.update_config(updated_config):
        print("✅ Конфигурация обновлена")
```

### Мониторинг системы

```python
with FoundryClient() as client:
    # Тест подключения
    conn_test = client.test_connection()
    print(f"Подключение: {'✅' if conn_test['connected'] else '❌'}")
    if conn_test['connected']:
        print(f"Время ответа: {conn_test['response_time']:.3f}s")
    
    # Метрики системы
    metrics = client.get_metrics()
    print(f"\nМетрики:")
    print(f"  Всего логов: {metrics.get('total_logs', 0)}")
    print(f"  Ошибок: {metrics.get('errors', 0)}")
    print(f"  Предупреждений: {metrics.get('warnings', 0)}")
    
    # Последние логи
    recent_logs = client.get_logs(limit=5)
    print(f"\nПоследние логи:")
    for log in recent_logs:
        print(f"  [{log.get('level', 'INFO')}] {log.get('message', '')}")
```

---

## 🔧 Обработка ошибок

### Надежная обработка ошибок

```python
from sdk import FoundryClient, FoundryError, FoundryConnectionError, FoundryAPIError

def safe_generate(prompt, max_retries=3):
    """Безопасная генерация с обработкой ошибок"""
    
    for attempt in range(max_retries):
        try:
            with FoundryClient() as client:
                # Проверяем доступность
                if not client.is_alive():
                    raise FoundryConnectionError("API недоступен")
                
                # Генерируем
                response = client.generate(prompt, use_rag=True)
                
                if response.success:
                    return response.content
                else:
                    print(f"Попытка {attempt + 1}: {response.error}")
                    
        except FoundryConnectionError as e:
            print(f"Ошибка подключения (попытка {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Экспоненциальная задержка
                
        except FoundryAPIError as e:
            print(f"Ошибка API: {e}")
            break  # API ошибки обычно не исправляются повторами
            
        except FoundryError as e:
            print(f"SDK ошибка: {e}")
            break
            
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            break
    
    return None

# Использование
result = safe_generate("Расскажи о квантовых компьютерах")
if result:
    print("Результат:", result)
else:
    print("Не удалось получить ответ")
```

### Умная генерация с fallback

```python
with FoundryClient() as client:
    # Пробуем разные стратегии
    strategies = [
        {"use_rag": True, "temperature": 0.7},
        {"use_rag": False, "temperature": 0.5},
        {"use_rag": False, "temperature": 0.3, "max_tokens": 100}
    ]
    
    prompt = "Объясни принцип работы нейронных сетей"
    
    for i, strategy in enumerate(strategies, 1):
        print(f"Стратегия {i}: {strategy}")
        
        try:
            response = client.generate(prompt, **strategy)
            if response.success:
                print("✅ Успех!")
                print("Ответ:", response.content[:200] + "...")
                break
            else:
                print(f"❌ Ошибка: {response.error}")
                
        except Exception as e:
            print(f"❌ Исключение: {e}")
    else:
        print("Все стратегии не сработали")
```

---

## 🧪 Тестирование и отладка

### Полный тест системы

```python
with FoundryClient() as client:
    print("🧪 Запуск полного теста системы...")
    
    # Автоматическая настройка
    setup_result = client.auto_setup()
    print(f"Настройка системы: {setup_result}")
    
    # Быстрый тест
    test_result = client.quick_test("Тестовый промпт для проверки")
    print(f"Быстрый тест: {test_result}")
    
    # Детальная проверка
    if test_result.get("connection"):
        print("✅ Подключение работает")
        
        if test_result.get("models", 0) > 0:
            print(f"✅ Доступно моделей: {test_result['models']}")
            
            if test_result.get("generation"):
                print("✅ Генерация работает")
            else:
                print("❌ Проблемы с генерацией")
        else:
            print("⚠️ Нет доступных моделей")
            
        if test_result.get("rag_search"):
            print("✅ RAG поиск работает")
        else:
            print("⚠️ Проблемы с RAG поиском")
    else:
        print("❌ Нет подключения к API")
    
    # Ошибки
    if test_result.get("errors"):
        print("❌ Обнаружены ошибки:")
        for error in test_result["errors"]:
            print(f"  - {error}")
```

---

**FastAPI Foundry SDK v0.2.1**  
© 2025 AiStros Team