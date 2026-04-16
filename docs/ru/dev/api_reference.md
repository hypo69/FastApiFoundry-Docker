# API Справочник FastAPI Foundry

FastAPI Foundry предоставляет RESTful API для программного взаимодействия с моделями ИИ, чатом, RAG системой, управлением конфигурацией и другими функциями. Все API-эндпоинты доступны по базовому префиксу `/api/v1/`.

Полная интерактивная документация API доступна по адресу `/docs` после запуска сервера FastAPI Foundry.

## 🗺️ Общие сведения

*   **Базовый URL**: `http://localhost:9696/api/v1` (порт может отличаться)
*   **Формат ответа**: JSON.
*   **Обработка ошибок**: В случае ошибки возвращается JSON-объект с ключом `"success": False` и `"error": "Сообщение об ошибке"`.

    ```json
    // Успешный ответ
    {"success": true, "data": { ... }}

    // Ответ с ошибкой
    {"success": false, "error": "Подробное описание ошибки"}
    ```

## ⚡ Эндпоинты по функциональным областям

Ниже представлен список основных API эндпоинтов, сгруппированных по файлам в директории `src/api/endpoints/`:

### `/api/v1/health` (src/api/endpoints/health.py)

*   **GET `/health`**: Проверка состояния сервиса. Возвращает статус работы FastAPI Foundry и подключенных бэкендов ИИ.

### `/api/v1/generate` (src/api/endpoints/generate.py)

*   **POST `/generate`**: Однократная генерация текста ИИ-моделью.
    *   **Тело запроса**: `{"prompt": "Ваш запрос", "model": "имя_модели", "temperature": 0.7, "max_tokens": 2048}`

### `/api/v1/chat` (src/api/endpoints/chat_endpoints.py / chat_endpoints_new.py)

*   **POST `/chat/send`**: Отправка сообщения в чат с поддержанием истории.
    *   **Тело запроса**: `{"message": "Ваше сообщение", "model": "имя_модели", "session_id": "id_сессии"}`

### `/api/v1/models` (src/api/endpoints/models.py / models_extra.py)

*   **GET `/models`**: Получить список всех доступных моделей, обнаруженных FastAPI Foundry.
*   **GET `/models/foundry`**: Получить список моделей, доступных через Foundry Local.

### `/api/v1/foundry` (src/api/endpoints/foundry.py / foundry_management.py)

*   **GET `/foundry/status`**: Проверить статус сервиса Foundry Local.
*   **POST `/foundry/service/start`**: Запустить сервис Foundry Local.
*   **POST `/foundry/service/stop`**: Остановить сервис Foundry Local.

### `/api/v1/foundry/models` (src/api/endpoints/foundry_models.py)

*   **POST `/foundry/models/load`**: Загрузить модель в Foundry Local.
    *   **Тело запроса**: `{"model_id": "имя_модели"}`
*   **POST `/foundry/models/unload`**: Выгрузить модель из Foundry Local.
    *   **Тело запроса**: `{"model_id": "имя_модели"}`

### `/api/v1/rag` (src/api/endpoints/rag.py)

*   **GET `/rag/status`**: Получить статус системы RAG (включена ли, модель, количество чанков).
*   **PUT `/rag/config`**: Обновить конфигурацию RAG в `config.json`.
*   **POST `/rag/clear`**: Удалить все файлы индекса RAG.
*   **POST `/rag/search`**: Поиск релевантных документов по запросу (возвращает заглушку).
*   **POST `/rag/rebuild`**: Перестроить индекс RAG (возвращает заглушку).

### `/api/v1/translation` (src/api/endpoints/translation.py)

*   **POST `/translation/translate`**: Перевод текста с использованием LLM, DeepL, Google или Helsinki.
    *   **Тело запроса**: `{"text": "Текст для перевода", "target_lang": "ru", "source_lang": "en", "provider": "llm"}`

### `/api/v1/config` (src/api/endpoints/config.py)

*   **GET `/config`**: Получить текущую конфигурацию `config.json`.
*   **PUT `/config`**: Обновить часть или всю конфигурацию `config.json`.
*   **GET `/config/env`**: Получить текущие переменные окружения.
*   **PUT `/config/env`**: Обновить переменные окружения в файле `.env`.

### `/api/v1/logs` (src/api/endpoints/logs.py)

*   **GET `/logs`**: Получить последние записи логов приложения.

### `/api/v1/hf` (src/api/endpoints/hf_models.py)

*   **POST `/hf/download`**: Скачать модель с HuggingFace.
*   **POST `/hf/generate`**: Генерация текста с использованием HuggingFace моделей.

### `/api/v1/llama` (src/api/endpoints/llama_cpp.py)

*   **GET `/llama/status`**: Статус llama.cpp сервера.
*   **POST `/llama/start`**: Запустить llama.cpp сервер.
*   **POST `/llama/stop`**: Остановить llama.cpp сервер.

### `/api/v1/mcp-powershell` (src/api/endpoints/mcp_powershell.py)

*   **POST `/mcp-powershell/run`**: Выполнить команду PowerShell через MCP сервер.

### `/api/v1/agent` (src/api/endpoints/agent.py)

*   **GET `/agent/list`**: Список всех доступных ИИ-агентов.
*   **GET `/agent/{name}/tools`**: Получить список инструментов для указанного агента.
*   **POST `/agent/run`**: Запустить ИИ-агента с заданным сообщением и моделью.
    *   **Тело запроса**: `{"message": "Сообщение для агента", "agent": "имя_агента", "model": "имя_модели"}`

### `/api/v1/converter` (src/api/endpoints/converter.py)

*   **POST `/converter/gguf-to-onnx`**: Конвертировать модель из формата GGUF в ONNX.
