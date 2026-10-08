from datetime import date

from agent import DEFAULT_QUERY
from agent.parse import parse_query


def test_default_query():
    today = date(2026, 10, 8)
    parsed = parse_query(DEFAULT_QUERY, today=today)
    assert parsed["region"] == "Pilbara"
    assert parsed["commodity"] == "lithium"
    assert parsed["commodity_label"] == "锂"
    assert parsed["as_of"] == "2026-10-08"
    assert parsed["news_days"] == 7


def test_missing_region_and_commodity_use_defaults():
    parsed = parse_query("给我生成一份今日简报", today=date(2026, 10, 8))
    assert parsed["region"] == "Pilbara"
    assert parsed["commodity"] == "lithium"
    assert parsed["commodity_label"] == "锂"
    assert parsed["as_of"] == "2026-10-08"
    assert parsed["news_days"] == 7


def test_explicit_date_and_window():
    parsed = parse_query("Pilbara lithium 2026-10-01 3天", today=date(2026, 10, 8))
    assert parsed["as_of"] == "2026-10-01"
    assert parsed["news_days"] == 3
    assert parsed["commodity"] == "lithium"
