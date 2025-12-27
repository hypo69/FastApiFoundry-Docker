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
    import os
    from ...core.config import settings
    
    try:
        return {
            "success": True,
            "config": {
                "foundry_ai": {
                    "base_url": settings.foundry_base_url,
                    "default_model": settings.foundry_default_model
                },
                "fastapi_server": {
                    "host": settings.api_host,
                    "port": settings.api_port
                }
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }