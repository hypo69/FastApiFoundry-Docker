#!/usr/bin/env python3
import uvicorn
import sys

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

uvicorn.run(
    "src.api.main:app",
    host="0.0.0.0",
    port=port,
    reload=False,
    log_level="info"
)