from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_SERVICES = Path(__file__).resolve().parent.parent
if str(_SERVICES) not in sys.path:
    sys.path.insert(0, str(_SERVICES))

from data import ensure_fixture_mode, load_json, quiet_mcp_logging  # noqa: E402

ensure_fixture_mode()

mcp = FastMCP("lme-price-mcp")
quiet_mcp_logging()


def _parse_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


def _series(commodity: str) -> dict | None:
    payload = load_json("prices.json")
    return payload.get(commodity)


@mcp.tool()
def get_price(commodity: str, date: str) -> dict:
    series = _series(commodity)
    if series is None:
        return {"commodity": commodity, "date": date, "error": "unknown_commodity"}
    target = _parse_date(date)
    points = sorted(series["points"], key=lambda item: item["date"])
    chosen = None
    for point in points:
        if _parse_date(point["date"]) <= target:
            chosen = point
        else:
            break
    if chosen is None:
        return {"commodity": commodity, "date": date, "error": "no_price"}
    result = {
        "commodity": commodity,
        "date": date,
        "price": chosen["price"],
        "currency": series["currency"],
        "unit": series["unit"],
        "source": series["source"],
    }
    if chosen["date"] != date:
        result["matched_date"] = chosen["date"]
    return result


@mcp.tool()
def get_trend(commodity: str, days: int) -> dict:
    window = max(int(days), 1)
    series = _series(commodity)
    if series is None:
        return {"commodity": commodity, "days": window, "error": "unknown_commodity"}
    points = sorted(series["points"], key=lambda item: item["date"])
    if not points:
        return {
            "commodity": commodity,
            "days": window,
            "source": series["source"],
            "points": [],
        }
    end = _parse_date(points[-1]["date"])
    start = end - timedelta(days=window)
    selected = [point for point in points if start <= _parse_date(point["date"]) <= end]
    if not selected:
        selected = points
    return {
        "commodity": commodity,
        "days": window,
        "source": series["source"],
        "points": [{"date": point["date"], "price": point["price"]} for point in selected],
    }
