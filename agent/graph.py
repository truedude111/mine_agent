from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agent.parse import parse_node
from agent.render import render_brief
from agent.state import BriefState
from agent.tools import McpHub, repo_root


def build_graph(hub: McpHub):
    async def fetch_news(state: BriefState) -> dict:
        query = f"{state['region']} {state['commodity']}"
        result = await hub.call(
            "mining-news-mcp",
            "search",
            {"query": query, "days": state["news_days"]},
        )
        return {"articles": result}

    async def fetch_price(state: BriefState) -> dict:
        result = await hub.call(
            "lme-price-mcp",
            "get_price",
            {"commodity": state["commodity"], "date": state["as_of"]},
        )
        return {"price": result}

    async def fetch_trend(state: BriefState) -> dict:
        result = await hub.call(
            "lme-price-mcp",
            "get_trend",
            {"commodity": state["commodity"], "days": state["news_days"]},
        )
        return {"trend": result}

    async def enrich(state: BriefState) -> dict:
        articles = state.get("articles") if isinstance(state.get("articles"), dict) else {}
        items = articles.get("items") if isinstance(articles.get("items"), list) else []
        bodies = []
        for item in items:
            url = item.get("url", "")
            bodies.append(await hub.call("mining-news-mcp", "fetch_article", {"url": url}))
        pdf_url = str(repo_root() / "fixtures" / "pilbara-lithium.pdf")
        resources = await hub.call(
            "mineral-pdf-mcp",
            "extract_resources",
            {"pdf_url": pdf_url},
        )
        return {"bodies": bodies, "resources": resources}

    def compose(state: BriefState) -> dict:
        return {"markdown": render_brief(state)}

    graph = StateGraph(BriefState)
    graph.add_node("parse", parse_node)
    graph.add_node("fetch_news", fetch_news)
    graph.add_node("fetch_price", fetch_price)
    graph.add_node("fetch_trend", fetch_trend)
    graph.add_node("enrich", enrich)
    graph.add_node("compose", compose)
    graph.add_edge(START, "parse")
    graph.add_edge("parse", "fetch_news")
    graph.add_edge("parse", "fetch_price")
    graph.add_edge("parse", "fetch_trend")
    graph.add_edge("fetch_news", "enrich")
    graph.add_edge("fetch_price", "enrich")
    graph.add_edge("fetch_trend", "enrich")
    graph.add_edge("enrich", "compose")
    graph.add_edge("compose", END)
    return graph.compile()


async def run_brief_state(query: str) -> BriefState:
    hub = McpHub()
    try:
        await hub.start()
        app = build_graph(hub)
        return await app.ainvoke({"query": query})
    finally:
        await hub.close()


async def run_brief_async(query: str) -> str:
    state = await run_brief_state(query)
    return state.get("markdown", "")
