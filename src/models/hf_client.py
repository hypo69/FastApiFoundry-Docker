# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: HuggingFace Local Model Client
# =============================================================================
# Description:
#   Client for working with local HuggingFace models.
#   Supports downloading via huggingface_hub, loading into memory,
#   and inference via transformers pipeline.
#
# Examples:
#   >>> from src.models.hf_client import hf_client
#   >>> await hf_client.download_model("google/gemma-2b")
#   >>> result = await hf_client.generate("Hello", model_id="google/gemma-2b")
#
# File: src/models/hf_client.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Directory for saving models — read from config.json first, HF_MODELS_DIR env as legacy fallback
def _get_models_dir() -> Path:
    """Return HuggingFace models directory.

    Priority:
        1. ``directories.hf_models`` from config.json
        2. ``HF_MODELS_DIR`` environment variable (legacy)
        3. ``~/.cache/huggingface/hub`` default (standard HuggingFace cache)

    Returns:
        Path: Resolved absolute path to the models directory.
    """
    try:
        from ..core.config import config
        cfg_dir = config.dir_hf_models
        if cfg_dir and not cfg_dir.startswith("${"):
            return Path(cfg_dir).expanduser()
    except Exception:
        pass
    # Legacy fallback: HF_MODELS_DIR env var
    raw = os.environ.get("HF_MODELS_DIR", "")
    if raw and not raw.startswith("${"):
        return Path(raw).expanduser()
    return Path.home() / ".cache" / "huggingface" / "hub"

HF_MODELS_DIR = _get_models_dir()

# Standard HuggingFace cache — same as HF_MODELS_DIR default, kept for explicit reference
HF_CACHE_DIR = Path.home() / ".cache" / "huggingface" / "hub"

# Models loaded into memory: {model_id: {"pipeline": Pipeline, "tokenizer": Tokenizer}}
# Stored at module level — one instance for the entire FastAPI process.
_loaded_models: dict = {}


def _check_transformers() -> bool:
    """! Check availability of the transformers library.

    Returns:
        bool: True if installed, False otherwise.
    """
    try:
        import transformers  # noqa
        return True
    except ImportError:
        return False


def _check_huggingface_hub() -> bool:
    """! Check availability of the huggingface_hub library.

    Returns:
        bool: True if installed, False otherwise.
    """
    try:
        import huggingface_hub  # noqa
        return True
    except ImportError:
        return False


