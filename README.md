# loop-verify

**Have a *different* AI grade the work your AI just did.**

loop-verify is an **independent checker** for the self-verification loop — the part the
[loop-kit](https://github.com/akihidem/loop-kit) loop honestly admits it cannot do.

When an AI checks its own work, it shares its own blind spots. Free loop-kit checks
Claude's work *with Claude* (same family → the same misses slip through). loop-verify
hands the grading to a **different model lineage** (codex / GPT / Gemini), so defects the
self-check waves through get caught. The verdict format is identical to loop-kit's
`validator`, so it's a **drop-in replacement** for the same-family check.

> Open source (MIT). Just a tool — no accounts, no metering, no billing.

## What it does

- **In:** your frozen YES/NO acceptance `criteria` + the `artifact` to inspect (a diff or
  file contents).
- **Out:** a verdict — `PASS`/`FAIL`, each criterion `OK`/`NG`, any defects outside the
  criteria, and concrete `fix_instructions`. (Same contract as loop-kit's `validator`.)
- **The point:** the grader is a *different* model family from whoever wrote the work, so
  it doesn't share their blind spots. That independence is the whole value — and it's
  measurable (see [the edge bench](#does-independence-actually-help-the-edge-bench)).

Three ways to use it: as an [MCP server](#run-as-an-mcp-server), as a
[Python function](#use-it-from-python), or via the [edge bench](#does-independence-actually-help-the-edge-bench).

## Install

```bash
python3 -m venv ~/.venvs/loop-verify
~/.venvs/loop-verify/bin/pip install -r requirements.txt
```

## Demo (one command, runs anywhere)

```bash
python demo/run_demo.py                  # deterministic, offline (mock backend)
python demo/run_demo.py --backend codex  # the REAL edge (costs codex quota)
```

Exit code 0 iff the demo's invariants held, so it doubles as a smoke test. With
`--backend codex` it shows the independent checker catching planted defects a naive
same-family check misses.

## Run as an MCP server

```bash
# local (stdio), codex backend:
LOOP_VERIFY_BACKEND=codex ~/.venvs/loop-verify/bin/python -m loop_verify.server

# HTTP transport (binds 127.0.0.1:8000 by default; localhost-only Host check):
LOOP_VERIFY_BACKEND=codex ~/.venvs/loop-verify/bin/python -m loop_verify.server --transport http

# ...to serve other hosts, bind all interfaces and allow their Host header:
LOOP_VERIFY_HOST=0.0.0.0 LOOP_VERIFY_PORT=8000 LOOP_VERIFY_ALLOWED_HOSTS=myhost:8000 \
LOOP_VERIFY_BACKEND=codex ~/.venvs/loop-verify/bin/python -m loop_verify.server --transport http
# (LOOP_VERIFY_ALLOWED_HOSTS="*" disables the Host check; binding 0.0.0.0 alone also
#  opens it. Host/port are read at startup — set them via env, not flags.)

# OpenAI backend (needs OPENAI_API_KEY + `pip install openai`):
OPENAI_API_KEY=... LOOP_VERIFY_BACKEND=openai \
  ~/.venvs/loop-verify/bin/python -m loop_verify.server

# Gemini backend (needs GEMINI_API_KEY + `pip install google-genai`):
GEMINI_API_KEY=... LOOP_VERIFY_BACKEND=gemini \
  ~/.venvs/loop-verify/bin/python -m loop_verify.server
```

Tools: `independent_verify(criteria, artifact)` and `info()`. Backend selected by
`LOOP_VERIFY_BACKEND` (`codex` default | `openai` | `gemini` | `mock`). For http, bind
with `LOOP_VERIFY_HOST` / `LOOP_VERIFY_PORT` (read at startup).

Verify the http transport is reachable end to end (boots a server, runs a real MCP
client round-trip, no key needed):

```bash
python demo/http_smoke.py
```

## Wire it into loop-kit's loop-protocol

[loop-kit](https://github.com/akihidem/loop-kit)'s `loop-protocol` skill already **prefers a
cross-vendor checker when one is available** and falls back to its bundled same-family haiku
`validator` otherwise. To make loop-verify that checker, run it as an MCP server (above) so the
`independent_verify(criteria, artifact)` tool is in the session — loop-protocol picks it up
automatically. Nothing to patch in loop-kit: the verdict contract is identical, so it's a genuine
drop-in. Without loop-verify, loop-kit still runs on the haiku validator (zero external accounts);
with it, the loop reaches real cross-lineage independence.

## Deploy (Docker)

The codex backend needs the `codex` CLI (not in the image), so a container uses a
key-based backend:

```bash
docker build -t loop-verify .
docker run --rm -p 8000:8000 \
  -e LOOP_VERIFY_BACKEND=openai -e OPENAI_API_KEY=sk-... \
  loop-verify
# MCP endpoint: http://localhost:8000/mcp
```

The image binds `0.0.0.0`, so FastMCP's DNS-rebinding Host check is **off by default**
(the container accepts any `Host` header). To restrict it, add
`-e LOOP_VERIFY_ALLOWED_HOSTS=myhost:8000`.

## Use it from Python

```python
from loop_verify.service import run_independent_verify

result = run_independent_verify(criteria, artifact, backend="codex")
# -> {"verdict": "PASS"|"FAIL", "passed": bool, "criteria": [...],
#     "defects_outside": [...], "fix_instructions": str, "checker": ..., "lineage": ...}
```

## Does independence actually help? (the edge bench)

```bash
python bench/edge_bench.py --backend codex   # independent checker -> GO/NO-GO
python bench/edge_bench.py --backend mock     # naive/blind baseline -> typically NO-GO
```

The gap between an independent checker (catches planted defects) and a naive one
(misses them) is the whole reason to use this. Exit code = the edge verdict, so it
can gate CI.

Measured on the bundled 9 fixtures (4 clean / 5 buggy, diverse bug classes): the codex
backend scored **recall 1.0, false-positive 0.0 → GO** (every real bug flagged, every
clean artifact passed), while the naive same-family baseline misses them → NO-GO.

## Honest limits

- **codex backend cost**: the codex backend runs on the operator's personal ChatGPT
  Plus quota — fine for personal/local use, not for serving many users. Use the OpenAI
  backend with your own key for that.
- **Independent ≠ ground truth**: a different lineage reduces shared blind spots; it
  does not eliminate error.
- **The edge is the point**: if the bench ever shows the independent checker ≈ a naive
  one, there is no reason to use it — that is a NO-GO, reported honestly, not buried.
