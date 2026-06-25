# loop-verify (paid)

Independent verification for the self-verification loop — the part the free
**loop-kit** loop honestly admits it cannot do.

Free loop-kit checks Claude's work *with Claude* (same family → shared blind spots).
loop-verify supplies an **independent checker from a different model lineage**
(codex / GPT / Gemini), delivered as a metered MCP suite.

> Proprietary. Not open source. See `LICENSE`.

## Free vs Pro

| | Free (loop-kit) | Pro (loop-verify) |
|---|---|---|
| Checker | Claude validates Claude | a **different lineage** (codex / GPT / Gemini) |
| Blind spots | shared (same family) | broken by independence |
| L0 deterministic gate | yes (yours) | yes (yours) |
| Delivery | local agent | metered MCP suite, per-mode entitlement |

The verdict contract is identical to loop-kit's `validator`, so `independent_verify`
is a drop-in replacement for the free same-family check.

## Selectable suite (à la carte)

A key buys only the modes it needs (per-mode entitlement + monthly cap).

| Mode | MCP tool | v0.1.0 |
|---|---|---|
| **A** independent-verify | `independent_verify` | **active** |
| B governance (criteria registry / audit) | `verification_registry` | declared |
| C analytics (Goodhart-risk) | `verification_analytics` | declared |
| D loop-as-a-service | `run_loop` | declared |

v0 builds **A solid**; B/C/D are declared so the suite shape and the entitlement /
metering plumbing are real and each can be lit up without re-architecting.

## Run

```bash
python3 -m venv ~/.venvs/loop-verify
~/.venvs/loop-verify/bin/pip install -r requirements.txt

# local (stdio), codex backend — the cheap edge-prover:
LOOP_VERIFY_BACKEND=codex ~/.venvs/loop-verify/bin/python -m loop_verify.server

# remote service (HTTP), prod OpenAI backend (needs OPENAI_API_KEY + `pip install openai`):
OPENAI_API_KEY=... LOOP_VERIFY_BACKEND=openai \
  ~/.venvs/loop-verify/bin/python -m loop_verify.server --transport http
```

Backend via `LOOP_VERIFY_BACKEND` (`codex` default | `openai` prod | `gemini` | `mock`);
key store via `LOOP_VERIFY_STORE` (default `~/.loop-verify/keys.json`). Provision a key
in the store with its entitled modes and monthly cap.

## The edge must be proven first

```bash
python bench/edge_bench.py --backend codex   # real independent checker -> GO/NO-GO
python bench/edge_bench.py --backend mock     # naive/blind baseline -> typically NO-GO
```

The gap between an independent checker (GO) and a naive one (NO-GO) **is** the product.
Exit code = the edge verdict, so it can gate CI.

## Honest limits

- **COGS / scale**: the codex backend runs on the operator's personal ChatGPT Plus
  quota — **not scalable to paying customers**, so codex stays the cheap *edge-prover*.
  The **OpenAI prod backend is now wired** (`LOOP_VERIFY_BACKEND=openai`, server-side
  key) and removes that blocker — it is unit-tested with an injected client and awaits a
  live key. An HTTP transport (`--transport http`) makes it a remotely-reachable service.
- **DIY threat**: a customer can run codex themselves. The moat is aggregation,
  metering, zero-setup, the *proven* edge, and curation — not secrecy.
- **Independent ≠ ground truth**: a different lineage reduces shared blind spots; it
  does not eliminate error. Consistent with loop-kit's own honesty.
- **The edge is the heart**: if the bench ever shows the independent checker ≈ a naive
  one, the value collapses — that is a NO-GO, reported honestly, not buried.
- **"Paid" in v0 is the paywall mechanism** (api-key + monthly cap + per-mode
  entitlement). Real billing (Stripe etc.) is a later seam, not wired here.
