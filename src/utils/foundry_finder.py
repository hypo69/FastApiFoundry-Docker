# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Foundry Finder Utility
# =============================================================================
# Описание:
#   Утилита для поиска запущенного Foundry сервиса
#   Проверяет известные порты и переменные окружения
#
# File: foundry_finder.py
# Project: FastApiFoundry (Docker)
# Version: 0.3.3
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import os
import requests
import logging

logger = logging.getLogger(__name__)

def find_foundry_port() -> int | None:
    """Найти порт запущенного Foundry"""
    # Сначала проверяем переменную окружения
    foundry_port = os.getenv('FOUNDRY_DYNAMIC_PORT')
    if foundry_port:
        try:
            port = int(foundry_port)
            if _test_foundry_port(port):
                logger.info(f"✅ Foundry найден через переменную окружения: {port}")
                return port
        except ValueError:
            pass
    
    # Проверяем известные порты
    test_ports = [62171, 50477, 58130]
    logger.info(f"🔍 Поиск Foundry на портах: {test_ports}")
    
    for port in test_ports:
        if _test_foundry_port(port):
            logger.info(f"✅ Foundry найден на порту: {port}")
            return port
    
    logger.warning("❌ Foundry не найден на известных портах")
    return None

def _test_foundry_port(port: int) -> bool:
    """Проверить доступность Foundry на порту"""
    try:
        logger.debug(f"Проверка порта {port}...")
        response = requests.get(f'http://127.0.0.1:{port}/v1/models', timeout=2)
        if response.status_code == 200:
            return True
        else:
            logger.debug(f"❌ Порт {port}: HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.debug(f"❌ Порт {port}: {e}")
        return False

def find_foundry_url() -> str | None:
    """Найти URL запущенного Foundry"""
    port = find_foundry_port()
    if port:
        return f"http://localhost:{port}/v1/"
    return None