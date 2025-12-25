#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Базовый класс для лончеров FastAPI Foundry
# =============================================================================
# Описание:
#   Общая функциональность для всех лончеров проекта
#   Управление портами, конфигурацией, процессами
#
# File: launcher_base.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import json
import os
import sys
import socket
import signal
import psutil
import subprocess
import time
import platform
from pathlib import Path
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

class LauncherBase(ABC):
    """Базовый класс для всех лончеров"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Инициализация лончера"""
        self.project_root = project_root or Path(__file__).parent
        self.config_file = self.project_root / "src" / "config.json"
        self.env_file = self.project_root / ".env"
        self.config = self.load_config()
        self.system = platform.system().lower()
        
    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из config.json"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.log_error(f"Config file not found: {self.config_file}")
                return self._get_default_config()
        except Exception as e:
            self.log_error(f"Failed to load config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Конфигурация по умолчанию"""
        return {
            "fastapi_server": {
                "host": "0.0.0.0",
                "port": 8000,
                "mode": "dev",
                "workers": 1,
                "reload": True
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
                "model": "sentence-transformers/all-MiniLM-L6-v2"
            },
            "security": {
                "api_key": "",
                "https_enabled": False
            },
            "logging": {
                "level": "INFO"
            }
        }
    
    def check_port(self, port: int) -> bool:
        """Проверка доступности порта"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(('127.0.0.1', port))
                return result != 0  # True если порт свободен
        except Exception:
            return False
    
    def kill_process_on_port(self, port: int) -> bool:
        """Завершение процесса на указанном порту"""
        try:
            self.log_info(f"Проверяем порт {port}...")
            
            if self.system == "windows":
                # Windows
                result = subprocess.run(
                    ["netstat", "-ano"], 
                    capture_output=True, 
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if f":{port}" in line and "LISTENING" in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                self.log_warning(f"Найден процесс PID {pid} на порту {port}, завершаем...")
                                
                                kill_result = subprocess.run(
                                    ["taskkill", "/PID", pid, "/F"], 
                                    capture_output=True, 
                                    text=True,
                                    timeout=5
                                )
                                
                                if kill_result.returncode == 0:
                                    self.log_info(f"✅ Процесс PID {pid} успешно завершен")
                                    return True
                                else:
                                    self.log_error(f"❌ Не удалось завершить PID {pid}")
            else:
                # Unix/Linux/macOS
                result = subprocess.run(
                    ["lsof", "-ti", f":{port}"], 
                    capture_output=True, 
                    text=True,
                    timeout=10
                )
                
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            self.log_warning(f"Найден процесс PID {pid} на порту {port}, завершаем...")
                            subprocess.run(["kill", "-9", pid], capture_output=True, timeout=5)
                            self.log_info(f"✅ Процесс PID {pid} завершен")
                            return True
                            
        except Exception as e:
            self.log_error(f"Ошибка при проверке порта {port}: {e}")
        
        if self.check_port(port):
            self.log_info(f"Порт {port} свободен")
        return False
    
    def find_free_port(self, start_port: int, max_attempts: int = 100) -> Optional[int]:
        """Поиск свободного порта"""
        for port in range(start_port, start_port + max_attempts):
            if self.check_port(port):
                return port
        return None
    
    def resolve_port_conflict(self, port: int, resolution: str = "kill_process") -> int:
        """Разрешение конфликтов портов"""
        if self.check_port(port):
            return port
            
        if resolution == "kill_process":
            if self.kill_process_on_port(port):
                time.sleep(1)  # Ждем освобождения порта
                if self.check_port(port):
                    return port
        elif resolution == "find_free_port":
            free_port = self.find_free_port(port + 1)
            if free_port:
                self.log_info(f"🔄 Найден свободный порт: {free_port}")
                return free_port
        
        return port
    
    def check_docker(self) -> tuple[bool, str]:
        """Проверка Docker"""
        try:
            result = subprocess.run(
                ["docker", "version", "--format", "{{.Server.Version}}"],
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, "Docker Engine недоступен"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, "Docker не установлен или не запущен"
    
    def build_env_vars(self, **kwargs) -> Dict[str, str]:
        """Построение переменных окружения"""
        env_vars = {}
        
        # FastAPI Server
        server_config = self.config.get('fastapi_server', {})
        env_vars.update({
            'FASTAPI_FOUNDRY_MODE': kwargs.get('mode', server_config.get('mode', 'dev')),
            'HOST': kwargs.get('host', server_config.get('host', '0.0.0.0')),
            'PORT': str(kwargs.get('port', server_config.get('port', 8000))),
            'API_WORKERS': str(kwargs.get('workers', server_config.get('workers', 1))),
            'API_RELOAD': str(kwargs.get('reload', server_config.get('reload', True))).lower(),
            'LOG_LEVEL': kwargs.get('log_level', self.config.get('logging', {}).get('level', 'INFO'))
        })
        
        # Foundry AI
        foundry_config = self.config.get('foundry_ai', {})
        env_vars.update({
            'FOUNDRY_BASE_URL': kwargs.get('foundry_url', foundry_config.get('base_url', 'http://localhost:50477/v1/')),
            'FOUNDRY_DEFAULT_MODEL': kwargs.get('model', foundry_config.get('default_model', 'deepseek-r1-distill-qwen-7b-generic-cpu:3')),
            'FOUNDRY_TEMPERATURE': str(kwargs.get('temperature', foundry_config.get('temperature', 0.6))),
            'FOUNDRY_TOP_P': str(kwargs.get('top_p', foundry_config.get('top_p', 0.9))),
            'FOUNDRY_TOP_K': str(kwargs.get('top_k', foundry_config.get('top_k', 40))),
            'FOUNDRY_MAX_TOKENS': str(kwargs.get('max_tokens', foundry_config.get('max_tokens', 2048))),
            'FOUNDRY_TIMEOUT': str(kwargs.get('timeout', foundry_config.get('timeout', 300)))
        })
        
        # RAG System
        rag_config = self.config.get('rag_system', {})
        env_vars.update({
            'RAG_ENABLED': str(kwargs.get('rag_enabled', rag_config.get('enabled', True))).lower(),
            'RAG_INDEX_DIR': kwargs.get('rag_dir', rag_config.get('index_dir', './rag_index')),
            'RAG_MODEL': kwargs.get('rag_model', rag_config.get('model', 'sentence-transformers/all-MiniLM-L6-v2'))
        })
        
        # Security
        if kwargs.get('api_key'):
            env_vars['API_KEY'] = kwargs['api_key']
        
        return env_vars
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None) -> subprocess.Popen:
        """Запуск команды"""
        return subprocess.Popen(
            command,
            cwd=cwd or self.project_root,
            env={**os.environ, **(env or {})},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    
    def validate_config(self, **kwargs) -> bool:
        """Валидация конфигурации"""
        # Проверка порта
        port = kwargs.get('port', self.config.get('fastapi_server', {}).get('port', 8000))
        try:
            port = int(port)
            if not (1 <= port <= 65535):
                self.log_error("Port must be between 1 and 65535")
                return False
        except ValueError:
            self.log_error("Port must be a valid number")
            return False
        
        # Проверка хоста
        host = kwargs.get('host', self.config.get('fastapi_server', {}).get('host', '0.0.0.0'))
        if not host or not host.strip():
            self.log_error("Host cannot be empty")
            return False
        
        return True
    
    # Методы логирования
    def log_info(self, message: str):
        """Информационное сообщение"""
        print(f"ℹ️  {message}")
    
    def log_warning(self, message: str):
        """Предупреждение"""
        print(f"⚠️  {message}")
    
    def log_error(self, message: str):
        """Ошибка"""
        print(f"❌ {message}")
    
    def log_success(self, message: str):
        """Успех"""
        print(f"✅ {message}")
    
    # Абстрактные методы
    @abstractmethod
    def run_normal_mode(self, **kwargs) -> bool:
        """Запуск в обычном режиме"""
        pass
    
    @abstractmethod
    def run_docker_mode(self, **kwargs) -> bool:
        """Запуск в Docker режиме"""
        pass
    
    def run(self, docker_mode: bool = False, **kwargs) -> bool:
        """Основной метод запуска"""
        if not self.validate_config(**kwargs):
            return False
        
        if docker_mode:
            return self.run_docker_mode(**kwargs)
        else:
            return self.run_normal_mode(**kwargs)