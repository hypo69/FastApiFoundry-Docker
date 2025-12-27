#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Запуск FastApiFoundry сервера
# =============================================================================
# Описание:
#   Простой запуск FastAPI сервера. Для полного запуска с AI используйте start.ps1
#
# File: run.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import uvicorn
import requests
import sys

def check_foundry():
    """Проверка работы Foundry на порту из переменной окружения"""
    import os
    foundry_url = os.getenv('FOUNDRY_BASE_URL', 'http://localhost:50477/v1/')
    try:
        response = requests.get(f"{foundry_url}models", timeout=3)
        return response.status_code == 200
    except:
        return False

def main():
    """Основная функция запуска сервера"""
    print("🚀 FastAPI Foundry")
    
    # Проверка работы Foundry
    if not check_foundry():
        print("\n❌ Foundry не запущен!")
        print("\n💡 Для полного запуска с AI моделями используйте:")
        print("   .\\start.ps1")
        print("\n🛑 Выход...")
        return False
    
    print("✅ Foundry работает")
    print("🌐 Запуск FastAPI сервера...")
    
    try:
        uvicorn.run(
            "src.api.main:app",
            host="0.0.0.0", 
            port=8000, 
            reload=True
        )
        return True
    except KeyboardInterrupt:
        print("\n✅ Остановлено")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1)