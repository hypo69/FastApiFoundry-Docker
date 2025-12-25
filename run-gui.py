#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: GUI лончер для FastAPI Foundry
# =============================================================================
# Описание:
#   Кроссплатформенный графический интерфейс для запуска FastAPI Foundry
#   Поддерживает все режимы: локальный запуск, Docker, настройка параметров
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
# Date: 9 декабря 2025
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import time
from pathlib import Path
from launcher_base import LauncherBase

class FastApiFoundryGUILauncher(LauncherBase):
    """GUI лончер для FastAPI Foundry"""
    
    def __init__(self):
        super().__init__()
        self.root = None
        self.widgets = {}
        
    def create_gui(self):
        """Создание GUI интерфейса"""
        self.root = tk.Tk()
        self.root.title("FastAPI Foundry — Launch Configuration")
        self.root.geometry("550x750")
        self.root.resizable(False, False)
        
        # Центрирование окна
        self._center_window()
        
        # Создание интерфейса
        self._create_widgets()
        
    def _center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self):
        """Создание всех виджетов интерфейса"""
        # Создание Notebook (вкладки)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладки
        self._create_fastapi_tab(notebook)
        self._create_foundry_tab(notebook)
        self._create_rag_tab(notebook)
        self._create_docker_tab(notebook)
        
        # Кнопки
        self._create_buttons()
    
    def _create_fastapi_tab(self, notebook):
        """Создание вкладки FastAPI Server"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="FastAPI Server")
        
        # Заголовок
        header = tk.Label(tab, text=f"FastAPI Server Configuration (Port {self.config['fastapi_server']['port']})",
                         font=("Segoe UI", 10, "bold"), fg="darkblue")
        header.pack(pady=(20, 10))
        
        # Контейнер для полей
        frame = tk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=20)
        
        # Mode
        tk.Label(frame, text="FASTAPI_FOUNDRY_MODE:").grid(row=0, column=0, sticky='w', pady=5)
        self.widgets['mode'] = tk.StringVar(value=self.config['fastapi_server']['mode'])
        mode_combo = ttk.Combobox(frame, textvariable=self.widgets['mode'], 
                                 values=["dev", "production"], state="readonly", width=25)
        mode_combo.grid(row=0, column=1, pady=5)
        
        # Host
        tk.Label(frame, text="HOST:").grid(row=1, column=0, sticky='w', pady=5)
        self.widgets['host'] = tk.StringVar(value=self.config['fastapi_server']['host'])
        tk.Entry(frame, textvariable=self.widgets['host'], width=28).grid(row=1, column=1, pady=5)
        
        # Port
        tk.Label(frame, text="PORT (FastAPI Server):").grid(row=2, column=0, sticky='w', pady=5)
        self.widgets['port'] = tk.StringVar(value=str(self.config['fastapi_server']['port']))
        tk.Entry(frame, textvariable=self.widgets['port'], width=28).grid(row=2, column=1, pady=5)
        
        # API Key
        tk.Label(frame, text="API_KEY (optional):").grid(row=3, column=0, sticky='w', pady=5)
        self.widgets['api_key'] = tk.StringVar(value=self.config['security']['api_key'])
        tk.Entry(frame, textvariable=self.widgets['api_key'], show="*", width=28).grid(row=3, column=1, pady=5)
        
        # Workers
        tk.Label(frame, text="API_WORKERS:").grid(row=4, column=0, sticky='w', pady=5)
        self.widgets['workers'] = tk.IntVar(value=self.config['fastapi_server']['workers'])
        tk.Spinbox(frame, from_=1, to=16, textvariable=self.widgets['workers'], width=26).grid(row=4, column=1, pady=5)
        
        # Reload
        self.widgets['reload'] = tk.BooleanVar(value=self.config['fastapi_server']['reload'])
        tk.Checkbutton(frame, text="API_RELOAD (dev mode)", variable=self.widgets['reload']).grid(row=5, column=0, columnspan=2, sticky='w', pady=5)
        
        # Log Level
        tk.Label(frame, text="LOG_LEVEL:").grid(row=6, column=0, sticky='w', pady=5)
        self.widgets['log_level'] = tk.StringVar(value=self.config['logging']['level'])
        log_combo = ttk.Combobox(frame, textvariable=self.widgets['log_level'], 
                               values=["DEBUG", "INFO", "WARNING", "ERROR"], state="readonly", width=25)
        log_combo.grid(row=6, column=1, pady=5)
    
    def _create_foundry_tab(self, notebook):
        """Создание вкладки Foundry AI Model"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Foundry AI Model")
        
        # Заголовок
        header = tk.Label(tab, text="Foundry AI Model Configuration", 
                         font=("Segoe UI", 10, "bold"), fg="darkgreen")
        header.pack(pady=(20, 10))
        
        frame = tk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=20)
        
        # Base URL
        tk.Label(frame, text="FOUNDRY_BASE_URL:").grid(row=0, column=0, sticky='w', pady=5)
        self.widgets['foundry_url'] = tk.StringVar(value=self.config['foundry_ai']['base_url'])
        tk.Entry(frame, textvariable=self.widgets['foundry_url'], width=28).grid(row=0, column=1, pady=5)
        
        # Default Model
        tk.Label(frame, text="FOUNDRY_DEFAULT_MODEL:").grid(row=1, column=0, sticky='w', pady=5)
        self.widgets['model'] = tk.StringVar(value=self.config['foundry_ai']['default_model'])
        tk.Entry(frame, textvariable=self.widgets['model'], width=28).grid(row=1, column=1, pady=5)
        
        # Temperature
        tk.Label(frame, text="FOUNDRY_TEMPERATURE:").grid(row=2, column=0, sticky='w', pady=5)
        self.widgets['temperature'] = tk.DoubleVar(value=self.config['foundry_ai']['temperature'])
        tk.Spinbox(frame, from_=0.0, to=2.0, increment=0.1, textvariable=self.widgets['temperature'], width=26).grid(row=2, column=1, pady=5)
        
        # Top P
        tk.Label(frame, text="FOUNDRY_TOP_P:").grid(row=3, column=0, sticky='w', pady=5)
        self.widgets['top_p'] = tk.DoubleVar(value=self.config['foundry_ai']['top_p'])
        tk.Spinbox(frame, from_=0.0, to=1.0, increment=0.01, textvariable=self.widgets['top_p'], width=26).grid(row=3, column=1, pady=5)
        
        # Top K
        tk.Label(frame, text="FOUNDRY_TOP_K:").grid(row=4, column=0, sticky='w', pady=5)
        self.widgets['top_k'] = tk.IntVar(value=self.config['foundry_ai']['top_k'])
        tk.Spinbox(frame, from_=1, to=200, textvariable=self.widgets['top_k'], width=26).grid(row=4, column=1, pady=5)
        
        # Max Tokens
        tk.Label(frame, text="FOUNDRY_MAX_TOKENS:").grid(row=5, column=0, sticky='w', pady=5)
        self.widgets['max_tokens'] = tk.IntVar(value=self.config['foundry_ai']['max_tokens'])
        tk.Spinbox(frame, from_=1, to=32768, textvariable=self.widgets['max_tokens'], width=26).grid(row=5, column=1, pady=5)
        
        # Timeout
        tk.Label(frame, text="FOUNDRY_TIMEOUT (sec):").grid(row=6, column=0, sticky='w', pady=5)
        self.widgets['timeout'] = tk.IntVar(value=self.config['foundry_ai']['timeout'])
        tk.Spinbox(frame, from_=10, to=3600, textvariable=self.widgets['timeout'], width=26).grid(row=6, column=1, pady=5)
    
    def _create_rag_tab(self, notebook):
        """Создание вкладки RAG System"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="RAG System")
        
        frame = tk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # RAG Enabled
        self.widgets['rag_enabled'] = tk.BooleanVar(value=self.config['rag_system']['enabled'])
        tk.Checkbutton(frame, text="RAG_ENABLED", variable=self.widgets['rag_enabled']).grid(row=0, column=0, columnspan=2, sticky='w', pady=10)
        
        # Index Dir
        tk.Label(frame, text="RAG_INDEX_DIR:").grid(row=1, column=0, sticky='w', pady=5)
        self.widgets['rag_dir'] = tk.StringVar(value=self.config['rag_system']['index_dir'])
        tk.Entry(frame, textvariable=self.widgets['rag_dir'], width=28).grid(row=1, column=1, pady=5)
        
        # Model
        tk.Label(frame, text="RAG_MODEL:").grid(row=2, column=0, sticky='w', pady=5)
        self.widgets['rag_model'] = tk.StringVar(value=self.config['rag_system']['model'])
        rag_models = [
            "sentence-transformers/all-MiniLM-L6-v2",
            "sentence-transformers/all-mpnet-base-v2",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        ]
        rag_combo = ttk.Combobox(frame, textvariable=self.widgets['rag_model'], 
                               values=rag_models, state="readonly", width=25)
        rag_combo.grid(row=2, column=1, pady=5)
    
    def _create_docker_tab(self, notebook):
        """Создание вкладки Docker"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Docker")
        
        frame = tk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Docker Mode
        self.widgets['docker_mode'] = tk.BooleanVar(value=False)
        tk.Checkbutton(frame, text="Запуск из Docker контейнера", variable=self.widgets['docker_mode'],
                      font=("Segoe UI", 10, "bold"), fg="darkblue").grid(row=0, column=0, columnspan=2, sticky='w', pady=10)
        
        # Info
        info_text = "При включении Docker режима run.py будет запущен внутри контейнера\nчерез docker-compose. Убедитесь что Docker Desktop запущен."
        tk.Label(frame, text=info_text, fg="gray", justify="left").grid(row=1, column=0, columnspan=2, sticky='w', pady=10)
        
        # Container Name
        tk.Label(frame, text="Container Name:").grid(row=2, column=0, sticky='w', pady=5)
        self.widgets['container_name'] = tk.StringVar(value="fastapi-foundry-docker")
        tk.Entry(frame, textvariable=self.widgets['container_name'], width=28).grid(row=2, column=1, pady=5)
        
        # Docker Port
        tk.Label(frame, text="Host Port (внешний):").grid(row=3, column=0, sticky='w', pady=5)
        self.widgets['docker_port'] = tk.StringVar(value="8000")
        tk.Entry(frame, textvariable=self.widgets['docker_port'], width=28).grid(row=3, column=1, pady=5)
        
        # Build Option
        self.widgets['docker_build'] = tk.BooleanVar(value=False)
        tk.Checkbutton(frame, text="Пересобрать образ перед запуском (--build)", 
                      variable=self.widgets['docker_build']).grid(row=4, column=0, columnspan=2, sticky='w', pady=10)
    
    def _create_buttons(self):
        """Создание кнопок управления"""
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Кнопка запуска
        run_button = tk.Button(button_frame, text="🚀 RUN", command=self._run_application,
                              font=("Segoe UI", 12, "bold"), bg="lightgreen", width=12, height=2)
        run_button.pack(side='right', padx=(10, 0))
        
        # Кнопка закрытия
        close_button = tk.Button(button_frame, text="❌ CLOSE", command=self.root.quit,
                                font=("Segoe UI", 12), width=12, height=2)
        close_button.pack(side='right')
    
    def _get_gui_values(self):
        """Получение значений из GUI"""
        return {
            'mode': self.widgets['mode'].get(),
            'host': self.widgets['host'].get(),
            'port': int(self.widgets['port'].get()),
            'api_key': self.widgets['api_key'].get(),
            'workers': self.widgets['workers'].get(),
            'reload': self.widgets['reload'].get(),
            'log_level': self.widgets['log_level'].get(),
            'foundry_url': self.widgets['foundry_url'].get(),
            'model': self.widgets['model'].get(),
            'temperature': self.widgets['temperature'].get(),
            'top_p': self.widgets['top_p'].get(),
            'top_k': self.widgets['top_k'].get(),
            'max_tokens': self.widgets['max_tokens'].get(),
            'timeout': self.widgets['timeout'].get(),
            'rag_enabled': self.widgets['rag_enabled'].get(),
            'rag_dir': self.widgets['rag_dir'].get(),
            'rag_model': self.widgets['rag_model'].get(),
            'docker_mode': self.widgets['docker_mode'].get(),
            'container_name': self.widgets['container_name'].get(),
            'docker_port': int(self.widgets['docker_port'].get()),
            'docker_build': self.widgets['docker_build'].get()
        }
    
    def _run_application(self):
        """Запуск приложения"""
        try:
            values = self._get_gui_values()
            
            if not self.validate_config(**values):
                return
            
            if values['docker_mode']:
                success = self.run_docker_mode(**values)
            else:
                success = self.run_normal_mode(**values)
            
            if success:
                messagebox.showinfo("Success", "FastAPI Foundry started successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start: {e}")
    
    def run_normal_mode(self, **kwargs) -> bool:
        """Запуск в обычном режиме"""
        try:
            # Разрешение конфликтов портов
            port = kwargs.get('port', self.config['fastapi_server']['port'])
            resolved_port = self.resolve_port_conflict(port)
            if resolved_port != port:
                kwargs['port'] = resolved_port
                self.widgets['port'].set(str(resolved_port))
                self.log_info(f"🔄 Порт FastAPI изменен на: {resolved_port}")
            
            # Построение переменных окружения
            env_vars = self.build_env_vars(**kwargs)
            
            # Команда запуска
            cmd = ["python", "run.py"]
            
            # Добавление аргументов
            if kwargs.get('host'):
                cmd.extend(['--host', kwargs['host']])
            if kwargs.get('port'):
                cmd.extend(['--port', str(kwargs['port'])])
            if kwargs.get('mode'):
                cmd.extend(['--mode', kwargs['mode']])
            if kwargs.get('workers'):
                cmd.extend(['--workers', str(kwargs['workers'])])
            if kwargs.get('reload'):
                cmd.append('--reload')
            if kwargs.get('log_level'):
                cmd.extend(['--log-level', kwargs['log_level']])
            
            self.log_info("Starting FastAPI Foundry with configuration:")
            self.log_info(f"FastAPI Server - Host: {kwargs.get('host')} Port: {kwargs.get('port')}")
            self.log_info(f"Foundry AI Model - URL: {kwargs.get('foundry_url')}")
            self.log_info(f"Mode: {kwargs.get('mode')}")
            
            # Запуск в отдельном процессе
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                env={**os.environ, **env_vars}
            )
            
            return True
            
        except Exception as e:
            self.log_error(f"Failed to start in normal mode: {e}")
            return False
    
    def run_docker_mode(self, **kwargs) -> bool:
        """Запуск в Docker режиме"""
        try:
            self.log_info("Starting FastAPI Foundry in Docker container...")
            
            # Проверка Docker
            docker_ok, docker_version = self.check_docker()
            if not docker_ok:
                messagebox.showerror("Docker Error", f"Docker недоступен: {docker_version}")
                return False
            
            self.log_success(f"Docker запущен (версия: {docker_version})")
            
            # Разрешение конфликтов портов
            docker_port = kwargs.get('docker_port', 8000)
            resolved_port = self.resolve_port_conflict(docker_port)
            if resolved_port != docker_port:
                kwargs['docker_port'] = resolved_port
                self.widgets['docker_port'].set(str(resolved_port))
                self.log_info(f"🔄 Порт Docker изменен на: {resolved_port}")
            
            # Проверка образа
            if kwargs.get('docker_build', False):
                self.log_info("Building Docker image...")
                try:
                    subprocess.run(["docker-compose", "down"], cwd=self.project_root, timeout=30)
                    result = subprocess.run(["docker-compose", "build"], cwd=self.project_root, timeout=300)
                    if result.returncode != 0:
                        messagebox.showerror("Build Error", "Ошибка сборки Docker образа")
                        return False
                    self.log_success("Docker image built successfully")
                except subprocess.TimeoutExpired:
                    messagebox.showerror("Build Error", "Таймаут сборки Docker образа")
                    return False
            
            # Подготовка переменных окружения
            env_vars = {
                "PORT": str(resolved_port),
                "FOUNDRY_HOST": "localhost",
                "FOUNDRY_PORT": "50477",
                "RAG_ENABLED": str(kwargs.get('rag_enabled', True)).lower()
            }
            
            if kwargs.get('api_key'):
                env_vars["API_KEY"] = kwargs['api_key']
            
            # Остановка существующего контейнера
            self.log_info("Stopping existing containers...")
            subprocess.run(["docker-compose", "down"], cwd=self.project_root, timeout=30)
            
            # Запуск контейнера
            self.log_info("Starting Docker container...")
            
            # Обновление переменных окружения
            import os
            for key, value in env_vars.items():
                os.environ[key] = value
            
            result = subprocess.run(["docker-compose", "up", "-d"], cwd=self.project_root, timeout=60)
            if result.returncode == 0:
                # Проверка статуса
                time.sleep(3)
                status_result = subprocess.run(["docker-compose", "ps", "-q"], cwd=self.project_root,
                                             capture_output=True, text=True, timeout=10)
                if status_result.stdout.strip():
                    messagebox.showinfo("Docker Success",
                                      f"FastAPI Foundry Docker container started!\n\n"
                                      f"🌐 URL: http://localhost:{resolved_port}\n"
                                      f"📚 API Docs: http://localhost:{resolved_port}/docs\n"
                                      f"❤️ Health: http://localhost:{resolved_port}/api/v1/health\n\n"
                                      f"Container: {kwargs.get('container_name')}\n\n"
                                      f"Для просмотра логов: docker-compose logs -f\n"
                                      f"Для остановки: docker-compose down")
                    return True
                else:
                    messagebox.showwarning("Docker Warning", "Контейнер запущен, но статус неизвестен.\nПроверьте: docker-compose logs")
                    return False
            else:
                messagebox.showerror("Docker Error", "Ошибка запуска контейнера")
                return False
                
        except subprocess.TimeoutExpired:
            messagebox.showerror("Docker Error", "Таймаут запуска контейнера")
            return False
        except Exception as e:
            self.log_error(f"Failed to start in Docker mode: {e}")
            return False
    
    def run(self):
        """Запуск GUI"""
        self.create_gui()
        self.root.mainloop()

def main():
    """Главная функция"""
    launcher = FastApiFoundryGUILauncher()
    launcher.run()

if __name__ == "__main__":
    main()