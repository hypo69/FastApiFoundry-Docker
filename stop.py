# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Остановка FastAPI Foundry серверов с логированием
# =============================================================================
# Описание:
#   Скрипт для завершения всех процессов FastAPI Foundry на портах 8000-8010
#   С подробным логированием для отладки ошибок
#
# File: stop.py
# Project: FastAPI Foundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import os
import sys
import subprocess
import argparse
import platform
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stop.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def kill_processes_on_ports(ports):
    """Завершить процессы на указанных портах"""
    logger.info(f"Начинаем поиск процессов на портах: {ports}")
    system = platform.system().lower()
    killed_count = 0
    
    for port in ports:
        logger.info(f"Проверяем порт {port}")
        
        if system == "windows":
            try:
                logger.debug("Выполняем netstat -ano")
                result = subprocess.run(
                    ["netstat", "-ano"], 
                    capture_output=True, 
                    text=True,
                    timeout=10
                )
                
                logger.debug(f"netstat return code: {result.returncode}")
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if f":{port}" in line and "LISTENING" in line:
                            parts = line.split()
                            logger.debug(f"Найдена строка: {line.strip()}")
                            logger.debug(f"Части строки: {parts}")
                            
                            if len(parts) >= 5:
                                pid = parts[-1]
                                logger.info(f"Найден процесс PID {pid} на порту {port}")
                                
                                try:
                                    kill_result = subprocess.run(
                                        ["taskkill", "/PID", pid, "/F"], 
                                        capture_output=True, 
                                        text=True,
                                        timeout=5
                                    )
                                    
                                    logger.debug(f"taskkill return code: {kill_result.returncode}")
                                    logger.debug(f"taskkill stdout: {kill_result.stdout}")
                                    logger.debug(f"taskkill stderr: {kill_result.stderr}")
                                    
                                    if kill_result.returncode == 0:
                                        logger.info(f"✅ Успешно завершен процесс PID {pid}")
                                        killed_count += 1
                                    else:
                                        logger.warning(f"❌ Не удалось завершить PID {pid}: {kill_result.stderr.strip()}")
                                        
                                except subprocess.TimeoutExpired:
                                    logger.error(f"Timeout при завершении PID {pid}")
                                except Exception as e:
                                    logger.error(f"Ошибка при завершении PID {pid}: {e}")
                else:
                    logger.error(f"netstat завершился с кодом {result.returncode}: {result.stderr}")
                            
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout при выполнении netstat для порта {port}")
            except Exception as e:
                logger.error(f"Ошибка при проверке порта {port}: {e}")
        
        else:  # Unix/Linux/macOS
            try:
                logger.debug(f"Выполняем lsof -ti :{port}")
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
                            logger.info(f"Найден процесс PID {pid} на порту {port}")
                            try:
                                subprocess.run(["kill", "-9", pid], 
                                             capture_output=True, timeout=5)
                                logger.info(f"✅ Завершен процесс PID {pid}")
                                killed_count += 1
                            except Exception as e:
                                logger.error(f"Ошибка при завершении PID {pid}: {e}")
                                
            except Exception as e:
                logger.error(f"Ошибка при проверке порта {port}: {e}")
    
    logger.info(f"Всего завершено процессов: {killed_count}")
    return killed_count

def main():
    logger.info("=" * 50)
    logger.info("🛑 Запуск скрипта остановки FastAPI Foundry")
    logger.info(f"Система: {platform.system()} {platform.release()}")
    logger.info(f"Python: {sys.version}")
    logger.info("=" * 50)
    
    parser = argparse.ArgumentParser(description="Остановка FastAPI Foundry серверов")
    parser.add_argument("--ports", default="8000,8001,8002,8003,8004,8005",
                       help="Порты для проверки (через запятую)")
    parser.add_argument("--debug", action="store_true",
                       help="Включить отладочные сообщения")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Включен режим отладки")
    
    try:
        ports = [int(p.strip()) for p in args.ports.split(",")]
        logger.info(f"Порты для проверки: {ports}")
    except ValueError as e:
        logger.error(f"Ошибка в формате портов: {e}")
        return 1
    
    try:
        killed_count = kill_processes_on_ports(ports)
        
        logger.info("=" * 50)
        logger.info(f"✅ Завершено процессов: {killed_count}")
        logger.info("🔍 Проверяем результат...")
        
        # Проверка результата
        for port in ports[:3]:
            try:
                if platform.system().lower() == "windows":
                    result = subprocess.run(["netstat", "-an"], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        if f":{port}" in result.stdout and "LISTENING" in result.stdout:
                            logger.warning(f"❌ Порт {port} все еще занят")
                        else:
                            logger.info(f"✅ Порт {port} свободен")
                    else:
                        logger.error(f"Ошибка проверки порта {port}")
                        
            except Exception as e:
                logger.error(f"Ошибка при проверке порта {port}: {e}")
        
        logger.info("=" * 50)
        logger.info("🏁 Скрипт завершен")
        return 0
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)