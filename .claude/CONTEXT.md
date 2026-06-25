# loop-verify — CONTEXT

## North star
An open-source (MIT) **independent checker** for the self-verification loop. Free
loop-kit = Claude checks Claude (shared blind spots, admitted in its README).
loop-verify supplies the missing piece: an INDEPENDENT checker from a different model
lineage (codex / GPT / Gemini), as a drop-in MCP tool. **Just a tool — no accounts,
no metering, no billing.** (Pivoted away from the paid-product framing 2026-06-25.)

## Architecture
- `loop_verify/checker/` — Checker protocol + Verdict (identical contract to loop-kit's
  validator). Backends: CodexChecker (default), OpenAI (own-key path), Gemini (stub),
  MockChecker (deterministic tests). Selected by LOOP_VERIFY_BACKEND.
- `loop_verify/service.py` — pure logic: run_independent_verify(criteria, artifact,
  checker=|backend=). Never raises (bad backend / crashing checker -> FAIL verdict).
- `loop_verify/server.py` — thin FastMCP wrapper. Tools: independent_verify, info.
- `bench/edge_bench.py` — does independence help? independent (codex) GO vs naive (mock)
  NO-GO. Exit code = verdict.
- `demo/run_demo.py` — one-command demo: contract + the edge. mock default / --backend codex.

## L0
`~/.venvs/loop-verify/bin/python -m pytest tests -q`. Deterministic via MockChecker.
Real edge = `bench/edge_bench.py --backend codex` (costs codex quota).

## Decisions / honesty
- Default backend = codex (operator ChatGPT Plus quota): fine personal/local; use the
  OpenAI backend with your own key to serve many users.
- Independent ≠ ground truth. If the bench ever shows independent ≈ naive, there's no
  reason to use it — report NO-GO honestly.
- The checker prompt must NOT force false positives (old Rule 4 did; fixed — a checker
  that can never PASS has no precision).

## Removed (was the paid-product machinery)
- `loop_verify/metering/` (api-key store + entitlement/cap gate), `loop_verify/admin.py`
  (key CLI), `loop_verify/modes/` (A/B/C/D à-la-carte suite), `docs/GTM.md`, proprietary
  LICENSE -> MIT. Repo made public.

## Out of scope / future
- Gemini backend impl; HTTP hosted deploy; a larger marker-free, lineage-controlled bench.
