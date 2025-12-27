# 🔧 Foundry CLI Commands Reference

**Версия:** 0.2.1  
**Проект:** FastApiFoundry (Docker)  
**Дата:** 9 декабря 2025  

---

## 📋 ПРАВИЛЬНЫЕ КОМАНДЫ FOUNDRY

### 🤖 Управление моделями
```bash
# Список доступных моделей
foundry model list

# Информация о модели
foundry model info <model>

# Скачать модель в кэш
foundry model download <model>

# Загрузить модель в сервис
foundry model load <model>

# Выгрузить модель из сервиса
foundry model unload <model>

# Запустить модель (чат)
foundry model run <model>
```

### 🗄️ Управление кэшем
```bash
# Список моделей в кэше
foundry cache list

# Удалить модель из кэша
foundry cache remove <model>

# Путь к кэшу
foundry cache location

# Изменить путь кэша
foundry cache cd <path>
```

### ⚙️ Управление сервисом
```bash
# Список загруженных моделей
foundry service list

# Запустить сервис
foundry service start

# Остановить сервис
foundry service stop

# Перезапустить сервис
foundry service restart

# Статус сервиса
foundry service status
```

---

## 🔄 WORKFLOW УПРАВЛЕНИЯ МОДЕЛЯМИ

### 1. Скачивание модели
```bash
foundry model download deepseek-r1-distill-qwen-7b-generic-cpu:3
```

### 2. Загрузка в сервис
```bash
foundry model load deepseek-r1-distill-qwen-7b-generic-cpu:3
```

### 3. Проверка статуса
```bash
foundry service list
```

### 4. Выгрузка модели
```bash
foundry model unload deepseek-r1-distill-qwen-7b-generic-cpu:3
```

### 5. Удаление из кэша
```bash
foundry cache remove deepseek-r1-distill-qwen-7b-generic-cpu:3
```

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

- **НЕ ИСПОЛЬЗУЙ** `foundry pull` - такой команды НЕТ
- **НЕ ИСПОЛЬЗУЙ** `foundry remove` - такой команды НЕТ  
- **ПРАВИЛЬНО**: `foundry model load/unload`
- **ПРАВИЛЬНО**: `foundry cache remove` для удаления из кэша

---

## 🎯 ИНТЕГРАЦИЯ С WEB-КОНСОЛЬЮ

Веб-консоль на http://localhost:8000 использует PowerShell скрипты:

- **`scripts/load-model.ps1`** - загрузка модели
- **`scripts/unload-model.ps1`** - выгрузка модели
- **`scripts/list-models.ps1`** - список моделей
- **`scripts/service-status.ps1`** - статус сервиса
