#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой HTTP сервер для тестирования без uvicorn
"""

import sys
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Добавляем текущую директорию в sys.path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from src.core.config import config

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            try:
                with open('static/index.html', 'r', encoding='utf-8') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content.encode())
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'index.html not found')
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy", 
                "message": "Simple server running",
                "server_type": "HTTP",
                "foundry_status": "not_connected",
                "timestamp": "2025-12-27T20:45:00Z"
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        elif self.path == '/api':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "service": "FastAPI Foundry (Simple Mode)",
                "version": "0.2.1",
                "description": "Simplified HTTP server for testing",
                "endpoints": {
                    "health": "/health",
                    "api_info": "/api",
                    "home": "/"
                },
                "note": "Install uvicorn and fastapi for full functionality"
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        elif self.path.startswith('/static/'):
            try:
                file_path = self.path[1:]
                with open(file_path, 'rb') as f:
                    content = f.read()
                if file_path.endswith('.js'):
                    content_type = 'application/javascript'
                elif file_path.endswith('.css'):
                    content_type = 'text/css'
                else:
                    content_type = 'text/html'
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

def main():
    port = config.api_port
    server = HTTPServer(('localhost', port), SimpleHandler)
    print(f"Simple server running on http://localhost:{port}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        server.shutdown()

if __name__ == "__main__":
    main()