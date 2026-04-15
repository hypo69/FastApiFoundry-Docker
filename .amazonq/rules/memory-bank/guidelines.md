# FastAPI Foundry — Development Guidelines

## File Header Standard
Every Python file MUST begin with this header (observed in 100% of source files):

```python
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: <Functional description>
# =============================================================================
# Описание:
#   <Detailed description of module purpose>
#
# Примеры:
#   >>> from src.module import ClassName
#   >>> ClassName().method()
#
# File: <filename.py>
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================
```

- Header comments starting with `#` are NEVER modified
- Version field must be updated on every file change (current: `0.4.1`)
- Project field: always `FastApiFoundry (Docker)`

## Singleton Pattern
Used for all shared service clients and configuration:

```python
# Module-level singleton (foundry_client.py pattern)
foundry_client = FoundryClient()  # at module bottom

# Class-level singleton (config_manager.py pattern)
class Config:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

config = Config()  # global instance at module bottom
```

## Configuration Access Pattern
Never access `config.json` directly in endpoint code. Always use the `config` singleton:

```python
from src.core.config import config   # or from config_manager import config

host = config.api_host
port = config.api_port
model = config.foundry_default_model
```

Config properties use `.get()` with safe defaults — never raise on missing keys:
```python
@property
def api_port(self) -> int:
    return self._config_data.get("fastapi_server", {}).get("port", 8000)
```

## Logging Pattern
All Python modules use `logging.getLogger(__name__)` — never `print()` in production code (except `run.py` startup messages):

```python
import logging
logger = logging.getLogger(__name__)

logger.info("✅ Operation succeeded")
logger.warning("⚠️ Non-critical issue")
logger.error(f"❌ Error description: {e}")
logger.debug(f"Detail: {value}")
```

Emoji prefixes are used consistently in log messages:
- `✅` — success
- `❌` — error/failure
- `⚠️` — warning
- `🔍` — search/discovery operation
- `📋` — list/data retrieval
- `📥` / `📤` — load/unload
- `🤖` — AI/model operation
- `🏥` — health check

## Async HTTP Client Pattern (aiohttp)
All Foundry API calls use `aiohttp` with lazy session initialization:

```python
async def _get_session(self):
    if self.session is None or self.session.closed:
        self.session = aiohttp.ClientSession(timeout=self.timeout)
    return self.session

async def close(self):
    if self.session and not self.session.closed:
        await self.session.close()
```

Always call `await self._update_base_url()` before making requests to handle dynamic Foundry port discovery.

## Error Response Pattern
All API methods return consistent dict responses — never raise exceptions to callers:

```python
# Success
return {"success": True, "content": result, "model": model_id}

# Failure
return {"success": False, "error": "Human-readable message"}

# With extra context
return {
    "success": False,
    "error": f"HTTP {response.status}: {error_text}",
    "models": []
}
```

Health check responses always include `"timestamp": datetime.now().isoformat()`.

## FastAPI Router Pattern
Each endpoint file defines a module-level `router = APIRouter()` and is registered in `app.py`:

```python
# In endpoint file
from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
async def health_check():
    ...

# In app.py
from .endpoints import health
app.include_router(health.router, prefix="/api/v1")
```

## Exception Handling in Endpoints
Endpoints catch all exceptions and return structured responses rather than letting FastAPI return 500:

```python
@router.get("/health")
async def health_check():
    try:
        result = await foundry_client.health_check()
        return {...}
    except Exception as e:
        return {
            "status": "healthy",   # API itself is still up
            "foundry_status": "error",
            "error": str(e)
        }
```

## Lifespan Management
Use `@asynccontextmanager` lifespan (not deprecated `on_event`):

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await foundry_client.close()

app = FastAPI(lifespan=lifespan)
```

## Import Order Convention
```python
# 1. Standard library
import os, sys, json, logging
from pathlib import Path
from datetime import datetime

# 2. Third-party
import aiohttp
from fastapi import APIRouter

# 3. Internal (relative imports within src/)
from ..models.foundry_client import foundry_client
from ..core.config import config
from ..utils.foundry_finder import find_foundry_port
```

## JavaScript Module Pattern (Browser Extension)
Prompt files export named constants as ES modules — no default exports:

```javascript
// prompts/es.js pattern (same structure in de.js, fr.js, en.js, etc.)
export const PAGE = `System prompt for single page summarization...`;
export const MERGE = `System prompt for merging multiple tab summaries...`;
```

Each language file exports exactly `PAGE` and `MERGE` constants. New languages follow this exact structure.

## Prompt Design Pattern (Browser Extension)
All language prompts follow a consistent structure:
1. Role declaration ("You are a concise summarizer")
2. Input description
3. Rules section (word limit, bullet points, HTML output only)
4. Input placeholder at end

Output format is always: valid HTML only (`<p>`, `<ul>`, `<li>`, `<strong>`) — no Markdown, no code blocks.

## Config.json Variable Substitution
Secrets are never hardcoded in `config.json`. Use `${VAR_NAME}` syntax:

```json
{
  "foundry_ai": {
    "base_url": "${FOUNDRY_BASE_URL}",
    "api_key": "${FOUNDRY_API_KEY}"
  },
  "huggingface": {
    "models_dir": "${HF_MODELS_DIR:~/.models/hf}"
  }
}
```

`${VAR:default}` syntax provides fallback values. The `env_processor.py` handles substitution at startup.

## Port Discovery Pattern
Foundry port is resolved in priority order:
1. `FOUNDRY_BASE_URL` environment variable (full URL)
2. `FOUNDRY_DYNAMIC_PORT` environment variable (port number)
3. Auto-discovery via `tasklist` + `netstat` (Windows)
4. Probe known ports: `[62171, 50477, 58130]`

## Windows UTF-8 Handling
`run.py` sets UTF-8 encoding explicitly at startup for Windows compatibility:

```python
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
```

## Logging File Structure
Each component writes to dedicated log files in `logs/`:
- `{component}.log` — all messages
- `{component}-errors.log` — errors only
- `{component}-structured.jsonl` — structured JSON lines

Components: `fastapi-app`, `fastapi-foundry`, `foundry-client`, `foundry-models`, `models-api`, `logging-api`, `log-analyzer`, `web-logs`, `examples-api`

## Testing Conventions
- Test files in `tests/` prefixed with `test_`
- Use `pytest` + `pytest-asyncio` for async tests
- Test files mirror source structure: `test_foundry_models.py`, `test_rag.py`, `test_config.py`
- PowerShell tests: `test_port.ps1`

## Docker / Deployment
- Never commit `.env` (only `.env.example`)
- Volumes: `./logs` and `./rag_index` are always mounted
- Health check target: `GET /api/v1/health`
- Production mode: set `FASTAPI_FOUNDRY_MODE=production` env var

## What NOT to Do
- Do NOT use `print()` in endpoint/model/utility code (only `run.py` startup)
- Do NOT hardcode secrets in `config.json` — use `${VAR}` substitution
- Do NOT raise exceptions from API methods — return `{"success": False, "error": "..."}` dicts
- Do NOT use `on_event("startup")` — use `lifespan` context manager
- Do NOT access `config.json` directly — always use `config` singleton properties
- Do NOT delete files — rename with `~` suffix to disable
