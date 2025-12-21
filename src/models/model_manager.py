# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Model Manager for FastAPI Foundry
# =============================================================================
# Описание:
#   Менеджер для управления подключением и конфигурацией AI моделей
#   Поддерживает различные провайдеры: Foundry, Ollama, OpenAI, Anthropic
#
# File: model_manager.py
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
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from config import settings
from ..utils.logging_system import get_logger

# Создать логгер для менеджера моделей
logger = get_logger("model-manager")

class ModelManager:
    """Менеджер для управления подключенными AI моделями"""
    
    def __init__(self):
        self.connected_models: Dict[str, Dict[str, Any]] = {}
        self.providers_config = {
            "foundry": {
                "name": "Foundry AI",
                "description": "Локальный AI сервер Foundry",
                "supported_features": ["text_generation", "chat", "embeddings"],
                "requires_api_key": False,
                "default_endpoint": settings.foundry_base_url,
                "documentation_url": "https://github.com/foundryai/foundry"
            },
            "ollama": {
                "name": "Ollama",
                "description": "Локальный AI сервер Ollama",
                "supported_features": ["text_generation", "chat", "embeddings"],
                "requires_api_key": False,
                "default_endpoint": "http://localhost:11434/api/",
                "documentation_url": "https://ollama.ai/docs"
            },
            "openai": {
                "name": "OpenAI",
                "description": "OpenAI API (GPT-4, GPT-3.5, etc.)",
                "supported_features": ["text_generation", "chat", "embeddings", "function_calling"],
                "requires_api_key": True,
                "default_endpoint": "https://api.openai.com/v1/",
                "documentation_url": "https://platform.openai.com/docs"
            },
            "anthropic": {
                "name": "Anthropic",
                "description": "Anthropic Claude API",
                "supported_features": ["text_generation", "chat"],
                "requires_api_key": True,
                "default_endpoint": "https://api.anthropic.com/v1/",
                "documentation_url": "https://docs.anthropic.com"
            },
            "custom": {
                "name": "Custom Provider",
                "description": "Кастомный провайдер с настраиваемым endpoint",
                "supported_features": ["text_generation"],
                "requires_api_key": False,
                "default_endpoint": None,
                "documentation_url": None
            }
        }
        self.config_file = Path("models_config.json")
        self.load_config()
    
    def load_config(self):
        """Загрузить конфигурацию моделей из файла"""
        logger.debug("Загрузка конфигурации моделей", config_file=str(self.config_file))
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.connected_models = data.get('connected_models', {})
                logger.info("Конфигурация моделей загружена", 
                           models_count=len(self.connected_models),
                           models=list(self.connected_models.keys()))
            except Exception as e:
                logger.exception("Критическая ошибка загрузки конфигурации", 
                               config_file=str(self.config_file), error=str(e))
                self.connected_models = {}
        else:
            logger.info("Конфигурация не найдена, создание модели по умолчанию")
            # Добавляем Foundry модель по умолчанию
            self.add_default_foundry_model()
    
    def save_config(self):
        """Сохранить конфигурацию моделей в файл"""
        try:
            config_data = {
                'connected_models': self.connected_models,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False, default=str)
            logger.info("Конфигурация моделей сохранена")
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")
    
    def add_default_foundry_model(self):
        """Добавить модель Foundry по умолчанию"""
        default_model = {
            "model_id": settings.foundry_default_model,
            "model_name": "Foundry Default Model",
            "provider": "foundry",
            "endpoint_url": settings.foundry_base_url,
            "api_key": None,
            "parameters": {
                "temperature": settings.foundry_temperature,
                "max_tokens": settings.foundry_max_tokens,
                "top_p": settings.foundry_top_p,
                "top_k": settings.foundry_top_k
            },
            "default_temperature": settings.foundry_temperature,
            "default_max_tokens": settings.foundry_max_tokens,
            "enabled": True,
            "status": "unknown",
            "last_check": datetime.now(),
            "usage_count": 0,
            "avg_response_time": None,
            "created_at": datetime.now()
        }
        self.connected_models[settings.foundry_default_model] = default_model
        self.save_config()
    
    async def connect_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Подключить новую модель"""
        model_id = model_data["model_id"]
        logger.info("Попытка подключения модели", 
                   model_id=model_id, 
                   provider=model_data.get("provider", "unknown"))
        
        try:
            # Проверяем, не подключена ли уже модель
            if model_id in self.connected_models:
                logger.warning("Модель уже подключена", model_id=model_id)
                return {
                    "success": False,
                    "model_id": model_id,
                    "message": f"Модель {model_id} уже подключена",
                    "error": "Model already connected"
                }
            
            # Создаем конфигурацию модели
            model_config = {
                "model_id": model_id,
                "model_name": model_data.get("model_name", model_id),
                "provider": model_data["provider"],
                "endpoint_url": model_data.get("endpoint_url") or self.providers_config[model_data["provider"]]["default_endpoint"],
                "api_key": model_data.get("api_key"),
                "parameters": model_data.get("parameters", {}),
                "default_temperature": model_data.get("default_temperature", 0.7),
                "default_max_tokens": model_data.get("default_max_tokens", 2048),
                "enabled": model_data.get("enabled", True),
                "status": "unknown",
                "last_check": datetime.now(),
                "usage_count": 0,
                "avg_response_time": None,
                "created_at": datetime.now()
            }
            
            logger.debug("Конфигурация модели создана", 
                        model_id=model_id, 
                        endpoint=model_config["endpoint_url"])
            
            # Тестируем подключение к модели
            with logger.timer("model_connection_test", model_id=model_id):
                test_result = await self.test_model_connection(model_config)
                model_config["status"] = "online" if test_result["success"] else "offline"
            
            # Сохраняем модель
            self.connected_models[model_id] = model_config
            self.save_config()
            
            logger.info("Модель успешно подключена", 
                       model_id=model_id, 
                       status=model_config["status"],
                       response_time=test_result.get("response_time"))
            
            return {
                "success": True,
                "model_id": model_id,
                "message": f"Модель {model_id} успешно подключена",
                "status": model_config["status"]
            }
            
        except Exception as e:
            logger.exception("Критическая ошибка подключения модели", 
                           model_id=model_id, error=str(e))
            return {
                "success": False,
                "model_id": model_id,
                "message": "Ошибка подключения модели",
                "error": str(e)
            }
    
    async def disconnect_model(self, model_id: str) -> Dict[str, Any]:
        """Отключить модель"""
        if model_id not in self.connected_models:
            return {
                "success": False,
                "model_id": model_id,
                "message": f"Модель {model_id} не найдена",
                "error": "Model not found"
            }
        
        try:
            del self.connected_models[model_id]
            self.save_config()
            
            return {
                "success": True,
                "model_id": model_id,
                "message": f"Модель {model_id} отключена"
            }
            
        except Exception as e:
            logger.error(f"Ошибка отключения модели {model_id}: {e}")
            return {
                "success": False,
                "model_id": model_id,
                "message": "Ошибка отключения модели",
                "error": str(e)
            }
    
    async def update_model(self, model_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновить настройки модели"""
        if model_id not in self.connected_models:
            return {
                "success": False,
                "model_id": model_id,
                "message": f"Модель {model_id} не найдена",
                "error": "Model not found"
            }
        
        try:
            model_config = self.connected_models[model_id]
            
            # Обновляем поля
            if "model_name" in update_data:
                model_config["model_name"] = update_data["model_name"]
            if "enabled" in update_data:
                model_config["enabled"] = update_data["enabled"]
            if "default_temperature" in update_data:
                model_config["default_temperature"] = update_data["default_temperature"]
            if "default_max_tokens" in update_data:
                model_config["default_max_tokens"] = update_data["default_max_tokens"]
            if "parameters" in update_data:
                model_config["parameters"].update(update_data["parameters"])
            if "api_key" in update_data:
                model_config["api_key"] = update_data["api_key"]
            
            model_config["updated_at"] = datetime.now()
            
            # Тестируем подключение после обновления
            if model_config["enabled"]:
                test_result = await self.test_model_connection(model_config)
                model_config["status"] = "online" if test_result["success"] else "offline"
            else:
                model_config["status"] = "disabled"
            
            self.save_config()
            
            return {
                "success": True,
                "model_id": model_id,
                "message": f"Модель {model_id} обновлена",
                "status": model_config["status"]
            }
            
        except Exception as e:
            logger.error(f"Ошибка обновления модели {model_id}: {e}")
            return {
                "success": False,
                "model_id": model_id,
                "message": "Ошибка обновления модели",
                "error": str(e)
            }
    
    async def test_model_connection(self, model_config: Dict[str, Any], test_prompt: str = "Hello") -> Dict[str, Any]:
        """Тестировать подключение к модели"""
        start_time = time.time()
        
        try:
            provider = model_config["provider"]
            
            if provider == "foundry":
                result = await self._test_foundry_model(model_config, test_prompt)
            elif provider == "ollama":
                result = await self._test_ollama_model(model_config, test_prompt)
            elif provider == "openai":
                result = await self._test_openai_model(model_config, test_prompt)
            elif provider == "anthropic":
                result = await self._test_anthropic_model(model_config, test_prompt)
            else:
                result = await self._test_custom_model(model_config, test_prompt)
            
            response_time = time.time() - start_time
            
            if result["success"]:
                # Обновляем статистику
                model_config["last_check"] = datetime.now()
                if model_config["avg_response_time"] is None:
                    model_config["avg_response_time"] = response_time
                else:
                    model_config["avg_response_time"] = (model_config["avg_response_time"] + response_time) / 2
            
            result["response_time"] = response_time
            return result
            
        except Exception as e:
            logger.error(f"Ошибка тестирования модели {model_config['model_id']}: {e}")
            return {
                "success": False,
                "model_id": model_config["model_id"],
                "error": str(e),
                "response_time": time.time() - start_time
            }
    
    async def _test_foundry_model(self, model_config: Dict[str, Any], test_prompt: str) -> Dict[str, Any]:
        """Тестировать Foundry модель"""
        # Используем актуальный endpoint URL из конфигурации, даже если в модели устаревший
        endpoint_url = model_config.get('endpoint_url') or settings.foundry_base_url
        # Если endpoint использует старый порт 5272, замен на текущий от settings
        if endpoint_url.endswith(':5272/v1/') or ':5272' in endpoint_url:
            endpoint_url = settings.foundry_base_url
            logger.info(f"Обновлен endpoint для модели {model_config['model_id']}: {endpoint_url}")

        async with aiohttp.ClientSession() as session:
            url = f"{endpoint_url.rstrip('/')}/chat/completions"
            
            payload = {
                "model": model_config["model_id"],
                "messages": [{"role": "user", "content": test_prompt}],
                "max_tokens": 50,
                "temperature": 0.7
            }
            
            async with session.post(url, json=payload, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "model_id": model_config["model_id"],
                        "response_text": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                        "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                    }
                else:
                    return {
                        "success": False,
                        "model_id": model_config["model_id"],
                        "error": f"HTTP {response.status}: {await response.text()}"
                    }
    
    async def _test_ollama_model(self, model_config: Dict[str, Any], test_prompt: str) -> Dict[str, Any]:
        """Тестировать Ollama модель"""
        async with aiohttp.ClientSession() as session:
            url = f"{model_config['endpoint_url'].rstrip('/')}/generate"
            
            payload = {
                "model": model_config["model_id"],
                "prompt": test_prompt,
                "stream": False
            }
            
            async with session.post(url, json=payload, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "model_id": model_config["model_id"],
                        "response_text": data.get("response", ""),
                        "tokens_used": None
                    }
                else:
                    return {
                        "success": False,
                        "model_id": model_config["model_id"],
                        "error": f"HTTP {response.status}: {await response.text()}"
                    }
    
    async def _test_openai_model(self, model_config: Dict[str, Any], test_prompt: str) -> Dict[str, Any]:
        """Тестировать OpenAI модель"""
        if not model_config.get("api_key"):
            return {
                "success": False,
                "model_id": model_config["model_id"],
                "error": "API key required for OpenAI"
            }
        
        async with aiohttp.ClientSession() as session:
            url = f"{model_config['endpoint_url'].rstrip('/')}/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {model_config['api_key']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model_config["model_id"],
                "messages": [{"role": "user", "content": test_prompt}],
                "max_tokens": 50,
                "temperature": 0.7
            }
            
            async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "model_id": model_config["model_id"],
                        "response_text": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                        "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                    }
                else:
                    return {
                        "success": False,
                        "model_id": model_config["model_id"],
                        "error": f"HTTP {response.status}: {await response.text()}"
                    }
    
    async def _test_anthropic_model(self, model_config: Dict[str, Any], test_prompt: str) -> Dict[str, Any]:
        """Тестировать Anthropic модель"""
        if not model_config.get("api_key"):
            return {
                "success": False,
                "model_id": model_config["model_id"],
                "error": "API key required for Anthropic"
            }
        
        async with aiohttp.ClientSession() as session:
            url = f"{model_config['endpoint_url'].rstrip('/')}/messages"
            
            headers = {
                "x-api-key": model_config['api_key'],
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": model_config["model_id"],
                "max_tokens": 50,
                "messages": [{"role": "user", "content": test_prompt}]
            }
            
            async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "model_id": model_config["model_id"],
                        "response_text": data.get("content", [{}])[0].get("text", ""),
                        "tokens_used": data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)
                    }
                else:
                    return {
                        "success": False,
                        "model_id": model_config["model_id"],
                        "error": f"HTTP {response.status}: {await response.text()}"
                    }
    
    async def _test_custom_model(self, model_config: Dict[str, Any], test_prompt: str) -> Dict[str, Any]:
        """Тестировать кастомную модель"""
        async with aiohttp.ClientSession() as session:
            url = model_config["endpoint_url"]
            
            headers = {"Content-Type": "application/json"}
            if model_config.get("api_key"):
                headers["Authorization"] = f"Bearer {model_config['api_key']}"
            
            payload = {
                "model": model_config["model_id"],
                "prompt": test_prompt,
                "max_tokens": 50
            }
            
            async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "model_id": model_config["model_id"],
                        "response_text": str(data),
                        "tokens_used": None
                    }
                else:
                    return {
                        "success": False,
                        "model_id": model_config["model_id"],
                        "error": f"HTTP {response.status}: {await response.text()}"
                    }
    
    async def check_all_models_health(self):
        """Проверить здоровье всех подключенных моделей"""
        for model_id, model_config in self.connected_models.items():
            if model_config["enabled"]:
                test_result = await self.test_model_connection(model_config, "ping")
                model_config["status"] = "online" if test_result["success"] else "offline"
                model_config["last_check"] = datetime.now()
        
        self.save_config()
    
    def get_connected_models(self) -> Dict[str, Any]:
        """Получить список подключенных моделей"""
        models_list = []
        online_count = 0
        
        for model_id, config in self.connected_models.items():
            model_info = {
                "model_id": model_id,
                "model_name": config["model_name"],
                "provider": config["provider"],
                "endpoint_url": config.get("endpoint_url"),
                "enabled": config["enabled"],
                "status": config["status"],
                "last_check": config["last_check"],
                "parameters": config.get("parameters", {}),
                "usage_count": config.get("usage_count", 0),
                "avg_response_time": config.get("avg_response_time")
            }
            models_list.append(model_info)
            
            if config["status"] == "online" and config["enabled"]:
                online_count += 1
        
        return {
            "success": True,
            "models": models_list,
            "total_count": len(models_list),
            "online_count": online_count,
            "default_model": settings.foundry_default_model,
            "timestamp": datetime.now()
        }
    
    def get_providers(self) -> Dict[str, Any]:
        """Получить список доступных провайдеров"""
        providers_list = []
        
        for provider_id, config in self.providers_config.items():
            provider_info = {
                "provider_id": provider_id,
                "name": config["name"],
                "description": config["description"],
                "supported_features": config["supported_features"],
                "requires_api_key": config["requires_api_key"],
                "default_endpoint": config["default_endpoint"],
                "documentation_url": config["documentation_url"]
            }
            providers_list.append(provider_info)
        
        return {
            "success": True,
            "providers": providers_list,
            "timestamp": datetime.now()
        }
    
    def get_model_config(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Получить конфигурацию модели"""
        return self.connected_models.get(model_id)
    
    def increment_usage(self, model_id: str, response_time: float = None):
        """Увеличить счетчик использования модели"""
        if model_id in self.connected_models:
            self.connected_models[model_id]["usage_count"] += 1
            
            if response_time and self.connected_models[model_id]["avg_response_time"]:
                current_avg = self.connected_models[model_id]["avg_response_time"]
                self.connected_models[model_id]["avg_response_time"] = (current_avg + response_time) / 2
            elif response_time:
                self.connected_models[model_id]["avg_response_time"] = response_time

# Глобальный экземпляр менеджера моделей
model_manager = ModelManager()