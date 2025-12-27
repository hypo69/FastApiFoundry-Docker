# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Environment Variables Processor for Config
# =============================================================================
# Описание:
#   Утилита для подстановки переменных окружения в config.json
#   Поддерживает синтаксис ${VAR_NAME:default_value}
#
# Примеры:
#   from src.utils.env_processor import process_config
#   config = process_config('config.json')
#
# File: src/utils/env_processor.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import os
import json
import re
from pathlib import Path
from typing import Any, Dict, Union
from dotenv import load_dotenv

def load_env_variables():
    """Загрузка переменных окружения из .env файла"""
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
        return True
    return False

def substitute_env_vars(value: str) -> Union[str, int, float, bool]:
    """
    Подстановка переменных окружения в строке
    
    Поддерживаемые форматы:
    - ${VAR_NAME} - обязательная переменная
    - ${VAR_NAME:default} - с значением по умолчанию
    
    Args:
        value (str): Строка с переменными окружения
        
    Returns:
        Union[str, int, float, bool]: Обработанное значение
    """
    if not isinstance(value, str):
        return value
    
    # Паттерн для поиска ${VAR_NAME} или ${VAR_NAME:default}
    pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
    
    def replace_var(match):
        var_name = match.group(1)
        default_value = match.group(2) if match.group(2) is not None else None
        
        # Получаем значение из переменных окружения
        env_value = os.getenv(var_name)
        
        if env_value is not None:
            result = env_value
        elif default_value is not None:
            result = default_value
        else:
            raise ValueError(f"Environment variable '{var_name}' is required but not set")
        
        return result
    
    # Заменяем все переменные
    result = re.sub(pattern, replace_var, value)
    
    # Пытаемся преобразовать в соответствующий тип
    return convert_type(result)

def convert_type(value: str) -> Union[str, int, float, bool]:
    """Преобразование строки в соответствующий тип"""
    if not isinstance(value, str):
        return value
    
    # Булевы значения
    if value.lower() in ('true', 'yes', '1', 'on'):
        return True
    if value.lower() in ('false', 'no', '0', 'off'):
        return False
    
    # Числа
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        pass
    
    # Массивы (разделенные запятыми)
    if ',' in value:
        return [item.strip() for item in value.split(',')]
    
    return value

def process_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Рекурсивная обработка словаря"""
    result = {}
    
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = process_dict(value)
        elif isinstance(value, list):
            result[key] = [
                process_dict(item) if isinstance(item, dict) 
                else substitute_env_vars(item) if isinstance(item, str)
                else item
                for item in value
            ]
        elif isinstance(value, str):
            result[key] = substitute_env_vars(value)
        else:
            result[key] = value
    
    return result

def process_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Загрузка и обработка конфигурационного файла
    
    Args:
        config_path (Union[str, Path]): Путь к config.json
        
    Returns:
        Dict[str, Any]: Обработанная конфигурация
        
    Raises:
        FileNotFoundError: Если файл не найден
        json.JSONDecodeError: Если файл содержит невалидный JSON
        ValueError: Если обязательная переменная окружения не установлена
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    # Загружаем переменные окружения
    load_env_variables()
    
    # Читаем и парсим JSON
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    # Обрабатываем переменные окружения
    processed_config = process_dict(config_data)
    
    return processed_config

def validate_config(config: Dict[str, Any]) -> bool:
    """
    Валидация обработанной конфигурации
    
    Args:
        config (Dict[str, Any]): Конфигурация для проверки
        
    Returns:
        bool: True если конфигурация валидна
    """
    required_sections = ['fastapi_server', 'foundry_ai', 'security']
    
    for section in required_sections:
        if section not in config:
            print(f"❌ Missing required section: {section}")
            return False
    
    # Проверяем критичные настройки
    if not config.get('security', {}).get('api_key'):
        print("⚠️ API_KEY not set in security section")
    
    if not config.get('security', {}).get('secret_key'):
        print("⚠️ SECRET_KEY not set in security section")
    
    return True

def save_processed_config(config: Dict[str, Any], output_path: Union[str, Path]):
    """Сохранение обработанной конфигурации"""
    output_path = Path(output_path)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import sys
    
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    
    try:
        print(f"🔧 Processing config: {config_file}")
        config = process_config(config_file)
        
        print("✅ Config processed successfully!")
        
        if validate_config(config):
            print("✅ Config validation passed!")
        else:
            print("⚠️ Config validation warnings found")
        
        # Сохраняем обработанную конфигурацию для отладки
        debug_path = Path(config_file).with_suffix('.processed.json')
        save_processed_config(config, debug_path)
        print(f"💾 Processed config saved to: {debug_path}")
        
    except Exception as e:
        print(f"❌ Error processing config: {e}")
        sys.exit(1)