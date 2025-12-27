#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Конфигурация FastAPI Foundry
# =============================================================================
# Описание:
#   Минимальная конфигурация
#
# File: config.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import json
import os
from pathlib import Path

# Загружаем config.json
config_file = Path(__file__).parent.parent / "config.json"
config_data = {}
if config_file.exists():
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except:
        pass

def get_config(key, default=None):
    """Получить значение из config.json или env"""
    env_key = key.upper()
    return os.getenv(env_key, config_data.get(key, default))

class Settings:
    """Простые настройки"""
    
    def __init__(self):
        # API
        self.api_host = get_config('host', '0.0.0.0')
        self.api_port = int(get_config('port', 8000))
        self.api_key = get_config('api_key', '')
        
        # Foundry - используем переменную окружения или config.json
        foundry_env_url = os.getenv('FOUNDRY_BASE_URL')
        if foundry_env_url:
            self.foundry_base_url = foundry_env_url
        else:
            self.foundry_base_url = config_data.get('foundry_ai', {}).get('base_url', 'http://localhost:50477/v1/')
        self.foundry_default_model = get_config('foundry_default_model', 'deepseek-r1-distill-qwen-7b-generic-cpu:3')
        self.foundry_timeout = int(get_config('foundry_timeout', 30))
        
        # RAG
        self.rag_enabled = get_config('rag_enabled', 'true').lower() == 'true'
        self.rag_index_dir = get_config('rag_index_dir', './rag_index')
        self.rag_model = get_config('rag_model', 'all-MiniLM-L6-v2')
        
        # CORS
        self.cors_origins = get_config('cors_origins', '["*"]')

settings = Settings()