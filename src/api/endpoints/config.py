# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Config Endpoints (Refactored)
# =============================================================================
# Описание:
#   Endpoint для получения конфигурации в веб-интерфейсе
#
# File: config.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ...core.config import config
import json
import os
from datetime import datetime

router = APIRouter()

@router.get("/config")
async def get_config():
    """Получить конфигурацию для веб-интерфейса"""
    try:
        # Получаем полную конфигурацию из config.json
        raw_config = config.get_raw_config()
        
        return {
            "success": True,
            "config": raw_config,
            "foundry_ai": {
                "base_url": config.foundry_base_url or raw_config.get('foundry_ai', {}).get('base_url', 'http://localhost:50477/v1/'),
                "default_model": config.foundry_default_model or raw_config.get('foundry_ai', {}).get('default_model'),
                "auto_load_default": config.foundry_auto_load_default or raw_config.get('foundry_ai', {}).get('auto_load_default', False)
            },
            "api": {
                "host": config.api_host,
                "port": config.api_port
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load configuration: {str(e)}",
            "config": {},
            "foundry_ai": {
                "base_url": "http://localhost:50477/v1/",
                "default_model": None,
                "auto_load_default": False
            },
            "api": {
                "host": "0.0.0.0",
                "port": 9696
            }
        }

class ConfigUpdateRequest(BaseModel):
    config: Dict[str, Any]

@router.post("/config")
async def save_config(request: ConfigUpdateRequest):
    """Сохранить конфигурацию"""
    try:
        config_path = "config.json"
        
        # Создаем бэкап текущей конфигурации
        backup_path = None
        if os.path.exists(config_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"config.json.backup_{timestamp}"
            with open(config_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_content)
        
        # Сохраняем новую конфигурацию
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(request.config, f, indent=2, ensure_ascii=False)
        
        # Обновляем глобальную конфигурацию
        config.reload_config()
        
        return {
            "success": True,
            "message": "Configuration saved successfully",
            "backup_created": backup_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save configuration: {str(e)}")


def _read_env_file(path: str) -> Dict[str, str]:
    """Читает .env файл и возвращает словарь ключ-значение (без комментариев)"""
    result = {}
    if not os.path.exists(path):
        return result
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                result[key.strip()] = value.strip()
    return result


def _write_env_file(path: str, data: Dict[str, str]) -> None:
    """Записывает словарь обратно в .env файл"""
    lines = []
    for key, value in data.items():
        lines.append(f"{key}={value}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _read_json_file(path: str) -> Optional[Dict[str, Any]]:
    """Читает JSON файл, возвращает None если не существует"""
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _read_text_file(path: str) -> Optional[str]:
    """Читает текстовый файл, возвращает None если не существует"""
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


class RawContentRequest(BaseModel):
    content: str


@router.get("/config/env-raw")
async def get_env_raw():
    """Чтение .env файла как сырой текст для редактора"""
    content = _read_text_file(".env") or ""
    return {"success": True, "content": content}


@router.post("/config/env-raw")
async def save_env_raw(request: RawContentRequest):
    """Запись .env файла из редактора (сырой текст)"""
    with open(".env", "w", encoding="utf-8") as f:
        f.write(request.content)
    return {"success": True}


@router.get("/config/raw")
async def get_config_raw():
    """Чтение config.json как сырой текст для редактора"""
    content = _read_text_file("config.json") or ""
    return {"success": True, "content": content}


@router.post("/config/raw")
async def save_config_raw(request: RawContentRequest):
    """Запись config.json из редактора (сырой текст).
    Валидация JSON на стороне клиента, но проверяем и здесь.
    """
    try:
        json.loads(request.content)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Невалидный JSON: {e}")
    with open("config.json", "w", encoding="utf-8") as f:
        f.write(request.content)
    config.reload_config()
    return {"success": True}


class EnvUpdateRequest(BaseModel):
    key: str
    value: str


@router.post("/config/env")
async def save_env_variable(request: EnvUpdateRequest):
    """Сохранение одной переменной окружения в .env файл.

    Используется для сохранения секретов (токены, ключи) из веб-интерфейса.
    Переменная обновляется если существует, добавляется если нет.
    """
    env_path = ".env"
    current = _read_env_file(env_path)
    current[request.key] = request.value

    # Перезапись .env с сохранением всех существующих значений
    lines = []
    for k, v in current.items():
        lines.append(f"{k}={v}")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    # Применяем в текущем процессе сразу
    os.environ[request.key] = request.value

    return {"success": True, "key": request.key}


@router.get("/config/export")
async def export_config():
    """Экспорт ВСЕХ настроек проекта в один JSON: config.json + .env + MCP конфиги"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fastapi-foundry-full-backup-{timestamp}.json"

        export_data = {
            "_meta": {
                "exported_at": datetime.now().isoformat(),
                "project": "FastApiFoundry (Docker)",
                "version": "0.2.1",
                "sources": ["config.json", ".env", "mcp-servers/aistros-foundry/claude-desktop-config.json", ".foundry_url", "mcp-powershell-servers/settings.json"],
                "includes": ["foundry_ai", "huggingface", "llama_cpp", "rag_system", "security", "logging", "mcp_powershell_servers"]
            },
            "config_json": config.get_raw_config(),
            "env": _read_env_file(".env"),
            "mcp_claude_desktop": _read_json_file("mcp-servers/aistros-foundry/claude-desktop-config.json"),
            "mcp_powershell_settings": _read_json_file("mcp-powershell-servers/settings.json"),
            "foundry_url": _read_text_file(".foundry_url"),
            "llama_url":   _read_text_file(".llama_url"),
        }

        return JSONResponse(
            content=export_data,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export configuration: {str(e)}")


class ConfigImportRequest(BaseModel):
    config: Dict[str, Any]
    merge: Optional[bool] = False


@router.post("/config/import")
async def import_config(request: ConfigImportRequest):
    """Импорт полного бэкапа настроек. merge=True — слияние, False — полная замена"""
    try:
        imported = request.config
        imported.pop("_meta", None)

        if not imported:
            raise HTTPException(status_code=400, detail="Empty configuration")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        restored: Dict[str, Any] = {}

        # --- config.json ---
        if "config_json" in imported:
            config_path = "config.json"
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    backup_content = f.read()
                with open(f"config.json.backup_{timestamp}", "w", encoding="utf-8") as f:
                    f.write(backup_content)

            new_config_json = imported["config_json"]
            if request.merge:
                current = config.get_raw_config()
                for section, values in new_config_json.items():
                    if section in current and isinstance(current[section], dict) and isinstance(values, dict):
                        current[section].update(values)
                    else:
                        current[section] = values
                new_config_json = current

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(new_config_json, f, indent=2, ensure_ascii=False)
            config.reload_config()
            restored["config_json"] = True

        # --- .env ---
        if "env" in imported and isinstance(imported["env"], dict):
            env_path = ".env"
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    env_backup = f.read()
                with open(f".env.backup_{timestamp}", "w", encoding="utf-8") as f:
                    f.write(env_backup)

            if request.merge:
                current_env = _read_env_file(env_path)
                current_env.update(imported["env"])
                _write_env_file(env_path, current_env)
            else:
                _write_env_file(env_path, imported["env"])
            restored["env"] = True

        # --- claude-desktop-config.json ---
        if "mcp_claude_desktop" in imported and imported["mcp_claude_desktop"] is not None:
            mcp_path = "mcp-servers/aistros-foundry/claude-desktop-config.json"
            if os.path.exists(mcp_path):
                with open(mcp_path, "r", encoding="utf-8") as f:
                    mcp_backup = f.read()
                with open(f"{mcp_path}.backup_{timestamp}", "w", encoding="utf-8") as f:
                    f.write(mcp_backup)
            with open(mcp_path, "w", encoding="utf-8") as f:
                json.dump(imported["mcp_claude_desktop"], f, indent=2, ensure_ascii=False)
            restored["mcp_claude_desktop"] = True

        # --- .foundry_url ---
        if "foundry_url" in imported and imported["foundry_url"]:
            with open(".foundry_url", "w", encoding="utf-8") as f:
                f.write(imported["foundry_url"])
            restored["foundry_url"] = True

        # --- .llama_url ---
        if "llama_url" in imported and imported["llama_url"]:
            with open(".llama_url", "w", encoding="utf-8") as f:
                f.write(imported["llama_url"])
            restored["llama_url"] = True

        # --- mcp-powershell-servers/settings.json ---
        if "mcp_powershell_settings" in imported and imported["mcp_powershell_settings"] is not None:
            mcp_ps_path = "mcp-powershell-servers/settings.json"
            if os.path.exists(mcp_ps_path):
                with open(mcp_ps_path, "r", encoding="utf-8") as f:
                    mcp_ps_backup = f.read()
                with open(f"{mcp_ps_path}.backup_{timestamp}", "w", encoding="utf-8") as f:
                    f.write(mcp_ps_backup)
            with open(mcp_ps_path, "w", encoding="utf-8") as f:
                json.dump(imported["mcp_powershell_settings"], f, indent=2, ensure_ascii=False)
            restored["mcp_powershell_settings"] = True

        return {
            "success": True,
            "message": f"Configuration {'merged' if request.merge else 'imported'} successfully",
            "restored": restored
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import configuration: {str(e)}")