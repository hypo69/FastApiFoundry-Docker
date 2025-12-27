# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Foundry Service Management API
# =============================================================================
# Описание:
#   API endpoints для управления Foundry сервисом
#   Запуск, остановка и проверка статуса Foundry
#
# Примеры:
#   POST /api/v1/foundry/start - Запуск Foundry
#   POST /api/v1/foundry/stop - Остановка Foundry
#   GET /api/v1/foundry/status - Проверка статуса
#
# File: foundry_management.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import subprocess
import psutil
import asyncio
import aiohttp
import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging

# Импортируем утилиту для управления портами
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "utils"))
from port_manager import ensure_port_free

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/foundry", tags=["foundry"])

class FoundryResponse(BaseModel):
    success: bool
    message: str
    status: Optional[str] = None
    models: Optional[List[str]] = None
    error: Optional[str] = None

def is_foundry_installed() -> bool:
    """Проверить, установлен ли Foundry"""
    try:
        result = subprocess.run(['foundry', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def is_foundry_running() -> bool:
    """Проверить, запущен ли Foundry процесс"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = proc.info.get('cmdline', [])
            if cmdline and any('foundry' in str(arg).lower() for arg in cmdline):
                return True
        return False
    except Exception as e:
        logger.error(f"Error checking Foundry process: {e}")
        return False

def is_port_in_use(port: int) -> bool:
    """Проверить, используется ли порт"""
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return True
        return False
    except Exception:
        return False

async def check_foundry_health() -> dict:
    """Проверить здоровье Foundry через HTTP"""
    import os
    foundry_url = os.getenv('FOUNDRY_BASE_URL', 'http://localhost:50477/v1/')
    base_url = foundry_url.rstrip('/v1/').rstrip('/')
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{base_url}/v1/models', timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model.get('id', 'unknown') for model in data.get('data', [])]
                    return {'status': 'healthy', 'models': models}
                else:
                    return {'status': 'unhealthy', 'error': f'HTTP {response.status}'}
    except asyncio.TimeoutError:
        return {'status': 'timeout', 'error': 'Connection timeout'}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@router.post("/start", response_model=FoundryResponse)
async def start_foundry():
    """Запустить Foundry сервис (отключено - используйте start.ps1)"""
    return FoundryResponse(
        success=False,
        message="Запуск Foundry отключен. Используйте start.ps1 для управления Foundry",
        status="disabled",
        error="Use start.ps1 script to manage Foundry"
    )

@router.post("/stop", response_model=FoundryResponse)
async def stop_foundry():
    """Остановить Foundry сервис (отключено - используйте Ctrl+C)"""
    return FoundryResponse(
        success=False,
        message="Остановка Foundry отключена. Используйте Ctrl+C в консоли start.ps1",
        status="disabled",
        error="Use Ctrl+C in start.ps1 console to stop"
    )

@router.get("/status", response_model=FoundryResponse)
async def get_foundry_status():
    """Получить статус Foundry сервиса"""
    try:
        # Проверяем установку
        foundry_installed = is_foundry_installed()
        
        if not foundry_installed:
            return FoundryResponse(
                success=True,
                message="Foundry не установлен",
                status="not_installed"
            )
        
        # Проверить процессы
        process_running = is_foundry_running()
        port_in_use = is_port_in_use(50477)
        
        # Проверить HTTP доступность
        health = await check_foundry_health()
        
        if health['status'] == 'healthy':
            return FoundryResponse(
                success=True,
                message="Foundry работает нормально",
                status="running",
                models=health.get('models', [])
            )
        elif process_running or port_in_use:
            return FoundryResponse(
                success=True,
                message="Foundry запущен, но не отвечает",
                status="starting",
                error=health.get('error')
            )
        else:
            return FoundryResponse(
                success=True,
                message="Foundry установлен, но не запущен",
                status="stopped"
            )
            
    except Exception as e:
        logger.error(f"Error checking Foundry status: {e}")
        return FoundryResponse(
            success=False,
            message="Ошибка при проверке статуса",
            status="error",
            error=str(e)
        )