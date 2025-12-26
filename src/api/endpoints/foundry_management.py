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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/foundry", tags=["foundry"])

class FoundryResponse(BaseModel):
    success: bool
    message: str
    status: Optional[str] = None
    models: Optional[List[str]] = None
    error: Optional[str] = None

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
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:50477/v1/models', timeout=5) as response:
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

@router.post("/install", response_model=FoundryResponse)
async def install_foundry():
    """Установить Foundry"""
    try:
        # Проверяем, не установлен ли уже
        if is_foundry_running() or is_port_in_use(50477):
            return FoundryResponse(
                success=False,
                message="Foundry уже установлен или запущен",
                status="already_installed"
            )
        
        # Установка Foundry через curl
        try:
            # Для Linux/Unix систем в Docker
            process = subprocess.run(
                ['curl', '-L', 'https://foundry.paradigm.xyz', '|', 'bash'],
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if process.returncode == 0:
                # Запуск foundryup
                foundryup_process = subprocess.run(
                    ['foundryup'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if foundryup_process.returncode == 0:
                    return FoundryResponse(
                        success=True,
                        message="Foundry успешно установлен",
                        status="installed"
                    )
                else:
                    return FoundryResponse(
                        success=False,
                        message="Ошибка при запуске foundryup",
                        status="failed",
                        error=foundryup_process.stderr
                    )
            else:
                return FoundryResponse(
                    success=False,
                    message="Ошибка скачивания Foundry",
                    status="failed",
                    error=process.stderr
                )
                
        except subprocess.TimeoutExpired:
            return FoundryResponse(
                success=False,
                message="Таймаут установки Foundry",
                status="timeout"
            )
            
    except Exception as e:
        logger.error(f"Error installing Foundry: {e}")
        return FoundryResponse(
            success=False,
            message="Ошибка при установке Foundry",
            status="error",
            error=str(e)
        )

@router.post("/start", response_model=FoundryResponse)
async def start_foundry():
    """Запустить Foundry сервис"""
    try:
        # Проверить, не запущен ли уже
        if is_foundry_running() or is_port_in_use(50477):
            return FoundryResponse(
                success=False,
                message="Foundry уже запущен или порт 50477 занят",
                status="already_running"
            )
        
        # Попытка запуска Foundry
        # Используем наш launcher скрипт
        try:
            # Сначала пробуем через наш launcher
            launcher_path = Path(__file__).parent.parent.parent.parent / "utils" / "foundry_launcher.py"
            if launcher_path.exists():
                process = subprocess.Popen(
                    [sys.executable, str(launcher_path), '--start', '--port', '50477'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Ждем завершения launcher'а
                stdout, stderr = process.communicate(timeout=30)
                
                if process.returncode == 0:
                    # Проверяем, что Foundry действительно запустился
                    await asyncio.sleep(2)
                    health = await check_foundry_health()
                    if health['status'] == 'healthy':
                        return FoundryResponse(
                            success=True,
                            message="Foundry успешно запущен через launcher",
                            status="running",
                            models=health.get('models', [])
                        )
                    else:
                        return FoundryResponse(
                            success=False,
                            message="Foundry запущен, но не отвечает на запросы",
                            status="starting",
                            error=health.get('error')
                        )
                else:
                    error_msg = stderr.decode() if stderr else "Unknown launcher error"
                    return FoundryResponse(
                        success=False,
                        message="Launcher не смог запустить Foundry",
                        status="failed",
                        error=error_msg
                    )
            
            # Fallback: прямой запуск foundry
            process = subprocess.Popen(
                ['foundry', '--port', '50477'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP') else 0
            )
            
            # Ждем немного, чтобы процесс запустился
            await asyncio.sleep(2)
            
            # Проверяем, что процесс действительно запустился
            if process.poll() is None:  # Процесс еще работает
                health = await check_foundry_health()
                if health['status'] == 'healthy':
                    return FoundryResponse(
                        success=True,
                        message="Foundry успешно запущен",
                        status="running",
                        models=health.get('models', [])
                    )
                else:
                    return FoundryResponse(
                        success=False,
                        message="Foundry запущен, но не отвечает на запросы",
                        status="starting",
                        error=health.get('error')
                    )
            else:
                # Процесс завершился с ошибкой
                stderr = process.stderr.read().decode() if process.stderr else "Unknown error"
                return FoundryResponse(
                    success=False,
                    message="Foundry не удалось запустить",
                    status="failed",
                    error=stderr
                )
                
        except FileNotFoundError:
            return FoundryResponse(
                success=False,
                message="Foundry не найден в системе",
                status="not_found",
                error="Установите Foundry: https://github.com/foundry-rs/foundry"
            )
            
    except Exception as e:
        logger.error(f"Error starting Foundry: {e}")
        return FoundryResponse(
            success=False,
            message="Ошибка при запуске Foundry",
            status="error",
            error=str(e)
        )

@router.post("/stop", response_model=FoundryResponse)
async def stop_foundry():
    """Остановить Foundry сервис"""
    try:
        stopped_processes = 0
        
        # Найти и остановить все процессы Foundry
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('foundry' in str(arg).lower() for arg in cmdline):
                    proc.terminate()
                    stopped_processes += 1
                    logger.info(f"Terminated Foundry process {proc.pid}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if stopped_processes > 0:
            # Ждем немного, чтобы процессы завершились
            await asyncio.sleep(1)
            
            return FoundryResponse(
                success=True,
                message=f"Остановлено {stopped_processes} процессов Foundry",
                status="stopped"
            )
        else:
            return FoundryResponse(
                success=False,
                message="Foundry процессы не найдены",
                status="not_running"
            )
            
    except Exception as e:
        logger.error(f"Error stopping Foundry: {e}")
        return FoundryResponse(
            success=False,
            message="Ошибка при остановке Foundry",
            status="error",
            error=str(e)
        )

@router.get("/status", response_model=FoundryResponse)
async def get_foundry_status():
    """Получить статус Foundry сервиса"""
    try:
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
                message="Foundry не запущен",
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