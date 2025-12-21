#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Проверка виртуального окружения в Docker
# =============================================================================
# Описание:
#   Скрипт для проверки что Docker использует правильный Python из venv
#   Выводит информацию о Python интерпретаторе и установленных пакетах
#
# Примеры:
#   python check_venv.py
#   docker run fastapi-foundry:0.2.1 python check_venv.py
#
# File: check_venv.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import sys
import os
import subprocess

def check_python_environment():
    """Проверить текущее Python окружение"""
    print("=" * 60)
    print("🐍 PYTHON ENVIRONMENT CHECK")
    print("=" * 60)
    
    # Python executable path
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path[0] if sys.path else 'N/A'}")
    
    # Virtual environment check
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        print(f"✅ Virtual environment: {venv_path}")
    else:
        print("❌ No virtual environment detected")
    
    # Check if we're in expected venv
    expected_venv = "/app/venv"
    if expected_venv in sys.executable:
        print(f"✅ Using expected venv: {expected_venv}")
    else:
        print(f"❌ Not using expected venv: {expected_venv}")
    
    # Environment variables
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print(f"PATH: {os.environ.get('PATH', 'Not set')[:100]}...")
    
    # Check pip location
    try:
        pip_result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                                  capture_output=True, text=True, timeout=10)
        if pip_result.returncode == 0:
            print(f"Pip version: {pip_result.stdout.strip()}")
        else:
            print(f"❌ Pip error: {pip_result.stderr}")
    except Exception as e:
        print(f"❌ Pip check failed: {e}")
    
    # Check key packages
    key_packages = ['fastapi', 'uvicorn', 'pydantic']
    print("\n📦 KEY PACKAGES:")
    for package in key_packages:
        try:
            __import__(package)
            print(f"✅ {package} - installed")
        except ImportError:
            print(f"❌ {package} - missing")
    
    print("=" * 60)

if __name__ == "__main__":
    check_python_environment()