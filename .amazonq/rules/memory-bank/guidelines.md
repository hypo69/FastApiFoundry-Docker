# FastAPI Foundry — Development Guidelines

## File Header Standard (ALL files)
Every Python file must start with this exact header pattern:

```python
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: <Functional description>
# =============================================================================
# Описание:
#   <Detailed description of module purpose>
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
- Encoding declaration `# -*- coding: utf-8 -*-` is always first line
- All files use UTF-8 without BOM

## Singleton Pattern (Config)
The `Config` class in `config_manager.py` uses `__new__` for singleton:

```python
class Config:
    _instance = None
    _config_data = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

# Global instance — import and use directly
config = Config()
```

Use `config` singleton everywhere; never instantiate `Config()` directly in consuming code.

## Global Module Instances
Modules expose a pre-instantiated global object at module level:

```python
# foundry_client.py
foundry_client = FoundryClient()   # global instance

# config_manager.py
config = Config()                  # global singleton
```

Import the instance, not the class:
```python
from ..models.foundry_client import foundry_client
from src.core.config import config   # or: from config_manager import config
```

## Exception Hierarchy (SDK pattern)
Custom exceptions follow a base → specific hierarchy:

```python
class FoundryError(Exception):          # base
    pass

class FoundryConnectionError(FoundryError): pass
class FoundryAPIError(FoundryError):        pass
class FoundryConfigError(FoundryError):     pass
class FoundryModelError(FoundryError):      pass
```

Always catch the base class when handling any Foundry error; catch specific subclasses for targeted handling.

## Async HTTP Client Pattern (aiohttp)
All Foundry API calls use `aiohttp` with lazy session management:

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

Session is created lazily on first use and reused. Always call `close()` in lifespan shutdown.

## Response Dict Convention
All async methods return plain dicts (not Pydantic models) with a `success` boolean:

```python
# Success
return {"success": True, "content": "...", "model": "...", "tokens_used": 0}

# Failure
return {"success": False, "error": "Human-readable message"}

# Health check
return {"status": "healthy"|"unhealthy"|"disconnected", "url": ..., "port": ..., "timestamp": ...}
```

Check `result["success"]` or `result["status"]` before using data.

## Error Handling Pattern
Wrap all external calls in `try/except Exception`:

```python
async def some_method(self):
    try:
        await self._update_base_url()
        if not self.base_url:
            return {"success": False, "error": "Foundry недоступен"}
        session = await self._get_session()
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {"success": True, ...}
            else:
                return {"success": False, "error": f"HTTP {response.status}"}
    except Exception as e:
        logger.error(f"❌ Описание ошибки: {e}")
        return {"success": False, "error": str(e)}
```

Never let exceptions propagate from client methods — always return error dict.

## Logging Convention
Use `logging.getLogger(__name__)` — never `print()` in library code (only in `run.py` startup):

```python
logger = logging.getLogger(__name__)

logger.info("✅ Успешное действие")
logger.warning("⚠️ Предупреждение")
logger.error("❌ Ошибка: {e}")
logger.debug("Детали для отладки")
```

Emoji prefixes are used consistently:
- `✅` — success
- `❌` — error/failure
- `⚠️` — warning
- `🔍` — search/discovery
- `📋` — list/info
- `📥`/`📤` — load/unload
- `🤖` — AI/model operation

## Module `__init__.py` Pattern
Export only the public API via `__all__`:

```python
from .env_processor import process_config, load_env_variables, validate_config

__all__ = [
    'process_config',
    'load_env_variables',
    'validate_config'
]
```

SDK packages also set `__version__`:
```python
__version__ = "0.2.1"
__all__ = ["FoundryClient"]
```

## FastAPI Application Factory
`create_app()` in `src/api/app.py` is the single place for:
1. FastAPI instantiation with `lifespan`
2. Static files mount (`/static`)
3. CORS middleware (allow all origins in dev)
4. Request logging middleware
5. Global exception handler (returns JSON 500)
6. Router registration with `/api/v1` prefix

```python
def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI Foundry", version="0.4.1", lifespan=lifespan)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
    # ... routers
    return app
```

`src/api/main.py` just calls `app = create_app()`.

## Lifespan Pattern
Use `@asynccontextmanager` for startup/shutdown:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await foundry_client.close()
```

## Config Access Pattern
Config properties map directly to `config.json` sections:

```python
config.api_port          # fastapi_server.port
config.foundry_base_url  # dynamically set at runtime by run.py
config.rag_enabled       # rag_system.enabled
```

`foundry_base_url` is the only mutable property — set by `run.py` after Foundry discovery:
```python
config.foundry_base_url = foundry_base_url  # set once at startup
```

## Foundry URL Resolution Order
Always resolve in this priority:
1. `FOUNDRY_BASE_URL` env var
2. `FOUNDRY_DYNAMIC_PORT` env var (legacy) → build URL
3. `config.foundry_base_url` (set at startup)
4. Auto-detect via `tasklist` + `netstat` (Windows) or port scan

## Streaming Response Pattern
Generator methods use `async for` with SSE parsing:

```python
async def generate_stream(self, prompt, **kwargs):
    async with session.post(url, json=payload) as response:
        async for line in response.content:
            line_str = line.decode('utf-8').strip()
            if line_str.startswith('data: '):
                data_str = line_str[6:]
                if data_str == '[DONE]':
                    yield {"success": True, "finished": True}
                    break
                try:
                    data = json.loads(data_str)
                    content = data['choices'][0]['delta'].get('content', '')
                    if content:
                        yield {"success": True, "content": content, "finished": False}
                except json.JSONDecodeError:
                    continue
```

## Naming Conventions
- Classes: `PascalCase` — `FoundryClient`, `Config`, `FoundryError`
- Functions/methods: `snake_case` — `find_free_port`, `resolve_foundry_base_url`
- Module-level instances: `snake_case` — `foundry_client`, `config`
- Private methods: `_leading_underscore` — `_get_session`, `_update_base_url`
- Constants: `UPPER_SNAKE_CASE` — `REQUESTS_AVAILABLE`, `UVICORN_AVAILABLE`

## Windows-Specific Considerations
- UTF-8 encoding must be forced explicitly in `run.py` for Windows:
  ```python
  os.environ['PYTHONIOENCODING'] = 'utf-8'
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
  ```
- Foundry discovery uses `tasklist` and `netstat` (Windows CLI tools)
- PowerShell scripts (`.ps1`) are the primary launcher mechanism
- `sys.path.append('C:/python311/Lib/site-packages')` for non-venv python311

## Version Tracking
- Current version: `0.4.1` (app.py, config_manager.py, foundry_client.py)
- All modified files must update `# Version:` in header
- `__version__` in SDK `__init__.py` must match

## SANDBOX/sdk — External SDK Conventions
The SDK in `SANDBOX/sdk/` follows slightly different patterns for external consumers:
- Uses `requests` (sync) not `aiohttp`
- Has `setup.py` for pip packaging
- Exception hierarchy rooted at `FoundryError`
- `__version__` exported from `__init__.py`
- Not imported by main app — standalone package
