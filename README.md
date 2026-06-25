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

# HTTP transport (for a remotely-reachable tool):
LOOP_VERIFY_BACKEND=codex ~/.venvs/loop-verify/bin/python -m loop_verify.server --transport http

# OpenAI backend (needs OPENAI_API_KEY + `pip install openai`):
OPENAI_API_KEY=... LOOP_VERIFY_BACKEND=openai \
  ~/.venvs/loop-verify/bin/python -m loop_verify.server
```

Tools: `independent_verify(criteria, artifact)` and `info()`. Backend selected by
`LOOP_VERIFY_BACKEND` (`codex` default | `openai` | `gemini` | `mock`).

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
