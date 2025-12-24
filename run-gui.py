#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: GUI лончер для FastAPI Foundry (Python версия)
# =============================================================================
# Описание:
#   Графический интерфейс для запуска run.py с полным набором параметров
#   Настройки загружаются из src/config.json
#
# Примеры:
#   python run-gui.py
#
# File: run-gui.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 24 декабря 2025
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import sys
import subprocess
import socket
import signal
import psutil
import threading
import time
from pathlib import Path

class FastApiFoundryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FastAPI Foundry — Launch Configuration")
        self.root.geometry("550x750")
        self.root.resizable(False, False)

        # Определение директории скрипта
        self.script_dir = Path(__file__).parent
        self.config_file = self.script_dir / "src" / "config.json"

        # Загрузка конфигурации
        self.config = self.load_config()

        # Создание интерфейса
        self.create_widgets()

        # Центрирование окна
        self.center_window()

    def load_config(self):
        """Загрузка конфигурации из src/config.json"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                messagebox.showerror("Error", f"Config file not found: {self.config_file}")
                sys.exit(1)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")
            sys.exit(1)

    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        # Создание Notebook (вкладки)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладки
        self.create_fastapi_tab()
        self.create_foundry_tab()
        self.create_rag_tab()
        self.create_docker_tab()

        # Кнопки
        self.create_buttons()

    def create_fastapi_tab(self):
        """Создание вкладки FastAPI Server"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="FastAPI Server")

        # Заголовок
        header = tk.Label(tab, text=f"FastAPI Server Configuration (Port {self.config['fastapi_server']['port']})",
                         font=("Segoe UI", 10, "bold"), fg="darkblue")
        header.pack(pady=(20, 10))

        # Контейнер для полей
        frame = tk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=20)

        # Mode
        tk.Label(frame, text="FASTAPI_FOUNDRY_MODE:").grid(row=0, column=0, sticky='w', pady=5)
        self.mode_var = tk.StringVar(value=self.config['fastapi_server']['mode'])
        mode_combo = ttk.Combobox(frame, textvariable=self.mode_var, values=["dev", "production"], state="readonly", width=25)
        mode_combo.grid(row=0, column=1, pady=5)

        # Host
        tk.Label(frame, text="HOST:").grid(row=1, column=0, sticky='w', pady=5)
        self.host_var = tk.StringVar(value=self.config['fastapi_server']['host'])
        tk.Entry(frame, textvariable=self.host_var, width=28).grid(row=1, column=1, pady=5)

        # Port
        tk.Label(frame, text="PORT (FastAPI Server):").grid(row=2, column=0, sticky='w', pady=5)
        self.port_var = tk.StringVar(value=str(self.config['fastapi_server']['port']))
        tk.Entry(frame, textvariable=self.port_var, width=28).grid(row=2, column=1, pady=5)

        # API Key
        tk.Label(frame, text="API_KEY (optional):").grid(row=3, column=0, sticky='w', pady=5)
        self.api_key_var = tk.StringVar(value=self.config['security']['api_key'])
        tk.Entry(frame, textvariable=self.api_key_var, show="*", width=28).grid(row=3, column=1, pady=5)

        # Workers
        tk.Label(frame, text="API_WORKERS:").grid(row=4, column=0, sticky='w', pady=5)
        self.workers_var = tk.IntVar(value=self.config['fastapi_server']['workers'])
        tk.Spinbox(frame, from_=1, to=16, textvariable=self.workers_var, width=26).grid(row=4, column=1, pady=5)

        # Reload
        self.reload_var = tk.BooleanVar(value=self.config['fastapi_server']['reload'])
        tk.Checkbutton(frame, text="API_RELOAD (dev mode)", variable=self.reload_var).grid(row=5, column=0, columnspan=2, sticky='w', pady=5)

        # Log Level
        tk.Label(frame, text="LOG_LEVEL:").grid(row=6, column=0, sticky='w', pady=5)
        self.log_level_var = tk.StringVar(value=self.config['logging']['level'])
        log_combo = ttk.Combobox(frame, textvariable=self.log_level_var, values=["DEBUG", "INFO", "WARNING", "ERROR"], state="readonly", width=25)
        log_combo.grid(row=6, column=1, pady=5)

    def create_foundry_tab(self):
        """Создание вкладки Foundry AI Model"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Foundry AI Model")

        # Заголовок
        header = tk.Label(tab, text="Foundry AI Model Configuration", font=("Segoe UI", 10, "bold"), fg="darkgreen")
        header.pack(pady=(20, 10))

        frame = tk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=20)

        # Base URL
        tk.Label(frame, text="FOUNDRY_BASE_URL (AI Model):").grid(row=0, column=0, sticky='w', pady=5)
        self.foundry_url_var = tk.StringVar(value=self.config['foundry_ai']['base_url'])
        tk.Entry(frame, textvariable=self.foundry_url_var, width=28).grid(row=0, column=1, pady=5)

        # Default Model
        tk.Label(frame, text="FOUNDRY_DEFAULT_MODEL:").grid(row=1, column=0, sticky='w', pady=5)
        self.model_var = tk.StringVar(value=self.config['foundry_ai']['default_model'])
        tk.Entry(frame, textvariable=self.model_var, width=28).grid(row=1, column=1, pady=5)

        # Temperature
        tk.Label(frame, text="FOUNDRY_TEMPERATURE:").grid(row=2, column=0, sticky='w', pady=5)
        self.temp_var = tk.DoubleVar(value=self.config['foundry_ai']['temperature'])
        tk.Spinbox(frame, from_=0.0, to=2.0, increment=0.1, textvariable=self.temp_var, width=26).grid(row=2, column=1, pady=5)

        # Top P
        tk.Label(frame, text="FOUNDRY_TOP_P:").grid(row=3, column=0, sticky='w', pady=5)
        self.top_p_var = tk.DoubleVar(value=self.config['foundry_ai']['top_p'])
        tk.Spinbox(frame, from_=0.0, to=1.0, increment=0.01, textvariable=self.top_p_var, width=26).grid(row=3, column=1, pady=5)

        # Top K
        tk.Label(frame, text="FOUNDRY_TOP_K:").grid(row=4, column=0, sticky='w', pady=5)
        self.top_k_var = tk.IntVar(value=self.config['foundry_ai']['top_k'])
        tk.Spinbox(frame, from_=1, to=200, textvariable=self.top_k_var, width=26).grid(row=4, column=1, pady=5)

        # Max Tokens
        tk.Label(frame, text="FOUNDRY_MAX_TOKENS:").grid(row=5, column=0, sticky='w', pady=5)
        self.max_tokens_var = tk.IntVar(value=self.config['foundry_ai']['max_tokens'])
        tk.Spinbox(frame, from_=1, to=32768, textvariable=self.max_tokens_var, width=26).grid(row=5, column=1, pady=5)

        # Timeout
        tk.Label(frame, text="FOUNDRY_TIMEOUT (sec):").grid(row=6, column=0, sticky='w', pady=5)
        self.timeout_var = tk.IntVar(value=self.config['foundry_ai']['timeout'])
        tk.Spinbox(frame, from_=10, to=3600, textvariable=self.timeout_var, width=26).grid(row=6, column=1, pady=5)

    def create_rag_tab(self):
        """Создание вкладки RAG System"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="RAG System")

        frame = tk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        # RAG Enabled
        self.rag_enabled_var = tk.BooleanVar(value=self.config['rag_system']['enabled'])
        tk.Checkbutton(frame, text="RAG_ENABLED", variable=self.rag_enabled_var).grid(row=0, column=0, columnspan=2, sticky='w', pady=10)

        # Index Dir
        tk.Label(frame, text="RAG_INDEX_DIR:").grid(row=1, column=0, sticky='w', pady=5)
        self.rag_dir_var = tk.StringVar(value=self.config['rag_system']['index_dir'])
        tk.Entry(frame, textvariable=self.rag_dir_var, width=28).grid(row=1, column=1, pady=5)

        # Model
        tk.Label(frame, text="RAG_MODEL:").grid(row=2, column=0, sticky='w', pady=5)
        self.rag_model_var = tk.StringVar(value=self.config['rag_system']['model'])
        rag_models = [
            "sentence-transformers/all-MiniLM-L6-v2",
            "sentence-transformers/all-mpnet-base-v2",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        ]
        rag_combo = ttk.Combobox(frame, textvariable=self.rag_model_var, values=rag_models, state="readonly", width=25)
        rag_combo.grid(row=2, column=1, pady=5)

    def create_docker_tab(self):
        """Создание вкладки Docker"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Docker")

        frame = tk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Docker Mode
        self.docker_mode_var = tk.BooleanVar(value=False)
        tk.Checkbutton(frame, text="Запуск из Docker контейнера", variable=self.docker_mode_var,
                      font=("Segoe UI", 10, "bold"), fg="darkblue").grid(row=0, column=0, columnspan=2, sticky='w', pady=10)

        # Info
        info_text = "При включении Docker режима run.py будет запущен внутри контейнера\nчерез docker-compose. Убедитесь что Docker Desktop запущен."
        tk.Label(frame, text=info_text, fg="gray", justify="left").grid(row=1, column=0, columnspan=2, sticky='w', pady=10)

        # Container Name
        tk.Label(frame, text="Container Name:").grid(row=2, column=0, sticky='w', pady=5)
        self.container_name_var = tk.StringVar(value="fastapi-foundry-docker")
        tk.Entry(frame, textvariable=self.container_name_var, width=28).grid(row=2, column=1, pady=5)

        # Docker Port
        tk.Label(frame, text="Host Port (внешний):").grid(row=3, column=0, sticky='w', pady=5)
        self.docker_port_var = tk.StringVar(value="8000")
        tk.Entry(frame, textvariable=self.docker_port_var, width=28).grid(row=3, column=1, pady=5)

        # Build Option
        self.docker_build_var = tk.BooleanVar(value=False)
        tk.Checkbutton(frame, text="Пересобрать образ перед запуском (--build)", variable=self.docker_build_var).grid(row=4, column=0, columnspan=2, sticky='w', pady=10)

    def create_buttons(self):
        """Создание кнопок управления"""
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill='x', padx=20, pady=(0, 20))

        # Кнопка запуска
        self.run_button = tk.Button(button_frame, text="🚀 RUN", command=self.run_application,
                                   font=("Segoe UI", 12, "bold"), bg="lightgreen", width=12, height=2)
        self.run_button.pack(side='right', padx=(10, 0))

        # Кнопка закрытия
        self.close_button = tk.Button(button_frame, text="❌ CLOSE", command=self.root.quit,
                                     font=("Segoe UI", 12), width=12, height=2)
        self.close_button.pack(side='right')

    def validate_input(self):
        """Валидация ввода"""
        try:
            port = int(self.port_var.get())
            if port < 1 or port > 65535:
                raise ValueError("Port must be between 1 and 65535")
        except ValueError:
            messagebox.showwarning("Validation Error", "PORT must be a valid number")
            return False

        if not self.host_var.get().strip():
            messagebox.showwarning("Validation Error", "HOST cannot be empty")
            return False

        return True

    def resolve_port_conflict(self, port, resolution="kill_process"):
        """Разрешение конфликтов портов"""
        try:
            # Проверка занятости порта
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()

            if result == 0:  # Порт занят
                if resolution == "kill_process":
                    # Найти и убить процесс
                    for proc in psutil.process_iter(['pid', 'name', 'connections']):
                        try:
                            for conn in proc.info['connections'] or []:
                                if conn.laddr.port == port:
                                    print(f"⚠️ Найден процесс PID {proc.info['pid']} на порту {port}, завершаем...")
                                    os.kill(proc.info['pid'], signal.SIGTERM)
                                    time.sleep(1)
                                    return port
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                elif resolution == "find_free_port":
                    # Найти свободный порт
                    for test_port in range(port + 1, port + 101):
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        result = sock.connect_ex(('127.0.0.1', test_port))
                        sock.close()
                        if result != 0:
                            return test_port
                    return None
            return port
        except Exception as e:
            print(f"Error resolving port conflict: {e}")
            return port

    def check_docker(self):
        """Проверка Docker"""
        try:
            result = subprocess.run(["docker", "version", "--format", "{{.Server.Version}}"],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, "Docker Engine недоступен"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, "Docker не установлен или не запущен"

    def run_application(self):
        """Запуск приложения"""
        if not self.validate_input():
            return

        try:
            if self.docker_mode_var.get():
                self.run_docker_mode()
            else:
                self.run_normal_mode()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start: {e}")

    def run_docker_mode(self):
        """Запуск в Docker режиме"""
        print("Starting FastAPI Foundry in Docker container...")
        container_name = self.container_name_var.get()
        docker_port = self.docker_port_var.get()

        print(f"Container: {container_name}")
        print(f"Host Port: {docker_port} -> Container Port: 8000")

        # Проверка Docker
        docker_ok, docker_version = self.check_docker()
        if not docker_ok:
            messagebox.showerror("Docker Error", f"Docker недоступен: {docker_version}")
            return

        print(f"✅ Docker запущен (версия: {docker_version})")

        # Разрешение конфликтов портов
        try:
            resolved_port = self.resolve_port_conflict(int(docker_port))
            if resolved_port != int(docker_port):
                self.docker_port_var.set(str(resolved_port))
                print(f"🔄 Порт FastAPI изменен на: {resolved_port}")
        except Exception as e:
            print(f"Error resolving port conflict: {e}")

        # Проверка образа
        if self.docker_build_var.get():
            print("Building Docker image...")
            try:
                subprocess.run(["docker-compose", "down"], cwd=self.script_dir, timeout=30)
                result = subprocess.run(["docker-compose", "build"], cwd=self.script_dir, timeout=300)
                if result.returncode != 0:
                    messagebox.showerror("Build Error", "Ошибка сборки Docker образа")
                    return
                print("✅ Docker image built successfully")
            except subprocess.TimeoutExpired:
                messagebox.showerror("Build Error", "Таймаут сборки Docker образа")
                return

        # Подготовка переменных окружения
        env_vars = {
            "PORT": docker_port,
            "FOUNDRY_HOST": "localhost",
            "FOUNDRY_PORT": "50477",
            "RAG_ENABLED": str(self.rag_enabled_var.get()).lower()
        }

        if self.api_key_var.get():
            env_vars["API_KEY"] = self.api_key_var.get()

        # Остановка существующего контейнера
        print("Stopping existing containers...")
        subprocess.run(["docker-compose", "down"], cwd=self.script_dir, timeout=30)

        # Запуск контейнера
        print("Starting Docker container...")
        env_string = " ".join(f"{k}={v}" for k, v in env_vars.items())
        cmd = f"{env_string} docker-compose up -d"

        try:
            result = subprocess.run(cmd, shell=True, cwd=self.script_dir, timeout=60)
            if result.returncode == 0:
                # Проверка статуса
                time.sleep(3)
                status_result = subprocess.run(["docker-compose", "ps", "-q"], cwd=self.script_dir,
                                             capture_output=True, text=True, timeout=10)
                if status_result.stdout.strip():
                    messagebox.showinfo("Docker Success",
                                      f"FastAPI Foundry Docker container started!\n\n"
                                      f"🌐 URL: http://localhost:{docker_port}\n"
                                      f"📚 API Docs: http://localhost:{docker_port}/docs\n"
                                      f"❤️ Health: http://localhost:{docker_port}/api/v1/health\n\n"
                                      f"Container: {container_name}\n\n"
                                      f"Для просмотра логов: docker-compose logs -f\n"
                                      f"Для остановки: docker-compose down")
                else:
                    messagebox.showwarning("Docker Warning", "Контейнер запущен, но статус неизвестен.\nПроверьте: docker-compose logs")
            else:
                messagebox.showerror("Docker Error", "Ошибка запуска контейнера")
        except subprocess.TimeoutExpired:
            messagebox.showerror("Docker Error", "Таймаут запуска контейнера")

    def run_normal_mode(self):
        """Запуск в обычном режиме"""
        # Разрешение конфликтов портов
        try:
            resolved_port = self.resolve_port_conflict(int(self.port_var.get()))
            if resolved_port != int(self.port_var.get()):
                self.port_var.set(str(resolved_port))
                print(f"🔄 Порт FastAPI изменен на: {resolved_port}")
        except Exception as e:
            print(f"Error resolving port conflict: {e}")

        # Сборка переменных окружения
        env_vars = {
            "FASTAPI_FOUNDRY_MODE": self.mode_var.get(),
            "HOST": self.host_var.get(),
            "PORT": self.port_var.get(),
            "API_WORKERS": str(self.workers_var.get()),
            "API_RELOAD": str(self.reload_var.get()).lower(),
            "LOG_LEVEL": self.log_level_var.get(),
            "FOUNDRY_BASE_URL": self.foundry_url_var.get(),
            "FOUNDRY_DEFAULT_MODEL": self.model_var.get(),
            "FOUNDRY_TEMPERATURE": str(self.temp_var.get()),
            "FOUNDRY_TOP_P": str(self.top_p_var.get()),
            "FOUNDRY_TOP_K": str(self.top_k_var.get()),
            "FOUNDRY_MAX_TOKENS": str(self.max_tokens_var.get()),
            "FOUNDRY_TIMEOUT": str(self.timeout_var.get()),
            "RAG_ENABLED": str(self.rag_enabled_var.get()).lower(),
            "RAG_INDEX_DIR": self.rag_dir_var.get(),
            "RAG_MODEL": self.rag_model_var.get()
        }

        if self.api_key_var.get():
            env_vars["API_KEY"] = self.api_key_var.get()

        # Команда запуска
        env_string = " ".join(f"{k}={v}" for k, v in env_vars.items())
        cmd = f"{env_string} python run.py"

        print("Starting FastAPI Foundry with configuration:")
        print(f"FastAPI Server - Host: {self.host_var.get()} Port: {self.port_var.get()}")
        print(f"Foundry AI Model - URL: {self.foundry_url_var.get()}")
        print(f"Mode: {self.mode_var.get()}")

        try:
            # Запуск в отдельном процессе
            subprocess.Popen(cmd, shell=True, cwd=self.script_dir)
            messagebox.showinfo("Success", "FastAPI Foundry started successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start: {e}")


def main():
    root = tk.Tk()
    app = FastApiFoundryGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()