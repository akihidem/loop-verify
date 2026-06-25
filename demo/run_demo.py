"""End-to-end demo — drives the whole loop-verify stack in one command.

It provisions a key in a THROWAWAY store (never touches your real keys), then walks
the value story out loud:

  1. provision a metered API key (the paywall mechanism)
  2. Mode A independent_verify end to end — the validator contract + metering
  3. monthly-cap enforcement — over-cap calls are denied, no overshoot
  4. THE EDGE — an independent checker vs a naive same-family baseline on the same
     planted-defect fixtures (the part free loop-kit cannot do)
  5. the suite — which modes are active vs declared

Runs anywhere, deterministically, with the default mock backend (no quota burned).
Re-run with `--backend codex` to see the REAL edge (costs codex quota):

    python demo/run_demo.py                 # deterministic, offline
    python demo/run_demo.py --backend codex # real independent checker

Exit code 0 iff every mechanism invariant held — so the demo doubles as a smoke test.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # run standalone

from bench.edge_bench import load_fixtures, run_bench  # noqa: E402
from loop_verify.checker import get_checker  # noqa: E402
from loop_verify.metering.store import Store  # noqa: E402
from loop_verify.modes.registry import MODES  # noqa: E402
from loop_verify.service import run_independent_verify  # noqa: E402

MONTH = "2026-06"  # pinned so the demo is deterministic regardless of the calendar
KEY = "demo-key-001"
CAP = 2

CLEAN = "def add(a, b):\n    return a + b\n"
CRITERIA = "1. add(a, b) returns the sum.\n2. add(2, 3) == 5."


def hr(title: str) -> None:
    print(f"\n{'=' * 64}\n{title}\n{'=' * 64}")


def kv(label: str, value) -> None:
    print(f"  {label:<22} {value}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="loop-verify end-to-end demo")
    ap.add_argument("--backend", default="mock", help="mock (default, offline) | codex (real edge) | openai | gemini")
    args = ap.parse_args(argv)

    ok = True  # tracks deterministic mechanism invariants for the exit code

    with tempfile.TemporaryDirectory(prefix="loop-verify-demo-") as tmp:
        store = Store(Path(tmp) / "keys.json")

        # 1. provision -------------------------------------------------------
        hr("1. Provision a metered API key (paywall mechanism)")
        rec = store.add_key(KEY, ["A"], monthly_cap=CAP)
        kv("key", KEY)
        kv("entitlements", rec["entitlements"])
        kv("monthly_cap", rec["monthly_cap"])

        # 2. mode A end to end ----------------------------------------------
        hr("2. Mode A independent_verify — contract + metering")
        out = run_independent_verify(CRITERIA, CLEAN, KEY, store=store, backend=args.backend, month=MONTH)
        kv("allowed", out.get("allowed"))
        kv("verdict", out.get("verdict"))
        kv("passed", out.get("passed"))
        kv("checker / lineage", f"{out.get('checker')} / {out.get('lineage')}")
        kv("usage_this_month", out.get("usage_this_month"))
        contract_keys = {"allowed", "verdict", "passed", "criteria", "fix_instructions"}
        have_contract = contract_keys.issubset(out)
        ok &= bool(out.get("allowed")) and have_contract and out.get("usage_this_month") == 1
        kv("-> contract complete", have_contract)

        # 3. cap enforcement -------------------------------------------------
        hr(f"3. Monthly-cap enforcement (cap = {CAP})")
        run_independent_verify(CRITERIA, CLEAN, KEY, store=store, backend=args.backend, month=MONTH)  # 2nd: hits cap
        kv("usage after 2 calls", store.usage(KEY, MONTH))
        denied = run_independent_verify(CRITERIA, CLEAN, KEY, store=store, backend=args.backend, month=MONTH)
        kv("3rd call allowed", denied.get("allowed"))
        kv("reason", denied.get("reason"))
        kv("usage unchanged", store.usage(KEY, MONTH))
        ok &= denied.get("allowed") is False and "cap" in (denied.get("reason") or "") and store.usage(KEY, MONTH) == CAP

        # 4. the edge --------------------------------------------------------
        hr("4. THE EDGE — independent checker vs naive same-family baseline")
        fixtures = load_fixtures()
        independent = run_bench(fixtures, get_checker(args.backend))
        naive = run_bench(fixtures, get_checker("mock"))  # marker-blind same-family stand-in
        print("  planted-defect fixtures (ground truth in each file):")
        for r in independent["rows"]:
            print(f"    - {r['name']:<22} has_defect={r['has_defect']!s:<5} independent_flagged={r['flagged']}")
        kv("independent verdict", f"{independent['verdict']} (recall={independent['recall']}, fp={independent['false_positive']}, {independent['lineage']})")
        kv("naive verdict", f"{naive['verdict']} (recall={naive['recall']}, fp={naive['false_positive']}, {naive['lineage']})")
        if args.backend == "mock":
            print("  NOTE: with the mock backend both sides are naive — no edge to show.")
            print("        Re-run `python demo/run_demo.py --backend codex` for the REAL edge.")
        else:
            edge = independent["recall"] > naive["recall"]
            kv("-> independent beats naive", edge)

        # 5. the suite -------------------------------------------------------
        hr("5. The suite — active vs declared modes")
        for m in MODES.values():
            print(f"    [{m.key}] {m.name:<20} {m.status:<7} ({m.tool})")
        ok &= any(m.status == "active" for m in MODES.values())

    hr("RESULT")
    kv("backend", args.backend)
    kv("mechanism invariants", "PASS" if ok else "FAIL")
    print()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
