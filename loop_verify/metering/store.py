"""API-key registry + monthly usage counter (stdlib JSON store).

A key record: {entitlements: [mode keys], monthly_cap: int|None, usage: {YYYY-MM: count}}.
This is the paywall MECHANISM. Real billing (Stripe etc.) is a later seam — here a
key is "entitled" iff it exists in the store with the mode in its plan. The month is
always passed in by callers so logic stays deterministic under test.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path


class Store:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._lock = threading.Lock()
        self._data: dict = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8") or "{}")
            except json.JSONDecodeError:
                return {}
        return {}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8")

    def get_key(self, api_key: str) -> dict | None:
        return self._data.get(api_key)

    def add_key(self, api_key: str, entitlements, monthly_cap: int | None = None) -> dict:
        with self._lock:
            self._data[api_key] = {
                "entitlements": list(entitlements),
                "monthly_cap": monthly_cap,
                "usage": {},
            }
            self._save()
            return self._data[api_key]

    def usage(self, api_key: str, month: str) -> int:
        rec = self._data.get(api_key) or {}
        return int((rec.get("usage") or {}).get(month, 0))

    def record_usage(self, api_key: str, month: str, n: int = 1) -> int:
        with self._lock:
            rec = self._data.setdefault(
                api_key, {"entitlements": [], "monthly_cap": None, "usage": {}}
            )
            usage = rec.setdefault("usage", {})
            usage[month] = int(usage.get(month, 0)) + n
            self._save()
            return usage[month]

    def try_consume(self, api_key: str, month: str) -> tuple[bool, int]:
        """Atomically reserve one unit against the key's own monthly cap, under the lock.

        Reading the cap and incrementing the counter happen under a single lock, so
        this is the sole source of truth for the cap decision — no check-then-increment
        race, and no cap read outside the lock (TOCTOU). Returns (ok, used_after).
        ok=False with NO increment (and NO record creation) if the key is unknown or
        its cap is already reached — fail closed.
        """
        with self._lock:
            rec = self._data.get(api_key)
            if rec is None:
                return (False, 0)
            cap = rec.get("monthly_cap")
            usage = rec.setdefault("usage", {})
            used = int(usage.get(month, 0))
            if cap is not None and used >= cap:
                return (False, used)
            usage[month] = used + 1
            self._save()
            return (True, usage[month])
