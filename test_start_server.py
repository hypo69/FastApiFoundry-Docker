#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой запуск FastAPI сервера с embedded Python 3.11
"""
import os
import sys
import subprocess

# Устанавливаем PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Запускаем uvicorn
os.chdir(current_dir)
subprocess.run([
    'python-3.11.0-embed-amd64/python.exe', '-m', 'uvicorn',
    'src.api.main:app',
    '--host', '0.0.0.0',
    '--port', '8000',
    '--reload',
    '--log-level', 'info'
])