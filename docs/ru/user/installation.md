# Установка FastAPI Foundry

## Системные требования

- Windows 10/11
- Python 3.11+
- PowerShell 7+
- Интернет-соединение

---

## Два способа установки

| | `install.bat` | `install.ps1` |
|---|---|---|
| **Запуск** | Двойной клик | PowerShell |
| **Python** | Из `bin\Python-3.11.9.zip` если нет в PATH | Ищет в PATH |
| **Когда** | Первая установка, нет PS7 | Повторная установка, CI |

Оба варианта — только терминал, без браузера.

---

## Через install.bat (рекомендуется для первой установки)

```
install.bat
  ├─ Проверяет PowerShell 7+ (устанавливает через winget/curl/MSI если нет)
  └─ Запускает install.ps1 через pwsh.exe
```

Двойной клик по `install.bat` в проводнике.

---

## Через install.ps1 (PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

### Параметры

| Параметр | Описание |
|---|---|
| `-Force` | Пересоздать venv (архивирует текущий `requirements.txt`) |
| `-SkipRag` | Пропустить RAG-зависимости (~3-5 GB) |
| `-SkipTesseract` | Пропустить установку Tesseract OCR |

### Что делает install.ps1

```
install.ps1
  ├─ 0. Проверка PowerShell 7+
  ├─ 1. Поиск Python 3.11+ (или распаковка из bin\Python-3.11.9.zip)
  ├─ 2. Создание venv\
  ├─ 3. pip install -r requirements.txt
  ├─ 4. pip install sentence-transformers faiss-cpu  (если не -SkipRag)
  ├─ 5. install\install-tesseract.ps1               (если не -SkipTesseract)
  ├─ 6. Создание .env из .env.example               (если нет)
  ├─ 7. Создание logs\
  ├─ 8. Распаковка llama.cpp из bin\llama-*.zip     (если есть)
  ├─ 9. Установка Foundry Local через winget        (интерактивно)
  ├─ 10. Загрузка моделей по умолчанию              (интерактивно)
  └─ 11. Создание ярлыков на рабочем столе
```

---

## Ручная установка (CLI)

Для автоматизации или Docker:

```powershell
# 1. Создать venv
python -m venv venv

# 2. Установить зависимости
venv\Scripts\pip.exe install -r requirements.txt

# 3. Создать .env
Copy-Item .env.example .env
notepad .env

# 4. Установить Foundry (опционально)
winget install Microsoft.FoundryLocal

# 5. Запустить
.\start.ps1
```

---

## Настройка .env

После установки отредактируйте `.env`:

```env
# Foundry (определяется автоматически если пусто)
FOUNDRY_BASE_URL=http://localhost:50477/v1

# HuggingFace (для закрытых моделей: Gemma, Llama)
HF_TOKEN=hf_ваш_токен
HF_MODELS_DIR=D:\models

# llama.cpp (опционально)
LLAMA_MODEL_PATH=D:\models\model.gguf
LLAMA_AUTO_START=false
```

Или через мастер настройки:

```powershell
.\install\setup-env.ps1
```

---

## Tesseract OCR

Нужен для OCR изображений при RAG-индексации (PNG, JPG, TIFF, изображения в PDF).

```powershell
# Автоматически
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

## Файлы зависимостей

| Файл | Размер | Назначение |
|---|---|---|
| `requirements.txt` | ~50 MB | Всё: FastAPI, RAG, ML, PDF, OCR, тесты |

Все зависимости объединены в один файл `requirements.txt`.

---

## Автозапуск при входе в Windows

### Как это работает

```
Вход пользователя
  └─ Планировщик задач Windows (AtLogOn)
       └─ autostart.ps1 (скрыто, без окна)
            └─ start.ps1 (весь вывод → logs/autostart.log)
                 └─ FastAPI сервер на http://localhost:9696
```

`autostart.ps1` — обёртка над `start.ps1`:
- запускает его через `powershell.exe -NonInteractive -NoProfile -WindowStyle Hidden`
- перехватывает stdout/stderr, очищает ANSI-коды, пишет в `logs/autostart.log`
- опционально устанавливает PowerShell 7 из `bin/PowerShell-7.4.6-win-x64.msi` если не найден

### Регистрация в Планировщике задач (Task Scheduler)

Требует запуска от имени администратора:

```powershell
# Установить автозапуск
powershell -ExecutionPolicy Bypass -File .\install\install-autostart.ps1

# Удалить автозапуск
powershell -ExecutionPolicy Bypass -File .\install\install-autostart.ps1 -Uninstall
```

Что регистрирует `install-autostart.ps1`:

| Параметр | Значение |
|---|---|
| Имя задачи | `FastApiFoundry-Autostart` |
| Триггер | `AtLogOn` — при входе любого пользователя |
| Уровень прав | `RunLevel Highest` (администратор) |
| Окно | Скрыто (`-WindowStyle Hidden`) |
| Перезапуски | 3 попытки с интервалом 1 минута |
| Лимит времени | Без ограничений |
| Лог | `logs/autostart.log` |

### Ярлыки на рабочем столе

`install.ps1` создаёт два ярлыка на рабочем столе:

| Ярлык | Скрипт | Окно |
|---|---|---|
| **AI Assistant** | `start.ps1` | Видимое окно PowerShell |
| **AI Assistant (Silent)** | `autostart.ps1` | Скрытое окно, без консоли |

Создать ярлыки вручную:

```powershell
powershell -ExecutionPolicy Bypass -File .\install\install-shortcuts.ps1
```

### Проверка автозапуска

```powershell
# Просмотреть задачу в планировщике
Get-ScheduledTask -TaskName 'FastApiFoundry-Autostart'

# Просмотреть лог запуска
Get-Content logs\autostart.log -Tail 30

# Запустить задачу вручную (для теста)
Start-ScheduledTask -TaskName 'FastApiFoundry-Autostart'
```

### Остановка всех сервисов

В silent mode нет видимого окна — для остановки используйте `stop.ps1`:

```powershell
# Остановить FastAPI, llama.cpp, MkDocs
powershell -ExecutionPolicy Bypass -File .\stop.ps1

# То же + остановить Foundry Local
powershell -ExecutionPolicy Bypass -File .\stop.ps1 -StopFoundry
```

`stop.ps1` останавливает по порядку:

| Шаг | Сервис | Метод |
|---|---|---|
| 1 | FastAPI (9696) | PID-файл `%TEMP%\fastapi-foundry.pid`, затем по порту |
| 2 | llama.cpp (9780) | По порту из `config.json` |
| 3 | MkDocs (9697) | По порту из `config.json` |
| 4 | Foundry Local | Только с `-StopFoundry` |

!!! warning "Foundry не останавливается по умолчанию"
    Foundry — системный сервис Microsoft. Его остановка выгрузит загруженную модель из памяти.
    Используйте `-StopFoundry` осознанно.

---

## Проверка установки

```powershell
venv\Scripts\python.exe check_env.py
venv\Scripts\python.exe diagnose.py
.\start.ps1
```

После запуска:

- Веб-интерфейс: http://localhost:9696
- Swagger UI: http://localhost:9696/docs
- Health check: http://localhost:9696/api/v1/health
