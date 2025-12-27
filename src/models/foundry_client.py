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
import psutil
from datetime import datetime

class FoundryClient:
    """Клиент для работы с Foundry API"""
    
    def __init__(self, base_url=None):
        # Используем переменную окружения или по умолчанию
        import os
        if base_url:
            self.base_url = base_url
        else:
            foundry_env_url = os.getenv('FOUNDRY_BASE_URL')
            if foundry_env_url:
                self.base_url = foundry_env_url.rstrip('/v1/').rstrip('/') + '/v1'
            else:
                self.base_url = "http://localhost:50477/v1"
        
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.session = None
        print(f"🔗 Инициализация Foundry клиента: {self.base_url}")
    
    def get_foundry_port(self):
        """Получить реальный порт Foundry из запущенных процессов"""
        try:
            # Проверяем порты в диапазоне 50400-50800
            import socket
            for port in range(50400, 50800):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.1)
                        result = s.connect_ex(('127.0.0.1', port))
                        if result == 0:
                            # Порт открыт, проверяем что это Foundry
                            try:
                                import requests
                                response = requests.get(f'http://127.0.0.1:{port}/v1/models', timeout=1)
                                if response.status_code == 200:
                                    return port
                            except:
                                continue
                except:
                    continue
        except:
            pass
        return 50477  # Порт по умолчанию
    
    def update_base_url(self):
        """Обновить base_url с реальным портом"""
        real_port = self.get_foundry_port()
        self.base_url = f"http://localhost:{real_port}/v1"
        return self.base_url
    
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
        """Проверка состояния Foundry сервиса"""
        try:
            # Обновляем URL с реальным портом каждый раз
            import os
            foundry_env_url = os.getenv('FOUNDRY_BASE_URL')
            if foundry_env_url:
                self.base_url = foundry_env_url.rstrip('/v1/').rstrip('/') + '/v1'
            else:
                self.update_base_url()
            
            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/models"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    models_count = len(data.get('data', []))
                    # Извлекаем порт из URL
                    port = int(self.base_url.split(':')[2].split('/')[0])
                    return {
                        "status": "healthy",
                        "models_count": models_count,
                        "url": self.base_url,
                        "port": port,
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
            # При ошибке получаем порт из переменной окружения
            import os
            foundry_env_url = os.getenv('FOUNDRY_BASE_URL', 'http://localhost:50477/v1/')
            try:
                port = int(foundry_env_url.split(':')[2].split('/')[0])
            except:
                port = 50477
            
            return {
                "status": "disconnected",
                "error": f"Сервер Foundry не запущен на порту {port}",
                "url": foundry_env_url,
                "port": port,
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_text(self, prompt: str, **kwargs):
        """Генерация текста через Foundry"""
        try:
            # Проверяем доступность Foundry
            health = await self.health_check()
            if health["status"] != "healthy":
                real_port = health.get("port", 50477)
                return {
                    "success": False,
                    "error": f"Сервер Foundry недоступен. Пожалуйста, запустите Foundry на порту {real_port}.",
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
            real_port = self.get_foundry_port()
            return {
                "success": False,
                "error": f"Не удается подключиться к серверу Foundry. Пожалуйста, запустите Foundry на порту {real_port}."
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
                "error": "Сервер Foundry недоступен",
                "models": []
            }

# Глобальный экземпляр клиента
foundry_client = FoundryClient()