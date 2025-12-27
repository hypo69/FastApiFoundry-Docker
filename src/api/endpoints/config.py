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
from fastapi import APIRouter

router = APIRouter()

@router.get("/config")
async def get_config():
    """Получить конфигурацию системы"""
    try:
        config_file = Path("config.json")
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return {
                "success": True,
                "config": config
            }
        else:
            return {
                "success": False,
                "error": "Config file not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }