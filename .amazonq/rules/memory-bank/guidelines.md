# FastAPI Foundry — Development Guidelines

**Version:** 0.7.0
**Project:** AI Assistant (ai_assist)

---

## 1. File Header (Mandatory for ALL files)

Every Python, JS, CSS, HTML, PowerShell file must start with this header block:

```python
# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: <Short descriptive name>
# =============================================================================
# Description:
#   <What this module does>
#
# File: filename.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.1
# Changes in 0.6.1:
#   - <what changed>
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================
```

JavaScript variant:
```javascript
/**
 * ui.js — Short description
 *
 * Contains:
 *  - functionName() — what it does
 */
```

---

## 2. Python Code Standards

### 2.1 Docstrings

Use Google-style docstrings. Start the summary line with `"""` — no `!` prefix (deprecated):

```python
def find_free_port(start_port: int = 9696, end_port: int = 9796) -> Optional[int]:
    """Find a free port in the given range.

    Args:
        start_port (int): Start of range. Default: 9696.
        end_port (int): End of range. Default: 9796.

    Returns:
        Optional[int]: Free port number or None if all ports are occupied.

    Raises:
        OSError: On socket errors.
    """
```

> ⚠️ `"""! text` — устаревший синтаксис, не использовать.

### 2.2 Type Annotations

Always annotate function signatures and declare local variables with types at the top of the function body:

```python
def get_server_port() -> int:
    default_port: int = config.api_port
    auto_find: bool = False
    free_port: Optional[int] = None
    ...
```

### 2.3 Guard Clauses (Early Return)

Prefer early return over deep nesting:

```python
# ✅ Correct
if not prompt:
    return {"success": False, "error": "Prompt is required"}

# ❌ Avoid
if prompt:
    # deep nested logic
```

### 2.4 Inline Comment Style

Comments explain *why*, not *what*. Bilingual pattern: Russian description + English translation on the same line or adjacent:

```python
# Проверка существования экземпляра (Singleton)
# Check for existing instance (Singleton)
if cls._instance is None:
    ...

# Проверка: если автопоиск отключен, используем фиксированный порт
if not auto_find:
    return default_port
```

Comments starting with `# Проверка` (Check) are a recurring idiom for guard conditions.

### 2.5 Exception Handling

Wrap risky operations in try/except, log with context, re-raise or return error dict:

```python
try:
    result = await foundry_client.generate_text(...)
    if "content" not in result:
        return {"success": False, "error": result.get("error", "Foundry error")}
    return {"success": True, "content": result["content"], ...}
except Exception as e:
    return {"success": False, "error": str(e)}
```

For infrastructure code (config loading), re-raise after logging:
```python
except json.JSONDecodeError as e:
    logger.error(f'❌ config.json содержит некорректный JSON: {e}')
    raise
```

### 2.6 Logging

Use `logging.getLogger(__name__)` — never `print()` in library code. Use emoji prefixes for visibility:

```python
logger = logging.getLogger(__name__)
logger.info("✅ RAG system initialized")
logger.warning("⚠️ RAG system not initialized")
logger.error(f"❌ Ошибка создания папки архива: {e}")
```

`print()` is only used in `run.py` for startup banner output.

### 2.7 Singleton Pattern

Config and client singletons use `__new__` with `_instance` class variable:

```python
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

config = Config()  # module-level singleton
```

### 2.8 Config Access Pattern

Always access config via the singleton, never read `config.json` directly in endpoints:

```python
from ...core.config import config as app_config

temperature = request.get("temperature", app_config.foundry_temperature)
```

Use `config.get_section("section_name")` for full sections, `config.get_raw_config()` for the full dict.

---

## 3. API Endpoint Patterns

### 3.1 Router Structure

Each feature area has its own file in `src/api/endpoints/`. Routers are registered in `app.py` with `/api/v1` prefix:

```python
router = APIRouter()

@router.post("/generate")
@api_response_handler
async def generate_text(request: dict) -> dict:
    ...
```

### 3.2 Response Format

All endpoints return a consistent dict:

```python
# Success
{"success": True, "content": "...", "model": "...", "usage": {...}}

# Error
{"success": False, "error": "Description of error"}
```

### 3.3 Model Routing by Prefix

Model selection is done by string prefix in the `model` field:

