# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Foundry SDK Client (Enhanced)
# =============================================================================
# Описание:
#   Расширенный клиент для работы с FastAPI Foundry API
#   Включает управление моделями, RAG, конфигурацией и мониторингом
#
# File: client.py
# Project: FastApiFoundry (Docker)
# Version: 0.3.4
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import json
import requests
import time
from typing import Dict, List, Optional, Any, Union
from .models import GenerationRequest, GenerationResponse, ModelInfo, HealthStatus
from .exceptions import FoundryError, FoundryConnectionError, FoundryAPIError

class FoundryClient:
    """Расширенный клиент для FastAPI Foundry API"""
    
    def __init__(self, base_url: str = "http://localhost:9696", api_key: Optional[str] = None, timeout: int = 30):
        """
        Инициализация клиента
        
        Args:
            base_url: Базовый URL API сервера
            api_key: API ключ для аутентификации
            timeout: Таймаут запросов в секундах
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.timeout = timeout
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Выполнить HTTP запрос с улучшенной обработкой ошибок"""
        url = f"{self.base_url}{endpoint}"
        
        # Устанавливаем таймаут если не указан
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError as e:
            raise FoundryConnectionError(f"Не удалось подключиться к {url}: {e}")
        except requests.Timeout as e:
            raise FoundryConnectionError(f"Таймаут запроса к {url}: {e}")
        except requests.HTTPError as e:
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', response.text)
            except:
                error_msg = response.text
            raise FoundryAPIError(f"HTTP ошибка {response.status_code}: {error_msg}")
        except Exception as e:
            raise FoundryError(f"Неожиданная ошибка: {e}")
    
    # === ОСНОВНЫЕ ФУНКЦИИ ===
    
    def health(self) -> HealthStatus:
        """Проверить здоровье системы"""
        data = self._make_request("GET", "/api/v1/health")
        return HealthStatus(**data)
    
    def is_alive(self) -> bool:
        """Быстрая проверка доступности API"""
        try:
            health = self.health()
            return health.is_healthy
        except:
            return False
    
    def wait_for_ready(self, max_wait: int = 60) -> bool:
        """Ждать пока API станет доступным"""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if self.is_alive():
                return True
            time.sleep(2)
        return False
    
    # === МОДЕЛИ ===
    
    def list_models(self) -> List[ModelInfo]:
        """Получить список доступных моделей"""
        data = self._make_request("GET", "/api/v1/models")
        if data.get("success"):
            return [ModelInfo(**model) for model in data.get("models", [])]
        return []
    
    def get_connected_models(self) -> List[ModelInfo]:
        """Получить список подключенных моделей"""
        data = self._make_request("GET", "/api/v1/models/connected")
        if data.get("success"):
            return [ModelInfo(**model) for model in data.get("models", [])]
        return []
    
    def load_model(self, model_id: str) -> bool:
        """Загрузить модель в Foundry"""
        data = self._make_request(
            "POST", 
            "/api/v1/foundry/models/load",
            json={"model_id": model_id}
        )
        return data.get("success", False)
    
    def unload_model(self, model_id: str) -> bool:
        """Выгрузить модель из Foundry"""
        data = self._make_request(
            "POST", 
            "/api/v1/foundry/models/unload",
            json={"model_id": model_id}
        )
        return data.get("success", False)
    
    def get_model_status(self, model_id: str) -> Dict[str, Any]:
        """Получить статус конкретной модели"""
        data = self._make_request("GET", f"/api/v1/foundry/models/status/{model_id}")
        return data if data.get("success") else {}
    
    # === ГЕНЕРАЦИЯ ===
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_rag: bool = True,
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> GenerationResponse:
        """
        Генерировать текст
        
        Args:
            prompt: Входной промпт
            model: ID модели (опционально)
            temperature: Температура генерации (0.0-2.0)
            max_tokens: Максимальное количество токенов
            use_rag: Использовать RAG контекст
            system_prompt: Системный промпт
            stream: Потоковая генерация (пока не поддерживается)
            
        Returns:
            Результат генерации
        """
        request_data = GenerationRequest(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            use_rag=use_rag,
            system_prompt=system_prompt
        )
        
        data = self._make_request(
            "POST", 
            "/api/v1/generate",
            json=request_data.dict(exclude_none=True),
            timeout=120  # Увеличенный таймаут для генерации
        )
        
        return GenerationResponse(**data)
    
    def chat(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        model: Optional[str] = None,
        use_rag: bool = True
    ) -> GenerationResponse:
        """Отправить сообщение в чат"""
        request_data = {
            "message": message,
            "use_rag": use_rag
        }
        
        if conversation_id:
            request_data["conversation_id"] = conversation_id
        if model:
            request_data["model"] = model
        
        data = self._make_request(
            "POST",
            "/api/v1/chat",
            json=request_data,
            timeout=120
        )
        
        return GenerationResponse(**data)
    
    def batch_generate(
        self,
        prompts: List[str],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_rag: bool = True
    ) -> List[GenerationResponse]:
        """Пакетная генерация текста"""
        request_data = {
            "prompts": prompts,
            "use_rag": use_rag
        }
        
        if model:
            request_data["model"] = model
        if temperature is not None:
            request_data["temperature"] = temperature
        if max_tokens:
            request_data["max_tokens"] = max_tokens
        
        data = self._make_request(
            "POST",
            "/api/v1/batch-generate", 
            json=request_data,
            timeout=300  # Увеличенный таймаут для пакетной обработки
        )
        
        if data.get("success"):
            return [GenerationResponse(**result) for result in data.get("results", [])]
        return []
    
    # === RAG СИСТЕМА ===
    
    def rag_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Поиск в RAG индексе"""
        data = self._make_request(
            "POST",
            "/api/v1/rag/search",
            json={"query": query, "top_k": top_k}
        )
        
        if data.get("success"):
            return data.get("results", [])
        return []
    
    def rag_status(self) -> Dict[str, Any]:
        """Получить статус RAG системы"""
        data = self._make_request("GET", "/api/v1/rag/status")
        return data.get("status", {}) if data.get("success") else {}
    
    def rag_clear(self) -> bool:
        """Очистить RAG индекс"""
        data = self._make_request("POST", "/api/v1/rag/clear")
        return data.get("success", False)
    
    def rag_reload(self) -> bool:
        """Перезагрузить RAG индекс"""
        data = self._make_request("POST", "/api/v1/rag/reload")
        return data.get("success", False)
    
    def rag_initialize(self) -> bool:
        """Инициализировать RAG систему"""
        data = self._make_request("GET", "/api/v1/rag/initialize")
        return data.get("success", False)
    
    # === КОНФИГУРАЦИЯ ===
    
    def get_config(self) -> Dict[str, Any]:
        """Получить конфигурацию системы"""
        data = self._make_request("GET", "/api/v1/config")
        if data.get("success"):
            return data.get("config", {})
        return {}
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """Обновить конфигурацию системы"""
        data = self._make_request(
            "POST", 
            "/api/v1/config",
            json={"config": config}
        )
        return data.get("success", False)
    
    def set_default_model(self, model_id: str) -> bool:
        """Установить модель по умолчанию"""
        config = self.get_config()
        if not config:
            return False
        
        config.setdefault("foundry_ai", {})["default_model"] = model_id
        return self.update_config(config)
    
    # === FOUNDRY УПРАВЛЕНИЕ ===
    
    def foundry_status(self) -> Dict[str, Any]:
        """Получить статус Foundry сервиса"""
        data = self._make_request("GET", "/api/v1/foundry/status")
        return data if data.get("success") else {}
    
    def foundry_models_loaded(self) -> List[Dict[str, Any]]:
        """Получить список загруженных моделей в Foundry"""
        data = self._make_request("GET", "/api/v1/foundry/models/loaded")
        if data.get("success"):
            return data.get("models", [])
        return []
    
    # === МОНИТОРИНГ И ЛОГИ ===
    
    def get_logs(self, level: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Получить системные логи"""
        params = {"limit": limit}
        if level:
            params["level"] = level
        
        data = self._make_request("GET", "/logs/recent", params=params)
        if data.get("success"):
            return data.get("data", {}).get("logs", [])
        return []
    
    def get_metrics(self) -> Dict[str, Any]:
        """Получить метрики производительности"""
        try:
            logs = self.get_logs(limit=1000)
            
            # Подсчет статистики
            stats = {
                "total_logs": len(logs),
                "errors": len([l for l in logs if l.get("level") == "error"]),
                "warnings": len([l for l in logs if l.get("level") == "warning"]),
                "info": len([l for l in logs if l.get("level") == "info"]),
                "debug": len([l for l in logs if l.get("level") == "debug"])
            }
            
            return stats
        except:
            return {}
    
    # === УТИЛИТЫ ===
    
    def test_connection(self) -> Dict[str, Any]:
        """Тестировать подключение к API"""
        try:
            start_time = time.time()
            health = self.health()
            response_time = time.time() - start_time
            
            return {
                "connected": True,
                "response_time": response_time,
                "api_status": health.status,
                "foundry_status": health.foundry_status,
                "models_available": health.models_count > 0
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
    
    def auto_setup(self) -> Dict[str, Any]:
        """Автоматическая настройка системы"""
        results = {
            "health_check": False,
            "models_loaded": False,
            "rag_initialized": False,
            "errors": []
        }
        
        try:
            # Проверка здоровья
            health = self.health()
            results["health_check"] = health.is_healthy
            
            # Проверка моделей
            models = self.list_models()
            results["models_loaded"] = len(models) > 0
            
            # Инициализация RAG если нужно
            rag_status = self.rag_status()
            if not rag_status.get("loaded", False):
                if self.rag_initialize():
                    results["rag_initialized"] = True
                else:
                    results["errors"].append("Failed to initialize RAG")
            else:
                results["rag_initialized"] = True
                
        except Exception as e:
            results["errors"].append(str(e))
        
        return results
    
    def quick_test(self, prompt: str = "Hello, how are you?") -> Dict[str, Any]:
        """Быстрый тест всех основных функций"""
        results = {
            "connection": False,
            "generation": False,
            "rag_search": False,
            "models": 0,
            "errors": []
        }
        
        try:
            # Тест подключения
            connection = self.test_connection()
            results["connection"] = connection["connected"]
            
            if not results["connection"]:
                results["errors"].append(connection.get("error", "Connection failed"))
                return results
            
            # Тест моделей
            models = self.list_models()
            results["models"] = len(models)
            
            # Тест генерации (только если есть модели)
            if models:
                try:
                    response = self.generate(prompt, max_tokens=50, use_rag=False)
                    results["generation"] = response.success
                    if not response.success:
                        results["errors"].append(f"Generation failed: {response.error}")
                except Exception as e:
                    results["errors"].append(f"Generation error: {e}")
            
            # Тест RAG поиска
            try:
                rag_results = self.rag_search("test query", top_k=1)
                results["rag_search"] = len(rag_results) >= 0  # Даже пустой результат - успех
            except Exception as e:
                results["errors"].append(f"RAG search error: {e}")
                
        except Exception as e:
            results["errors"].append(f"Quick test error: {e}")
        
        return results
    
    # === РАСШИРЕННЫЕ ФУНКЦИИ ===
    
    def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        **kwargs
    ) -> GenerationResponse:
        """Генерация с повторными попытками"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return self.generate(prompt, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Экспоненциальная задержка
        
        # Если все попытки неудачны
        return GenerationResponse(
            success=False,
            error=f"Failed after {max_retries} attempts: {last_error}"
        )
    
    def smart_generate(
        self,
        prompt: str,
        prefer_rag: bool = True,
        fallback_model: Optional[str] = None,
        **kwargs
    ) -> GenerationResponse:
        """Умная генерация с автоматическим выбором параметров"""
        # Попробуем с RAG
        if prefer_rag:
            try:
                response = self.generate(prompt, use_rag=True, **kwargs)
                if response.success:
                    return response
            except:
                pass
        
        # Попробуем без RAG
        try:
            response = self.generate(prompt, use_rag=False, **kwargs)
            if response.success:
                return response
        except:
            pass
        
        # Попробуем с fallback моделью
        if fallback_model:
            try:
                return self.generate(prompt, model=fallback_model, use_rag=False, **kwargs)
            except:
                pass
        
        return GenerationResponse(
            success=False,
            error="All generation attempts failed"
        )
    
    def close(self):
        """Закрыть сессию"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()