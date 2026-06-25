"""The selectable suite. Users buy modes à la carte (per-mode entitlement).

v0.1.0 builds mode A solid; B/C/D are DECLARED so the suite shape and the
entitlement/metering plumbing are real, and each can be lit up later without
re-architecting. (Honest: only A is functional today.)
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Mode:
    key: str
    name: str
    tool: str
    status: str   # "active" | "stub"
    summary: str


MODES: dict[str, Mode] = {
    "A": Mode(
        "A", "independent-verify", "independent_verify", "active",
        "Independent adversarial verification by a different model lineage — the part free loop-kit cannot do.",
    ),
    "B": Mode(
        "B", "governance", "verification_registry", "stub",
        "Frozen-criteria registry, verification history and audit log for teams.",
    ),
    "C": Mode(
        "C", "analytics", "verification_analytics", "stub",
        "Aggregate loop analytics and Goodhart-risk scoring across runs.",
    ),
    "D": Mode(
        "D", "loop-as-a-service", "run_loop", "stub",
        "Headless build-and-verify to completion (done-for-you).",
    ),
}


def active_modes() -> list[Mode]:
    return [m for m in MODES.values() if m.status == "active"]
