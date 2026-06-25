"""OpenAIChecker — prod backend (now wired).

The scalability fix: a server-side OpenAI key means paying customers get an
independent checker WITHOUT the operator's personal codex quota. The client is
injectable so the implementation is unit-tested deterministically (no live key,
no network); the live path lazily constructs `openai.OpenAI`.
"""
from __future__ import annotations

import os

from .base import Verdict
from .parse import parse_verdict
from .prompt import build_prompt


class OpenAIChecker:
    name = "openai"
    lineage = "openai/gpt"

    def __init__(self, *, model: str = "gpt-4o", api_key: str | None = None, client=None, timeout: int = 120):
        self.model = model
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self._client = client                 # inject for tests / custom transport
        self.timeout = timeout

    def available(self) -> bool:
        return self._client is not None or bool(self.api_key)

    def _get_client(self):
        if self._client is not None:
            return self._client
        if not self.api_key:
            raise RuntimeError("OpenAIChecker requires a server-side OPENAI_API_KEY")
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError("openai package not installed (pip install openai)") from e
        self._client = OpenAI(api_key=self.api_key)
        return self._client

    def verify(self, criteria: str, artifact: str) -> Verdict:
        prompt = build_prompt(criteria, artifact)
        try:
            client = self._get_client()
            resp = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            text = resp.choices[0].message.content or ""
        except Exception as e:  # noqa: BLE001 — any backend failure becomes a FAIL verdict, never crash the server
            return Verdict(
                verdict="FAIL",
                fix_instructions=f"openai backend error: {e}",
                checker=self.name,
                lineage=self.lineage,
            )
        v = parse_verdict(text)
        v.checker = self.name
        v.lineage = self.lineage
        return v
