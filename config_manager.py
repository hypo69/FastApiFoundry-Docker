# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Единый класс конфигурации
# =============================================================================
# Описание:
#   Единый класс Config для всего проекта FastApiFoundry
#   Загружает настройки из config.json и предоставляет единый интерфейс
#
# File: config_manager.py
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
from typing import Dict, Any, Optional

class Config:
    """Единый класс конфигурации для всего проекта"""
    
    _instance = None
    _config_data = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Загрузить конфигурацию из config.json"""
        config_path = Path("config.json")
        
        if not config_path.exists():
            raise FileNotFoundError("config.json not found")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config_data = json.load(f)
    
    def reload(self):
        """Перезагрузить конфигурацию"""
        self._load_config()
    
    # FastAPI Server настройки
    @property
    def api_host(self) -> str:
        return self._config_data.get("fastapi_server", {}).get("host", "0.0.0.0")
    
    @property
    def api_port(self) -> int:
        return self._config_data.get("fastapi_server", {}).get("port", 8000)
    
    @property
    def api_mode(self) -> str:
        return self._config_data.get("fastapi_server", {}).get("mode", "dev")
    
    @property
    def api_workers(self) -> int:
        return self._config_data.get("fastapi_server", {}).get("workers", 1)
    
    @property
    def api_reload(self) -> bool:
        return self._config_data.get("fastapi_server", {}).get("reload", True)
    
    @property
    def api_log_level(self) -> str:
        return self._config_data.get("fastapi_server", {}).get("log_level", "INFO")
    
    # Foundry AI настройки
    @property
    def foundry_base_url(self) -> str:
        return self._config_data.get("foundry_ai", {}).get("base_url", "http://localhost:50477/v1/")
    
    @property
    def foundry_default_model(self) -> str:
        return self._config_data.get("foundry_ai", {}).get("default_model", "")
    
    @property
    def foundry_auto_load_default(self) -> bool:
        return self._config_data.get("foundry_ai", {}).get("auto_load_default", False)
    
    @property
    def foundry_temperature(self) -> float:
        return self._config_data.get("foundry_ai", {}).get("temperature", 0.7)
    
    @property
    def foundry_top_p(self) -> float:
        return self._config_data.get("foundry_ai", {}).get("top_p", 0.9)
    
    @property
    def foundry_top_k(self) -> int:
        return self._config_data.get("foundry_ai", {}).get("top_k", 40)
    
    @property
    def foundry_max_tokens(self) -> int:
        return self._config_data.get("foundry_ai", {}).get("max_tokens", 2048)
    
    @property
    def foundry_timeout(self) -> int:
        return self._config_data.get("foundry_ai", {}).get("timeout", 300)
    
    # RAG System настройки
    @property
    def rag_enabled(self) -> bool:
        return self._config_data.get("rag_system", {}).get("enabled", False)
    
    @property
    def rag_index_dir(self) -> str:
        return self._config_data.get("rag_system", {}).get("index_dir", "./rag_index")
    
    @property
    def rag_model(self) -> str:
        return self._config_data.get("rag_system", {}).get("model", "sentence-transformers/all-MiniLM-L6-v2")
    
    @property
    def rag_chunk_size(self) -> int:
        return self._config_data.get("rag_system", {}).get("chunk_size", 1000)
    
    @property
    def rag_top_k(self) -> int:
        return self._config_data.get("rag_system", {}).get("top_k", 5)
    
    # Security настройки
    @property
    def security_api_key(self) -> str:
        return self._config_data.get("security", {}).get("api_key", "")
    
    @property
    def security_https_enabled(self) -> bool:
        return self._config_data.get("security", {}).get("https_enabled", False)
    
    @property
    def security_cors_origins(self) -> list:
        return self._config_data.get("security", {}).get("cors_origins", ["*"])
    
    @property
    def security_ssl_cert_file(self) -> str:
        return self._config_data.get("security", {}).get("ssl_cert_file", "~/.ssl/cert.pem")
    
    @property
    def security_ssl_key_file(self) -> str:
        return self._config_data.get("security", {}).get("ssl_key_file", "~/.ssl/key.pem")
    
    # Logging настройки
    @property
    def logging_level(self) -> str:
        return self._config_data.get("logging", {}).get("level", "INFO")
    
    @property
    def logging_file(self) -> str:
        return self._config_data.get("logging", {}).get("file", "logs/fastapi-foundry.log")
    
    # MCP Server настройки
    @property
    def mcp_base_url(self) -> str:
        return self._config_data.get("mcp_server", {}).get("base_url", "http://localhost:50477/v1/")
    
    @property
    def mcp_default_model(self) -> str:
        return self._config_data.get("mcp_server", {}).get("default_model", "")
    
    @property
    def mcp_timeout(self) -> int:
        return self._config_data.get("mcp_server", {}).get("timeout", 30)
    
    # Docker настройки
    @property
    def docker_foundry_host(self) -> str:
        return self._config_data.get("docker", {}).get("foundry_host", "localhost")
    
    @property
    def docker_foundry_port(self) -> int:
        return self._config_data.get("docker", {}).get("foundry_port", 50477)
    
    @property
    def docker_rag_enabled(self) -> bool:
        return self._config_data.get("docker", {}).get("rag_enabled", True)
    
    # Методы для получения сырых данных
    def get_section(self, section: str) -> Dict[str, Any]:
        """Получить целую секцию конфигурации"""
        return self._config_data.get(section, {})
    
    def get_raw_config(self) -> Dict[str, Any]:
        """Получить всю конфигурацию"""
        return self._config_data.copy()
    
    def update_config(self, new_config: Dict[str, Any]):
        """Обновить конфигурацию и сохранить в файл"""
        self._config_data = new_config
        
        config_path = Path("config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=2, ensure_ascii=False)

# Глобальный экземпляр конфигурации
config = Config()