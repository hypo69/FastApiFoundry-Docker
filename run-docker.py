#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Docker лончер для FastAPI Foundry
# =============================================================================
# Описание:
#   Специализированный лончер для запуска в Docker контейнере
#   Автоматическое управление контейнерами, портами, логами
#
# Примеры:
#   python run-docker.py
#   python run-docker.py --port 8001 --build
#
# File: run-docker.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import argparse
import sys
import os
import time
import subprocess
from launcher_base import LauncherBase

class DockerLauncher(LauncherBase):
    """Лончер для Docker режима"""
    
    def run_normal_mode(self, **kwargs) -> bool:
        """В Docker лончере нет обычного режима"""
        self.log_error("Use run.py for normal mode")
        return False
    
    def run_docker_mode(self, **kwargs) -> bool:
        """Запуск в Docker режиме"""
        try:
            self.log_info("🐳 Starting FastAPI Foundry in Docker...")
            
            # Проверка Docker
            docker_ok, docker_version = self.check_docker()
            if not docker_ok:
                self.log_error(f"Docker недоступен: {docker_version}")
                return False
            
            self.log_success(f"Docker запущен (версия: {docker_version})")
            
            # Разрешение конфликтов портов
            port = kwargs.get('port', 8000)
            resolved_port = self.resolve_port_conflict(port)
            if resolved_port != port:
                self.log_info(f"🔄 Порт изменен на: {resolved_port}")
                port = resolved_port
            
            # Сборка образа если нужно
            if kwargs.get('build', False):
                self.log_info("🔨 Building Docker image...")
                subprocess.run(["docker-compose", "down"], cwd=self.project_root, timeout=30)
                result = subprocess.run(["docker-compose", "build"], cwd=self.project_root, timeout=300)
                if result.returncode != 0:
                    self.log_error("Ошибка сборки Docker образа")
                    return False
                self.log_success("Docker image built successfully")
            
            # Подготовка переменных окружения
            env_vars = {
                "PORT": str(port),
                "FOUNDRY_HOST": "localhost",
                "FOUNDRY_PORT": "50477",
                "RAG_ENABLED": "true"
            }
            
            # Обновление переменных окружения
            for key, value in env_vars.items():
                os.environ[key] = value
            
            # Остановка существующих контейнеров
            self.log_info("🛑 Stopping existing containers...")
            subprocess.run(["docker-compose", "down"], cwd=self.project_root, timeout=30)
            
            # Запуск контейнера
            self.log_info("🚀 Starting Docker container...")
            result = subprocess.run(["docker-compose", "up", "-d"], cwd=self.project_root, timeout=60)
            
            if result.returncode == 0:
                # Проверка статуса
                time.sleep(3)
                status_result = subprocess.run(
                    ["docker-compose", "ps", "-q"], 
                    cwd=self.project_root,
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                
                if status_result.stdout.strip():
                    self.log_success("FastAPI Foundry Docker container started!")
                    self.log_info(f"🌐 URL: http://localhost:{port}")
                    self.log_info(f"📚 API Docs: http://localhost:{port}/docs")
                    self.log_info(f"❤️ Health: http://localhost:{port}/api/v1/health")
                    self.log_info("")
                    self.log_info("Управление контейнером:")
                    self.log_info("  Логи: docker-compose logs -f")
                    self.log_info("  Остановка: docker-compose down")
                    self.log_info("  Перезапуск: docker-compose restart")
                    return True
                else:
                    self.log_warning("Контейнер запущен, но статус неизвестен")
                    self.log_info("Проверьте: docker-compose logs")
                    return False
            else:
                self.log_error("Ошибка запуска контейнера")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_error("Таймаут запуска контейнера")
            return False
        except Exception as e:
            self.log_error(f"Failed to start Docker container: {e}")
            return False

def parse_args():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description="FastAPI Foundry Docker Launcher")
    parser.add_argument('--port', type=int, default=8000, help='Host port for container')
    parser.add_argument('--build', action='store_true', help='Rebuild image before starting')
    parser.add_argument('--logs', action='store_true', help='Show logs after starting')
    parser.add_argument('--stop', action='store_true', help='Stop running containers')
    return parser.parse_args()

def main():
    """Главная функция"""
    args = parse_args()
    launcher = DockerLauncher()
    
    if args.stop:
        launcher.log_info("🛑 Stopping Docker containers...")
        result = subprocess.run(["docker-compose", "down"], cwd=launcher.project_root)
        if result.returncode == 0:
            launcher.log_success("Containers stopped")
        else:
            launcher.log_error("Failed to stop containers")
        return
    
    # Запуск в Docker режиме
    success = launcher.run(
        docker_mode=True,
        port=args.port,
        build=args.build
    )
    
    if success and args.logs:
        launcher.log_info("📋 Showing container logs...")
        subprocess.run(["docker-compose", "logs", "-f"], cwd=launcher.project_root)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()