#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки реализации чата с моделями
"""
import asyncio
import sys
import os

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.enhanced_foundry_client import enhanced_foundry_client

async def test_models():
    """Тестирование получения списка моделей"""
    print("🔍 Тестирование получения списка моделей...")

    try:
        models_info = await enhanced_foundry_client.list_models()
        print(f"✅ Получено {models_info.get('count', 0)} моделей")

        if models_info.get('success'):
            models = models_info.get('models', [])
            for i, model in enumerate(models[:5]):  # Показываем первые 5
                print(f"  {i+1}. {model.get('name')} ({model.get('type')}, {model.get('size')})")
            if len(models) > 5:
                print(f"  ... и еще {len(models) - 5} моделей")
        else:
            print(f"❌ Ошибка: {models_info.get('error')}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

async def test_chat_session():
    """Тестирование создания сессии чата"""
    print("\n💬 Тестирование создания сессии чата...")

    try:
        from api.endpoints.chat_endpoints import start_chat_session

        # Имитируем запрос
        request_data = {
            "model": "qwen2.5-0.5b-instruct-generic-cpu:4",
            "use_rag": False
        }

        result = await start_chat_session(request_data)
        print(f"✅ Сессия создана: {result}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

async def main():
    """Главная функция тестирования"""
    print("🚀 Тестирование реализации чата с AI моделями")
    print("=" * 50)

    await test_models()
    await test_chat_session()

    print("\n✅ Тестирование завершено")

if __name__ == "__main__":
    asyncio.run(main())