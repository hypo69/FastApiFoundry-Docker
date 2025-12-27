#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для установки зависимостей в venv
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package_name):
    """Установить пакет через pip"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package_name
        ], capture_output=True, text=True, check=True)
        print(f"✅ {package_name} установлен успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки {package_name}: {e}")
        return False

def main():
    print("🔧 Установка зависимостей...")
    
    # Основные зависимости
    packages = [
        "fastapi",
        "uvicorn[standard]", 
        "requests",
        "aiohttp",
        "python-dotenv"
    ]
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Установлено {success_count}/{len(packages)} пакетов")
    
    # Проверка импортов
    print("\n🧪 Проверка импортов...")
    try:
        import fastapi
        print("✅ fastapi")
    except ImportError:
        print("❌ fastapi")
    
    try:
        import uvicorn
        print("✅ uvicorn")
    except ImportError:
        print("❌ uvicorn")
    
    try:
        import requests
        print("✅ requests")
    except ImportError:
        print("❌ requests")
    
    try:
        import aiohttp
        print("✅ aiohttp")
    except ImportError:
        print("❌ aiohttp")

if __name__ == "__main__":
    main()