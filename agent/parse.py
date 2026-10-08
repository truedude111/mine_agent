from __future__ import annotations

import re
from datetime import date

from agent.state import BriefState

_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
_DAYS_RE = re.compile(r"(\d+)\s*天")


def parse_query(query: str, today: date | None = None) -> dict:
    today = today or date.today()
    region = "Pilbara"
    if "Pilbara" in query:
        region = "Pilbara"

    commodity = "lithium"
    commodity_label = "锂"
    if "锂" in query or re.search(r"lithium", query, re.I):
        commodity = "lithium"
        commodity_label = "锂"

    as_of = today.isoformat()
    dated = _DATE_RE.search(query)
    if dated:
        as_of = dated.group(0)
    if "今日" in query:
        as_of = today.isoformat()

    news_days = 7
    days_match = _DAYS_RE.search(query)
    if days_match:
        news_days = int(days_match.group(1))

    return {
        "query": query,
        "region": region,
        "commodity": commodity,
        "commodity_label": commodity_label,
        "as_of": as_of,
        "news_days": news_days,
    }


def parse_node(state: BriefState) -> dict:
    return parse_query(state.get("query", ""))
