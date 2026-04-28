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
 * Локальное хранилище данных о моделях для быстрой проверки.
 */
let _cachedModelsList = [];

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
        _cachedModelsList = data.models || [];
        return _cachedModelsList;
    } catch (error) {
        console.error(`Сбой при получении моделей: ${error.message}`);
        return [];
    }
}

/**
 * Проверка системных ресурсов (RAM).
 * 
 * @returns {Promise<Object|null>} Данные о памяти.
 */
async function fetchSystemRamStats() {
    try {
        const response = await fetch('/api/v1/system/stats');
        if (!response.ok) return null;
        const data = await response.json();
        return data.success ? data : null;
    } catch (e) {
        return null;
    }
}

/**
 * Проверка соответствия выбранной модели объему оперативной памяти.
 * 
 * ПОЧЕМУ ЭТО ВАЖНО:
 *   Предотвращение критических ошибок системы и зависаний при попытке 
 *   загрузить модель, размер которой превышает доступную RAM.
 */
async function checkModelRamRequirements(modelId) {
    const warningEl = document.getElementById('model-ram-warning');
    if (!warningEl) return;

    // Скрытие предупреждения по умолчанию
    // Hiding the warning by default
    warningEl.style.display = 'none';
    warningEl.className = 'alert alert-warning mt-2 small';

    const model = _cachedModelsList.find(m => m.name === modelId);
    if (!model) return;

    const stats = await fetchSystemRamStats();
    if (!stats || !stats.ram_total_mb) return;

    // Расчет порога (85% от общего объема памяти для учета ОС)
    // Calculation of the threshold (85% of total RAM to account for OS)
    const safetyThreshold = stats.ram_total_mb * 0.85;

    if (model.size_mb > safetyThreshold) {
        warningEl.innerHTML = `
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            <strong>Внимание:</strong> Размер модели (${model.size_mb} MB) 
            слишком велик для вашей оперативной памяти (${Math.round(stats.ram_total_mb)} MB). 
            Это может привести к нестабильной работе системы.
        `;
        warningEl.style.display = 'block';
    }
}

/**
 * Обработка изменения выбора модели.
 * 
 * @param {Event} event
 */
function handleModelSelectionChange(event) {
    const selectedModel = event.target.value;
    // Запуск проверки требований RAM
    // Initiation of RAM requirement verification
    checkModelRamRequirements(selectedModel);
}

/**
 * Рендеринг списка моделей в HTML-элемент <select>.
 * 
 * ПОЧЕМУ ЭТО ВАЖНО:
 *   Автоматизация обновления пользовательского интерфейса при изменении 
 *   состава доступных файлов моделей в системе.
 */
async function renderModelsSelector() {
    const selector = document.getElementById('model-selector');
    // Прерывание выполнения при отсутствии элемента в DOM
    // Interruption of execution if the element is missing in the DOM
    if (!selector) {
        return;
    }

    const models = await fetchAvailableModels();
    
    // Очистка текущих опций перед добавлением новых
    // Clearing of current options before adding new ones
    selector.innerHTML = '';
    
    if (models.length === 0) {
        const emptyOpt = document.createElement('option');
        emptyOpt.textContent = 'No models found';
        selector.appendChild(emptyOpt);
        return;
    }

    // Grouping of models by directories
    const groups = new Map();

    models.forEach(model => {
        const pathParts = model.name.split(/[\\/]/);
        const fileName = pathParts.pop();
        const folderName = pathParts.join('/') || 'Root';

        if (!groups.has(folderName)) {
            groups.set(folderName, []);
        }
        groups.get(folderName).push({ ...model, fileName });
    });

    // Creation of optgroup elements for each folder
    groups.forEach((folderModels, folder) => {
        const optGroup = document.createElement('optgroup');
        optGroup.label = folder;

        folderModels.forEach(model => {
            const option = document.createElement('option');
            option.value = model.name;
            // Formatting of display text: Name (Size MB)
            option.textContent = `${model.fileName} (${model.size_mb} MB)`;
            optGroup.appendChild(option);
        });

        selector.appendChild(optGroup);
    });

    // Привязка слушателя события изменения
    // Binding of the change event listener
    selector.removeEventListener('change', handleModelSelectionChange);
    selector.addEventListener('change', handleModelSelectionChange);
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

// Добавление слушателя события загрузки DOM для автоматической инициализации
// Addition of the DOM load event listener for automatic initialization
document.addEventListener('DOMContentLoaded', () => {
    // Запуск отрисовки селектора моделей
    // Execution of the model selector rendering
    renderModelsSelector();
});