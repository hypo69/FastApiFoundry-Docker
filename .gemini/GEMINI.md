<!--
===============================================================================
Название процесса: Конфигурация для Gemini AI
===============================================================================
Описание:
    Файл конфигурации и настроек для интеграции с Gemini AI в проекте FastAPI Foundry.
    Содержит специфичные настройки и параметры для работы с Gemini моделями.

Примеры:
    Использование Gemini API:
    # Настройка API ключа
    export GEMINI_API_KEY="your-api-key"
    
    # Запуск с Gemini
    python run.py --provider gemini

File: GEMINI.md
Project: FastApiFoundry (Docker)
Version: 0.2.1
Author: hypo69
Copyright: © 2026 hypo69
Copyright: © 2026 hypo69
Date: 9 декабря 2025
===============================================================================
-->

# 🤖 Gemini AI Integration

Интеграция с Google Gemini AI для FastAPI Foundry.

## 🚀 Настройка

### 1. API Ключ
```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

### 2. Конфигурация
Добавьте в `config.json`:
```json
{
  "gemini": {
    "api_key": "${GEMINI_API_KEY}",
    "model": "gemini-pro",
    "temperature": 0.7
  }
}
```

## 📚 Документация

Подробная документация доступна в [основном README](README.md).

---
**[⬆️ Назад к корневому README](README.md)**