#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Конфигурация FastAPI Foundry
# =============================================================================
# Описание:
#   Простая конфигурация без Pydantic BaseSettings
#   Загружает настройки из config.json и переменных окружения
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
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Загружаем config.json
config_file = Path(__file__).parent.parent / "config.json"
config_data = {}
if config_file.exists():
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except Exception:
        config_data = {}

class Settings:
    """Простой класс настроек"""
    
    def __init__(self):
        # FastAPI Server
        fastapi_config = config_data.get('fastapi_server', {})
        self.api_host = os.getenv('API_HOST', fastapi_config.get('host', '0.0.0.0'))
        self.api_port = int(os.getenv('API_PORT', fastapi_config.get('port', 8000)))
        self.api_reload = os.getenv('API_RELOAD', str(fastapi_config.get('reload', False))).lower() == 'true'
        self.api_workers = int(os.getenv('API_WORKERS', fastapi_config.get('workers', 1)))
        
        # Security
        security_config = config_data.get('security', {})
        self.api_key = os.getenv('API_KEY', security_config.get('api_key', ''))
        self.https_enabled = security_config.get('https_enabled', False)
        self.ssl_cert_file = security_config.get('ssl_cert_file', '~/.ssl/cert.pem')
        self.ssl_key_file = security_config.get('ssl_key_file', '~/.ssl/key.pem')
        
        # Foundry AI
        foundry_config = config_data.get('foundry_ai', {})
        self.foundry_base_url = os.getenv('FOUNDRY_BASE_URL', foundry_config.get('base_url', 'http://localhost:50477/v1/'))
        self.foundry_default_model = os.getenv('FOUNDRY_DEFAULT_MODEL', foundry_config.get('default_model', 'deepseek-r1-distill-qwen-7b-generic-cpu:3'))
        self.foundry_temperature = float(os.getenv('FOUNDRY_TEMPERATURE', foundry_config.get('temperature', 0.6)))
        self.foundry_top_p = float(os.getenv('FOUNDRY_TOP_P', foundry_config.get('top_p', 0.9)))
        self.foundry_top_k = int(os.getenv('FOUNDRY_TOP_K', foundry_config.get('top_k', 40)))
        self.foundry_max_tokens = int(os.getenv('FOUNDRY_MAX_TOKENS', foundry_config.get('max_tokens', 2048)))
        self.foundry_timeout = int(os.getenv('FOUNDRY_TIMEOUT', foundry_config.get('timeout', 300)))
        
        # RAG System
        rag_config = config_data.get('rag_system', {})
        self.rag_enabled = os.getenv('RAG_ENABLED', str(rag_config.get('enabled', True))).lower() == 'true'
        self.rag_index_dir = os.getenv('RAG_INDEX_DIR', rag_config.get('index_dir', './rag_index'))
        self.rag_model = os.getenv('RAG_MODEL', rag_config.get('model', 'sentence-transformers/all-MiniLM-L6-v2'))
        
        # Logging
        logging_config = config_data.get('logging', {})
        self.log_level = os.getenv('LOG_LEVEL', logging_config.get('level', 'INFO'))
        self.log_file = os.getenv('LOG_FILE', logging_config.get('file', 'logs/fastapi-foundry.log'))
        
        # CORS
        cors_origins = fastapi_config.get('cors_origins', ['*'])
        self.cors_origins = json.loads(os.getenv('CORS_ORIGINS', json.dumps(cors_origins)))

# Создаем глобальный экземпляр настроек
settings = Settings()

def get_settings():
    """Получить настройки"""
    return settings