# MCPServerLauncher PowerShell Module

## Описание

**MCPServerLauncher** — это PowerShell модуль для автоматического запуска и управления MCP (Model Context Protocol) серверами. Модуль поддерживает работу с несколькими типами серверов:

- **STDIO сервер** — для выполнения PowerShell скриптов через стандартные потоки ввода-вывода
- **HTTPS сервер** — для предоставления REST API
- **WordPress CLI сервер** — для управления WordPress через командную строку

## Требования

- PowerShell 7.0 или выше
- Windows, Linux или macOS
- Права на запуск фоновых процессов

## Установка

### Вариант 1: Ручная установка

1. Скопируйте файлы модуля в одну из директорий PowerShell модулей:

```powershell
# Узнать доступные пути для модулей
$env:PSModulePath -split [IO.Path]::PathSeparator

# Рекомендуемая директория для пользовательских модулей
$modulePath = "$HOME\Documents\PowerShell\Modules\MCPServerLauncher"
```

2. Создайте директорию и скопируйте файлы:

```powershell
New-Item -Path $modulePath -ItemType Directory -Force
Copy-Item *.psd1, *.psm1 -Destination $modulePath
```

3. Импортируйте модуль:

```powershell
Import-Module MCPServerLauncher
```

### Вариант 2: Установка из локального репозитория

```powershell
# Из директории проекта
Install-Module -Name .\MCPServerLauncher -Scope CurrentUser
```

## Быстрый старт

### Импорт модуля

```powershell
Import-Module MCPServerLauncher
```

### Запуск всех серверов

```powershell
# Запуск с ожиданием (блокирующий режим)
Start-MCPServerLauncher

# Запуск без ожидания (фоновый режим)
Start-MCPServerLauncher -NoWait

# Краткая форма
Start-MCP
```

### Проверка статуса серверов

```powershell
# Полная форма
Get-MCPServerStatus

# Краткая форма
Get-MCPStatus
```

### Остановка всех серверов

```powershell
# Полная форма
Stop-MCPServers

# Краткая форма
Stop-MCP
```

### Перезапуск серверов

```powershell
# Полная форма
Restart-MCPServers

# Краткая форма
Restart-MCP
```

## Доступные команды

### Start-MCPServerLauncher

Запускает все доступные MCP серверы.

**Параметры:**

- `-ConfigPath` — путь к директории с конфигурациями (по умолчанию: `src\config`)
- `-NoWait` — не ожидать после запуска серверов

**Примеры:**

```powershell
# Запуск с параметрами по умолчанию
Start-MCPServerLauncher

# Запуск с пользовательским путем к конфигурациям
Start-MCPServerLauncher -ConfigPath 'C:\MyProject\config'

# Запуск в фоновом режиме
Start-MCPServerLauncher -NoWait
```

### Stop-MCPServers

Останавливает все запущенные MCP серверы.

**Примеры:**

```powershell
Stop-MCPServers
```

### Get-MCPServerStatus

Отображает статус всех зарегистрированных MCP серверов.

**Примеры:**

```powershell
Get-MCPServerStatus
```

**Пример вывода:**

```
=== СТАТУС MCP СЕРВЕРОВ ===

  ✓ powershell-stdio (PID: 12345)
  ✓ powershell-https (PID: 12346)
  ✗ wordpress-cli (остановлен)

Запущено серверов: 2 / 3
```

### Restart-MCPServers

Перезапускает все MCP серверы (останавливает и запускает заново).

**Параметры:**

- `-ConfigPath` — путь к директории с конфигурациями

**Примеры:**

```powershell
Restart-MCPServers
```

### Test-MCPServerRunning

Проверяет, запущен ли указанный сервер.

**Параметры:**

- `-ServerName` — имя сервера для проверки

**Возвращает:** `$true` если сервер запущен, иначе `$false`

**Примеры:**

```powershell
if (Test-MCPServerRunning -ServerName 'powershell-stdio') {
    Write-Host 'STDIO сервер запущен'
}
```

### Get-MCPServerLog

Отображает логи MCP launcher.

**Параметры:**

