# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Поиск всех AI моделей в системе
# =============================================================================
# Описание:
#   Поиск моделей Foundry, Ollama, HuggingFace и других AI фреймворков
#
# File: ai_model_scanner.py
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
import json

def scan_all_ai_models() -> Dict[str, Any]:
    """Сканирование всех AI моделей в системе"""
    
    results = {
        "foundry": {"directories": [], "models": []},
        "ollama": {"directories": [], "models": []},
        "huggingface": {"directories": [], "models": []},
        "other": {"directories": [], "models": []}
    }
    
    # Пути для поиска
    search_locations = {
        "foundry": [
            Path.home() / ".foundry",
            Path.home() / ".cache" / "foundry",
            Path("C:") / "foundry" if sys.platform == "win32" else Path("/opt/foundry"),
        ],
        "ollama": [
            Path.home() / ".ollama",
            Path("C:") / "Users" / os.getenv("USERNAME", "") / ".ollama" if sys.platform == "win32" else Path.home() / ".ollama",
            Path("/usr/share/ollama") if sys.platform != "win32" else None,
        ],
        "huggingface": [
            Path.home() / ".cache" / "huggingface",
            Path.home() / ".cache" / "transformers",
            Path.home() / "transformers_cache",
        ]
    }
    
    print("🔍 Сканирование AI моделей в системе...")
    print()
    
    for framework, paths in search_locations.items():
        print(f"🔍 Поиск {framework.upper()} моделей...")
        
        for path in paths:
            if path and path.exists():
                print(f"  ✅ Найдена директория: {path}")
                results[framework]["directories"].append(str(path))
                
                # Сканирование файлов
                try:
                    for item in path.rglob("*"):
                        if item.is_file():
                            size_mb = item.stat().st_size / (1024 * 1024)
                            
                            # Определяем тип файла модели
                            if any(ext in item.name.lower() for ext in [
                                '.bin', '.safetensors', '.gguf', '.ggml', 
                                'pytorch_model', 'model.json', 'config.json',
                                '.pt', '.pth', '.onnx'
                            ]):
                                if size_mb > 5:  # Файлы больше 5MB
                                    results[framework]["models"].append({
                                        "name": item.name,
                                        "path": str(item),
                                        "size_mb": round(size_mb, 1),
                                        "parent": item.parent.name
                                    })
                except PermissionError:
                    print(f"  ⚠️  Нет доступа к {path}")
            else:
                print(f"  ❌ Не найдена: {path}")
        print()
    
    # Дополнительный поиск в общих местах
    print("🔍 Поиск в общих директориях...")
    common_paths = [
        Path.home() / "models",
        Path.home() / "Downloads",
        Path("C:") / "models" if sys.platform == "win32" else Path("/models"),
        Path(".") / "models",
    ]
    
    for path in common_paths:
        if path.exists():
            print(f"  ✅ Сканирование: {path}")
            try:
                for item in path.rglob("*"):
                    if item.is_file():
                        size_mb = item.stat().st_size / (1024 * 1024)
                        if size_mb > 50 and any(ext in item.name.lower() for ext in [
                            '.bin', '.safetensors', '.gguf', '.ggml'
                        ]):
                            results["other"]["models"].append({
                                "name": item.name,
                                "path": str(item),
                                "size_mb": round(size_mb, 1),
                                "parent": item.parent.name
                            })
            except PermissionError:
                print(f"  ⚠️  Нет доступа к {path}")
    
    return results

def check_ai_installations() -> Dict[str, bool]:
    """Проверка установленных AI фреймворков"""
    
    installations = {}
    
    # Проверка через команды
    commands = {
        "foundry": ["foundry", "foundry-server"],
        "ollama": ["ollama"],
        "python": ["python", "python3"],
        "transformers": ["transformers-cli"],
    }
    
    import shutil
    
    for framework, cmds in commands.items():
        found = False
        for cmd in cmds:
            if shutil.which(cmd):
                installations[framework] = True
                found = True
                break
        if not found:
            installations[framework] = False
    
    # Проверка Python пакетов
    try:
        import transformers
        installations["transformers_lib"] = True
    except ImportError:
        installations["transformers_lib"] = False
    
    try:
        import torch
        installations["pytorch"] = True
    except ImportError:
        installations["pytorch"] = False
    
    return installations

def main():
    """Главная функция"""
    print("=" * 70)
    print("🤖 СКАНЕР AI МОДЕЛЕЙ В СИСТЕМЕ")
    print("=" * 70)
    print()
    
    # Проверка установок
    installations = check_ai_installations()
    
    print("🔧 УСТАНОВЛЕННЫЕ ФРЕЙМВОРКИ:")
    for framework, installed in installations.items():
        status = "✅ Установлен" if installed else "❌ Не найден"
        print(f"  {framework}: {status}")
    print()
    
    # Сканирование моделей
    results = scan_all_ai_models()
    
    # Вывод результатов
    print("=" * 70)
    print("📊 РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ")
    print("=" * 70)
    
    total_models = 0
    for framework, data in results.items():
        model_count = len(data["models"])
        total_models += model_count
        
        if model_count > 0:
            print(f"\n🤖 {framework.upper()}: {model_count} моделей")
            
            # Показываем первые 5 моделей
            for model in data["models"][:5]:
                print(f"  📄 {model['name']} ({model['size_mb']} MB)")
                print(f"     📁 {model['parent']}")
            
            if model_count > 5:
                print(f"     ... и еще {model_count - 5} моделей")
    
    print(f"\n📊 ВСЕГО НАЙДЕНО МОДЕЛЕЙ: {total_models}")
    
    if total_models == 0:
        print("\n💡 РЕКОМЕНДАЦИИ:")
        print("  1. Установите Ollama: https://ollama.ai/")
        print("  2. Скачайте модели: ollama pull llama2")
        print("  3. Или установите Foundry с моделями")
        print("  4. Проверьте директории Downloads на наличие .gguf файлов")

if __name__ == "__main__":
    main()