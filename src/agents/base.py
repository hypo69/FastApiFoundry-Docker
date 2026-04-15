# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Base Agent — базовый класс для всех агентов
# =============================================================================
# Описание:
#   Реализует агентный цикл: модель → tool_calls → выполнение → модель.
#   Каждый конкретный агент наследует BaseAgent и определяет:
#     - TOOLS       : список инструментов в формате OpenAI function calling
#     - _execute_tool : логику выполнения каждого инструмента
#
# File: src/agents/base.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]

    def to_openai(self) -> Dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }


@dataclass
class ToolCallResult:
    tool: str
    arguments: Dict[str, Any]
    result: str
    success: bool = True


@dataclass
class AgentResult:
    success: bool
    answer: str = ""
    tool_calls: List[ToolCallResult] = field(default_factory=list)
    iterations: int = 0
    error: str = ""
    note: str = ""


class BaseAgent(ABC):
    """
    Базовый класс агента.

    Подклассы должны определить:
      - tools: List[ToolDefinition]
      - _execute_tool(name, arguments) -> str
    """

    name: str = "base"
    description: str = ""

    def __init__(self, foundry_client):
        self.foundry_client = foundry_client

    @property
    @abstractmethod
    def tools(self) -> List[ToolDefinition]:
        """Список инструментов агента"""
        ...

    @abstractmethod
    async def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Выполнить инструмент и вернуть результат как строку"""
        ...

    def tools_openai(self) -> List[Dict]:
        return [t.to_openai() for t in self.tools]

    async def run(
        self,
        user_message: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        max_iterations: int = 5,
    ) -> AgentResult:
        """Запустить агентный цикл"""
        await self.foundry_client._update_base_url()
        if not self.foundry_client.base_url:
            return AgentResult(success=False, error="Foundry недоступен")

        messages = [{"role": "user", "content": user_message}]
        tool_calls_log: List[ToolCallResult] = []

        for iteration in range(max_iterations):
            logger.info(f"🤖 [{self.name}] итерация {iteration + 1}/{max_iterations}")

            payload = {
                "model": model,
                "messages": messages,
                "tools": self.tools_openai(),
                "tool_choice": "auto",
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
            }

            try:
                session = await self.foundry_client._get_session()
                url = f"{self.foundry_client.base_url.rstrip('/')}/chat/completions"

                async with session.post(url, json=payload) as resp:
                    if resp.status in (400, 422):
                        # Модель не поддерживает tools — fallback
                        logger.warning(f"⚠️ [{self.name}] tools не поддерживаются, fallback")
                        payload.pop("tools", None)
                        payload.pop("tool_choice", None)
                        async with session.post(url, json=payload) as resp2:
                            data = await resp2.json()
                        content = data["choices"][0]["message"]["content"]
                        return AgentResult(
                            success=True,
                            answer=content,
                            tool_calls=[],
                            iterations=iteration + 1,
                            note="Модель не поддерживает function calling",
                        )

                    if resp.status != 200:
                        err = await resp.text()
                        return AgentResult(success=False, error=f"HTTP {resp.status}: {err}")

                    data = await resp.json()

            except Exception as e:
                return AgentResult(success=False, error=str(e))

            choice = data["choices"][0]
            message = choice["message"]
            finish_reason = choice.get("finish_reason", "")
            messages.append(message)

            # Финальный ответ — нет tool_calls
            if finish_reason == "stop" or not message.get("tool_calls"):
                return AgentResult(
                    success=True,
                    answer=message.get("content", ""),
                    tool_calls=tool_calls_log,
                    iterations=iteration + 1,
                )

            # Выполняем tool_calls
            for tc in message["tool_calls"]:
                fn_name = tc["function"]["name"]
                try:
                    fn_args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    fn_args = {}

                logger.info(f"🔧 [{self.name}] {fn_name}({fn_args})")
                result_str = await self._execute_tool(fn_name, fn_args)
                logger.info(f"✅ [{self.name}] {fn_name}: {result_str[:80]}...")

                tcr = ToolCallResult(tool=fn_name, arguments=fn_args, result=result_str)
                tool_calls_log.append(tcr)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result_str,
                })

        return AgentResult(
            success=True,
            answer="Достигнут лимит итераций",
            tool_calls=tool_calls_log,
            iterations=max_iterations,
        )
