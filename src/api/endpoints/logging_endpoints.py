# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Logging API Endpoints
# =============================================================================
# Описание:
#   Простые API endpoints для логирования
#   Минимальная функциональность без сложных зависимостей
#
# File: logging_endpoints.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/logs/recent")
async def get_recent_logs():
    """Получить последние записи логов"""
    try:
        import os
        from pathlib import Path
        
        logs_dir = Path("logs")
        all_logs = []
        
        # Основные файлы логов
        log_files = [
            "fastapi-foundry.log",
            "foundry-client.log", 
            "web-logs.log"
        ]
        
        for log_file in log_files:
            log_path = logs_dir / log_file
            if log_path.exists():
                try:
                    # Читаем последние 50 строк
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        recent_lines = lines[-50:] if len(lines) > 50 else lines
                        
                        for line in recent_lines:
                            if line.strip():
                                # Парсим строку лога
                                parts = line.strip().split(' | ')
                                if len(parts) >= 3:
                                    timestamp = parts[0]
                                    level = parts[1].strip()
                                    message = ' | '.join(parts[2:])
                                    
                                    all_logs.append({
                                        "timestamp": timestamp,
                                        "level": level.lower(),
                                        "logger": log_file.replace('.log', ''),
                                        "message": message
                                    })
                                else:
                                    # Простая строка
                                    all_logs.append({
                                        "timestamp": datetime.now().strftime('%H:%M:%S'),
                                        "level": "info",
                                        "logger": log_file.replace('.log', ''),
                                        "message": line.strip()
                                    })
                except Exception as e:
                    logger.error(f"Error reading {log_file}: {e}")
        
        # Сортируем по времени (последние сверху)
        all_logs = sorted(all_logs, key=lambda x: x['timestamp'], reverse=True)[:100]
        
        return {
            "success": True,
            "data": {
                "logs": all_logs,
                "total": len(all_logs),
                "message": f"Загружено {len(all_logs)} записей логов"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": {
                "logs": [],
                "total": 0,
                "message": "Ошибка чтения логов"
            }
        }

@router.post("/logs/web")
async def log_web_message(request: dict):
    """Логирование сообщений с веб-интерфейса"""
    try:
        message = request.get('message', '')
        level = request.get('level', 'info')
        
        # Простое логирование
        if level == 'error':
            logger.error(f"Web UI: {message}")
        elif level == 'warning':
            logger.warning(f"Web UI: {message}")
        else:
            logger.info(f"Web UI: {message}")
        
        return {
            "success": True,
            "message": "Log message recorded"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }