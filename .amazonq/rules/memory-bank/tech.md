# FastAPI Foundry — Technology Stack

**Version:** 0.7.0
**Project:** AI Assistant (ai_assist)

---

## Runtime

| Component | Technology | Version |
|---|---|---|
| Language | Python | 3.11+ |
| Web framework | FastAPI | 0.136.0 |
| ASGI server | Uvicorn | 0.44.0 |
| Data validation | Pydantic | 2.13.2 |
| Async HTTP | aiohttp | 3.13.5 |
| HTTP client | requests | 2.33.1 |
| WebSockets | websockets | 16.0 |
| Config | python-dotenv | 1.2.2 |
| MCP protocol | mcp | latest |

## AI / ML Stack

| Component | Technology | Version |
|---|---|---|
| Vector search | faiss-cpu | 1.13.2 |
| Embeddings | sentence-transformers | 5.4.1 |
| Deep learning | PyTorch | 2.11.0 |
| Transformers | HuggingFace transformers | 4.57.6 |
| ONNX runtime | onnxruntime | 1.24.4 |
| Model optimization | optimum | 2.1.0 |
| Numerics | numpy | 2.4.4 |
| ML utilities | scikit-learn | 1.8.0 |

## Text Extraction (RAG)

| Format | Library |
|---|---|
| PDF | pdfplumber, PyPDF2 |
| Office (DOCX/XLSX/PPTX) | python-docx, openpyxl, python-pptx |
| OCR (images) | pytesseract + Pillow (Tesseract-OCR required) |
| HTML/XML | BeautifulSoup4, lxml |
| Archives | py7zr, zipfile |

## Infrastructure

| Component | Technology |
|---|---|
| Containerization | Docker + docker-compose |
| Documentation | MkDocs (Material theme) |
| Process management | psutil |
| Logging | Python logging + JSONL structured logs |
| OS | Windows (primary), Linux (Docker) |

---

## Dependency Files

| File | Purpose |
|---|---|
| `requirements.txt` | Core server (FastAPI, uvicorn, aiohttp, pydantic, mcp) |
| `requirements-rag.txt` | RAG + ML (~3-5 GB: torch, faiss, sentence-transformers) |
| `requirements-extras.txt` | Optional extras |
| `requirements-dev.txt` | Development tools |
| `docs/requirements.txt` | MkDocs plugins |

---

## Development Commands

### Start server
```powershell
# Full start (installs deps, starts Foundry, runs server)
powershell -ExecutionPolicy Bypass -File .\start.ps1

# Direct Python start (Foundry must already be running)
venv\Scripts\python.exe run.py
```

### Install dependencies
```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
# Or minimal:
install.bat
```

### Docker
```powershell
docker-compose up -d
docker-compose logs -f
docker-compose down
```

### Diagnostics
```powershell
venv\Scripts\python.exe check_env.py
venv\Scripts\python.exe diagnose.py
venv\Scripts\python.exe check_engine\smoke_all_endpoints.py
```

### Documentation
```powershell
# Start MkDocs dev server
mkdocs serve -a localhost:9697
# Or via script
powershell -ExecutionPolicy Bypass -File .\scripts\restart-mkdocs.ps1
# Build docs
mkdocs build
```

### Model management
```powershell
# Download GGUF model
powershell -ExecutionPolicy Bypass -File .\scripts\download-model.ps1
# List available models
powershell -ExecutionPolicy Bypass -File .\scripts\list-models.ps1
# Load model into Foundry
powershell -ExecutionPolicy Bypass -File .\scripts\load-model.ps1
```

---

## Key Ports

| Service | Default Port | Config Key |
|---|---|---|
| FastAPI server | 9696 | `fastapi_server.port` |
| MkDocs docs | 9697 | `docs_server.port` |
| llama.cpp | 9780 | `llama_cpp.port` |
| Foundry Local | auto-detected | `foundry_ai.base_url` |
| Docker (mapped) | 8000 | `PORT` env var |

---

## Environment Variables (.env)

```env
# Foundry (auto-detected if empty)
FOUNDRY_BASE_URL=http://localhost:50477/v1

# HuggingFace (required for gated models: Gemma, Llama)
HF_TOKEN=hf_your_token
HF_MODELS_DIR=D:\models

# llama.cpp
LLAMA_MODEL_PATH=D:\models\model.gguf
LLAMA_AUTO_START=false

# Security
API_KEY=your_api_key

# RAG
RAG_ENABLED=true
RAG_INDEX_PATH=./rag_index
```

---

## Virtual Environment

The project uses `~venv/` (tilde prefix) as the virtual environment directory.

```powershell
# Activate
~venv\Scripts\Activate.ps1
# Run Python
~venv\Scripts\python.exe
# Install packages
~venv\Scripts\pip.exe install -r requirements.txt
```

---

## CI/CD

GitHub Actions workflows in `.github/workflows/`:
- `deploy-docs.yml` — builds and deploys MkDocs to GitHub Pages
- `docs.yml` — documentation build check

Online docs: https://hypo69.github.io/FastApiFoundry-Docker/
