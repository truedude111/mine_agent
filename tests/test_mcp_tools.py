import asyncio
import json
import os
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import stdio_client

from agent.tools import parse_tool_result, repo_root, server_params


async def _call(module: str, tool: str, arguments: dict) -> dict:
    os.environ["MINING_DATA"] = "fixture"
    async with stdio_client(server_params(module), errlog=open(os.devnull, "w", encoding="utf-8")) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool, arguments)
            payload = parse_tool_result(result)
            assert isinstance(payload, dict)
            return payload


def test_search_returns_items():
    payload = asyncio.run(_call("mining_news_mcp", "search", {"query": "Pilbara lithium", "days": 7}))
    assert payload["query"] == "Pilbara lithium"
    assert payload["days"] == 7
    assert "items" in payload
    assert len(payload["items"]) >= 2
    first = payload["items"][0]
    assert "title" in first and "url" in first and "date" in first and "summary" in first


def test_extract_resources_returns_indicated_inferred():
    pdf = str(repo_root() / "fixtures" / "pilbara-lithium.pdf")
    payload = asyncio.run(_call("mineral_pdf_mcp", "extract_resources", {"pdf_url": pdf}))
    assert "resources" in payload
    categories = {item["category"] for item in payload["resources"]}
    assert categories == {"Indicated", "Inferred"}
    assert payload["source"]


def test_extract_resources_relative_path():
    payload = asyncio.run(
        _call("mineral_pdf_mcp", "extract_resources", {"pdf_url": "fixtures/pilbara-lithium.pdf"})
    )
    assert "resources" in payload
    assert Path(payload["pdf_url"]).as_posix().endswith("pilbara-lithium.pdf") or payload["pdf_url"] == "fixtures/pilbara-lithium.pdf"


def test_get_price_returns_fields():
    payload = asyncio.run(_call("lme_price_mcp", "get_price", {"commodity": "lithium", "date": "2026-10-08"}))
    assert payload["commodity"] == "lithium"
    assert payload["price"] == "980"
    assert payload["currency"] == "USD"
    assert payload["unit"] == "t"
    assert payload["source"] == "fixture://prices/lithium"


def test_unknown_commodity_json_roundtrip():
    payload = asyncio.run(_call("lme_price_mcp", "get_price", {"commodity": "zinc", "date": "2026-10-08"}))
    assert json.dumps(payload)
    assert payload["error"] == "unknown_commodity"
