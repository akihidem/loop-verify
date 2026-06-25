"""End-to-end demo — see loop-verify work in one command.

  1. independent_verify on a clean artifact — the validator contract
  2. THE EDGE — an independent checker vs a naive same-family baseline on the same
     planted-defect fixtures (the part free loop-kit cannot do)

Runs anywhere, deterministically, with the default mock backend (no quota burned).
Re-run with `--backend codex` to see the REAL edge (costs codex quota):

    python demo/run_demo.py                 # deterministic, offline
    python demo/run_demo.py --backend codex # real independent checker

Exit code 0 iff the demo's invariants held — so it doubles as a smoke test.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # run standalone

from bench.edge_bench import load_fixtures, run_bench  # noqa: E402
from loop_verify.checker import get_checker  # noqa: E402
from loop_verify.service import run_independent_verify  # noqa: E402

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

    ok = True  # tracks deterministic invariants for the exit code

    # 1. the contract -------------------------------------------------------
    hr("1. independent_verify — the validator contract")
    out = run_independent_verify(CRITERIA, CLEAN, backend=args.backend)
    kv("verdict", out.get("verdict"))
    kv("passed", out.get("passed"))
    kv("checker / lineage", f"{out.get('checker')} / {out.get('lineage')}")
    contract_keys = {"verdict", "passed", "criteria", "defects_outside", "fix_instructions"}
    have_contract = contract_keys.issubset(out)
    kv("-> contract complete", have_contract)
    ok &= have_contract

    # 2. the edge -----------------------------------------------------------
    hr("2. THE EDGE — independent checker vs naive same-family baseline")
    fixtures = load_fixtures()
    independent = run_bench(fixtures, get_checker(args.backend))
    naive = run_bench(fixtures, get_checker("mock"))  # marker-blind same-family stand-in
    print("  planted-defect fixtures (ground truth in each file):")
    for r in independent["rows"]:
        print(f"    - {r['name']:<26} has_defect={r['has_defect']!s:<5} independent_flagged={r['flagged']}")
    kv("independent verdict", f"{independent['verdict']} (recall={independent['recall']}, fp={independent['false_positive']}, {independent['lineage']})")
    kv("naive verdict", f"{naive['verdict']} (recall={naive['recall']}, fp={naive['false_positive']}, {naive['lineage']})")
    if args.backend == "mock":
        print("  NOTE: with the mock backend both sides are naive — no edge to show.")
        print("        Re-run `python demo/run_demo.py --backend codex` for the REAL edge.")
    else:
        kv("-> independent beats naive", independent["recall"] > naive["recall"])

    hr("RESULT")
    kv("backend", args.backend)
    kv("invariants", "PASS" if ok else "FAIL")
    print()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
