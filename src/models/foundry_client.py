# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Foundry Client with Full Model Support
# =============================================================================
# Описание:
#   Клиент для работы с Foundry API с поддержкой всех возможностей моделей
#   Включает управление моделями, генерацию текста, статус сервиса
#
# File: foundry_client.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import asyncio
import aiohttp
import json
import logging
import subprocess
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..core.config import settings
from ..utils.logging_system import get_logger

# Создать логгер для Foundry клиента
logger = get_logger("foundry-client")

class FoundryClient:
    """Клиент для работы с Foundry API"""
    
    def __init__(self):
        self.base_url = settings.foundry_base_url
        self.timeout = aiohttp.ClientTimeout(total=settings.foundry_timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self._lock = asyncio.Lock()
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получить HTTP сессию"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def close(self):
        """Закрыть HTTP сессию"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья Foundry сервиса"""
        logger.debug("Начало проверки здоровья Foundry сервиса", url=self.base_url)
        
        try:
            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/models"
            
            with logger.timer("foundry_health_check", url=url):
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        models_count = len(data.get('data', []))
                        logger.info("Foundry сервис здоров", 
                                   models_count=models_count, 
                                   url=self.base_url)
                        return {
                            "status": "healthy",
                            "models_count": models_count,
                            "url": self.base_url,
                            "timestamp": datetime.now()
                        }
                    else:
                        logger.warning("Foundry сервис недоступен", 
                                      status_code=response.status, 
                                      url=self.base_url)
                        return {
                            "status": "unhealthy",
                            "error": f"HTTP {response.status}",
                            "url": self.base_url,
                            "timestamp": datetime.now()
                        }
        except Exception as e:
            logger.error("Критическая ошибка проверки здоровья Foundry", 
                        error=str(e), url=self.base_url, exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "url": self.base_url,
                "timestamp": datetime.now()
            }
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Получить статус сервиса Foundry через API проверку"""
        logger.debug("Проверка статуса Foundry сервиса")
        
        try:
            # Проверяем доступность через API вместо команды service
            health = await self.health_check()
            
            if health["status"] == "healthy":
                logger.info("Foundry сервис работает нормально", 
                           models_count=health.get("models_count", 0))
                return {
                    "success": True,
                    "running": True,
                    "message": "Service is running",
                    "models_count": health.get("models_count", 0),
                    "url": health["url"]
                }
            else:
                logger.warning("Foundry сервис не отвечает", 
                              error=health.get("error", "Unknown error"))
                return {
                    "success": False,
                    "running": False,
                    "message": "Service is not responding",
                    "error": health.get("error", "Unknown error")
                }
                
        except Exception as e:
            logger.exception("Критическая ошибка проверки статуса сервиса", error=str(e))
            return {
                "success": False,
                "running": False,
                "error": str(e),
                "message": "Error checking service status"
            }

    async def start_service(self) -> Dict[str, Any]:
        """Запустить сервис Foundry (заглушка)"""
        # Foundry уже работает, проверяем статус
        health = await self.health_check()
        if health["status"] == "healthy":
            return {
                "success": True,
                "message": "Foundry service is already running",
                "status": "running"
            }
        else:
            return {
                "success": False,
                "message": "Foundry service is not responding",
                "error": health.get("error", "Service not available")
            }
    
    async def stop_service(self) -> Dict[str, Any]:
        """Остановить сервис Foundry (заглушка)"""
        return {
            "success": False,
            "message": "Cannot stop external Foundry service",
            "error": "Service is managed externally"
        }
    
    async def list_available_models(self) -> Dict[str, Any]:
        """Получить список доступных моделей"""
        logger.debug("Запрос списка доступных моделей")
        
        try:
            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/models"
            
            with logger.timer("list_models", url=url):
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get('data', [])
                        logger.info("Получен список моделей", 
                                   models_count=len(models),
                                   models=[m.get('id', 'unknown') for m in models[:5]])  # Первые 5
                        return {
                            "success": True,
                            "models": models,
                            "count": len(models)
                        }
                    else:
                        logger.error("Ошибка получения списка моделей", 
                                    status_code=response.status)
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "models": []
                        }
        except Exception as e:
            logger.exception("Критическая ошибка получения списка моделей", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "models": []
            }
    
    async def run_model(self, model_name: str) -> Dict[str, Any]:
        """Запустить модель (заглушка)"""
        # Модели уже запущены в Foundry
        models = await self.list_available_models()
        if models["success"]:
            model_ids = [m["id"] for m in models["models"]]
            if model_name in model_ids:
                return {
                    "success": True,
                    "message": f"Model {model_name} is available",
                    "model": model_name
                }
            else:
                return {
                    "success": False,
                    "error": f"Model {model_name} not found",
                    "available_models": model_ids
                }
        else:
            return {
                "success": False,
                "error": "Cannot list models"
            }

# Глобальный экземпляр клиента
foundry_client = FoundryClient()