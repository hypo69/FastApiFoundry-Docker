#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Освобождение портов
# =============================================================================
# Описание:
#   Убивает все процессы на указанном порту
#
# File: kill_port.py
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

def kill_port(port):
    """Убить все процессы на указанном порту"""
    try:
        if os.name == 'nt':  # Windows
            # Найти процессы на порту
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            pids = []
            for line in lines:
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        if pid.isdigit() and pid != '0':  # Исключаем PID 0
                            pids.append(pid)
            
            # Убить процессы
            killed_count = 0
            for pid in pids:
                try:
                    subprocess.run(['taskkill', '/F', '/PID', pid], check=True, capture_output=True)
                    print(f"✅ Killed process {pid} on port {port}")
                    killed_count += 1
                except subprocess.CalledProcessError:
                    print(f"❌ Failed to kill process {pid}")
            
            if killed_count == 0:
                print(f"ℹ️ No processes found on port {port}")
                    
        else:  # Linux/macOS
            try:
                subprocess.run(['pkill', '-f', f':{port}'], check=True)
                print(f"✅ Killed processes on port {port}")
            except subprocess.CalledProcessError:
                print(f"ℹ️ No processes found on port {port}")
                
        print(f"🔓 Port {port} is now free")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def kill_foundry_ports():
    """Убить процессы только на основном порту Foundry"""
    foundry_port = 50477  # Только основной порт
    
    print(f"🔍 Освобождаем порт Foundry {foundry_port}...")
    kill_port(foundry_port)
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            kill_port(port)
        except ValueError:
            if sys.argv[1] == "foundry":
                kill_foundry_ports()
            else:
                print("❌ Invalid port number")
    else:
        print("Usage: python kill_port.py <port> or python kill_port.py foundry")