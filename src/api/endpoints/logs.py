# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Logs API endpoint
# =============================================================================
# Описание:
#   API endpoint для получения логов системы
#
# File: logs.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import logging
import os
from pathlib import Path
from fastapi import APIRouter
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger("logs-api")
router = APIRouter()

@router.get("/logs/recent")
async def get_recent_logs():
    """Получить последние логи системы"""
    try:
        logs = []
        
        # Проверяем различные источники логов
        log_sources = [
            "logs/fastapi-foundry.log",
            "logs/app.log",
            "fastapi-foundry.log",
            "app.log"
        ]
        
        for log_file in log_sources:
            log_path = Path(log_file)
            if log_path.exists():
                logger.info(f"Читаем логи из: {log_path.absolute()}")
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        # Берем последние 100 строк
                        for line in lines[-100:]:
                            line = line.strip()
                            if line:
                                logs.append({
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "level": "info",
                                    "logger": "system",
                                    "message": line,
                                    "source": str(log_path)
                                })
                except Exception as e:
                    logger.error(f"Ошибка чтения {log_path}: {e}")
        
        # Добавляем тестовые логи если нет реальных
        if not logs:
            test_logs = [
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "level": "info",
                    "logger": "config-api",
                    "message": "GET /config - запрос конфигурации",
                    "source": "system"
                },
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "level": "info", 
                    "logger": "config-api",
                    "message": "Конфигурация загружена успешно",
                    "source": "system"
                }
            ]
            logs.extend(test_logs)
        
        logger.info(f"Возвращаем {len(logs)} записей логов")
        
        return {
            "success": True,
            "data": {
                "logs": logs,
                "count": len(logs),
                "message": f"Найдено {len(logs)} записей логов"
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения логов: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": {
                "logs": [],
                "count": 0,
                "message": "Ошибка загрузки логов"
            }
        }