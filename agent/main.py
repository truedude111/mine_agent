from __future__ import annotations

import asyncio
import os
import sys

from agent import DEFAULT_QUERY
from agent.graph import run_brief_async


def run_brief(query: str) -> str:
    return asyncio.run(run_brief_async(query))


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    query = os.environ.get("BRIEF_QUERY") or DEFAULT_QUERY
    markdown = run_brief(query)
    print(markdown, end="" if markdown.endswith("\n") else "\n")


if __name__ == "__main__":
    main()
