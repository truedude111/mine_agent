import asyncio
import os

from agent import DEFAULT_QUERY
from agent.graph import run_brief_state
from agent.render import render_brief


def test_run_brief_matches_template():
    os.environ["MINING_DATA"] = "fixture"
    state = asyncio.run(run_brief_state(DEFAULT_QUERY))
    markdown = state["markdown"]
    without = dict(state)
    without.pop("markdown", None)
    assert markdown == render_brief(without)
    assert "Pilbara lithium miners keep shipments on schedule" in markdown
    assert "Indicated" in markdown
    assert "Inferred" in markdown
    assert "12.4" in markdown
    assert "980" in markdown
    assert "fixture://news/pilbara-lithium-1" in markdown
    assert "fixture://prices/lithium" in markdown
    assert "fixtures/pilbara-lithium.pdf" in markdown
