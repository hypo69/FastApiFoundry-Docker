# MCPServerLauncher — PowerShell MCP Серверы

PowerShell модуль для запуска и управления MCP (Model Context Protocol) серверами.
Поддерживает STDIO и HTTPS режимы работы.

## Требования

- PowerShell 7.0+
- Windows 10/11 или Windows Server 2019+

## Структура

```
mcp-powershell-servers/
├── src/
│   ├── clients/
│   │   ├── nodejs.js              # Node.js клиент
│   │   ├── powershell.ps1         # PowerShell клиент
│   │   ├── python_client.py       # Python клиент
│   │   └── wpcli.ps1              # WP-CLI клиент
│   ├── config/
│   │   ├── Config-McpHTTPS.json
│   │   ├── Config-McpWPCLI.json
│   │   └── mcp-powershell-stdio.config.json
│   └── servers/
│       ├── McpSTDIOServer.ps1     # MCP через STDIO (JSON-RPC 2.0)
│       ├── McpHttpsServer.ps1     # MCP через HTTPS
│       ├── McpWPCLIServer.ps1     # MCP для WordPress CLI
│       ├── McpWpServer.ps1        # MCP для WordPress
│       ├── McpHuggingFaceServer.ps1
│       ├── huggingface_mcp.py     # Python MCP для HuggingFace (облако)
│       └── local_models_mcp.py    # Python MCP для локальных моделей (FastAPI Foundry)
├── MCPServerLauncher.psd1         # Манифест модуля
├── Start-MCPServers.ps1           # Главный скрипт запуска
└── settings.json                  # Настройки серверов
```

## Быстрый старт

```powershell
# Импорт модуля
Import-Module .\MCPServerLauncher.psd1

# Запуск всех серверов
Start-MCPServerLauncher

# Запуск в фоновом режиме
Start-MCPServerLauncher -NoWait

# Проверка статуса
Get-MCPServerStatus

# Остановка
Stop-MCPServers
```

## Команды модуля

| Команда | Псевдоним | Описание |
|---|---|---|
| `Start-MCPServerLauncher` | `Start-MCP` | Запустить все серверы |
| `Stop-MCPServers` | `Stop-MCP` | Остановить все серверы |
| `Get-MCPServerStatus` | `Get-MCPStatus` | Статус серверов |
| `Restart-MCPServers` | `Restart-MCP` | Перезапустить серверы |
| `Test-MCPServerRunning` | — | Проверить конкретный сервер |
| `Get-MCPServerLog` | — | Просмотр логов |

### Start-MCPServerLauncher

```powershell
# Параметры:
#   -ConfigPath  — путь к директории конфигураций (по умолчанию: src\config)
#   -NoWait      — не блокировать консоль после запуска

Start-MCPServerLauncher -ConfigPath 'C:\MyProject\config' -NoWait
```

### Get-MCPServerLog

```powershell
# Последние 100 строк
Get-MCPServerLog -Tail 100

# Следить в реальном времени
Get-MCPServerLog -Follow
```

### Test-MCPServerRunning

```powershell
if (Test-MCPServerRunning -ServerName 'powershell-stdio') {
    Write-Host 'STDIO сервер запущен'
}
```

## Серверы

### McpSTDIOServer.ps1 — STDIO режим

Используется для локальной интеграции с AI-клиентами (Claude Desktop, gemini-cli).
Клиент сам запускает сервер как дочерний процесс и общается через stdin/stdout.

```powershell
.\src\servers\McpSTDIOServer.ps1
```

### McpHttpsServer.ps1 — HTTPS режим

REST API для сетевого взаимодействия. Подходит для веб-приложений и удалённых клиентов.

```powershell
.\src\servers\McpHttpsServer.ps1 -Port 8443 -ServerHost "0.0.0.0"
```

### McpWPCLIServer.ps1 — WordPress CLI

MCP сервер для управления WordPress через WP-CLI.

### McpHuggingFaceServer.ps1 / huggingface_mcp.py

MCP сервер для работы с HuggingFace Hub через облачный Inference API. Требует `HF_TOKEN`.

### local_models_mcp.py — Локальные AI модели

Python MCP STDIO сервер для работы с локальными AI моделями через FastAPI Foundry REST API.
Проксирует запросы к `http://localhost:9696` — единой точке входа для всех бэкендов.

**Требования:** FastAPI Foundry должен быть запущен (`venv\Scripts\python.exe run.py`).

**Инструменты:**

| Tool | Описание | FastAPI endpoint |
|---|---|---|
| `generate` | Генерация текста | `POST /api/v1/generate` |
| `chat` | Чат с историей сессии | `POST /api/v1/ai/chat` |
| `list_models` | Список всех локальных моделей | `GET /api/v1/models` |
| `rag_search` | Поиск по RAG индексу (FAISS) | `POST /api/v1/rag/search` |
| `health` | Статус сервиса | `GET /api/v1/health` |

**Маршрутизация моделей** (через поле `model` в `generate` / `chat`):

```
""                              → Foundry Local (ONNX, по умолчанию)
"llama::D:/models/qwen.gguf"   → llama.cpp
"ollama::llama3"               → Ollama
"hf::microsoft/phi-2"          → HuggingFace Transformers
```

**Запуск вручную:**

```powershell
$env:FASTAPI_BASE_URL = "http://localhost:9696"
python .\src\servers\local_models_mcp.py
```

**Лог файл:** `%TEMP%\mcp-local-models.log`

## Выбор режима: STDIO vs HTTPS

| | STDIO | HTTPS |
|---|---|---|
| Расположение клиента | Та же машина | Любая машина в сети |
| Безопасность | Выше (нет открытых портов) | Требует настройки TLS |
| Типичные клиенты | Claude Desktop, gemini-cli | curl, веб-приложения |
| Запуск | Клиент запускает сервер сам | Сервер запускается отдельно |

## Конфигурация

`src/config/mcp-powershell-stdio.config.json`:

```json
{
  "Port": 8090,
  "Host": "localhost",
  "TimeoutSeconds": 300,
  "Security": {
    "BlockDangerousCommands": true,
    "RestrictedCommands": ["Remove-Item", "Format-Volume", "Stop-Computer"]
  }
}
```

## Интеграция с Claude Desktop

Добавьте в конфигурацию Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "powershell": {
      "command": "pwsh",
      "args": ["-File", "C:\\path\\to\\mcp-powershell-servers\\src\\servers\\McpSTDIOServer.ps1"]
    },
    "local-models": {
      "command": "python",
      "args": ["C:\\path\\to\\mcp-powershell-servers\\src\\servers\\local_models_mcp.py"],
      "env": {
        "FASTAPI_BASE_URL": "http://localhost:9696"
      }
    }
  }
}
```

> **Важно:** перед подключением `local-models` убедитесь, что FastAPI Foundry запущен:
> ```powershell
> venv\Scripts\python.exe run.py
> ```

## Логи

| Сервер | Лог файл |
|---|---|
| McpSTDIOServer.ps1 | `%TEMP%\mcp-powershell-server.log` |
| McpSTDIOServer.v1.ps1 | `%TEMP%\mcp-stdio-server.log` |
| local_models_mcp.py | `%TEMP%\mcp-local-models.log` |
| Launcher | `%TEMP%\mcp-launcher.log` |

```powershell
Get-MCPServerLog -Follow
```

## Устранение неполадок

```powershell
# Проверить версию PowerShell (требуется 7+)
$PSVersionTable.PSVersion

# Разрешить выполнение скриптов
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Просмотр последних ошибок
Get-MCPServerLog -Tail 100
```
