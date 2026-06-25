"""OpenAIChecker — prod seam (declared, not wired in v0).

The production path: a server-side OpenAI key, metered, so paying customers get an
independent checker without the operator's personal codex quota. v0 deliberately
leaves this as a clear NotImplementedError seam — codex proves the edge first.
"""
from __future__ import annotations

import os

from .base import Verdict


class OpenAIChecker:
    name = "openai"
    lineage = "openai/gpt"

    def __init__(self, *, model: str = "gpt-4o", api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def available(self) -> bool:
        return bool(self.api_key)

    def verify(self, criteria: str, artifact: str) -> Verdict:
        raise NotImplementedError(
            "OpenAIChecker is the prod seam and is not wired in v0. "
            "Set a server-side OPENAI_API_KEY and implement the chat call against "
            "prompts/checker.md before enabling this backend."
        )
