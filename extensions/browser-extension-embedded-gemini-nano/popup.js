/**
 * =============================================================================
 * Название процесса: Логика взаимодействия пользователя с ИИ
 * =============================================================================
 * Описание:
 *   Обработка ввода пользователя, управление состоянием UI во время генерации
 *   и отображение входящего потока данных от Gemini Nano.
 *
 * File: popup.js
 * Project: AiStros
 * Author: hypo69
 * Copyright: © 2026 hypo69
 * =============================================================================
 */

const inputField = document.getElementById('user-input');
const sendButton = document.getElementById('send-btn');
const chatArea = document.getElementById('chat-area');
const resetButton = document.getElementById('reset-btn');

/**
 * Stream initialization.
 * Connects to background service worker and handles response chunks.
 */
function sendPrompt() {
    const text = inputField.value.trim();
    if (!text) return;

    // Clear previous output and disable UI
    chatArea.innerText = 'Thinking...';
    inputField.disabled = true;
    sendButton.disabled = true;

    const port = chrome.runtime.connect({ name: 'gemini-nano-stream' });

    port.postMessage({ type: 'PROMPT', payload: text });

    port.onMessage.addListener((msg) => {
        if (msg.type === 'CHUNK') {
            // Full text replacement or appending depending on API version behavior
            chatArea.innerText = msg.data;
        } else if (msg.type === 'DONE') {
            inputField.disabled = false;
            sendButton.disabled = false;
            inputField.value = '';
            port.disconnect();
        } else if (msg.type === 'ERROR') {
            chatArea.innerText = `Error: ${msg.data}`;
            inputField.disabled = false;
            sendButton.disabled = false;
        }
    });
}

/**
 * UI events registration.
 */
sendButton.addEventListener('click', sendPrompt);

inputField.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendPrompt();
    }
});

resetButton.addEventListener('click', () => {
    chrome.runtime.connect({ name: 'gemini-nano-stream' }).postMessage({ type: 'RESET' });
    chatArea.innerText = 'Session reset. Ready for new questions.';
});