```python
if model and str(model).startswith("hf::"):
    # HuggingFace path
elif model and str(model).startswith("llama::"):
    # llama.cpp path
elif model and str(model).startswith("ollama::"):
    # Ollama path
else:
    # Default: Foundry
```

### 3.4 @api_response_handler Decorator

Wrap endpoint functions with `@api_response_handler` from `src/utils/api_utils.py` for consistent error handling. Place it directly above the route decorator:

```python
@router.post("/generate")
@api_response_handler
async def generate_text(request: dict) -> dict:
```

### 3.5 SSE Streaming Pattern

For streaming endpoints, use `StreamingResponse` with an async generator:

```python
async def event_stream():
    async for raw in proc.stdout:
        line = raw.decode("utf-8", errors="replace").rstrip()
        if line:
            yield f"data: {json.dumps({'line': line})}\n\n"
    await proc.wait()
    yield f"data: {json.dumps({'done': True, 'code': proc.returncode})}\n\n"

return StreamingResponse(event_stream(), media_type="text/event-stream")
```

---

## 4. Configuration System

### 4.1 Config Properties

All config values are exposed as `@property` on the `Config` class with safe defaults:

```python
@property
def api_port(self) -> int:
    return self._config_data.get('fastapi_server', {}).get('port') or 9696
```

Pattern: `dict.get(section, {}).get(key) or default` — the `or default` handles both missing keys and falsy values (empty string, 0, None).

### 4.2 Adding New Config Values

1. Add to `config.json` with a default value
2. Add a `@property` to `Config` class in `config_manager.py`
3. Access via `config.property_name` in code

### 4.3 Runtime Config Override

Some properties support runtime override (e.g., `foundry_base_url`):

```python
@foundry_base_url.setter
def foundry_base_url(self, value: str) -> None:
    self._foundry_base_url = value
```

---

## 5. JavaScript / Frontend Patterns

### 5.1 Module Exports

All JS files use ES modules with named exports:

```javascript
export function showAlert(message, type = 'info') { ... }
export async function refreshLogs(append = false) { ... }
export function initLogViewer() { ... }
```

### 5.2 DOM Safety Pattern

Always check element existence before use with optional chaining:

```javascript
document.getElementById('log-file-select')?.addEventListener('change', resetAndRefresh);
const file = document.getElementById('log-file-select')?.value || 'fastapi-foundry.log';
```

### 5.3 API Calls

Use `fetch` with `window.API_BASE` prefix:

```javascript
const data = await fetch(`${window.API_BASE}/logs?${params}`).then(r => r.json());
if (!data.success) throw new Error(data.detail || 'API error');
```

### 5.4 i18n

All user-visible strings use `data-i18n` attributes in HTML and `i18n()` function in JS. Never hardcode UI text:

```html
<button data-i18n="btn.save">Save</button>
```

```javascript
showAlert(i18n('error.not_found'));
```

Locale files: `static/locales/en.json`, `ru.json`, `he.json`.

### 5.5 Debounce Pattern

For search/filter inputs, debounce with `setTimeout`:

```javascript
let _searchTimer;
document.getElementById('log-search')?.addEventListener('input', () => {
    clearTimeout(_searchTimer);
    _searchTimer = setTimeout(resetAndRefresh, 400);
});
```

---

## 6. Security Patterns

### 6.1 Filename Sanitization

Always sanitize user-provided filenames before file operations:

```python
def sanitize_filename(filename: str) -> str:
    filename = filename.replace("..", "").replace("/", "").replace("\\", "")
    dangerous_chars = ["<", ">", ":", '"', "|", "?", "*", "\0"]
    for char in dangerous_chars:
        filename = filename.replace(char, "")
    filename = "".join(char for char in filename if ord(char) >= 32)
    filename = filename.strip(" .")
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext
    return filename or "sanitized_file"
```

### 6.2 MIME Validation

Validate file content against declared extension using `python-magic` when available, with graceful fallback:

```python
if magic is None:
    return True, None  # Skip MIME check if library unavailable
```

### 6.3 Optional Imports

Wrap optional heavy dependencies in try/except at module level:

```python
try:
    import magic
except ImportError:
    magic = None

try:
    import resource  # Unix only
except ImportError:
    resource = None  # Windows — resource limits not available
```

---

## 7. File & Log Management

### 7.1 Archive Instead of Delete

Never permanently delete files. Move to `archive/` with timestamp suffix:

