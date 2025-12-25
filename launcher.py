#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Универсальный лончер FastAPI Foundry
# =============================================================================
# Описание:
#   Единый лончер для всех режимов запуска FastAPI Foundry
#   Поддержка CLI, GUI, Docker, обычного режима
#
# Примеры:
#   python launcher.py                    # GUI режим
#   python launcher.py --cli              # CLI режим
#   python launcher.py --docker           # Docker режим
#   python launcher.py --docker --build   # Docker с пересборкой
#
# File: launcher.py
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
import subprocess
import webbrowser
import time
from pathlib import Path
from launcher_base import LauncherBase

class UniversalLauncher(LauncherBase):
    """Универсальный лончер для всех режимов"""
    
    def run_normal_mode(self, **kwargs) -> bool:
        """Запуск в обычном режиме"""
        try:
            # Построение команды
            cmd = ["python", "run.py"]
            
            # Добавление аргументов
            if kwargs.get('host'):
                cmd.extend(['--host', kwargs['host']])
            if kwargs.get('port'):
                cmd.extend(['--port', str(kwargs['port'])])
            if kwargs.get('mode'):
                cmd.extend(['--mode', kwargs['mode']])
            if kwargs.get('workers'):
                cmd.extend(['--workers', str(kwargs['workers'])])
            if kwargs.get('reload'):
                cmd.append('--reload')
            if kwargs.get('log_level'):
                cmd.extend(['--log-level', kwargs['log_level']])
            
            # Построение переменных окружения
            env_vars = self.build_env_vars(**kwargs)
            
            self.log_info("🚀 Starting FastAPI Foundry (Normal Mode)")
            self.log_info(f"Command: {' '.join(cmd)}")
            
            # Запуск
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                env={**os.environ, **env_vars}
            )
            
            # Открытие браузера
            if kwargs.get('open_browser', True) and kwargs.get('mode', 'dev') != 'production':
                port = kwargs.get('port', self.config['fastapi_server']['port'])
                time.sleep(3)
                webbrowser.open(f"http://localhost:{port}")
            
            return True
            
        except Exception as e:
            self.log_error(f"Failed to start in normal mode: {e}")
            return False

class DockerLauncher(LauncherBase):
    """Лончер для Docker режима"""
    
    def run_normal_mode(self, **kwargs) -> bool:
        """Не поддерживается в Docker лончере"""
        return False
    
    def run_docker_mode(self, **kwargs) -> bool:
        """Запуск в Docker режиме"""
        universal = UniversalLauncher()
        return universal.run_docker_mode(**kwargs)
    
    def run_docker_mode(self, **kwargs) -> bool:
        """Запуск в Docker режиме"""
        try:
            self.log_info("🐳 Starting FastAPI Foundry (Docker Mode)")
            
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
                "RAG_ENABLED": str(kwargs.get('rag_enabled', True)).lower()
            }
            
            if kwargs.get('api_key'):
                env_vars["API_KEY"] = kwargs['api_key']
            
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
                    
                    # Открытие браузера
                    if kwargs.get('open_browser', True):
                        time.sleep(2)
                        webbrowser.open(f"http://localhost:{port}")
                    
                    return True
                else:
                    self.log_warning("Контейнер запущен, но статус неизвестен")
                    return False
            else:
                self.log_error("Ошибка запуска контейнера")
                return False
                
        except Exception as e:
            self.log_error(f"Failed to start Docker container: {e}")
            return False
    
    def stop_containers(self) -> bool:
        """Остановка контейнеров"""
        try:
            self.log_info("🛑 Stopping Docker containers...")
            result = subprocess.run(["docker-compose", "down"], cwd=self.project_root, timeout=30)
            if result.returncode == 0:
                self.log_success("Containers stopped")
                return True
            else:
                self.log_error("Failed to stop containers")
                return False
        except Exception as e:
            self.log_error(f"Error stopping containers: {e}")
            return False
    
    def show_logs(self, follow: bool = True):
        """Показать логи контейнера"""
        try:
            cmd = ["docker-compose", "logs"]
            if follow:
                cmd.append("-f")
            
            self.log_info("📋 Showing container logs...")
            subprocess.run(cmd, cwd=self.project_root)
        except Exception as e:
            self.log_error(f"Error showing logs: {e}")
    
    def container_status(self):
        """Статус контейнера"""
        try:
            result = subprocess.run(
                ["docker-compose", "ps"], 
                cwd=self.project_root,
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                self.log_info("📊 Container Status:")
                print(result.stdout)
            else:
                self.log_error("Failed to get container status")
        except Exception as e:
            self.log_error(f"Error getting container status: {e}")

def parse_args():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description="FastAPI Foundry Universal Launcher")
    
    # Режимы запуска
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--gui', action='store_true', help='Launch GUI (default)')
    mode_group.add_argument('--cli', action='store_true', help='Launch CLI mode')
    mode_group.add_argument('--docker', action='store_true', help='Launch Docker mode')
    
    # Параметры
    parser.add_argument('--port', type=int, default=8000, help='Port to use')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--mode', choices=['dev', 'production'], default='dev', help='Run mode')
    parser.add_argument('--workers', type=int, default=1, help='Number of workers')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO', help='Log level')
    
    # Docker специфичные
    parser.add_argument('--build', action='store_true', help='Rebuild Docker image')
    parser.add_argument('--logs', action='store_true', help='Show logs after starting')
    parser.add_argument('--stop', action='store_true', help='Stop running containers')
    parser.add_argument('--status', action='store_true', help='Show container status')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser')
    
    return parser.parse_args()

def main():
    """Главная функция"""
    args = parse_args()
    launcher = UniversalLauncher()
    
    # Специальные команды
    if args.stop:
        launcher.stop_containers()
        return
    
    if args.status:
        launcher.container_status()
        return
    
    # Определение режима запуска
    if args.docker:
        # Docker режим
        success = launcher.run(
            docker_mode=True,
            port=args.port,
            build=args.build,
            open_browser=not args.no_browser
        )
        
        if success and args.logs:
            launcher.show_logs()
            
    elif args.cli:
        # CLI режим (обычный запуск)
        success = launcher.run(
            docker_mode=False,
            host=args.host,
            port=args.port,
            mode=args.mode,
            workers=args.workers,
            reload=args.reload,
            log_level=args.log_level,
            open_browser=not args.no_browser
        )
    else:
        # GUI режим (по умолчанию)
        try:
            from run_gui import FastApiFoundryGUILauncher
            gui_launcher = FastApiFoundryGUILauncher()
            gui_launcher.run()
            return
        except ImportError:
            launcher.log_error("GUI mode not available, falling back to CLI")
            success = launcher.run(
                docker_mode=False,
                host=args.host,
                port=args.port,
                mode=args.mode,
                workers=args.workers,
                reload=args.reload,
                log_level=args.log_level,
                open_browser=not args.no_browser
            )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()