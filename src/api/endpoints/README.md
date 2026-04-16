# src/api/endpoints

FastAPI route handlers. One file per feature area.

## Files

| File | Prefix | Description |
|---|---|---|
| `health.py` | `/api/v1/health` | Service health check |
| `generate.py` | `/api/v1/generate` | Single-shot text generation |
| `chat_endpoints.py` | `/api/v1/chat` | Session-aware chat |
| `models.py` | `/api/v1/models` | Model list / connected models |
| `foundry.py` | `/api/v1/foundry` | Foundry status |
| `foundry_management.py` | `/api/v1/foundry` | Start / stop Foundry service |
| `foundry_models.py` | `/api/v1/foundry/models` | Load / unload Foundry models |
| `rag.py` | `/api/v1/rag` | RAG status, search, build, profiles |
| `translation.py` | `/api/v1/translation` | Text translation (LLM / DeepL / Google / Helsinki) |
| `config.py` | `/api/v1/config` | Read / write config.json and .env |
| `logs.py` | `/api/v1/logs` | Log streaming |
| `hf_models.py` | `/api/v1/hf` | HuggingFace model download / inference |
| `llama_cpp.py` | `/api/v1/llama` | llama.cpp server control |
| `mcp_powershell.py` | `/api/v1/mcp-powershell` | PowerShell MCP server proxy |
| `agent.py` | `/api/v1/agent` | AI agent with tool calls |
| `converter.py` | `/api/v1/converter` | GGUF → ONNX conversion |

## Pattern

Each file registers its own `APIRouter`. Routers are imported and mounted in `src/api/app.py`:

```python
from .endpoints.translation import router as translation_router
app.include_router(translation_router, prefix="/api/v1")
```

All handlers return a consistent dict:

```python
# success
{"success": True, "data": ...}

# failure
{"success": False, "error": "Human-readable message"}
```
