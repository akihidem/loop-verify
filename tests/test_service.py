from loop_verify.checker import MockChecker
from loop_verify.service import run_independent_verify


def test_verify_clean_passes():
    out = run_independent_verify("c", "def f():\n    return 1\n", checker=MockChecker())
    assert out["passed"] and out["verdict"] == "PASS"
    assert out["lineage"] == "mock/deterministic"


def test_verify_marker_fails_with_defects():
    out = run_independent_verify("c", "y = 1  # BUG\n", checker=MockChecker())
    assert out["passed"] is False and out["defects_outside"]


def test_verify_returns_full_contract():
    out = run_independent_verify("c", "code", checker=MockChecker())
    for k in ("verdict", "passed", "criteria", "defects_outside", "fix_instructions", "checker", "lineage"):
        assert k in out


def test_verify_unknown_backend_fails_closed():
    # A misconfigured backend must fail closed, not raise.
    out = run_independent_verify("c", "code", backend="codxe")
    assert out["passed"] is False and "unknown backend" in out["fix_instructions"]


class _RaisingChecker:
    name = "boom"
    lineage = "test/raises"

    def verify(self, criteria, artifact):
        raise RuntimeError("kaboom")


def test_verify_checker_raise_becomes_fail_verdict():
    # A custom checker that raises must not crash: it becomes a FAIL verdict.
    out = run_independent_verify("c", "code", checker=_RaisingChecker())
    assert out["passed"] is False and "kaboom" in out["fix_instructions"]
    assert out["checker"] == "boom"
