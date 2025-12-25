# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: MCP Server with Logging for FastAPI Foundry
# =============================================================================
# Описание:
#   MCP сервер с полным логированием для интеграции с Claude Desktop
#
# File: server.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# Настройка логирования для MCP сервера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | MCP-SERVER | %(funcName)-15s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/mcp-server.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

class MCPServer:
    """MCP сервер для FastAPI Foundry"""
    
    def __init__(self):
        self.api_base = "http://localhost:8002/api/v1"
        logger.info("MCP Server initialized")
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка MCP запроса"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            logger.info(f"Handling MCP request: {method}", extra={"params": params})
            
            if method == "tools/list":
                return await self.list_tools()
            elif method == "tools/call":
                return await self.call_tool(params)
            elif method == "resources/list":
                return await self.list_resources()
            elif method == "resources/read":
                return await self.read_resource(params)
            else:
                logger.warning(f"Unknown MCP method: {method}")
                return {"error": f"Unknown method: {method}"}
                
        except Exception as e:
            logger.error(f"MCP request error: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def list_tools(self) -> Dict[str, Any]:
        """Список доступных инструментов"""
        tools = [
            {
                "name": "generate_text",
                "description": "Generate text using AI models",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                        "model": {"type": "string"},
                        "temperature": {"type": "number"},
                        "max_tokens": {"type": "integer"}
                    },
                    "required": ["prompt"]
                }
            },
            {
                "name": "list_models",
                "description": "List available AI models",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "foundry_status",
                "description": "Get Foundry service status",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]
        
        logger.info(f"Listed {len(tools)} MCP tools")
        return {"tools": tools}
    
    async def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Вызов инструмента"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Calling MCP tool: {tool_name}", extra={"args": arguments})
        
        try:
            if tool_name == "generate_text":
                return await self.generate_text(arguments)
            elif tool_name == "list_models":
                return await self.list_models()
            elif tool_name == "foundry_status":
                return await self.get_foundry_status()
            else:
                logger.error(f"Unknown tool: {tool_name}")
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Tool call error: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def generate_text(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация текста"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base}/generate"
                
                payload = {
                    "prompt": args["prompt"],
                    "model": args.get("model"),
                    "temperature": args.get("temperature", 0.7),
                    "max_tokens": args.get("max_tokens", 2048),
                    "use_rag": args.get("use_rag", True)
                }
                
                logger.info(f"Generating text via API", extra={"model": payload.get("model")})
                
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info("Text generation successful", extra={
                            "tokens": data.get("tokens_used"),
                            "model": data.get("model")
                        })
                        return {"content": data.get("content", "")}
                    else:
                        error = await response.text()
                        logger.error(f"API error: {response.status} - {error}")
                        return {"error": f"API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"Generate text error: {e}")
            return {"error": str(e)}
    
    async def list_models(self) -> Dict[str, Any]:
        """Список моделей"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base}/models/connected"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("models", [])
                        logger.info(f"Retrieved {len(models)} models")
                        return {"models": models}
                    else:
                        error = await response.text()
                        logger.error(f"Models API error: {response.status} - {error}")
                        return {"error": f"API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"List models error: {e}")
            return {"error": str(e)}
    
    async def get_foundry_status(self) -> Dict[str, Any]:
        """Статус Foundry"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base}/foundry/status"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info("Foundry status retrieved", extra={"status": data})
                        return data
                    else:
                        error = await response.text()
                        logger.error(f"Foundry status API error: {response.status} - {error}")
                        return {"error": f"API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"Foundry status error: {e}")
            return {"error": str(e)}
    
    async def list_resources(self) -> Dict[str, Any]:
        """Список ресурсов"""
        resources = [
            {
                "uri": "foundry://models",
                "name": "Available Models",
                "description": "List of all available AI models"
            },
            {
                "uri": "foundry://status",
                "name": "System Status",
                "description": "Current system and service status"
            }
        ]
        
        logger.info(f"Listed {len(resources)} MCP resources")
        return {"resources": resources}
    
    async def read_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Чтение ресурса"""
        uri = params.get("uri")
        logger.info(f"Reading MCP resource: {uri}")
        
        if uri == "foundry://models":
            return await self.list_models()
        elif uri == "foundry://status":
            return await self.get_foundry_status()
        else:
            logger.error(f"Unknown resource: {uri}")
            return {"error": f"Unknown resource: {uri}"}

async def main():
    """Главная функция MCP сервера"""
    server = MCPServer()
    logger.info("Starting MCP Server for FastAPI Foundry")
    
    # Создать директорию для логов
    Path("logs").mkdir(exist_ok=True)
    
    try:
        while True:
            # Чтение запроса из stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
                
            try:
                request = json.loads(line.strip())
                response = await server.handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                print(json.dumps({"error": "Invalid JSON"}))
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        logger.info("MCP Server stopped by user")
    except Exception as e:
        logger.error(f"MCP Server error: {e}", exc_info=True)
    finally:
        logger.info("MCP Server shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())