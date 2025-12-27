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
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("config-api")

router = APIRouter()

@router.get("/config")
async def get_config():
    """Получить полную конфигурацию из config.json"""
    logger.info("GET /config - запрос конфигурации")
    try:
        # Читаем напрямую из корневого config.json
        config_path = Path("config.json")
        logger.info(f"Читаем конфигурацию из: {config_path.absolute()}")
        
        if not config_path.exists():
            logger.error(f"config.json не найден по пути: {config_path.absolute()}")
            return {
                "success": False,
                "error": "config.json not found"
            }
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        logger.info(f"Конфигурация загружена успешно. Секции: {list(config_data.keys())}")
        return {
            "success": True,
            "config": config_data
        }
    except Exception as e:
        logger.error(f"Ошибка загрузки конфигурации: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/config")
async def update_config(request: Request):
    """Обновить конфигурацию в config.json"""
    logger.info("POST /config - запрос обновления конфигурации")
    try:
        # Получаем JSON данные из запроса
        request_data = await request.json()
        logger.info(f"Полученные данные: {list(request_data.keys()) if request_data else 'None'}")
        
        if "config" not in request_data:
            logger.error("Отсутствует поле 'config' в запросе")
            return {
                "success": False,
                "error": "Missing 'config' field in request"
            }
        
        new_config = request_data["config"]
        logger.info(f"Новая конфигурация содержит секции: {list(new_config.keys()) if new_config else 'None'}")
        
        # Создать бэкап
        config_path = Path("config.json")
        backup_path = Path("config.json.backup")
        
        if config_path.exists():
            logger.info(f"Создаем бэкап: {backup_path.absolute()}")
            with open(config_path, 'r', encoding='utf-8') as f:
                backup_data = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_data)
        
        # Сохраняем новую конфигурацию
        logger.info(f"Сохраняем конфигурацию в: {config_path.absolute()}")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=2, ensure_ascii=False)
        
        logger.info("Конфигурация сохранена успешно")
        return {
            "success": True,
            "message": "Configuration updated successfully",
            "backup_created": str(backup_path)
        }
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except Exception as e:
        logger.error(f"Ошибка сохранения конфигурации: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))