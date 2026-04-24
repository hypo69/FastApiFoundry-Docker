# CLI Reference

Справочник по командам командной строки для всех компонентов FastAPI Foundry.

---

## Foundry Local CLI

Foundry Local управляется через команду `foundry`. Устанавливается через:

```powershell
winget install Microsoft.FoundryLocal
```

---

### foundry service

Управление фоновым сервисом Foundry (inference engine).

| Команда | Описание |
|---|---|
| `foundry service start` | Запустить сервис в фоне |
| `foundry service stop` | Остановить сервис |
| `foundry service status` | Показать статус, URL и порт |
| `foundry service restart` | Перезапустить сервис |

```powershell
foundry service start
foundry service status
# 🟢 Model management service is running on http://127.0.0.1:52632/openai/status

foundry service stop
```

!!! tip "Порт динамический"
    Foundry каждый раз может запускаться на другом порту.
    FastAPI Foundry находит его автоматически через `tasklist` + `netstat`.
    Чтобы зафиксировать порт — задайте `FOUNDRY_BASE_URL` в `.env`.

---

### foundry model

Управление моделями: скачивание, загрузка в память, выгрузка.

| Команда | Описание |
|---|---|
| `foundry model list` | Список скачанных моделей в локальном кэше |
| `foundry model list-available` | Каталог всех доступных моделей для скачивания |
| `foundry model ls` | Краткий список (псевдоним `list`) |
| `foundry model download <id>` | Скачать модель в кэш (`~/.foundry/cache/models`) |
| `foundry model load <id>` | Загрузить модель в сервис (inference ready) |
| `foundry model unload <id>` | Выгрузить модель из памяти |
| `foundry model info <id>` | Подробная информация о модели |
| `foundry model remove <id>` | Удалить модель из кэша |

```powershell
# Посмотреть что доступно
foundry model list-available

# Скачать и загрузить
foundry model download qwen2.5-0.5b-instruct-generic-cpu:4
foundry model load qwen2.5-0.5b-instruct-generic-cpu:4

# Проверить что загружено
foundry model list

# Выгрузить (освободить RAM)
foundry model unload qwen2.5-0.5b-instruct-generic-cpu:4
```

!!! info "Формат ID модели"
    ID модели в Foundry имеет формат `<name>:<variant>`, например:
    `qwen2.5-0.5b-instruct-generic-cpu:4`

    - `generic-cpu` — оптимизирована для CPU (ONNX)
    - `openvino-gpu` — оптимизирована для Intel GPU
    - `:4` — вариант квантизации (4-bit)

---

### foundry run

Интерактивный чат с моделью прямо в терминале.

```powershell
# Запустить чат (скачает и загрузит модель если нужно)
foundry run qwen2.5-0.5b-instruct-generic-cpu:4

# Выйти из чата
/exit
```

---

### Рекомендуемые модели Foundry

| Модель | Размер | Тип | Описание |
|---|---|---|---|
| `qwen2.5-0.5b-instruct-generic-cpu:4` | 0.8 GB | CPU | Самая лёгкая, быстрая |
| `qwen2.5-1.5b-instruct-generic-cpu:4` | 1.78 GB | CPU | Хороший баланс |
| `qwen2.5-3b-instruct-generic-cpu:4` | 2.8 GB | CPU | Средняя |
| `qwen3-0.6b-generic-cpu:4` | 0.9 GB | CPU | Новейшая архитектура |
| `deepseek-r1-distill-qwen-7b-generic-cpu:3` | 6.43 GB | CPU | С цепочками рассуждений |
| `deepseek-r1-distill-qwen-14b-generic-cpu:4` | ~9 GB | CPU | Продвинутая |
| `phi-3-mini-4k-instruct-openvino-gpu:1` | 2.4 GB | GPU | Intel GPU inference |

---

### Кэш и директории Foundry

| Путь | Назначение |
|---|---|
| `~/.foundry/cache/models/` | Скачанные модели (ONNX) |
| `~/.foundry/logs/` | Логи сервиса |

```powershell
# Посмотреть кэш
ls ~/.foundry/cache/models/
```

---

## llama.cpp

Запуск GGUF моделей через `llama-server.exe`. Бинарники включены в `bin/`.

---

### Запуск сервера

```powershell
# Минимальный запуск
.\\bin\\llama-b8802-bin-win-cpu-x64\\llama-server.exe `
  --model ~/.models/qwen2.5-0.5b-q4_k_m.gguf `
  --port 9780

# Рекомендуемый запуск
.\\bin\\llama-b8802-bin-win-cpu-x64\\llama-server.exe `
  --model ~/.models/qwen2.5-0.5b-q4_k_m.gguf `
  --port 9780 `
  --host 127.0.0.1 `
  --ctx-size 4096 `
  --threads 8

