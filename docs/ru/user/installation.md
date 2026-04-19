# Установка FastAPI Foundry

## Системные требования

- Windows 10/11
- Python 3.11+ (или будет установлен автоматически из `bin/Python-3.11.9.zip`)
- PowerShell 5+

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
6. Создаёт `.env` из `.env.example` (если `.env` ещё не существует)
7. Создаёт папку `logs\`
8. Если в `bin\` найден архив `llama-*-bin-win-*.zip` — распаковывает и прописывает путь в `.env`
9. Если `foundry` не найден в PATH — предлагает установить через `winget`
10. Опционально загружает модели по умолчанию через `install\install-models.ps1`

### Параметры install.ps1

```powershell
# Стандартная установка
.\install.ps1

# Пересоздать venv (если что-то сломалось)
.\install.ps1 -Force

# Без RAG зависимостей (экономит ~2 GB)
.\install.ps1 -SkipRag
```

---

## Настройка конфигурации

После установки скопируйте `.env.example` в `.env` и заполните секреты:

```powershell
Copy-Item .env.example .env
notepad .env
```

Минимальный `.env` для старта:

```env
# HuggingFace токен (только для закрытых моделей: Gemma, Llama)
HF_TOKEN=hf_ваш_токен

# Foundry URL — только если автоопределение не работает
# FOUNDRY_BASE_URL=http://localhost:50477/v1
```

Все остальные настройки (порты, пути к моделям, флаги автозапуска) — в `config.json`.
Подробнее: [Конфигурация](configuration.md)

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

# Запустить сервер
.\start.ps1
```

После запуска:

- Веб-интерфейс: http://localhost:9696
- Swagger UI: http://localhost:9696/docs
- Health check: http://localhost:9696/api/v1/health
