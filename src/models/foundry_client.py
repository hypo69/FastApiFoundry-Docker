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
from datetime import datetime

class FoundryClient:
    """Клиент для работы с Foundry API"""
    
    def __init__(self, base_url="http://localhost:50477/v1"):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.session = None
    
    async def _get_session(self):
        """Получить HTTP сессию"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def close(self):
        """Закрыть HTTP сессию"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def health_check(self):
        """Проверка здоровья Foundry сервиса"""
        try:
            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/models"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    models_count = len(data.get('data', []))
                    return {
                        "status": "healthy",
                        "models_count": models_count,
                        "url": self.base_url,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status}",
                        "url": self.base_url,
                        "timestamp": datetime.now().isoformat()
                    }
        except Exception as e:
            return {
                "status": "disconnected",
                "error": "Foundry server not running on port 50477",
                "url": self.base_url,
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_text(self, prompt: str, **kwargs):
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
                "model": kwargs.get('model', "deepseek-r1:14b"),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get('temperature', 0.7),
                "max_tokens": kwargs.get('max_tokens', 2048),
                "top_p": kwargs.get('top_p', 0.9),
                "top_k": kwargs.get('top_k', 40),
                "stream": False
            }
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data['choices'][0]['message']['content']
                    
                    return {
                        "success": True,
                        "content": content,
                        "model": payload['model'],
                        "tokens_used": data.get('usage', {}).get('total_tokens', 0),
                        "response_data": data
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": "Cannot connect to Foundry server. Please start Foundry on port 50477."
            }

    async def list_available_models(self):
        """Получить список доступных моделей"""
        try:
            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/models"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get('data', [])
                    return {
                        "success": True,
                        "models": models,
                        "count": len(models)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "models": []
                    }
        except Exception as e:
            return {
                "success": False,
                "error": "Foundry server not available",
                "models": []
            }

# Глобальный экземпляр клиента
foundry_client = FoundryClient()