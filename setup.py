#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker-only установщик FastAPI Foundry
"""

import subprocess
import sys
from pathlib import Path

def check_docker():
    """Проверить Docker"""
    try:
        docker_result = subprocess.run(["docker", "--version"], capture_output=True, text=True, check=True)
        compose_result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True, check=True)
        print(f"✅ Docker: {docker_result.stdout.strip()}")
        print(f"✅ Docker Compose: {compose_result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker не установлен!")
        print("\nУстановите Docker Desktop:")
        print("https://www.docker.com/products/docker-desktop/")
        return False

def setup_env():
    """Настройка .env файла"""
    if not Path(".env").exists():
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ .env создан из .env.example")
        else:
            env_content = """# FastAPI Foundry Configuration
FOUNDRY_BASE_URL=http://localhost:55581/v1/
FOUNDRY_DEFAULT_MODEL=deepseek-r1-distill-qwen-7b-generic-cpu:3
API_HOST=0.0.0.0
API_PORT=8000
RAG_ENABLED=true
LOG_LEVEL=INFO
"""
            with open(".env", "w") as f:
                f.write(env_content)
            print("✅ .env создан")
    else:
        print("✅ .env уже существует")

def main():
    print("🐳 FastAPI Foundry - Docker Setup")
    print("=" * 40)
    
    if not check_docker():
        sys.exit(1)
    
    setup_env()
    
    print("\n🚀 Готово! Запускайте:")
    print("   docker compose up -d")
    print("\n🌐 После запуска:")
    print("   http://localhost:8000")
    print("   http://localhost:8000/docs")

if __name__ == "__main__":
    main()