# С GPU (CUDA/Vulkan)
.\\bin\\llama-b8802-bin-win-cpu-x64\\llama-server.exe `
  --model ~/.models/model.gguf `
  --port 9780 `
  --n-gpu-layers 35
```

Или через скрипт (читает настройки из `config.json`):

```powershell
.\\scripts\\llama-start.ps1
```

---

### Все параметры llama-server

#### Модель

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--model <path>` | — | **Обязательно.** Путь к `.gguf` файлу |
| `--model-alias <name>` | — | Псевдоним модели в API ответах |
| `--lora <path>` | — | Путь к LoRA адаптеру |
| `--lora-scale <float>` | 1.0 | Масштаб LoRA |

#### Сервер

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--host <addr>` | `127.0.0.1` | Адрес прослушивания (`0.0.0.0` = все интерфейсы) |
| `--port <int>` | `8080` | Порт HTTP сервера |
| `--timeout <int>` | `600` | Таймаут запроса в секундах |
| `--threads-http <int>` | `auto` | Потоков для HTTP обработки |
| `--api-key <key>` | — | Ключ для защиты API (Bearer token) |
| `--cors-allow-origin <url>` | — | Разрешённый CORS origin |

#### Контекст и память

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--ctx-size <int>` | `512` | Размер контекста в токенах. Увеличьте до 4096–32768 для длинных диалогов |
| `--batch-size <int>` | `2048` | Размер батча при обработке промпта |
| `--ubatch-size <int>` | `512` | Размер микробатча |
| `--rope-scaling <type>` | — | Масштабирование RoPE: `none`, `linear`, `yarn` |
| `--rope-scale <float>` | — | Коэффициент масштабирования RoPE |
| `--yarn-ext-factor <float>` | — | YaRN экстраполяция |
| `--cache-type-k <type>` | `f16` | Тип кэша K: `f32`, `f16`, `q8_0`, `q4_0` |
| `--cache-type-v <type>` | `f16` | Тип кэша V: `f32`, `f16`, `q8_0`, `q4_0` |

#### CPU

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--threads <int>` | `auto` | Потоков CPU для inference (рекомендуется = физические ядра) |
| `--threads-batch <int>` | `auto` | Потоков для обработки батча |
| `--cpu-mask <hex>` | — | Маска CPU affinity (hex) |
| `--no-mmap` | — | Не использовать mmap для загрузки модели |
| `--mlock` | — | Заблокировать модель в RAM (не выгружать) |
| `--numa <mode>` | — | NUMA режим: `distribute`, `isolate`, `numactl` |

#### GPU

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--n-gpu-layers <int>` | `0` | Слоёв на GPU. `0` = только CPU, `-1` = все слои на GPU |
| `--split-mode <mode>` | `layer` | Режим разбивки по GPU: `none`, `layer`, `row` |
| `--tensor-split <list>` | — | Распределение по GPU: `0.7,0.3` |
| `--main-gpu <int>` | `0` | Основной GPU для операций |
| `--gpu-layers-draft <int>` | — | Слоёв черновика на GPU (speculative decoding) |

#### Генерация

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--temp <float>` | `0.8` | Температура по умолчанию |
| `--top-k <int>` | `40` | Top-K сэмплинг |
| `--top-p <float>` | `0.95` | Top-P (nucleus) сэмплинг |
| `--min-p <float>` | `0.05` | Min-P сэмплинг |
| `--repeat-penalty <float>` | `1.1` | Штраф за повторения |
| `--repeat-last-n <int>` | `64` | Окно для штрафа повторений |
| `--seed <int>` | `-1` | Seed генерации (`-1` = случайный) |
| `--n-predict <int>` | `-1` | Максимум токенов (`-1` = без ограничений) |

#### Параллелизм

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--parallel <int>` | `1` | Параллельных слотов (одновременных запросов) |
| `--cont-batching` | — | Включить continuous batching |
| `--flash-attn` | — | Включить Flash Attention (ускорение, нужна поддержка GPU) |

#### Логирование

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--log-disable` | — | Отключить вывод логов в консоль |
| `--log-file <path>` | — | Записывать логи в файл |
| `--verbose` | — | Подробный вывод |

---

### Проверка работы

```powershell
# Статус сервера
curl http://localhost:9780/health

# Список моделей (OpenAI-совместимый)
curl http://localhost:9780/v1/models

# Тестовый запрос
curl -X POST http://localhost:9780/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d '{"model": "local", "messages": [{"role": "user", "content": "Hello"}]}'
```

---

### Скачивание GGUF моделей

