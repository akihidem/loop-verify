# loop-verify — CONTEXT

## North star
An open-source (MIT) **independent checker** for the self-verification loop. Free
loop-kit = Claude checks Claude (shared blind spots, admitted in its README).
loop-verify supplies the missing piece: an INDEPENDENT checker from a different model
lineage (codex / GPT / Gemini), as a drop-in MCP tool. **Just a tool — no accounts,
no metering, no billing.** (Pivoted away from the paid-product framing 2026-06-25.)

## Architecture
- `loop_verify/checker/` — Checker protocol + Verdict (identical contract to loop-kit's
  validator). Backends: CodexChecker (default), OpenAI + Gemini (own-key paths, injectable
  client, unit-tested w/o live key), MockChecker (deterministic tests). Sel by LOOP_VERIFY_BACKEND.
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

## Deploy
- HTTP transport: `server.py --transport http`; bind via LOOP_VERIFY_HOST/PORT (env-only,
  read at construction so FastMCP's host-derived Host-header protection stays consistent).
  Remote exposure: LOOP_VERIFY_ALLOWED_HOSTS allowlist (0.0.0.0 alone disables the Host check).
- Dockerfile (host 0.0.0.0, backend=openai since codex CLI isn't in the image).
- `demo/http_smoke.py` = real MCP client round-trip over http (mock backend, no key). Verified live.

## Out of scope / future
- A larger marker-free, lineage-controlled bench; auth on the http endpoint; a hosted instance.
  (Gemini backend wired 2026-06-25, mirrors openai — injectable client, unit-tested, awaits live key.)
