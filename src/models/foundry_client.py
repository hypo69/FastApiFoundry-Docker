# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Foundry Client
# =============================================================================
# Description:
#   Async HTTP client for Foundry Local API.
#   Foundry loads models on-demand (not at service start).
#   .foundry/cache/models is disk storage only — RAM is used per-request.
#
# File: foundry_client.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.1
# Changes in 0.6.1:
#   - Removed inline subprocess model-load retry from generate_text (wrong layer)
#   - generate_text now returns clear error on HTTP 400 (model not loaded)
#   - Added max_loaded_models / ttl_seconds awareness via config model_manager section
# Author: hypo69
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
        """Получить HTTP сессию.

        Returns:
            aiohttp.ClientSession: Active HTTP session.
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def close(self):
        """Закрыть HTTP сессию.

        Returns:
            None
        """
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _find_foundry_port(self) -> int | None:
        """Find running Foundry port via `foundry service status` output.

        Returns:
            int | None: Port number if Foundry responds with HTTP 200, None otherwise.
        """
        import subprocess as _sp
        import re as _re
        try:
            result = _sp.run(['foundry', 'service', 'status'],
                             capture_output=True, text=True, timeout=10,
                             encoding='utf-8', errors='replace')
            output = (result.stdout or '') + (result.stderr or '')
            match = _re.search(r'http://127\.0\.0\.1:(\d+)', output)
            if match:
                port = int(match.group(1))
                session = await self._get_session()
                try:
                    async with session.get(f'http://127.0.0.1:{port}/v1/models',
                                           timeout=aiohttp.ClientTimeout(total=2)) as r:
                        if r.status == 200:
                            logger.info(f'✅ Foundry found via status on port {port}')
                            return port
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f'foundry service status failed: {e}')

        # Fallback: scan known ports
        known = [52632, 62171, 50477, 58130]
        session = await self._get_session()
        for port in known:
            try:
                async with session.get(f'http://127.0.0.1:{port}/v1/models',
                                       timeout=aiohttp.ClientTimeout(total=2)) as r:
                    if r.status == 200:
                        logger.info(f'✅ Foundry found on known port {port}')
                        return port
            except Exception:
                continue
        return None
    
    async def _update_base_url(self):
        """Обновить base_url из переменной окружения или Config.

        Priority: FOUNDRY_DYNAMIC_PORT env var → config.foundry_base_url → port scan.

        Returns:
            None
        """
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
        """Проверка состояния Foundry.

        Returns:
            dict: status (healthy/unhealthy/disconnected), url, port, timestamp,
                  models_count (on healthy), error (on failure).
        """
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
        """Generate text via Foundry chat/completions endpoint.

        Foundry loads models on-demand: the model must already be loaded
        via `foundry model load` before calling this method.
        HTTP 400 means the model is not loaded — caller should load it first.

        Args:
            prompt: User input text.
            **kwargs: model (str), temperature (float), max_tokens (int).

        Returns:
            dict: success, content, model, usage on success;
                  success=False, error on failure.
                  error='model_not_loaded' when HTTP 400 received.
        """
        model = kwargs.get('model') or None

        try:
            health = await self.health_check()
            if health["status"] != "healthy":
                return {"success": False, "error": f"Foundry недоступен: {health.get('error')}"}

            session = await self._get_session()
            url = f"{self.base_url.rstrip('/')}/chat/completions"

            # Use first loaded model when none specified
            if not model:
                models_resp = await self.list_available_models()
                loaded = models_resp.get('models', [])
                if loaded:
                    model = loaded[0].get('id', '')
                    logger.info(f"🤖 Модель не указана, используем: {model}")
                else:
                    return {"success": False, "error": "Нет загруженных моделей в Foundry. Загрузите модель через вкладку Foundry."}

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
                    # Model is not loaded in Foundry service.
                    # Foundry does NOT auto-load from cache on inference request.
                    # The caller must explicitly load the model first.
                    logger.warning(f"⚠️ HTTP 400: модель {model} не загружена в Foundry сервис")
                    return {
                        "success": False,
                        "error": f"Модель {model} не загружена. Загрузите её через вкладку Foundry → Downloaded Models → Load & Use.",
                        "error_code": "model_not_loaded",
                        "model_id": model,
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ HTTP {response.status}: {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            logger.error(f"❌ Исключение при генерации: {e}")
            return {"success": False, "error": f"Ошибка: {str(e)}"}

    async def generate_stream(self, prompt: str, **kwargs):
        """Генерация текста с потоковой передачей.

        Args:
            prompt: User input text.
            **kwargs: model (str), temperature (float), max_tokens (int).

        Yields:
            dict: success, content, finished on each token chunk;
                  success=False, error on failure.
        """
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
        """Получить список доступных моделей.

        Returns:
            dict: success, models (list of model dicts), count on success;
                  success=False, error, models=[] on failure.
        """
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
        """Загрузить модель.

        Args:
            model_id: Foundry model identifier, e.g. 'qwen3-0.6b-generic-cpu:4'.

        Returns:
            dict: success, message on success; success=False, error on failure.
        """
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
        """Выгрузить модель.

        Args:
            model_id: Foundry model identifier.

        Returns:
            dict: success, message on success; success=False, error on failure.
        """
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
        """Получить список моделей (alias for list_available_models).

        Returns:
            dict: Same as list_available_models().
        """
        return await self.list_available_models()

# Глобальный экземпляр клиента
foundry_client = FoundryClient()