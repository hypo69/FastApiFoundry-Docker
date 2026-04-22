# Установка FastAPI Foundry

## Системные требования

- Windows 10/11
- Python 3.11+ (или распаковывается из `bin/Python-3.11.9.zip`)
- PowerShell 5+
- Интернет-соединение

---

## Три способа установки

| | `install.bat` | `install.ps1` | Вручную |
|---|---|---|---|
| **Запуск** | Двойной клик | PowerShell | Командная строка |
| **Python** | Из `bin\Python-3.11.9.zip` | Ищет в PATH | Любой |
| **GUI** | ✅ Открывает браузер | ✅ Открывает браузер | ❌ Только консоль |
| **Когда** | Первая установка | Первая установка | CI, Docker, опытные |

---

## GUI-установка (рекомендуется)

### Через install.bat (двойной клик)

```
install.bat
  ├─ Распаковывает bin\Python-3.11.9.zip → bin\Python-3.11.9\
  ├─ Создаёт venv\
  ├─ pip install fastapi uvicorn python-dotenv psutil
  └─ python install\server.py  → браузер http://localhost:9698
```

### Через install.ps1 (PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

```
install.ps1
  ├─ Проверяет Python 3.11+ в PATH
  ├─ Создаёт venv\
  ├─ pip install -r requirements.txt
  └─ python install\server.py  → браузер http://localhost:9698
```

### Интерфейс установщика (http://localhost:9698)

| Вкладка | Что устанавливает | Опция |
|---|---|---|
| **Core Packages** | `requirements.txt` — FastAPI, uvicorn, aiohttp | — обязательно |
| **RAG / ML** | `requirements-rag.txt` — torch, transformers, faiss (~3-5 GB) | ☑ Skip |
| **Text Extraction** | `requirements-extras.txt` — PDF, DOCX, OCR, архивы | ☑ Skip |
| **Docs / SDK / Tests** | `requirements-dev.txt` — MkDocs, foundry-local-sdk, pytest | ☑ Skip |
| **.env File** | Создаёт `.env` из `.env.example` | поле HF Token |
| **Foundry Local** | `install-foundry.ps1` — winget install | ☑ Skip |
| **Download Models** | `install-models.ps1` — модели по умолчанию | ☑ Skip |
| **Desktop Shortcuts** | `install-shortcuts.ps1` — ярлыки на рабочем столе | ☑ Skip |

---

## CLI-установка (без браузера)

Для автоматизации, CI или если GUI не нужен — все шаги вручную:

```powershell
# 1. Создать venv (если нет)
python -m venv venv

# 2. Активировать
venv\Scripts\Activate.ps1

# 3. Обновить pip
python -m pip install --upgrade pip

# 4. Основные зависимости (обязательно)
pip install -r requirements.txt

# 5. RAG + ML (опционально, ~3-5 GB)
pip install -r requirements-rag.txt

# 6. Извлечение текста — PDF, DOCX, OCR (опционально)
pip install -r requirements-extras.txt

# 7. Docs + SDK + тесты (опционально)
pip install -r requirements-dev.txt

# 8. Создать .env
copy .env.example .env
notepad .env

# 9. Установить Foundry (опционально)
winget install Microsoft.FoundryLocal

# 10. Запустить сервер
.\start.ps1
```

### Параметры install.ps1

```powershell
.\install.ps1              # стандартная установка + GUI
.\install.ps1 -Force       # пересоздать venv
.\install.ps1 -SkipRag     # без RAG (~2 GB экономии)
.\install.ps1 -SkipTesseract  # без Tesseract OCR
```

---

## PID-файлы процессов

Все запущенные процессы отслеживаются через PID-файлы. `start.ps1` читает их при каждом запуске и завершает старые процессы перед стартом новых.

| Процесс | PID-файл | Кто пишет | Кто читает и убивает |
|---|---|---|---|
| **FastAPI** (порт 9696) | `%TEMP%\fastapi-foundry.pid` | `start.ps1` | `start.ps1` при следующем запуске |
| **Installer UI** (порт 9698) | `install\.installer.pid` | `install\server.py` | `start.ps1` (этап 6.5) или кнопка Finish |
| **MkDocs** (порт 9697) | нет файла | — | `start.ps1` по порту через `Get-NetTCPConnection` |
| **llama.cpp** (порт 9780) | нет файла | — | `start.ps1` по порту через `Get-NetTCPConnection` |
| **Foundry** | нет файла | — | не трогается намеренно |

### Жизненный цикл installer PID

```
install.bat / install.ps1
  └─ python install\server.py
       ├─ пишет PID → install\.installer.pid
       ├─ открывает браузер
       └─ ждёт...
           ├─ пользователь нажал Finish
           │    └─ POST /api/shutdown → удаляет .installer.pid → SIGTERM
           └─ пользователь закрыл браузер (сервер жив)
                └─ start.ps1 читает .installer.pid → Kill → удаляет файл
```

### Жизненный цикл FastAPI PID

```
start.ps1
  ├─ читает %TEMP%\fastapi-foundry.pid
  │    └─ Kill старый процесс → удалить файл
  ├─ Start-Process python run.py → PassThru
  └─ $proc.Id → %TEMP%\fastapi-foundry.pid
       └─ finally: Remove-Item (при завершении start.ps1)
```

!!! info "Почему разные места хранения"
    `%TEMP%\fastapi-foundry.pid` — стандартное место для временных файлов процессов,
    доступно из любого скрипта без знания пути проекта.
    `install\.installer.pid` — рядом со скриптом установщика, удаляется вместе с проектом.

---

## Файлы зависимостей

| Файл | Размер | Назначение |
|---|---|---|
| `requirements.txt` | ~50 MB | Ядро: FastAPI, uvicorn, aiohttp, pydantic, mcp |
| `requirements-rag.txt` | ~3-5 GB | RAG: torch, transformers, faiss, sentence-transformers |
| `requirements-extras.txt` | ~200 MB | Текст: PDF, DOCX, OCR, архивы |
| `requirements-dev.txt` | ~100 MB | Dev: MkDocs, foundry-local-sdk, pytest |

---

## Tesseract OCR

Нужен для OCR изображений при RAG-индексации (PNG, JPG, TIFF, изображения в PDF).

```powershell
# Автоматически через скрипт
.\install\install-tesseract.ps1

# Или вручную
winget install UB-Mannheim.TesseractOCR
```

После установки `install-tesseract.ps1` добавляет в `.env`:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

Без Tesseract: изображения пропускаются при индексации, всё остальное работает нормально.

---

## Проверка установки

```powershell
venv\Scripts\python.exe check_env.py
venv\Scripts\python.exe diagnose.py
tesseract --version
.\start.ps1
```

После запуска:

- Веб-интерфейс: http://localhost:9696
- Swagger UI: http://localhost:9696/docs
- Health check: http://localhost:9696/api/v1/health
