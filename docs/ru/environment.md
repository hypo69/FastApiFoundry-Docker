# 🔐 Environment Variables Configuration

**Версия:** 0.2.1  
**Проект:** FastApiFoundry (Docker)  
**Дата:** 9 декабря 2025  

---

## 📋 Настройка переменных окружения

### 🔧 Быстрая настройка

1. **Скопируйте пример файла:**
   ```bash
   cp .env.example .env
   ```

2. **Отредактируйте `.env` файл** с вашими данными

3. **Перезапустите приложение:**
   ```bash
   python run.py
   ```

---

## 🔑 GitHub Configuration

### Основные параметры:
```env
GITHUB_USER=your_username
GITHUB_PASSWORD=your_password_or_token  
GITHUB_PAT=ghp_your_personal_access_token_here
```

### 🎯 Как получить GitHub PAT:

1. Перейдите в **GitHub Settings** → **Developer settings** → **Personal access tokens**
2. Нажмите **Generate new token (classic)**
3. Выберите необходимые права:
   - `repo` - для доступа к репозиториям
   - `read:user` - для чтения профиля
   - `gist` - для работы с gist
4. Скопируйте токен в `GITHUB_PAT`

---

## ⚙️ FastAPI Configuration

```env
API_KEY=your_secret_api_key_here
SECRET_KEY=your_jwt_secret_key_here
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 🔐 Генерация секретных ключей:

```python
import secrets

# Для API_KEY
api_key = secrets.token_urlsafe(32)
print(f"API_KEY={api_key}")

# Для SECRET_KEY (JWT)
secret_key = secrets.token_urlsafe(64)
print(f"SECRET_KEY={secret_key}")
```

---

## 🤖 Foundry AI Configuration

```env
FOUNDRY_BASE_URL=http://localhost:50477/v1
FOUNDRY_API_KEY=optional_foundry_api_key
FOUNDRY_TIMEOUT=30
```

---

## 📊 Database Configuration

### SQLite (по умолчанию):
```env
DATABASE_URL=sqlite:///./fastapi_foundry.db
```

### PostgreSQL:
```env
DATABASE_URL=postgresql://user:password@localhost/dbname
```

---

## 🔍 RAG System Configuration

```env
RAG_INDEX_PATH=rag_index
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
```

---

## 📧 Email Configuration

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_TLS=true
```

### 🎯 Gmail App Password:

1. Включите **2-Step Verification** в Google Account
2. Перейдите в **App passwords**
3. Создайте пароль для приложения
4. Используйте этот пароль в `SMTP_PASSWORD`

---

## 🔄 Redis Configuration

```env
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your_redis_password
```

---

## 🌍 External APIs

### OpenAI:
```env
OPENAI_API_KEY=sk-your_openai_key_here
```

### Anthropic (Claude):
```env
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
```

### HuggingFace:
```env
HUGGINGFACE_API_KEY=hf_your_huggingface_key_here
```

---

## 🚀 Environment Modes

### Development:
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

### Production:
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

---

## 🔒 Безопасность

### ✅ Что МОЖНО делать:
- Хранить API ключи и токены
- Хранить пароли и секретные ключи
- Хранить URL подключений к БД
- Хранить настройки SMTP

### ❌ Что НЕЛЬЗЯ делать:
- Коммитить `.env` в Git (уже в .gitignore)
- Передавать `.env` файл другим людям
- Хранить `.env` в публичных местах
- Использовать слабые пароли

---

## 🛠️ Использование в коде

### Python:
```python
import os
from dotenv import load_dotenv

# Загрузка переменных
load_dotenv()

# Использование
github_token = os.getenv('GITHUB_PAT')
api_key = os.getenv('API_KEY')
```

### PowerShell (start.ps1):
```powershell
# Загрузка .env файла
if (Test-Path "$Root\.env") {
    Get-Content "$Root\.env" | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
        }
    }
}

# Использование
$githubToken = $env:GITHUB_PAT
```

---

## 🔧 Troubleshooting

### Проблема: Переменные не загружаются
```bash
# Проверьте формат файла
cat .env | grep -v '^#' | grep '='

# Проверьте права доступа
ls -la .env
```

### Проблема: Кодировка файла
- Убедитесь что `.env` в UTF-8
- Нет BOM (Byte Order Mark)
- Unix line endings (LF, не CRLF)

---

**ВАЖНО:** Никогда не коммитьте реальный `.env` файл в Git!
