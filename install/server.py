# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: FastAPI Foundry — Installation Server
# =============================================================================
# Description:
#   Standalone FastAPI server for the interactive installer UI.
#   Launched by install.ps1 after pip install -r requirements.txt.
#   Runs on port 9698, serves SPA, streams install step output via SSE.
#
# File: install/server.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import asyncio
import json
import os
import signal
import subprocess
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

ROOT        = Path(__file__).parent.parent
INSTALL_DIR = Path(__file__).parent
STATIC_DIR  = INSTALL_DIR / "static"
PID_FILE    = Path(os.environ.get('TEMP', '/tmp')) / 'fastapi-foundry-installer.pid'

app = FastAPI(title="FastAPI Foundry Installer", docs_url=None, redoc_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Helpers ───────────────────────────────────────────────────────────────────

def _venv_python() -> str:
    return str(ROOT / "venv" / "Scripts" / "python.exe")

def _venv_pip() -> str:
    return str(ROOT / "venv" / "Scripts" / "pip.exe")

def _ps(script: str) -> list[str]:
    return ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(INSTALL_DIR / script)]

# ── Install steps ─────────────────────────────────────────────────────────────

STEPS: list[dict] = [
    {
        # Core server — fast, no heavy ML deps
        "id": "requirements",
        "label_key": "steps.requirements",
        "icon": "bi-list-check",
        "cmd": lambda: [_venv_pip(), "install", "-r", str(ROOT / "requirements.txt")],
    },
    {
        # RAG + ML: torch, transformers, faiss (~3-5 GB, slow)
        "id": "rag",
        "label_key": "steps.rag",
        "icon": "bi-search",
        "cmd": lambda: [_venv_pip(), "install", "-r", str(ROOT / "requirements-rag.txt")],
    },
    {
        # Text extraction: PDF, DOCX, OCR, archives
        "id": "extras",
        "label_key": "steps.extras",
        "icon": "bi-file-earmark-zip",
        "cmd": lambda: [_venv_pip(), "install", "-r", str(ROOT / "requirements-extras.txt")],
    },
    {
        # Docs + SDK + testing (optional)
        "id": "dev",
        "label_key": "steps.dev",
        "icon": "bi-code-slash",
        "cmd": lambda: [_venv_pip(), "install", "-r", str(ROOT / "requirements-dev.txt")],
    },
    {
        "id": "env",
        "label_key": "steps.env",
        "icon": "bi-file-earmark-text",
        "cmd": lambda: [sys.executable, str(INSTALL_DIR / "_setup_env.py")],
    },
    {
        "id": "foundry",
        "label_key": "steps.foundry",
        "icon": "bi-cpu",
        "cmd": lambda: _ps("install-foundry.ps1"),
    },
    {
        "id": "models",
        "label_key": "steps.models",
        "icon": "bi-download",
        "cmd": lambda: _ps("install-models.ps1"),
    },
    {
        "id": "huggingface",
        "label_key": "steps.huggingface",
        "icon": "bi-boxes",
        "cmd": lambda: _ps("install-huggingface-cli.ps1"),
    },
    {
        "id": "llama",
        "label_key": "steps.llama",
        "icon": "bi-cpu",
        "cmd": lambda: _ps("install-llama.ps1"),
    },
    {
        "id": "shortcuts",
        "label_key": "steps.shortcuts",
        "icon": "bi-link-45deg",
        "cmd": lambda: _ps("install-shortcuts.ps1"),
    },
]

STEPS_MAP = {s["id"]: s for s in STEPS}

# ── API ───────────────────────────────────────────────────────────────────────

@app.get("/api/steps")
async def get_steps():
    return JSONResponse([
        {"id": s["id"], "label_key": s["label_key"], "icon": s["icon"]}
        for s in STEPS
    ])


@app.get("/api/status")
async def get_status():
    venv_ok    = (ROOT / "venv" / "Scripts" / "python.exe").exists()
    env_ok     = (ROOT / ".env").exists()
    req_ok     = (ROOT / "requirements.txt").exists()
    foundry_ok = False
    try:
        r = subprocess.run(["foundry", "--version"], capture_output=True, timeout=5)
        foundry_ok = r.returncode == 0
    except Exception:
        pass
    return JSONResponse({
        "venv": venv_ok,
        "env": env_ok,
        "requirements": req_ok,
        "foundry": foundry_ok,
    })


