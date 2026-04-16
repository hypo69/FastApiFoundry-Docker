# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Utils Module Initialization
# =============================================================================
# Description:
#   Utilities module initialization for FastAPI Foundry
#   Exports core functions for configuration management
#
# File: src/utils/__init__.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: December 9, 2025
# =============================================================================

from .env_processor import process_config, load_env_variables, validate_config

__all__ = [
    'process_config',
    'load_env_variables', 
    'validate_config'
]