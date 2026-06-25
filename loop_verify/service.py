"""Pure service logic — no MCP dependency, so it is fully unit-testable.

server.py is a thin FastMCP wrapper over these functions.
"""
from __future__ import annotations

import datetime

from .checker import get_checker
from .metering.gate import check_access
from .modes.registry import MODES


def current_month() -> str:
    return datetime.date.today().strftime("%Y-%m")


def run_independent_verify(criteria, artifact, api_key, *, store, checker=None, month=None) -> dict:
    """Mode A. Gate by entitlement+cap, run an independent checker, meter the call."""
    month = month or current_month()
    gate = check_access(store, api_key, "A", month)
    if not gate.allowed:
        return {"allowed": False, "mode": "A", "reason": gate.reason}
    checker = checker or get_checker()
    verdict = checker.verify(criteria, artifact)
    used = store.record_usage(api_key, month)
    out = verdict.to_dict()
    out.update({
        "allowed": True,
        "mode": "A",
        "checker": verdict.checker or getattr(checker, "name", ""),
        "lineage": verdict.lineage or getattr(checker, "lineage", ""),
        "usage_this_month": used,
    })
    return out


def run_stub_mode(mode_key, api_key, *, store, month=None) -> dict:
    """B/C/D: gate identically, but report that the mode is declared, not built."""
    month = month or current_month()
    mode = MODES.get(mode_key)
    if mode is None:
        return {"allowed": False, "reason": f"unknown mode {mode_key}"}
    gate = check_access(store, api_key, mode_key, month)
    if not gate.allowed:
        return {"allowed": False, "mode": mode_key, "reason": gate.reason}
    return {
        "allowed": True,
        "mode": mode_key,
        "status": "not_yet_available",
        "message": f"mode {mode_key} ({mode.name}) is declared but not built in v0.1.0",
    }
