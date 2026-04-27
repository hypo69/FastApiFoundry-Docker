# 📦 Скрипты установки (install/)

Вспомогательные скрипты для автоматизации первичной настройки и развёртывания.
Вызываются основным установщиком `install.ps1`, но могут запускаться отдельно.

## Файлы

| Скрипт | Описание |
|---|---|
| `Install-Foundry.ps1` | Установка Microsoft Foundry Local CLI через `winget` |
| `Install-Models.ps1` | Загрузка базовых моделей для Foundry и RAG |
| `Install-HuggingFaceCli.ps1` | Установка `huggingface-hub` и авторизация `hf auth login` |
| `Install-Tesseract.ps1` | Загрузка и тихая установка Tesseract OCR 5.x |
| `Install-Shortcuts.ps1` | Создание ярлыков на рабочем столе для быстрого запуска |
| `Install-Autostart.ps1` | Настройка автозапуска сервера при входе в систему |
| `Setup-Env.ps1` | Интерактивная настройка файла `.env` |
| `Make-Ico.ps1` | Конвертация PNG-иконок в `icon.ico` |
| `ReinstallFoundry.ps1` | Полная переустановка Foundry Local (CI/QA) |

## Использование

```powershell
# Установить Foundry Local
.\install\Install-Foundry.ps1

# Скачать модели по умолчанию
.\install\Install-Models.ps1

# Установить HuggingFace CLI и авторизоваться
.\install\Install-HuggingFaceCli.ps1

# Установить Tesseract OCR
.\install\Install-Tesseract.ps1

# Настроить .env интерактивно
.\install\Setup-Env.ps1

# Создать ярлыки на рабочем столе
.\install\Install-Shortcuts.ps1

# Зарегистрировать автозапуск
.\install\Install-Autostart.ps1
```

## Примечание

Все скрипты вызываются автоматически из `install.ps1` при первичной установке.
Запускайте их отдельно только для обновления отдельных компонентов.
