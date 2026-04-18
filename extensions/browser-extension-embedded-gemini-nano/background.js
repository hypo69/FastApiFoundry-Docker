// =============================================================================
// Название процесса: Фоновый сервис управления ИИ-сессией
// =============================================================================
// Описание:
//   Управление жизненным циклом сессии Gemini Nano. Обработка входящих 
//   подключений через порты для реализации потоковой передачи данных (streaming).
//
// File: background.js
// Project: AiStros
// Author: hypo69
// Copyright: © 2026 hypo69
// =============================================================================

let aiSession = null;

/**
 * Initialization of the AI session.
 * 
 * WHY SINGLETON:
 *   Создание сессии — ресурсоемкая операция. Повторное использование существующей
 *   сессии ускоряет отклик и сохраняет контекст диалога.
 */
async function getSession() {
    if (aiSession) return aiSession;

    // API availability check
    if (!self.ai || !self.ai.languageModel) {
        throw new Error('Prompt API not supported in this Chrome version');
    }

    aiSession = await self.ai.languageModel.create({
        temperature: 0.7,
        topK: 3
    });
    return aiSession;
}

/**
 * Port connection listener for streaming.
 * 
 * ПОЧЕМУ PORT (Long-lived connection):
 *   Стандартный sendMessage не поддерживает отправку множества сообщений
 *   на один запрос. Port позволяет стримить чанки текста по мере генерации.
 */
chrome.runtime.onConnect.addListener((port) => {
    if (port.name !== 'gemini-nano-stream') return;

    port.onMessage.addListener(async (msg) => {
        if (msg.type === 'PROMPT') {
            try {
                const session = await getSession();
                
                // Streaming execution check
                if (session.promptStreaming) {
                    const stream = session.promptStreaming(msg.payload);
                    for await (const chunk of stream) {
                        port.postMessage({ type: 'CHUNK', data: chunk });
                    }
                    port.postMessage({ type: 'DONE' });
                } else {
                    // Fallback for non-streaming versions
                    const response = await session.prompt(msg.payload);
                    port.postMessage({ type: 'CHUNK', data: response });
                    port.postMessage({ type: 'DONE' });
                }
            } catch (error) {
                port.postMessage({ type: 'ERROR', data: error.message });
            }
        }

        /**
         * Reset of the session and history.
         */
        if (msg.type === 'RESET') {
            if (aiSession) aiSession.destroy();
            aiSession = null;
            port.postMessage({ type: 'RESET_DONE' });
        }
    });
});