# loop-verify — GTM & pricing hypotheses (v0, to validate)

> Discipline: validate demand **before** building billing. Every number here is a
> HYPOTHESIS to test, not a plan. If the cheapest experiments show no one pays above
> COGS, that is a **NO-GO** — reported honestly, same rule as the edge bench. A cheap
> NO-GO is a success of the process, not a failure.

## 1. What we sell, in one line
An independent second opinion on AI-written work: a checker from a **different model
lineage** that catches the defects your agent's own self-check (same family) misses.
Proven: codex caught planted defects a naive same-family check passed (recall 1.0 vs 0.0).

## 2. The core tension — value vs DIY
The honest threat (in our own README): a user can run codex/GPT themselves. So we are
**not** selling model access (that is commodity). We sell:
- **Zero-setup** independent verification wired into the loop (MCP, drop-in for loop-kit's `validator`).
- **Aggregation** across lineages (codex/GPT/Gemini) — pick the one most independent of the builder.
- **Governance** (mode B): frozen-criteria registry + audit trail — what teams need and won't build.
- **The proven edge** + curation (we keep measuring that the checker actually beats same-family).

→ Implication: the buyer who pays is the one for whom **DIY is not free** — i.e. teams
(setup / governance / audit cost), not hobbyists (who will DIY).

## 3. ICP candidates (the bet)
| ICP | Pain | Pays? | Wedge |
|---|---|---|---|
| **A. Indie / solo agentic devs** | "is my AI output correct?" | low ($-sensitive, DIY-prone) | mode A, cheap/usage |
| **B. Small eng teams shipping AI code** | slop in PRs, no reviewer bandwidth | **medium-high** (budget + governance need) | mode A+B as a CI gate + audit |
| **C. AI-tooling / agent-framework builders** | want embeddable independent verify | medium (build-vs-buy) | mode A via API/MCP, white-label |

**Recommended bet: B (small teams) primary.** They have budget, DIY is *not* free for them,
and they need mode B governance (a real moat vs solo DIY). A = top-of-funnel (free/cheap,
feeds awareness). C = partnerships later.

## 4. Pricing hypotheses (per-mode, metered — TO VALIDATE)
COGS = LLM tokens per verification (real). Price must clear COGS + margin.
- **Mode A independent-verify**
  - Free: 20 verifications/mo (funnel from loop-kit).
  - Solo: ~$19/mo, ~300 verifications, overage ~$0.05 each.
  - Team: ~$99/mo, ~3000 verifications, pooled.
- **Mode B governance** (registry/audit): +$/seat/mo — the sticky, higher-margin layer.
- **Mode C analytics**: add-on.
- **Mode D loop-as-a-service**: per-run/compute (highest COGS, premium).

All numbers are guesses to test against willingness-to-pay, not commitments.

## 5. Funnel
loop-kit (free, public, OSS) -> awareness via the methodology article (note/Qiita) + the
2026 "loop engineering" wave -> loop-verify (paid) when the free same-family check is not
enough. The free tier's own README admits the blind spot — that is the honest upsell.

## 6. Demand validation plan (cheapest first — BEFORE billing)
1. **Fake-door landing + waitlist**: a page stating the value + pricing tiers + "join beta".
   Signal: signups, and which tier they pick. Cost: one page.
2. **5-10 problem interviews** with small teams doing agentic coding: do they feel the
   self-graded-slop pain? would they pay? how much? Signal: WTP + ICP fit.
3. **Free manual beta of mode A** (provision keys by hand — the store already supports it)
   to ~10 users. Signal: real usage, retention, "would you pay to keep it?".
4. Only if 1-3 are positive: wire billing (Stripe) + a live prod key.

## 7. Kill criteria (honest NO-GO)
- Waitlist ~0 / interviews say "I'd just run codex myself" -> NO-GO, do not build billing.
- Beta users do not retain / will not pay above COGS -> NO-GO.
- If only solo devs bite (won't pay) and teams don't -> pivot to OSS + sponsorship, not a paid product.

## 8. Recommended first step
Run validation #1 + #2 (landing/waitlist + interviews) — cheapest, fastest demand signal.
Next deliverable I can draft: the landing-page copy + the interview script for the chosen ICP.
