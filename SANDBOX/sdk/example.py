#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Простой пример использования FastAPI Foundry SDK"""

from sdk import FoundryClient

def main():
    print("🚀 FastAPI Foundry SDK - Simple Example")
    print("=" * 50)
    
    with FoundryClient("http://localhost:9696") as client:
        # Проверка здоровья
        health = client.health()
        print(f"Status: {health.get('status', 'unknown')}")
        
        # Список моделей
        models = client.list_models()
        if models.get("success"):
            print(f"Models: {len(models.get('models', []))}")
        
        # Генерация текста
        response = client.generate("Hello, how are you?", max_tokens=50)
        if response.get("success"):
            print(f"Response: {response.get('content', response.get('response', ''))}")
        else:
            print(f"Error: {response.get('error')}")

if __name__ == "__main__":
    main()