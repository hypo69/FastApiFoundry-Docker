# Changelog

All notable changes to FastApiFoundry (Docker) are documented here.

## [0.6.0] - 2025-12-09

### Fixed
- **Duplicate startup output** — `run.py` and `config_manager.py` printed startup
  messages twice when Uvicorn ran in `reload=True` mode. Uvicorn spawns a child
  worker process that inherits the parent environment, causing all module-level
  code to execute a second time.

  Fix: `run.py` sets `_UVICORN_CHILD=1` on first execution. Both `run.py` and
  `config_manager._load_config` check this flag before printing. Foundry
  discovery messages migrated from `print()` to `logger` (already suppressed in
  the child by Uvicorn's log routing).

  Affected files: `run.py`, `config_manager.py`
