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
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
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
            logger.info(f"Foundry client: using port from environment {foundry_port}")
        
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.session = None
        if self.base_url:
            logger.info(f"Foundry client: {self.base_url}")
        else:
            logger.info("Foundry client: waiting for URL...")
    
    async def _get_session(self):
        """Получить HTTP сессию"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def close(self):
        """Закрыть HTTP сессию"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _find_foundry_port(self) -> int | None:
        """Найти порт запущенного Foundry"""
        test_ports = [62171, 50477, 58130]
        logger.info(f"🔍 Поиск Foundry на портах: {test_ports}")
        
        session = await self._get_session()
        
        for port in test_ports:
            try:
                logger.debug(f"Проверка порта {port}...")
                async with session.get(f'http://127.0.0.1:{port}/v1/models', timeout=aiohttp.ClientTimeout(total=2)) as response:
                    if response.status == 200:
                        logger.info(f"✅ Foundry найден на порту: {port}")
                        return port
                    else:
                        logger.debug(f"❌ Порт {port}: HTTP {response.status}")
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.debug(f"❌ Порт {port}: {e}")
        
        logger.warning("❌ Foundry не найден на известных портах")
        return None
    
    async def _update_base_url(self):
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
        foundry_port = await self._find_foundry_port()
        if foundry_port:
            self.base_url = f'http://localhost:{foundry_port}/v1/'
            # Устанавливаем в Config для других компонентов
            config.foundry_base_url = self.base_url
            logger.info(f"✅ Foundry найден и сохранен в Config: {self.base_url}")
        else:
            logger.error("❌ Не удалось найти Foundry")
    
    async def health_check(self):
        """Проверка состояния Foundry"""
        logger.debug("🏥 Проверка состояния Foundry...")
        
        try:
            # Обновляем URL перед каждым запросом
            await self._update_base_url()
            
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
                    try:
                        from urllib.parse import urlparse
                        parsed = urlparse(self.base_url)
                        port = parsed.port or 50477
                    except (ValueError, AttributeError, IndexError):
                        port = 50477
                    models_count = len(data.get('data', []))
                    logger.debug(f"✅ Foundry онлайн: {self.base_url} ({models_count} моделей)")
                    return {
                        "status": "healthy",
                        "models_count": models_count,
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
                from urllib.parse import urlparse
                parsed = urlparse(self.base_url) if self.base_url else None
                port = parsed.port if parsed and parsed.port else 50477
            except (ValueError, AttributeError, IndexError):
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
        """Генерация текста. Если модель не загружена — загружает её автоматически."""
        model = kwargs.get('model') or None
        
        try:
            health = await self.health_check()
            if health["status"] != "healthy":
                return {"success": False, "error": f"Foundry недоступен: {health.get('error')}"}
            
            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/chat/completions"

            # Если модель не указана — берём первую загруженную
            if not model:
                models_resp = await self.list_available_models()
                loaded = models_resp.get('models', [])
                if loaded:
                    model = loaded[0].get('id', '')
                    logger.info(f"🤖 Модель не указана, используем: {model}")
                else:
                    return {"success": False, "error": "Нет загруженных моделей в Foundry"}

            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get('temperature', 0.7),
                "max_tokens": kwargs.get('max_tokens', 2048),
                "stream": False
            }

            logger.info(f"🤖 Генерация: модель={model}")
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('choices'):
                        content = data['choices'][0]['message']['content']
                        usage = data.get('usage') or {}
                        return {"success": True, "content": content, "model": model, "usage": usage}
                    return {"success": False, "error": "Некорректный ответ от Foundry"}
                elif response.status == 400:
                    # Модель не загружена — пробуем загрузить и повторить
                    logger.warning(f"⚠️ HTTP 400 для модели {model} — пробуем загрузить")
                    import subprocess
                    proc = subprocess.Popen(
                        ["foundry", "model", "load", model],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )
                    # Ждём до 60 секунд пока модель загрузится
                    import asyncio
                    for _ in range(30):
                        await asyncio.sleep(2)
                        async with session.post(url, json=payload) as retry:
                            if retry.status == 200:
                                data = await retry.json()
                                if data.get('choices'):
                                    content = data['choices'][0]['message']['content']
                                    logger.info(f"✅ Модель {model} загружена и ответила")
                                    return {"success": True, "content": content, "model": model}
                    return {"success": False, "error": f"Модель {model} не отвечает после загрузки"}
                else:
                    error_text = await response.text()
                    logger.error(f"❌ HTTP {response.status}: {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            logger.error(f"❌ Исключение при генерации: {e}")
            return {"success": False, "error": f"Ошибка: {str(e)}"}

    async def generate_stream(self, prompt: str, **kwargs):
        """Генерация текста с потоковой передачей"""
        try:
            # Переменные решения о модели
            model = kwargs.get('model') or ""
            health = await self.health_check()
            if health["status"] != "healthy":
                yield {
                    "success": False,
                    "error": f"Foundry недоступен на порту {health.get('port', 50477)}",
                    "foundry_status": health["status"]
                }
                return
            
            # Выбор модели при отсутствии значения model (model=None, model="")
            if not model:
                models_resp = await self.list_available_models()
                loaded = models_resp.get('models', [])
                if loaded:
                    model = loaded[0].get('id', '')
                    logger.info(f"🤖 Модель не указана, используем: {model}")
                if not model:
                    yield {"success": False, "error": "Нет загруженных моделей в Foundry"}
                    return

            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/chat/completions"
            
            payload = {
                # Модель фиксируется после fallback-выбора
                "model": model,
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
        logger.debug("📋 Получение списка моделей...")
        
        try:
            await self._update_base_url()
            
            if not self.base_url:
                logger.error("❌ Foundry не найден")
                return {
                    "success": False,
                    "error": "Foundry недоступен",
                    "models": []
                }
            
            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/models"
            
            logger.debug(f"Запрос моделей: {url}")
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get('data', [])
                    logger.debug(f"✅ Получено {len(models)} моделей")
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
            await self._update_base_url()
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
            await self._update_base_url()
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