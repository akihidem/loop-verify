"""GeminiChecker — backend for running on your own Google API key.

A different lineage again (google/gemini) — useful when you want an independent
checker from neither Claude nor OpenAI. The client is injectable so the
implementation is unit-tested deterministically (no live key, no network); the
live path lazily constructs `google.genai.Client`. Mirrors openai.py.
"""
from __future__ import annotations

import os

from .base import Verdict
from .parse import parse_verdict
from .prompt import build_prompt


class GeminiChecker:
    name = "gemini"
    lineage = "google/gemini"

    def __init__(self, *, model: str = "gemini-2.5-pro", api_key: str | None = None, client=None, timeout: int = 120):
        self.model = model
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY")
        self._client = client                 # inject for tests / custom transport
        self.timeout = timeout

    def available(self) -> bool:
        return self._client is not None or bool(self.api_key)

    def _get_client(self):
        if self._client is not None:
            return self._client
        if not self.api_key:
            raise RuntimeError("GeminiChecker requires a server-side GEMINI_API_KEY")
        try:
            from google import genai
        except ImportError as e:
            raise RuntimeError("google-genai package not installed (pip install google-genai)") from e
        # http_options timeout is in milliseconds.
        self._client = genai.Client(api_key=self.api_key, http_options={"timeout": self.timeout * 1000})
        return self._client

    def verify(self, criteria: str, artifact: str) -> Verdict:
        prompt = build_prompt(criteria, artifact)
        try:
            client = self._get_client()
            resp = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={"temperature": 0},
            )
            text = getattr(resp, "text", "") or ""
        except Exception as e:  # noqa: BLE001 — any backend failure becomes a FAIL verdict, never crash the server
            return Verdict(
                verdict="FAIL",
                fix_instructions=f"gemini backend error: {e}",
                checker=self.name,
                lineage=self.lineage,
            )
        v = parse_verdict(text)
        v.checker = self.name
        v.lineage = self.lineage
        return v
