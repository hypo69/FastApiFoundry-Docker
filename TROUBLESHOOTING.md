# 🚨 РЕШЕНИЕ ПРОБЛЕМ С ЗАПУСКОМ

**Проект:** FastApiFoundry (Docker)  
**Версия:** 0.2.1  
**Дата:** 9 декабря 2025  

---

## 🔧 БЫСТРОЕ РЕШЕНИЕ

### 1️⃣ Диагностика проблемы
```powershell
python diagnose.py
```

### 2️⃣ Рекомендуемый запуск
```powershell
.\launcher.ps1 -Mode quick
```

### 3️⃣ Ручной запуск по шагам
```powershell
# Терминал 1: запуск Foundry
foundry service start

# Терминал 2: запуск FastAPI
python run.py
```

---

## 🐛 ТИПИЧНЫЕ ПРОБЛЕМЫ

### ❌ Проблема: "Сервер запускается, но нет вывода"

**Причина:** Сервер запущен в фоновом режиме

**Решение:**
```powershell
# Запустить напрямую — вывод будет в терминале
python run.py
```

### ❌ Проблема: "Foundry не найден"

**Решение:**
```powershell
# Установка Foundry через winget
winget install Microsoft.FoundryLocal

# Запуск сервиса
foundry service start
```

### ❌ Проблема: "Порт занят"

**Решение:**
```powershell
# Остановка процессов проекта
python stop.py

# Или принудительно
taskkill /F /IM python.exe
taskkill /F /IM foundry.exe
```

### ❌ Проблема: "Зависимости не найдены"

**Решение:**
```powershell
# Если используете venv (рекомендуется)
venv\Scripts\activate
pip install -r requirements.txt

# Если без venv
pip install -r requirements.txt
```

---

## 📋 ПРАВИЛЬНЫЙ ПОРЯДОК ЗАПУСКА

### 🥇 Способ 1: Лаунчер (РЕКОМЕНДУЕТСЯ)
```powershell
.\launcher.ps1 -Mode quick
```
Автоматически устанавливает зависимости, запускает Foundry и FastAPI.

### 🥈 Способ 2: Скрипт запуска
```powershell
.\start.ps1
```

### 🥉 Способ 3: Пошаговый (для отладки)
```powershell
# Терминал 1
foundry service start

# Терминал 2
python run.py
```

---

## 🔍 ПРОВЕРКА РАБОТЫ

После запуска проверьте:

```powershell
# Health check
curl http://localhost:9696/api/v1/health

# Открыть веб-интерфейс
start http://localhost:9696

# Открыть API документацию
start http://localhost:9696/docs
```

---

## 📞 ЕСЛИ НИЧЕГО НЕ ПОМОГАЕТ

1. **Полная диагностика:**
   ```powershell
   python diagnose.py
   ```

2. **Полная очистка:**
   ```powershell
   python stop.py
   taskkill /F /IM python.exe
   taskkill /F /IM foundry.exe
   ```

3. **Переустановка зависимостей:**
   ```powershell
   .\install.ps1 -Force
   ```

4. **Перезапуск:**
   ```powershell
   .\launcher.ps1 -Mode quick
   ```

---

**ПОМНИТЕ:** Всегда сначала запускайте Foundry, потом FastAPI!
