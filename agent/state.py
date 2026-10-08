from __future__ import annotations

from typing import TypedDict


class BriefState(TypedDict, total=False):
    query: str
    region: str
    commodity: str
    commodity_label: str
    as_of: str
    news_days: int
    articles: dict
    price: dict
    trend: dict
    bodies: list[dict]
    resources: dict
    markdown: str
