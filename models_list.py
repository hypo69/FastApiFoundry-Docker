# -*- coding: utf-8 -*-
# Актуальный список моделей для FastAPI Foundry
# Получен из Foundry API

import subprocess
import json
import sys
from typing import List, Dict, Any

def get_foundry_models() -> List[Dict[str, Any]]:
    """Получить список моделей из Foundry"""
    try:
        # Запускаем команду foundry model list
        result = subprocess.run(['foundry', 'model', 'list'],
                              capture_output=True, text=True, encoding='utf-8')

        if result.returncode != 0:
            print(f"Ошибка выполнения команды: {result.stderr}")
            return []

        lines = result.stdout.strip().split('\n')

        models = []
        current_model = None

        for line in lines:
            line = line.strip()
            if not line or line.startswith('Alias') or line.startswith('-'):
                continue

            # Парсим строку модели
            if line.startswith('   ') and current_model:
                # Это дополнительная строка для той же модели (CPU/GPU версия)
                parts = line.split()
                if len(parts) >= 6:
                    device = parts[0]
                    task = parts[1] if len(parts) > 1 else 'chat'
                    size = f"{parts[2]} {parts[3]}" if len(parts) > 3 else 'Unknown'
                    license = parts[4] if len(parts) > 4 else 'Unknown'
                    model_id = ' '.join(parts[5:]) if len(parts) > 5 else 'Unknown'

                    # Добавляем вариант модели
                    variant = {
                        'device': device,
                        'task': task,
                        'size': size,
                        'license': license,
                        'model_id': model_id.strip()
                    }
                    current_model['variants'].append(variant)
            else:
                # Это новая модель
                parts = line.split()
                if len(parts) >= 5:
                    alias = parts[0]
                    device = parts[1]
                    task = parts[2] if len(parts) > 2 else 'chat'
                    size = f"{parts[3]} {parts[4]}" if len(parts) > 4 else 'Unknown'
                    license = parts[5] if len(parts) > 5 else 'Unknown'
                    model_id = ' '.join(parts[6:]) if len(parts) > 6 else 'Unknown'

                    current_model = {
                        'alias': alias,
                        'primary_device': device,
                        'primary_task': task,
                        'primary_size': size,
                        'license': license,
                        'primary_model_id': model_id.strip(),
                        'variants': [{
                            'device': device,
                            'task': task,
                            'size': size,
                            'license': license,
                            'model_id': model_id.strip()
                        }]
                    }
                    models.append(current_model)

        return models

    except Exception as e:
        print(f"Ошибка получения списка моделей: {e}")
        return []

def get_loaded_models() -> List[Dict[str, str]]:
    """Получить список загруженных моделей"""
    try:
        result = subprocess.run(['foundry', 'service', 'list'],
                              capture_output=True, text=True, encoding='utf-8')

        if result.returncode != 0:
            print(f"Ошибка получения загруженных моделей: {result.stderr}")
            return []

        lines = result.stdout.strip().split('\n')
        loaded_models = []

        for line in lines:
            if '🟢' in line and 'Model ID' not in line:
                parts = line.replace('🟢', '').strip().split()
                if len(parts) >= 2:
                    loaded_models.append({
                        'alias': parts[0],
                        'model_id': ' '.join(parts[1:])
                    })

        return loaded_models

    except Exception as e:
        print(f"Ошибка получения загруженных моделей: {e}")
        return []

def create_models_json(models: List[Dict], loaded_models: List[Dict]) -> Dict:
    """Создать JSON структуру для веб-интерфейса"""
    loaded_ids = {model['model_id'] for model in loaded_models}

    json_models = []
    current_model_id = None

    for model in models:
        # Используем primary модель для отображения
        primary = model['variants'][0]

        # Определяем, загружена ли эта модель
        is_loaded = any(variant['model_id'] in loaded_ids for variant in model['variants'])

        model_entry = {
            'id': primary['model_id'],
            'name': f"{model['alias']} ({primary['device']})",
            'size': primary['size'],
            'description': f"{model['alias']} - {primary['task']} модель",
            'current': is_loaded
        }

        json_models.append(model_entry)

        if is_loaded and not current_model_id:
            current_model_id = primary['model_id']

    return {
        'models': json_models,
        'current_model': current_model_id or (json_models[0]['id'] if json_models else None)
    }

def print_models_table(models: List[Dict], loaded_models: List[Dict]):
    """Вывести таблицу моделей в консоль"""
    loaded_ids = {model['model_id'] for model in loaded_models}

    print("📋 АКТУАЛЬНЫЙ СПИСОК МОДЕЛЕЙ ИЗ FOUNDRY:")
    print("=" * 80)

    for i, model in enumerate(models, 1):
        primary = model['variants'][0]
        is_loaded = any(variant['model_id'] in loaded_ids for variant in model['variants'])

        status = "✅ ЗАГРУЖЕНА" if is_loaded else ""
        print(f"{i:2d}. {model['alias']} ({primary['size']}) {status}")
        print(f"    Основная: {primary['model_id']}")
        print(f"    Лицензия: {primary['license']}")

        # Показываем варианты
        if len(model['variants']) > 1:
            print("    Варианты:")
            for variant in model['variants'][1:]:
                variant_status = " (загружена)" if variant['model_id'] in loaded_ids else ""
                print(f"      - {variant['device']}: {variant['model_id']}{variant_status}")

        print()

    # Показываем загруженные модели отдельно
    if loaded_models:
        print("🎯 ЗАГРУЖЕННЫЕ МОДЕЛИ:")
        print("-" * 40)
        for model in loaded_models:
            print(f"   {model['alias']} - {model['model_id']}")
        print()

if __name__ == "__main__":
    print("Получение актуальных данных из Foundry...")

    # Получаем данные
    models = get_foundry_models()
    loaded_models = get_loaded_models()

    if not models:
        print("❌ Не удалось получить список моделей из Foundry")
        sys.exit(1)

    # Выводим таблицу
    print_models_table(models, loaded_models)

    # Создаем JSON для веб-интерфейса
    json_data = create_models_json(models, loaded_models)

    # Сохраняем в файл
    with open('available_models.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Сохранено {len(json_data['models'])} моделей в available_models.json")
    print(f"🎯 Текущая модель: {json_data['current_model']}")