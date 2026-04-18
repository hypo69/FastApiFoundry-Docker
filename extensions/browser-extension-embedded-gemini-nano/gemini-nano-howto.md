# Руководство по работе с Gemini Nano в Google Chrome

Это руководство содержит инструкции по активации, проверке и программному использованию локальной модели Gemini Nano (on-device AI) внутри браузера Google Chrome.

## 1. Что такое Gemini Nano?

Gemini Nano — это облегченная версия большой языковой модели от Google, предназначенная для работы непосредственно на устройстве пользователя. Она используется для генерации текста, суммаризации и работы AI-функций без отправки данных на сервер.

**Где хранятся веса модели:**
`%LOCALAPPDATA%\Google\Chrome\User Data\OptimizationGuideOnDeviceModel` (размер ~4+ ГБ).

---

## 2. Подготовка и активация (chrome://flags)

Для работы локального API необходимо включить экспериментальные флаги. Скопируйте и вставьте следующие пути в адресную строку Chrome:

1.  **Enables optimization guide on device**
    *   **URL:** `chrome://flags/#optimization-guide-on-device-model`
    *   **Значение:** `Enabled BypassPerfRequirement` (игнорирует аппаратные ограничения).
2.  **Prompt API for Gemini Nano**
    *   **URL:** `chrome://flags/#prompt-api-for-gemini-nano`
    *   **Значение:** `Enabled`

После изменения флагов нажмите кнопку **Relaunch** для перезапуска браузера.

---

## 3. Принудительная загрузка модели

Если API возвращает `undefined`, проверьте статус загрузки компонентов:

1.  Перейдите на страницу `chrome://components/`.
2.  Найдите пункт **Optimization Guide On Device Model**.
3.  Нажмите **Check for update** (Проверить обновления).
4.  Дождитесь статуса **Component updated** (версия должна стать отличной от 0.0.0.0).

*Совет: Если загрузка не начинается, откройте консоль (F12) и выполните `await window.ai.languageModel.create();`. Это инициирует запрос к сервису.*

---

## 4. Проверка готовности через консоль

Выполните этот скрипт в консоли разработчика, чтобы проверить, готова ли модель к работе:

```javascript
async function checkNano() {
    if (!window.ai || !window.ai.languageModel) {
        console.error("Prompt API не поддерживается или флаги выключены.");
        return;
}
    const capabilities = await window.ai.languageModel.capabilities();
    console.log("Статус модели:", capabilities.available); // Должно быть "readily"
}
checkNano();
```

---

## 5. Программное использование (Prompt API)

### Простой запрос
```javascript
const session = await window.ai.languageModel.create({
    temperature: 0.7,
    topK: 3
});

const result = await session.prompt("Объясни принцип работы Docker за одно предложение.");
console.log(result);
```

### Стриминг ответа (как в ChatGPT)
```javascript
const session = await window.ai.languageModel.create();
const stream = session.promptStreaming("Напиши короткое стихотворение о программировании.");

for await (const chunk of stream) {
    process.stdout.write(chunk); // Или обновление UI
}
```

---

## 6. Использование в расширениях (Manifest V3)

Для использования в Service Worker расширения убедитесь, что API вызывается в контексте, где доступен объект `self.ai`.

**Пример в background.js:**
```javascript
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === 'AI_PROMPT') {
        handleAi(msg.text).then(sendResponse);
        return true;
    }
});
```

---

## 7. Устранение неполадок

*   **Ошибка "BypassPerfRequirement":** Если ваше железо (RAM/GPU) не проходит тесты Google, модель не загрузится без установленного флага `BypassPerfRequirement`.
*   **Место на диске:** Для работы требуется минимум 22 ГБ свободного места на системном диске для распаковки и кэширования.
*   **Язык интерфейса:** В редких случаях модель требует, чтобы основным языком Chrome был установлен **English (US)**.