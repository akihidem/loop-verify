"""Render the adversarial checker prompt. The template is model-agnostic so every
backend (codex / OpenAI / Gemini) is held to the same verdict contract.
"""
from __future__ import annotations

from pathlib import Path

_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "prompts" / "checker.md"


def build_prompt(criteria: str, artifact: str, *, max_artifact_chars: int = 24000) -> str:
    template = _TEMPLATE_PATH.read_text(encoding="utf-8")
    art = artifact or ""
    if len(art) > max_artifact_chars:
        art = art[:max_artifact_chars] + "\n...[truncated for length]..."
    # str.format would choke on braces in the artifact; do explicit replacement.
    return template.replace("{criteria}", (criteria or "").strip()).replace("{artifact}", art.strip())
