# 📦 INSTALL.md

**Проект:** FastApiFoundry (Docker)
**Версия:** 0.3.4
**Автор:** hypo69
**Лицензия:** CC BY-NC-SA 4.0

---

## Содержание

1. [Системные требования](#системные-требования)
2. [Установка проекта](#установка-проекта)
3. [Запуск AI бэкенда](#запуск-ai-бэкенда)
   - [Вариант A — Microsoft Foundry Local](#вариант-a--microsoft-foundry-local)
   - [Вариант B — llama.cpp (GGUF модели)](#вариант-b--llamacpp-gguf-модели)
   - [Вариант C — Ollama](#вариант-c--ollama)
4. [Запуск сервера](#запуск-сервера)
5. [Проверка работы](#проверка-работы)
6. [Устранение проблем](#устранение-проблем)

---

## Системные требования

| Компонент | Минимум | Рекомендуется |
|-----------|---------|---------------|
| Python | 3.11+ | 3.11 |
| RAM | 4 GB | 8 GB+ |
| Диск | 2 GB | 10 GB+ (с RAG) |
| ОС | Windows 10+ | Windows 11 |

> Если Python не установлен в системе — `install.ps1` автоматически предложит
> использовать локальный интерпретатор из `bin\Python-3.11.9.zip`. Подробнее: [Установка Python из локального архива](#установка-python-из-локального-архива).

---

## Установка Python из локального архива

Если Python 3.11+ **не установлен** в системе и нет доступа к интернету,
`install.ps1` автоматически обнаружит архив `bin\Python-3.11.9.zip` и предложит
установить интерпретатор из него.

### Как это работает

```
install.ps1
  └─ Python 3.11+ найден в PATH?
       ДА  → используется системный Python
       НЕТ → найден bin\Python-3.11.9.zip?
               НЕТ → сообщение + выход
               ДА  → предложение установить (y/N)
                       N → выход
                       Y → Expand-Archive → bin\Python-3.11.9\
                             → python.exe используется для создания venv
```

### Расположение файлов

| Путь | Описание |
|------|----------|
| `bin\Python-3.11.9.zip` | Архив с интерпретатором (поставляется с проектом) |
| `bin\Python-3.11.9\` | Создаётся автоматически при распаковке |
| `venv\` | Виртуальное окружение, создаётся из локального интерпретатора |

### Ручная распаковка (если нужно)

```powershell
Expand-Archive -Path bin\Python-3.11.9.zip -DestinationPath bin\Python-3.11.9
bin\Python-3.11.9\python.exe -m venv venv
venv\Scripts\pip.exe install -r requirements.txt
```

> После создания `venv` локальный интерпретатор в `bin\Python-3.11.9\` больше
> не нужен для запуска проекта — `venv` самодостаточен.

---

## Установка проекта

### Самый быстрый способ (Windows, всё в одном)

```bat
install.bat
```

Этот файл автоматически запустит все необходимые скрипты:
- `install.ps1` — создаёт venv, устанавливает зависимости, RAG, .env, папку logs
- `install-foundry.ps1` — устанавливает Microsoft Foundry Local (AI backend)

Если возникнут ошибки, следуйте подсказкам в окне или смотрите INSTALL.md ниже.

### Быстрый способ (PowerShell)

```powershell
# Стандартная установка (venv + зависимости + .env + logs/)
.\install.ps1

# С RAG зависимостями (torch, sentence-transformers, faiss-cpu, ~2 GB)
.\install.ps1  # RAG устанавливается по умолчанию

# Без RAG
.\install.ps1 -SkipRag

# Переустановить venv с нуля
.\install.ps1 -Force
```

Или через GUI:

```powershell
.\install-gui.ps1
```

### Ручная установка

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
mkdir logs
copy .env.example .env
```

RAG зависимости отдельно (опционально):

```powershell
python install_rag_deps.py
```

---

## Запуск AI бэкенда

Выберите **один** из вариантов. Сервер автоматически найдёт запущенный бэкенд.

---

### Вариант A — Microsoft Foundry Local

Официальный бэкенд. Работает с ONNX моделями.

```powershell
# Установка через скрипт
.\install-foundry.ps1

# Или вручную через winget
winget install Microsoft.FoundryLocal
foundry service start
foundry model download qwen2.5-0.5b-instruct-generic-cpu
```

Доступные модели:

| Модель | Размер | Описание |
|--------|--------|----------|
| `qwen2.5-0.5b-instruct-generic-cpu` | ~300 MB | Самая лёгкая |
| `qwen2.5-7b-instruct-generic-cpu` | ~4 GB | Средняя |
| `deepseek-r1-distill-qwen-7b-generic-cpu` | ~4 GB | Рассуждения |

Проверка:

```powershell
curl http://localhost:50477/v1/models
```

> Foundry использует динамический порт. Сервер найдёт его автоматически через `tasklist` + `netstat`.

---

### Вариант B — llama.cpp (GGUF модели)

Используйте если у вас есть `.gguf` файл (например, `gemma-2-2b-it-Q6_K.gguf`).

**Установка llama.cpp:**

Скачать готовый бинарник: https://github.com/ggerganov/llama.cpp/releases

Выбрать `llama-*-bin-win-*.zip` для Windows.

**Запуск:**

```powershell
# Порт 50477 — проект найдёт его автоматически
llama-server.exe -m путь\к\модели.gguf --port 50477 --host 127.0.0.1

# С параметрами
llama-server.exe -m путь\к\модели.gguf --port 50477 --host 127.0.0.1 -c 4096 -ngl 0
```

| Параметр | Описание |
|----------|----------|
| `-m` | Путь к .gguf файлу |
| `--port 50477` | Порт (проверяется автоматически) |
| `-c` | Размер контекста в токенах |
| `-ngl 0` | Только CPU (без GPU) |

Проверка:

```powershell
curl http://localhost:50477/v1/models
```

---

### Вариант C — Ollama

**Установка:** https://ollama.com/download

**Запуск с GGUF файлом:**

Создать файл `Modelfile`:

```
FROM ./gemma-2-2b-it-Q6_K.gguf
```

```powershell
ollama create gemma2-local -f Modelfile
ollama serve
```

Указать URL в `.env`:

```env
FOUNDRY_BASE_URL=http://localhost:11434/v1
```

Проверка:

```powershell
curl http://localhost:11434/v1/models
```

---

## Запуск сервера

```powershell
venv\Scripts\python.exe run.py
```

Или через лаунчер:

```powershell
.\launcher.ps1 -Mode quick
```

---

## Проверка работы

```powershell
# Статус сервиса
curl http://localhost:9696/api/v1/health

# Список моделей
curl http://localhost:9696/api/v1/models

# Тестовая генерация
curl -X POST http://localhost:9696/api/v1/generate `
  -H "Content-Type: application/json" `
  -d "{\"prompt\": \"Привет!\", \"max_tokens\": 100}"
```

- Веб-интерфейс: http://localhost:9696
- API документация: http://localhost:9696/docs

---

## Устранение проблем

**AI бэкенд не найден:**

```powershell
# Проверить что сервер отвечает
curl http://localhost:50477/v1/models

# Указать URL явно в .env
FOUNDRY_BASE_URL=http://localhost:50477/v1
```

**Порт 9696 занят:**

```powershell
netstat -ano | findstr :9696
python stop.py
```

**Ошибки зависимостей:**

```powershell
venv\Scripts\pip.exe install -r requirements.txt --no-cache-dir
```

**Логи:**

```powershell
type logs\app.log
```

---

## Файлы установки

| Файл | Назначение |
|------|-----------|
| `install.ps1` | Главный установщик (venv + зависимости + .env + logs) |
| `install-foundry.ps1` | Установка Microsoft Foundry Local через winget |
| `install-gui.ps1` | GUI установщик (Windows Forms) |
| `install_rag_deps.py` | Установка RAG зависимостей (torch, faiss, sentence-transformers) |
| `install-models.ps1` | Скачивание моделей по умолчанию (Foundry + HuggingFace) |
| `bin\Python-3.11.9.zip` | Локальный интерпретатор Python для офлайн-установки |

---

© 2025 AiStros Team — https://aistros.com
