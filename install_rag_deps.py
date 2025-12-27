# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: RAG Dependencies Installer
# =============================================================================
# Описание:
#   Установка зависимостей для RAG системы
#   sentence-transformers и faiss-cpu
#
# File: install_rag_deps.py
# Project: FastApiFoundry (Docker)
# Version: 0.3.3
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import subprocess
import sys
from pathlib import Path

def install_package(package_name):
    """Установить пакет через pip"""
    try:
        print(f"📦 Installing {package_name}...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package_name
        ], capture_output=True, text=True, check=True)
        
        print(f"✅ {package_name} installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}")
        print(f"Error: {e.stderr}")
        return False

def check_package(package_name):
    """Проверить установлен ли пакет"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def main():
    """Главная функция"""
    print("🚀 Installing RAG Dependencies for FastAPI Foundry")
    print("=" * 55)
    
    # Список необходимых пакетов
    packages = [
        "sentence-transformers",
        "faiss-cpu",
        "torch",  # Зависимость для sentence-transformers
        "transformers"  # Зависимость для sentence-transformers
    ]
    
    # Проверяем какие пакеты уже установлены
    installed = []
    to_install = []
    
    for package in packages:
        # Специальная проверка для faiss
        if package == "faiss-cpu":
            if check_package("faiss"):
                installed.append(package)
            else:
                to_install.append(package)
        else:
            if check_package(package.replace("-", "_")):
                installed.append(package)
            else:
                to_install.append(package)
    
    if installed:
        print("✅ Already installed:")
        for pkg in installed:
            print(f"   - {pkg}")
    
    if to_install:
        print(f"\n📦 Installing {len(to_install)} packages:")
        for pkg in to_install:
            print(f"   - {pkg}")
        
        print()
        success_count = 0
        for package in to_install:
            if install_package(package):
                success_count += 1
        
        print(f"\n📊 Installation Summary:")
        print(f"   ✅ Successful: {success_count}/{len(to_install)}")
        print(f"   ❌ Failed: {len(to_install) - success_count}/{len(to_install)}")
        
        if success_count == len(to_install):
            print("\n🎉 All RAG dependencies installed successfully!")
            print("\n📝 Next steps:")
            print("   1. Run: python create_rag_index.py")
            print("   2. Start server: python run.py")
            print("   3. Test RAG: http://localhost:8000/api/v1/rag/status")
        else:
            print("\n⚠️  Some packages failed to install. Check errors above.")
    else:
        print("\n🎉 All RAG dependencies are already installed!")
        print("\n📝 Next steps:")
        print("   1. Run: python create_rag_index.py (if not done)")
        print("   2. Start server: python run.py")
        print("   3. Test RAG: http://localhost:8000/api/v1/rag/status")

if __name__ == "__main__":
    main()