"""The verdict contract — deliberately identical in shape to loop-kit's `validator`
agent output, so an independent checker is a drop-in replacement for the
same-family one.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Protocol, runtime_checkable


@dataclass
class CriterionResult:
    index: int
    ok: bool
    note: str = ""


@dataclass
class Verdict:
    verdict: str = "FAIL"              # "PASS" | "FAIL"
    criteria: list[CriterionResult] = field(default_factory=list)
    defects_outside: list[str] = field(default_factory=list)
    fix_instructions: str = ""
    checker: str = ""                  # which checker/model produced this verdict
    lineage: str = ""                  # model lineage, e.g. "codex/gpt" — the independence claim
    raw: str = ""                      # raw checker text (for audit)

    @property
    def passed(self) -> bool:
        return self.verdict.strip().upper() == "PASS"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["passed"] = self.passed
        return d


@runtime_checkable
class Checker(Protocol):
    """A checker reads frozen criteria + a deliverable and returns a Verdict.

    Implementations MUST NOT mutate the deliverable. The whole point of this
    package is that `name`/`lineage` is different from the caller (which is
    Claude inside loop-kit) — that independence is the value.
    """

    name: str
    lineage: str

    def verify(self, criteria: str, artifact: str) -> Verdict: ...
