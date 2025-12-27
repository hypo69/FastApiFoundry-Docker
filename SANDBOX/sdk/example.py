#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Foundry SDK Example
# =============================================================================
# Описание:
#   Пример использования FastAPI Foundry SDK
#
# File: example.py
# Project: FastApiFoundry (Docker)
# Version: 0.3.4
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import sys
import os

# Добавляем путь к SDK
sys.path.insert(0, os.path.dirname(__file__))

from .client import FoundryClient
from .exceptions import FoundryError

def main():
    """Демонстрация использования SDK"""
    
    print("🚀 FastAPI Foundry SDK Example")
    print("=" * 50)
    
    # Создаем клиент
    with FoundryClient(base_url="http://localhost:9696") as client:
        
        try:
            # 1. Проверка здоровья
            print("\n1️⃣ Health Check:")
            health = client.health()
            print(f"  Status: {health.status}")
            print(f"  Foundry: {health.foundry_status}")
            print(f"  RAG chunks: {health.rag_chunks}")
            print(f"  Models: {health.models_count}")
            
            # 2. Список моделей
            print("\n2️⃣ Available Models:")
            models = client.list_models()
            for model in models:
                print(f"  - {model.id} ({model.provider})")
            
            # 3. RAG поиск
            print("\n3️⃣ RAG Search:")
            results = client.rag_search("FastAPI installation", top_k=3)
            print(f"  Found {len(results)} results")
            for i, result in enumerate(results, 1):
                print(f"    {i}. {result.get('source', 'Unknown')} (score: {result.get('score', 0):.3f})")
            
            # 4. Генерация текста (только если Foundry доступен)
            if health.is_foundry_connected:
                print("\n4️⃣ Text Generation:")
                response = client.generate(
                    prompt="Как установить FastAPI Foundry?",
                    use_rag=True,
                    max_tokens=200
                )
                
                if response.success:
                    print(f"  Response: {response.content[:100]}...")
                    if response.rag_sources:
                        print(f"  Sources: {', '.join(response.rag_sources)}")
                else:
                    print(f"  Error: {response.error}")
            else:
                print("\n4️⃣ Text Generation: SKIPPED (Foundry not available)")
            
            # 5. Конфигурация
            print("\n5️⃣ Configuration:")
            config = client.get_config()
            if config:
                foundry_config = config.get("foundry_ai", {})
                print(f"  Foundry URL: {foundry_config.get('base_url', 'N/A')}")
                print(f"  Default model: {foundry_config.get('default_model', 'N/A')}")
                print(f"  RAG enabled: {config.get('rag_system', {}).get('enabled', False)}")
            
            # 6. Очистка RAG (опционально)
            print("\n6️⃣ RAG Clear (optional):")
            print("  Skipped - use client.rag_clear() to clear RAG index")
            
            print("\n✅ SDK работает корректно!")
            
        except FoundryError as e:
            print(f"\n❌ SDK Error: {e}")
        except Exception as e:
            print(f"\n❌ Unexpected Error: {e}")

if __name__ == "__main__":
    main()