# FastAPI Foundry — Technology Stack

## Languages & Runtimes
- **Python 3.11+** — primary backend language (path: `C:/python311`)
- **JavaScript (ES6+)** — frontend SPA (no build step, vanilla JS)
- **PowerShell 5+** — Windows scripts, MCP servers, launchers
- **HTML5 / CSS3** — web UI templates (partials system)

## Core Framework
- **FastAPI** `>=0.104.0` — async REST API framework
- **Uvicorn** `>=0.24.0` with `[standard]` extras — ASGI server
  - `timeout_keep_alive=300`, `timeout_graceful_shutdown=10`
  - Reload mode enabled by default (dev); workers=1 when reload=True

## HTTP & Async
- **aiohttp** `>=3.9.0` — async HTTP client for Foundry API calls
- **requests** `>=2.31.0` — sync HTTP for startup checks
- **websockets** `>=11.0.0` — WebSocket support
- **watchfiles** `>=0.20.0` — file watching for hot reload

## AI / ML Stack
- **sentence-transformers** `>=2.2.0` — embeddings for RAG
- **faiss-cpu** `>=1.7.0` — vector similarity search
- **torch** `>=2.0.0` — PyTorch (required by sentence-transformers)
- **numpy** `>=1.24.0` — numerical operations
- **transformers** `>=4.40.0` — HuggingFace model inference
- **accelerate** `>=0.30.0` — HuggingFace acceleration
- **huggingface_hub** `>=0.23.0` — model downloads
- **optimum[onnxruntime]** `>=1.16.0` — GGUF→ONNX conversion
- **onnxruntime** `>=1.17.0` — ONNX model inference

## Configuration & Environment
- **python-dotenv** `>=1.0.0` — `.env` file loading
- **PyYAML** `>=6.0` — YAML config support
- `config.json` — primary config file (JSON, loaded by `Config` singleton)
- `config_manager.py` — `Config` class with `@property` accessors

## Logging & Monitoring
- **psutil** `>=5.9.0` — system resource monitoring
- Python `logging` module — structured + plain text logs
- Log files in `logs/` directory: `*.log`, `*-errors.log`, `*-structured.jsonl`
- Log format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Testing
- **pytest** `>=7.4.0`
- **pytest-asyncio** `>=0.21.0`
- Smoke tests: `check_engine/smoke_all_endpoints.py`
- Diagnostic scripts: `check_engine/check_*.py`

## Docker
- `Dockerfile` — container image
- `docker-compose.yml` — service definition
  - Port: `${PORT:-8000}:8000`
  - Volumes: `./logs`, `./rag_index`, `./.env`
  - Health check: `GET /api/v1/health` every 30s

## External Dependencies
- **Microsoft Foundry Local CLI** — `foundry` command, runs AI models on port 50477 (dynamic)
- **llama.cpp** — bundled binaries in `bin/llama-b8802-bin-win-cpu-x64/`
  - `llama-server.exe` — local inference server
- **HuggingFace Hub** — model downloads via `huggingface-cli` / `hf` CLI

## Development Commands

### Start server
```bash
python run.py
# or with venv
venv\Scripts\python.exe run.py
```

### PowerShell launcher (interactive menu)
```powershell
.\launcher.ps1
.\launcher.ps1 -Mode quick    # Quick start
.\launcher.ps1 -Mode diag     # Diagnostics
.\launcher.ps1 -Mode setup    # Configure .env
```

### Docker
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

### Install dependencies
```bash
pip install -r requirements.txt
# or
.\install.ps1
```

### Check environment
```bash
python check_env.py
python diagnose.py
```

### Verify API
```bash
curl http://localhost:9696/api/v1/health
curl http://localhost:9696/api/v1/models
curl http://localhost:9696/docs
```

### Run tests
```bash
python -m pytest tests/ -v
python check_engine/smoke_all_endpoints.py
```

## Key Environment Variables
| Variable | Purpose | Default |
|---|---|---|
| `API_KEY` | API authentication key | — |
| `SECRET_KEY` | JWT secret | — |
| `FOUNDRY_BASE_URL` | Foundry API URL | auto-detected |
| `FOUNDRY_DYNAMIC_PORT` | Foundry port (legacy) | auto-detected |
| `HF_TOKEN` / `HUGGING_FACE_TOKEN` | HuggingFace token | — |
| `GITHUB_PAT` | GitHub personal access token | — |
| `RAG_INDEX_PATH` | RAG index directory | `rag_index/` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENVIRONMENT` | `development` / `production` | — |

## API Endpoints Summary
| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/health` | GET | Service health check |
| `/api/v1/models` | GET | List available models |
| `/api/v1/generate` | POST | Text generation |
| `/api/v1/chat` | POST | Chat with history |
| `/api/v1/rag/search` | POST | RAG vector search |
| `/api/v1/foundry/*` | GET/POST | Foundry management |
| `/api/v1/hf/*` | GET/POST | HuggingFace models |
| `/api/v1/llama/*` | GET/POST | llama.cpp inference |
| `/api/v1/config` | GET/POST | Config read/write |
| `/api/v1/logs` | GET | Log viewer |
| `/docs` | GET | Swagger UI |
