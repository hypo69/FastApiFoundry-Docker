#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Остановка FastAPI Foundry серверов
# =============================================================================
# Описание:
#   Простой скрипт для завершения процессов FastAPI Foundry
#   Упрощенная версия без избыточного логирования
#
# File: stop.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import subprocess
import platform
import sys

def kill_processes_on_ports(ports):
    """Завершить процессы на указанных портах"""
    print(f"Checking ports: {ports}")
    system = platform.system().lower()
    killed_count = 0
    
    for port in ports:
        print(f"Checking port {port}...")
        
        if system == "windows":
            try:
                result = subprocess.run(
                    ["netstat", "-ano"], 
                    capture_output=True, 
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if f":{port}" in line and "LISTENING" in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                print(f"Found process PID {pid} on port {port}, killing...")
                                
                                kill_result = subprocess.run(
                                    ["taskkill", "/PID", pid, "/F"], 
                                    capture_output=True, 
                                    text=True,
                                    timeout=5
                                )
                                
                                if kill_result.returncode == 0:
                                    print(f"✅ Killed process PID {pid}")
                                    killed_count += 1
                                else:
                                    print(f"❌ Failed to kill PID {pid}")
                                    
            except Exception as e:
                print(f"Error checking port {port}: {e}")
        
        else:  # Unix/Linux/macOS
            try:
                result = subprocess.run(
                    ["lsof", "-ti", f":{port}"], 
                    capture_output=True, 
                    text=True,
                    timeout=10
                )
                
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            print(f"Found process PID {pid} on port {port}, killing...")
                            subprocess.run(["kill", "-9", pid], capture_output=True, timeout=5)
                            print(f"✅ Killed process PID {pid}")
                            killed_count += 1
                            
            except Exception as e:
                print(f"Error checking port {port}: {e}")
    
    print(f"Total processes killed: {killed_count}")
    return killed_count

def main():
    print("🛑 FastAPI Foundry Stop Script")
    print("=" * 40)
    
    # Порты по умолчанию
    ports = [8000, 8001, 8002, 8003, 8004, 8005]
    
    if len(sys.argv) > 1:
        try:
            ports = [int(p.strip()) for p in sys.argv[1].split(",")]
        except ValueError:
            print("Invalid port format. Use: python stop.py 8000,8001,8002")
            return 1
    
    killed_count = kill_processes_on_ports(ports)
    
    print("=" * 40)
    print(f"✅ Killed {killed_count} processes")
    print("🏁 Done")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())