- `-Tail` — количество последних строк для отображения (по умолчанию: 50)
- `-Follow` — следить за обновлениями лог-файла в реальном времени

**Примеры:**

```powershell
# Показать последние 50 строк
Get-MCPServerLog

# Показать последние 100 строк
Get-MCPServerLog -Tail 100

# Следить за логами в реальном времени
Get-MCPServerLog -Follow

# Комбинация параметров
Get-MCPServerLog -Tail 20 -Follow
```

## Псевдонимы

Для удобства использования доступны короткие псевдонимы:

| Полная команда | Псевдоним |
|----------------|-----------|
| `Start-MCPServerLauncher` | `Start-MCP` |
| `Stop-MCPServers` | `Stop-MCP` |
| `Get-MCPServerStatus` | `Get-MCPStatus` |
| `Restart-MCPServers` | `Restart-MCP` |

## Структура проекта

Модуль ищет серверные скрипты в следующих локациях (в порядке приоритета):

1. `<ProjectRoot>\src\servers\<ServerScript>`
2. `<ProjectRoot>\servers\<ServerScript>`
3. `<ProjectRoot>\<ServerScript>`

Где `<ProjectRoot>` — это директория, в которой находится модуль.

## Логирование

Модуль создает лог-файл в временной директории пользователя:

```powershell
# Путь к лог-файлу
$env:TEMP\mcp-launcher.log
```

Для просмотра логов используйте команду:

```powershell
Get-MCPServerLog -Follow
```

## Серверы

Модуль поддерживает следующие серверы:

### 1. PowerShell STDIO сервер

**Скрипт:** `Start-McpStdioServer.ps1`

**Описание:** Сервер для выполнения PowerShell скриптов через стандартные потоки ввода-вывода

**Лог-файл:** `$env:TEMP\mcp-server.log`

### 2. PowerShell HTTPS сервер

**Скрипт:** `Start-McpHTTPSServer.ps1`

**Описание:** HTTPS сервер для предоставления REST API

### 3. WordPress CLI сервер

**Скрипт:** `Start-McpWPCLIServer.ps1`

**Описание:** Сервер для управления WordPress через командную строку

## Примеры использования

### Пример 1: Базовый запуск

```powershell
# Импорт модуля
Import-Module MCPServerLauncher

# Запуск всех серверов
Start-MCP

# Проверка статуса
Get-MCPStatus

# Остановка всех серверов
Stop-MCP
```

### Пример 2: Автоматический запуск при старте системы

Добавьте в ваш PowerShell профиль (`$PROFILE`):

```powershell
# Автоматический импорт и запуск MCP серверов
Import-Module MCPServerLauncher
Start-MCPServerLauncher -NoWait
```

### Пример 3: Мониторинг серверов

```powershell
# Запуск серверов в фоне
Start-MCP -NoWait

# Мониторинг статуса каждые 10 секунд
while ($true) {
    Clear-Host
    Get-MCPStatus
    Start-Sleep -Seconds 10
}
```

### Пример 4: Проверка и перезапуск остановленного сервера

```powershell
if (-not (Test-MCPServerRunning -ServerName 'powershell-stdio')) {
    Write-Host 'STDIO сервер остановлен, перезапуск...'
    Restart-MCP
}
```

## Устранение неполадок

### Серверы не запускаются

1. Проверьте, что скрипты серверов находятся в правильных директориях
2. Проверьте права на выполнение скриптов:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

3. Проверьте логи:

```powershell
Get-MCPServerLog -Tail 100
```

### Серверы запускаются, но сразу останавливаются

1. Проверьте логи серверов
2. Убедитесь, что все зависимости установлены
3. Проверьте конфигурационные файлы серверов

### Модуль не импортируется

1. Проверьте, что модуль находится в одной из директорий `$env:PSModulePath`
2. Проверьте версию PowerShell:

```powershell
$PSVersionTable.PSVersion
```

Требуется PowerShell 7.0 или выше.

## Конфигурация

### Переменные окружения

Модуль поддерживает следующие переменные окружения для серверов:

- `POWERSHELL_EXECUTION_POLICY` — политика выполнения для серверных процессов (по умолчанию: `RemoteSigned`)

