#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Простой генератор SSL сертификатов
# =============================================================================
# Описание:
#   Создает самоподписанные SSL сертификаты для HTTPS
#
# File: generate-ssl.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import os
import subprocess
from pathlib import Path

def generate_ssl_certificates():
    """Генерация SSL сертификатов через openssl"""
    
    ssl_dir = Path.home() / ".ssl"
    ssl_dir.mkdir(exist_ok=True)
    
    cert_file = ssl_dir / "cert.pem"
    key_file = ssl_dir / "key.pem"
    
    print(f"🔐 Создание SSL сертификатов в {ssl_dir}")
    
    # Команда openssl
    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096",
        "-keyout", str(key_file),
        "-out", str(cert_file),
        "-days", "365", "-nodes",
        "-subj", "/C=US/ST=State/L=City/O=FastAPI-Foundry/CN=localhost"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ SSL сертификаты созданы:")
            print(f"   Сертификат: {cert_file}")
            print(f"   Ключ: {key_file}")
            print(f"   Срок действия: 365 дней")
            print()
            print("🚀 Теперь можете запустить сервер с HTTPS поддержкой")
            return True
        else:
            print(f"❌ Ошибка openssl: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ OpenSSL не найден!")
        print("💡 Установите OpenSSL:")
        print("   Windows: https://slproweb.com/products/Win32OpenSSL.html")
        print("   или используйте: winget install OpenSSL.Light")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🔐 SSL Certificate Generator для FastAPI Foundry")
    print("=" * 50)
    generate_ssl_certificates()