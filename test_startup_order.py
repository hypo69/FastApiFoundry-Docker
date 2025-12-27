#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Тест нового порядка запуска
# =============================================================================
# Описание:
#   Тест правильного порядка: Foundry -> FastAPI консоль
#
# File: test_startup_order.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import requests
import time

def test_foundry_connection():
    """Тест подключения к Foundry"""
    print("🔍 Тестируем подключение к Foundry...")
    
    try:
        response = requests.get("http://localhost:50477/v1/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models_count = len(data.get('data', []))
            print(f"✅ Foundry работает! Доступно моделей: {models_count}")
            return True
        else:
            print(f"❌ Foundry отвечает с ошибкой: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Foundry не запущен (порт 50477 недоступен)")
        return False
    except Exception as e:
        print(f"❌ Ошибка проверки Foundry: {e}")
        return False

def test_fastapi_connection():
    """Тест подключения к FastAPI"""
    print("🔍 Тестируем подключение к FastAPI...")
    
    try:
        response = requests.get("http://localhost:9696/api/v1/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ FastAPI работает! Статус: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ FastAPI отвечает с ошибкой: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ FastAPI не запущен (порт 8000 недоступен)")
        return False
    except Exception as e:
        print(f"❌ Ошибка проверки FastAPI: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("=" * 60)
    print("🧪 ТЕСТ ПОРЯДКА ЗАПУСКА")
    print("=" * 60)
    print("Правильный порядок:")
    print("1. Foundry сервер (порт 50477)")
    print("2. FastAPI консоль (порт 8000)")
    print("=" * 60)
    
    # Тест 1: Foundry
    foundry_ok = test_foundry_connection()
    print()
    
    # Тест 2: FastAPI
    fastapi_ok = test_fastapi_connection()
    print()
    
    # Результат
    print("=" * 60)
    if foundry_ok and fastapi_ok:
        print("🎉 ВСЕ РАБОТАЕТ! Порядок запуска правильный.")
        print("✅ Foundry: запущен и отвечает")
        print("✅ FastAPI: запущен и отвечает")
    elif not foundry_ok and fastapi_ok:
        print("⚠️  ЧАСТИЧНО РАБОТАЕТ")
        print("❌ Foundry: не запущен")
        print("✅ FastAPI: запущен")
        print("💡 Запустите Foundry перед FastAPI для полной функциональности")
    elif foundry_ok and not fastapi_ok:
        print("⚠️  ЧАСТИЧНО РАБОТАЕТ")
        print("✅ Foundry: запущен")
        print("❌ FastAPI: не запущен")
        print("💡 Запустите FastAPI: python run.py")
    else:
        print("❌ НИЧЕГО НЕ РАБОТАЕТ")
        print("❌ Foundry: не запущен")
        print("❌ FastAPI: не запущен")
        print("💡 Запустите сначала Foundry, потом FastAPI")
    
    print("=" * 60)

if __name__ == "__main__":
    main()