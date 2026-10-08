from __future__ import annotations

import json
import os
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

REPO_ROOT = Path(__file__).resolve().parent.parent
SERVERS = {
    "mining-news-mcp": "mining_news_mcp",
    "mineral-pdf-mcp": "mineral_pdf_mcp",
    "lme-price-mcp": "lme_price_mcp",
}


def repo_root() -> Path:
    return REPO_ROOT


def server_params(module: str) -> StdioServerParameters:
    env = os.environ.copy()
    env["MINING_DATA"] = os.environ.get("MINING_DATA", "fixture")
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONUTF8"] = "1"
    pythonpath = env.get("PYTHONPATH", "")
    extras = [str(REPO_ROOT), str(REPO_ROOT / "services")]
    env["PYTHONPATH"] = os.pathsep.join(extras + ([pythonpath] if pythonpath else []))
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", module],
        cwd=str(REPO_ROOT),
        env=env,
    )


def parse_tool_result(result: Any) -> dict:
    if getattr(result, "isError", False):
        texts = []
        for block in getattr(result, "content", []) or []:
            text = getattr(block, "text", None)
            if text:
                texts.append(text)
        return {"error": texts[0] if texts else "tool_error"}
    for block in getattr(result, "content", []) or []:
        text = getattr(block, "text", None)
        if not text:
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return {"error": text}
        if isinstance(payload, dict):
            return payload
        return {"error": "invalid_payload"}
    structured = getattr(result, "structuredContent", None)
    if isinstance(structured, dict):
        return structured
    return {"error": "empty_result"}


class McpHub:
    def __init__(self) -> None:
        self._stack = AsyncExitStack()
        self.sessions: dict[str, ClientSession] = {}

    async def start(self) -> None:
        await self._stack.__aenter__()
        errlog = self._stack.enter_context(open(os.devnull, "w", encoding="utf-8"))
        for name, module in SERVERS.items():
            read, write = await self._stack.enter_async_context(
                stdio_client(server_params(module), errlog=errlog)
            )
            session = await self._stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            self.sessions[name] = session

    async def close(self) -> None:
        await self._stack.aclose()
        self.sessions.clear()

    async def call(self, server: str, tool: str, arguments: dict) -> dict:
        session = self.sessions.get(server)
        if session is None:
            return {"error": f"session_missing:{server}"}
        try:
            result = await session.call_tool(tool, arguments)
        except Exception as exc:  # noqa: BLE001
            return {"error": str(exc)}
        return parse_tool_result(result)
