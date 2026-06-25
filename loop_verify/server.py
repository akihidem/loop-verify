"""FastMCP server — thin wrapper over service.py.

Run: `python -m loop_verify.server` (stdio) or `--transport http`.
Backend selected by LOOP_VERIFY_BACKEND (default codex).
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import __version__
from .checker import _BACKENDS
from .service import run_independent_verify

mcp = FastMCP("loop-verify")


@mcp.tool()
def independent_verify(criteria: str, artifact: str) -> dict:
    """Independent adversarial verification by a DIFFERENT model lineage than Claude.

    Free loop-kit checks Claude's work with Claude (shared blind spots). This runs an
    independent checker (codex / GPT / Gemini) instead — a drop-in for loop-kit's
    same-family `validator`.

    criteria: the frozen YES/NO acceptance criteria.
    artifact: the deliverable (a unified diff, or file contents) to inspect.
    Returns the validator contract: verdict/passed, per-criterion, defects, fix_instructions.
    """
    return run_independent_verify(criteria, artifact)


@mcp.tool()
def info() -> dict:
    """Version and the available checker backends."""
    return {"version": __version__, "backends": sorted(_BACKENDS)}


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="loop-verify MCP server")
    ap.add_argument(
        "--transport", default="stdio", choices=["stdio", "http", "sse"],
        help="stdio (default, local) | http (streamable-http) | sse",
    )
    args = ap.parse_args()
    transport = {"stdio": "stdio", "http": "streamable-http", "sse": "sse"}[args.transport]
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
