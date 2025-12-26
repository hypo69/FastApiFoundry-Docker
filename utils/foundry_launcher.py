#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Foundry Launcher Utility
# =============================================================================
# Описание:
#   Утилита для запуска и управления Foundry сервисом
#   Автоматическая установка и настройка Foundry
#
# Примеры:
#   python utils/foundry_launcher.py --start
#   python utils/foundry_launcher.py --stop
#   python utils/foundry_launcher.py --status
#
# File: foundry_launcher.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import os
import sys
import subprocess
import time
import argparse
import requests
from pathlib import Path

def check_foundry_installed():
    """Проверить, установлен ли Foundry"""
    try:
        result = subprocess.run(['foundry', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def install_foundry():
    """Установить Foundry"""
    print("🔧 Foundry не найден. Попытка установки...")
    
    # Для Windows - скачать и установить
    if os.name == 'nt':
        print("📥 Скачивание Foundry для Windows...")
        # Здесь должна быть логика установки для Windows
        print("❌ Автоматическая установка для Windows не реализована")
        print("📖 Установите Foundry вручную: https://github.com/foundry-rs/foundry")
        return False
    else:
        # Для Linux/macOS
        try:
            print("📥 Установка Foundry через curl...")
            subprocess.run(['curl', '-L', 'https://foundry.paradigm.xyz', '|', 'bash'], 
                         shell=True, check=True)
            subprocess.run(['foundryup'], check=True)
            return True
        except subprocess.CalledProcessError:
            print("❌ Ошибка установки Foundry")
            return False

def start_foundry(port=50477):
    """Запустить Foundry сервис"""
    if not check_foundry_installed():
        if not install_foundry():
            return False
    
    print(f"🚀 Запуск Foundry на порту {port}...")
    
    try:
        # Запуск в фоновом режиме
        process = subprocess.Popen(
            ['foundry', '--port', str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        
        # Ждем запуска
        print("⏳ Ожидание запуска сервиса...")
        time.sleep(3)
        
        # Проверяем статус
        if check_foundry_status(port):
            print(f"✅ Foundry успешно запущен на порту {port}")
            return True
        else:
            print("❌ Foundry запущен, но не отвечает на запросы")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запуска Foundry: {e}")
        return False

def stop_foundry():
    """Остановить Foundry сервис"""
    print("🛑 Остановка Foundry...")
    
    try:
        if os.name == 'nt':
            # Windows
            subprocess.run(['taskkill', '/f', '/im', 'foundry.exe'], 
                         capture_output=True)
        else:
            # Linux/macOS
            subprocess.run(['pkill', '-f', 'foundry'], 
                         capture_output=True)
        
        print("✅ Foundry остановлен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка остановки Foundry: {e}")
        return False

def check_foundry_status(port=50477):
    """Проверить статус Foundry"""
    try:
        response = requests.get(f'http://localhost:{port}/v1/models', timeout=5)
        if response.status_code == 200:
            models = response.json().get('data', [])
            print(f"✅ Foundry работает на порту {port}")
            print(f"📊 Доступно моделей: {len(models)}")
            for model in models[:3]:  # Показать первые 3 модели
                print(f"   - {model.get('id', 'unknown')}")
            return True
        else:
            print(f"⚠️ Foundry отвечает с кодом {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Foundry не отвечает на порту {port}")
        return False
    except Exception as e:
        print(f"❌ Ошибка проверки статуса: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Foundry Launcher Utility')
    parser.add_argument('--start', action='store_true', help='Запустить Foundry')
    parser.add_argument('--stop', action='store_true', help='Остановить Foundry')
    parser.add_argument('--status', action='store_true', help='Проверить статус')
    parser.add_argument('--port', type=int, default=50477, help='Порт для Foundry')
    
    args = parser.parse_args()
    
    if args.start:
        start_foundry(args.port)
    elif args.stop:
        stop_foundry()
    elif args.status:
        check_foundry_status(args.port)
    else:
        print("🤖 Foundry Launcher Utility")
        print("Использование:")
        print("  python utils/foundry_launcher.py --start   # Запустить")
        print("  python utils/foundry_launcher.py --stop    # Остановить")
        print("  python utils/foundry_launcher.py --status  # Статус")

if __name__ == "__main__":
    main()