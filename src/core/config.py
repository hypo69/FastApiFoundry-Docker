# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Единая конфигурация проекта (Refactored)
# =============================================================================
# Описание:
#   Импорт единого класса конфигурации для использования в FastAPI
#
# File: config.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

from config_manager import config

# Экспортируем для обратной совместимости
settings = config