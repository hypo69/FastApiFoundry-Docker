#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Запуск FastApiFoundry сервера с embedded Python 3.11
# =============================================================================
# Описание:
#   Запуск FastAPI сервера используя embedded Python 3.11
#
# File: run_embedded.py
# Project: FastApiFoundry (Docker)
# Version: 0.1.0
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 27 декабря 2025
# =============================================================================

import sys
import os
import subprocess
import time
import json
import requests
from pathlib import Path

# Добавляем текущую директорию в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def check_dependencies():
    """Проверить и установить зависимости"""
    try:
        import uvicorn
        import fastapi
        import requests
        print("✅ Зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("🔧 Устанавливаю зависимости...")

        # Устанавливаем зависимости используя pip
        try:
            subprocess.check_call([
                os.path.join(current_dir, 'python-3.11.0-embed-amd64', 'python.exe'),
                '-m', 'pip', 'install', '-r', 'requirements.txt'
            ])
            print("✅ Зависимости установлены")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка установки зависимостей: {e}")
            return False

def check_foundry(base_url="http://localhost:50477/v1"):
    """Проверить Foundry сервер"""
    try:
        response = requests.get(f"{base_url}/models", timeout=5)
        if response.status_code == 200:
            models = len(response.json().get('data', []))
            return True, f"✅ Foundry работает, моделей: {models}"
        return False, f"❌ Foundry HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "❌ Foundry не запущен (порт 50477)"
    except Exception as e:
        return False, f"❌ Ошибка Foundry: {e}"

def try_start_foundry():
    """Попытаться запустить Foundry"""
    try:
        subprocess.Popen(['foundry'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time.sleep(3)
        return True
    except Exception:
        return False

def ensure_foundry(base_url="http://localhost:50477/v1"):
    """Проверить и запустить Foundry"""
    print("🔍 Проверяем Foundry...")

    for i in range(3):
        is_running, message = check_foundry(base_url)
        print(message)

        if is_running:
            return True

        if i < 2:
            print(f"🚀 Попытка {i+1}/3: запускаем Foundry...")
            if try_start_foundry():
                time.sleep(7)

    print("\n⚠️  Foundry не запущен. FastAPI запустится без AI функций.\n")
    return False

def main():
    """Главная функция"""
    print("🚀 FastAPI Foundry с embedded Python 3.11")
    print("=" * 50)

    # Проверяем зависимости
    if not check_dependencies():
        return False

    # Проверяем Foundry
    ensure_foundry()

    # Создаем логи
    Path("logs").mkdir(exist_ok=True)

    print("🌐 Запуск сервера на http://localhost:8000")
    print("📚 Документация: http://localhost:8000/docs")

    try:
        # Запускаем uvicorn с embedded Python
        python_exe = os.path.join(current_dir, 'python-3.11.0-embed-amd64', 'python.exe')

        subprocess.run([
            python_exe, '-m', 'uvicorn',
            'src.api.main:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload',
            '--log-level', 'info'
        ], check=True)

        return True

    except KeyboardInterrupt:
        print("\n✅ Остановлено пользователем")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)