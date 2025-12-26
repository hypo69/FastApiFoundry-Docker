# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Поиск моделей Foundry в системе
# =============================================================================
# Описание:
#   Утилита для поиска и анализа моделей Foundry в различных директориях
#
# File: foundry_model_finder.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

def find_foundry_models() -> Dict[str, Any]:
    """Поиск моделей Foundry в системе"""
    
    # Возможные пути для моделей
    search_paths = [
        # Windows
        Path.home() / ".foundry" / "models",
        Path.home() / ".cache" / "foundry",
        Path.home() / "AppData" / "Local" / "foundry",
        Path.home() / "AppData" / "Roaming" / "foundry",
        Path("C:") / "foundry" / "models",
        
        # Linux/macOS
        Path.home() / ".foundry",
        Path.home() / ".local" / "share" / "foundry",
        Path("/opt/foundry/models"),
        Path("/usr/local/foundry/models"),
        
        # Docker volumes
        Path("/models"),
        Path("/app/models"),
        
        # Текущая директория
        Path(".") / "models",
        Path("..") / "models",
    ]
    
    found_models = []
    model_dirs = []
    
    print("🔍 Поиск моделей Foundry в системе...")
    print()
    
    for search_path in search_paths:
        if search_path.exists():
            print(f"✅ Найдена директория: {search_path}")
            model_dirs.append(str(search_path))
            
            # Поиск файлов моделей
            for item in search_path.rglob("*"):
                if item.is_file():
                    # Типичные файлы моделей
                    if any(ext in item.name.lower() for ext in [
                        '.bin', '.safetensors', '.gguf', '.ggml', 
                        'pytorch_model', 'model.json', 'config.json'
                    ]):
                        size_mb = item.stat().st_size / (1024 * 1024)
                        if size_mb > 10:  # Только большие файлы (модели)
                            found_models.append({
                                "path": str(item),
                                "name": item.name,
                                "size_mb": round(size_mb, 1),
                                "parent_dir": str(item.parent)
                            })
        else:
            print(f"❌ Не найдена: {search_path}")
    
    print()
    print(f"📊 Найдено директорий: {len(model_dirs)}")
    print(f"📊 Найдено файлов моделей: {len(found_models)}")
    
    return {
        "model_directories": model_dirs,
        "model_files": found_models,
        "total_directories": len(model_dirs),
        "total_files": len(found_models)
    }

def check_foundry_installation() -> Dict[str, Any]:
    """Проверка установки Foundry"""
    
    print("🔍 Проверка установки Foundry...")
    
    # Поиск исполняемых файлов
    executables = []
    
    # Windows
    if sys.platform == "win32":
        possible_exes = [
            "foundry.exe",
            "foundry-server.exe", 
            "foundry-cli.exe"
        ]
        
        # Поиск в PATH
        for exe in possible_exes:
            import shutil
            if shutil.which(exe):
                executables.append(shutil.which(exe))
        
        # Поиск в стандартных директориях
        standard_dirs = [
            Path("C:") / "Program Files" / "Foundry",
            Path("C:") / "Program Files (x86)" / "Foundry",
            Path.home() / "AppData" / "Local" / "Programs" / "Foundry"
        ]
        
        for dir_path in standard_dirs:
            if dir_path.exists():
                for exe in possible_exes:
                    exe_path = dir_path / exe
                    if exe_path.exists():
                        executables.append(str(exe_path))
    
    # Linux/macOS
    else:
        import shutil
        for exe in ["foundry", "foundry-server"]:
            if shutil.which(exe):
                executables.append(shutil.which(exe))
    
    print(f"📊 Найдено исполняемых файлов: {len(executables)}")
    for exe in executables:
        print(f"  ✅ {exe}")
    
    return {
        "executables": executables,
        "installed": len(executables) > 0
    }

def main():
    """Главная функция"""
    print("=" * 60)
    print("🔍 ПОИСК МОДЕЛЕЙ FOUNDRY В СИСТЕМЕ")
    print("=" * 60)
    print()
    
    # Проверка установки
    installation = check_foundry_installation()
    print()
    
    # Поиск моделей
    models = find_foundry_models()
    print()
    
    # Вывод результатов
    print("=" * 60)
    print("📋 РЕЗУЛЬТАТЫ ПОИСКА")
    print("=" * 60)
    
    print(f"🔧 Foundry установлен: {'Да' if installation['installed'] else 'Нет'}")
    print(f"📁 Найдено директорий с моделями: {models['total_directories']}")
    print(f"📄 Найдено файлов моделей: {models['total_files']}")
    
    if models['model_files']:
        print()
        print("📄 НАЙДЕННЫЕ МОДЕЛИ:")
        for model in models['model_files'][:10]:  # Первые 10
            print(f"  📄 {model['name']} ({model['size_mb']} MB)")
            print(f"     📁 {model['parent_dir']}")
    
    if models['model_directories']:
        print()
        print("📁 ДИРЕКТОРИИ С МОДЕЛЯМИ:")
        for dir_path in models['model_directories']:
            print(f"  📁 {dir_path}")
    
    print()
    print("💡 Для запуска Foundry используйте найденные пути к моделям")

if __name__ == "__main__":
    main()