#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Foundry with Tunnel
# =============================================================================
# Описание:
#   Запуск FastAPI Foundry с автоматическим созданием туннеля
#   Поддерживает ngrok, cloudflared, localtunnel
#
# File: start_with_tunnel.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import os
import sys
import time
import subprocess
import threading
import argparse
from pathlib import Path

def run_fastapi(mode="dev", ssl=False, mcp=False, auto_port=False):
    """Запустить FastAPI сервер"""
    print("🚀 Starting FastAPI Foundry...")
    cmd = [sys.executable, "run.py", f"--{mode}"]
    if ssl:
        cmd.append("--ssl")
    if mcp:
        cmd.append("--mcp")
    if auto_port:
        cmd.append("--auto-port")
    subprocess.run(cmd)

def run_ngrok(port=8000, subdomain=None):
    """Запустить ngrok туннель"""
    print(f"🌐 Starting ngrok tunnel for port {port}...")
    
    cmd = ["ngrok", "http", str(port)]
    if subdomain:
        cmd.extend(["--subdomain", subdomain])
    
    subprocess.run(cmd)

def run_cloudflared(port=8000):
    """Запустить Cloudflare туннель"""
    print(f"☁️ Starting Cloudflare tunnel for port {port}...")
    subprocess.run(["cloudflared", "tunnel", "--url", f"http://localhost:{port}"])

def run_localtunnel(port=8000, subdomain=None):
    """Запустить LocalTunnel"""
    print(f"⚡ Starting LocalTunnel for port {port}...")
    
    cmd = ["lt", "--port", str(port)]
    if subdomain:
        cmd.extend(["--subdomain", subdomain])
    
    subprocess.run(cmd)

def run_serveo(port=8000):
    """Запустить Serveo туннель"""
    print(f"🔧 Starting Serveo tunnel for port {port}...")
    subprocess.run(["ssh", "-R", f"80:localhost:{port}", "serveo.net"])

def main():
    parser = argparse.ArgumentParser(description="FastAPI Foundry with Tunnel")
    
    parser.add_argument(
        "--tunnel",
        choices=["ngrok", "cloudflared", "localtunnel", "serveo"],
        default="ngrok",
        help="Tunnel service to use (default: ngrok)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8443,
        help="Port for FastAPI server (default: 8443)"
    )
    
    parser.add_argument(
        "--subdomain",
        help="Custom subdomain (ngrok/localtunnel only)"
    )
    
    parser.add_argument(
        "--tunnel-only",
        action="store_true",
        help="Only start tunnel (FastAPI should be running separately)"
    )
    
    parser.add_argument(
        "--mode",
        choices=["dev", "prod"],
        default="dev",
        help="FastAPI mode (default: dev)"
    )
    
    parser.add_argument(
        "--ssl",
        action="store_true",
        help="Enable HTTPS for FastAPI"
    )
    
    parser.add_argument(
        "--mcp",
        action="store_true",
        help="Start MCP Console alongside FastAPI"
    )
    
    parser.add_argument(
        "--auto-port",
        action="store_true",
        help="Auto-detect free ports"
    )
    
    args = parser.parse_args()
    
    print("🚀 FastAPI Foundry Tunnel Starter")
    print("=" * 50)
    print(f"Tunnel: {args.tunnel}")
    print(f"Port: {args.port}")
    print(f"Mode: {args.mode}")
    print(f"SSL: {'Yes' if args.ssl else 'No'}")
    print(f"MCP: {'Yes' if args.mcp else 'No'}")
    print(f"Auto-port: {'Yes' if args.auto_port else 'No'}")
    if args.subdomain:
        print(f"Subdomain: {args.subdomain}")
    print("=" * 50)
    
    if not args.tunnel_only:
        # Запустить FastAPI в отдельном потоке
        fastapi_thread = threading.Thread(
            target=run_fastapi, 
            args=(args.mode, args.ssl, args.mcp, args.auto_port),
            daemon=True
        )
        fastapi_thread.start()
        
        # Подождать запуска FastAPI
        print("⏳ Waiting for FastAPI to start...")
        time.sleep(8 if args.mcp else 5)
    
    # Запустить туннель
    try:
        if args.tunnel == "ngrok":
            run_ngrok(args.port, args.subdomain)
        elif args.tunnel == "cloudflared":
            run_cloudflared(args.port)
        elif args.tunnel == "localtunnel":
            run_localtunnel(args.port, args.subdomain)
        elif args.tunnel == "serveo":
            run_serveo(args.port)
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping tunnel...")
    except FileNotFoundError as e:
        print(f"❌ Tunnel service not found: {e}")
        print("💡 Install the tunnel service first:")
        
        if args.tunnel == "ngrok":
            print("   - Download from: https://ngrok.com/download")
            print("   - Or: choco install ngrok")
        elif args.tunnel == "cloudflared":
            print("   - Download from: https://github.com/cloudflare/cloudflared/releases")
            print("   - Or: winget install Cloudflare.cloudflared")
        elif args.tunnel == "localtunnel":
            print("   - Install: npm install -g localtunnel")
        elif args.tunnel == "serveo":
            print("   - Requires SSH client (built-in on most systems)")

if __name__ == "__main__":
    main()