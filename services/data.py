from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def fixtures_dir() -> Path:
    return repo_root() / "fixtures"


def ensure_fixture_mode() -> None:
    mode = os.environ.get("MINING_DATA", "fixture")
    if mode != "fixture":
        print(f"MINING_DATA={mode} is not supported in this build", file=sys.stderr)
        raise SystemExit(1)


def quiet_mcp_logging() -> None:
    logging.getLogger("mcp").setLevel(logging.WARNING)


def load_json(name: str) -> Any:
    path = fixtures_dir() / name
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def demo_pdf_path() -> Path:
    return (fixtures_dir() / "pilbara-lithium.pdf").resolve()
