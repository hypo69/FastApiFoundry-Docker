# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Python Version Compatibility Check
# =============================================================================
# Описание:
#   Проверка совместимости версии Python с Docker образом
#   Минимальная версия: Python 3.11 (как в Dockerfile)
#
# File: python_version_check.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import sys
import platform

def check_python_compatibility():
    """Проверить совместимость версии Python"""
    
    # Минимальная версия (как в Docker)
    min_major = 3
    min_minor = 11
    
    current_major = sys.version_info.major
    current_minor = sys.version_info.minor
    current_micro = sys.version_info.micro
    
    print(f"🐍 Текущая версия Python: {current_major}.{current_minor}.{current_micro}")
    print(f"🐳 Docker использует: Python 3.11-slim")
    print(f"📋 Минимальная версия: {min_major}.{min_minor}")
    
    if current_major == min_major and current_minor >= min_minor:
        print("✅ Версия Python совместима!")
        return True
    else:
        print("❌ Версия Python НЕ совместима!")
        print(f"📥 Установите Python {min_major}.{min_minor}+ с https://www.python.org/downloads/")
        return False

def get_system_info():
    """Получить информацию о системе"""
    print("\n📊 Информация о системе:")
    print(f"   Платформа: {platform.system()} {platform.release()}")
    print(f"   Архитектура: {platform.machine()}")
    print(f"   Python путь: {sys.executable}")
    
    # Проверка виртуального окружения
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("   🔧 Виртуальное окружение: АКТИВНО")
    else:
        print("   ⚠️  Виртуальное окружение: НЕ АКТИВНО")

if __name__ == "__main__":
    print("🚀 FastAPI Foundry - Python Compatibility Check")
    print("=" * 50)
    
    compatible = check_python_compatibility()
    get_system_info()
    
    print("\n" + "=" * 50)
    if compatible:
        print("🎉 Система готова для запуска FastAPI Foundry!")
    else:
        print("🔧 Требуется обновление Python для совместимости с Docker")
    
    sys.exit(0 if compatible else 1)