```powershell
# Установить HuggingFace CLI
pip install huggingface_hub

# Авторизация (нужна для Gemma, Llama)
hf auth login

# Скачать модель (рекомендуется Q4_K_M)
hf download bartowski/Qwen2.5-0.5B-Instruct-GGUF `
  --include "*Q4_K_M.gguf" `
  --local-dir ~/.models

hf download bartowski/gemma-2-2b-it-GGUF `
  --include "*Q6_K.gguf" `
  --local-dir ~/.models

hf download bartowski/Llama-3.2-3B-Instruct-GGUF `
  --include "*Q4_K_M.gguf" `
  --local-dir ~/.models
```

| Квантование | Размер (7B) | Качество | Рекомендация |
|---|---|---|---|
| `Q2_K` | ~2.8 GB | Низкое | Только для edge-устройств |
| `Q3_K_M` | ~3.3 GB | Среднее | Если RAM критически мало |
| `Q4_K_M` | ~4.1 GB | Хорошее | **Рекомендуется** — лучший баланс |
| `Q5_K_M` | ~4.8 GB | Очень хорошее | Если есть запас RAM |
| `Q6_K` | ~5.5 GB | Отличное | Близко к оригиналу |
| `Q8_0` | ~7.2 GB | Максимальное | Почти без потерь |
| `F16` | ~14 GB | Оригинал | Только для серверов с GPU |

Проверенные кураторы GGUF: **bartowski**, **unsloth**, **TheBloke**

---

### Настройка в config.json

```json
{
  "llama_cpp": {
    "port": 9780,
    "host": "127.0.0.1",
    "model_path": "~/.models/qwen2.5-0.5b-q4_k_m.gguf",
    "auto_start": true,
    "bin_version": "llama-b8802-bin-win-cpu-x64"
  },
  "directories": {
    "models": "~/.models"
  }
}
```

| Ключ | Описание |
|---|---|
| `port` | Порт llama-server (по умолчанию 9780) |
| `host` | Хост (127.0.0.1 = только локально) |
| `model_path` | Путь к `.gguf` файлу для автозапуска |
| `auto_start` | Запускать llama-server при старте `start.ps1` |
| `bin_version` | Версия бинарника в `bin/` — обновляется автоматически |
| `directories.models` | Директория для хранения GGUF моделей |

---

## HuggingFace CLI

HuggingFace CLI (`hf` / `huggingface-cli`) — инструмент для работы с Hub.

### Установка

```powershell
pip install huggingface_hub
```

После установки доступны две команды — они эквивалентны:

```powershell
hf <команда>
huggingface-cli <команда>
```

---

### hf auth

Управление авторизацией.

| Команда | Описание |
|---|---|
| `hf auth login` | Войти (запросит токен) |
| `hf auth logout` | Выйти |
| `hf auth switch` | Переключить аккаунт |
| `hf whoami` | Показать текущего пользователя |

```powershell
# Войти с токеном (токен создаётся на huggingface.co/settings/tokens)
hf auth login
# Enter your token: hf_...

# Проверить авторизацию
hf whoami
# Logged in as: your-username
```

!!! info "Когда нужна авторизация"
    Токен обязателен для скачивания **gated** моделей (Gemma, Llama, Mistral).
    Для открытых моделей (Qwen, TinyLlama, Phi) авторизация не нужна.

---

### hf download

Скачивание моделей и датасетов.

```powershell
hf download <repo_id> [options]
```

| Параметр | Описание |
|---|---|
| `<repo_id>` | **Обязательно.** ID репозитория: `author/model-name` |
| `--include <pattern>` | Скачать только файлы по паттерну (glob) |
| `--exclude <pattern>` | Исключить файлы по паттерну |
| `--local-dir <path>` | Директория для сохранения (по умолчанию — кэш HF) |
| `--token <token>` | Токен (если не задан через `hf auth login`) |
| `--repo-type <type>` | Тип репозитория: `model` (по умолчанию), `dataset`, `space` |
| `--revision <rev>` | Ветка, тег или коммит (по умолчанию `main`) |
| `--quiet` | Без прогресс-бара |
| `--force-download` | Перескачать даже если файл уже есть |

```powershell
# Скачать всю модель
hf download Qwen/Qwen2.5-0.5B-Instruct `
  --local-dir ~/.hf_models/Qwen--Qwen2.5-0.5B-Instruct

# Скачать только GGUF файл нужной квантизации
hf download bartowski/Qwen2.5-0.5B-Instruct-GGUF `
  --include "*Q4_K_M.gguf" `
  --local-dir ~/.models

# Скачать несколько файлов по паттерну
hf download bartowski/gemma-2-2b-it-GGUF `
  --include "*.gguf" `
  --exclude "*Q2*" `
  --local-dir ~/.models

# Скачать закрытую модель с токеном
hf download meta-llama/Llama-3.2-1B-Instruct `
  --local-dir ~/.hf_models/Llama-3.2-1B-Instruct `
  --token hf_ваш_токен

# Скачать конкретную версию (тег/коммит)
hf download Qwen/Qwen2.5-0.5B-Instruct `
  --revision v1.0 `
  --local-dir ~/.hf_models/Qwen--Qwen2.5-0.5B-Instruct
```

