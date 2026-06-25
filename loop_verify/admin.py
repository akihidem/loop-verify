"""Admin CLI — provision and inspect API keys in the metering store.

The metering store is the paywall mechanism; until a key exists with the right
entitlements, the MCP server denies every call. This CLI is how an operator hands
a key to a (beta) customer without editing JSON by hand.

    python -m loop_verify.admin add-key KEY --modes A,B --cap 300
    python -m loop_verify.admin list
    python -m loop_verify.admin show KEY

Store path: $LOOP_VERIFY_STORE or ~/.loop-verify/keys.json (override with --store).
"""
from __future__ import annotations

import argparse
import json
import sys

from .metering.store import Store, default_store_path
from .modes.registry import MODES
from .service import current_month


def _parse_modes(raw: str) -> list[str]:
    modes = [m.strip().upper() for m in raw.split(",") if m.strip()]
    unknown = [m for m in modes if m not in MODES]
    if unknown:
        raise SystemExit(f"unknown mode(s) {unknown}; valid: {sorted(MODES)}")
    if not modes:
        raise SystemExit("at least one mode is required (e.g. --modes A)")
    return modes


def cmd_add_key(store: Store, args) -> int:
    cap = args.cap if args.cap is not None and args.cap >= 0 else None
    exists = store.get_key(args.key) is not None
    if exists and not args.force:
        raise SystemExit(
            f"key '{args.key}' already exists; re-run with --force to update its plan "
            "(usage is preserved)"
        )
    # set_plan preserves the usage counter even on --force — re-provisioning never
    # silently resets quota or wipes the audit trail.
    rec = store.set_plan(args.key, _parse_modes(args.modes), monthly_cap=cap)
    print(json.dumps({"key": args.key, "updated": exists, **rec}, ensure_ascii=False, indent=2))
    return 0


def cmd_list(store: Store, args) -> int:
    month = args.month or current_month()
    rows = {
        k: {
            "entitlements": rec.get("entitlements", []),
            "monthly_cap": rec.get("monthly_cap"),
            "usage_this_month": int((rec.get("usage") or {}).get(month, 0)),
        }
        for k, rec in store.all_keys().items()
    }
    print(json.dumps({"month": month, "keys": rows}, ensure_ascii=False, indent=2))
    return 0


def cmd_show(store: Store, args) -> int:
    rec = store.get_key(args.key)
    if rec is None:
        print(json.dumps({"key": args.key, "found": False}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"key": args.key, "found": True, **rec}, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="loop_verify.admin", description="loop-verify key admin")
    ap.add_argument("--store", default="", help="store path (default: $LOOP_VERIFY_STORE or ~/.loop-verify/keys.json)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add-key", help="create/replace a key with entitlements + monthly cap")
    a.add_argument("key")
    a.add_argument("--modes", default="A", help="comma list of mode keys, e.g. A,B (default A)")
    a.add_argument("--cap", type=int, default=None, help="monthly cap (omit or negative = unlimited)")
    a.add_argument("--force", action="store_true", help="update an existing key's plan (usage preserved)")
    a.set_defaults(func=cmd_add_key)

    li = sub.add_parser("list", help="list keys with this month's usage")
    li.add_argument("--month", default="", help="YYYY-MM (default: current month)")
    li.set_defaults(func=cmd_list)

    sh = sub.add_parser("show", help="show one key's full record")
    sh.add_argument("key")
    sh.set_defaults(func=cmd_show)
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    store = Store(args.store or default_store_path())
    return args.func(store, args)


if __name__ == "__main__":
    sys.exit(main())
