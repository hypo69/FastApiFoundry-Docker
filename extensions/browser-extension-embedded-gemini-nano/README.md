# Gemini Nano Assistant (Embedded)

## Описание
Экспериментальное расширение для Chrome, использующее встроенную модель **Gemini Nano** через **Prompt API**. Все вычисления происходят локально на вашем устройстве, данные не отправляются на серверы.

## Структура файлов
- `manifest.json`: Конфигурация расширения (MV3).
- `background.js`: Управление сессией ИИ и потоковой передачей данных.
- `popup.html`: Интерфейс взаимодействия.
- `popup.js`: Обработка действий пользователя.
- `styles.css`: Визуальное оформление (дизайн в стиле `summarizer`).
- `Instruction.md`: Техническое руководство по активации модели в Chrome.

## Требования
1. Google Chrome версии 127+.
2. Активированные флаги:
   - `chrome://flags/#optimization-guide-on-device-model` (Enabled BypassPerfRequirement)
   - `chrome://flags/#prompt-api-for-gemini-nano` (Enabled)
3. Загруженный компонент `Optimization Guide On Device Model` в `chrome://components`.

## Установка
Загрузите папку через `chrome://extensions` -> `Load unpacked`.