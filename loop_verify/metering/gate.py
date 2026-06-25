"""Per-mode entitlement + monthly-cap gate. Deterministic (month passed in)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GateResult:
    allowed: bool
    reason: str = "ok"


def check_access(store, api_key: str, mode_key: str, month: str) -> GateResult:
    rec = store.get_key(api_key)
    if rec is None:
        return GateResult(False, "unknown api key")
    if mode_key not in (rec.get("entitlements") or []):
        return GateResult(False, f"mode {mode_key} not in your plan")
    cap = rec.get("monthly_cap")
    used = int((rec.get("usage") or {}).get(month, 0))
    if cap is not None and used >= cap:
        return GateResult(False, f"monthly cap reached ({used}/{cap})")
    return GateResult(True, "ok")
