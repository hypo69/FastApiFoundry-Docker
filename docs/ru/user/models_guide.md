# Руководство по работе с моделями ИИ

FastAPI Foundry поддерживает четыре бэкенда для запуска моделей ИИ. Каждый доступен
через единый REST API и веб-интерфейс.

| Бэкенд | Префикс модели | Формат | Рекомендуется для |
|---|---|---|---|
| **Microsoft Foundry Local** | *(без префикса)* | ONNX | Qwen, DeepSeek, Mistral — быстрый CPU inference |
| **HuggingFace Transformers** | `hf::model-id` | PyTorch / safetensors | Любые модели с Hub |
| **llama.cpp** | `llama::model-name` | GGUF | Большие модели на CPU/GPU |
| **Ollama** | *(настраивается через URL)* | GGUF | Удобное управление моделями |

---

## 🤖 Microsoft Foundry Local

Рекомендуемый бэкенд для моделей Qwen, DeepSeek, Mistral в формате ONNX.
FastAPI Foundry автоматически обнаруживает запущенный Foundry Local.

### Запуск сервиса

```powershell
foundry service start
```

### Загрузка модели

```powershell
# Скачать модель
foundry model download qwen2.5-0.5b-instruct-generic-cpu

# Список доступных моделей
foundry model list-available

# Загрузить в память
foundry model load qwen2.5-0.5b-instruct-generic-cpu
```

### Автоопределение порта

`run.py` автоматически находит Foundry по процессу `Inference.Service.Agent*`
и сканирует порты `[62171, 50477, 58130]`. Можно задать явно:

```env
# .env
FOUNDRY_BASE_URL=http://localhost:50477/v1/
```

### Автозагрузка модели при старте

```json
// config.json
{
  "foundry_ai": {
    "auto_load_default": true,
    "default_model": "qwen2.5-0.5b-instruct-generic-cpu"
  }
}
```

### API

```bash
# Список загруженных моделей Foundry
GET /api/v1/foundry/models/loaded

# Загрузить модель
POST /api/v1/foundry/models/load
{"model_id": "qwen2.5-0.5b-instruct-generic-cpu"}

# Выгрузить модель
POST /api/v1/foundry/models/unload
{"model_id": "qwen2.5-0.5b-instruct-generic-cpu"}
```

---

## 🤗 HuggingFace Transformers

Полноценная интеграция с HuggingFace Hub: скачивание, загрузка в память,
inference через `transformers.pipeline`. Реализовано в `src/models/hf_client.py`.

### Концепция

```
HuggingFace Hub
      ↓  snapshot_download()
~/.models/author--model-name/   ← HF_MODELS_DIR (из .env)
      ↓  AutoModelForCausalLM
RAM / VRAM (_loaded_models dict)
      ↓  pipeline("text-generation")
/api/v1/hf/generate
```

Модели также сканируются из стандартного кэша `~/.cache/huggingface/hub`.

### Настройка

```env
# .env
HF_TOKEN=hf_ваш_токен          # обязателен для закрытых моделей (Gemma, Llama)
HF_MODELS_DIR=D:\models         # куда скачивать (по умолчанию ~/.models)
```

Токен создаётся на [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) с ролью `Read`.

### Популярные модели

| Модель | Размер | Лицензия |
|---|---|---|
| `Qwen/Qwen2.5-0.5B-Instruct` | ~1 GB | Открытая |
| `Qwen/Qwen2.5-1.5B-Instruct` | ~3 GB | Открытая |
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | ~2 GB | Открытая |
| `microsoft/phi-2` | ~5 GB | Открытая |
| `deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B` | ~3 GB | Открытая |
| `mistralai/Mistral-7B-Instruct-v0.3` | ~14 GB | Нужно принять |
| `meta-llama/Llama-3.2-1B-Instruct` | ~2 GB | Нужно принять |
| `google/gemma-2-2b-it` | ~5 GB | Нужно принять |

Для моделей с пометкой «Нужно принять» — откройте страницу модели на huggingface.co
и примите лицензию, затем установите `HF_TOKEN`.

### API

