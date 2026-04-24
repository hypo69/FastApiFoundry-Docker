# CI/CD: Automatic Documentation Build

FastAPI Foundry documentation is built and published automatically on every push to the `main` or `master` branches via GitHub Actions.

## Overview

The system consists of three parallel jobs that generate documentation from source code in different languages, and one final job that publishes everything to GitHub Pages.

```text
push → [docs-js]          ──┐
     → [docs-powershell]  ──┼──→ [deploy] → GitHub Pages
     → (Python inline)    ──┘
```

| Job | Runner | Tool | Covers |
|---|---|---|---|
| `docs-js` | ubuntu-latest | TypeDoc | JSDoc in extension `.js` files |
| `docs-powershell` | windows-latest | PlatyPS | Comment-based help in `.ps1` files |
| `deploy` | ubuntu-latest | MkDocs Material | Python docstrings + all `.md` files |

---

## Triggers

The build is triggered by changes in:
`src/**`, `docs/**`, `mkdocs.yml`, `extensions/**`, `scripts/**`, `config.json`, etc.

---

## Output Structure

After a successful deploy, the documentation is available at the repository's GitHub Pages URL.

Structure:
```text
/                           ← Home
/user/getting_started/      ← Quick Start
/dev/architecture/          ← Architecture
/dev/api_reference/         ← REST API Reference
/dev/code/                  ← Python Reference (mkdocstrings)
/dev/js/                    ← JS: Browser Extension (TypeDoc)
/dev/powershell/            ← PowerShell: MCP Servers (PlatyPS)
```

---

## Local Build

To preview the documentation locally:

```bash
# Install dependencies
pip install -r docs/requirements.txt

# Start dev server with hot reload
mkdocs serve
```

The server will be available at `http://127.0.0.1:8000`.

---

## Adding New Modules

### Python Module
Create a file in `docs/en/dev/code/` and use:
```markdown
# My Module
::: src.my_package.my_module
```

### JavaScript / PowerShell
New files are picked up automatically by CI jobs if they follow the standard JSDoc or Comment-based help format.