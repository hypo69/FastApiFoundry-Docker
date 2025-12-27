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

def find_foundry() -> str | None:
    """
    Найти запущенный Foundry сервис
    
    Returns:
        str | None: URL Foundry API или None если не найден
    """
    # Проверяем переменную окружения
    foundry_port = os.getenv('FOUNDRY_DYNAMIC_PORT')
    if foundry_port:
        url = f"http://localhost:{foundry_port}/v1/"
        if _test_foundry_url(url):
            logger.info(f"✅ Foundry найден через переменную окружения: {url}")
            return url
    
    # Проверяем известные порты
    test_ports = [62171, 50477, 58130, 51601]
    logger.debug(f"🔍 Поиск Foundry на портах: {test_ports}")
    
    for port in test_ports:
        url = f"http://localhost:{port}/v1/"
        if _test_foundry_url(url):
            logger.info(f"✅ Foundry найден на порту {port}: {url}")
            return url
    
    logger.warning("❌ Foundry не найден")
    return None

def _test_foundry_url(url: str) -> bool:
    """
    Проверить доступность Foundry API
    
    Args:
        url: URL для проверки
        
    Returns:
        bool: True если Foundry доступен
    """
    try:
        response = requests.get(f"{url.rstrip('/')}/models", timeout=2)
        return response.status_code == 200
    except Exception:
        return False