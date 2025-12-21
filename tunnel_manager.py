# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Tunnel Manager for FastAPI Foundry
# =============================================================================
# Описание:
#   Менеджер туннелей для автоматического создания публичных URL
#   Поддерживает ngrok, cloudflared, localtunnel, serveo
#
# File: tunnel_manager.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import asyncio
import subprocess
import logging
import json
import re
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class TunnelManager:
    """Менеджер туннелей для FastAPI Foundry"""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.tunnel_url: Optional[str] = None
        self.tunnel_type: Optional[str] = None
        self.port: int = 8000
    
    async def start_ngrok(self, port: int, subdomain: Optional[str] = None) -> Dict[str, Any]:
        """Запустить ngrok туннель"""
        try:
            cmd = ["ngrok", "http", str(port), "--log=stdout"]
            if subdomain:
                cmd.extend(["--subdomain", subdomain])
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Ждем URL в выводе
            for _ in range(30):  # 30 секунд таймаут
                if self.process.poll() is not None:
                    break
                
                line = self.process.stdout.readline()
                if "started tunnel" in line and "https://" in line:
                    match = re.search(r'https://[^\s]+', line)
                    if match:
                        self.tunnel_url = match.group()
                        self.tunnel_type = "ngrok"
                        self.port = port
                        
                        return {
                            "success": True,
                            "url": self.tunnel_url,
                            "type": "ngrok",
                            "port": port
                        }
                
                await asyncio.sleep(1)
            
            return {"success": False, "error": "Failed to get ngrok URL"}
            
        except FileNotFoundError:
            return {"success": False, "error": "ngrok not found. Install: choco install ngrok"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def start_cloudflared(self, port: int) -> Dict[str, Any]:
        """Запустить Cloudflare туннель"""
        try:
            cmd = ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"]
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Ждем URL в выводе
            for _ in range(30):
                if self.process.poll() is not None:
                    break
                
                line = self.process.stderr.readline()  # cloudflared пишет в stderr
                if "https://" in line and "trycloudflare.com" in line:
                    match = re.search(r'https://[^\s]+', line)
                    if match:
                        self.tunnel_url = match.group()
                        self.tunnel_type = "cloudflared"
                        self.port = port
                        
                        return {
                            "success": True,
                            "url": self.tunnel_url,
                            "type": "cloudflared",
                            "port": port
                        }
                
                await asyncio.sleep(1)
            
            return {"success": False, "error": "Failed to get Cloudflare URL"}
            
        except FileNotFoundError:
            return {"success": False, "error": "cloudflared not found. Install: winget install Cloudflare.cloudflared"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def start_localtunnel(self, port: int, subdomain: Optional[str] = None) -> Dict[str, Any]:
        """Запустить LocalTunnel"""
        try:
            cmd = ["lt", "--port", str(port)]
            if subdomain:
                cmd.extend(["--subdomain", subdomain])
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Ждем URL в выводе
            for _ in range(30):
                if self.process.poll() is not None:
                    break
                
                line = self.process.stdout.readline()
                if "https://" in line and "loca.lt" in line:
                    match = re.search(r'https://[^\s]+', line)
                    if match:
                        self.tunnel_url = match.group()
                        self.tunnel_type = "localtunnel"
                        self.port = port
                        
                        return {
                            "success": True,
                            "url": self.tunnel_url,
                            "type": "localtunnel",
                            "port": port
                        }
                
                await asyncio.sleep(1)
            
            return {"success": False, "error": "Failed to get LocalTunnel URL"}
            
        except FileNotFoundError:
            return {"success": False, "error": "localtunnel not found. Install: npm install -g localtunnel"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def start_tunnel(
        self, 
        tunnel_type: str, 
        port: int, 
        subdomain: Optional[str] = None
    ) -> Dict[str, Any]:
        """Запустить туннель указанного типа"""
        logger.info(f"Starting {tunnel_type} tunnel on port {port}")
        
        if tunnel_type == "ngrok":
            return await self.start_ngrok(port, subdomain)
        elif tunnel_type == "cloudflared":
            return await self.start_cloudflared(port)
        elif tunnel_type == "localtunnel":
            return await self.start_localtunnel(port, subdomain)
        else:
            return {"success": False, "error": f"Unknown tunnel type: {tunnel_type}"}
    
    def stop_tunnel(self) -> Dict[str, Any]:
        """Остановить активный туннель"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
                
                result = {
                    "success": True,
                    "message": f"Stopped {self.tunnel_type} tunnel",
                    "url": self.tunnel_url
                }
                
                self.process = None
                self.tunnel_url = None
                self.tunnel_type = None
                
                return result
                
            except subprocess.TimeoutExpired:
                self.process.kill()
                return {"success": True, "message": "Tunnel forcefully stopped"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No active tunnel"}
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус туннеля"""
        if self.process and self.process.poll() is None:
            return {
                "active": True,
                "type": self.tunnel_type,
                "url": self.tunnel_url,
                "port": self.port,
                "pid": self.process.pid
            }
        else:
            return {
                "active": False,
                "type": None,
                "url": None,
                "port": None,
                "pid": None
            }

# Глобальный экземпляр менеджера туннелей
tunnel_manager = TunnelManager()