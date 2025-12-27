# 📡 API Methods Reference

Полная документация всех методов FoundryClient.

---

## 🏥 Health & Status

### `health() -> HealthStatus`

Проверка здоровья системы.

```python
health = client.health()
print(f"API: {health.status}")
print(f"Foundry: {health.foundry_status}")
print(f"RAG chunks: {health.rag_chunks}")
```

### `is_alive() -> bool`

Быстрая проверка доступности API.

```python
if client.is_alive():
    print("API доступен")
```

### `wait_for_ready(max_wait=60) -> bool`

Ждать пока API станет доступным.

```python
if client.wait_for_ready(max_wait=30):
    print("API готов к работе")
```

---

## 🤖 Models Management

### `list_models() -> List[ModelInfo]`

Получить список всех доступных моделей.

```python
models = client.list_models()
for model in models:
    print(f"{model.id} ({model.provider})")
```

### `get_connected_models() -> List[ModelInfo]`

Получить только подключенные модели.

```python
connected = client.get_connected_models()
print(f"Подключено моделей: {len(connected)}")
```

### `load_model(model_id: str) -> bool`

Загрузить модель в Foundry.

```python
success = client.load_model("deepseek-r1-distill-qwen-7b-generic-cpu:3")
if success:
    print("Модель загружена")
```

### `unload_model(model_id: str) -> bool`

Выгрузить модель из Foundry.

```python
success = client.unload_model("model-id")
```

### `get_model_status(model_id: str) -> Dict`

Получить статус конкретной модели.

```python
status = client.get_model_status("model-id")
print(status.get("status", "unknown"))
```

---

## ✍️ Text Generation

### `generate(prompt, **kwargs) -> GenerationResponse`

Основной метод генерации текста.

**Параметры:**
- `prompt: str` - Входной промпт
- `model: Optional[str]` - ID модели
- `temperature: Optional[float]` - Температура (0.0-2.0)
- `max_tokens: Optional[int]` - Максимум токенов
- `use_rag: bool = True` - Использовать RAG
- `system_prompt: Optional[str]` - Системный промпт

```python
response = client.generate(
    prompt="Объясни квантовую физику",
    temperature=0.7,
    max_tokens=500,
    use_rag=True
)

if response.success:
    print(response.content)
    print(f"Модель: {response.model_used}")
    print(f"Токенов: {response.tokens_used}")
```

### `chat(message, **kwargs) -> GenerationResponse`

Отправить сообщение в чат с поддержкой сессий.

**Параметры:**
- `message: str` - Сообщение
- `conversation_id: Optional[str]` - ID разговора
- `model: Optional[str]` - ID модели
- `use_rag: bool = True` - Использовать RAG

```python
response = client.chat(
    message="Привет, как дела?",
    conversation_id="session-123",
    use_rag=True
)
```

### `batch_generate(prompts, **kwargs) -> List[GenerationResponse]`

Пакетная генерация для множественных промптов.

```python
prompts = [
    "Что такое AI?",
    "Как работает ML?",
    "Объясни Deep Learning"
]

responses = client.batch_generate(
    prompts=prompts,
    max_tokens=100,
    use_rag=True
)

for i, response in enumerate(responses):
    print(f"Ответ {i+1}: {response.content}")
```

---

## 🔍 RAG System

### `rag_search(query: str, top_k=5) -> List[Dict]`

Поиск в RAG индексе.

```python
results = client.rag_search("Docker installation", top_k=3)
for result in results:
    print(f"Источник: {result['source']}")
    print(f"Релевантность: {result['score']:.3f}")
    print(f"Текст: {result['text'][:100]}...")
```

### `rag_status() -> Dict`

Получить статус RAG системы.

```python
status = client.rag_status()
print(f"Загружено: {status.get('loaded', False)}")
print(f"Чанков: {status.get('chunks_count', 0)}")
```

### `rag_clear() -> bool`

Очистить RAG индекс.

```python
if client.rag_clear():
    print("RAG индекс очищен")
```

### `rag_reload() -> bool`

Перезагрузить RAG индекс.

```python
if client.rag_reload():
    print("RAG индекс перезагружен")
```

### `rag_initialize() -> bool`

Инициализировать RAG систему.

```python
if client.rag_initialize():
    print("RAG система инициализирована")
```

---

## ⚙️ Configuration

### `get_config() -> Dict`

Получить конфигурацию системы.

```python
config = client.get_config()
foundry_config = config.get("foundry_ai", {})
print(f"Foundry URL: {foundry_config.get('base_url')}")
```

### `update_config(config: Dict) -> bool`

Обновить конфигурацию системы.

```python
new_config = {
    "foundry_ai": {
        "default_model": "new-model-id"
    }
}

if client.update_config(new_config):
    print("Конфигурация обновлена")
```

### `set_default_model(model_id: str) -> bool`

Установить модель по умолчанию.

```python
if client.set_default_model("deepseek-r1-distill-qwen-7b-generic-cpu:3"):
    print("Модель по умолчанию установлена")
```

---

## 🏭 Foundry Management

### `foundry_status() -> Dict`

Получить статус Foundry сервиса.

```python
status = client.foundry_status()
print(f"Статус: {status.get('status')}")
print(f"URL: {status.get('url')}")
```

### `foundry_models_loaded() -> List[Dict]`

Получить список загруженных моделей в Foundry.

```python
loaded = client.foundry_models_loaded()
for model in loaded:
    print(f"Загружена: {model.get('id')}")
```

---

## 📊 Monitoring & Logs

### `get_logs(level=None, limit=100) -> List[Dict]`

Получить системные логи.

```python
# Все логи
logs = client.get_logs(limit=50)

# Только ошибки
errors = client.get_logs(level="error", limit=20)

for log in errors:
    print(f"[{log['level']}] {log['message']}")
```

### `get_metrics() -> Dict`

Получить метрики производительности.

```python
metrics = client.get_metrics()
print(f"Всего логов: {metrics.get('total_logs', 0)}")
print(f"Ошибок: {metrics.get('errors', 0)}")
```

---

## 🔧 Utility Methods

### `test_connection() -> Dict`

Тестировать подключение к API.

```python
result = client.test_connection()
if result["connected"]:
    print(f"Подключение OK ({result['response_time']:.3f}s)")
else:
    print(f"Ошибка: {result['error']}")
```

### `auto_setup() -> Dict`

Автоматическая настройка системы.

```python
setup_result = client.auto_setup()
print(f"Health check: {setup_result['health_check']}")
print(f"Models loaded: {setup_result['models_loaded']}")
print(f"RAG initialized: {setup_result['rag_initialized']}")
```

### `quick_test(prompt="Hello") -> Dict`

Быстрый тест всех основных функций.

```python
test_result = client.quick_test("Test prompt")
print(f"Подключение: {test_result['connection']}")
print(f"Генерация: {test_result['generation']}")
print(f"RAG поиск: {test_result['rag_search']}")
print(f"Моделей: {test_result['models']}")
```

---

## 🚀 Advanced Methods

### `generate_with_retry(prompt, max_retries=3, **kwargs)`

Генерация с повторными попытками.

```python
response = client.generate_with_retry(
    prompt="Сложный вопрос",
    max_retries=5,
    max_tokens=200
)
```

### `smart_generate(prompt, prefer_rag=True, **kwargs)`

Умная генерация с автоматическим выбором параметров.

```python
response = client.smart_generate(
    prompt="Расскажи о проекте",
    prefer_rag=True,
    fallback_model="backup-model"
)
```

---

**FastAPI Foundry SDK v0.2.1**  
© 2025 AiStros Team