```bash
# Статус интеграции (версии библиотек, CUDA, путь к моделям)
GET /api/v1/hf/status

# Список скачанных и загруженных моделей
GET /api/v1/hf/models

# Список моделей пользователя + популярные публичные модели
GET /api/v1/hf/hub/models

# Скачать модель с Hub
POST /api/v1/hf/models/download
{"model_id": "Qwen/Qwen2.5-0.5B-Instruct"}

# Для закрытой модели — передать токен явно
POST /api/v1/hf/models/download
{"model_id": "google/gemma-2-2b-it", "token": "hf_..."}

# Загрузить в память (CPU или GPU)
POST /api/v1/hf/models/load
{"model_id": "Qwen/Qwen2.5-0.5B-Instruct", "device": "auto"}

# Выгрузить из памяти (освобождает RAM/VRAM)
POST /api/v1/hf/models/unload
{"model_id": "Qwen/Qwen2.5-0.5B-Instruct"}

# Генерация текста
POST /api/v1/hf/generate
{
  "model_id": "Qwen/Qwen2.5-0.5B-Instruct",
  "prompt": "Объясни, что такое RAG",
  "max_new_tokens": 512,
  "temperature": 0.7
}
```

### Пример ответа `/api/v1/hf/status`

```json
{
  "success": true,
  "transformers": {"available": true, "version": "4.40.0"},
  "huggingface_hub": {"available": true, "version": "0.23.0"},
  "torch": {"available": true, "version": "2.1.0", "cuda": false},
  "hf_token_set": true,
  "models_dir": "D:\\models"
}
```

### Использование в чате

В веб-интерфейсе HuggingFace модели отображаются с префиксом `hf::`:

```
hf::Qwen/Qwen2.5-0.5B-Instruct
hf::TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

Модель должна быть **скачана и загружена в память** перед использованием в чате.
При первом обращении через `/api/v1/hf/generate` загрузка происходит автоматически.

### Зависимости

```bash
pip install transformers accelerate huggingface_hub torch
```

Если зависимости не установлены — `/api/v1/hf/status` вернёт `"available": false`,
остальные эндпоинты вернут понятное сообщение об ошибке.

---

## 🦙 llama.cpp

Запуск GGUF моделей на CPU или GPU через `llama-server.exe`.
Бинарники для Windows x64 включены в `bin/llama-b8802-bin-win-cpu-x64/`.

### Настройка

```env
# .env
LLAMA_SERVER_PATH=.\bin\llama-b8802-bin-win-cpu-x64\llama-server.exe
```

### Запуск через скрипт

```powershell
.\scripts\llama-start.ps1
```

Или вручную:

```powershell
.\bin\llama-b8802-bin-win-cpu-x64\llama-server.exe `
  --model D:\models\qwen2.5-0.5b-q4_k_m.gguf `
  --port 8080 `
  --ctx-size 4096
```

### API

```bash
# Статус llama.cpp сервера
GET /api/v1/llama/status

# Запустить сервер с моделью
POST /api/v1/llama/start
{"model_path": "D:\\models\\qwen2.5-0.5b-q4_k_m.gguf"}

# Остановить сервер
POST /api/v1/llama/stop
```

В чате и генерации llama.cpp модели используются с префиксом `llama::`.

---

## 🦙 Ollama

```bash
# Установить и запустить
# https://ollama.com/download

ollama run llama2
ollama run qwen2.5:0.5b
```

Настройте `FOUNDRY_BASE_URL` на порт Ollama (по умолчанию `11434`):

```env
FOUNDRY_BASE_URL=http://127.0.0.1:11434/v1/
```

---

## ⚙️ Конфигурация моделей

```json
// config.json
{
  "foundry_ai": {
    "default_model": "qwen2.5-0.5b-instruct-generic-cpu",
    "auto_load_default": false,
    "temperature": 0.7,
    "max_tokens": 2048
  },
  "directories": {
    "models": "~/.models",
    "hf_models": "~/.hf_models"
  }
}
```

| Параметр | Описание |
|---|---|
| `default_model` | Модель по умолчанию в веб-интерфейсе |
| `auto_load_default` | Загружать модель при старте (только Foundry) |
| `temperature` | Температура генерации (0.0 — детерминировано, 2.0 — максимально случайно) |
| `max_tokens` | Максимум токенов в ответе |
| `directories.models` | Директория GGUF моделей для llama.cpp |
| `directories.hf_models` | Директория HuggingFace моделей (переопределяет `HF_MODELS_DIR`) |
