#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматический установщик FastAPI Foundry
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_git():
    """Проверить и установить Git"""
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True)
        print(f"✅ Git уже установлен: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Git не установлен")
        print("\nGit нужен для клонирования репозиториев")
        
        install = input("Установить Git? (y/n): ").lower()
        if install == 'y':
            if sys.platform == "win32":
                print("Открываю страницу загрузки Git...")
                import webbrowser
                webbrowser.open("https://git-scm.com/download/win")
                print("Установите Git и перезапустите этот скрипт")
                return False
            elif sys.platform == "darwin":
                print("Установите Git через Homebrew: brew install git")
                return False
            else:
                print("Установите Git через пакетный менеджер:")
                print("  Ubuntu/Debian: sudo apt install git")
                print("  CentOS/RHEL: sudo yum install git")
                return False
        return True

def check_docker():
    """Проверить и установить Docker"""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True, check=True)
        print(f"✅ Docker уже установлен: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Docker не установлен")
        print("\nDocker нужен для контейнеризации (опционально)")
        
        install = input("Установить Docker? (y/n): ").lower()
        if install == 'y':
            if sys.platform == "win32":
                print("Открываю страницу загрузки Docker Desktop...")
                import webbrowser
                webbrowser.open("https://www.docker.com/products/docker-desktop/")
                print("Установите Docker Desktop и перезагрузите компьютер")
                return False
            elif sys.platform == "darwin":
                print("Установите Docker Desktop с https://www.docker.com/products/docker-desktop/")
                return False
            else:
                print("Установите Docker через пакетный менеджер:")
                print("  Ubuntu: sudo apt install docker.io")
                print("  CentOS: sudo yum install docker")
                return False
        return True

def run_command(cmd, description, show_output=False):
    """Выполнить команду с описанием"""
    print(f"🔄 {description}...")
    try:
        if show_output:
            # Показывать вывод в реальном времени
            result = subprocess.run(cmd, shell=True, check=True)
        else:
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ошибка: {e}")
        return False

def main():
    """Главная функция установки"""
    print("🚀 FastAPI Foundry - Автоматическая установка")
    print("=" * 50)
    
    # Проверка Python версии
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} - OK")
    
    # Проверка Git
    if not check_git():
        print("⚠️  Git не установлен, но продолжаем...")
    
    # Проверка Docker
    if not check_docker():
        print("⚠️  Docker не установлен, но продолжаем...")
    
    # Создание виртуального окружения
    if not Path("venv").exists():
        if not run_command(f"{sys.executable} -m venv venv", "Создание виртуального окружения"):
            sys.exit(1)
    else:
        print("✅ Виртуальное окружение уже существует")
    
    # Определение команды активации
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:  # Linux/Mac
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Обновление pip
    run_command(f"{python_cmd} -m pip install --upgrade pip", "Обновление pip")
    
    # Установка зависимостей
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Установка зависимостей", show_output=True):
        print("⚠️ Ошибка установки зависимостей. Попробуйте установить вручную:")
        print(f"  {pip_cmd} install -r requirements.txt")
    
    # Создание директорий
    directories = ["logs", "rag_index"]
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Директория {dir_name} создана")
    
    # Копирование .env файла
    if not Path(".env").exists():
        if Path(".env.example").exists():
            shutil.copy(".env.example", ".env")
            print("✅ Файл .env создан из .env.example")
        else:
            # Создание базового .env файла
            env_content = """# FastAPI Foundry Configuration
FOUNDRY_BASE_URL=http://localhost:55581/v1/
FOUNDRY_DEFAULT_MODEL=deepseek-r1-distill-qwen-7b-generic-cpu:3
FOUNDRY_TEMPERATURE=0.6
FOUNDRY_MAX_TOKENS=2048

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=

# RAG Settings
RAG_ENABLED=true
RAG_INDEX_DIR=./rag_index

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/fastapi-foundry.log
"""
            with open(".env", "w", encoding="utf-8") as f:
                f.write(env_content)
            print("✅ Базовый файл .env создан")
    else:
        print("✅ Файл .env уже существует")

    # Тестирование установки
    print("\n🧪 Тестирование установки...")
    test_passed = 0
    test_failed = 0

    # Test Python
    try:
        result = subprocess.run(f"{python_cmd} --version", shell=True, capture_output=True, text=True, check=True)
        print(f"  ✅ Python: {result.stdout.strip()}")
        test_passed += 1
    except subprocess.CalledProcessError:
        print("  ❌ Python: не найден в venv")
        test_failed += 1

    # Test FastAPI
    try:
        result = subprocess.run(f'{python_cmd} -c "import fastapi; print(fastapi.__version__)"', shell=True, capture_output=True, text=True, check=True)
        print(f"  ✅ FastAPI: версия {result.stdout.strip()}")
        test_passed += 1
    except subprocess.CalledProcessError:
        print("  ❌ FastAPI: не установлен")
        test_failed += 1

    # Test uvicorn
    try:
        result = subprocess.run(f'{python_cmd} -c "import uvicorn; print(uvicorn.__version__)"', shell=True, capture_output=True, text=True, check=True)
        print(f"  ✅ Uvicorn: версия {result.stdout.strip()}")
        test_passed += 1
    except subprocess.CalledProcessError:
        print("  ❌ Uvicorn: не установлен")
        test_failed += 1

    if test_failed == 0:
        print("\n✅ Все тесты пройдены!")
    else:
        print(f"\n⚠️  {test_failed} тестов не пройдено")

    print("\n" + "="*50)
    print("🎉 Установка завершена!")
    print("="*50)
    print("\n📋 Следующие шаги:")
    print("\n1. Запустить на порту по умолчанию (8000):")
    if os.name == 'nt':
        print("   python run.py")
    else:
        print("   python run.py")

    print("\n2. Запустить с проверкой занятости порта (если порт занят - подключиться к существующему):")
    if os.name == 'nt':
        print("   python run.py --fixed-port 8000")
    else:
        print("   python run.py --fixed-port 8000")

    print("\n3. Запустить с автопоиском свободного порта:")
    if os.name == 'nt':
        print("   python run.py --auto-port")
    else:
        print("   python run.py --auto-port")

    print("\n4. Запустить с MCP консолью и браузером:")
    if os.name == 'nt':
        print("   python run.py --mcp --browser")
    else:
        print("   python run.py --mcp --browser")

    print("\n5. Production режим:")
    if os.name == 'nt':
        print("   python run.py --prod")
    else:
        print("   python run.py --prod")

    print("\n6. Справка:")
    if os.name == 'nt':
        print("   python run.py --help")
    else:
        print("   python run.py --help")

    print("\n📚 Документация:")
    print("   - README.md - основная информация")
    print("   - docs/ - полная документация")

    print("\n🌐 После запуска:")
    print("   - Веб-интерфейс: http://localhost:8000")
    print("   - API документация: http://localhost:8000/docs")
    print("   - Health Check: http://localhost:8000/api/v1/health")
    print("\n💡 Порт можно изменить через --port или --fixed-port")

if __name__ == "__main__":
    main()