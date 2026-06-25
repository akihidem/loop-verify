# loop-verify

An **independent checker** for the self-verification loop — the part the
[loop-kit](https://github.com/akihidem/loop-kit) loop honestly admits it cannot do.

Free loop-kit checks Claude's work *with Claude* (same family → shared blind spots).
loop-verify runs an **independent checker from a different model lineage**
(codex / GPT / Gemini) instead. The verdict contract is identical to loop-kit's
`validator`, so it is a **drop-in replacement** for the same-family check.

> Open source (MIT). Just a tool — no accounts, no metering, no billing.

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

## Honest limits

- **codex backend cost**: the codex backend runs on the operator's personal ChatGPT
  Plus quota — fine for personal/local use, not for serving many users. Use the OpenAI
  backend with your own key for that.
- **Independent ≠ ground truth**: a different lineage reduces shared blind spots; it
  does not eliminate error.
- **The edge is the point**: if the bench ever shows the independent checker ≈ a naive
  one, there is no reason to use it — that is a NO-GO, reported honestly, not buried.