```python
timestamp = datetime.fromtimestamp(file_mtime).strftime("%Y%m%d_%H%M%S")
archive_name = f"{file_path.stem}_{timestamp}.tmp"
shutil.move(str(file_path), str(archive_dir / archive_name))
```

### 7.2 Startup Cleanup

Run cleanup routines at startup in `run.py`:

```python
cleanup_log_temp_files(log_dir)      # Archive .tmp files older than retention_hours
cleanup_session_history(current_dir) # Rotate session_history.json if older than retention_days
cleanup_archive_size(current_dir)    # FIFO delete if archive/ exceeds max_size_gb
```

### 7.3 Path Handling

Always use `pathlib.Path` for file paths, never string concatenation:

```python
config_path = Path('config.json')
archive_dir = log_dir.parent / "archive"
archive_dir.mkdir(parents=True, exist_ok=True)
```

---

## 8. PowerShell Standards

See `POWERSHELL_CODE_RULES.md` for full details. Key rules:

- File header with `# -*- coding: utf-8 -*-` block
- `$ErrorActionPreference = 'Stop'` at top
- Constants in `UPPER_SNAKE_CASE`
- Functions as `Verb-Noun` with `<# .SYNOPSIS ... #>` docblock
- `Write-Host '🚀 Message'` for user-facing output (with emoji)
- `# --- main ---` separator before entry point
- Suppress side-effect output: `command | Out-Null`

---

## 11. Documentation — Workflow Diagrams

Whenever documentation describes a **sequence of actions** (scripts, startup chains, pipelines, install steps, request flows), render it as an ASCII workflow diagram instead of prose or a plain list.

### When to use

- Script calls another script calls another process
- Install step sequence with branching (if/else)
- Request lifecycle through multiple components
- Startup/shutdown order of services
- Any multi-step process where order and branching matter

### Format rules

```
Entry point
  │
  ├─ [condition] → branch A
  │     └─ sub-step
  │
  └─ [condition] → branch B
        ├─ step 1
        ├─ step 2  (inline note)
        └─ step 3
             └─ result / output
```

- Use `│` for vertical flow, `├─` for branches, `└─` for last branch
- Add inline notes in `(parentheses)` on the same line
- Add conditions in `[square brackets]`
- Show output/result at the bottom leaf
- Wrap in a fenced ` ```  ``` ` block (no language tag — plain text)
- Place the diagram **before** the prose explanation, not after

### Example — install.ps1 workflow

```
install.ps1
  ├─ [PS < 7] → error, exit
  ├─ [python not found] → unpack bin\Python-3.11.9.zip
  ├─ [venv exists + -Force] → remove venv
  ├─ pip install -r requirements.txt
  ├─ [-SkipRag?] → skip sentence-transformers / faiss
  ├─ [-SkipTesseract?] → skip OCR install
  ├─ [no .env] → copy .env.example
  ├─ [no logs/] → mkdir logs/
  ├─ [llama zip found] → extract to bin/
  ├─ [foundry not installed] → winget install (interactive)
  ├─ [first install] → download default models (interactive)
  └─ create desktop shortcuts
```

### Example — request lifecycle

```
POST /api/v1/generate
  │
  ├─ @api_response_handler  (error wrapper)
  ├─ model prefix check
  │     ├─ hf::     → hf_client.generate()
  │     ├─ llama::  → llama HTTP API
  │     ├─ ollama:: → ollama_client.generate()
  │     └─ (none)   → foundry_client.generate()
  └─ return {success, content, model, usage}
```

### When NOT to use

- Simple 2-step sequences — use a numbered list instead
- Pure data structures — use a table
- File trees — use the standard tree format with `├──`


After every code change:
1. Update docstring of changed function/class
2. Add entry to `CHANGELOG.md` in format `## [version] - date / ### Changed / - description`
3. Update `docs/ru/dev/api_reference.md` if endpoint changed
4. Commit: `git add . && git commit -m "docs: sync documentation"`

CHANGELOG format:
```markdown
## [0.6.1] - 2025-MM-DD
### Added
- `src/module.py` — description
### Changed
- `src/other.py` — description
### Fixed
- `src/fix.py` — description
```

---

## 10. Versioning

Current version: **0.6.1**

- All file headers must show `Version: 0.6.1`
- Semantic versioning: Major.Minor.Patch
- `VERSION` file in root contains current version string
- Version bumped in: file headers, `app.py` FastAPI title, `docker-compose.yml` image tag
