#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Тест системы конфигурации FastAPI Foundry
# =============================================================================
# Описание:
#   Простой скрипт для проверки загрузки конфигурации из разных источников
#   Показывает приоритет: аргументы > .env > config.json > defaults
#
# Примеры:
#   python test_config.py
#
# File: test_config.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import json
from config import config

def main():
    """Тест системы конфигурации"""
    print("🔧 FastAPI Foundry Configuration Test")
    print("=" * 50)
    
    # Показать основные настройки
    print("\n📋 Current Configuration:")
    print(f"  FastAPI Host: {config.get('fastapi_server.host')}")
    print(f"  FastAPI Port: {config.get('fastapi_server.port')}")
    print(f"  Mode: {config.get('fastapi_server.mode')}")
    print(f"  Reload: {config.get('fastapi_server.reload')}")
    print(f"  Log Level: {config.get('fastapi_server.log_level')}")
    
    print(f"\n🤖 Foundry AI:")
    print(f"  Base URL: {config.get('foundry_ai.base_url')}")
    print(f"  Default Model: {config.get('foundry_ai.default_model')}")
    print(f"  Temperature: {config.get('foundry_ai.temperature')}")
    
    print(f"\n🔍 RAG System:")
    print(f"  Enabled: {config.get('rag_system.enabled')}")
    print(f"  Index Dir: {config.get('rag_system.index_dir')}")
    print(f"  Model: {config.get('rag_system.model')}")
    
    print(f"\n🔐 Security:")
    print(f"  API Key: {'***' if config.get('security.api_key') else 'Not set'}")
    print(f"  HTTPS: {config.get('security.https_enabled')}")
    
    # Тест обновления из аргументов
    print(f"\n🧪 Testing argument override:")
    print(f"  Original port: {config.get('fastapi_server.port')}")
    
    config.update_from_args(port=9999, host='127.0.0.1')
    print(f"  After update_from_args(port=9999, host='127.0.0.1'):")
    print(f"    Host: {config.get('fastapi_server.host')}")
    print(f"    Port: {config.get('fastapi_server.port')}")
    
    # Показать полную конфигурацию
    print(f"\n📄 Full Configuration (JSON):")
    print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))
    
    print(f"\n✅ Configuration test completed!")

if __name__ == "__main__":
    main()