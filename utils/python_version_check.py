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
    
    # Docker использует Python 3.11
    docker_major = 3
    docker_minor = 11
    
    current_major = sys.version_info.major
    current_minor = sys.version_info.minor
    current_micro = sys.version_info.micro
    
    print(f"🐳 Docker использует: Python {docker_major}.{docker_minor}-slim")
    print(f"🐍 Локальная версия Python: {current_major}.{current_minor}.{current_micro}")
    print(f"📋 Для совместимости нужно: Python {docker_major}.{docker_minor}+")
    
    if current_major == docker_major and current_minor >= docker_minor:
        print("✅ Локальная версия совместима с Docker!")
        return True
    else:
        print("❌ Локальная версия НЕ совместима с Docker!")
        print(f"📥 Установите Python {docker_major}.{docker_minor}+ для совместимости")
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
        print("🎉 Локальная система совместима с Docker!")
        print("🖥️  Можно запускать GUI лончер")
    else:
        print("🐳 Используйте Docker для гарантированной совместимости")
    
    sys.exit(0 if compatible else 1)