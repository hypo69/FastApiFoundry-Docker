# Telegram Боты

FastAPI Foundry включает два Telegram бота с разными ролями.

## Архитектура

```
telegram/
├── __init__.py        # Запуск обоих ботов через asyncio.gather
├── admin_bot.py       # Admin Bot — мониторинг и управление
└── helpdesk_bot.py    # HelpDesk Bot — поддержка клиентов
```

```
Клиент → HelpDesk Bot → RAG (профиль "support") → AI модель → ответ
Админ  → Admin Bot   → Foundry / логи / система
```

---

## Admin Bot

Бот для администратора системы. Мониторинг, управление Foundry, работа с логами и RAG.

**Доступ:** ограничен списком `TELEGRAM_ADMIN_IDS`.

### Настройка

В `.env`:

```env
TELEGRAM_ADMIN_TOKEN=токен_от_BotFather
TELEGRAM_ADMIN_IDS=123456789,987654321
```

### Команды

| Команда | Описание |
|---|---|
| `/status` | Статус Foundry: состояние, порт, PID |
| `/stats` | График CPU / RAM / Disk |
| `/foundry_start` | Запустить Foundry сервис |
| `/foundry_stop` | Остановить Foundry сервис |
| `/logs` | Последние 5 ошибок из лога |
| `/get_logs` | Скачать полный файл лога |
| `/clear_logs` | Очистить лог (с подтверждением) |
| `/restart_server` | Перезапустить FastAPI сервер (с подтверждением) |
| `/rag_rebuild` | Инициировать переиндексацию RAG |
| `/rag_status` | Информация об активном RAG индексе |
| `/rag_profiles` | Список RAG профилей с выбором |

### Фоновый мониторинг

Бот автоматически проверяет каждые `status_check_interval` секунд (по умолчанию 300):

- **Foundry статус** — при изменении на `failed` / `stopped` / `unknown` отправляет алерт
- **Диск** — при заполнении > 95% отправляет алерт (один раз до нормализации)

### Загрузка ZIP-архивов

Отправьте боту `.zip` файл — он распакует его в `data/uploads/<имя_архива>/`.  
После этого запустите `/rag_rebuild` для индексации.

---

## HelpDesk Bot

Бот для клиентов. Отвечает на вопросы о системе, используя RAG + активную AI модель.

**Доступ:** открыт для всех пользователей Telegram.

### Настройка

В `.env`:

```env
TELEGRAM_HELPDESK_TOKEN=токен_от_BotFather
```

В `config.json`:

```json
{
  "telegram_helpdesk": {
    "rag_profile": "support"
  }
}
```

### Команды

| Команда | Описание |
|---|---|
| `/start` | Приветствие и инструкция |
| `/help` | То же что `/start` |
| `/new` | Сбросить историю диалога |

### Логика ответа

1. Пользователь отправляет вопрос
2. Бот ищет релевантный контекст в RAG профиле `support` (top-5 чанков)
3. Контекст + вопрос + история диалога отправляются в активную AI модель
4. Ответ возвращается пользователю
5. Диалог сохраняется в `logs/helpdesk_dialogs.jsonl`

### Многоходовые диалоги

Бот хранит последние 6 ходов диалога в памяти (per `chat_id`).  
Команда `/new` сбрасывает историю.

---

## Подготовка RAG профиля для HelpDesk

Создайте профиль `support` и проиндексируйте документацию:

```bash
# Через API
POST /api/v1/helpdesk/rag-profiles
{"name": "support", "description": "Project documentation"}

POST /api/v1/rag/build
{"docs_dir": "./docs", "profile": "support"}
```

Или через веб-интерфейс: таб **Support** → раздел **RAG Profiles** → **Create Profile**.

---

## Запуск

### Вместе с FastAPI сервером

Добавьте в `run.py`:

```python
from telegram import start_all_bots
asyncio.create_task(start_all_bots())
```

### Автономно

```powershell
~venv\Scripts\python.exe -m telegram
```

---

## Диалоги в веб-интерфейсе

Таб **Support** в веб-интерфейсе показывает:

- Список пользователей, написавших в HelpDesk бот
- Историю переписки по каждому пользователю
- Статус бота (активен / отключён)
- Управление RAG профилями

---

## Переменные окружения

| Переменная | Описание |
|---|---|
| `TELEGRAM_ADMIN_TOKEN` | Токен Admin Bot (от @BotFather) |
| `TELEGRAM_ADMIN_IDS` | ID администраторов через запятую |
| `TELEGRAM_HELPDESK_TOKEN` | Токен HelpDesk Bot (от @BotFather) |

## Параметры config.json

| Параметр | По умолчанию | Описание |
|---|---|---|
| `telegram.status_check_interval` | `300` | Интервал мониторинга Foundry (сек) |
| `telegram_helpdesk.rag_profile` | `"support"` | RAG профиль для HelpDesk бота |
