#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Глобальный класс конфигурации FastAPI Foundry
# =============================================================================
# Описание:
#   Единый класс для управления конфигурацией из config.json, .env и аргументов
#   Приоритет: аргументы командной строки > .env > config.json > значения по умолчанию
#
# Примеры:
#   from config import Config
#   config = Config()
#   print(config.get('fastapi_server.port'))
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
from typing import Any, Dict, Optional, Union
from dotenv import load_dotenv

class Config:
    """Глобальный класс конфигурации"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.project_root = Path(__file__).parent
            self.config_file = self.project_root / "config.json"
            self.env_file = self.project_root / ".env"
            
            # Загрузить конфигурацию
            self._load_config()
            self._initialized = True
    
    def _load_config(self):
        """Загрузка конфигурации из всех источников"""
        # 1. Значения по умолчанию
        self.data = self._get_default_config()
        
        # 2. Загрузить из config.json
        self._load_from_json()
        
        # 3. Загрузить из .env
        self._load_from_env()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Конфигурация по умолчанию"""
        return {
            "fastapi_server": {
                "host": "0.0.0.0",
                "port": 8000,
                "mode": "dev",
                "workers": 1,
                "reload": True,
                "log_level": "INFO"
            },
            "foundry_ai": {
                "base_url": "http://localhost:50477/v1/",
                "default_model": "deepseek-r1-distill-qwen-7b-generic-cpu:3",
                "temperature": 0.6,
                "top_p": 0.9,
                "top_k": 40,
                "max_tokens": 2048,
                "timeout": 300
            },
            "rag_system": {
                "enabled": True,
                "index_dir": "./rag_index",
                "model": "sentence-transformers/all-MiniLM-L6-v2",
                "chunk_size": 1000,
                "top_k": 5
            },
            "security": {
                "api_key": "",
                "https_enabled": False,
                "cors_origins": ["*"],
                "ssl_cert_file": "~/.ssl/cert.pem",
                "ssl_key_file": "~/.ssl/key.pem"
            },
            "logging": {
                "level": "INFO",
                "file": "logs/fastapi-foundry.log"
            },
            "mcp_server": {
                "base_url": "http://localhost:51601/v1/",
                "default_model": "deepseek-r1-distill-qwen-7b-generic-cpu:3",
                "timeout": 30
            },
            "docker": {
                "foundry_host": "localhost",
                "foundry_port": 8008,
                "rag_enabled": True
            }
        }
    
    def _load_from_json(self):
        """Загрузка из config.json"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    json_config = json.load(f)
                    self._merge_config(json_config)
        except Exception as e:
            print(f"Warning: Failed to load config.json: {e}")
    
    def _load_from_env(self):
        """Загрузка из .env файла"""
        try:
            # Загрузить .env файл
            if self.env_file.exists():
                load_dotenv(self.env_file)
            
            # Маппинг переменных окружения
            env_mapping = {
                # FastAPI Server
                'API_HOST': 'fastapi_server.host',
                'API_PORT': 'fastapi_server.port',
                'API_RELOAD': 'fastapi_server.reload',
                'API_WORKERS': 'fastapi_server.workers',
                'LOG_LEVEL': 'fastapi_server.log_level',
                'DEFAULT_MODE': 'fastapi_server.mode',
                
                # Foundry AI
                'FOUNDRY_BASE_URL': 'foundry_ai.base_url',
                'FOUNDRY_DEFAULT_MODEL': 'foundry_ai.default_model',
                'FOUNDRY_TEMPERATURE': 'foundry_ai.temperature',
                'FOUNDRY_TOP_P': 'foundry_ai.top_p',
                'FOUNDRY_TOP_K': 'foundry_ai.top_k',
                'FOUNDRY_MAX_TOKENS': 'foundry_ai.max_tokens',
                'FOUNDRY_TIMEOUT': 'foundry_ai.timeout',
                
                # RAG System
                'RAG_ENABLED': 'rag_system.enabled',
                'RAG_INDEX_DIR': 'rag_system.index_dir',
                'RAG_MODEL': 'rag_system.model',
                'RAG_CHUNK_SIZE': 'rag_system.chunk_size',
                'RAG_TOP_K': 'rag_system.top_k',
                
                # Security
                'API_KEY': 'security.api_key',
                'HTTPS_ENABLED': 'security.https_enabled',
                'SSL_CERT_FILE': 'security.ssl_cert_file',
                'SSL_KEY_FILE': 'security.ssl_key_file',
                
                # Logging
                'LOG_FILE': 'logging.file',
                
                # MCP Server
                'MCP_FOUNDRY_BASE_URL': 'mcp_server.base_url',
                'MCP_FOUNDRY_DEFAULT_MODEL': 'mcp_server.default_model',
                'MCP_FOUNDRY_TIMEOUT': 'mcp_server.timeout',
                
                # Docker
                'DOCKER_FOUNDRY_HOST': 'docker.foundry_host',
                'DOCKER_FOUNDRY_PORT': 'docker.foundry_port',
                'DOCKER_RAG_ENABLED': 'docker.rag_enabled'
            }
            
            # Применить переменные окружения
            for env_var, config_path in env_mapping.items():
                value = os.getenv(env_var)
                if value is not None:
                    self._set_nested_value(config_path, self._convert_value(value))
                    
        except Exception as e:
            print(f"Warning: Failed to load .env: {e}")
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """Слияние конфигураций"""
        def merge_dict(base: Dict, update: Dict):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(self.data, new_config)
    
    def _convert_value(self, value: str) -> Any:
        """Конвертация строкового значения в нужный тип"""
        # Boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer
        try:
            if '.' not in value:
                return int(value)
        except ValueError:
            pass
        
        # Float
        try:
            return float(value)
        except ValueError:
            pass
        
        # JSON array/object
        if value.startswith('[') or value.startswith('{'):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        # String
        return value
    
    def _set_nested_value(self, path: str, value: Any):
        """Установка значения по вложенному пути (например, 'fastapi_server.port')"""
        keys = path.split('.')
        current = self.data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def get(self, path: str, default: Any = None) -> Any:
        """Получение значения по пути"""
        keys = path.split('.')
        current = self.data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set(self, path: str, value: Any):
        """Установка значения по пути"""
        self._set_nested_value(path, value)
    
    def update_from_args(self, **kwargs):
        """Обновление конфигурации из аргументов командной строки"""
        for key, value in kwargs.items():
            if value is not None:
                if key == 'host':
                    self.set('fastapi_server.host', value)
                elif key == 'port':
                    self.set('fastapi_server.port', value)
                elif key == 'mode':
                    self.set('fastapi_server.mode', value)
                elif key == 'workers':
                    self.set('fastapi_server.workers', value)
                elif key == 'reload':
                    self.set('fastapi_server.reload', value)
                elif key == 'log_level':
                    self.set('fastapi_server.log_level', value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Получить всю конфигурацию как словарь"""
        return self.data.copy()
    
    def save_to_json(self, file_path: Optional[Path] = None):
        """Сохранить конфигурацию в JSON файл"""
        if file_path is None:
            file_path = self.config_file
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

# Глобальный экземпляр конфигурации
config = Config()