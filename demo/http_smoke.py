"""HTTP smoke test — proves the server is reachable over the streamable-http transport.

Boots `loop_verify.server --transport http` on a free port (mock backend, no quota),
opens a real MCP client session against it, lists the tools and calls both — then
tears the server down. Exit code 0 iff the round-trip worked.

    python demo/http_smoke.py

This is the HTTP-transport counterpart to demo/run_demo.py (which uses the service
layer directly). It needs no API key.
"""
from __future__ import annotations

import asyncio
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_port(host: str, port: int, timeout: float = 20.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket() as s:
            s.settimeout(0.5)
            if s.connect_ex((host, port)) == 0:
                return True
        time.sleep(0.2)
    return False


def _payload(result) -> dict:
    """A tool result carries its dict either as structuredContent or as JSON text content."""
    import json
    if getattr(result, "structuredContent", None):
        return result.structuredContent
    for c in result.content:
        text = getattr(c, "text", None)
        if text:
            return json.loads(text)
    return {}


async def _exercise(url: str) -> dict:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = [t.name for t in (await session.list_tools()).tools]
            info = _payload(await session.call_tool("info", {}))
            verify = _payload(await session.call_tool(
                "independent_verify",
                {"criteria": "1. add returns the sum.", "artifact": "def add(a, b):\n    return a + b\n"},
            ))
            return {"tools": tools, "info": info, "verify": verify}


def main() -> int:
    host, port = "127.0.0.1", _free_port()
    env = {**os.environ, "LOOP_VERIFY_BACKEND": "mock", "LOOP_VERIFY_HOST": host, "LOOP_VERIFY_PORT": str(port)}
    proc = subprocess.Popen(
        [sys.executable, "-m", "loop_verify.server", "--transport", "http"],
        cwd=str(ROOT), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    rc, server_out = 1, ""
    try:
        if not _wait_port(host, port):
            print("FAIL: server did not start listening")
        else:
            result = asyncio.run(_exercise(f"http://{host}:{port}/mcp"))
            print(f"  reachable at   http://{host}:{port}/mcp")
            print(f"  tools          {result['tools']}")
            print(f"  info()         {result['info']}")
            print(f"  verify.passed  {result['verify'].get('passed')}  verdict={result['verify'].get('verdict')}")
            ok = (
                "independent_verify" in result["tools"]
                and "info" in result["tools"]
                and result["verify"].get("verdict") in ("PASS", "FAIL")
            )
            print(f"\n  HTTP round-trip {'PASS' if ok else 'FAIL'}")
            rc = 0 if ok else 1
    finally:
        # Always reap the child via communicate() — never a blocking read on a live process.
        proc.terminate()
        try:
            server_out, _ = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            server_out, _ = proc.communicate()
    if rc != 0 and server_out:
        print("--- server output ---\n" + server_out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
