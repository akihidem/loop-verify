"""Edge bench — does independence actually help?

Claim to check: an INDEPENDENT checker (different model lineage) catches defects a
lenient/same-family check misses. Fixtures carry ground truth (`has_defect`); a
checker "catches" a defective fixture by returning FAIL.

Run for real:   python bench/edge_bench.py --backend codex
Contrast:       python bench/edge_bench.py --backend mock   (marker-blind -> misses real bugs -> NO-GO)

The gap between codex (GO) and a naive check (NO-GO) is the reason to use the tool.
Exit code = the edge verdict (GO -> 0, NO-GO -> 1) so it can act as a CI gate.

Honest limit: 9 hand-written fixtures (4 clean / 5 buggy, diverse bug classes) —
modest, not a statistically large suite. A larger, marker-free, lineage-controlled
benchmark is future work.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # make `python bench/edge_bench.py` work standalone

from loop_verify.checker import get_checker  # noqa: E402

FIX_DIR = Path(__file__).resolve().parent / "fixtures"


def load_fixtures() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(FIX_DIR.glob("*.json"))]


def run_bench(fixtures: list[dict], checker) -> dict:
    rows = []
    for fx in fixtures:
        v = checker.verify(fx["criteria"], fx["artifact"])
        rows.append({
            "name": fx["name"],
            "has_defect": bool(fx["has_defect"]),
            "flagged": (not v.passed),          # checker called it defective
            "verdict": v.verdict,
        })
    defective = [r for r in rows if r["has_defect"]]
    clean = [r for r in rows if not r["has_defect"]]
    recall = (sum(r["flagged"] for r in defective) / len(defective)) if defective else 0.0
    false_pos = (sum(r["flagged"] for r in clean) / len(clean)) if clean else 0.0
    go = recall >= 0.5 and false_pos <= 0.5
    return {
        "verdict": "GO" if go else "NO-GO",
        "recall": round(recall, 3),
        "false_positive": round(false_pos, 3),
        "n": len(rows),
        "checker": getattr(checker, "name", "?"),
        "lineage": getattr(checker, "lineage", ""),
        "rows": rows,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="loop-verify edge bench")
    ap.add_argument("--backend", default="codex", help="codex (real) | mock (smoke) | openai | gemini")
    ap.add_argument("--out", default="", help="optional path to write the report JSON")
    args = ap.parse_args(argv)

    checker = get_checker(args.backend)
    report = run_bench(load_fixtures(), checker)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    return 0 if report["verdict"] == "GO" else 1


if __name__ == "__main__":
    sys.exit(main())
