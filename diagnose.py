#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Диагностика FastAPI Foundry
# =============================================================================
# Описание:
#   Проверка состояния системы и диагностика проблем
#
# File: diagnose.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import sys
import os
import json
import socket
import requests
import subprocess
from pathlib import Path

def check_python():
    """Проверка Python"""
    print("🐍 Python:")
    print(f"   Версия: {sys.version}")
    print(f"   Путь: {sys.executable}")
    print(f"   Платформа: {sys.platform}")

def check_dependencies():
    """Проверка зависимостей"""
    print("\n📦 Зависимости:")
    
    required = ['uvicorn', 'fastapi', 'requests']
    for package in required:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - НЕ УСТАНОВЛЕН")

def check_config():
    """Проверка конфигурации"""
    print("\n⚙️ Конфигурация:")
    
    config_path = Path("config.json")
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("   ✅ config.json найден и валиден")
            
            # Проверка основных секций
            if 'fastapi_server' in config:
                port = config['fastapi_server'].get('port', 9696)
                print(f"   📌 FastAPI порт: {port}")
            
            if 'foundry_ai' in config:
                foundry_url = config['foundry_ai'].get('base_url', 'N/A')
                print(f"   🤖 Foundry URL: {foundry_url}")
                
        except Exception as e:
            print(f"   ❌ Ошибка чтения config.json: {e}")
    else:
        print("   ⚠️ config.json не найден")

def check_ports():
    """Проверка портов"""
    print("\n🔌 Порты:")
    
    # Проверка FastAPI портов
    for port in [9696, 9697, 9698]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('localhost', port))
            if result == 0:
                print(f"   🔴 {port} - ЗАНЯТ")
            else:
                print(f"   ✅ {port} - свободен")
    
    # Проверка Foundry портов
    foundry_ports = [50477, 63157, 50478, 50479]
    for port in foundry_ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('localhost', port))
            if result == 0:
                print(f"   🤖 {port} - возможно Foundry")
                # Проверяем, действительно ли это Foundry
                try:
                    response = requests.get(f"http://localhost:{port}/v1/models", timeout=2)
                    if response.status_code == 200:
                        print(f"      ✅ Foundry API работает")
                    else:
                        print(f"      ⚠️ Порт занят, но не Foundry API")
                except:
                    print(f"      ⚠️ Порт занят, но HTTP недоступен")

def check_processes():
    """Проверка процессов"""
    print("\n🔄 Процессы:")
    
    try:
        # Поиск Foundry процессов
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq foundry.exe'], 
                              capture_output=True, text=True, shell=True)
        if 'foundry.exe' in result.stdout:
            print("   ✅ Foundry процесс найден")
        else:
            print("   ❌ Foundry процесс не найден")
            
        # Поиск Python процессов с uvicorn
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        if 'python.exe' in result.stdout:
            print("   🐍 Python процессы найдены")
        else:
            print("   ⚠️ Python процессы не найдены")
            
    except Exception as e:
        print(f"   ❌ Ошибка проверки процессов: {e}")

def check_files():
    """Проверка файлов"""
    print("\n📁 Файлы:")
    
    important_files = [
        'run.py',
        'config.json',
        'src/api/main.py',
        'src/api/app.py',
        'requirements.txt'
    ]
    
    for file_path in important_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - НЕ НАЙДЕН")

def check_environment():
    """Проверка переменных окружения"""
    print("\n🌍 Переменные окружения:")
    
    env_vars = ['FOUNDRY_BASE_URL', 'FOUNDRY_PORT']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var} = {value}")
        else:
            print(f"   ⚠️ {var} не установлена")

def main():
    """Основная функция диагностики"""
    print("🔍 FastAPI Foundry - Диагностика")
    print("=" * 50)
    
    check_python()
    check_dependencies()
    check_config()
    check_ports()
    check_processes()
    check_files()
    check_environment()
    
    print("\n" + "=" * 50)
    print("📋 Рекомендации:")
    print("   1. Если Foundry не найден: запустите 'foundry service start'")
    print("   2. Если порты заняты: используйте './stop.py' для очистки")
    print("   3. Если зависимости отсутствуют: 'pip install -r requirements.txt'")
    print("   4. Для запуска используйте: './start_simple.ps1'")

if __name__ == "__main__":
    main()