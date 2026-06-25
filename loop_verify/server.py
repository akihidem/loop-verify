"""FastMCP server — thin wrapper over service.py.

Run: `python -m loop_verify.server` (stdio) or `--transport http`.
Backend selected by LOOP_VERIFY_BACKEND (default codex).
For the http transport, bind via LOOP_VERIFY_HOST / LOOP_VERIFY_PORT (read at startup,
so FastMCP's host-derived Host-header protection stays consistent). In a container, set
LOOP_VERIFY_HOST=0.0.0.0 (the Dockerfile does) and LOOP_VERIFY_ALLOWED_HOSTS to restrict.
"""
from __future__ import annotations

import os
import sys

from mcp.server.fastmcp import FastMCP

from . import __version__
from .checker import _BACKENDS
from .service import run_independent_verify


def _env_port(default: int = 8000) -> int:
    """Read LOOP_VERIFY_PORT defensively — a bad value warns and falls back to the
    default rather than crashing server startup."""
    raw = os.getenv("LOOP_VERIFY_PORT")
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        print(f"warning: ignoring invalid LOOP_VERIFY_PORT={raw!r}, using {default}", file=sys.stderr)
        return default


def _transport_security():
    """Explicit override for the http Host-header (DNS-rebinding) allowlist.

    When unset, FastMCP derives the protection from the bind host: a localhost bind
    gets a localhost-only allowlist, but binding 0.0.0.0 turns the Host check OFF
    (accepts any Host). So to expose remotely WITH an allowlist — tighter than the
    fully-open 0.0.0.0 default — set LOOP_VERIFY_ALLOWED_HOSTS (a comma list of
    host:port, or "*" to be explicit about disabling it). Origins are derived (http + https).
    """
    raw = os.getenv("LOOP_VERIFY_ALLOWED_HOSTS")
    if not raw:
        return None  # defer to FastMCP's host-derived default (see docstring)
    from mcp.server.transport_security import TransportSecuritySettings

    hosts = [h.strip() for h in raw.split(",") if h.strip()]
    if hosts == ["*"]:
        return TransportSecuritySettings(enable_dns_rebinding_protection=False)
    origins = [f"http://{h}" for h in hosts] + [f"https://{h}" for h in hosts]
    return TransportSecuritySettings(allowed_hosts=hosts, allowed_origins=origins)


# Default to localhost (safe); a container / deploy sets 0.0.0.0 via env.
_fastmcp_kwargs = {"host": os.getenv("LOOP_VERIFY_HOST", "127.0.0.1"), "port": _env_port()}
_sec = _transport_security()
if _sec is not None:  # else let FastMCP apply its built-in secure localhost default
    _fastmcp_kwargs["transport_security"] = _sec
mcp = FastMCP("loop-verify", **_fastmcp_kwargs)


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

    ap = argparse.ArgumentParser(
        description="loop-verify MCP server. Bind via LOOP_VERIFY_HOST / LOOP_VERIFY_PORT "
        "(read at startup so FastMCP's host-derived Host-header protection stays consistent); "
        "set LOOP_VERIFY_ALLOWED_HOSTS to expose remotely with a Host allowlist.",
    )
    ap.add_argument(
        "--transport", default="stdio", choices=["stdio", "http", "sse"],
        help="stdio (default, local) | http (streamable-http) | sse",
    )
    args = ap.parse_args()
    transport = {"stdio": "stdio", "http": "streamable-http", "sse": "sse"}[args.transport]
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
