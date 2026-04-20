# Установка FastAPI Foundry

## Системные требования

- Windows 10/11
- Python 3.11+ (или будет установлен автоматически из `bin/Python-3.11.9.zip`)
- PowerShell 5+
- Интернет-соединение (для загрузки Tesseract OCR и Foundry Local)

---

## Автоматическая установка

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

`install.ps1` выполняет следующие шаги:

1. Ищет Python 3.11+ в системе. Если не найден — предлагает установить из `bin\Python-3.11.9.zip`
2. Создаёт виртуальное окружение `venv\`
3. Обновляет `pip`
4. Устанавливает зависимости из `requirements.txt`
5. Опционально устанавливает RAG-зависимости (`sentence-transformers`, `faiss-cpu`) — можно пропустить флагом `-SkipRag`
6. **Устанавливает Tesseract OCR** — необходим для OCR изображений при индексации RAG
7. Создаёт `.env` из `.env.example` (если `.env` ещё не существует)
8. Создаёт папку `logs\`
9. Если в `bin\` найден архив `llama-*-bin-win-*.zip` — распаковывает и прописывает путь в `.env`
10. Если `foundry` не найден в PATH — предлагает установить через `winget`
11. Опционально загружает модели по умолчанию через `install\install-models.ps1`

### Параметры install.ps1

```powershell
# Стандартная установка
.\install.ps1

# Пересоздать venv (если что-то сломалось)
.\install.ps1 -Force

# Без RAG зависимостей (экономит ~2 GB)
.\install.ps1 -SkipRag

# Без установки Tesseract OCR
.\install.ps1 -SkipTesseract

# Комбинация флагов
.\install.ps1 -SkipRag -SkipTesseract
```

---

!!! tip "Настройка после установки"
    `install.ps1` автоматически создаёт `.env` из `.env.example`.  
    Все настройки (ключи, токены, порты) доступны через вкладку **Settings** в веб-интерфейсе: **http://localhost:9696**  
    Подробное описание всех параметров: [Конфигурация](configuration.md).

---

## Tesseract OCR

Tesseract OCR — системная программа для распознавания текста на изображениях.  
Используется в RAG-системе при индексации директорий: PNG, JPG, TIFF и изображения внутри PDF-файлов проходят через OCR перед добавлением в FAISS-индекс.

### Автоматическая установка (через install.ps1)

`install.ps1` автоматически вызывает `install\install-tesseract.ps1`, который:

1. Скачивает установщик Tesseract 5.x с GitHub (UB-Mannheim)
2. Устанавливает в `C:\Program Files\Tesseract-OCR` в тихом режиме
3. Добавляет путь в системный PATH
4. Прописывает `TESSERACT_CMD` в файл `.env`

### Ручная установка

Если автоматическая установка не сработала:

```powershell
# Запустить установщик Tesseract отдельно
powershell -ExecutionPolicy Bypass -File .\install\install-tesseract.ps1
```

Или вручную:

1. Скачать установщик: <https://github.com/UB-Mannheim/tesseract/wiki>  
   Файл: `tesseract-ocr-w64-setup-5.x.x.exe`
2. При установке отметить языковые пакеты **Russian** и **English**
3. Путь установки: `C:\Program Files\Tesseract-OCR`
4. Добавить в PATH вручную:

```powershell
[Environment]::SetEnvironmentVariable(
    'Path',
    $env:Path + ';C:\Program Files\Tesseract-OCR',
    [EnvironmentVariableTarget]::Machine
)
```

5. Перезапустить PowerShell и проверить:

```powershell
tesseract --version
```

### Переменная TESSERACT_CMD

`install-tesseract.ps1` автоматически добавляет в `.env`:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

Эта переменная используется `pytesseract` как явный путь к бинарнику — на случай если Tesseract не попал в PATH текущей сессии.

### Что происходит без Tesseract

Если Tesseract не установлен:

- PDF, DOCX, HTML, Markdown, JSON, YAML, исходный код — **индексируются нормально**
- PNG, JPG, TIFF и другие изображения — **пропускаются** при индексации директории
- Изображения внутри PDF — **пропускаются** (текст страниц извлекается)
- В логах появится предупреждение: `⚠️ TextExtractor not available`

---

## Установка бэкендов ИИ

### Microsoft Foundry Local (рекомендуется)

```powershell
# Через winget
winget install Microsoft.FoundryLocal

# Или через скрипт
.\install\install-foundry.ps1
```

После установки Foundry запускается автоматически при старте `start.ps1`.

### HuggingFace CLI

```powershell
.\install\install-huggingface-cli.ps1
```

Устанавливает `huggingface-hub` и запускает `hf auth login`.

### llama.cpp

Бинарники для Windows x64 уже включены в `bin\llama-b8802-bin-win-cpu-x64\`.
`install.ps1` автоматически прописывает путь в `.env`.

---

## Docker

```powershell
docker-compose build
docker-compose up
```

Или через `docker-compose up -d` для фонового режима.

Веб-интерфейс: **http://localhost:9696**

---

## Проверка установки

```powershell
# Проверить конфигурацию
venv\Scripts\python.exe check_env.py

# Диагностика системы
venv\Scripts\python.exe diagnose.py

# Проверить Tesseract
tesseract --version

# Запустить сервер
.\start.ps1
```

После запуска:

- Веб-интерфейс: http://localhost:9696
- Swagger UI: http://localhost:9696/docs
- Health check: http://localhost:9696/api/v1/health
