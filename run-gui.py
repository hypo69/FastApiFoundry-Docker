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

import os
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import time
from pathlib import Path
from launcher_base import LauncherBase
from src.utils.port_manager import ensure_port_free

class FastApiFoundryGUILauncher(LauncherBase):
    """GUI лончер для FastAPI Foundry"""
    
    def __init__(self):
        super().__init__()
        self.root = None
        self.widgets = {}
        
    def create_gui(self):
        """Создание GUI интерфейса"""
        self.root = tk.Tk()
        self.root.title("FastAPI Foundry — Конфигурация запуска")
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
        notebook.add(tab, text="Сервер FastAPI")
        
        # Заголовок
        header = tk.Label(tab, text=f"Конфигурация сервера FastAPI (Порт {self.config['fastapi_server']['port']})",
                         font=("Segoe UI", 10, "bold"), fg="darkblue")
        header.pack(pady=(20, 10))
        
        # Контейнер для полей
        frame = tk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=20)
        
        # Режим
        tk.Label(frame, text="РЕЖИМ:").grid(row=0, column=0, sticky='w', pady=5)
        self.widgets['mode'] = tk.StringVar(value=self.config['fastapi_server']['mode'])
        mode_combo = ttk.Combobox(frame, textvariable=self.widgets['mode'], 
                                 values=["разработка", "продакшн"], state="readonly", width=25)
        mode_combo.grid(row=0, column=1, pady=5)
        
        # Хост
        tk.Label(frame, text="ХОСТ:").grid(row=1, column=0, sticky='w', pady=5)
        self.widgets['host'] = tk.StringVar(value=self.config['fastapi_server']['host'])
        tk.Entry(frame, textvariable=self.widgets['host'], width=28).grid(row=1, column=1, pady=5)
        
        # Порт
        tk.Label(frame, text="ПОРТ:").grid(row=2, column=0, sticky='w', pady=5)
        self.widgets['port'] = tk.StringVar(value=str(self.config['fastapi_server']['port']))
        tk.Entry(frame, textvariable=self.widgets['port'], width=28).grid(row=2, column=1, pady=5)
        
        # API ключ
        tk.Label(frame, text="API КЛЮЧ (опционально):").grid(row=3, column=0, sticky='w', pady=5)
        self.widgets['api_key'] = tk.StringVar(value=self.config['security']['api_key'])
        tk.Entry(frame, textvariable=self.widgets['api_key'], show="*", width=28).grid(row=3, column=1, pady=5)
        
        # Воркеры
        tk.Label(frame, text="ВОРКЕРЫ:").grid(row=4, column=0, sticky='w', pady=5)
        self.widgets['workers'] = tk.IntVar(value=self.config['fastapi_server']['workers'])
        tk.Spinbox(frame, from_=1, to=16, textvariable=self.widgets['workers'], width=26).grid(row=4, column=1, pady=5)
        
        # Автоперезагрузка
        self.widgets['reload'] = tk.BooleanVar(value=self.config['fastapi_server']['reload'])
        tk.Checkbutton(frame, text="Автоперезагрузка (режим разработки)", variable=self.widgets['reload']).grid(row=5, column=0, columnspan=2, sticky='w', pady=5)
        
        # Уровень логов
        tk.Label(frame, text="УРОВЕНЬ ЛОГОВ:").grid(row=6, column=0, sticky='w', pady=5)
        self.widgets['log_level'] = tk.StringVar(value=self.config['logging']['level'])
        log_combo = ttk.Combobox(frame, textvariable=self.widgets['log_level'], 
                               values=["ОТЛАДКА", "ИНФО", "ПРЕДУПРЕЖДЕНИЕ", "ОШИБКА"], state="readonly", width=25)
        log_combo.grid(row=6, column=1, pady=5)
    
    def _create_foundry_tab(self, notebook):
        """Создание вкладки Foundry AI Model"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Модель Foundry AI")
        
        # Заголовок
        header = tk.Label(tab, text="Конфигурация модели Foundry AI", 
                         font=("Segoe UI", 10, "bold"), fg="darkgreen")
        header.pack(pady=(20, 10))
        
        frame = tk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=20)
        
        # Базовый URL
        tk.Label(frame, text="БАЗОВЫЙ URL:").grid(row=0, column=0, sticky='w', pady=5)
        self.widgets['foundry_url'] = tk.StringVar(value=self.config['foundry_ai']['base_url'])
        tk.Entry(frame, textvariable=self.widgets['foundry_url'], width=28).grid(row=0, column=1, pady=5)
        
        # Модель по умолчанию
        tk.Label(frame, text="МОДЕЛЬ ПО УМОЛЧАНИЮ:").grid(row=1, column=0, sticky='w', pady=5)
        self.widgets['model'] = tk.StringVar(value=self.config['foundry_ai']['default_model'])
        tk.Entry(frame, textvariable=self.widgets['model'], width=28).grid(row=1, column=1, pady=5)
        
        # Температура
        tk.Label(frame, text="ТЕМПЕРАТУРА:").grid(row=2, column=0, sticky='w', pady=5)
        self.widgets['temperature'] = tk.DoubleVar(value=self.config['foundry_ai']['temperature'])
        tk.Spinbox(frame, from_=0.0, to=2.0, increment=0.1, textvariable=self.widgets['temperature'], width=26).grid(row=2, column=1, pady=5)
        
        # Top P
        tk.Label(frame, text="TOP P:").grid(row=3, column=0, sticky='w', pady=5)
        self.widgets['top_p'] = tk.DoubleVar(value=self.config['foundry_ai']['top_p'])
        tk.Spinbox(frame, from_=0.0, to=1.0, increment=0.01, textvariable=self.widgets['top_p'], width=26).grid(row=3, column=1, pady=5)
        
        # Top K
        tk.Label(frame, text="TOP K:").grid(row=4, column=0, sticky='w', pady=5)
        self.widgets['top_k'] = tk.IntVar(value=self.config['foundry_ai']['top_k'])
        tk.Spinbox(frame, from_=1, to=200, textvariable=self.widgets['top_k'], width=26).grid(row=4, column=1, pady=5)
        
        # Максимум токенов
        tk.Label(frame, text="МАКС ТОКЕНОВ:").grid(row=5, column=0, sticky='w', pady=5)
        self.widgets['max_tokens'] = tk.IntVar(value=self.config['foundry_ai']['max_tokens'])
        tk.Spinbox(frame, from_=1, to=32768, textvariable=self.widgets['max_tokens'], width=26).grid(row=5, column=1, pady=5)
        
        # Таймаут
        tk.Label(frame, text="ТАЙМАУТ (сек):").grid(row=6, column=0, sticky='w', pady=5)
        self.widgets['timeout'] = tk.IntVar(value=self.config['foundry_ai']['timeout'])
        tk.Spinbox(frame, from_=10, to=3600, textvariable=self.widgets['timeout'], width=26).grid(row=6, column=1, pady=5)
    
    def _create_rag_tab(self, notebook):
        """Создание вкладки RAG System"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Система RAG")
        
        frame = tk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Включить RAG
        self.widgets['rag_enabled'] = tk.BooleanVar(value=self.config['rag_system']['enabled'])
        tk.Checkbutton(frame, text="ВКЛЮЧИТЬ RAG", variable=self.widgets['rag_enabled']).grid(row=0, column=0, columnspan=2, sticky='w', pady=10)
        
        # Папка индекса
        tk.Label(frame, text="ПАПКА ИНДЕКСА:").grid(row=1, column=0, sticky='w', pady=5)
        self.widgets['rag_dir'] = tk.StringVar(value=self.config['rag_system']['index_dir'])
        tk.Entry(frame, textvariable=self.widgets['rag_dir'], width=28).grid(row=1, column=1, pady=5)
        
        # Модель RAG
        tk.Label(frame, text="МОДЕЛЬ RAG:").grid(row=2, column=0, sticky='w', pady=5)
        self.widgets['rag_model'] = tk.StringVar(value=self.config['rag_system']['model'])
        tk.Entry(frame, textvariable=self.widgets['rag_model'], width=28).grid(row=2, column=1, pady=5)
    
    def _create_docker_tab(self, notebook):
        """Создание вкладки Docker"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Docker")
        
        frame = tk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Информация о Docker
        docker_available, docker_info = self.check_docker()
        status_color = "green" if docker_available else "red"
        status_text = f"Docker: {'Доступен' if docker_available else 'Недоступен'}"
        
        tk.Label(frame, text=status_text, fg=status_color, font=("Segoe UI", 10, "bold")).pack(pady=10)
        
        if docker_available:
            tk.Label(frame, text=f"Версия: {docker_info}", fg="gray").pack()
        
        # Опции Docker
        self.widgets['docker_build'] = tk.BooleanVar(value=False)
        tk.Checkbutton(frame, text="Пересобрать образ Docker", variable=self.widgets['docker_build']).pack(pady=5)
        
        self.widgets['docker_detached'] = tk.BooleanVar(value=True)
        tk.Checkbutton(frame, text="Запуск в фоне (-d)", variable=self.widgets['docker_detached']).pack(pady=5)
    
    def _create_buttons(self):
        """Создание кнопок управления"""
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        # Кнопка запуска
        start_btn = tk.Button(
            button_frame, 
            text="🚀 Запустить FastAPI Foundry", 
            command=self._start_server,
            bg="#4CAF50", 
            fg="white", 
            font=("Segoe UI", 10, "bold"),
            height=2
        )
        start_btn.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Кнопка Docker запуска
        docker_btn = tk.Button(
            button_frame, 
            text="🐳 Запустить с Docker", 
            command=self._start_docker,
            bg="#2196F3", 
            fg="white", 
            font=("Segoe UI", 10, "bold"),
            height=2
        )
        docker_btn.pack(side='left', fill='x', expand=True, padx=5)
        
        # Кнопка выхода
        exit_btn = tk.Button(
            button_frame, 
            text="❌ Выход", 
            command=self.root.quit,
            bg="#f44336", 
            fg="white", 
            font=("Segoe UI", 10, "bold"),
            height=2
        )
        exit_btn.pack(side='right', padx=(5, 0))
    
    def _get_gui_config(self) -> dict:
        """Получение конфигурации из GUI"""
        # Преобразование русских значений в английские
        mode_map = {"разработка": "dev", "продакшн": "production"}
        log_level_map = {"ОТЛАДКА": "DEBUG", "ИНФО": "INFO", "ПРЕДУПРЕЖДЕНИЕ": "WARNING", "ОШИБКА": "ERROR"}
        
        return {
            'host': self.widgets['host'].get(),
            'port': int(self.widgets['port'].get()),
            'mode': mode_map.get(self.widgets['mode'].get(), "dev"),
            'workers': self.widgets['workers'].get(),
            'reload': self.widgets['reload'].get(),
            'log_level': log_level_map.get(self.widgets['log_level'].get(), "INFO"),
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
            'api_key': self.widgets['api_key'].get()
        }
    
    def _start_server(self):
        """Запуск сервера в обычном режиме"""
        try:
            config = self._get_gui_config()
            
            # Проверка и освобождение порта
            port = config['port']
            if not ensure_port_free(port):
                messagebox.showerror("Ошибка", f"Не удалось освободить порт {port}")
                return
            
            if not self.validate_config(**config):
                messagebox.showerror("Ошибка конфигурации", "Неверная конфигурация. Проверьте логи.")
                return
            
            self.log_info("Запуск FastAPI Foundry с конфигурацией:")
            self.log_info(f"Сервер FastAPI - Хост: {config['host']} Порт: {config['port']}")
            self.log_info(f"Модель Foundry AI - URL: {config['foundry_url']}")
            self.log_info(f"Режим: {config['mode']}")
            
            success = self.run_normal_mode(**config)
            
            if success:
                self.log_success("FastAPI Foundry успешно запущен!")
                messagebox.showinfo("Успех", "FastAPI Foundry успешно запущен!")
            else:
                self.log_error("Не удалось запустить FastAPI Foundry")
                messagebox.showerror("Ошибка", "Не удалось запустить FastAPI Foundry. Проверьте логи.")
                
        except Exception as e:
            self.log_error(f"Ошибка запуска в обычном режиме: {e}")
            messagebox.showerror("Ошибка", f"Ошибка запуска: {e}")
    
    def _start_docker(self):
        """Запуск сервера в Docker режиме"""
        try:
            config = self._get_gui_config()
            config['docker_build'] = self.widgets['docker_build'].get()
            config['docker_detached'] = self.widgets['docker_detached'].get()
            
            self.log_info("Запуск FastAPI Foundry с Docker:")
            self.log_info(f"Порт: {config['port']}")
            self.log_info(f"Сборка: {config['docker_build']}")
            self.log_info(f"В фоне: {config['docker_detached']}")
            
            success = self.run_docker_mode(**config)
            
            if success:
                self.log_success("FastAPI Foundry Docker успешно запущен!")
                messagebox.showinfo("Успех", "FastAPI Foundry Docker успешно запущен!")
            else:
                self.log_error("Не удалось запустить FastAPI Foundry Docker")
                messagebox.showerror("Ошибка", "Не удалось запустить Docker. Проверьте логи.")
                
        except Exception as e:
            self.log_error(f"Ошибка запуска в Docker режиме: {e}")
            messagebox.showerror("Ошибка", f"Ошибка запуска Docker: {e}")
    
    def run_normal_mode(self, **kwargs) -> bool:
        """Запуск в обычном режиме"""
        try:
            # Импорт и запуск run.py
            from run import FastAPILauncher
            launcher = FastAPILauncher()
            return launcher.run_normal_mode(**kwargs)
        except Exception as e:
            self.log_error(f"Ошибка запуска обычного режима: {e}")
            return False
    
    def run_docker_mode(self, **kwargs) -> bool:
        """Запуск в Docker режиме"""
        try:
            # Импорт Docker лончера
            from docker_launcher import DockerPythonLauncher
            docker_launcher = DockerPythonLauncher()
            
            self.log_info("Запуск FastAPI Foundry через Docker...")
            return docker_launcher.run_fastapi()
        except Exception as e:
            self.log_error(f"Ошибка запуска Docker режима: {e}")
            return False
    
    def run(self):
        """Запуск GUI"""
        self.create_gui()
        self.root.mainloop()

if __name__ == "__main__":
    launcher = FastApiFoundryGUILauncher()
    launcher.run()