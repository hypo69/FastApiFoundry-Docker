# FastAPI Foundry — Development Guidelines

## File Header Standard
Every Python file MUST start with this header:
```python
# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: <Descriptive name of the module's function>
# =============================================================================
# Description:
#   <What this module does, what APIs it uses>
#
# File: <filename.py>
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# =============================================================================
```
JavaScript files use JSDoc block comment at top. HTML files use `<!-- ... -->` block.

## Python Code Patterns

### Singleton Pattern (used in Config, FoundryClient, RAGSystem)
```python
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

# Module-level global instance
config = Config()
```

### Async HTTP Client (aiohttp pattern)
```python
class SomeClient:
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

### Error Return Pattern (no exceptions for expected failures)
```python
async def some_operation(self) -> dict:
    try:
        # ... operation
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"❌ Operation failed: {e}")
        return {"success": False, "error": str(e)}
```
All API-facing methods return `{"success": bool, ...}` dicts, never raise to callers.

### Logging Convention
```python
logger = logging.getLogger(__name__)

# Emoji prefixes for log levels:
logger.info("✅ Success message")
logger.info("📋 List/info message")
logger.info("🔍 Search/discovery message")
logger.info("📥 Load/download message")
logger.warning("⚠️ Warning message")
logger.error("❌ Error message")
logger.debug("Detailed debug info")
```
Never use `print()` in production code (except `config_manager.py` startup prints).

### Async CPU-bound Operations (run_in_executor pattern)
```python
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, blocking_function, arg1, arg2)
```
Used for FAISS operations, SentenceTransformer encoding, file I/O in async context.

### Async Lock for Shared State
```python
self._lock = asyncio.Lock()

async def initialize(self):
    async with self._lock:
        return await self._load_index()
```

### Config Access Pattern
```python
from ..core.config import config  # within src/
from config_manager import config  # at root level

# Access via properties:
port = config.api_port
model = config.foundry_default_model
```
Never read `config.json` directly — always use the `Config` singleton.

### Optional Dependency Guard
```python
FEATURE_AVAILABLE = False
try:
    import some_optional_lib
    FEATURE_AVAILABLE = True
except ImportError:
    logger.warning("Feature not available. Install: pip install some_optional_lib")

# Then guard usage:
if not FEATURE_AVAILABLE:
    return False
```

### FastAPI Router Registration
```python
# In app.py — all routers use /api/v1 prefix
app.include_router(health.router, prefix="/api/v1")
app.include_router(models.router, prefix="/api/v1")
```

### Lifespan for Startup/Shutdown
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await rag_system.initialize()
    yield
    # shutdown
    await foundry_client.close()

app = FastAPI(lifespan=lifespan)
```

## JavaScript Patterns

### Module Exports (ES6 modules)
```javascript
// Named exports only — no default exports
export async function loadModels() { ... }
export function showAlert(message, type = 'info') { ... }

// Import from sibling modules
import { showAlert, updateChatModelBadge } from './ui.js';
```

### API Call Pattern
```javascript
// Always use window.API_BASE for base URL
const data = await fetch(`${window.API_BASE}/endpoint`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key: value })
}).then(r => r.json());

if (data.success) {
    showAlert('Success message', 'success');
} else {
    showAlert(`Failed: ${data.error}`, 'danger');
}
```

### DOM Safety Pattern
```javascript
// Always null-check before DOM access
const el = document.getElementById('some-id');
if (!el) return;
```

### Parallel API Requests
```javascript
const [res1, res2, res3] = await Promise.all([
    fetch(`${window.API_BASE}/endpoint1`).then(r => r.json()),
    fetch(`${window.API_BASE}/endpoint2`).then(r => r.json()),
    fetch(`${window.API_BASE}/endpoint3`).then(r => r.json()),
]);
```

### Model Prefix Routing (frontend)
```javascript
if (modelId.startsWith('hf::')) {
    // HuggingFace model
} else if (modelId.startsWith('llama::')) {
    // llama.cpp model
} else {
    // Foundry model
}
```

### Bootstrap Alert Helper
```javascript
export function showAlert(message, type = 'info') {
    const container = document.getElementById('alert-container');
    if (!container) return;
    const el = document.createElement('div');
    el.className = `alert alert-${type} alert-dismissible fade show`;
    el.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    container.appendChild(el);
    setTimeout(() => { el.classList.remove('show'); setTimeout(() => el.remove(), 150); }, 5000);
}
```

### DOMContentLoaded Initialization
```javascript
document.addEventListener('DOMContentLoaded', () => {
    loadModels();
    loadConnectedModels();
    // attach event listeners
});
```

### Polling Pattern (wait for async operation)
```javascript
async function waitForModelLoaded(modelId, timeoutMs = 90000) {
    const startedAt = Date.now();
    while (Date.now() - startedAt < timeoutMs) {
        const data = await fetch(`${window.API_BASE}/foundry/models/loaded`).then(r => r.json());
        if (data.success && data.models.some(m => m.id === modelId)) return true;
        await new Promise(resolve => setTimeout(resolve, 3000));
    }
    return false;
}
```

## Naming Conventions

### Python
- Classes: `PascalCase` — `FoundryClient`, `RAGSystem`, `Config`
- Functions/methods: `snake_case` — `generate_text`, `list_available_models`
- Module-level singletons: `snake_case` — `foundry_client`, `rag_system`, `config`
- Private methods: `_leading_underscore` — `_get_session`, `_load_index`, `_update_base_url`
- Constants: `UPPER_SNAKE_CASE` — `RAG_AVAILABLE`, `REQUESTS_AVAILABLE`

### JavaScript
- Functions: `camelCase` — `loadModels`, `showAlert`, `updateModelSelect`
- DOM IDs referenced: `kebab-case` — `chat-model`, `models-list`, `log-output`
- Global state: `window._savedChatModel`, `window.API_BASE`, `window.CONFIG`

## API Response Contract
All API endpoints return JSON with consistent structure:
```json
// Success
{"success": true, "data": ..., "count": N}

// Error
{"success": false, "error": "Human-readable message"}

// Health check
{"status": "healthy|unhealthy|disconnected", "timestamp": "ISO8601"}
```

## Configuration Rules
- Public settings → `config.json` (port, host, model names, RAG params)
- Secrets → `.env` only (`API_KEY`, `SECRET_KEY`, `HF_TOKEN`, `GITHUB_PAT`)
- Never hardcode ports — use `config.api_port` or `FOUNDRY_DYNAMIC_PORT` env var
- Config sections: `fastapi_server`, `foundry_ai`, `rag_system`, `port_management`, `directories`

## Windows / UTF-8 Handling
```python
# Always set at top of entry point scripts
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
```
All file operations use `encoding='utf-8'` explicitly.

## Foundry Port Discovery Order
1. `FOUNDRY_BASE_URL` env var
2. `FOUNDRY_DYNAMIC_PORT` env var (legacy)
3. Auto-scan ports `[62171, 50477, 58130]` via HTTP GET `/v1/models`
4. Windows process scan via `tasklist` + `netstat`

## RAG System Usage
```python
# Initialize (called in lifespan)
await rag_system.initialize()

# Search
results = await rag_system.search(query, top_k=5)
context = rag_system.format_context(results)

# Status
status = await rag_system.get_status()
# Returns: {available, enabled, loaded, chunks_count, vectors_count}
```

## Logging Files
- `logs/app.log` — main application log
- `logs/<module>-errors.log` — error-only log per module
- `logs/<module>-structured.jsonl` — structured JSON log per module
- Suppress noisy libraries: `logging.getLogger('watchfiles').setLevel(logging.WARNING)`
