# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Foundry Management API
# =============================================================================
# Описание:
#   API endpoints для управления Foundry сервисом
#   Старт/стоп сервиса и получение статуса
#
# File: src/api/endpoints/foundry_management.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import subprocess
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/foundry", tags=["foundry"])

class FoundryStatus(BaseModel):
    running: bool
    port: Optional[int] = None
    url: Optional[str] = None

def find_foundry_port() -> Optional[int]:
    try:
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
                                            return port
                                    except Exception:
                                        continue
                    break
    except Exception:
        pass
    return None

@router.get("/status", response_model=FoundryStatus)
async def get_foundry_status():
    port = find_foundry_port()
    if port:
        return FoundryStatus(
            running=True,
            port=port,
            url=f"http://localhost:{port}/v1/"
        )
    return FoundryStatus(running=False)

@router.post("/start")
async def start_foundry():
    try:
        subprocess.run(['foundry', 'service', 'start'], check=True, capture_output=True)
        return {"message": "Foundry start command executed"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to start Foundry: {e}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Foundry CLI not found")

@router.post("/stop")
async def stop_foundry():
    try:
        subprocess.run(['foundry', 'service', 'stop'], check=True, capture_output=True)
        return {"message": "Foundry stop command executed"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop Foundry: {e}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Foundry CLI not found")