#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Запуск FastApiFoundry сервера
# =============================================================================
# Описание:
#   Простой запуск FastAPI сервера с проверкой Foundry
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
import webbrowser
import threading
import time
import os
import sys
import argparse
import json
import subprocess
import requests
from pathlib import Path
from utils.port_manager import ensure_port_free

def check_foundry(base_url="http://localhost:50477/v1"):
    """Проверить Foundry сервер"""
    try:
        response = requests.get(f"{base_url}/models", timeout=5)
        if response.status_code == 200:
            models = len(response.json().get('data', []))
            return True, f"✅ Foundry работает, моделей: {models}"
        return False, f"❌ Foundry HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "❌ Foundry не запущен (порт 50477)"
    except Exception as e:
        return False, f"❌ Ошибка Foundry: {e}"

def try_start_foundry():
    """Попытаться запустить Foundry"""
    try:
        cmd = ['foundry']
        kwargs = {'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL}
        if os.name == 'nt':
            kwargs['shell'] = True
        subprocess.Popen(cmd, **kwargs)
        time.sleep(3)
        return True
    except Exception:
        return False

def ensure_foundry(base_url="http://localhost:50477/v1"):
    """Проверить и запустить Foundry"""
    print("🔍 Проверяем Foundry...")
    
    # Проверяем 3 раза
    for i in range(3):
        is_running, message = check_foundry(base_url)
        print(message)
        
        if is_running:
            return True
            
        if i < 2:  # Не последняя попытка
            print(f"🚀 Попытка {i+1}/3: запускаем Foundry...")
            if try_start_foundry():
                time.sleep(7)  # Ждем запуска
    
    print("\n⚠️  Foundry не запущен. FastAPI запустится без AI функций.\n")
    return False

def load_config():
    """Загрузить config.json"""
    try:
        with open("config.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "fastapi_server": {"host": "0.0.0.0", "port": 8000, "mode": "dev", "reload": True, "log_level": "INFO"},
            "foundry_ai": {"base_url": "http://localhost:50477/v1/"},
            "rag_system": {"enabled": True}
        }

def open_browser(url, delay=3):
    """Открыть браузер"""
    def _open():
        time.sleep(delay)
        if os.getenv('FASTAPI_FOUNDRY_MODE') != 'production':
            webbrowser.open(url)
    
    threading.Thread(target=_open, daemon=True).start()

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="FastAPI Foundry Server")
    parser.add_argument('--host', help='Host to bind to')
    parser.add_argument('--port', type=int, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='Log level')
    args = parser.parse_args()
    
    config = load_config()
    
    # Получаем настройки
    host = args.host or config["fastapi_server"]["host"]
    port = args.port or config["fastapi_server"]["port"]
    reload = args.reload or config["fastapi_server"]["reload"]
    log_level = args.log_level or config["fastapi_server"]["log_level"]
    mode = config["fastapi_server"]["mode"]
    
    os.environ["FASTAPI_FOUNDRY_MODE"] = mode
    
    print(f"🚀 FastAPI Foundry | Mode: {mode} | Port: {port}")
    
    # Проверяем Foundry
    ensure_foundry(config['foundry_ai']['base_url'])
    
    # Проверяем порт
    Path("logs").mkdir(exist_ok=True)
    if not ensure_port_free(port):
        print(f"❌ Порт {port} занят")
        return False
    
    # Открываем браузер
    if mode != 'production':
        open_browser(f"http://localhost:{port}")
    
    print(f"🌐 http://localhost:{port} | 📚 http://localhost:{port}/docs")
    
    try:
        uvicorn.run(
            "src.api.main:app",
            host=host, 
            port=port, 
            reload=reload,
            log_level=log_level.lower(),
            access_log=True
        )
        return True
    except KeyboardInterrupt:
        print("\n✅ Остановлено пользователем")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Порт {port} уже используется")
        return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1)