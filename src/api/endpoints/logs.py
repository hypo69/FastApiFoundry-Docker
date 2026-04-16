# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Logs API Endpoints
# =============================================================================
# Description:
#   API endpoints for retrieving application logs
#   Displays logs on the Logs tab in the web interface
#
# File: logs.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
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
    """Get the last log lines from all main log files"""
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
        logger.error(f"Error reading logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/clear")
async def clear_logs() -> Dict[str, Any]:
    """Clear log file"""
    try:
        log_file = Path("logs/app.log")
        
        if log_file.exists():
            # Clear file
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("")
            
            logger.info("Log file cleared")
            return {
                "success": True,
                "message": "Logs cleared"
            }
        else:
            return {
                "success": True,
                "message": "Log file does not exist"
            }
            
    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing logs: {str(e)}")

@router.get("/logs/download")
async def download_logs():
    """Download log file"""
    try:
        log_file = Path("logs/app.log")
        
        if not log_file.exists():
            raise HTTPException(status_code=404, detail="Log file not found")
        
        from fastapi.responses import FileResponse
        
        logger.info("Downloading log file")
        return FileResponse(
            path=str(log_file),
            filename="app.log",
            media_type="text/plain"
        )
        
    except Exception as e:
        logger.error(f"Error downloading logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading logs: {str(e)}")


@router.get("/logs/export")
async def export_log(name: str = Query(default="fastapi-foundry", description="Logger name"), errors_only: bool = Query(default=False)):
    """Download log file via export_to_file.

    Examples:
        GET /api/v1/logs/export
        GET /api/v1/logs/export?name=foundry-client
        GET /api/v1/logs/export?errors_only=true
    """
    from fastapi.responses import FileResponse
    try:
        named_logger = app_logger if name == app_logger.name else __import__('src.logger', fromlist=['get_logger']).get_logger(name)
        log_path = named_logger.get_error_log_path() if errors_only else named_logger.get_log_path()
        if not log_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {log_path}")
        return FileResponse(
            path=str(log_path),
            filename=log_path.name,
            media_type="text/plain"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
