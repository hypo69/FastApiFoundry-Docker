# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Foundry Client (Refactored)
# =============================================================================
# Описание:
#   Упрощенный клиент для работы с Foundry API
#   Использует только класс Config для получения настроек
#
# File: foundry_client.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import asyncio
import aiohttp
import json
import socket
import requests
import logging
import os
from datetime import datetime

from ..utils.foundry_finder import find_foundry_port, find_foundry_url

# Настройка логирования
logger = logging.getLogger(__name__)

class FoundryClient:
    """Клиент для работы с Foundry API"""
    
    def __init__(self, base_url=None):
        # Проверяем переменную окружения FOUNDRY_DYNAMIC_PORT
        foundry_port = os.getenv('FOUNDRY_DYNAMIC_PORT')
        if foundry_port and not base_url:
            base_url = f"http://localhost:{foundry_port}/v1/"
            print(f"🔗 Foundry клиент: используется порт из окружения {foundry_port}")
        
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.session = None
        if self.base_url:
            print(f"🔗 Foundry клиент: {self.base_url}")
        else:
            print("🔗 Foundry клиент: ожидание URL...")
    
    async def _get_session(self):
        """Получить HTTP сессию"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def close(self):
        """Закрыть HTTP сессию"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _find_foundry_port(self) -> int | None:
        """Найти порт запущенного Foundry"""
        test_ports = [62171, 50477, 58130]
        logger.info(f"🔍 Поиск Foundry на портах: {test_ports}")
        
        for port in test_ports:
            try:
                logger.debug(f"Проверка порта {port}...")
                response = requests.get(f'http://127.0.0.1:{port}/v1/models', timeout=2)
                if response.status_code == 200:
                    logger.info(f"✅ Foundry найден на порту: {port}")
                    return port
                else:
                    logger.debug(f"❌ Порт {port}: HTTP {response.status_code}")
            except Exception as e:
                logger.debug(f"❌ Порт {port}: {e}")
        
        logger.warning("❌ Foundry не найден на известных портах")
        return None
    
    def _update_base_url(self):
        """Обновить base_url из переменной окружения или Config"""
        # Сначала проверяем переменную окружения
        foundry_port = os.getenv('FOUNDRY_DYNAMIC_PORT')
        if foundry_port:
            self.base_url = f"http://localhost:{foundry_port}/v1/"
            logger.debug(f"✅ Используется порт из окружения: {foundry_port}")
            return
        
        from ..core.config import config
        
        logger.debug("🔄 Обновление base_url...")
        
        # Затем проверяем Config
        if config.foundry_base_url:
            self.base_url = config.foundry_base_url
            logger.info(f"✅ Используется URL из Config: {self.base_url}")
            return
        
        # Если нет в Config - ищем сами
        logger.info("🔍 URL не найден в Config, ищем Foundry...")
        foundry_port = self._find_foundry_port()
        if foundry_port:
            self.base_url = f'http://localhost:{foundry_port}/v1/'
            # Устанавливаем в Config для других компонентов
            config.foundry_base_url = self.base_url
            logger.info(f"✅ Foundry найден и сохранен в Config: {self.base_url}")
        else:
            logger.error("❌ Не удалось найти Foundry")
    
    async def health_check(self):
        """Проверка состояния Foundry"""
        logger.info("🏥 Проверка состояния Foundry...")
        
        try:
            # Обновляем URL перед каждым запросом
            self._update_base_url()
            
            if not self.base_url:
                logger.error("❌ Foundry не найден")
                return {
                    "status": "disconnected",
                    "error": "Foundry не найден",
                    "url": None,
                    "port": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/models"
            logger.debug(f"Отправка запроса к {url}")
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    port = int(self.base_url.split(':')[2].split('/')[0])
                    logger.info(f"✅ Foundry онлайн: {self.base_url}")
                    return {
                        "status": "healthy",
                        "models_count": len(data.get('data', [])),
                        "url": self.base_url,
                        "port": port,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    logger.warning(f"⚠️ Foundry ответил с ошибкой: HTTP {response.status}")
                    return {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status}",
                        "url": self.base_url,
                        "timestamp": datetime.now().isoformat()
                    }
        except Exception as e:
            try:
                port = int(self.base_url.split(':')[2].split('/')[0]) if self.base_url else 50477
            except:
                port = 50477
            
            logger.error(f"❌ Ошибка подключения к Foundry: {e}")
            return {
                "status": "disconnected",
                "error": f"Foundry недоступен: {str(e)}",
                "url": self.base_url,
                "port": port,
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_text(self, prompt: str, **kwargs):
        """Генерация текста"""
        model = kwargs.get('model', "deepseek-r1:14b")
        logger.info(f"🤖 Генерация текста для модели: {model}")
        
        try:
            health = await self.health_check()
            if health["status"] != "healthy":
                logger.error(f"❌ Foundry недоступен: {health.get('error')}")
                return {
                    "success": False,
                    "error": f"Foundry недоступен на порту {health.get('port', 50477)}",
                    "foundry_status": health["status"]
                }
            
            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/chat/completions"
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get('temperature', 0.7),
                "max_tokens": kwargs.get('max_tokens', 2048),
                "stream": False
            }
            
            logger.debug(f"Отправка запроса к {url}")
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'choices' in data and len(data['choices']) > 0:
                        content = data['choices'][0]['message']['content']
                        logger.info("✅ Текст успешно сгенерирован")
                        return {
                            "success": True,
                            "content": content,
                            "model": payload['model'],
                            "tokens_used": data.get('usage', {}).get('total_tokens', 0)
                        }
                    else:
                        logger.error("❌ Некорректный ответ от Foundry")
                        return {
                            "success": False,
                            "error": "Некорректный ответ от Foundry"
                        }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка генерации: HTTP {response.status}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
        except Exception as e:
            logger.error(f"❌ Исключение при генерации: {e}")
            return {
                "success": False,
                "error": f"Ошибка подключения к Foundry: {str(e)}"
            }

    async def generate_stream(self, prompt: str, **kwargs):
        """Генерация текста с потоковой передачей"""
        try:
            health = await self.health_check()
            if health["status"] != "healthy":
                yield {
                    "success": False,
                    "error": f"Foundry недоступен на порту {health.get('port', 50477)}",
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
        logger.info("📋 Получение списка моделей...")
        
        try:
            self._update_base_url()
            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/models"
            
            logger.debug(f"Запрос моделей: {url}")
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get('data', [])
                    logger.info(f"✅ Получено {len(models)} моделей")
                    return {
                        "success": True,
                        "models": models,
                        "count": len(models)
                    }
                else:
                    logger.warning(f"⚠️ Ошибка получения моделей: HTTP {response.status}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "models": []
                    }
        except Exception as e:
            logger.error(f"❌ Исключение при получении моделей: {e}")
            return {
                "success": False,
                "error": "Foundry недоступен",
                "models": []
            }

    async def load_model(self, model_id: str):
        """Загрузить модель"""
        logger.info(f"📥 Загрузка модели: {model_id}")
        
        try:
            self._update_base_url()
            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/models/{model_id}/load"
            
            async with session.post(url) as response:
                if response.status == 200:
                    logger.info(f"✅ Модель {model_id} успешно загружена")
                    return {"success": True, "message": f"Модель {model_id} загружена"}
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка загрузки модели {model_id}: HTTP {response.status}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            logger.error(f"❌ Исключение при загрузке модели {model_id}: {e}")
            return {"success": False, "error": f"Ошибка загрузки модели: {str(e)}"}

    async def unload_model(self, model_id: str):
        """Выгрузить модель"""
        logger.info(f"📤 Выгрузка модели: {model_id}")
        
        try:
            self._update_base_url()
            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/models/{model_id}/unload"
            
            async with session.post(url) as response:
                if response.status == 200:
                    logger.info(f"✅ Модель {model_id} успешно выгружена")
                    return {"success": True, "message": f"Модель {model_id} выгружена"}
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка выгрузки модели {model_id}: HTTP {response.status}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            logger.error(f"❌ Исключение при выгрузке модели {model_id}: {e}")
            return {"success": False, "error": f"Ошибка выгрузки модели: {str(e)}"}

    async def list_models(self):
        """Получить список моделей"""
        return await self.list_available_models()

# Глобальный экземпляр клиента
foundry_client = FoundryClient()