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
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from src.logger import logger as app_logger

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/logs")
async def get_logs(lines: int = 100) -> Dict[str, Any]:
    """Получить последние строки логов из всех основных лог-файлов"""
    try:
        log_candidates = [
            Path("logs/fastapi-app.log"),
            Path("logs/fastapi-foundry.log"),
            Path("logs/app.log"),
        ]

        log_file = next((p for p in log_candidates if p.exists()), None)

        if not log_file:
            return {"success": True, "logs": [], "total_lines": 0, "file": None}

        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()

        recent = all_lines[-lines:] if len(all_lines) > lines else all_lines
        clean = [line.rstrip("\n\r") for line in recent if line.strip()]

        return {
            "success": True,
            "logs": clean,
            "total_lines": len(all_lines),
            "returned_lines": len(clean),
            "file": str(log_file),
        }
    except Exception as e:
        logger.error(f"Ошибка чтения логов: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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


@router.get("/logs/export")
async def export_log(name: str = Query(default="fastapi-foundry", description="Имя логгера"), errors_only: bool = Query(default=False)):
    """Скачать лог-файл через export_to_file.

    Примеры:
        GET /api/v1/logs/export
        GET /api/v1/logs/export?name=foundry-client
        GET /api/v1/logs/export?errors_only=true
    """
    from fastapi.responses import FileResponse
    try:
        named_logger = app_logger if name == app_logger.name else __import__('src.logger', fromlist=['get_logger']).get_logger(name)
        log_path = named_logger.get_error_log_path() if errors_only else named_logger.get_log_path()
        if not log_path.exists():
            raise HTTPException(status_code=404, detail=f"Файл не найден: {log_path}")
        return FileResponse(
            path=str(log_path),
            filename=log_path.name,
            media_type="text/plain"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))