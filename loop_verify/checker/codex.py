"""CodexChecker — the default independent backend.

codex runs on the operator's ChatGPT Plus quota, a DIFFERENT model lineage from
Claude — so it catches what a same-family check misses. Great for personal/local
use; to serve many users, use the OpenAI backend with your own API key (openai.py).

Trap (from prior runs): codex hangs forever if stdin is left open. We always pass
stdin=DEVNULL and `exec --skip-git-repo-check`, and run in a temp cwd so codex has
nothing to mutate.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile

from .base import Verdict
from .parse import parse_verdict
from .prompt import build_prompt


class CodexChecker:
    name = "codex"
    lineage = "codex/openai"

    def __init__(self, *, model: str | None = None, timeout: int = 240, codex_bin: str = "codex"):
        self.model = model
        self.timeout = timeout
        self.codex_bin = codex_bin

    def available(self) -> bool:
        return shutil.which(self.codex_bin) is not None

    def verify(self, criteria: str, artifact: str) -> Verdict:
        if not self.available():
            return Verdict(
                verdict="FAIL",
                fix_instructions=f"codex binary '{self.codex_bin}' not found on PATH",
                checker=self.name,
                lineage=self.lineage,
            )
        prompt = build_prompt(criteria, artifact)
        cmd = [self.codex_bin, "exec", "--skip-git-repo-check"]
        if self.model:
            cmd += ["-m", self.model]
        cmd.append(prompt)
        try:
            with tempfile.TemporaryDirectory(prefix="loop-verify-codex-") as workdir:
                proc = subprocess.run(
                    cmd,
                    stdin=subprocess.DEVNULL,        # never leave stdin open -> codex hangs
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=workdir,                     # isolated throwaway dir (codex exec defaults to a read-only sandbox)
                )
        except subprocess.TimeoutExpired:
            return Verdict(
                verdict="FAIL",
                fix_instructions=f"codex checker timed out after {self.timeout}s",
                checker=self.name,
                lineage=self.lineage,
            )
        out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        v = parse_verdict(out)
        v.checker = self.name
        v.lineage = self.lineage
        return v
