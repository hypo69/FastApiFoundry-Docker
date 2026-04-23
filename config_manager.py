# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Унифицированный класс конфигурации
# =============================================================================
# Описание:
#   Класс Config для всего проекта FastApiFoundry.
#   Загружает настройки из config.json и предоставляет единый интерфейс доступа.
#
# File: config_manager.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.1
# Изменения в 0.6.1:
#   - Полная русификация документации
#   - Добавлены строгие аннотации типов возвращаемых значений
#   - Комментарии к проверкам `if` в стиле "Проверка ..."
# Author: hypo69
# Copyright: © 2026 hypo69
# License: MIT
# =============================================================================

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class Config:
    """Единый класс конфигурации для всего проекта."""

    _instance = None
    _config_data: Dict[str, Any] = {}
    _foundry_base_url = None  # Dynamically set in run.py

    def __new__(cls):
        if cls._instance is None: # Проверка существования экземпляра (Singleton)
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
            # Инициализация необходимых директорий
            # Initialization of required directories
            cls._instance._ensure_dirs()
        return cls._instance

    def _ensure_dirs(self) -> None:
        """! Создание необходимых директорий проекта.
        
        Обоснование:
          - Гарантированное наличие папки archive для ротации логов и истории сессий.
          - Автоматическое создание при первом запуске (инициализация/инсталляция).
        """
        archive_path: Path = Path('archive')
        if not archive_path.exists(): # Проверка наличия папки
            try:
                archive_path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                logger.error(f"❌ Ошибка создания папки архива: {e}")

    def _load_config(self) -> None:
        """Загрузка конфигурации из файла config.json.

        Raises:
            FileNotFoundError: If config.json does not exist.
            json.JSONDecodeError: If config.json contains invalid JSON.
            OSError: If config.json cannot be read (permissions, lock).
        """
        config_path = Path('config.json')

        if not config_path.is_file(): # Проверка наличия файла конфигурации
            # Файл отсутствует — запуск невозможен; выбрасываем исключение
            raise FileNotFoundError(f'Файл config.json не найден: {config_path.absolute()}')

        _quiet = os.getenv('_UVICORN_CHILD') == '1'
        if not _quiet: # Проверка необходимости вывода логов загрузки
            print(f'Загрузка конфигурации: {config_path.absolute()}')

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config_data = json.load(f)
            if not _quiet: # Проверка вывода структуры секций
                print(f'Конфигурация загружена, секции: {list(self._config_data.keys())}')
        except json.JSONDecodeError as e:
            # Ошибка парсинга JSON — логируем и выбрасываем исключение
            logger.error(f'❌ config.json содержит некорректный JSON: {e}')
            raise
        except OSError as e:
            logger.error(f'❌ Не удалось прочитать config.json: {e}')
            raise

    def reload_config(self) -> None:
        """Перезагрузка конфигурации с диска.

        Raises:
            Same as _load_config().
        """
        self._load_config()

    # ── Сервер FastAPI ────────────────────────────────────────────────────

    @property
    def api_host(self) -> str:
        return self._config_data.get('fastapi_server', {}).get('host') or '0.0.0.0'

    @property
    def api_port(self) -> int:
        return self._config_data.get('fastapi_server', {}).get('port') or 9696

    @property
    def api_workers(self) -> int:
        return self._config_data.get('fastapi_server', {}).get('workers') or 1

    @property
    def api_reload(self) -> bool:
        return self._config_data.get('fastapi_server', {}).get('reload', True)

    @property
    def api_log_level(self) -> str:
        return self._config_data.get('fastapi_server', {}).get('log_level', 'INFO')

    # ── Логирование ───────────────────────────────────────────────────────

    @property
    def logging_retention_hours(self) -> int:
        return self._config_data.get('logging', {}).get('retention_hours') or 24

    @property
    def history_retention_days(self) -> int:
        return self._config_data.get('logging', {}).get('history_retention_days') or 7

    @property
    def archive_max_size_gb(self) -> int:
        return self._config_data.get('logging', {}).get('archive_max_size_gb') or 2

    @property
    def archive_keep_files(self) -> List[str]:
        return self._config_data.get('logging', {}).get('archive_keep_files') or []

    # ── Telegram Admin Bot ────────────────────────────────────────────────

    @property
    def telegram_admin_token(self) -> str:
        """Token for admin_bot. Env: TELEGRAM_ADMIN_TOKEN."""
        return os.getenv('TELEGRAM_ADMIN_TOKEN', '')

    @property
    def telegram_admin_ids(self) -> List[int]:
        """Allowed admin user IDs. Env: TELEGRAM_ADMIN_IDS (comma-separated)."""
        raw = os.getenv('TELEGRAM_ADMIN_IDS', '')
        if raw:
            try:
                return [int(x.strip()) for x in raw.split(',') if x.strip()]
            except ValueError:
                pass
        return self._config_data.get('telegram', {}).get('allowed_external_ids', [])

    @property
    def telegram_status_check_interval(self) -> int:
        return self._config_data.get('telegram', {}).get('status_check_interval', 300)

    # ── Telegram HelpDesk Bot ─────────────────────────────────────────────

    @property
    def telegram_helpdesk_token(self) -> str:
        """Token for helpdesk_bot. Env: TELEGRAM_HELPDESK_TOKEN."""
        return os.getenv('TELEGRAM_HELPDESK_TOKEN', '')

    @property
    def telegram_helpdesk_rag_profile(self) -> str:
        """RAG profile used by helpdesk_bot."""
        return self._config_data.get('telegram_helpdesk', {}).get('rag_profile', 'support')

    # ── Telegram legacy aliases (backward compat) ─────────────────────────

    @property
    def telegram_enabled(self) -> bool:
        return bool(self.telegram_admin_token)

    @property
    def telegram_token(self) -> str:
        """Deprecated: use telegram_admin_token."""
        return self.telegram_admin_token

    @property
    def telegram_allowed_ids(self) -> List[int]:
        """Deprecated: use telegram_admin_ids."""
        return self.telegram_admin_ids

    @property
    def telegram_chat_history_enabled(self) -> bool:
        return self._config_data.get('telegram', {}).get('chat_history_enabled', True)

    @property
    def telegram_chat_history_file(self) -> str:
        return self._config_data.get('telegram', {}).get('chat_history_file', 'session_history.json')

    @property
    def telegram_support_token(self) -> str:
        """Deprecated: use telegram_helpdesk_token."""
        return self.telegram_helpdesk_token

    @property
    def telegram_support_rag_profile(self) -> str:
        """Deprecated: use telegram_helpdesk_rag_profile."""
        return self.telegram_helpdesk_rag_profile

    # ── ИИ Foundry ────────────────────────────────────────────────────────

    @property
    def foundry_base_url(self) -> str:
        # Runtime override (set by run.py after discovery) takes priority.
        # Falls back to static value from config.json.
        if self._foundry_base_url:
            return self._foundry_base_url
        return self._config_data.get('foundry_ai', {}).get('base_url', '') or ''

    @foundry_base_url.setter
    def foundry_base_url(self, value: str) -> None:
        self._foundry_base_url = value

    @property
    def foundry_default_model(self) -> str:
        return self._config_data.get('foundry_ai', {}).get('default_model', '')

    @property
    def foundry_auto_load_default(self) -> bool:
        return self._config_data.get('foundry_ai', {}).get('auto_load_default', False)

    @property
    def foundry_temperature(self) -> float:
        return self._config_data.get('foundry_ai', {}).get('temperature', 0.7)

    @property
    def foundry_max_tokens(self) -> int:
        return self._config_data.get('foundry_ai', {}).get('max_tokens', 2048)

    @property
    def foundry_top_p(self) -> float:
        return self._config_data.get('foundry_ai', {}).get('top_p', 0.9)

    @property
    def foundry_top_k(self) -> int:
        return self._config_data.get('foundry_ai', {}).get('top_k', 50)

    # ── Управление портами ────────────────────────────────────────────────

    @property
    def port_auto_find_free(self) -> bool:
        return self._config_data.get('port_management', {}).get('auto_find_free_port', False)

    @property
    def port_range_start(self) -> int:
        return self._config_data.get('port_management', {}).get('port_range_start', 8000)

    @property
    def port_range_end(self) -> int:
        return self._config_data.get('port_management', {}).get('port_range_end', 8100)

    # ── Система RAG ───────────────────────────────────────────────────────

    @property
    def rag_enabled(self) -> bool:
        return self._config_data.get('rag_system', {}).get('enabled', False)

    @property
    def rag_index_dir(self) -> str:
        raw = self._config_data.get('rag_system', {}).get('index_dir') or '~/.rag'
        return str(Path(raw).expanduser())

    @property
    def rag_model(self) -> str:
        return self._config_data.get('rag_system', {}).get('model', 'sentence-transformers/all-MiniLM-L6-v2')

    @property
    def rag_chunk_size(self) -> int:
        return self._config_data.get('rag_system', {}).get('chunk_size', 1000)

    @property
    def rag_top_k(self) -> int:
        return self._config_data.get('rag_system', {}).get('top_k', 5)

    # ── Директории ────────────────────────────────────────────────────────

    @property
    def dir_models(self) -> str:
        raw = self._config_data.get('directories', {}).get('models') or '~/.models'
        return str(Path(raw).expanduser())

    @property
    def dir_rag(self) -> str:
        raw = self._config_data.get('directories', {}).get('rag') or '~/.rag'
        return str(Path(raw).expanduser())

    @property
    def dir_hf_models(self) -> str:
        raw = self._config_data.get('directories', {}).get('hf_models') or '~/.hf_models'
        return str(Path(raw).expanduser())

    # ── Помощники ─────────────────────────────────────────────────────────

    def get_section(self, section: str) -> Dict[str, Any]:
        """Получение всей секции конфигурации целиком.

        Args:
            section (str): Название секции (например, 'fastapi_server').

        Returns:
            Dict[str, Any]: Содержимое секции или пустой словарь.
        """
        return self._config_data.get(section, {})

    def get_raw_config(self) -> Dict[str, Any]:
        """Получение копии всей конфигурации.

        Returns:
            Dict[str, Any]: Полное содержимое config.json в виде словаря.
        """
        return self._config_data.copy()

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Обновление конфигурации в памяти и сохранение в файл config.json.

        Args:
            new_config (Dict[str, Any]): Новый словарь настроек.

        Raises:
            OSError: При ошибке записи на диск.
        """
        self._config_data = new_config
        config_path = Path('config.json')
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=2, ensure_ascii=False)
        except OSError as e:
            # Запись на диск не удалась — настройки обновлены в памяти, но не сохранены
            logger.error(f'❌ Не удалось записать в config.json: {e}')
            raise


# Global configuration instance
config = Config()
