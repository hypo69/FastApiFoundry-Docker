# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Config endpoint
# =============================================================================
# Описание:
#   Endpoint для получения конфигурации системы
#
# File: config.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
from ...config_manager import config

router = APIRouter()

@router.get("/config")
async def get_config():
    """Получить полную конфигурацию из config.json"""
    try:
        return {
            "success": True,
            "config": config.get_raw_config()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/config")
async def update_config(request: Request):
    """Обновить конфигурацию в config.json"""
    try:
        # Получаем JSON данные из запроса
        request_data = await request.json()
        
        if "config" not in request_data:
            raise HTTPException(status_code=400, detail="Missing 'config' field")
        
        new_config = request_data["config"]
        
        # Создать бэкап
        config_path = Path("config.json")
        backup_path = Path("config.json.backup")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                backup_data = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_data)
        
        # Обновляем конфигурацию
        config.update_config(new_config)
        
        return {
            "success": True,
            "message": "Configuration updated successfully",
            "backup_created": str(backup_path)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }