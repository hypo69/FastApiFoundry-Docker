/**
 * =============================================================================
 * Название процесса: Модуль управления моделями
 * =============================================================================
 * Описание:
 *   Клиентская логика для взаимодействия с API загрузки/выгрузки моделей.
 *   Связывание действий пользователя в UI с HTTP запросами.
 *
 * File: static/js/models.js
 * Project: FastApiFoundry (Docker)
 * Version: 0.6.0
 * Author: hypo69
 * =============================================================================
 */

/**
 * Обновление списка доступных моделей.
 * 
 * ПОЧЕМУ ЭТО ВАЖНО:
 *   Обеспечение актуальности данных в выпадающих списках выбора моделей 
 *   на основе текущего состояния файловой системы и подключенных провайдеров.
 */
async function fetchAvailableModels() {
    console.log('Запрос списка доступных моделей...');
    
    try {
        const response = await fetch('/v1/models/list', {
            headers: {
                'X-API-Key': localStorage.getItem('api_key') || ''
            }
        });

        if (!response.ok) {
            throw new Error(`Ошибка загрузки списка: ${response.status}`);
        }

        const data = await response.json();
        return data.models || [];
    } catch (error) {
        console.error(`Сбой при получении моделей: ${error.message}`);
        return [];
    }
}

/**
 * Выполнение запроса на загрузку модели.
 * 
 * ПОЧЕМУ POST:
 *   Загрузка модели требует передачи параметров конфигурации (settings), 
 *   что лучше всего реализуется через тело JSON запроса.
 * 
 * @param {string} modelId - Идентификатор целевой модели.
 */
async function requestModelLoad(modelId) {
    console.log(`Инициация загрузки: ${modelId}`);
    
    try {
        const response = await fetch('/v1/models/load', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': localStorage.getItem('api_key') || ''
            },
            body: JSON.stringify({
                model_id: modelId,
                settings: {
                    temperature: 0.7
                }
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка сервера при загрузке');
        }
        
        console.log('Загрузка завершена успешно');
    } catch (error) {
        console.error(`Ошибка обработки запроса: ${error.message}`);
        alert(`Не удалось загрузить модель: ${error.message}`);
    }
}

/**
 * Выполнение запроса на выгрузку активной модели.
 * 
 * ПОЧЕМУ ЭТО НУЖНО:
 *   Освобождение системных ресурсов (VRAM/RAM) перед выполнением тяжелых задач.
 */
async function requestModelUnload() {
    console.log('Инициация выгрузки активной модели');
    
    try {
        const response = await fetch('/v1/models/unload', {
            method: 'POST',
            headers: {
                'X-API-Key': localStorage.getItem('api_key') || ''
            }
        });

        if (response.ok) {
            console.log('Модель успешно выгружена');
        } else {
            throw new Error('Сбой при попытке выгрузки');
        }
    } catch (error) {
        console.error(`Ошибка связи: ${error.message}`);
    }
}