from agent.render import render_brief

COMPLETE_STATE = {
    "query": "给我生成一份关于 Pilbara 锂矿的今日简报",
    "region": "Pilbara",
    "commodity": "lithium",
    "commodity_label": "锂",
    "as_of": "2026-10-08",
    "news_days": 7,
    "articles": {
        "query": "Pilbara lithium",
        "days": 7,
        "items": [
            {
                "title": "Pilbara lithium miners keep shipments on schedule",
                "url": "fixture://news/pilbara-lithium-1",
                "date": "2026-10-08",
                "summary": "港口库存处于正常区间。",
            }
        ],
    },
    "bodies": [
        {
            "url": "fixture://news/pilbara-lithium-1",
            "title": "Pilbara lithium miners keep shipments on schedule",
            "source": "fixture://news/pilbara-lithium-1",
            "content": "Pilbara 地区锂矿今日发运按计划执行。",
        }
    ],
    "resources": {
        "pdf_url": "fixtures/pilbara-lithium.pdf",
        "source": "fixtures/pilbara-lithium.pdf",
        "resources": [
            {
                "category": "Indicated",
                "commodity": "lithium",
                "quantity": "12.4",
                "unit": "Mt",
                "source": "fixtures/pilbara-lithium.pdf",
            },
            {
                "category": "Inferred",
                "commodity": "lithium",
                "quantity": "8.1",
                "unit": "Mt",
                "source": "fixtures/pilbara-lithium.pdf",
            },
        ],
    },
    "price": {
        "commodity": "lithium",
        "date": "2026-10-08",
        "price": "980",
        "currency": "USD",
        "unit": "t",
        "source": "fixture://prices/lithium",
    },
    "trend": {
        "commodity": "lithium",
        "days": 7,
        "source": "fixture://prices/lithium",
        "points": [
            {"date": "2026-10-02", "price": "960"},
            {"date": "2026-10-08", "price": "980"},
        ],
    },
}


def test_complete_brief_has_five_sections_and_is_deterministic():
    first = render_brief(COMPLETE_STATE)
    second = render_brief(COMPLETE_STATE)
    assert first == second
    assert "## 新闻摘要" in first
    assert "## 储量数据" in first
    assert "## 价格走势" in first
    assert "## 风险提示" in first
    assert "## 来源链接" in first
    assert "Indicated" in first
    assert "Inferred" in first
    assert "12.4" in first
    assert "8.1" in first
    assert "2026-10-02" in first and "960" in first
    assert "2026-10-08" in first and "980" in first
    assert "fixture://news/pilbara-lithium-1" in first
    assert "fixture://prices/lithium" in first
    assert "价格走高" in first


def test_empty_news_does_not_invent_move():
    state = dict(COMPLETE_STATE)
    state["articles"] = {"query": "x", "days": 7, "items": []}
    state["bodies"] = []
    text = render_brief(state)
    assert "## 新闻摘要" in text
    assert "窗口内无匹配新闻" in text
    assert "新闻窗口内无匹配条目" in text
    assert "价格走高" in text


def test_tool_error_keeps_section_and_skips_inference():
    state = dict(COMPLETE_STATE)
    state["price"] = {"commodity": "zinc", "date": "2026-10-08", "error": "unknown_commodity"}
    state["trend"] = {"commodity": "zinc", "days": 7, "error": "unknown_commodity"}
    state["resources"] = {"pdf_url": "other.pdf", "error": "unsupported_pdf"}
    text = render_brief(state)
    assert "## 储量数据" in text
    assert "## 价格走势" in text
    assert "## 风险提示" in text
    assert "unknown_commodity" in text
    assert "unsupported_pdf" in text
    assert "价格走高" not in text
    assert "价格走低" not in text
    assert "该级别储量" not in text
