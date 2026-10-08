from __future__ import annotations

from typing import Any

from agent.state import BriefState


def _as_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _snippet(text: str, limit: int = 120) -> str:
    return text[:limit]


def _add_source(seen: list[str], source: str | None) -> None:
    if not source:
        return
    if source not in seen:
        seen.append(source)


def _first_resource(resources: list[dict], category: str) -> dict | None:
    for item in resources:
        if item.get("category") == category:
            return item
    return None


def _fmt_price(value: Any) -> str:
    return str(value)


def render_brief(state: BriefState) -> str:
    region = state.get("region", "Pilbara")
    label = state.get("commodity_label", "锂")
    as_of = state.get("as_of", "")
    news_days = state.get("news_days", 7)
    articles = _as_dict(state.get("articles"))
    price = _as_dict(state.get("price"))
    trend = _as_dict(state.get("trend"))
    resources = _as_dict(state.get("resources"))
    bodies = state.get("bodies") if isinstance(state.get("bodies"), list) else []

    sources: list[str] = []
    lines: list[str] = [f"# {region} {label}矿简报（{as_of}）", "", "## 新闻摘要"]

    news_empty = False
    if articles.get("error"):
        lines.append(f"- {articles['error']}")
        _add_source(sources, str(articles.get("source") or articles.get("url") or ""))
    else:
        items = articles.get("items") if isinstance(articles.get("items"), list) else []
        if not items:
            news_empty = True
            lines.append("- 窗口内无匹配新闻")
        else:
            for index, item in enumerate(items):
                title = item.get("title", "")
                url = item.get("url", "")
                news_date = item.get("date", "")
                summary = item.get("summary", "")
                lines.append(f"- {news_date} {title}：{summary}")
                body = bodies[index] if index < len(bodies) else {}
                if body.get("error"):
                    lines.append("  正文要点：正文未取得")
                else:
                    content = str(body.get("content", ""))
                    lines.append(f"  正文要点：{_snippet(content)}")
                    _add_source(sources, body.get("source"))
                lines.append(f"  来源：{url}")
                _add_source(sources, url)

    lines.extend(["", "## 储量数据"])
    if resources.get("error"):
        lines.append(f"- {resources['error']}")
        _add_source(sources, resources.get("source") or resources.get("pdf_url"))
    else:
        resource_list = resources.get("resources") if isinstance(resources.get("resources"), list) else []
        indicated = _first_resource(resource_list, "Indicated")
        inferred = _first_resource(resource_list, "Inferred")
        if indicated:
            lines.append(
                f"- Indicated：{indicated.get('quantity')} {indicated.get('unit')}（来源：{indicated.get('source')}）"
            )
            _add_source(sources, indicated.get("source"))
        else:
            lines.append("- Indicated：来源未给出该级别储量")
        if inferred:
            lines.append(
                f"- Inferred：{inferred.get('quantity')} {inferred.get('unit')}（来源：{inferred.get('source')}）"
            )
            _add_source(sources, inferred.get("source"))
        else:
            lines.append("- Inferred：来源未给出该级别储量")
        _add_source(sources, resources.get("source") or resources.get("pdf_url"))

    lines.extend(["", "## 价格走势"])
    if price.get("error"):
        lines.append(f"- {price['error']}")
        _add_source(sources, price.get("source"))
    else:
        lines.append(
            f"- {as_of} 价格：{price.get('price')} {price.get('currency')}/{price.get('unit')}（来源：{price.get('source')}）"
        )
        _add_source(sources, price.get("source"))
        if price.get("matched_date"):
            lines.append(f"- 匹配日期：{price['matched_date']}")

    if trend.get("error"):
        lines.append(f"- {trend['error']}")
        _add_source(sources, trend.get("source"))
    else:
        points = trend.get("points") if isinstance(trend.get("points"), list) else []
        if points:
            first, last = points[0], points[-1]
            lines.append(
                f"- 近 {news_days} 天：{first.get('date')} {_fmt_price(first.get('price'))} → {last.get('date')} {_fmt_price(last.get('price'))}"
            )
        _add_source(sources, trend.get("source"))

    lines.extend(["", "## 风险提示"])
    if not trend.get("error"):
        points = trend.get("points") if isinstance(trend.get("points"), list) else []
        trend_source = trend.get("source", "")
        if len(points) < 2:
            lines.append(f"- 价格点不足，无法比较走势（来源：{trend_source}）")
        else:
            try:
                first_price = float(points[0]["price"])
                last_price = float(points[-1]["price"])
            except (TypeError, ValueError, KeyError):
                first_price = last_price = None
            if first_price is None or last_price is None:
                lines.append(f"- 价格点不足，无法比较走势（来源：{trend_source}）")
            elif last_price > first_price:
                lines.append(f"- 价格走高（来源：{trend_source}）")
            elif last_price < first_price:
                lines.append(f"- 价格走低（来源：{trend_source}）")
            else:
                lines.append(f"- 价格持平（来源：{trend_source}）")
        _add_source(sources, trend_source)

    if not resources.get("error"):
        resource_list = resources.get("resources") if isinstance(resources.get("resources"), list) else []
        res_source = resources.get("source") or resources.get("pdf_url") or ""
        indicated = _first_resource(resource_list, "Indicated")
        inferred = _first_resource(resource_list, "Inferred")
        if indicated:
            lines.append(f"- 来源给出了该级别储量（Indicated）（来源：{res_source}）")
        else:
            lines.append(f"- 来源未给出该级别储量（Indicated）（来源：{res_source}）")
        if inferred:
            lines.append(f"- 来源给出了该级别储量（Inferred）（来源：{res_source}）")
        else:
            lines.append(f"- 来源未给出该级别储量（Inferred）（来源：{res_source}）")
        _add_source(sources, res_source)

    if news_empty:
        lines.append("- 新闻窗口内无匹配条目")

    lines.extend(["", "## 来源链接"])
    for source in sources:
        lines.append(f"- {source}")
    if not sources:
        lines.append("- （无）")

    return "\n".join(lines) + "\n"
