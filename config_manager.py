# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Единый класс конфигурации (Refactored)
# =============================================================================
# Описание:
#   Упрощенный класс Config для всего проекта FastApiFoundry
#   Загружает настройки из config.json и предоставляет единый интерфейс
#
# File: config_manager.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import json
from pathlib import Path
from typing import Dict, Any

class Config:
    """Единый класс конфигурации для всего проекта"""
    
    _instance = None
    _config_data = None
    _foundry_base_url = None  # Динамически устанавливается в run.py
    
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
        # Возвращаем только динамически установленный URL
        return self._foundry_base_url
    
    @foundry_base_url.setter
    def foundry_base_url(self, value: str):
        """Установить foundry_base_url динамически (используется в run.py)"""
        self._foundry_base_url = value
    
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
    def foundry_max_tokens(self) -> int:
        return self._config_data.get("foundry_ai", {}).get("max_tokens", 2048)
    
    # Port Management настройки
    @property
    def port_auto_find_free(self) -> bool:
        return self._config_data.get("port_management", {}).get("auto_find_free_port", False)
    
    @property
    def port_range_start(self) -> int:
        return self._config_data.get("port_management", {}).get("port_range_start", 8000)
    
    @property
    def port_range_end(self) -> int:
        return self._config_data.get("port_management", {}).get("port_range_end", 8100)
    
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
    
    # Методы для работы с конфигурацией
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