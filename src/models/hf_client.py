# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: HuggingFace Local Model Client
# =============================================================================
# Описание:
#   Клиент для работы с локальными HuggingFace моделями.
#   Поддерживает скачивание через huggingface_hub, загрузку в память
#   и inference через transformers pipeline.
#
# Примеры:
#   >>> from src.models.hf_client import hf_client
#   >>> await hf_client.download_model("google/gemma-2b")
#   >>> result = await hf_client.generate("Hello", model_id="google/gemma-2b")
#
# File: src/models/hf_client.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Директория для сохранения моделей: ~/.models/hf
# Читаем напрямую из окружения, игнорируя config.json чтобы избежать подстановки ${VAR}
def _get_models_dir() -> Path:
    raw = os.environ.get("HF_MODELS_DIR", "")
    if raw and not raw.startswith("${"):
        return Path(raw).expanduser()
    return Path.home() / ".models"

HF_MODELS_DIR = _get_models_dir()

# Стандартный кэш HuggingFace — сканируется дополнительно в list_downloaded()
HF_CACHE_DIR = Path.home() / ".cache" / "huggingface" / "hub"

# Загруженные в память модели: {model_id: {"pipeline": Pipeline, "tokenizer": Tokenizer}}
# Хранится на уровне модуля — один экземпляр на весь процесс FastAPI.
_loaded_models: dict = {}


def _check_transformers() -> bool:
    """! Проверить доступность библиотеки transformers.

    Returns:
        bool: True если установлена, False если нет.
    """
    try:
        import transformers  # noqa
        return True
    except ImportError:
        return False


def _check_huggingface_hub() -> bool:
    """! Проверить доступность библиотеки huggingface_hub.

    Returns:
        bool: True если установлена, False если нет.
    """
    try:
        import huggingface_hub  # noqa
        return True
    except ImportError:
        return False


