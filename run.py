#!/usr/bin/env python311
# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Launching FastApiFoundry server
# =============================================================================
# Description:
#   Simple launch of the FastAPI server.
#   If Foundry is already running, AI will be available.
#   For a full launch (Foundry + env), use start.ps1
#
# File: run.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Changes in 0.6.0:
#   - Guard duplicate startup output: set _UVICORN_CHILD=1 on first run so
#     uvicorn reload child process skips env/config print messages
#   - Foundry discovery prints replaced with logger calls
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# Date: 9 декабря 2025
# =============================================================================

# FORCED UTF-8 ENCODING SETUP
import os
import sys
import locale

# Set UTF-8 for the entire Python process
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    except:
        pass  # If already set
    # Attempt to set UTF-8 locale
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass  # Use system locale


import json
import socket
import logging
from pathlib import Path

# Add current directory to sys.path for importing modules
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Add site-packages for python311
sys.path.append('C:/python311/Lib/site-packages')

# Load environment variables before importing configuration
# Guard against double-execution in uvicorn reload mode (reloader spawns a child process)
_in_reloader_child = os.getenv('_UVICORN_CHILD') == '1'
if not _in_reloader_child:
    os.environ['_UVICORN_CHILD'] = '1'

try:
    from src.utils.env_processor import load_env_variables, process_config
    load_env_variables()
    if not _in_reloader_child:
        print("Environment variables loaded")
except ImportError:
    if not _in_reloader_child:
        print("Environment processor not available, using default config")

from src.core.config import config

# Import requests only if available
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    print("Warning: requests is unavailable, some features are disabled")
    REQUESTS_AVAILABLE = False

try:
    import uvicorn
    UVICORN_AVAILABLE = True
except ImportError:
    print("Error: uvicorn is unavailable, server cannot be started")
    UVICORN_AVAILABLE = False
    sys.exit(1)

# Initialize logging subsystem (handlers wired in src/logger/__init__.py)
from src.logger import logger as _root_logger  # noqa: E402 — must follow sys.path setup
from src.utils.logging_config import setup_logging
setup_logging(os.getenv('LOG_LEVEL', 'INFO'))

logger = logging.getLogger(__name__)


# =============================================================================
# Utils
# =============================================================================
def find_free_port(start_port: int = 9696, end_port: int = 9796) -> int | None:
    """Find a free port in range"""
    logger.debug(f"Searching for a free port in range {start_port}-{end_port}")
    
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('localhost', port))
                logger.info(f"Free port found: {port}")
                return port
            except OSError:
                logger.debug(f"Port {port} is occupied")
                continue
    
    logger.warning(f"No free port found in range {start_port}-{end_port}")
    return None


# =============================================================================
# Port management
# =============================================================================
def get_server_port() -> int:
    """FastAPI server port is being determined"""
    default_port = config.api_port
    auto_find = config.port_auto_find_free
    
    logger.info(f"Determining FastAPI server port...")
    logger.debug(f"Default port: {default_port}")
    logger.debug(f"Auto-find free port: {auto_find}")

    if not auto_find:
        logger.info(f'Using fixed port: {default_port}')
        return default_port

    start_port = config.port_range_start
    end_port = config.port_range_end

    free_port = find_free_port(start_port, end_port)
    if free_port:
        logger.info(f'Found free port: {free_port}')
        return free_port

    logger.warning(f'Free port not found, using port {default_port}')
    return default_port


# =============================================================================
# Foundry
# =============================================================================
def find_foundry_port() -> int | None:
    if not REQUESTS_AVAILABLE:
        return None
    
    try:
        import subprocess
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Inference.Service.Agent*'], 
                              capture_output=True, text=True, shell=True)
        
        if 'Inference.Service.Agent' not in result.stdout:
            return None
            
        for line in result.stdout.split('\n'):
            if 'Inference.Service.Agent' in line:
                parts = line.split()
                if len(parts) >= 2:
                    pid = parts[1]
                    netstat_result = subprocess.run(['netstat', '-ano'], 
                                                   capture_output=True, text=True)
                    
                    for netline in netstat_result.stdout.split('\n'):
                        if 'LISTENING' in netline and pid in netline:
                            parts = netline.split()
                            if len(parts) >= 2:
                                addr = parts[1]
                                if ':' in addr:
                                    try:
                                        port = int(addr.split(':')[-1])
                                        response = requests.get(f'http://127.0.0.1:{port}/v1/models', timeout=1)
                                        if response.status_code == 200:
                                            print(f"Foundry API confirmed on port: {port}")
                                            return port
                                    except Exception:
                                        continue
                    break
    except Exception:
        pass
    return None


