# FastAPI Foundry — Development Guidelines

## File Header Standard
Every Python file MUST start with this header (all fields required):

```python
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: <Functional description>
# =============================================================================
# Описание:
#   <Detailed description of what this module does>
#
# Примеры:
#   >>> from src.module import ClassName
#   >>> ClassName().method()
#
# File: <filename.py>
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# =============================================================================
```

JavaScript files use `// filename.js` comment at top, then ES module exports.

---

## Python Code Patterns

### Singleton Pattern (used in Config and FoundryClient)
```python
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

# Module-level singleton export
config = Config()
```

### Async HTTP Client Pattern (aiohttp)
```python
class FoundryClient:
    def __init__(self):
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30)

    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
```

### Response Dict Pattern
All client methods return a consistent dict — never raise exceptions to callers:
```python
# Success
return {"success": True, "content": result, "model": model_id}

# Failure
return {"success": False, "error": "Human-readable message"}

# With extra context
return {"success": False, "error": "...", "models": [], "count": 0}
```

### Error Handling Pattern
Wrap all external calls in try/except, log with emoji prefix, return error dict:
```python
try:
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            logger.info(f"✅ Success: {url}")
            return {"success": True, "data": data}
        else:
            logger.warning(f"⚠️ HTTP {response.status}")
            return {"success": False, "error": f"HTTP {response.status}"}
except Exception as e:
    logger.error(f"❌ Exception: {e}")
    return {"success": False, "error": str(e)}
```

### Logging Pattern
Use `logging.getLogger(__name__)` — never `print()` in library code:
```python
logger = logging.getLogger(__name__)

logger.info("✅ Operation succeeded")
logger.warning("⚠️ Degraded state")
logger.error(f"❌ Error: {e}")
logger.debug(f"Checking port {port}...")
```

Emoji prefixes used consistently:
- `✅` — success
- `❌` — error / not found
- `⚠️` — warning / degraded
- `🔍` — searching / scanning
- `📋` — listing
- `📥` / `📤` — load / unload
- `🤖` — AI generation
- `🏥` — health check

### FastAPI Router Pattern
One router per endpoint file, prefix applied in `app.py`:
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

### Lifespan Pattern (startup/shutdown)
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

### Config Access Pattern
Always import the singleton, never instantiate Config directly:
```python
from ..core.config import config   # inside src/
from src.core.config import config  # from root
# or
from config_manager import config   # direct

port = config.api_port
url = config.foundry_base_url
```

Config properties use `.get()` with defaults — never KeyError:
```python
@property
def api_port(self) -> int:
    return self._config_data.get("fastapi_server", {}).get("port", 8000)
```

### `__init__.py` Pattern
Keep `__init__.py` minimal — only re-export public API:
```python
from .gguf_to_onnx import GGUFConverter, ConversionResult
__all__ = ["GGUFConverter", "ConversionResult"]
```

---

## JavaScript / Browser Extension Patterns

### Prompt Module Pattern
Each language prompt file exports two named constants:
```javascript
// prompts/xx.js
export const PAGE = `System prompt for single page summarization...`;
export const MERGE = `System prompt for merging multiple tab summaries...`;
```

Prompt rules always specify:
- Output language (native to the locale)
- Word/length limit
- Output format: valid HTML only (`<p>`, `<ul>`, `<li>`, `<strong>`)
- Exclusions: navigation, ads, cookie notices
- No markdown, no code blocks

### Connector Pattern
Each AI provider connector exports a uniform interface so `summarizer.js` can swap providers:
```javascript
// connectors/foundry.js, gemini.js, openai-compat.js, openrouter.js
export async function sendMessage(messages, options) { ... }
```

---

## Configuration Patterns

### `config.json` Variable Substitution
Use `${VAR}` for required env vars, `${VAR:default}` for optional:
```json
{
  "foundry_ai": {
    "base_url": "${FOUNDRY_BASE_URL}",
    "api_key": "${FOUNDRY_API_KEY}"
  },
  "llama_cpp": {
    "base_url": "${LLAMA_BASE_URL:http://127.0.0.1:9780/v1}"
  }
}
```

Never store secrets directly in `config.json` — always use `${VAR}`.

### Port Auto-Discovery
The server auto-finds a free port in range 9696–9796 if `auto_find_free_port: true`.
Foundry port is discovered dynamically via process inspection + HTTP probe.

---

## Naming Conventions

| Item | Convention | Example |
|---|---|---|
| Python files | snake_case | `foundry_client.py` |
| Python classes | PascalCase | `FoundryClient`, `Config` |
| Python functions/methods | snake_case | `health_check()`, `list_models()` |
| FastAPI routers | `router` (module-level) | `router = APIRouter()` |
| Module-level singletons | lowercase noun | `foundry_client`, `config` |
| JS prompt exports | UPPER_SNAKE | `PAGE`, `MERGE` |
| JS connector files | provider name | `foundry.js`, `gemini.js` |
| Config sections | snake_case | `fastapi_server`, `foundry_ai` |

---

## Project-Specific Rules

1. **Never delete files** — rename with `~` suffix to disable (per AGENT_INSTRUCTIONS.md)
2. **config.json is the single source of truth** for all non-secret settings
3. **RAG system is currently disabled** (torch DLL issue on Windows) — do not re-enable without testing
4. **Windows UTF-8**: `run.py` forces `PYTHONIOENCODING=utf-8` and patches stdout/stderr on win32
5. **Foundry URL is dynamic** — set via `FOUNDRY_BASE_URL` env var or auto-discovered at startup; never hardcode
6. **Reload mode forces workers=1** — uvicorn limitation, handled in `run.py`
7. **All API responses include `timestamp`** from `datetime.now().isoformat()`
8. **Version in file headers** must match project version (currently `0.4.1` in app/client files)

---

## Testing Patterns

Tests live in `tests/` and use pytest + pytest-asyncio:
```python
import pytest

@pytest.mark.asyncio
async def test_health():
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

Run all tests: `python -m pytest tests/ -v`

---

## Commit Message Format

| Prefix | Use for |
|---|---|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `config:` | Configuration change |
| `docs:` | Documentation update |
| `test:` | Test additions/changes |