@app.get("/api/defaults")
async def get_defaults():
    """Returns default values from config.json for pre-filling installer fields."""
    try:
        cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        return JSONResponse({
            "models_dir": cfg.get("directories", {}).get("models", "~/.models"),
        })
    except Exception:
        return JSONResponse({"models_dir": "~/.models"})


@app.get("/api/run/{step_id}")
async def run_step(step_id: str):
    """Stream step output via Server-Sent Events."""
    step = STEPS_MAP.get(step_id)
    if not step:
        return JSONResponse({"error": "Unknown step"}, status_code=404)

    cmd = step["cmd"]()

    async def event_stream():
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=str(ROOT),
            )
            async for raw in proc.stdout:
                line = raw.decode("utf-8", errors="replace").rstrip()
                if line:
                    yield f"data: {json.dumps({'line': line})}\n\n"
            await proc.wait()
            yield f"data: {json.dumps({'done': True, 'code': proc.returncode})}\n\n"
        except FileNotFoundError as exc:
            yield f"data: {json.dumps({'line': f'ERROR: {exc}', 'done': True, 'code': 1})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'line': str(exc), 'done': True, 'code': 1})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/api/run/huggingface")
async def run_huggingface(token: str = ""):
    """Stream HuggingFace CLI install + optional token auth via SSE."""
    cmd = _ps("install-huggingface-cli.ps1")
    if token:
        cmd += ["-Token", token]
    else:
        cmd += ["-SkipAuth"]

    async def event_stream():
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=str(ROOT),
            )
            async for raw in proc.stdout:
                line = raw.decode("utf-8", errors="replace").rstrip()
                if line:
                    yield f"data: {json.dumps({'line': line})}\n\n"
            await proc.wait()
            yield f"data: {json.dumps({'done': True, 'code': proc.returncode})}\n\n"
        except FileNotFoundError as exc:
            yield f"data: {json.dumps({'line': f'ERROR: {exc}', 'done': True, 'code': 1})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'line': str(exc), 'done': True, 'code': 1})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/api/run/llama")
async def run_llama(models_dir: str = ""):
    """Stream llama.cpp extraction + config update via SSE."""
    cmd = _ps("install-llama.ps1")
    if models_dir:
        cmd += ["-ModelsDir", models_dir]

    async def event_stream():
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=str(ROOT),
            )
            async for raw in proc.stdout:
                line = raw.decode("utf-8", errors="replace").rstrip()
                if line:
                    yield f"data: {json.dumps({'line': line})}\n\n"
            await proc.wait()
            yield f"data: {json.dumps({'done': True, 'code': proc.returncode})}\n\n"
        except FileNotFoundError as exc:
            yield f"data: {json.dumps({'line': f'ERROR: {exc}', 'done': True, 'code': 1})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'line': str(exc), 'done': True, 'code': 1})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── Static SPA ────────────────────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


# ── Shutdown endpoint ────────────────────────────────────────────────────────

@app.post("/api/shutdown")
async def shutdown():
    """Gracefully stop the installer server (called after install completes)."""
    async def _stop():
        await asyncio.sleep(0.3)
        _cleanup_pid()
        os.kill(os.getpid(), signal.SIGTERM)
    asyncio.create_task(_stop())
    return JSONResponse({"ok": True})


# ── PID helpers ───────────────────────────────────────────────────────────────

def _write_pid() -> None:
    try:
        PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    except Exception as exc:
        print(f"[installer] Cannot write PID file: {exc}")


def _cleanup_pid() -> None:
    try:
        if PID_FILE.exists():
            PID_FILE.unlink()
    except Exception:
        pass


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import atexit, threading, webbrowser

    _write_pid()
    atexit.register(_cleanup_pid)

    def _open_browser():
        import time; time.sleep(1.2)
        webbrowser.open("http://localhost:9698")

    threading.Thread(target=_open_browser, daemon=True).start()
    print(f"🚀 FastAPI Foundry Installer → http://localhost:9698  (PID {os.getpid()})")
    print(f"💾 PID file: {PID_FILE}")
    uvicorn.run(app, host="0.0.0.0", port=9698, log_level="warning")