### Рабочая директория

Все серверы запускаются с рабочей директорией, установленной в корень проекта, что обеспечивает правильную работу относительных путей.

## Лицензия

MIT License

Copyright (c) 2025 hypo69

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Автор

**hypo69**

- GitHub: [https://github.com/hypo69/hypo](https://github.com/hypo69/hypo)

## Поддержка

Для сообщений об ошибках и предложений используйте GitHub Issues.

## История изменений

### Version 1.0.1

- Автоматический запуск MCP серверов
- Управление жизненным циклом серверов
- Поддержка STDIO, HTTPS и WordPress CLI серверов
- Подробное логирование
- Мониторинг статуса серверов
- Псевдонимы команд для удобства
- Полная документация и примеры


# 📦 MCP Servers - Финальный пакет файлов

## 🎯 Обзор

Полный пакет исправленных, дополненных и готовых к интеграции файлов для проекта MCP Servers Collection.

**Дата создания:** 2025-01-24  
**Версия:** 1.0.0  
**Статус:** ✅ Готово к использованию

---

## 📥 Скачивание файлов

### 🆕 Новые/Исправленные файлы (8)

#### 1. **python_client.py** (17 KB)
[Скачать](computer:///mnt/user-data/outputs/python_client.py)

**Описание:** Полноценный Python клиент для MCP серверов
- Поддержка HTTPS и STDIO протоколов
- Контекстный менеджер
- Полная типизация
- 9 публичных методов

---

#### 2. **McpWpCliServer.ps1** (20 KB)
[Скачать](computer:///mnt/user-data/outputs/McpWpCliServer.ps1)

**Описание:** WordPress CLI MCP сервер (исправлен из пустого файла)
- STDIO протокол
- Автоматический JSON вывод
- 2 инструмента: `run-wp-cli`, `check-wp-cli`
- Проверка доступности WP-CLI

---

#### 3. **env_loader.py** (8.5 KB)
[Скачать](computer:///mnt/user-data/outputs/env_loader.py)

**Описание:** Утилита для загрузки переменных окружения
- Класс `EnvLoader` для работы с .env
- Класс `EnvConfig` с типизированной конфигурацией
- Автоматический поиск .env файла
- Валидация обязательных переменных
- Глобальные функции `load_env()`, `get_env()`, `get_config()`

**Использование:**
```python
from env_loader import load_env, get_env, get_config

# Загрузка .env
load_env()

# Получение переменной
api_key = get_env('GEMINI_API_KEY')

# Получение полной конфигурации
config = get_config()
print(config.wordpress_url)
```

---

#### 4. **.env.example** (3.2 KB)
[Скачать](computer:///mnt/user-data/outputs/.env.example)

**Описание:** Пример файла с переменными окружения (БЕЗ реальных секретов)
- Все необходимые переменные
- Комментарии на русском
- Ссылки где получить API ключи
- Безопасные placeholder значения

**Использование:**
```bash
# Копировать как .env
cp .env.example .env

# Отредактировать своими значениями
nano .env
```

---

#### 5. **.gitignore** (1.8 KB)
[Скачать](computer:///mnt/user-data/outputs/.gitignore)

**Описание:** Защита секретов от попадания в Git
- Блокирует .env файлы
- Блокирует все файлы с секретами
- Блокирует логи, кэши, временные файлы
- Исключения для .env.example

**Важно:** Добавить в корень проекта!

---

#### 6. **requirements_mcp.txt** (1.2 KB)
[Скачать](computer:///mnt/user-data/outputs/requirements_mcp.txt)

**Описание:** Python зависимости с python-dotenv
- ✅ **python-dotenv>=1.0.0** - для работы с .env
- psutil, requests, urllib3
- mcp, huggingface-hub
- pytest, black, pylint, mypy

**Установка:**
```bash
pip install -r requirements_mcp.txt
```

---

#### 7. **README_MCP.md** (16 KB)
[Скачать](computer:///mnt/user-data/outputs/README_MCP.md)

**Описание:** Главный README для всей коллекции
- Описание всех 6 серверов
- Описание всех 4 клиентов
- Инструкции по установке
- Примеры использования
- Безопасность

---

#### 8. **INTEGRATION_GUIDE.md** (14 KB)
[Скачать](computer:///mnt/user-data/outputs/INTEGRATION_GUIDE.md)

**Описание:** Руководство по интеграции в hypotez
- Целевая структура проекта
- 6 шагов интеграции
- Код для создания __init__.py
- Код для создания header.py
- Claude Desktop конфигурация

---

### 📋 Индексные и справочные файлы (2)

#### 9. **FILE_INDEX.md** (17 KB)
[Скачать](computer:///mnt/user-data/outputs/FILE_INDEX.md)

**Описание:** Полный индекс всех файлов проекта
- Детальное описание каждого файла
- Статистика по категориям
- Контрольный список готовности

---

#### 10. **FINAL_PACKAGE.md** (этот файл)
[Скачать](computer:///mnt/user-data/outputs/FINAL_PACKAGE.md)

**Описание:** Манифест финального пакета со всеми ссылками

---

### 📚 Документация OS Tools (7 файлов)

#### 11. **mcp_server.py** (32 KB)
[Скачать](computer:///mnt/user-data/outputs/mcp_server.py)

**Описание:** MCP сервер для работы с ОС
- Интеграция с env_loader
- Валидация команд и путей
- 11 инструментов

---

#### 12. **mcp_os_tools.py** (30 KB)
[Скачать](computer:///mnt/user-data/outputs/mcp_os_tools.py)

**Описание:** Инструменты для работы с ОС

---

#### 13. **mcp_client_example.py** (16 KB)
[Скачать](computer:///mnt/user-data/outputs/mcp_client_example.py)

**Описание:** Примеры использования клиента

---

#### 14. **install.py** (12 KB)
[Скачать](computer:///mnt/user-data/outputs/install.py)

**Описание:** Автоустановщик

---

#### 15. **mcp_server_config.json** (5.9 KB)
[Скачать](computer:///mnt/user-data/outputs/mcp_server_config.json)

**Описание:** Конфигурация OS Tools сервера

---

#### 16-21. **Документация** (README.md, QUICKSTART.md, CONFIG_GUIDE.md, и др.)
- [README.md](computer:///mnt/user-data/outputs/README.md) (11 KB)
- [QUICKSTART.md](computer:///mnt/user-data/outputs/QUICKSTART.md) (7.1 KB)
- [CONFIG_GUIDE.md](computer:///mnt/user-data/outputs/CONFIG_GUIDE.md) (15 KB)
- [JSON_RPC_EXAMPLES.md](computer:///mnt/user-data/outputs/JSON_RPC_EXAMPLES.md) (11 KB)
- [SUMMARY.md](computer:///mnt/user-data/outputs/SUMMARY.md) (11 KB)
- [UPDATE_NOTES.md](computer:///mnt/user-data/outputs/UPDATE_NOTES.md) (15 KB)

---

## 📊 Статистика пакета

| Категория | Файлов | Размер | Статус |
|-----------|--------|--------|--------|
| **Python код** | 5 | ~95 KB | ✅ |
| **PowerShell код** | 1 | 20 KB | ✅ |
| **Конфигурация** | 4 | ~11 KB | ✅ |
| **Документация** | 11 | ~120 KB | ✅ |
| **Всего** | **21** | **~246 KB** | ✅ |

---

## 🔑 Ключевые улучшения

### ✅ Безопасность
1. **Файл .env** - все секреты теперь в переменных окружения
2. **Файл .env.example** - безопасный шаблон без секретов
3. **Файл .gitignore** - защита от случайного коммита секретов
4. **env_loader.py** - безопасная загрузка переменных

### ✅ Исправленные файлы
1. **python_client.py** - создан с нуля (был пустой)
2. **McpWpCliServer.ps1** - создан правильно (был пустой с .пс1)
3. **requirements_mcp.txt** - добавлен python-dotenv

### ✅ Новый функционал
1. **Загрузка из .env** - класс EnvLoader
2. **Типизированная конфигурация** - dataclass EnvConfig
3. **Автоматический поиск .env** - в нескольких стандартных местах
4. **Валидация переменных** - проверка обязательных ключей

---

## 🚀 Быстрый старт

### Шаг 1: Скачайте файлы
Скачайте все файлы по ссылкам выше.

### Шаг 2: Создайте .env файл
```bash
# Скопируйте пример
cp .env.example .env

# Отредактируйте своими значениями
nano .env
```

### Шаг 3: Установите зависимости
```bash
pip install -r requirements_mcp.txt
```

### Шаг 4: Используйте переменные окружения
```python
from env_loader import load_env, get_env, get_config

# Автоматическая загрузка при импорте
# load_env() уже вызвана

# Получение переменной
api_key = get_env('GEMINI_API_KEY')

# Получение конфигурации
config = get_config()
print(f"WordPress URL: {config.wordpress_url}")
print(f"Server timeout: {config.mcp_server_timeout}")
```

---

## 📁 Структура для интеграции

```
hypotez/src/mcp/
├── .env                          # ❌ НЕ коммитить! (создать из .env.example)
├── .env.example                  # ✅ Скачать
├── .gitignore                    # ✅ Скачать
├── requirements_mcp.txt          # ✅ Скачать
│
├── utils/
│   └── env_loader.py             # ✅ Скачать (новый)
│
├── clients/
│   └── python_client.py          # ✅ Скачать (исправлен)
│
├── servers/
│   ├── McpWpCliServer.ps1        # ✅ Скачать (исправлен)
│   └── mcp_server.py             # ✅ Скачать
│
├── tools/
│   └── mcp_os_tools.py           # ✅ Скачать
│
├── config/
│   └── mcp_server_config.json    # ✅ Скачать
│
├── examples/
│   └── mcp_client_example.py     # ✅ Скачать
│
├── docs/
│   ├── README.md                 # ✅ Скачать
│   ├── QUICKSTART.md             # ✅ Скачать
│   ├── CONFIG_GUIDE.md           # ✅ Скачать
│   ├── JSON_RPC_EXAMPLES.md      # ✅ Скачать
│   ├── SUMMARY.md                # ✅ Скачать
│   └── UPDATE_NOTES.md           # ✅ Скачать
│
├── README_MCP.md                 # ✅ Скачать
├── INTEGRATION_GUIDE.md          # ✅ Скачать
├── FILE_INDEX.md                 # ✅ Скачать
└── install.py                    # ✅ Скачать
```

---

## 🔒 Безопасность секретов

### ⚠️ КРИТИЧЕСКИ ВАЖНО!

1. **НИКОГДА** не коммитьте файл `.env` в Git
2. **ВСЕГДА** используйте `.env.example` как шаблон
3. **ПРОВЕРЬТЕ** что `.gitignore` на месте
4. **ИСПОЛЬЗУЙТЕ** разные `.env` для dev/staging/prod

### ✅ Правильная работа с секретами:

```bash
# 1. Создать .env из примера
cp .env.example .env

# 2. Отредактировать ТОЛЬКО .env (не .env.example!)
nano .env

# 3. Добавить реальные секреты в .env
GEMINI_API_KEY=AIzaSy...  # ваш реальный ключ
WORDPRESS_PASSWORD=...     # ваш реальный пароль

# 4. Проверить что .env в .gitignore
cat .gitignore | grep ".env"

# 5. Убедиться что .env не отслеживается Git
git status  # .env не должен быть в списке

# 6. Коммитить ТОЛЬКО .env.example
git add .env.example .gitignore
git commit -m "Add .env.example and .gitignore"
```

---

## 🔧 Использование env_loader

### Пример 1: Простое использование
```python
from env_loader import get_env

# Получение переменной
api_key = get_env('GEMINI_API_KEY')

# С значением по умолчанию
port = get_env('MCP_HTTPS_PORT', '8443')
```

### Пример 2: Использование конфигурации
```python
from env_loader import get_config

config = get_config()

print(f"WordPress URL: {config.wordpress_url}")
print(f"WordPress Username: {config.wordpress_username}")
print(f"Server Timeout: {config.mcp_server_timeout}")
print(f"Block Dangerous Commands: {config.block_dangerous_commands}")
```

### Пример 3: Явная загрузка
```python
from env_loader import load_env, get_env

# Загрузка из конкретного файла
load_env('/path/to/custom/.env')

# Теперь переменные доступны
api_key = get_env('GEMINI_API_KEY')
```

### Пример 4: В MCP сервере
```python
import header
from header import __root__
from src import gs
from src.logger.logger import logger

# Загрузка переменных окружения
from env_loader import get_config

class MCPServer:
    def __init__(self):
        # Загрузка конфигурации из .env
        self.env_config = get_config()
        
        # Использование переменных
        self.timeout = self.env_config.mcp_server_timeout
        self.port = self.env_config.mcp_https_port
        
        logger.info(f'Server timeout: {self.timeout}s')
        logger.info(f'Server port: {self.port}')
```

---

## 📝 Пример .env файла (с безопасными значениями)

```bash
# AI API Keys
GEMINI_API_KEY=your_key_here
HUGGINGFACE_TOKEN=hf_your_token_here

# GitHub
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here

# WordPress
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=your_username
WORDPRESS_PASSWORD=your_password
WORDPRESS_API_KEY=xxxx xxxx xxxx xxxx xxxx xxxx
WORDPRESS_PATH=/var/www/html/wordpress

# MCP Server
MCP_SERVER_TIMEOUT=300
MCP_HTTPS_PORT=8443
MCP_HTTPS_HOST=localhost
MCP_AUTH_TOKEN=your_secure_token

# Logging
PYDOLL_LOG_LEVEL=INFO
PYDOLL_DEBUG=false

# Security
BLOCK_DANGEROUS_COMMANDS=true
MAX_OUTPUT_SIZE=100000
```

---

## ✅ Контрольный список

### Перед началом работы:
- [ ] Скачаны все 21 файл
- [ ] Создан .env из .env.example
- [ ] В .env добавлены реальные секреты
- [ ] Установлены зависимости: `pip install -r requirements_mcp.txt`
- [ ] Проверен .gitignore (`.env` должен быть в списке)
- [ ] .env НЕ добавлен в Git

### Для интеграции в hypotez:
- [ ] Создана структура директорий
- [ ] Скопированы все файлы
- [ ] Созданы __init__.py файлы (код в INTEGRATION_GUIDE.md)
- [ ] Создан header.py (код в INTEGRATION_GUIDE.md)
- [ ] Запущен тест: `python clients/python_client.py`

---

# MCP PowerShell Server

Сервер MCP (Model Context Protocol) для выполнения PowerShell скриптов, поддерживающий как HTTP, так и STDIO режимы работы.

## Описание

MCP PowerShell Server позволяет ИИ-ассистентам выполнять PowerShell команды и скрипты через стандартизированный протокол MCP. Сервер поддерживает два режима работы:

-   **STDIO режим**: Для интеграции с `gemini-cli` и другими локальными MCP-клиентами.
-   **HTTP режим**: Для веб-приложений и интеграции по сети через REST API.

## Какой режим выбрать: HTTP или STDIO?

Выбор между `mcp-powershell-http.ps1` и `mcp-powershell-stdio.ps1` зависит от того, **как и откуда** клиентское приложение будет взаимодействовать с сервером.

*   **`mcp-powershell-http.ps1` (HTTP режим)** работает как **официант в ресторане**. Он принимает заказы (HTTP-запросы) от любого клиента в сети, передает их на "кухню" (PowerShell) и возвращает готовый результат (HTTP-ответ).
*   **`mcp-powershell-stdio.ps1` (STDIO режим)** работает как **личный помощник на кухне**. Он получает задания напрямую (через стандартный ввод `stdin`) от управляющего процесса (например, `gemini-cli`), который сам его запустил, и немедленно отдает результат обратно (через стандартный вывод `stdout`).

### Когда использовать HTTP режим

Вам следует выбрать HTTP, если требуется **сетевое взаимодействие**.

-   **Удаленное управление:** Клиентское приложение находится на другом компьютере.
-   **Веб-интеграция:** Необходимо вызывать PowerShell-скрипты из веб-приложения, панели администратора или через AJAX-запросы.
-   **Микросервисная архитектура:** Другие сервисы в вашей сети должны взаимодействовать с PowerShell.
-   **Простое тестирование:** Вы хотите использовать инструменты вроде `curl`, Postman или `Invoke-RestMethod` для отправки команд.

> **Простыми словами:** выбирайте HTTP, если между клиентом и сервером есть **сеть**.

### Когда использовать STDIO режим

Этот режим идеально подходит для **локальной и безопасной интеграции**.

-   **Основной сценарий — Gemini CLI:** Инструмент `gemini-cli` сам запускает `mcp-powershell-stdio.ps1` как дочерний процесс и общается с ним напрямую через стандартные потоки ввода-вывода.
-   **Интеграция с другими локальными приложениями:** Ваша программа на Python, Node.js или другом языке может запустить сервер и управлять им, не открывая сетевые порты.
-   **Повышенная безопасность:** Поскольку сетевые порты не открываются, этот способ по умолчанию более безопасен.

> **Простыми словами:** выбирайте STDIO, если клиент и сервер находятся **на одной машине**, и клиент сам запускает сервер.

### Сравнительная таблица

| Характеристика | HTTP режим (`mcp-powershell-http.ps1`) | STDIO режим (`mcp-powershell-stdio.ps1`) |
| :--- | :--- | :--- |
| **Основной сценарий** | Сетевое взаимодействие, веб-API | Локальная интеграция с CLI-инструментами |
| **Тип связи** | Клиент-сервер по сети (TCP/IP) | Межпроцессное взаимодействие (IPC) |
| **Расположение** | Клиент и сервер могут быть на разных машинах | Клиент и сервер **должны быть** на одной машине |
| **Безопасность** | Требует внимания (доступ к порту, файрвол) | Более безопасен по умолчанию (нет открытых портов) |
| **Типичные клиенты** | `curl`, Postman, веб-приложения, удаленные скрипты | `gemini-cli`, локальные приложения-обертки |

## Особенности

-   ✅ Поддержка MCP протокола версии 2024-11-05
-   ✅ Два режима работы: STDIO и HTTP
-   ✅ Изоляция выполнения скриптов в отдельных PowerShell процессах
-   ✅ Настраиваемые тайм-ауты выполнения
-   ✅ Детальное логирование всех операций
-   ✅ Обработка ошибок и предупреждений PowerShell
-   ✅ Поддержка параметров скриптов
-   ✅ Настраиваемая рабочая директория
-   ✅ Автоматические launcher'ы для упрощения запуска

## Системные требования

-   PowerShell 7.0 или новее
-   Windows 10/11 или Windows Server 2019+
-   .NET 6.0 или новее

## Структура проекта

```
mcp-powershell-server/
├── src/
│   ├── clients/           # Клиентские приложения
│   │   ├── node/         # Node.js клиент
│   │   ├── powershell/   # PowerShell клиент
│   │   └── python/       # Python клиент
│   └── servers/          # Серверные компоненты
│       ├── mcp-powershell-stdio.ps1   # STDIO версия сервера
│       ├── mcp-powershell-http.ps1    # HTTP версия сервера
│       ├── test-mcp.ps1               # Тестовый сервер
│       └── config.json                # Файл конфигурации
├── docs/                 # Документация
├── README.md            # Этот файл
└── how-to-use.md        # Подробное руководство
```

## Быстрый старт

### STDIO режим (для gemini-cli)

1.  **Запуск сервера:**
    ```powershell
    .\src\servers\mcp-powershell-stdio.ps1
    ```

2.  **Тестирование:**
    ```powershell
    .\src\servers\test-mcp.ps1
    ```

### HTTP режим

1.  **Базовый запуск:**
    ```powershell
    .\src\servers\mcp-powershell-http.ps1
    ```

2.  **С настраиваемыми параметрами:**
    ```powershell
    .\src\servers\mcp-powershell-http.ps1 -Port 9090 -ServerHost "0.0.0.0"
    ```

3.  **С файлом конфигурации:**
    ```powershell
    .\src\servers\mcp-powershell-http.ps1 -ConfigFile ".\src\servers\config.json"
    ```

## Доступные MCP инструменты

### `run-script`

Выполняет PowerShell скрипт с заданными параметрами.

**Параметры:**

-   `script` (обязательный) - PowerShell код для выполнения
-   `parameters` (опциональный) - Хеш-таблица параметров
-   `workingDirectory` (опциональный) - Рабочая директория
-   `timeoutSeconds` (опциональный) - Тайм-аут выполнения (1-3600 сек)

**Пример использования через MCP:**

```json
{
  "name": "run-script",
  "arguments": {
    "script": "Get-Process | Select-Object -First 5 | Format-Table",
    "workingDirectory": "C:\\",
    "timeoutSeconds": 30
  }
}
```

## Конфигурация

Сервер поддерживает конфигурацию через файл `config.json`:

```json
{
  "Port": 8090,
  "Host": "localhost",
  "MaxConcurrentRequests": 10,
  "TimeoutSeconds": 300,
  "AllowedPaths": [
    "C:\\Scripts\\",
    "C:\\Tools\\"
  ],
  "Security": {
    "EnableScriptValidation": true,
    "BlockDangerousCommands": true,
    "RestrictedCommands": [
      "Remove-Item",
      "Format-Volume",
      "Stop-Computer",
      "Restart-Computer"
    ]
  }
}
```

## Безопасность

-   Выполнение скриптов происходит в изолированных PowerShell процессах
-   Поддержка списка запрещенных команд
-   Ограничение по времени выполнения
-   Логирование всех выполняемых команд
-   Возможность ограничения доступных путей

## Логирование

-   **STDIO режим**: Логи записываются в `%TEMP%\mcp-powershell-server.log`
-   **HTTP режим**: Логи выводятся в консоль с цветовой индикацией

Уровни логирования: DEBUG, INFO, WARNING, ERROR

## Интеграция с ИИ-ассистентами

### Gemini CLI

```bash
gemini --mcp-config "path/to/mcp_servers.json" -m gemini-2.5-pro -p "Покажи первые 5 процессов в системе"
```

### Другие MCP-клиенты

Сервер совместим со всеми клиентами, поддерживающими MCP протокол 2024-11-05.

## Устранение неполадок

### Общие проблемы

1.  **Порт занят**: Измените порт в конфигурации или остановите процесс, использующий порт
2.  **Права доступа**: Запуск на привилегированных портах (<1024) требует прав администратора
3.  **Кодировка**: Убедитесь, что PowerShell настроен на UTF-8
4.  **Версия PowerShell**: Требуется PowerShell 7+

### Диагностика

Проверьте логи сервера для диагностики проблем:

```powershell
Get-Content "$env:TEMP\mcp-powershell-server.log" -Tail 20
```

## Разработка и расширение

Сервер легко расширяется новыми MCP инструментами. См. `how-to-use.md` для подробных инструкций по разработке.

## Лицензия

Этот проект распространяется под лицензией MIT. См. файл LICENSE для подробностей.

## Поддержка

-   Создайте Issue в GitHub репозитории
-   Проверьте документацию в `how-to-use.md`
-   Ознакомьтесь с примерами использования

## Версии

-   **1.0.0** - Начальная версия с поддержкой STDIO и HTTP режимов

## 🎉 Готово!

Все файлы готовы к использованию. Следуйте инструкциям выше для интеграции.

**Важно:** Всегда помните о безопасности секретов!

---

## 📞 Дополнительная документация

- [README_MCP.md](computer:///mnt/user-data/outputs/README_MCP.md) - Полное описание всех серверов
- [INTEGRATION_GUIDE.md](computer:///mnt/user-data/outputs/INTEGRATION_GUIDE.md) - Пошаговая интеграция
- [FILE_INDEX.md](computer:///mnt/user-data/outputs/FILE_INDEX.md) - Индекс всех файлов
- [CONFIG_GUIDE.md](computer:///mnt/user-data/outputs/CONFIG_GUIDE.md) - Руководство по конфигурации

---

**🎊 Пакет готов к использованию!**

**Дата:** 2025-01-24  
**Версия:** 1.0.0  
**Файлов:** 21  
**Размер:** ~246 KB