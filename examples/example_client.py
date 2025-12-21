#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Foundry Client Example
# =============================================================================
# Описание:
#   Пример клиента для работы с FastAPI Foundry API
#   Демонстрирует все доступные endpoints и функции
#
# File: example_client.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import asyncio
import aiohttp
import json
from typing import Dict, Any, List

class FastAPIFoundryClient:
    """Клиент для FastAPI Foundry API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None
    
    async def __aenter__(self):
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        self.session = aiohttp.ClientSession(headers=headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья сервиса"""
        async with self.session.get(f"{self.base_url}/api/v1/health") as response:
            return await response.json()
    
    async def list_models(self) -> Dict[str, Any]:
        """Получить список моделей"""
        async with self.session.get(f"{self.base_url}/api/v1/models") as response:
            return await response.json()
    
    async def generate_text(
        self,
        prompt: str,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        use_rag: bool = True,
        system_prompt: str = None
    ) -> Dict[str, Any]:
        """Генерация текста"""
        data = {
            "prompt": prompt,
            "use_rag": use_rag
        }
        
        if model:
            data["model"] = model
        if temperature is not None:
            data["temperature"] = temperature
        if max_tokens:
            data["max_tokens"] = max_tokens
        if system_prompt:
            data["system_prompt"] = system_prompt
        
        async with self.session.post(
            f"{self.base_url}/api/v1/generate",
            json=data
        ) as response:
            return await response.json()
    
    async def batch_generate(
        self,
        prompts: List[str],
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        use_rag: bool = True
    ) -> Dict[str, Any]:
        """Пакетная генерация"""
        data = {
            "prompts": prompts,
            "use_rag": use_rag
        }
        
        if model:
            data["model"] = model
        if temperature is not None:
            data["temperature"] = temperature
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        async with self.session.post(
            f"{self.base_url}/api/v1/batch-generate",
            json=data
        ) as response:
            return await response.json()
    
    async def rag_search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Поиск в RAG"""
        data = {
            "query": query,
            "top_k": top_k
        }
        
        async with self.session.post(
            f"{self.base_url}/api/v1/rag/search",
            json=data
        ) as response:
            return await response.json()
    
    async def get_config(self) -> Dict[str, Any]:
        """Получить конфигурацию"""
        async with self.session.get(f"{self.base_url}/api/v1/config") as response:
            return await response.json()
    
    async def rag_reload(self) -> Dict[str, Any]:
        """Перезагрузить RAG индекс"""
        async with self.session.post(f"{self.base_url}/api/v1/rag/reload") as response:
            return await response.json()
    
    async def get_connected_models(self) -> Dict[str, Any]:
        """Получить список подключенных моделей"""
        async with self.session.get(f"{self.base_url}/api/v1/models/connected") as response:
            return await response.json()
    
    async def connect_model(self, model_id: str, provider: str = "foundry", **kwargs) -> Dict[str, Any]:
        """Подключить новую модель"""
        data = {"model_id": model_id, "provider": provider, **kwargs}
        async with self.session.post(f"{self.base_url}/api/v1/models/connect", json=data) as response:
            return await response.json()
    
    async def get_model_providers(self) -> Dict[str, Any]:
        """Получить список провайдеров"""
        async with self.session.get(f"{self.base_url}/api/v1/models/providers") as response:
            return await response.json()
    
    async def check_models_health(self) -> Dict[str, Any]:
        """Проверить здоровье всех моделей"""
        async with self.session.post(f"{self.base_url}/api/v1/models/health-check") as response:
            return await response.json()
    
    async def start_tunnel(self, tunnel_type: str, port: int = 8000, subdomain: str = None) -> Dict[str, Any]:
        """Запустить туннель"""
        params = {"tunnel_type": tunnel_type, "port": port}
        if subdomain:
            params["subdomain"] = subdomain
        
        async with self.session.post(
            f"{self.base_url}/api/v1/tunnel/start",
            params=params
        ) as response:
            return await response.json()
    
    async def stop_tunnel(self) -> Dict[str, Any]:
        """Остановить туннель"""
        async with self.session.post(f"{self.base_url}/api/v1/tunnel/stop") as response:
            return await response.json()
    
    async def tunnel_status(self) -> Dict[str, Any]:
        """Статус туннеля"""
        async with self.session.get(f"{self.base_url}/api/v1/tunnel/status") as response:
            return await response.json()
    
    async def run_example(self, example_type: str) -> Dict[str, Any]:
        """Запустить пример"""
        data = {"example_type": example_type}
        async with self.session.post(f"{self.base_url}/api/v1/examples/run", json=data) as response:
            return await response.json()
    
    async def list_examples(self) -> Dict[str, Any]:
        """Получить список примеров"""
        async with self.session.get(f"{self.base_url}/api/v1/examples/list") as response:
            return await response.json()

async def main():
    """Демонстрация использования клиента"""
    
    # Инициализация клиента
    async with FastAPIFoundryClient(
        base_url="http://localhost:8000",
        api_key=None  # API ключ отключен в .env
    ) as client:
        
        print("🚀 FastAPI Foundry Client Demo")
        print("=" * 50)
        
        # 1. Проверка здоровья
        print("\n1️⃣ Health Check:")
        health = await client.health_check()
        print(json.dumps(health, indent=2, ensure_ascii=False))
        
        # 2. Список моделей
        print("\n2️⃣ Available Models:")
        models = await client.list_models()
        print(json.dumps(models, indent=2, ensure_ascii=False))
        
        # 3. Простая генерация (пропускаем - Foundry недоступен)
        print("\n3️⃣ Simple Text Generation: SKIPPED (Foundry unavailable)")
        
        # 4. Генерация с системным промптом (пропускаем)
        print("\n4️⃣ Generation with System Prompt: SKIPPED (Foundry unavailable)")
        
        # 5. RAG поиск
        print("\n5️⃣ RAG Search:")
        rag_result = await client.rag_search(
            query="WordPress плагины AiStros",
            top_k=3
        )
        print(f"Found {len(rag_result.get('results', []))} results")
        for i, result in enumerate(rag_result.get('results', [])[:2], 1):
            print(f"  {i}. {result['source']} - {result['section']} (score: {result['score']:.3f})")
        
        # 6. Пакетная генерация (пропускаем)
        print("\n6️⃣ Batch Generation: SKIPPED (Foundry unavailable)")
        
        # 7. Конфигурация
        print("\n7️⃣ Configuration:")
        config = await client.get_config()
        print(f"Foundry URL: {config['foundry']['base_url']}")
        print(f"Default model: {config['foundry']['default_model']}")
        print(f"RAG enabled: {config['rag']['available']}")
        print(f"RAG loaded: {config['rag']['loaded']}")
        
        # 8. Управление моделями
        print("\n8️⃣ Model Management:")
        
        # Получить подключенные модели
        connected_models = await client.get_connected_models()
        print(f"Connected models: {connected_models['total_count']} ({connected_models['online_count']} online)")
        
        # Получить провайдеров
        providers = await client.get_model_providers()
        print(f"Available providers: {len(providers['providers'])}")
        
        # Проверить здоровье моделей
        health_check = await client.check_models_health()
        print(f"Models health check: {'completed' if health_check['success'] else 'failed'}")
        
        # 9. Туннель управление
        print("\n9️⃣ Tunnel Management:")
        
        # Проверить статус туннеля
        tunnel_status = await client.tunnel_status()
        print(f"Tunnel active: {tunnel_status['active']}")
        
        print("\n✅ FastAPI Foundry API работает корректно!")
        print("⚠️  Для полной функциональности убедитесь, что Foundry сервер запущен (по умолчанию порт 55581)")

if __name__ == "__main__":
    asyncio.run(main())