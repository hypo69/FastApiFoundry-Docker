#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import uvicorn
import webbrowser
import threading
import time
import os
import sys
import subprocess
import platform
from pathlib import Path

# Установить режим логирования
os.environ["FASTAPI_FOUNDRY_MODE"] = "dev"

# Настройка логирования
from src.logger import logger

def kill_process_on_port(port):
    """Завершить процесс на указанном порту"""
    system = platform.system().lower()
    logger.info(f"Проверяем порт {port}...")
    
    try:
        if system == "windows":
            # Найти процесс на порту
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
                            logger.warning(f"Найден процесс PID {pid} на порту {port}, завершаем...")
                            
                            kill_result = subprocess.run(
                                ["taskkill", "/PID", pid, "/F"], 
                                capture_output=True, 
                                text=True,
                                timeout=5
                            )
                            
                            if kill_result.returncode == 0:
                                logger.info(f"✅ Процесс PID {pid} успешно завершен")
                                return True
                            else:
                                logger.error(f"❌ Не удалось завершить PID {pid}: {kill_result.stderr.strip()}")
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
                        logger.warning(f"Найден процесс PID {pid} на порту {port}, завершаем...")
                        subprocess.run(["kill", "-9", pid], capture_output=True, timeout=5)
                        logger.info(f"✅ Процесс PID {pid} завершен")
                        return True
                        
    except Exception as e:
        logger.error(f"Ошибка при проверке порта {port}: {e}")
    
    logger.info(f"Порт {port} свободен")
    return False

def open_browser():
    """Открыть браузер через 3 секунды после запуска сервера"""
    try:
        time.sleep(3)
        url = "http://localhost:8002"
        logger.info(f"Opening browser: {url}")
        webbrowser.open(url)
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")

if __name__ == "__main__":
    try:
        logger.info("=" * 60)
        logger.info("Starting FastAPI Foundry Application")
        logger.info(f"Mode: {os.getenv('FASTAPI_FOUNDRY_MODE', 'dev')}")
        logger.info(f"Python: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info("=" * 60)
        
        # Создать директорию для логов
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        logger.info(f"Logs directory: {logs_dir.absolute()}")
        
        # Проверить и освободить порт
        port = 8002
        logger.info(f"Проверяем доступность порта {port}...")
        kill_process_on_port(port)
        
        # Подождать немного после завершения процесса
        time.sleep(1)
        # Проверить импорты
        logger.debug("Checking imports...")
        try:
            from src.api.main import app
            logger.info("✅ FastAPI app imported successfully")
        except Exception as e:
            logger.error(f"❌ Failed to import FastAPI app: {e}")
            raise
        
        # Запустить браузер в отдельном потоке
        logger.debug("Starting browser thread...")
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        logger.info("Browser thread started")
        
        # Запустить FastAPI сервер
        host = "0.0.0.0"
        port = 8002
        logger.info(f"Starting FastAPI server on http://{host}:{port}")
        logger.info(f"Web interface: http://localhost:{port}")
        logger.info(f"API docs: http://localhost:{port}/docs")
        
        uvicorn.run(
            "src.api.main:app",
            host=host, 
            port=port, 
            reload=False,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("Application stopped by user (Ctrl+C)")
        logger.info("=" * 60)
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Check if all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error(f"❌ Port 8002 is already in use")
            logger.error("Run 'python stop.py' to stop existing servers")
        else:
            logger.error(f"❌ OS error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Application failed to start: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)
    finally:
        logger.info("=" * 60)
        logger.info("Application shutdown complete")
        logger.info("=" * 60)