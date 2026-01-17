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
from pydantic import BaseModel
from typing import Dict, Any
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