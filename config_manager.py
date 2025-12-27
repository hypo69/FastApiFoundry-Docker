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
            raise FileNotFoundError(f"config.json not found at {config_path.absolute()}")
        
        print(f"Loading config from: {config_path.absolute()}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config_data = json.load(f)
            
        print(f"Config loaded with sections: {list(self._config_data.keys())}")
    
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
    
    @property
    def api_cors_origins(self) -> list:
        return self._config_data.get("fastapi_server", {}).get("cors_origins", ["*"])
    
    # Foundry AI настройки
    @property
    def foundry_base_url(self) -> str:
        # Проверяем переменную окружения сначала
        import os
        foundry_env_url = os.getenv('FOUNDRY_BASE_URL')
        if foundry_env_url:
            return foundry_env_url.rstrip('/') + '/'
        
        # Проверяем флаг динамического порта
        use_dynamic = self._config_data.get("foundry_ai", {}).get("use_dynamic_port", False)
        if use_dynamic:
            foundry_port = os.getenv('FOUNDRY_PORT', '50477')
            return f"http://localhost:{foundry_port}/v1/"
        
        # Используем статический URL из конфига
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
    def mcp_name(self) -> str:
        return self._config_data.get("mcp_server", {}).get("name", "aistros-foundry")
    
    @property
    def mcp_version(self) -> str:
        return self._config_data.get("mcp_server", {}).get("version", "1.0.0")
    
    @property
    def mcp_description(self) -> str:
        return self._config_data.get("mcp_server", {}).get("description", "")
    
    @property
    def mcp_author(self) -> str:
        return self._config_data.get("mcp_server", {}).get("author", "hypo69")
    
    @property
    def mcp_license(self) -> str:
        return self._config_data.get("mcp_server", {}).get("license", "CC BY-NC-SA 4.0")
    
    @property
    def mcp_homepage(self) -> str:
        return self._config_data.get("mcp_server", {}).get("homepage", "https://aistros.com")
    
    @property
    def mcp_version_spec(self) -> str:
        return self._config_data.get("mcp_server", {}).get("mcpVersion", "2024-11-05")
    
    @property
    def mcp_base_url(self) -> str:
        return self._config_data.get("mcp_server", {}).get("base_url", "http://localhost:51601/v1/")
    
    @property
    def mcp_default_model(self) -> str:
        return self._config_data.get("mcp_server", {}).get("default_model", "")
    
    @property
    def mcp_timeout(self) -> int:
        return self._config_data.get("mcp_server", {}).get("timeout", 30)
    
    @property
    def mcp_capabilities(self) -> dict:
        return self._config_data.get("mcp_server", {}).get("capabilities", {})
    
    # Web Interface настройки
    @property
    def web_api_base(self) -> str:
        return self._config_data.get("web_interface", {}).get("api_base", "http://localhost:8002/api/v1")
    
    @property
    def web_auto_refresh_interval(self) -> int:
        return self._config_data.get("web_interface", {}).get("auto_refresh_interval", 30000)
    
    @property
    def web_logs_refresh_interval(self) -> int:
        return self._config_data.get("web_interface", {}).get("logs_refresh_interval", 10000)
    
    @property
    def web_max_chat_history(self) -> int:
        return self._config_data.get("web_interface", {}).get("max_chat_history", 100)
    
    # Examples настройки
    @property
    def examples_client_demo_enabled(self) -> bool:
        return self._config_data.get("examples", {}).get("client_demo", {}).get("enabled", True)
    
    @property
    def examples_rag_demo_enabled(self) -> bool:
        return self._config_data.get("examples", {}).get("rag_demo", {}).get("enabled", True)
    
    @property
    def examples_mcp_demo_enabled(self) -> bool:
        return self._config_data.get("examples", {}).get("mcp_demo", {}).get("enabled", True)
    
    @property
    def examples_model_demo_enabled(self) -> bool:
        return self._config_data.get("examples", {}).get("model_demo", {}).get("enabled", True)
    
    # Docker настройки
    @property
    def docker_image(self) -> str:
        return self._config_data.get("docker", {}).get("image", "fastapi-foundry:0.2.1")
    
    @property
    def docker_container_name(self) -> str:
        return self._config_data.get("docker", {}).get("container_name", "fastapi-foundry-docker")
    
    @property
    def docker_network(self) -> str:
        return self._config_data.get("docker", {}).get("network", "fastapi-foundry-network")
    
    @property
    def docker_foundry_host(self) -> str:
        return self._config_data.get("docker", {}).get("foundry_host", "localhost")
    
    @property
    def docker_foundry_port(self) -> int:
        return self._config_data.get("docker", {}).get("foundry_port", 8008)
    
    @property
    def docker_rag_enabled(self) -> bool:
        return self._config_data.get("docker", {}).get("rag_enabled", True)
    
    @property
    def docker_healthcheck(self) -> dict:
        return self._config_data.get("docker", {}).get("healthcheck", {})
    
    @property
    def docker_volumes(self) -> list:
        return self._config_data.get("docker", {}).get("volumes", [])
    
    # Port Management настройки
    @property
    def port_conflict_resolution(self) -> str:
        return self._config_data.get("port_management", {}).get("conflict_resolution", "kill_process")
    
    @property
    def port_auto_find_free(self) -> bool:
        return self._config_data.get("port_management", {}).get("auto_find_free_port", False)
    
    @property
    def port_range_start(self) -> int:
        return self._config_data.get("port_management", {}).get("port_range_start", 8000)
    
    @property
    def port_range_end(self) -> int:
        return self._config_data.get("port_management", {}).get("port_range_end", 8100)
    
    @property
    def port_foundry_port(self) -> int:
        return self._config_data.get("port_management", {}).get("foundry_port", 50477)
    
    # Development настройки
    @property
    def dev_debug(self) -> bool:
        return self._config_data.get("development", {}).get("debug", False)
    
    @property
    def dev_verbose(self) -> bool:
        return self._config_data.get("development", {}).get("verbose", False)
    
    @property
    def dev_temp_dir(self) -> str:
        return self._config_data.get("development", {}).get("temp_dir", "./temp")
    
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