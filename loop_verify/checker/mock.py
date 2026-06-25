"""MockChecker — deterministic backend for tests and offline demos.

It does NOT call any model. It applies a tiny set of rules so the contract,
parser and server wiring can be tested without burning codex/API quota
(L0 must be deterministic — see loop-protocol).
"""
from __future__ import annotations

from .base import CriterionResult, Verdict


class MockChecker:
    name = "mock"
    lineage = "mock/deterministic"

    def __init__(self, *, force: str | None = None):
        # force="PASS"/"FAIL" pins the verdict; otherwise a trivial heuristic.
        self.force = force

    def verify(self, criteria: str, artifact: str) -> Verdict:
        text = (artifact or "")
        # Heuristic: planted-defect markers used by fixtures/tests.
        planted = [m for m in ("BUG", "TODO", "FIXME", "raise NotImplementedError") if m in text]
        verdict = self.force or ("FAIL" if planted else "PASS")
        crit = [CriterionResult(index=1, ok=(verdict == "PASS"), note="mock")]
        defects = [f"found marker: {m}" for m in planted]
        return Verdict(
            verdict=verdict,
            criteria=crit,
            defects_outside=defects,
            fix_instructions=("remove planted defect markers" if verdict == "FAIL" else ""),
            checker=self.name,
            lineage=self.lineage,
            raw="mock",
        )
