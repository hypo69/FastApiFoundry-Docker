# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Foundry SDK Client
# =============================================================================
# Описание:
#   Основной клиент для работы с FastAPI Foundry API
#
# File: client.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import json
import requests
from typing import Dict, List, Optional, Any
from .models import GenerationRequest, GenerationResponse, ModelInfo, HealthStatus
from .exceptions import FoundryError, FoundryConnectionError, FoundryAPIError

class FoundryClient:
    """Клиент для FastAPI Foundry API"""
    
    def __init__(self, base_url: str = "http://localhost:9696", api_key: Optional[str] = None):
        """
        Инициализация клиента
        
        Args:
            base_url: Базовый URL API сервера
            api_key: API ключ для аутентификации
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Выполнить HTTP запрос"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError as e:
            raise FoundryConnectionError(f"Не удалось подключиться к {url}: {e}")
        except requests.HTTPError as e:
            raise FoundryAPIError(f"HTTP ошибка {response.status_code}: {response.text}")
        except Exception as e:
            raise FoundryError(f"Неожиданная ошибка: {e}")
    
    def health(self) -> HealthStatus:
        """Проверить здоровье системы"""
        data = self._make_request("GET", "/api/v1/health")
        return HealthStatus(**data)
    
    def list_models(self) -> List[ModelInfo]:
        """Получить список доступных моделей"""
        data = self._make_request("GET", "/api/v1/models")
        if data.get("success"):
            return [ModelInfo(**model) for model in data.get("models", [])]
        return []
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_rag: bool = True,
        system_prompt: Optional[str] = None
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
            json=request_data.dict(exclude_none=True)
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
            json=request_data
        )
        
        if data.get("success"):
            return [GenerationResponse(**result) for result in data.get("results", [])]
        return []
    
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
    
    def get_config(self) -> Dict[str, Any]:
        """Получить конфигурацию системы"""
        data = self._make_request("GET", "/api/v1/config")
        if data.get("success"):
            return data.get("config", {})
        return {}
    
    def close(self):
        """Закрыть сессию"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()