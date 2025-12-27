# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Тест редактора конфигурации
# =============================================================================
# Описание:
#   Простой тест для проверки работы редактора config.json
#
# File: test_config_editor.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import requests
import json

def test_config_editor():
    """Тест редактора конфигурации"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 Тестирование редактора конфигурации...")
    
    # 1. Получение текущей конфигурации
    print("\n1. Получение конфигурации...")
    try:
        response = requests.get(f"{base_url}/config")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Конфигурация получена успешно")
                print(f"   Foundry URL: {data['config']['foundry_ai']['base_url']}")
                print(f"   API Port: {data['config']['fastapi_server']['port']}")
            else:
                print(f"❌ Ошибка: {data.get('error')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return
    
    # 2. Тест обновления конфигурации
    print("\n2. Тест обновления конфигурации...")
    try:
        # Создаем тестовую конфигурацию
        test_config = data['config'].copy()
        test_config['fastapi_server']['log_level'] = 'DEBUG'  # Изменяем уровень логирования
        
        response = requests.post(f"{base_url}/config", 
                               json={"config": test_config})
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Конфигурация обновлена успешно")
                print(f"   Сообщение: {result['message']}")
                print(f"   Бэкап создан: {result['backup_created']}")
            else:
                print(f"❌ Ошибка обновления: {result.get('error')}")
        else:
            print(f"❌ HTTP ошибка при обновлении: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка при обновлении: {e}")
    
    # 3. Проверка что изменения сохранились
    print("\n3. Проверка сохранения изменений...")
    try:
        response = requests.get(f"{base_url}/config")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                current_log_level = data['config']['fastapi_server']['log_level']
                if current_log_level == 'DEBUG':
                    print("✅ Изменения сохранились корректно")
                else:
                    print(f"❌ Изменения не сохранились. Текущий уровень: {current_log_level}")
            else:
                print(f"❌ Ошибка при проверке: {data.get('error')}")
    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
    
    print("\n🎯 Тест завершен!")
    print("\n📋 Для использования:")
    print("   1. Откройте http://localhost:8000")
    print("   2. Перейдите на вкладку Settings")
    print("   3. Отредактируйте config.json в текстовом поле")
    print("   4. Нажмите 'Save' для сохранения")

if __name__ == "__main__":
    test_config_editor()