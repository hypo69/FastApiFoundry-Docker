# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Windows OS MCP Server — typed tools for Windows system info
# =============================================================================
# Description:
#   MCP STDIO server exposing Windows OS diagnostics as structured tools.
#   Tools: get_processes, get_services, get_disk_info, get_network_stats,
#          get_system_info, kill_process, get_startup_items
#
# File: mcp/src/servers/windows_os_mcp.py
# Project: AI Assistant (ai_assist)
# Version: 0.7.1
# Changes in 0.7.1:
#   - Initial implementation for Windows OS agent
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import json
import sys
import subprocess
from typing import Any, Dict, List


def _run_ps(script: str) -> str:
    """Run a PowerShell snippet and return stdout."""
    result = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30
    )
    return result.stdout.strip() or result.stderr.strip()


# ── Tool implementations ──────────────────────────────────────────────────────

def get_processes(sort_by: str = "cpu", top: int = 20) -> str:
    """Return top processes sorted by CPU or memory."""
    sort_map = {"cpu": "CPU", "memory": "WorkingSet", "name": "Name"}
    prop = sort_map.get(sort_by, "CPU")
    script = (
        f"Get-Process | Sort-Object -{prop} -Descending | Select-Object -First {top} "
        "Name, Id, CPU, @{N='MemMB';E={[math]::Round($_.WorkingSet/1MB,1)}}, "
        "Responding, StartTime | ConvertTo-Json -Compress"
    )
    return _run_ps(script)


def get_services(filter_status: str = "all") -> str:
    """Return Windows services, optionally filtered by status."""
    where = "" if filter_status == "all" else f"| Where-Object Status -eq '{filter_status}'"
    script = (
        f"Get-Service {where} | Select-Object Name, DisplayName, Status, StartType "
        "| ConvertTo-Json -Compress"
    )
    return _run_ps(script)


def get_disk_info() -> str:
    """Return disk usage for all drives."""
    script = (
        "Get-PSDrive -PSProvider FileSystem | "
        "Select-Object Name, @{N='UsedGB';E={[math]::Round($_.Used/1GB,2)}}, "
        "@{N='FreeGB';E={[math]::Round($_.Free/1GB,2)}}, "
        "@{N='TotalGB';E={[math]::Round(($_.Used+$_.Free)/1GB,2)}} "
        "| ConvertTo-Json -Compress"
    )
    return _run_ps(script)


def get_network_stats() -> str:
    """Return active TCP connections and network adapter stats."""
    script = (
        "$conn = Get-NetTCPConnection -State Established | "
        "Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State | "
        "Select-Object -First 30; "
        "$adapters = Get-NetAdapter | Where-Object Status -eq 'Up' | "
        "Select-Object Name, InterfaceDescription, LinkSpeed; "
        "@{connections=$conn; adapters=$adapters} | ConvertTo-Json -Depth 4 -Compress"
    )
    return _run_ps(script)


def get_system_info() -> str:
    """Return OS version, uptime, CPU and RAM summary."""
    script = (
        "$os = Get-CimInstance Win32_OperatingSystem; "
        "$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1; "
        "@{"
        "  OS=$os.Caption; Version=$os.Version; "
        "  UptimeHours=[math]::Round((New-TimeSpan $os.LastBootUpTime).TotalHours,1); "
        "  TotalRAM_GB=[math]::Round($os.TotalVisibleMemorySize/1MB,1); "
        "  FreeRAM_GB=[math]::Round($os.FreePhysicalMemory/1MB,1); "
        "  CPU=$cpu.Name; Cores=$cpu.NumberOfCores; "
        "  LoadPercent=$cpu.LoadPercentage"
        "} | ConvertTo-Json -Compress"
    )
    return _run_ps(script)


def kill_process(pid: int) -> str:
    """Stop a process by PID."""
    script = f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue; 'done'"
    return _run_ps(script)


def get_startup_items() -> str:
    """Return programs configured to run at startup."""
    script = (
        "Get-CimInstance Win32_StartupCommand | "
        "Select-Object Name, Command, Location, User | ConvertTo-Json -Compress"
    )
    return _run_ps(script)


# ── Tool registry ─────────────────────────────────────────────────────────────

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "get_processes",
        "description": "Список запущенных процессов Windows (топ N по CPU или памяти)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sort_by": {"type": "string", "enum": ["cpu", "memory", "name"], "default": "cpu"},
                "top": {"type": "integer", "default": 20, "minimum": 1, "maximum": 100}
            }
        }
    },
    {
        "name": "get_services",
        "description": "Список служб Windows с фильтром по статусу",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filter_status": {"type": "string", "enum": ["all", "Running", "Stopped"], "default": "all"}
            }
        }
    },
    {
        "name": "get_disk_info",
        "description": "Использование дискового пространства по всем дискам",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_network_stats",
        "description": "Активные TCP соединения и статус сетевых адаптеров",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_system_info",
        "description": "Общая информация о системе: ОС, CPU, RAM, uptime",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "kill_process",
        "description": "Завершить процесс по PID",
        "inputSchema": {
            "type": "object",
            "properties": {"pid": {"type": "integer", "description": "Process ID"}},
            "required": ["pid"]
        }
    },
    {
        "name": "get_startup_items",
        "description": "Программы в автозагрузке Windows",
        "inputSchema": {"type": "object", "properties": {}}
    },
]

_DISPATCH = {
    "get_processes": lambda a: get_processes(a.get("sort_by", "cpu"), int(a.get("top", 20))),
    "get_services": lambda a: get_services(a.get("filter_status", "all")),
    "get_disk_info": lambda a: get_disk_info(),
    "get_network_stats": lambda a: get_network_stats(),
    "get_system_info": lambda a: get_system_info(),
    "kill_process": lambda a: kill_process(int(a["pid"])),
    "get_startup_items": lambda a: get_startup_items(),
}


# ── MCP STDIO server loop ─────────────────────────────────────────────────────

def _respond(id_: Any, result: Any = None, error: Any = None) -> None:
    resp: Dict[str, Any] = {"jsonrpc": "2.0", "id": id_}
    if error:
        resp["error"] = error
    else:
        resp["result"] = result
    sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _handle(req: Dict[str, Any]) -> None:
    id_ = req.get("id")
    method = req.get("method", "")
    params = req.get("params") or {}

    if method == "initialize":
        _respond(id_, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "windows-os", "version": "0.7.1"}
        })
    elif method == "tools/list":
        _respond(id_, {"tools": TOOLS})
    elif method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments") or {}
        fn = _DISPATCH.get(name)
        if not fn:
            _respond(id_, error={"code": -32601, "message": f"Unknown tool: {name}"})
            return
        try:
            output = fn(args)
            _respond(id_, {"content": [{"type": "text", "text": output}]})
        except Exception as e:
            _respond(id_, error={"code": -32603, "message": str(e)})
    else:
        _respond(id_, error={"code": -32601, "message": f"Unknown method: {method}"})


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            _handle(req)
        except json.JSONDecodeError as e:
            _respond(None, error={"code": -32700, "message": f"Parse error: {e}"})


if __name__ == "__main__":
    main()
