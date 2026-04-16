# Руководство по работе с моделями ИИ

FastAPI Foundry предоставляет унифицированный интерфейс для работы с различными моделями искусственного интеллекта, запущенными на локальных бэкендах, таких как Microsoft Foundry Local, llama.cpp и Ollama.

## 💡 Общая концепция

Система FastAPI Foundry может подключаться к одному или нескольким бэкендам ИИ, каждый из которых предоставляет доступ к своим моделям. Веб-интерфейс и API позволяют:

*   Получать список доступных моделей.
*   Загружать и выгружать модели (для Foundry).
*   Отправлять запросы на генерацию текста или участие в чате с выбранной моделью.

## 🤖 Microsoft Foundry Local

**Foundry Local** — это рекомендуемый бэкенд для работы с моделями Microsoft и сообщества, такими как Qwen, DeepSeek, Mistral. Он обеспечивает высокую производительность и удобное управление моделями.

### Запуск сервиса Foundry

```powershell
foundry service start
```

### Загрузка моделей

Модели для Foundry можно загрузить с помощью Foundry CLI. Например:

```powershell
foundry model download qwen2.5-0.5b-instruct-generic-cpu
```

Список доступных моделей Foundry можно получить через:

```powershell
foundry model list-available
```

### Использование в FastAPI Foundry

FastAPI Foundry автоматически обнаруживает запущенный Foundry Local (если он доступен по `FOUNDRY_BASE_URL` в `.env` или через автоопределение портов). После запуска сервера FastAPI Foundry, вы сможете выбрать Foundry модели в веб-интерфейсе.

## 🦙 llama.cpp

**llama.cpp** позволяет запускать модели в формате GGUF (например, Llama 2, Mistral, CodeLlama) на CPU или GPU. Для интеграции с FastAPI Foundry требуется запущенный `llama-server.exe`.

### Запуск llama-server.exe

1.  **Скачайте** `llama-server.exe` из [релизов llama.cpp](https://github.com/ggerganov/llama.cpp/releases).
2.  **Распакуйте** его, например, в `bin/llama-b8802-bin-win-cpu-x64/`.
3.  **Укажите путь** к `llama-server.exe` в файле `.env`:
    ```
    LLAMA_SERVER_PATH=.\bin\llama-b8802-bin-win-cpu-x64\llama-server.exe
    ```
4.  **Запустите сервер** llama.cpp вручную или через скрипт проекта (например, `scripts\llama-start.ps1`, если он есть).

### Использование в FastAPI Foundry

Если `LLAMA_SERVER_PATH` настроен и `llama-server.exe` запущен, FastAPI Foundry будет доступен через API и веб-интерфейс. Вам нужно будет указать модель (например, `ggml-model-q4_0.bin`) для взаимодействия.

## 🦙 Ollama

**Ollama** предоставляет удобный способ запуска и управления широким спектром моделей.

### Установка и запуск Ollama

1.  **Скачайте и установите** Ollama с [официального сайта](https://ollama.com/download).
2.  **Запустите** Ollama (обычно он запускается как фоновый сервис).
3.  **Загрузите модель** через Ollama CLI (например, `ollama run llama2`).

### Использование в FastAPI Foundry

FastAPI Foundry может быть настроен для работы с Ollama. Убедитесь, что Ollama запущен и доступен по стандартному порту (обычно `127.0.0.1:11434`). Возможно, потребуется настройка `FOUNDRY_BASE_URL` или аналогичной переменной в `.env`, если Ollama используется как основной источник моделей.

## ⚙️ Конфигурация моделей

Настройки, связанные с моделями, находятся в `config.json` в секции `foundry_ai`:

```json
{
  "foundry_ai": {
    "default_model": "qwen2.5-0.5b-instruct-generic-cpu",
    "auto_load_default": false,
    "temperature": 0.7,
    "max_tokens": 2048
  }
}
```

*   `default_model`: Модель, которая будет выбрана по умолчанию в веб-интерфейсе.
*   `auto_load_default`: Загружать ли модель по умолчанию при старте (только для Foundry).
*   `temperature`: Температура генерации (креативность).
*   `max_tokens`: Максимальное количество токенов в ответе ИИ.
