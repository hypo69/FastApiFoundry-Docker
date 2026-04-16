# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: MCP PowerShell Servers Management Endpoints
# =============================================================================
# Description:
#   REST API for managing MCP PowerShell servers.
#   Starting, stopping, and status of servers from mcp-powershell-servers/settings.json
#
# File: mcp_powershell.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

MCP_SETTINGS_PATH = Path("mcp-powershell-servers/settings.json")
MCP_PIDS_PATH = Path("mcp-powershell-servers/.mcp-pids.json")

# In-memory storage for running processes
_running_processes: Dict[str, subprocess.Popen] = {}


def _load_settings() -> Dict[str, Any]:
    if not MCP_SETTINGS_PATH.exists():
        return {"mcpServers": {}}
    with open(MCP_SETTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_settings(data: Dict[str, Any]) -> None:
    with open(MCP_SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _load_pids() -> Dict[str, int]:
    if not MCP_PIDS_PATH.exists():
        return {}
    try:
        with open(MCP_PIDS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_pids(pids: Dict[str, int]) -> None:
    with open(MCP_PIDS_PATH, "w", encoding="utf-8") as f:
        json.dump(pids, f, indent=2)


def _is_process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def _get_server_status(name: str) -> str:
    proc = _running_processes.get(name)
    if proc and proc.poll() is None:
        return "running"
    pids = _load_pids()
    pid = pids.get(name)
    if pid and _is_process_alive(pid):
        return "running"
    return "stopped"


# ── GET /mcp-powershell/servers ──────────────────────────────────────────────

@router.get("/mcp-powershell/servers")
async def list_mcp_servers():
    """List all MCP servers from settings.json with their status"""
    try:
        settings = _load_settings()
        servers = settings.get("mcpServers", {})
        result = []
        for name, cfg in servers.items():
            result.append({
                "name": name,
                "command": cfg.get("command", ""),
                "description": cfg.get("description", ""),
                "status": _get_server_status(name),
                "envFile": cfg.get("envFile"),
            })
        return {"success": True, "servers": result}
    except Exception as e:
        logger.error(f"❌ list_mcp_servers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── POST /mcp-powershell/servers/{name}/start ────────────────────────────────

@router.post("/mcp-powershell/servers/{name}/start")
async def start_mcp_server(name: str):
    """Start an MCP server by name"""
    try:
        settings = _load_settings()
        servers = settings.get("mcpServers", {})

        if name not in servers:
            raise HTTPException(status_code=404, detail=f"Server '{name}' not found")

        if _get_server_status(name) == "running":
            return {"success": True, "message": f"Server '{name}' already running"}

        cfg = servers[name]
        command = cfg.get("command", "")
        args = cfg.get("args", [])
        env_file = cfg.get("envFile")

        if not command:
            raise HTTPException(status_code=400, detail="No command specified")

        # Load env from envFile if specified
        env = os.environ.copy()
        if env_file and Path(env_file).exists():
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, _, v = line.partition("=")
                        env[k.strip()] = v.strip()

        # Add env from cfg.env if present
        for k, v in cfg.get("env", {}).items():
            resolved = v
            if v.startswith("${") and v.endswith("}"):
                var_name = v[2:-1]
                resolved = os.environ.get(var_name, "")
            env[k] = resolved

        cmd = [command] + [str(a) for a in args]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=str(Path.cwd()),
        )

        _running_processes[name] = proc

        pids = _load_pids()
        pids[name] = proc.pid
        _save_pids(pids)

        logger.info(f"✅ MCP server '{name}' started (PID: {proc.pid})")
        return {"success": True, "message": f"Server '{name}' started", "pid": proc.pid}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ start_mcp_server '{name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── POST /mcp-powershell/servers/{name}/stop ─────────────────────────────────

@router.post("/mcp-powershell/servers/{name}/stop")
async def stop_mcp_server(name: str):
    """Stop an MCP server by name"""
    try:
        stopped = False

        proc = _running_processes.get(name)
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            _running_processes.pop(name, None)
            stopped = True

        pids = _load_pids()
        pid = pids.get(name)
        if pid and _is_process_alive(pid):
            try:
                os.kill(pid, 15)  # SIGTERM
                stopped = True
            except Exception:
                pass
        pids.pop(name, None)
        _save_pids(pids)

        logger.info(f"✅ MCP server '{name}' stopped")
        return {"success": True, "message": f"Server '{name}' {'stopped' if stopped else 'was not running'}"}

    except Exception as e:
        logger.error(f"❌ stop_mcp_server '{name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /mcp-powershell/servers/{name}/status ────────────────────────────────

@router.get("/mcp-powershell/servers/{name}/status")
async def get_mcp_server_status(name: str):
    """Status of a specific MCP server"""
    settings = _load_settings()
    if name not in settings.get("mcpServers", {}):
        raise HTTPException(status_code=404, detail=f"Server '{name}' not found")
    status = _get_server_status(name)
    pids = _load_pids()
    return {"success": True, "name": name, "status": status, "pid": pids.get(name)}


# ── GET /mcp-powershell/settings ─────────────────────────────────────────────

@router.get("/mcp-powershell/settings")
async def get_mcp_settings():
    """Get the contents of mcp-powershell-servers/settings.json"""
    try:
        return {"success": True, "settings": _load_settings()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── POST /mcp-powershell/settings ────────────────────────────────────────────

class McpSettingsRequest(BaseModel):
    settings: Dict[str, Any]


@router.post("/mcp-powershell/settings")
async def save_mcp_settings(request: McpSettingsRequest):
    """Save mcp-powershell-servers/settings.json"""
    try:
        _save_settings(request.settings)
        return {"success": True, "message": "MCP settings saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
