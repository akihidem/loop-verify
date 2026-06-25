"""GeminiChecker — prod seam (declared, not wired in v0). See openai.py."""
from __future__ import annotations

import os

from .base import Verdict


class GeminiChecker:
    name = "gemini"
    lineage = "google/gemini"

    def __init__(self, *, model: str = "gemini-1.5-pro", api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    def available(self) -> bool:
        return bool(self.api_key)

    def verify(self, criteria: str, artifact: str) -> Verdict:
        raise NotImplementedError(
            "GeminiChecker is the prod seam and is not wired in v0. "
            "Set a server-side GEMINI_API_KEY and implement the call against "
            "prompts/checker.md before enabling this backend."
        )
