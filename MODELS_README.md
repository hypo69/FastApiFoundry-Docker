убрать # 📋 Список моделей для FastAPI Foundry

## 🎯 Текущая модель
- **Phi-3 Mini 4K (GPU)** - `Phi-3-mini-4k-instruct-openvino-gpu:1`
- **Статус**: Загружена и готова к работе
- **Размер**: 2.01 GB
- **Описание**: Microsoft Phi-3 Mini - базовая модель для чата

## 📚 Доступные модели

### Microsoft Phi серии
1. **Phi-4** (8.83 GB) - Мощная модель для чата
   - ID: `phi-4-openvino-gpu:1`

2. **Phi-3.5 Mini** (1.95 GB) - Компактная модель
   - ID: `Phi-3.5-mini-instruct-openvino-gpu:1`

3. **Phi-3 Mini 128K** (2.27 GB) - С большим контекстом
   - ID: `Phi-3-mini-128k-instruct-openvino-gpu:1`

4. **Phi-3 Mini 4K** (2.01 GB) - Базовая модель ✅
   - ID: `Phi-3-mini-4k-instruct-openvino-gpu:1`

### Qwen 2.5 серии
5. **Qwen 2.5 Coder 0.5B** (0.36 GB) - Для кода
   - ID: `qwen2.5-coder-0.5b-instruct-openvino-gpu:2`

6. **Qwen 2.5 0.5B** (0.36 GB) - Очень компактная
   - ID: `qwen2.5-0.5b-instruct-openvino-gpu:2`

7. **Qwen 2.5 1.5B** (1.00 GB) - Средняя с инструментами
   - ID: `qwen2.5-1.5b-instruct-openvino-gpu:2`

8. **Qwen 2.5 7B** (4.79 GB) - Популярная модель
   - ID: `qwen2.5-7b-instruct-openvino-gpu:2`

9. **Qwen 2.5 14B** (4.79 GB) - Мощная с инструментами
   - ID: `qwen2.5-14b-instruct-openvino-gpu:2`

### Другие модели
10. **Mistral 7B** (4.27 GB) - Open-source
    - ID: `Mistral-7B-Instruct-v0-2-openvino-gpu:1`

11. **DeepSeek R1 7B** (4.19 GB) - Reasoning модель
    - ID: `DeepSeek-R1-Distill-Qwen-7B-openvino-gpu:1`

12. **DeepSeek R1 14B** (7.87 GB) - Мощная reasoning
    - ID: `DeepSeek-R1-Distill-Qwen-14B-openvino-gpu:1`

## 🚀 Как использовать

### В веб-интерфейсе
1. Откройте http://localhost:8000/static/chat.html
2. Выберите модель из списка
3. Нажмите "Новая сессия"
4. Введите сообщение и отправьте

### Через API
```bash
# Начать сессию
curl -X POST http://localhost:8000/api/v1/chat/start \
  -H "Content-Type: application/json" \
  -d '{"model": "Phi-3-mini-4k-instruct-openvino-gpu:1"}'

# Отправить сообщение
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-id", "message": "Привет!"}'
```

## ⚙️ Управление моделями

```bash
# Посмотреть загруженные модели
foundry service list

# Загрузить другую модель
foundry model run "qwen2.5-0.5b"

# Проверить статус
foundry service status
```

## 📝 Примечания

- Все модели оптимизированы для GPU через OpenVINO
- Модели с суффиксом `-gpu` работают на видеокарте
- Для CPU версий используйте `-cpu` в конце ID модели
- Текущая модель (Phi-3 Mini 4K) уже загружена и готова к работе