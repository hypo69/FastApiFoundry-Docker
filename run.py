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
import json
import socket
from pathlib import Path

def find_free_port(start_port=9696, end_port=9796):
    """Найти свободный порт в диапазоне"""
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return port
            except OSError:
                continue
    return None

def load_config():
    """Загрузить конфигурацию из config.json"""
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_server_port():
    """Получить порт для FastAPI сервера"""
    config = load_config()
    fastapi_config = config.get('fastapi_server', {})
    port_config = config.get('port_management', {})
    
    default_port = fastapi_config.get('port', 9696)
    auto_find = fastapi_config.get('auto_find_free_port', True)
    
    if auto_find:
        start_port = port_config.get('port_range_start', 9696)
        end_port = port_config.get('port_range_end', 9796)
        
        free_port = find_free_port(start_port, end_port)
        if free_port:
            print(f"🔍 Найден свободный порт: {free_port}")
            return free_port
        else:
            print(f"⚠️ Свободный порт не найден, используем: {default_port}")
            return default_port
    else:
        print(f"📌 Используем фиксированный порт: {default_port}")
        return default_port

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
    print("=" * 50)
    
    # Получаем порт для сервера
    port = get_server_port()
    
    # Проверка работы Foundry
    foundry_status = check_foundry()
    if not foundry_status:
        print("\n⚠️ Foundry не запущен, но сервер будет запущен")
        print("\n💡 Для полного запуска с AI моделями используйте:")
        print("   .\\start.ps1")
        print("   или")
        print("   .\\start_simple.ps1")
    else:
        print("✅ Foundry работает")
    
    print(f"\n🌐 Запуск FastAPI сервера на порту {port}...")
    print(f"🔗 Веб-интерфейс: http://localhost:{port}")
    print(f"📚 API документация: http://localhost:{port}/docs")
    print(f"🏥 Health check: http://localhost:{port}/api/v1/health")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "src.api.main:app",
            host="0.0.0.0", 
            port=port, 
            reload=True,
            log_level="info"
        )
        return True
    except KeyboardInterrupt:
        print("\n✅ Остановлено пользователем")
        return True
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1)