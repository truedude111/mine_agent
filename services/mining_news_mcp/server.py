from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_SERVICES = Path(__file__).resolve().parent.parent
if str(_SERVICES) not in sys.path:
    sys.path.insert(0, str(_SERVICES))

from data import ensure_fixture_mode, load_json, quiet_mcp_logging  # noqa: E402

ensure_fixture_mode()

mcp = FastMCP("mining-news-mcp")
quiet_mcp_logging()


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _tokens(query: str) -> list[str]:
    return [part.lower() for part in query.replace(",", " ").split() if part.strip()]


def _hit(item: dict, tokens: list[str]) -> bool:
    haystack = " ".join(
        [
            str(item.get("title", "")),
            str(item.get("summary", "")),
            " ".join(str(k) for k in item.get("keywords", [])),
        ]
    ).lower()
    return all(token in haystack for token in tokens)


@mcp.tool()
def search(query: str, days: int) -> dict:
    window = max(int(days), 1)
    items = load_json("news.json")
    tokens = _tokens(query)
    matched_by_keyword = [item for item in items if _hit(item, tokens)] if tokens else list(items)
    dates = [_parse_date(item["date"]) for item in items] or [date.today()]
    anchor = max(dates)
    start = anchor - timedelta(days=window)
    selected = [
        item
        for item in matched_by_keyword
        if start <= _parse_date(item["date"]) <= anchor
    ]
    return {
        "query": query,
        "days": window,
        "items": [
            {
                "title": item["title"],
                "url": item["url"],
                "date": item["date"],
                "summary": item["summary"],
            }
            for item in selected
        ],
    }


@mcp.tool()
def fetch_article(url: str) -> dict:
    articles = load_json("articles.json")
    article = articles.get(url)
    if article is None:
        return {"url": url, "error": "not_found"}
    return {
        "url": url,
        "title": article["title"],
        "source": article["source"],
        "content": article["content"],
    }
