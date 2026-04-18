# 📦 Скрипты установки (install/)

Вспомогательные скрипты для автоматизации первичной настройки и развёртывания.
Вызываются основным установщиком `install.ps1`, но могут запускаться отдельно.

## Файлы

| Скрипт | Описание |
|---|---|
| `install-foundry.ps1` | Установка Microsoft Foundry Local CLI через `winget` |
| `install-models.ps1` | Загрузка базовых моделей для Foundry и RAG |
| `install-huggingface-cli.ps1` | Установка `huggingface-hub` и авторизация `hf auth login` |
| `install-shortcuts.ps1` | Создание ярлыков на рабочем столе для быстрого запуска |
| `install-autostart.ps1` | Настройка автозапуска сервера при входе в систему |
| `setup-env.ps1` | Интерактивная настройка файла `.env` |

## Использование

```powershell
# Установить Foundry Local
.\install\install-foundry.ps1

# Скачать модели по умолчанию
.\install\install-models.ps1

# Установить HuggingFace CLI и авторизоваться
.\install\install-huggingface-cli.ps1

# Настроить .env интерактивно
.\install\setup-env.ps1

# Создать ярлыки на рабочем столе
.\install\install-shortcuts.ps1
```

## Примечание

Все скрипты вызываются автоматически из `install.ps1` при первичной установке.
Запускайте их отдельно только для обновления отдельных компонентов.
