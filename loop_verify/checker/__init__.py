"""Checker backend selection. Default backend = codex (v0 edge-prover).

A different lineage from Claude is the whole point — see base.Checker.
"""
from __future__ import annotations

import os

from .base import Checker, CriterionResult, Verdict
from .codex import CodexChecker
from .gemini import GeminiChecker
from .mock import MockChecker
from .openai import OpenAIChecker

_BACKENDS = {
    "codex": CodexChecker,
    "openai": OpenAIChecker,
    "gemini": GeminiChecker,
    "mock": MockChecker,
}


def get_checker(name: str | None = None, **kwargs) -> Checker:
    name = (name or os.getenv("LOOP_VERIFY_BACKEND", "codex")).lower()
    if name not in _BACKENDS:
        raise ValueError(f"unknown backend '{name}' (choose from {sorted(_BACKENDS)})")
    return _BACKENDS[name](**kwargs)


__all__ = [
    "Checker", "Verdict", "CriterionResult",
    "CodexChecker", "OpenAIChecker", "GeminiChecker", "MockChecker",
    "get_checker",
]
