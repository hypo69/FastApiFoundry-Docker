#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Docker Python Launcher для FastAPI Foundry
# =============================================================================
# Описание:
#   Лончер, который использует Python из Docker контейнера
#   Избегает конфликтов с локальным окружением
#
# File: docker-launcher.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import subprocess
import sys
import os
import time
from pathlib import Path
from src.utils.port_manager import ensure_port_free

class DockerPythonLauncher:
    """Лончер для запуска Python команд через Docker"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.image_name = "fastapi-foundry:0.2.1"
        
    def check_docker(self) -> bool:
        """Проверка Docker"""
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def build_image(self) -> bool:
        """Сборка Docker образа"""
        print("🐳 Сборка Docker образа...")
        try:
            result = subprocess.run([
                "docker", "build", "-t", self.image_name, "."
            ], cwd=self.project_root, timeout=300)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Ошибка сборки: {e}")
            return False
    
    def run_python_in_docker(self, script_path: str, *args) -> bool:
        """Запуск Python скрипта в Docker"""
        if not self.check_docker():
            print("❌ Docker не найден")
            return False
        
        # Проверяем наличие образа
        result = subprocess.run([
            "docker", "images", "-q", self.image_name
        ], capture_output=True, text=True)
        
        if not result.stdout.strip():
            print(f"📦 Образ {self.image_name} не найден, собираем...")
            if not self.build_image():
                return False
        
        # Запускаем контейнер
        cmd = [
            "docker", "run", "--rm", "-it",
            "-v", f"{self.project_root}:/app",
            "-p", "8000:8000",
            "-w", "/app",
            self.image_name,
            "python", script_path
        ] + list(args)
        
        print(f"🚀 Запуск: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd)
            return result.returncode == 0
        except KeyboardInterrupt:
            print("\n⏹️  Остановлено пользователем")
            return True
        except Exception as e:
            print(f"❌ Ошибка запуска: {e}")
            return False
    
    def run_fastapi(self):
        """Запуск FastAPI через Docker"""
        # Проверка и освобождение порта 8000
        if not ensure_port_free(8000):
            print("❌ Не удалось освободить порт 8000")
            return False
        print("✅ Порт 8000 свободен")
        
        return self.run_python_in_docker("run.py")
    
    def run_gui(self):
        """Запуск GUI (не поддерживается в Docker)"""
        print("❌ GUI не поддерживается в Docker режиме")
        print("💡 Используйте: python docker-launcher.py fastapi")
        return False
    
    def install_deps(self):
        """Установка зависимостей в Docker"""
        return self.run_python_in_docker("-m", "pip", "install", "-r", "requirements.txt")

def main():
    launcher = DockerPythonLauncher()
    
    if len(sys.argv) < 2:
        print("🐳 Docker Python Launcher для FastAPI Foundry")
        print()
        print("Использование:")
        print("  python docker-launcher.py fastapi    # Запуск FastAPI сервера")
        print("  python docker-launcher.py install    # Установка зависимостей")
        print("  python docker-launcher.py build      # Сборка Docker образа")
        print()
        return
    
    command = sys.argv[1].lower()
    
    if command == "fastapi":
        launcher.run_fastapi()
    elif command == "install":
        launcher.install_deps()
    elif command == "build":
        launcher.build_image()
    elif command == "gui":
        launcher.run_gui()
    else:
        print(f"❌ Неизвестная команда: {command}")

if __name__ == "__main__":
    main()