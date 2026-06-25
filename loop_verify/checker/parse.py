"""Parse a checker's free text into a structured Verdict.

The prompt asks every backend (codex / GPT / Gemini) to emit the same fixed
format. Backends are chatty (codex prints agent activity first), so we scan the
whole output and take the LAST verdict block — that is the final answer.
"""
from __future__ import annotations

import re

from .base import CriterionResult, Verdict

_VERDICT_RE = re.compile(r"Verdict:\s*(PASS|FAIL)", re.IGNORECASE)
_CRIT_RE = re.compile(r"\[(?:criterion\s*)?(\d+)\][ \t]*(OK|NG)\b(?:[ \t]*[-—:][ \t]*([^\n]*))?", re.IGNORECASE)
_DEFECTS_RE = re.compile(r"Defects outside the criteria:\s*(.*?)(?:\nFix instructions:|\Z)", re.IGNORECASE | re.DOTALL)
_FIX_RE = re.compile(r"Fix instructions:\s*(.*)\Z", re.IGNORECASE | re.DOTALL)


def parse_verdict(text: str) -> Verdict:
    text = text or ""
    matches = list(_VERDICT_RE.finditer(text))
    if not matches:
        # No parseable verdict — fail closed (ambiguity -> not-met), keep raw for audit.
        return Verdict(verdict="FAIL", fix_instructions="checker produced no parseable verdict", raw=text)

    verdict = matches[-1].group(1).upper()
    # Restrict criterion/defect parsing to the region from the final verdict onward.
    tail = text[matches[-1].start():]

    criteria: list[CriterionResult] = []
    seen: set[int] = set()
    for m in _CRIT_RE.finditer(tail):
        idx = int(m.group(1))
        if idx in seen:
            continue
        seen.add(idx)
        ok = m.group(2).upper() == "OK"
        note = (m.group(3) or "").strip()
        criteria.append(CriterionResult(index=idx, ok=ok, note=note))
    criteria.sort(key=lambda c: c.index)

    defects: list[str] = []
    dm = _DEFECTS_RE.search(tail)
    if dm:
        body = dm.group(1).strip()
        if body and body.lower() not in {"none", "none.", "なし", "(none)"}:
            for line in body.splitlines():
                line = line.strip().lstrip("-•* ").strip()
                if line:
                    defects.append(line)

    fix = ""
    fm = _FIX_RE.search(tail)
    if fm:
        fix = fm.group(1).strip()

    return Verdict(
        verdict=verdict,
        criteria=criteria,
        defects_outside=defects,
        fix_instructions=fix,
        raw=text,
    )
