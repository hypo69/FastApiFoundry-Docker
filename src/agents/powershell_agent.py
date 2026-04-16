# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: PowerShell Agent — агент для работы с локальной системой
# =============================================================================
# Описание:
#   Инструменты:
#     - run_powershell : выполнить PowerShell через McpSTDIOServer.ps1
#     - run_wp_cli     : выполнить WP-CLI через McpWPCLIServer.ps1
#     - http_get       : HTTP GET запрос
#
# File: src/agents/powershell_agent.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp

from .base import BaseAgent, ToolDefinition

logger = logging.getLogger(__name__)


def _find_server_script(name: str) -> Optional[str]:
    p = Path("mcp-powershell-servers/src/servers") / f"{name}.ps1"
    return str(p) if p.exists() else None


def _call_mcp_stdio(script_path: str, method: str, params: Dict) -> Dict:
    """Отправить один JSON-RPC запрос в STDIO сервер"""
    request = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    try:
        proc = subprocess.run(
            ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script_path],
            input=request,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(Path.cwd()),
        )
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
        return {"error": f"No JSON in stdout. stderr: {proc.stderr[:300]}"}
    except subprocess.TimeoutExpired:
        return {"error": "MCP server timeout (30s)"}
    except FileNotFoundError:
        return {"error": "pwsh not found. Install PowerShell 7+"}
    except Exception as e:
        return {"error": str(e)}


def _extract_content(response: Dict) -> str:
    result = response.get("result", {})
    content = result.get("content", [])
    if content:
        return "\n".join(c.get("text", "") for c in content if c.get("type") == "text")
    if "error" in response:
        return f"❌ {response['error']}"
    return "Команда выполнена, результат пустой"


class PowerShellAgent(BaseAgent):
    """Агент для работы с локальной системой через MCP PowerShell серверы"""

    name = "powershell"
    description = "Выполняет команды PowerShell, WP-CLI и HTTP запросы на локальной машине"

    @property
    def tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(
                name="run_powershell",
                description="Выполняет PowerShell команду или скрипт на локальной машине",
                parameters={
                    "type": "object",
                    "properties": {
                        "script": {
                            "type": "string",
                            "description": "PowerShell код. Например: 'Get-ChildItem' или 'ls'"
                        },
                        "working_directory": {
                            "type": "string",
                            "description": "Рабочая директория (опционально)"
                        }
                    },
                    "required": ["script"]
                }
            ),
            ToolDefinition(
                name="run_wp_cli",
                description="Выполняет команду WP-CLI для управления WordPress",
                parameters={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Аргументы WP-CLI. Например: 'post list'"
                        },
                        "working_directory": {
                            "type": "string",
                            "description": "Путь к директории WordPress"
                        }
                    },
                    "required": ["command"]
                }
            ),
            ToolDefinition(
                name="http_get",
                description="Выполняет HTTP GET запрос к указанному URL",
                parameters={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL для GET запроса"}
                    },
                    "required": ["url"]
                }
            ),
        ]

    async def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        if name == "run_powershell":
            return await self._run_powershell(arguments)
        if name == "run_wp_cli":
            return await self._run_wp_cli(arguments)
        if name == "http_get":
            return await self._http_get(arguments)
        return f"❌ Неизвестный инструмент: {name}"

    async def _run_powershell(self, args: Dict) -> str:
        script_path = _find_server_script("McpSTDIOServer")
        if not script_path:
            return "❌ McpSTDIOServer.ps1 не найден"
        _call_mcp_stdio(script_path, "initialize", {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "FastApiFoundry", "version": "0.4.1"}
        })
        response = _call_mcp_stdio(script_path, "tools/call", {
            "name": "run-script",
            "arguments": {
                "script": args["script"],
                "workingDirectory": args.get("working_directory", str(Path.cwd())),
                "timeoutSeconds": 30
            }
        })
        return _extract_content(response)

    async def _run_wp_cli(self, args: Dict) -> str:
        script_path = _find_server_script("McpWPCLIServer")
        if not script_path:
            return "❌ McpWPCLIServer.ps1 не найден"
        _call_mcp_stdio(script_path, "initialize", {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "FastApiFoundry", "version": "0.4.1"}
        })
        response = _call_mcp_stdio(script_path, "tools/call", {
            "name": "run-wp-cli",
            "arguments": {
                "commandArguments": args["command"],
                "workingDirectory": args.get("working_directory", str(Path.cwd()))
            }
        })
        return _extract_content(response)

    async def _http_get(self, args: Dict) -> str:
        url = args.get("url", "")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    text = await resp.text()
                    return f"HTTP {resp.status}\n{text[:2000]}"
        except Exception as e:
            return f"❌ HTTP ошибка: {e}"
