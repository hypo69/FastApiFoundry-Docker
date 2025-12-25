# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Управление портами и процессами
# =============================================================================
# Описание:
#   Утилиты для проверки и освобождения портов перед запуском сервера
#
# Примеры:
#   >>> from src.utils.port_manager import kill_port_process
#   >>> kill_port_process(8000)
#
# File: port_manager.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import subprocess
import sys
import time
import os

def kill_port_process(port: int) -> bool:
    """Убивает процесс, занимающий указанный порт"""
    try:
        if sys.platform == "win32":
            # Windows
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True, capture_output=True, text=True
            )
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 5 and f':{port}' in parts[1]:
                        pid = parts[-1]
                        print(f"Убиваем процесс PID {pid} на порту {port}")
                        subprocess.run(f'taskkill /f /pid {pid}', shell=True)
                        time.sleep(1)
                        return True
        else:
            # Linux/macOS
            result = subprocess.run(
                f'lsof -ti:{port}',
                shell=True, capture_output=True, text=True
            )
            if result.stdout:
                pid = result.stdout.strip()
                print(f"Убиваем процесс PID {pid} на порту {port}")
                subprocess.run(f'kill -9 {pid}', shell=True)
                time.sleep(1)
                return True
        return False
    except Exception as e:
        print(f"Ошибка при освобождении порта {port}: {e}")
        return False

def is_port_free(port: int) -> bool:
    """Проверяет, свободен ли порт"""
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True, capture_output=True, text=True
            )
            return not result.stdout.strip()
        else:
            result = subprocess.run(
                f'lsof -ti:{port}',
                shell=True, capture_output=True, text=True
            )
            return not result.stdout.strip()
    except Exception:
        return True

def ensure_port_free(port: int) -> bool:
    """Гарантирует, что порт свободен"""
    if is_port_free(port):
        return True
    
    print(f"Порт {port} занят, освобождаем...")
    return kill_port_process(port)