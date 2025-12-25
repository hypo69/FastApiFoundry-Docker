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
import psutil

def kill_port_process(port: int) -> bool:
    """Убивает процесс, занимающий указанный порт"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.info['connections'] or []:
                    if conn.laddr.port == port:
                        print(f"Убиваем процесс {proc.info['name']} (PID: {proc.info['pid']}) на порту {port}")
                        proc.kill()
                        time.sleep(1)
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    except Exception as e:
        print(f"Ошибка при освобождении порта {port}: {e}")
        return False

def is_port_free(port: int) -> bool:
    """Проверяет, свободен ли порт"""
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return False
        return True
    except Exception:
        return True

def ensure_port_free(port: int) -> bool:
    """Гарантирует, что порт свободен"""
    if is_port_free(port):
        return True
    
    print(f"Порт {port} занят, освобождаем...")
    return kill_port_process(port)