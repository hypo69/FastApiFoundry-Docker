# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Logs API Endpoints
# =============================================================================
# Описание:
#   API endpoints для получения логов приложения
#   Отображает логи на вкладке Logs в веб-интерфейсе
#
# File: logs.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import os
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/logs")
async def get_logs(lines: int = 100) -> Dict[str, Any]:
    """Получить последние строки логов"""
    try:
        log_file = Path("logs/app.log")
        
        if not log_file.exists():
            logger.warning("Файл логов не найден")
            return {
                "success": True,
                "logs": ["Файл логов не найден"],
                "total_lines": 0
            }
        
        # Читаем последние N строк
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            
        # Берем последние lines строк
        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        # Убираем переносы строк
        clean_lines = [line.rstrip('\n\r') for line in recent_lines]
        
        logger.info(f"Получено {len(clean_lines)} строк логов")
        
        return {
            "success": True,
            "logs": clean_lines,
            "total_lines": len(all_lines),
            "returned_lines": len(clean_lines)
        }
        
    except Exception as e:
        logger.error(f"Ошибка чтения логов: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка чтения логов: {str(e)}")

@router.get("/logs/clear")
async def clear_logs() -> Dict[str, Any]:
    """Очистить файл логов"""
    try:
        log_file = Path("logs/app.log")
        
        if log_file.exists():
            # Очищаем файл
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("")
            
            logger.info("Файл логов очищен")
            return {
                "success": True,
                "message": "Логи очищены"
            }
        else:
            return {
                "success": True,
                "message": "Файл логов не существует"
            }
            
    except Exception as e:
        logger.error(f"Ошибка очистки логов: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка очистки логов: {str(e)}")

@router.get("/logs/download")
async def download_logs():
    """Скачать файл логов"""
    try:
        log_file = Path("logs/app.log")
        
        if not log_file.exists():
            raise HTTPException(status_code=404, detail="Файл логов не найден")
        
        from fastapi.responses import FileResponse
        
        logger.info("Скачивание файла логов")
        return FileResponse(
            path=str(log_file),
            filename="app.log",
            media_type="text/plain"
        )
        
    except Exception as e:
        logger.error(f"Ошибка скачивания логов: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка скачивания логов: {str(e)}")