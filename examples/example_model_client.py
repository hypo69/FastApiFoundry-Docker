#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Model Management Client Example
# =============================================================================
# Описание:
#   Пример клиента для управления подключением AI моделей
#   Демонстрирует подключение различных провайдеров
#
# File: example_model_client.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import asyncio
import json
from example_client import FastAPIFoundryClient

async def demo_model_management():
    """Демонстрация управления моделями"""
    
    async with FastAPIFoundryClient(
        base_url="http://localhost:8000",
        api_key=None  # API ключ отключен в .env
    ) as client:
        
        print("🤖 FastAPI Foundry - Model Management Demo")
        print("=" * 60)
        
        # 1. Получить список провайдеров
        print("\n1️⃣ Available Providers:")
        providers = await client.get_model_providers()
        
        for provider in providers['providers']:
            print(f"  📦 {provider['name']} ({provider['provider_id']})")
            print(f"     {provider['description']}")
            print(f"     Features: {', '.join(provider['supported_features'])}")
            print(f"     API Key required: {'Yes' if provider['requires_api_key'] else 'No'}")
            if provider['default_endpoint']:
                print(f"     Default endpoint: {provider['default_endpoint']}")
            print()
        
        # 2. Получить текущие подключенные модели
        print("\n2️⃣ Currently Connected Models:")
        connected = await client.get_connected_models()
        
        print(f"Total models: {connected['total_count']}")
        print(f"Online models: {connected['online_count']}")
        print(f"Default model: {connected.get('default_model', 'None')}")
        
        for model in connected['models']:
            status_emoji = "🟢" if model['status'] == 'online' else "🔴" if model['status'] == 'offline' else "⚪"
            print(f"  {status_emoji} {model['model_id']} ({model['provider']})")
            print(f"     Name: {model['model_name']}")
            print(f"     Status: {model['status']}")
            print(f"     Enabled: {model['enabled']}")
            print(f"     Usage: {model['usage_count']} times")
            if model['avg_response_time']:
                print(f"     Avg response: {model['avg_response_time']:.2f}s")
            print()
        
        # 3. Проверить здоровье моделей
        print("\n3️⃣ Health Check:")
        health_result = await client.check_models_health()
        print(f"Health check: {'✅ Completed' if health_result['success'] else '❌ Failed'}")
        
        # 4. Демонстрация подключения новых моделей
        print("\n4️⃣ Model Connection Examples:")
        
        # Пример подключения Ollama модели
        print("\n📝 Example: Connect Ollama Model")
        print("Command:")
        print("  await client.connect_model(")
        print("      model_id='llama2:7b',")
        print("      provider='ollama',")
        print("      model_name='Llama 2 7B',")
        print("      endpoint_url='http://localhost:11434/api/'")
        print("  )")
        
        # Пример подключения OpenAI модели
        print("\n📝 Example: Connect OpenAI Model")
        print("Command:")
        print("  await client.connect_model(")
        print("      model_id='gpt-3.5-turbo',")
        print("      provider='openai',")
        print("      model_name='GPT-3.5 Turbo',")
        print("      api_key='your-openai-api-key'")
        print("  )")
        
        # Пример подключения Anthropic модели
        print("\n📝 Example: Connect Anthropic Model")
        print("Command:")
        print("  await client.connect_model(")
        print("      model_id='claude-3-sonnet-20240229',")
        print("      provider='anthropic',")
        print("      model_name='Claude 3 Sonnet',")
        print("      api_key='your-anthropic-api-key'")
        print("  )")
        
        # Пример подключения кастомной модели
        print("\n📝 Example: Connect Custom Model")
        print("Command:")
        print("  await client.connect_model(")
        print("      model_id='my-custom-model',")
        print("      provider='custom',")
        print("      model_name='My Custom AI Model',")
        print("      endpoint_url='http://my-server:8080/api/generate',")
        print("      api_key='optional-api-key'")
        print("  )")
        
        # 5. Интерактивное подключение модели (если пользователь хочет)
        print("\n5️⃣ Interactive Model Connection:")
        print("Would you like to connect a test model? (This is just a demo)")
        
        # Подключаем тестовую модель для демонстрации
        test_model_data = {
            "model_id": "test-model-demo",
            "provider": "foundry",
            "model_name": "Test Demo Model",
            "endpoint_url": "http://localhost:55581/v1/",
            "enabled": True
        }
        
        print(f"\n🔄 Connecting test model: {test_model_data['model_id']}")
        try:
            result = await client.connect_model(**test_model_data)
            if result['success']:
                print(f"✅ {result['message']}")
            else:
                print(f"❌ {result['message']}")
                if result.get('error'):
                    print(f"   Error: {result['error']}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
        
        # 6. Обновленный список моделей
        print("\n6️⃣ Updated Model List:")
        updated_connected = await client.get_connected_models()
        print(f"Total models: {updated_connected['total_count']}")
        
        # 7. Полезные команды
        print("\n7️⃣ Useful Commands:")
        print("📋 List all endpoints:")
        print("  curl http://localhost:8000/")
        print()
        print("🔍 Get connected models:")
        print("  curl http://localhost:8000/api/v1/models/connected")
        print()
        print("📦 Get providers:")
        print("  curl http://localhost:8000/api/v1/models/providers")
        print()
        print("🔗 Connect new model:")
        print("  curl -X POST http://localhost:8000/api/v1/models/connect \\")
        print("    -H 'Content-Type: application/json' \\")
        print("    -d '{\"model_id\": \"new-model\", \"provider\": \"foundry\"}'")
        print()
        print("🧪 Test model:")
        print("  curl -X POST http://localhost:8000/api/v1/models/test-model-demo/test \\")
        print("    -H 'Content-Type: application/json' \\")
        print("    -d '{\"test_prompt\": \"Hello, world!\"}'")
        print()
        print("❌ Disconnect model:")
        print("  curl -X DELETE http://localhost:8000/api/v1/models/test-model-demo")
        
        print("\n" + "=" * 60)
        print("🎉 Model Management Demo Complete!")
        print("📚 Check /docs for full API documentation")

if __name__ == "__main__":
    asyncio.run(demo_model_management())