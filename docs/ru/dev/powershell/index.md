# MCP Servers

Все MCP серверы проекта расположены в `mcp/src/servers/`.

Поддерживаются два типа серверов:

- **PowerShell** — STDIO и HTTPS, выполняют PowerShell-скрипты и WP-CLI команды
- **Python** — STDIO, проксируют запросы к FastAPI Foundry, FTP, HuggingFace, документации, Windows OS

## PowerShell серверы

| Файл | Протокол | Назначение |
|---|---|---|
| [`McpSTDIOServer.ps1`](mcp-stdio.md) | STDIO | Выполнение произвольных PowerShell скриптов |
| [`McpHttpsServer.ps1`](mcp-https.md) | HTTP (порт 8090) | То же через HTTP REST |
| [`McpWPCLIServer.ps1`](mcp-wpcli.md) | STDIO | Выполнение WP-CLI команд |
| [`McpHuggingFaceServer.ps1`](mcp-huggingface-ps.md) | HTTP SSE | Запросы к HuggingFace Inference API |

## Python серверы

| Файл | Протокол | Назначение |
|---|---|---|
| [`local_models_mcp.py`](mcp-local-models.md) | STDIO | Проксирование к FastAPI Foundry (generate, chat, RAG, health) |
| [`ftp_mcp.py`](mcp-ftp.md) | STDIO | FTP операции (list, upload, download, delete, rename) |
| [`huggingface_mcp.py`](mcp-huggingface-py.md) | STDIO | HuggingFace Inference API (text_generation) |
| [`docs_deploy_mcp.py`](mcp-docs-deploy.md) | STDIO | Деплой MkDocs документации на FTP |
| [`windows_os_mcp.py`](mcp-windows-os.md) | STDIO | Диагностика Windows OS (процессы, службы, диски, сеть) |

## Утилиты

| Скрипт | Описание |
|---|---|
| [`run-sandbox.ps1`](run-sandbox.md) | Запуск Windows Sandbox |
