"""Pure service logic — no MCP dependency, so it is fully unit-testable.

server.py is a thin FastMCP wrapper over this function.
"""
from __future__ import annotations

from .checker import get_checker
from .checker.base import Verdict


def run_independent_verify(criteria, artifact, *, checker=None, backend=None) -> dict:
    """Run an independent adversarial checker over a deliverable and return the verdict.

    Pass an explicit `checker` (tests inject MockChecker) or a `backend` name to select
    one (codex/openai/gemini/mock); if neither, the default backend (LOOP_VERIFY_BACKEND).
    The independence — a different model lineage from whoever produced the work — is the
    whole point. Returns the validator contract: verdict/passed, per-criterion, defects,
    fix_instructions. Never raises: a misconfigured backend or a crashing checker becomes
    a FAIL verdict, so a server wrapper never goes down.
    """
    if checker is None:
        try:
            checker = get_checker(backend)
        except ValueError as e:
            return Verdict(verdict="FAIL", fix_instructions=str(e)).to_dict()
    try:
        verdict = checker.verify(criteria, artifact)
    except Exception as e:  # noqa: BLE001 — a custom checker may raise; never crash.
        verdict = Verdict(
            verdict="FAIL",
            fix_instructions=f"checker raised: {e}",
            checker=getattr(checker, "name", ""),
            lineage=getattr(checker, "lineage", ""),
        )
    out = verdict.to_dict()
    out["checker"] = verdict.checker or getattr(checker, "name", "")
    out["lineage"] = verdict.lineage or getattr(checker, "lineage", "")
    return out
