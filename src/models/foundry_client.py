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
            logger.warning("Foundry сервер недоступен (порт 50477)", error=str(e))
            return {
                "status": "disconnected",
                "error": "Foundry server not running on port 50477",
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
            logger.warning("Не удалось проверить статус Foundry сервиса", error=str(e))
            return {
                "success": False,
                "running": False,
                "error": "Foundry server not available",
                "message": "Cannot connect to Foundry service"
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
            logger.warning("Не удалось получить список моделей Foundry", error=str(e))
            return {
                "success": False,
                "error": "Foundry server not available",
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
    async def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Генерация текста через Foundry"""
        try:
            # Проверяем доступность Foundry
            health = await self.health_check()
            if health["status"] != "healthy":
                return {
                    "success": False,
                    "error": "Foundry server not available. Please start Foundry on port 50477.",
                    "foundry_status": health["status"]
                }
            
            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/chat/completions"
            
            payload = {
                "model": kwargs.get('model', settings.foundry_default_model),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get('temperature', settings.foundry_temperature),
                "max_tokens": kwargs.get('max_tokens', settings.foundry_max_tokens),
                "top_p": kwargs.get('top_p', settings.foundry_top_p),
                "top_k": kwargs.get('top_k', settings.foundry_top_k),
                "stream": False
            }
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data['choices'][0]['message']['content']
                    
                    logger.info("Текст успешно сгенерирован", 
                               model=payload['model'],
                               tokens=data.get('usage', {}).get('total_tokens', 0))
                    
                    return {
                        "success": True,
                        "content": content,
                        "model": payload['model'],
                        "tokens_used": data.get('usage', {}).get('total_tokens', 0),
                        "response_data": data
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка генерации текста: HTTP {response.status}", 
                               error=error_text)
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
                    
        except Exception as e:
            logger.warning("Не удалось сгенерировать текст через Foundry", error=str(e))
            return {
                "success": False,
                "error": "Cannot connect to Foundry server. Please start Foundry on port 50477."
            }