class HFClient:
    """! Клиент для локальных HuggingFace моделей.

    Отвечает за:
    - Скачивание моделей через huggingface-cli в ~/.models/hf
    - Загрузку в память через transformers pipeline
    - Инференс через загруженный pipeline
    - Выгрузку из памяти с очисткой CUDA кэша

    Глобальный синглтон: hf_client = HFClient()
    """

    def download_model(self, model_id: str, token: Optional[str] = None) -> dict:
        """! Скачать модель через huggingface_hub.snapshot_download.

        Токен берётся из HF_TOKEN в .env.
        Модель сохраняется в HF_MODELS_DIR/<author>--<name>.

        Args:
            model_id: Например 'mistralai/Mistral-7B-Instruct-v0.3'.
            token:    Опциональный переопределяющий токен.

        Returns:
            dict: {"success": bool, "path": str, "error": str}
        """
        if not _check_huggingface_hub():
            return {"success": False, "error": "huggingface_hub не установлен. Запустите: pip install huggingface_hub"}

        from huggingface_hub import snapshot_download

        hf_token = token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        save_dir = HF_MODELS_DIR / model_id.replace("/", "--")
        save_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"📥 Скачивание {model_id} → {save_dir}")

        try:
            path = snapshot_download(
                repo_id=model_id,
                local_dir=str(save_dir),
                token=hf_token or None,
                ignore_patterns=["*.msgpack", "*.h5", "flax_model*", "tf_model*"],
            )
            logger.info(f"✅ {model_id} скачан: {path}")
            return {"success": True, "model_id": model_id, "path": path}
        except Exception as e:
            err = str(e)
            logger.error(f"❌ Ошибка скачивания {model_id}: {err}")
            if "401" in err or "403" in err or "gated" in err.lower() or "access" in err.lower():
                err = f"Нет доступа. Примите лицензию на huggingface.co/{model_id} и установите HF_TOKEN"
            return {"success": False, "error": err}

    def load_model(self, model_id: str, device: str = "auto") -> dict:
        """! Загрузить модель в память для inference.

        Args:
            model_id: ID модели или путь к локальной директории.
            device: 'auto', 'cpu', 'cuda'.

        Returns:
            dict: {"success": bool, "model_id": str, "device": str}
        """
        if not _check_transformers():
            return {"success": False, "error": "transformers не установлен. Запустите: pip install transformers accelerate"}

        if model_id in _loaded_models:
            return {"success": True, "model_id": model_id, "status": "already_loaded"}

        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

            # Ищем локальный путь: HF_MODELS_DIR → HF_CACHE_DIR → скачать
            dir_name = f"models--{model_id.replace('/', '--')}"
            local_path = None
            for base in (HF_MODELS_DIR, HF_CACHE_DIR):
                candidate = base / dir_name / "snapshots"
                if candidate.exists():
                    dirs = [s for s in candidate.iterdir() if s.is_dir()]
                    if dirs:
                        local_path = str(dirs[0])
                        break

            model_path = local_path or model_id
            local_files_only = local_path is not None
            hf_token = None if local_files_only else (os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN"))

            logger.info(f"Загрузка {model_id} из {'local: ' + model_path if local_files_only else 'HuggingFace Hub'}")

            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

            tokenizer = AutoTokenizer.from_pretrained(
                model_path, token=hf_token, local_files_only=local_files_only
            )
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch_dtype,
                device_map=device,
                token=hf_token,
                local_files_only=local_files_only
            )

            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
            )

            _loaded_models[model_id] = {"pipeline": pipe, "tokenizer": tokenizer}
            actual_device = str(next(model.parameters()).device)
            logger.info(f"✅ Модель {model_id} загружена на {actual_device}")
            return {"success": True, "model_id": model_id, "device": actual_device}

        except Exception as e:
            logger.error(f"❌ Ошибка загрузки {model_id}: {e}")
            return {"success": False, "error": str(e)}

    def unload_model(self, model_id: str) -> dict:
        """! Выгрузить модель из памяти."""
        if model_id not in _loaded_models:
            return {"success": False, "error": f"Модель {model_id} не загружена"}
        try:
            import gc, torch
            del _loaded_models[model_id]
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info(f"✅ Модель {model_id} выгружена")
            return {"success": True, "model_id": model_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def generate(self, prompt: str, model_id: str,
                       max_new_tokens: int = 512,
                       temperature: float = 0.7) -> dict:
        """! Генерация текста через загруженную HF модель.

        Args:
            prompt: Входной текст.
            model_id: ID загруженной модели.
            max_new_tokens: Максимальное количество новых токенов.
            temperature: Температура генерации.

        Returns:
            dict: {"success": bool, "content": str, "model": str}
        """
        if model_id not in _loaded_models:
            # Попробуем загрузить автоматически
            load_result = await asyncio.get_event_loop().run_in_executor(
                None, self.load_model, model_id
            )
            if not load_result["success"]:
                return {"success": False, "error": f"Модель не загружена: {load_result['error']}"}

        try:
            pipe = _loaded_models[model_id]["pipeline"]

            def _run():
                outputs = pipe(
                    prompt,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=temperature > 0,
                    pad_token_id=pipe.tokenizer.eos_token_id,
                    return_full_text=False
                )
                return outputs[0]["generated_text"]

            content = await asyncio.get_event_loop().run_in_executor(None, _run)
            return {"success": True, "content": content, "model": model_id}

        except Exception as e:
            logger.error(f"❌ Ошибка генерации {model_id}: {e}")
            return {"success": False, "error": str(e)}

    def list_downloaded(self) -> list:
        """! Список скачанных моделей.

        Сканирует две директории:
        - HF_MODELS_DIR (~/.models по умолчанию или из .env)
        - ~/.cache/huggingface/hub (стандартный кэш HuggingFace)

        Returns:
            list: [{"id": str, "path": str, "loaded": bool, "size_mb": float, "source": str}]
        """
        def _dir_size_mb(d: Path) -> float:
            try:
                return round(sum(f.stat().st_size for f in d.rglob("*") if f.is_file()) / 1024 / 1024, 1)
            except Exception:
                return 0.0

        def _scan_dir(base: Path, source: str) -> list:
            if not base.exists():
                return []
            results = []
            for d in base.iterdir():
                if not d.is_dir() or not d.name.startswith("models--"):
                    continue
                model_id = d.name[len("models--"):].replace("--", "/", 1)
                snapshots_dir = d / "snapshots"
                if snapshots_dir.exists():
                    snapshot_dirs = [s for s in snapshots_dir.iterdir() if s.is_dir()]
                    path = str(snapshot_dirs[0]) if snapshot_dirs else str(d)
                else:
                    path = str(d)
                results.append({
                    "id": model_id,
                    "path": path,
                    "loaded": model_id in _loaded_models,
                    "size_mb": _dir_size_mb(d),
                    "source": source,
                })
            return results

        # Сканируем обе директории, дедуплицируем по model_id
        seen: set = set()
        results = []
        for model in _scan_dir(HF_MODELS_DIR, "~/.models") + _scan_dir(HF_CACHE_DIR, "~/.cache/huggingface/hub"):
            if model["id"] not in seen:
                seen.add(model["id"])
                results.append(model)

        return sorted(results, key=lambda x: x["id"])

    def list_loaded(self) -> list:
        """! Список моделей загруженных в память.

        Returns:
            list: [{"id": str, "status": "loaded"}]
        """
        return [{"id": k, "status": "loaded"} for k in _loaded_models]


hf_client = HFClient()
