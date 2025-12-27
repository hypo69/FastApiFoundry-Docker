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
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0
# Copyright: © 2025 AiStros
# =============================================================================

import sys
import json
import socket
import os
import logging
from pathlib import Path

from src.core.config import config
import requests
import uvicorn

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
    logger.debug(f"🔍 Поиск свободного порта в диапазоне {start_port}-{end_port}")
    
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('localhost', port))
                logger.info(f"✅ Найден свободный порт: {port}")
                return port
            except OSError:
                logger.debug(f"❌ Порт {port} занят")
                continue
    
    logger.warning(f"⚠️ Не найден свободный порт в диапазоне {start_port}-{end_port}")
    return None


# =============================================================================
# Port management
# =============================================================================
def get_server_port() -> int:
    """Определяется порт FastAPI сервера"""
    default_port = config.api_port
    auto_find = config.port_auto_find_free
    
    logger.info(f"🔌 Определение порта FastAPI сервера...")
    logger.debug(f"Порт по умолчанию: {default_port}")
    logger.debug(f"Автопоиск свободного порта: {auto_find}")

    if not auto_find:
        logger.info(f'📌 Используется фиксированный порт: {default_port}')
        return default_port

    start_port = config.port_range_start
    end_port = config.port_range_end

    free_port = find_free_port(start_port, end_port)
    if free_port:
        logger.info(f'🔍 Найден свободный порт: {free_port}')
        return free_port

    logger.warning(f'⚠️ Свободный порт не найден, используется порт {default_port}')
    return default_port


# =============================================================================
# Foundry
# =============================================================================
def find_foundry_port() -> int | None:
    """Найти порт запущенного Foundry"""
    # Сначала проверяем известный порт 62171
    test_ports = [62171, 50477, 58130]
    print(f"🔍 Проверка известных портов: {test_ports}")
    
    for port in test_ports:
        try:
            response = requests.get(f'http://127.0.0.1:{port}/v1/models', timeout=2)
            if response.status_code == 200:
                print(f"✅ Foundry найден на порту: {port}")
                return port
            else:
                print(f"❌ Порт {port}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Порт {port}: {e}")
    
    # Если не найден, делаем полный поиск
    print("🔍 Полный поиск портов 50000-65000...")
    for port in range(50000, 65000, 100):  # Каждый 100-й порт для скорости
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.05)
                if s.connect_ex(('127.0.0.1', port)) == 0:
                    try:
                        response = requests.get(f'http://127.0.0.1:{port}/v1/models', timeout=1)
                        if response.status_code == 200:
                            print(f"✅ Foundry найден на порту: {port}")
                            return port
                    except:
                        continue
        except:
            continue
    
    print("❌ Foundry не найден")
    return None


def resolve_foundry_base_url() -> str | None:
    """Определяется base_url Foundry (только динамически)"""
    # Только автоматическое определение порта
    foundry_port = find_foundry_port()
    if foundry_port:
        foundry_url = f'http://localhost:{foundry_port}/v1/'
        print(f'🔗 Найден Foundry на порту: {foundry_url}')
        return foundry_url

    print('⚠️ Foundry не найден')
    return None


def check_foundry(foundry_base_url: str | None) -> bool:
    """Проверяется доступность Foundry"""
    if not foundry_base_url:
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
    logger.info('🚀 FastAPI Foundry')
    logger.info('=' * 50)

    # -------------------------------------------------------------------------
    # Foundry
    # -------------------------------------------------------------------------
    logger.info("🔍 Поиск Foundry...")
    foundry_base_url = resolve_foundry_base_url()

    if foundry_base_url and check_foundry(foundry_base_url):
        # Обновляем свойство Config с найденным URL
        config.foundry_base_url = foundry_base_url
        logger.info(f'✅ Foundry доступен: {foundry_base_url}')
    else:
        logger.warning('⚠️ Foundry недоступен — AI функции отключены')

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

    logger.info('\n🌐 Запуск FastAPI сервера')
    logger.info(f'   Host: {host}')
    logger.info(f'   Port: {port}')
    logger.info(f'   Reload: {reload_enabled}')
    logger.info(f'   Workers: {workers}')
    logger.info('-' * 50)
    logger.info(f'🔗 UI:   http://localhost:{port}')
    logger.info(f'📚 Docs: http://localhost:{port}/docs')
    logger.info(f'🏥 Health: http://localhost:{port}/api/v1/health')
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
        logger.info('\n✅ Остановлено пользователем')
        return True
    except Exception as exc:
        logger.error(f'❌ Ошибка запуска сервера: {exc}')
        return False


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