def resolve_foundry_base_url() -> str | None:
    """Foundry base_url is being determined (dynamically)"""
    # Check FOUNDRY_BASE_URL environment variable
    foundry_url = os.getenv('FOUNDRY_BASE_URL')
    if foundry_url:
        logger.info(f'Foundry found via environment variable: {foundry_url}')
        return foundry_url
    
    # Check FOUNDRY_DYNAMIC_PORT environment variable (legacy)
    foundry_port = os.getenv('FOUNDRY_DYNAMIC_PORT')
    if foundry_port:
        try:
            port = int(foundry_port)
            foundry_url = f'http://localhost:{port}/v1/'
            logger.info(f'Foundry found via legacy environment variable, port: {foundry_url}')
            return foundry_url
        except ValueError:
            pass
    
    # Automatic port detection
    foundry_port = find_foundry_port()
    if foundry_port:
        foundry_url = f'http://localhost:{foundry_port}/v1/'
        logger.info(f'Foundry found on port: {foundry_url}')
        return foundry_url

    logger.warning('Foundry not found')
    return None


def check_foundry(foundry_base_url: str | None) -> bool:
    """Checking Foundry availability"""
    if not foundry_base_url or not REQUESTS_AVAILABLE:
        return False

    try:
        response = requests.get(
            f'{foundry_base_url}models',
            timeout=3,
        )
        return response.status_code == 200
    except Exception:
        return False


# =============================================================================
# Main
# =============================================================================
def main() -> bool:
    """Main server launch function"""
    try:
        logger.info('FastAPI Foundry')
        logger.info('=' * 50)

        # -------------------------------------------------------------------------
        # Foundry
        # -------------------------------------------------------------------------
        logger.info("Searching for Foundry...")
        foundry_base_url = resolve_foundry_base_url()

        if foundry_base_url and check_foundry(foundry_base_url):
            # Update Config property with found URL
            config.foundry_base_url = foundry_base_url
            logger.info(f'Foundry is available: {foundry_base_url}')
        else:
            logger.warning('Foundry is unavailable - AI features are disabled')

        # -------------------------------------------------------------------------
        # FastAPI
        # -------------------------------------------------------------------------
        host = config.api_host
        reload_enabled = config.api_reload
        log_level = config.api_log_level.lower()
        workers = config.api_workers

        if reload_enabled:
            workers = 1

        port = get_server_port()

        logger.info('\nLaunching FastAPI server')
        logger.info(f'   Host: {host}')
        logger.info(f'   Port: {port}')
        logger.info(f'   Reload: {reload_enabled}')
        logger.info(f'   Workers: {workers}')
        logger.info('-' * 50)
        logger.info(f'UI:     http://localhost:{port}')
        logger.info(f'Docs:   http://localhost:{port}/docs')
        logger.info(f'Health: http://localhost:{port}/api/v1/health')
        logger.info('-' * 50)

        # FIXED: Added full error control for uvicorn launch
        try:
            uvicorn.run(
                'src.api.main:app',
                host=host,
                port=port,
                reload=reload_enabled,
                workers=workers,
                log_level=log_level,
                timeout_keep_alive=300,
                timeout_graceful_shutdown=10,
            )
            return True
        except KeyboardInterrupt:
            logger.info('\nStopped by user')
            return True
        except ImportError as e:
            logger.error(f'Import error - missing dependencies: {e}')
            logger.error('Try: venv\\Scripts\\python.exe -m pip install -r requirements.txt')
            return False
        except Exception as exc:
            logger.error(f'Server launch error: {exc}')
            logger.error('Check if the port is occupied and if all dependencies are installed')
            return False
            
    except Exception as e:
        logger.error(f'Critical error in main function: {e}')
        return False


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
