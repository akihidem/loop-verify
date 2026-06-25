import types

from loop_verify.checker.gemini import GeminiChecker


def _fake_client(text: str, *, captured: dict | None = None):
    """A stand-in shaped like google.genai.Client for deterministic tests (no key, no network)."""
    def generate_content(**kwargs):
        if captured is not None:
            captured.update(kwargs)
        return types.SimpleNamespace(text=text)

    models = types.SimpleNamespace(generate_content=generate_content)
    return types.SimpleNamespace(models=models)


def test_gemini_parses_fail():
    c = GeminiChecker(client=_fake_client(
        "Verdict: FAIL\nPer criterion:\n- [1] NG — off by one\nDefects outside the criteria: none\nFix instructions: use n+1\n"
    ))
    v = c.verify("criteria", "code")
    assert not v.passed
    assert v.checker == "gemini" and v.lineage == "google/gemini"
    assert v.criteria[0].index == 1 and not v.criteria[0].ok


def test_gemini_parses_pass():
    c = GeminiChecker(client=_fake_client("Verdict: PASS\nPer criterion:\n- [1] OK\n"))
    assert c.verify("criteria", "code").passed


def test_gemini_sends_temperature_zero():
    captured = {}
    c = GeminiChecker(client=_fake_client("Verdict: PASS\nPer criterion:\n- [1] OK\n", captured=captured))
    c.verify("criteria", "code")
    assert captured["config"]["temperature"] == 0
    assert captured["model"] == "gemini-2.5-pro"


def test_gemini_no_key_is_graceful(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    c = GeminiChecker()                        # no key, no injected client
    assert c.available() is False
    v = c.verify("criteria", "code")           # must not crash
    assert not v.passed and "GEMINI_API_KEY" in v.fix_instructions
