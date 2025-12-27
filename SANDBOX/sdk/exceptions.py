# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Foundry SDK Exceptions
# =============================================================================
# Описание:
#   Исключения для SDK
#
# File: exceptions.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

class FoundryError(Exception):
    """Базовое исключение SDK"""
    pass

class FoundryConnectionError(FoundryError):
    """Ошибка подключения к API"""
    pass

class FoundryAPIError(FoundryError):
    """Ошибка API (HTTP статус коды)"""
    pass

class FoundryConfigError(FoundryError):
    """Ошибка конфигурации"""
    pass

class FoundryModelError(FoundryError):
    """Ошибка работы с моделями"""
    pass