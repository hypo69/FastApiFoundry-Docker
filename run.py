#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Запуск FastApiFoundry сервера
# =============================================================================
# Описание:
#   Простой запуск FastAPI сервера.
#   Если Foundry уже запущен — AI будет доступен.
#   Для полного запуска (Foundry + env) используйте start.ps1
#
# File: run.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import sys
import json
import socket
import os
import logging
from pathlib import Path

# Добавляем текущую директорию в sys.path для импорта модулей
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Добавляем site-packages для python311
sys.path.append('C:/python311/Lib/site-packages')

# Загружаем переменные окружения перед импортом конфигурации
try:
    from src.utils.env_processor import load_env_variables, process_config
    load_env_variables()
    print("Environment variables loaded")
except ImportError:
    print("Environment processor not available, using default config")

from src.core.config import config

# Импортируем requests только если он доступен
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    print("Warning: requests not available, some features disabled")
    REQUESTS_AVAILABLE = False

try:
    import uvicorn
    UVICORN_AVAILABLE = True
except ImportError:
    print("Error: uvicorn not available, cannot start server")
    UVICORN_AVAILABLE = False
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


# =============================================================================
# Utils
# =============================================================================
def find_free_port(start_port: int = 9696, end_port: int = 9796) -> int | None:
    """Найти свободный порт в диапазоне"""
    logger.debug(f"Поиск свободного порта в диапазоне {start_port}-{end_port}")
    
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('localhost', port))
                logger.info(f"Найден свободный порт: {port}")
                return port
            except OSError:
                logger.debug(f"Порт {port} занят")
                continue
    
    logger.warning(f"Не найден свободный порт в диапазоне {start_port}-{end_port}")
    return None


# =============================================================================
# Port management
# =============================================================================
def get_server_port() -> int:
    """Определяется порт FastAPI сервера"""
    default_port = config.api_port
    auto_find = config.port_auto_find_free
    
    logger.info(f"Определение порта FastAPI сервера...")
    logger.debug(f"Порт по умолчанию: {default_port}")
    logger.debug(f"Автопоиск свободного порта: {auto_find}")

    if not auto_find:
        logger.info(f'Используется фиксированный порт: {default_port}')
        return default_port

    start_port = config.port_range_start
    end_port = config.port_range_end

    free_port = find_free_port(start_port, end_port)
    if free_port:
        logger.info(f'Найден свободный порт: {free_port}')
        return free_port

    logger.warning(f'Свободный порт не найден, используется порт {default_port}')
    return default_port


# =============================================================================
# Foundry
# =============================================================================
def find_foundry_port() -> int | None:
    """Найти порт запущенного Foundry по имени процесса"""
    if not REQUESTS_AVAILABLE:
        print("requests not available, cannot search for Foundry")
        return None
    
    try:
        # Ищем процесс Foundry
        import subprocess
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq foundry*'], 
                              capture_output=True, text=True, shell=True)
        
        if 'foundry' in result.stdout.lower():
            print("Foundry process found")
            
            # Ищем порт через netstat
            netstat_result = subprocess.run(['netstat', '-ano'], 
                                           capture_output=True, text=True)
            
            for line in netstat_result.stdout.split('\n'):
                if 'LISTENING' in line and '127.0.0.1:' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        addr = parts[1]
                        if '127.0.0.1:' in addr:
                            port = int(addr.split(':')[1])
                            # Проверяем, что это Foundry API
                            try:
                                response = requests.get(f'http://127.0.0.1:{port}/v1/models', timeout=1)
                                if response.status_code == 200:
                                    print(f"Foundry found on port: {port}")
                                    return port
                            except:
                                continue
        
        print("Foundry process not found")
        return None
        
    except Exception as e:
        print(f"Error searching for Foundry: {e}")
        return None


def resolve_foundry_base_url() -> str | None:
    """Определяется base_url Foundry (только динамически)"""
    # Проверяем переменную окружения FOUNDRY_DYNAMIC_PORT
    foundry_port = os.getenv('FOUNDRY_DYNAMIC_PORT')
    if foundry_port:
        try:
            port = int(foundry_port)
            foundry_url = f'http://localhost:{port}/v1/'
            print(f'Found Foundry from env var on port: {foundry_url}')
            return foundry_url
        except ValueError:
            pass
    
    # Только автоматическое определение порта
    foundry_port = find_foundry_port()
    if foundry_port:
        foundry_url = f'http://localhost:{foundry_port}/v1/'
        print(f'Found Foundry on port: {foundry_url}')
        return foundry_url

    print('Foundry not found')
    return None


def check_foundry(foundry_base_url: str | None) -> bool:
    """Проверяется доступность Foundry"""
    if not foundry_base_url or not REQUESTS_AVAILABLE:
        return False

    try:
        response = requests.get(
            f'{foundry_base_url}models',
            timeout=3,
        )
        return response.status_code == 200
    except Exception:
        return False


# =============================================================================
# Main
# =============================================================================
def main() -> bool:
    """Основная функция запуска сервера"""
    logger.info('FastAPI Foundry')
    logger.info('=' * 50)

    # -------------------------------------------------------------------------
    # Foundry
    # -------------------------------------------------------------------------
    logger.info("Poisk Foundry...")
    foundry_base_url = resolve_foundry_base_url()

    if foundry_base_url and check_foundry(foundry_base_url):
        # Обновляем свойство Config с найденным URL
        config.foundry_base_url = foundry_base_url
        logger.info(f'Foundry dostupен: {foundry_base_url}')
    else:
        logger.warning('Foundry nedostupен — AI funkcii otklyucheny')

    # -------------------------------------------------------------------------
    # FastAPI
    # -------------------------------------------------------------------------
    host = config.api_host
    reload_enabled = config.api_reload
    log_level = config.api_log_level.lower()
    workers = config.api_workers

    if reload_enabled:
        workers = 1

    port = get_server_port()

    logger.info('\nZapusk FastAPI servera')
    logger.info(f'   Host: {host}')
    logger.info(f'   Port: {port}')
    logger.info(f'   Reload: {reload_enabled}')
    logger.info(f'   Workers: {workers}')
    logger.info('-' * 50)
    logger.info(f'UI:   http://localhost:{port}')
    logger.info(f'Docs: http://localhost:{port}/docs')
    logger.info(f'Health: http://localhost:{port}/api/v1/health')
    logger.info('-' * 50)

    try:
        uvicorn.run(
            'src.api.main:app',
            host=host,
            port=port,
            reload=reload_enabled,
            workers=workers,
            log_level=log_level,
        )
        return True
    except KeyboardInterrupt:
        logger.info('\nStopped by user')
        return True
    except Exception as exc:
        logger.error(f'Server startup error: {exc}')
        return False


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
