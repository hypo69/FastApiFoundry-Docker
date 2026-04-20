# PowerShell MCP Servers

Документация генерируется автоматически из comment-based help (`.SYNOPSIS`, `.DESCRIPTION`) через PlatyPS при каждом пуше.

Исходный код: `mcp-powershell-servers/src/servers/`

| Сервер | Описание |
|---|---|
| `McpSTDIOServer.ps1` | MCP сервер через STDIO (JSON-RPC) |
| `McpHttpsServer.ps1` | MCP сервер через HTTPS |
| `McpWPCLIServer.ps1` | MCP сервер для WordPress CLI |
| `McpWpServer.ps1` | MCP сервер для WordPress |
| `McpHuggingFaceServer.ps1` | MCP сервер для HuggingFace |

## Утилиты

| Скрипт | Описание |
|---|---|
| [`microsoft_sandbox_operations/`](run-sandbox.md) | Запуск Windows Sandbox (pipeline: launcher + mapper + .wsb) |
