#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Запуск FastApiFoundry сервера
# =============================================================================
# Описание:
#   Основной скрипт запуска FastAPI сервера для Docker
#   Автоматическое освобождение портов, запуск браузера, логирование
#
# Примеры:
#   python run.py
#   python run.py --host 0.0.0.0 --port 8000
#
# File: run.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import uvicorn
import webbrowser
import threading
import time
import os
import sys
import ssl
import argparse
from pathlib import Path
from launcher_base import LauncherBase

# Установить режим логирования
os.environ["FASTAPI_FOUNDRY_MODE"] = os.getenv("FASTAPI_FOUNDRY_MODE", "dev")

# Настройка логирования
from src.logger import logger

class FastAPILauncher(LauncherBase):
    """Лончер для FastAPI сервера"""
    
    def __init__(self):
        super().__init__()
        self.logger = logger
    
    def log_info(self, message: str):
        self.logger.info(message)
    
    def log_warning(self, message: str):
        self.logger.warning(message)
    
    def log_error(self, message: str):
        self.logger.error(message)
    
    def log_success(self, message: str):
        self.logger.info(message)
    
    def open_browser(self, url: str, delay: int = 3):
        """Открыть браузер через указанное время"""
        def _open():
            try:
                time.sleep(delay)
                self.log_info(f"Opening browser: {url}")
                # Не открывать браузер в production режиме
                if os.getenv('FASTAPI_FOUNDRY_MODE') != 'production':
                    webbrowser.open(url)
            except Exception as e:
                self.log_error(f"Failed to open browser: {e}")
        
        thread = threading.Thread(target=_open)
        thread.daemon = True
        thread.start()
    
    def run_normal_mode(self, **kwargs) -> bool:
        """Запуск в обычном режиме"""
        try:
            # Разрешение конфликтов портов
            port = int(kwargs.get('port', self.config['fastapi_server']['port']))
            host = kwargs.get('host', self.config['fastapi_server']['host'])
            
            resolved_port = self.resolve_port_conflict(port)
            if resolved_port != port:
                kwargs['port'] = resolved_port
                port = resolved_port
            
            # Построение переменных окружения
            env_vars = self.build_env_vars(**kwargs)
            
            # Обновление переменных окружения
            for key, value in env_vars.items():
                os.environ[key] = value
            
            self.log_info("=" * 60)
            self.log_info("Starting FastAPI Foundry Application")
            self.log_info(f"Mode: {env_vars.get('FASTAPI_FOUNDRY_MODE', 'dev')}")
            self.log_info(f"Python: {sys.version}")
            self.log_info(f"Working directory: {os.getcwd()}")
            self.log_info("=" * 60)
            
            # Создать директорию для логов
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            self.log_info(f"Logs directory: {logs_dir.absolute()}")
            
            self.log_info(f"Проверяем доступность порта {port}...")
            self.kill_process_on_port(port)
            
            # Подождать немного после завершения процесса
            time.sleep(1)
            
            # Предварительная проверка импорта (закомментировано - uvicorn сам проверит)
            # try:
            #     from src.api.main import app
            # except Exception as e:
            #     self.log_error(f"Failed to import FastAPI app: {e}")
            #     return False
            
            # Запустить браузер в отдельном потоке (только в dev режиме)
            if env_vars.get('FASTAPI_FOUNDRY_MODE') != 'production':
                self.open_browser(f"http://localhost:{port}")
            
            self.log_info(f"Starting FastAPI server on http://{host}:{port}")
            self.log_info(f"Web interface: http://localhost:{port}")
            self.log_info(f"API docs: http://localhost:{port}/docs")
            
            # Проверка SSL сертификатов
            ssl_dir = Path.home() / ".ssl"
            cert_file = ssl_dir / "cert.pem"
            key_file = ssl_dir / "key.pem"
            
            if not (cert_file.exists() and key_file.exists()):
                self.log_warning("⚠️  SSL сертификаты не найдены")
                self.log_info("🔒 Для HTTPS поддержки запустите: .\\ssl-generator.ps1")
            else:
                self.log_info(f"✅ SSL сертификаты: {ssl_dir}")
            
            # Настройка SSL контекста для HTTPS
            ssl_context = None
            # Временно отключаем HTTPS для отладки
            # if settings.https_enabled:
            #     try:
            #         cert_file = Path(settings.ssl_cert_file).expanduser()
            #         key_file = Path(settings.ssl_key_file).expanduser()
            #         
            #         if cert_file.exists() and key_file.exists():
            #             ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            #             ssl_context.load_cert_chain(str(cert_file), str(key_file))
            #             logger.info("✅ HTTPS включен с SSL сертификатами")
            #         else:
            #             logger.warning("⚠️ HTTPS включен, но SSL сертификаты не найдены")
            #             logger.info("🔒 Сгенерируйте сертификаты: .\\ssl-generator.ps1")
            #     except Exception as e:
            #         logger.error(f"❌ Ошибка настройки HTTPS: {e}")
            #         logger.info("🔒 Сгенерируйте сертификаты: .\\ssl-generator.ps1")
            
            uvicorn.run(
                "src.api.main:app",
                host=host, 
                port=port, 
                reload=kwargs.get('reload', False),
                log_level=kwargs.get('log_level', 'info').lower(),
                access_log=True
            )
            
            return True
            
        except KeyboardInterrupt:
            self.log_info("\n" + "=" * 60)
            self.log_info("Application stopped by user (Ctrl+C)")
            self.log_info("=" * 60)
            return True
        except ImportError as e:
            self.log_error(f"Import error: {e}")
            self.log_error("Check if all dependencies are installed: pip install -r requirements.txt")
            return False
        except OSError as e:
            if "Address already in use" in str(e):
                self.log_error(f"Port {port} is already in use")
                self.log_error("Run 'python stop.py' to stop existing servers")
            else:
                self.log_error(f"OS error: {e}")
            return False
        except Exception as e:
            self.log_error(f"Application failed to start: {e}")
            return False
        finally:
            self.log_info("=" * 60)
            self.log_info("Application shutdown complete")
            self.log_info("=" * 60)
    
    def run_docker_mode(self, **kwargs) -> bool:
        """Запуск в Docker режиме"""
        self.log_error("Docker mode not supported in run.py")
        self.log_info("Use run-gui.py for Docker mode or docker-compose directly")
        return False

def parse_args():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description="FastAPI Foundry Server")
    parser.add_argument('--host', default=None, help='Host to bind to')
    parser.add_argument('--port', type=int, default=None, help='Port to bind to')
    parser.add_argument('--mode', choices=['dev', 'production'], default=None, help='Run mode')
    parser.add_argument('--workers', type=int, default=None, help='Number of workers')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--no-reload', action='store_true', help='Disable auto-reload')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default=None, help='Log level')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Подготовка параметров
    kwargs = {}
    if args.host:
        kwargs['host'] = args.host
    if args.port:
        kwargs['port'] = args.port
    if args.mode:
        kwargs['mode'] = args.mode
    if args.workers:
        kwargs['workers'] = args.workers
    if args.reload:
        kwargs['reload'] = True
    elif args.no_reload:
        kwargs['reload'] = False
    if args.log_level:
        kwargs['log_level'] = args.log_level
    
    # Запуск лончера
    launcher = FastAPILauncher()
    success = launcher.run(docker_mode=False, **kwargs)
    sys.exit(0 if success else 1)