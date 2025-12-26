#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Запуск FastApiFoundry сервера
# =============================================================================
# Описание:
#   Основной скрипт запуска FastAPI сервера
#   Простой и надежный запуск с чтением конфигурации
#
# Примеры использования:
#   python run.py
#     → Запуск с настройками по умолчанию (host=0.0.0.0, port=8000, mode=dev)
#
#   python run.py --host 127.0.0.1
#     → Изменить хост на локальный (по умолчанию 0.0.0.0 - все интерфейсы)
#
#   python run.py --port 8001
#     → Запуск на порту 8001 (по умолчанию 8000)
#
#   python run.py --reload
#     → Включить автоперезагрузку при изменении кода (по умолчанию false)
#
#   python run.py --log-level DEBUG
#     → Установить уровень логирования (по умолчанию INFO)
#     → Доступные уровни: DEBUG, INFO, WARNING, ERROR
#
#   python run.py --host 127.0.0.1 --port 8002 --reload --log-level DEBUG
#     → Комбинация параметров для разработки
#
# Источники конфигурации (по приоритету):
#   1. Аргументы командной строки (--host, --port, etc.) - высший приоритет
#   2. Переменные окружения (.env файл)
#   3. config.json файл
#   4. Значения по умолчанию - низший приоритет
#
# Настройки по умолчанию:
#   host: 0.0.0.0 (все сетевые интерфейсы)
#   port: 8000
#   mode: dev (автоматически открывает браузер)
#   reload: true (автоперезагрузка включена в dev режиме)
#   log_level: INFO
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

def check_foundry_status(base_url="http://localhost:50477/v1"):
    """Проверить статус Foundry сервера"""
    try:
        response = requests.get(f"{base_url}/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models_count = len(data.get('data', []))
            return True, f"Foundry работает, доступно моделей: {models_count}"
        else:
            return False, f"Foundry отвечает с ошибкой: HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Foundry не запущен (порт 50477 недоступен)"
    except Exception as e:
        return False, f"Ошибка проверки Foundry: {e}"

def start_foundry():
    """Попытаться запустить Foundry"""
    print("Попытка запуска Foundry...")
    try:
        # Попробовать запустить foundry через командную строку
        if os.name == 'nt':  # Windows
            subprocess.Popen(['foundry'], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:  # Linux/Mac
            subprocess.Popen(['foundry'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Подождать немного для запуска
        time.sleep(3)
        return True
    except Exception as e:
        print(f"Не удалось запустить Foundry автоматически: {e}")
        return False

def ensure_foundry_running(base_url="http://localhost:50477/v1", max_retries=3):
    """Убедиться что Foundry запущен и работает"""
    print("Проверяем статус Foundry сервера...")
    
    for attempt in range(max_retries):
        is_running, message = check_foundry_status(base_url)
        
        if is_running:
            print(f"✅ {message}")
            return True
        
        print(f"❌ {message}")
        
        if attempt < max_retries - 1:
            print(f"Попытка {attempt + 1}/{max_retries}: Пытаемся запустить Foundry...")
            if start_foundry():
                # Подождать больше времени после запуска
                print("Ждем запуска Foundry (10 секунд)...")
                time.sleep(10)
            else:
                print("Не удалось запустить Foundry автоматически")
                break
    
    print("\n" + "="*60)
    print("⚠️  ВНИМАНИЕ: Foundry сервер не запущен!")
    print("")
    print("Для работы с AI моделями необходимо:")
    print("1. Установить Foundry: https://github.com/foundry-rs/foundry")
    print("2. Запустить Foundry сервер на порту 50477")
    print("3. Или использовать веб-интерфейс для управления Foundry")
    print("")
    print("FastAPI консоль запустится, но AI функции будут недоступны")
    print("="*60 + "\n")
    
    return False

def load_config():
    """Загрузить конфигурацию из config.json"""
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "fastapi_server": {
            "host": "0.0.0.0",
            "port": 8000,
            "mode": "dev",
            "reload": True,
            "log_level": "INFO"
        },
        "foundry_ai": {
            "base_url": "http://localhost:50477/v1/"
        },
        "rag_system": {
            "enabled": True
        }
    }

def open_browser(url: str, delay: int = 3):
    """Открыть браузер через указанное время"""
    def _open():
        try:
            time.sleep(delay)
            print(f"Opening browser: {url}")
            if os.getenv('FASTAPI_FOUNDRY_MODE') != 'production':
                webbrowser.open(url)
        except Exception as e:
            print(f"Failed to open browser: {e}")
    
    thread = threading.Thread(target=_open)
    thread.daemon = True
    thread.start()

def main():
    """Главная функция запуска"""
    parser = argparse.ArgumentParser(description="FastAPI Foundry Server")
    parser.add_argument('--host', help='Host to bind to')
    parser.add_argument('--port', type=int, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='Log level')
    
    args = parser.parse_args()
    
    # Загрузить конфигурацию
    config = load_config()
    
    # Получить финальные значения
    host = args.host or config["fastapi_server"]["host"]
    port = args.port or config["fastapi_server"]["port"]
    reload = args.reload or config["fastapi_server"]["reload"]
    log_level = args.log_level or config["fastapi_server"]["log_level"]
    mode = config["fastapi_server"]["mode"]
    
    # Установить режим логирования
    os.environ["FASTAPI_FOUNDRY_MODE"] = mode
    
    print("=" * 60)
    print("Starting FastAPI Foundry Application")
    print(f"Mode: {mode}")
    print(f"Config source: config.json + args")
    print(f"Python: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print("=" * 60)
    
    # ПРОВЕРКА И ЗАПУСК FOUNDRY (ПЕРВЫЙ ПРИОРИТЕТ!)
    foundry_running = ensure_foundry_running(config['foundry_ai']['base_url'])
    
    if not foundry_running:
        print("Продолжаем запуск FastAPI консоли без Foundry...")
        time.sleep(2)
    
    # Создать директорию для логов
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print(f"Logs directory: {logs_dir.absolute()}")
    
    # ПРОВЕРКА ПОРТА FASTAPI (ВТОРОЙ ПРИОРИТЕТ)
    print(f"\nПроверяем доступность порта {port} для FastAPI...")
    if not ensure_port_free(port):
        print(f"Не удалось освободить порт {port}")
        return False
    print(f"Порт {port} свободен")
    
    # Подождать немного после завершения процесса
    time.sleep(1)
    
    # ЗАПУСК FASTAPI КОНСОЛИ (ТРЕТИЙ ПРИОРИТЕТ)
    print("\n" + "=" * 60)
    print("🚀 Запускаем FastAPI консоль...")
    print("=" * 60)
    
    # Запустить браузер в отдельном потоке (только в dev режиме)
    if mode != 'production':
        open_browser(f"http://localhost:{port}")
    
    print(f"Starting FastAPI server on http://{host}:{port}")
    print(f"Web interface: http://localhost:{port}")
    print(f"API docs: http://localhost:{port}/docs")
    print(f"Foundry URL: {config['foundry_ai']['base_url']}")
    print(f"RAG enabled: {config['rag_system']['enabled']}")
    
    try:
        # Запуск uvicorn
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
        print("\n" + "=" * 60)
        print("Application stopped by user (Ctrl+C)")
        print("=" * 60)
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        print("Check if all dependencies are installed: pip install -r requirements.txt")
        return False
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {port} is already in use")
            print("Run 'python stop.py' to stop existing servers")
        else:
            print(f"OS error: {e}")
        return False
    except Exception as e:
        print(f"Application failed to start: {e}")
        return False
    finally:
        print("=" * 60)
        print("Application shutdown complete")
        print("=" * 60)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)