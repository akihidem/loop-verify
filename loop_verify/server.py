"""FastMCP stdio server — thin wrapper over service.py.

Run: `python -m loop_verify.server` (stdio). Prod will add an HTTP transport.
Backend selected by LOOP_VERIFY_BACKEND (default codex); key store at
LOOP_VERIFY_STORE (default ~/.loop-verify/keys.json).
"""
from __future__ import annotations

import os
from dataclasses import asdict
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from . import __version__
from .metering.store import Store
from .modes.registry import MODES
from .service import run_independent_verify, run_stub_mode

_STORE_PATH = os.getenv("LOOP_VERIFY_STORE", str(Path.home() / ".loop-verify" / "keys.json"))
_store = Store(_STORE_PATH)

mcp = FastMCP("loop-verify")


@mcp.tool()
def independent_verify(criteria: str, artifact: str, api_key: str = "") -> dict:
    """Mode A — independent adversarial verification by a DIFFERENT model lineage than Claude.

    criteria: the frozen YES/NO acceptance criteria.
    artifact: the deliverable (a unified diff, or file contents) to inspect.
    api_key: your loop-verify key (gates entitlement + monthly cap).
    Returns the validator contract: verdict/passed, per-criterion, defects, fix_instructions.
    """
    return run_independent_verify(criteria, artifact, api_key, store=_store)


@mcp.tool()
def list_modes() -> dict:
    """List the suite modes and which are active vs declared."""
    return {"version": __version__, "modes": {k: asdict(m) for k, m in MODES.items()}}


@mcp.tool()
def verification_registry(api_key: str = "") -> dict:
    """Mode B (declared) — frozen-criteria registry / audit. Not built in v0."""
    return run_stub_mode("B", api_key, store=_store)


@mcp.tool()
def verification_analytics(api_key: str = "") -> dict:
    """Mode C (declared) — aggregate loop analytics. Not built in v0."""
    return run_stub_mode("C", api_key, store=_store)


@mcp.tool()
def run_loop(api_key: str = "") -> dict:
    """Mode D (declared) — loop-as-a-service. Not built in v0."""
    return run_stub_mode("D", api_key, store=_store)


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="loop-verify MCP server")
    ap.add_argument(
        "--transport", default="stdio", choices=["stdio", "http", "sse"],
        help="stdio (default, local) | http (streamable-http, for remote customers) | sse",
    )
    args = ap.parse_args()
    transport = {"stdio": "stdio", "http": "streamable-http", "sse": "sse"}[args.transport]
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
