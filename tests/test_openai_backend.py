import types

from loop_verify.checker.openai import OpenAIChecker


def _fake_client(text: str):
    """A stand-in shaped like openai.OpenAI for deterministic tests (no key, no network)."""
    def create(**kwargs):
        msg = types.SimpleNamespace(content=text)
        return types.SimpleNamespace(choices=[types.SimpleNamespace(message=msg)])

    completions = types.SimpleNamespace(create=create)
    chat = types.SimpleNamespace(completions=completions)
    return types.SimpleNamespace(chat=chat)


def test_openai_parses_fail():
    c = OpenAIChecker(client=_fake_client(
        "Verdict: FAIL\nPer criterion:\n- [1] NG — off by one\nDefects outside the criteria: none\nFix instructions: use n+1\n"
    ))
    v = c.verify("criteria", "code")
    assert not v.passed
    assert v.checker == "openai" and v.lineage == "openai/gpt"
    assert v.criteria[0].index == 1 and not v.criteria[0].ok


def test_openai_parses_pass():
    c = OpenAIChecker(client=_fake_client("Verdict: PASS\nPer criterion:\n- [1] OK\n"))
    assert c.verify("criteria", "code").passed


def test_openai_no_key_is_graceful(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    c = OpenAIChecker()                       # no key, no injected client
    assert c.available() is False
    v = c.verify("criteria", "code")          # must not crash
    assert not v.passed and "OPENAI_API_KEY" in v.fix_instructions