---

### hf upload

Загрузка файлов на Hub.

```powershell
hf upload <repo_id> <local_path> [remote_path] [options]
```

| Параметр | Описание |
|---|---|
| `<repo_id>` | ID репозитория |
| `<local_path>` | Локальный файл или директория |
| `[remote_path]` | Путь в репозитории (опционально) |
| `--repo-type <type>` | `model`, `dataset`, `space` |
| `--commit-message <msg>` | Сообщение коммита |
| `--token <token>` | Токен с правами записи |

---

### huggingface-cli scan-cache

Управление локальным кэшем HuggingFace.

| Команда | Описание |
|---|---|
| `huggingface-cli scan-cache` | Показать все скачанные модели и их размер |
| `huggingface-cli delete-cache` | Интерактивное удаление из кэша |
| `huggingface-cli env` | Показать переменные окружения HF |

```powershell
# Посмотреть что скачано и сколько занимает
huggingface-cli scan-cache

# REPO ID                                   REPO TYPE  SIZE ON DISK  NB FILES
# Qwen/Qwen2.5-0.5B-Instruct               model             987.4M        12
# google/gemma-2-2b-it                      model               4.9G        18

# Удалить конкретную модель из кэша
huggingface-cli delete-cache
# (интерактивный выбор через пробел, Enter для удаления)
```

!!! info "Два кэша"
    HuggingFace хранит модели в двух местах:

    | Кэш | Путь | Кто пишет |
    |---|---|---|
    | Стандартный HF кэш | `~/.cache/huggingface/hub` | `huggingface-cli`, `transformers` |
    | FastAPI Foundry | `~/.hf_models/` | FastAPI Foundry (`/api/v1/hf/models/download`) |

    FastAPI Foundry сканирует **оба** при `GET /api/v1/hf/models`.

---

### Переменные окружения HuggingFace

| Переменная | Описание |
|---|---|
| `HF_TOKEN` | Токен авторизации (приоритет над `hf auth login`) |
| `HF_HOME` | Корневая директория HF (`~/.cache/huggingface` по умолчанию) |
| `HF_HUB_CACHE` | Директория кэша моделей (`$HF_HOME/hub` по умолчанию) |
| `HF_HUB_OFFLINE` | `1` = работать только с локальным кэшем, не обращаться к Hub |
| `HF_HUB_DISABLE_PROGRESS_BARS` | `1` = отключить прогресс-бары при скачивании |
| `HF_HUB_DISABLE_TELEMETRY` | `1` = отключить телеметрию |
| `HF_HUB_VERBOSITY` | Уровень логов: `debug`, `info`, `warning`, `error` |
| `TRANSFORMERS_CACHE` | (устарело) Директория кэша transformers |
| `TRANSFORMERS_VERBOSITY` | Уровень логов transformers: `error` подавляет предупреждения |
| `TOKENIZERS_PARALLELISM` | `false` = отключить параллелизм токенизатора (убирает предупреждение) |

```env
# .env — рекомендуемые настройки
HF_TOKEN=hf_ваш_токен
TRANSFORMERS_VERBOSITY=error
TOKENIZERS_PARALLELISM=false
```

---

### Настройка в config.json

```json
{
  "huggingface": {
    "device": "auto",
    "default_max_new_tokens": 512,
    "default_temperature": 0.7
  },
  "directories": {
    "hf_models": "~/.hf_models"
  }
}
```

| Ключ | Описание |
|---|---|
| `huggingface.device` | Устройство для inference: `auto` (GPU если есть, иначе CPU), `cpu`, `cuda` |
| `huggingface.default_max_new_tokens` | Максимум новых токенов по умолчанию |
| `huggingface.default_temperature` | Температура генерации по умолчанию |
| `directories.hf_models` | Директория для скачивания моделей через FastAPI Foundry (default: `~/.cache/huggingface/hub`) |

---

## FastAPI Foundry — диагностика

```powershell
# Проверить конфигурацию и окружение
venv\Scripts\python.exe check_env.py

# Полная диагностика системы
venv\Scripts\python.exe diagnose.py

# Запустить все smoke-тесты
venv\Scripts\python.exe check_engine\smoke_all_endpoints.py

# Здоровье API
curl http://localhost:9696/api/v1/health

# Статус всех сервисов
curl http://localhost:9696/api/v1/foundry/status
curl http://localhost:9696/api/v1/llama/status
curl http://localhost:9696/api/v1/hf/status

# Список моделей
curl http://localhost:9696/api/v1/models
curl http://localhost:9696/api/v1/foundry/models/loaded
curl http://localhost:9696/api/v1/hf/models
```
