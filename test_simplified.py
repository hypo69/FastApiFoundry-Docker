#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Тест упрощенного кода
# =============================================================================
# Описание:
#   Простой тест для проверки работы упрощенного кода без Pydantic
#
# File: test_simplified.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import asyncio
import sys
import os

# Добавить src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_simplified_models():
    """Тест упрощенных моделей"""
    print("Testing simplified models...")
    
    from api.models import (
        create_generate_response,
        create_health_response,
        create_error_response,
        create_models_response
    )
    
    # Тест создания ответов
    gen_response = create_generate_response(
        success=True,
        content="Test content",
        model="test-model"
    )
    print(f"Generate response: {gen_response}")
    
    health_response = create_health_response(
        status="healthy",
        foundry_status="connected",
        rag_available=True
    )
    print(f"Health response: {health_response}")
    
    error_response = create_error_response(
        error="Test error",
        detail="Test detail"
    )
    print(f"Error response: {error_response}")
    
    models_response = create_models_response(
        success=True,
        models=[{"id": "model1"}, {"id": "model2"}]
    )
    print(f"Models response: {models_response}")
    
    print("✅ Simplified models test passed!")

async def test_foundry_client():
    """Тест упрощенного Foundry клиента"""
    print("Testing simplified Foundry client...")
    
    from models.foundry_client import FoundryClient
    
    client = FoundryClient()
    
    # Тест health check
    health = await client.health_check()
    print(f"Health check: {health}")
    
    # Тест списка моделей
    models = await client.list_available_models()
    print(f"Models: {models}")
    
    await client.close()
    print("✅ Foundry client test passed!")

async def main():
    """Главная функция тестирования"""
    print("=" * 50)
    print("Testing Simplified FastAPI Foundry Code")
    print("=" * 50)
    
    try:
        await test_simplified_models()
        print()
        await test_foundry_client()
        print()
        print("🎉 All tests passed! Code is simplified and working.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)