class HFClient:
    """! Client for local HuggingFace models.

    Responsible for:

    - Downloading models via `huggingface_hub.snapshot_download` to `HF_MODELS_DIR`
    - Loading into memory via `transformers.pipeline`
    - Inference via loaded pipeline (CPU float32 / GPU float16)
    - Unloading from memory with CUDA cache clearing

    Global singleton `hf_client` is created at module level and shared
    across the entire FastAPI process.

    Example:
        >>> from src.models.hf_client import hf_client
        >>> hf_client.download_model("Qwen/Qwen2.5-0.5B-Instruct")
        {"success": True, "model_id": "Qwen/Qwen2.5-0.5B-Instruct", "path": "..."}
        >>> hf_client.load_model("Qwen/Qwen2.5-0.5B-Instruct", device="auto")
        {"success": True, "model_id": "Qwen/Qwen2.5-0.5B-Instruct", "device": "cpu"}
        >>> import asyncio
        >>> asyncio.run(hf_client.generate("Hello", model_id="Qwen/Qwen2.5-0.5B-Instruct"))
        {"success": True, "content": "...", "model": "Qwen/Qwen2.5-0.5B-Instruct"}

    Environment variables:
        HF_TOKEN: HuggingFace access token (required for gated models).
        HF_MODELS_DIR: Directory to save downloaded models (default: ``~/.cache/huggingface/hub``).
    """

    def download_model(self, model_id: str, token: Optional[str] = None,
                        progress_callback=None) -> dict:
        """Download model via huggingface_hub.snapshot_download.

        Token is taken from HF_TOKEN in .env.
        Model is saved in HF_MODELS_DIR/<author>--<name>.

        Args:
            model_id: e.g., 'mistralai/Mistral-7B-Instruct-v0.3'.
            token:    Optional overriding token.
            progress_callback: Optional callable(filename, downloaded_bytes, total_bytes).

        Returns:
            dict: {"success": bool, "path": str, "error": str}
        """
        if not _check_huggingface_hub():
            return {"success": False, "error": "huggingface_hub is not installed. Run: pip install huggingface_hub"}

        from huggingface_hub import snapshot_download

        hf_token = token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        save_dir = HF_MODELS_DIR / model_id.replace("/", "--")
        save_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"📥 Downloading {model_id} → {save_dir}")

        try:
            if progress_callback:
                # Use huggingface_hub file_download with progress tracking
                from huggingface_hub import list_repo_files, hf_hub_download
                import threading

                try:
                    files = list(
                        list_repo_files(model_id, token=hf_token or None)
                    )
                    # Filter out heavy non-essential formats
                    skip = {".msgpack", ".h5"}
                    skip_prefix = ("flax_model", "tf_model")
                    files = [
                        f for f in files
                        if not any(f.endswith(s) for s in skip)
                        and not any(f.startswith(p) for p in skip_prefix)
                    ]
                except Exception:
                    files = []

                total_files = len(files)
                for idx, filename in enumerate(files, 1):
                    progress_callback({
                        "type": "file_start",
                        "filename": filename,
                        "file_index": idx,
                        "total_files": total_files,
                    })
                    try:
                        hf_hub_download(
                            repo_id=model_id,
                            filename=filename,
                            local_dir=str(save_dir),
                            token=hf_token or None,
                        )
                    except Exception as fe:
                        logger.warning(f"Skip {filename}: {fe}")
                    progress_callback({
                        "type": "file_done",
                        "filename": filename,
                        "file_index": idx,
                        "total_files": total_files,
                    })
                path = str(save_dir)
            else:
                path = snapshot_download(
                    repo_id=model_id,
                    local_dir=str(save_dir),
                    token=hf_token or None,
                    ignore_patterns=["*.msgpack", "*.h5", "flax_model*", "tf_model*"],
                )
            logger.info(f"✅ {model_id} downloaded: {path}")
            return {"success": True, "model_id": model_id, "path": path}
        except Exception as e:
            err = str(e)
            logger.error(f"❌ Error downloading {model_id}: {err}")
            if "401" in err or "403" in err or "gated" in err.lower() or "access" in err.lower():
                err = f"Access denied. Accept the license at huggingface.co/{model_id} and set HF_TOKEN"
            return {"success": False, "error": err}

    def load_model(self, model_id: str, device: str = "auto") -> dict:
        """! Load model into memory for inference.

        Args:
            model_id: Model ID or path to local directory.
            device: 'auto', 'cpu', 'cuda'.

        Returns:
            dict: {"success": bool, "model_id": str, "device": str}
        """
        if not _check_transformers():
            return {"success": False, "error": "transformers is not installed. Run: pip install transformers accelerate"}

        if model_id in _loaded_models:
            return {"success": True, "model_id": model_id, "status": "already_loaded"}

        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

            # Search for local path: HF_MODELS_DIR → HF_CACHE_DIR → download
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

            logger.info(f"Loading {model_id} from {'local: ' + model_path if local_files_only else 'HuggingFace Hub'}")

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
            logger.info(f"✅ Model {model_id} loaded on {actual_device}")
            return {"success": True, "model_id": model_id, "device": actual_device}

        except Exception as e:
            logger.error(f"❌ Error loading {model_id}: {e}")
            return {"success": False, "error": str(e)}

    def unload_model(self, model_id: str) -> dict:
        """! Unload model from memory."""
        if model_id not in _loaded_models:
            return {"success": False, "error": f"Model {model_id} is not loaded"}
        try:
            import gc, torch
            del _loaded_models[model_id]
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info(f"✅ Model {model_id} unloaded")
            return {"success": True, "model_id": model_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def generate(self, prompt: str, model_id: str,
                       max_new_tokens: int = 512,
                       temperature: float = 0.7) -> dict:
        """! Text generation via loaded HF model.

        Args:
            prompt: Input text.
            model_id: ID of the loaded model.
            max_new_tokens: Maximum number of new tokens.
            temperature: Generation temperature.

        Returns:
            dict: {"success": bool, "content": str, "model": str}
        """
        if model_id not in _loaded_models:
            # Try to load automatically
            load_result = await asyncio.get_event_loop().run_in_executor(
                None, self.load_model, model_id
            )
            if not load_result["success"]:
                return {"success": False, "error": f"Model not loaded: {load_result['error']}"}

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
            logger.error(f"❌ Error generating {model_id}: {e}")
            return {"success": False, "error": str(e)}

    def list_downloaded(self) -> list:
        """! List of downloaded models.

        Scans two directories:
        - HF_MODELS_DIR (~/.models by default or from .env)
        - ~/.cache/huggingface/hub (standard HuggingFace cache)

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

        # Scan both directories, deduplicate by model_id
        seen: set = set()
        results = []
        for model in _scan_dir(HF_MODELS_DIR, str(HF_MODELS_DIR)):
            if model["id"] not in seen:
                seen.add(model["id"])
                results.append(model)
        # Also scan standard cache if it differs from HF_MODELS_DIR
        if HF_CACHE_DIR != HF_MODELS_DIR:
            for model in _scan_dir(HF_CACHE_DIR, str(HF_CACHE_DIR)):
                if model["id"] not in seen:
                    seen.add(model["id"])
                    results.append(model)

        return sorted(results, key=lambda x: x["id"])

    def list_loaded(self) -> list:
        """! List of models loaded into memory.

        Returns:
            list: [{"id": str, "status": "loaded"}]
        """
        return [{"id": k, "status": "loaded"} for k in _loaded_models]


hf_client = HFClient()
