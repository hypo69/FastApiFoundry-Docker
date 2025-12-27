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
        """Получить реальный порт Foundry из переменной окружения или процессов"""
        import os
        
        # Сначала проверяем переменную окружения
        foundry_env_url = os.getenv('FOUNDRY_BASE_URL')
        if foundry_env_url:
            try:
                port = int(foundry_env_url.split(':')[2].split('/')[0])
                return port
            except:
                pass
        
        # Проверяем переменную FOUNDRY_PORT
        foundry_port = os.getenv('FOUNDRY_PORT')
        if foundry_port:
            try:
                return int(foundry_port)
            except:
                pass
        
        # Ищем в процессах
        try:
            import socket
            for port in range(50400, 50800):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.1)
                        result = s.connect_ex(('127.0.0.1', port))
                        if result == 0:
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
        return 50477
    
    def update_base_url(self):
        """Обновить base_url с реальным портом"""
        import os
        
        # Проверяем переменные окружения
        foundry_env_url = os.getenv('FOUNDRY_BASE_URL')
        if foundry_env_url:
            self.base_url = foundry_env_url.rstrip('/v1/').rstrip('/') + '/v1'
            print(f"🔗 Используем URL из переменной окружения: {self.base_url}")
            return self.base_url
        
        foundry_port = os.getenv('FOUNDRY_PORT')
        if foundry_port:
            self.base_url = f"http://localhost:{foundry_port}/v1"
            print(f"🔗 Используем порт из переменной окружения: {self.base_url}")
            return self.base_url
        
        # Поиск реального порта
        real_port = self.get_foundry_port()
        self.base_url = f"http://localhost:{real_port}/v1"
        print(f"🔗 Найден порт Foundry: {self.base_url}")
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
            
            print(f"🔗 Отправка запроса к Foundry: {url}")
            print(f"📝 Параметры: {payload}")
            
            async with session.post(url, json=payload) as response:
                print(f"📊 Ответ Foundry: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"📝 Данные от Foundry: {data}")
                    
                    if 'choices' in data and len(data['choices']) > 0:
                        content = data['choices'][0]['message']['content']
                        print(f"✅ Получен ответ: {content[:100]}...")
                        
                        return {
                            "success": True,
                            "content": content,
                            "model": payload['model'],
                            "tokens_used": data.get('usage', {}).get('total_tokens', 0),
                            "response_data": data
                        }
                    else:
                        print(f"❌ Нет choices в ответе: {data}")
                        return {
                            "success": False,
                            "error": "Некорректный формат ответа от Foundry"
                        }
                else:
                    error_text = await response.text()
                    print(f"❌ Ошибка HTTP {response.status}: {error_text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
                    
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            real_port = self.get_foundry_port()
            return {
                "success": False,
                "error": f"Не удается подключиться к серверу Foundry. Пожалуйста, запустите Foundry на порту {real_port}."
            }

    async def generate_stream(self, prompt: str, **kwargs):
        """Генерация текста с потоковой передачей"""
        try:
            # Проверяем доступность Foundry
            health = await self.health_check()
            if health["status"] != "healthy":
                yield {
                    "success": False,
                    "error": f"Сервер Foundry недоступен. Пожалуйста, запустите Foundry на порту {health.get('port', 50477)}.",
                    "foundry_status": health["status"]
                }
                return
            
            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/chat/completions"
            
            payload = {
                "model": kwargs.get('model', "deepseek-r1:14b"),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get('temperature', 0.7),
                "max_tokens": kwargs.get('max_tokens', 2048),
                "top_p": kwargs.get('top_p', 0.9),
                "top_k": kwargs.get('top_k', 40),
                "stream": True
            }
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    async for line in response.content:
                        if line:
                            line_str = line.decode('utf-8').strip()
                            if line_str.startswith('data: '):
                                data_str = line_str[6:]
                                if data_str == '[DONE]':
                                    yield {"success": True, "finished": True}
                                    break
                                try:
                                    data = json.loads(data_str)
                                    if 'choices' in data and len(data['choices']) > 0:
                                        delta = data['choices'][0].get('delta', {})
                                        content = delta.get('content', '')
                                        if content:
                                            yield {"success": True, "content": content, "finished": False}
                                except json.JSONDecodeError:
                                    continue
                else:
                    error_text = await response.text()
                    yield {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
                    
        except Exception as e:
            yield {
                "success": False,
                "error": f"Ошибка подключения к Foundry: {str(e)}"
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

    async def load_model(self, model_id: str):
        """Загрузить модель в память"""
        try:
            # Обновляем URL перед запросом
            self.update_base_url()
            
            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/models/{model_id}/load"
            
            async with session.post(url) as response:
                if response.status == 200:
                    return {"success": True, "message": f"Модель {model_id} загружена"}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": f"Cannot connect to host {self.base_url}: {str(e)}"}

    async def unload_model(self, model_id: str):
        """Выгрузить модель из памяти"""
        try:
            # Обновляем URL перед запросом
            self.update_base_url()
            
            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/models/{model_id}/unload"
            
            async with session.post(url) as response:
                if response.status == 200:
                    return {"success": True, "message": f"Модель {model_id} выгружена"}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": f"Cannot connect to host {self.base_url}: {str(e)}"}

    async def list_models(self):
        """Получить список моделей с детальной информацией"""
        return await self.list_available_models()

# Глобальный экземпляр клиента
# Инициализируется с динамическим определением порта
foundry_client = FoundryClient()