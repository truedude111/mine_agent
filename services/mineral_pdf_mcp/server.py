from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_SERVICES = Path(__file__).resolve().parent.parent
if str(_SERVICES) not in sys.path:
    sys.path.insert(0, str(_SERVICES))

from data import demo_pdf_path, ensure_fixture_mode, load_json, quiet_mcp_logging, repo_root  # noqa: E402

ensure_fixture_mode()

mcp = FastMCP("mineral-pdf-mcp")
quiet_mcp_logging()


def _resolve_pdf(pdf_url: str) -> Path:
    raw = Path(pdf_url)
    if raw.is_absolute():
        return raw.resolve()
    return (repo_root() / raw).resolve()


@mcp.tool()
def extract_resources(pdf_url: str) -> dict:
    expected = demo_pdf_path()
    try:
        candidate = _resolve_pdf(pdf_url)
    except OSError:
        return {"pdf_url": pdf_url, "error": "unsupported_pdf"}
    if candidate != expected:
        return {"pdf_url": pdf_url, "error": "unsupported_pdf"}
    if not candidate.is_file():
        return {"pdf_url": pdf_url, "error": f"missing_pdf:{candidate}"}
    payload = load_json("resources.json")
    return {
        "pdf_url": payload.get("pdf_url", "fixtures/pilbara-lithium.pdf"),
        "source": payload.get("source", "fixtures/pilbara-lithium.pdf"),
        "resources": payload.get("resources", []),
    }
