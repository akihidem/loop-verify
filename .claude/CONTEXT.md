# loop-verify — CONTEXT

## North star
The paid backend for the self-verification loop. Free loop-kit = Claude checks Claude
(shared blind spots, admitted in its README). loop-verify sells the missing piece:
an INDEPENDENT checker from a different model lineage, as a selectable metered MCP suite.
loop-kit (public, free) stays the funnel; this repo is the product (private, proprietary).

## Architecture
- `loop_verify/checker/` — Checker protocol + Verdict (identical contract to loop-kit's
  validator). Backends: CodexChecker (v0), OpenAI/Gemini (prod seams, NotImplementedError),
  MockChecker (deterministic tests). Selected by LOOP_VERIFY_BACKEND.
- `loop_verify/modes/registry.py` — the suite: A active, B/C/D declared. Per-mode entitlement.
- `loop_verify/metering/` — api-key store (stdlib JSON) + entitlement/monthly-cap gate.
  Paywall MECHANISM only; billing (Stripe) deferred.
- `loop_verify/service.py` — pure logic (no mcp dep, fully unit-testable).
- `loop_verify/server.py` — thin FastMCP stdio wrapper.
- `bench/edge_bench.py` — proves the edge: independent (codex) GO vs naive (mock) NO-GO.

## Frozen acceptance criteria (v0.1.0)
1. independent_verify (mode A) runs end-to-end (service layer) returning the validator
   contract; codex behind the Checker seam, tests use MockChecker (deterministic).
2. Backend seam: CodexChecker works + OpenAI/Gemini stubs; selectable by env.
3. Metering: per-mode entitlement + monthly cap; over-cap denied, counter increments.
4. Edge bench: codex vs naive on fixtures -> GO/NO-GO; exit code = verdict.
5. README: Free vs Pro + honest limits (codex non-scalable / DIY / edge-must-be-proven);
   private repo; proprietary LICENSE.

L0 = pytest (criteria 1-3 deterministic via mock) + bench machinery test.
Real edge = `bench/edge_bench.py --backend codex` (costs codex quota).

## Decisions / honesty
- v0 backend = codex to PROVE the edge cheaply; it does NOT scale to customers.
- "Paid" = api-key + cap + entitlement; no real billing yet.
- Build local only; GitHub (private) push is a later y/n.

## Out of scope (v0.2+)
- HTTP transport + hosted deploy; prod OpenAI/Gemini impls + key mgmt; real billing;
  B/C/D mode implementations; a larger marker-free, lineage-controlled benchmark.
