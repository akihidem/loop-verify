from loop_verify.checker import MockChecker
from loop_verify.metering.store import Store
from loop_verify.service import run_independent_verify, run_stub_mode

M = "2026-06"


def _store(tmp_path, **keys):
    s = Store(tmp_path / "k.json")
    for k, (ents, cap) in keys.items():
        s.add_key(k, ents, monthly_cap=cap)
    return s


def test_verify_denied_unknown_key(tmp_path):
    s = Store(tmp_path / "k.json")
    out = run_independent_verify("c", "code", "nope", store=s, checker=MockChecker(), month=M)
    assert out["allowed"] is False and "unknown" in out["reason"]


def test_verify_allowed_and_metered(tmp_path):
    s = _store(tmp_path, k1=(["A"], 5))
    out = run_independent_verify("c", "def f():\n    return 1\n", "k1", store=s, checker=MockChecker(), month=M)
    assert out["allowed"] and out["passed"] and out["usage_this_month"] == 1
    assert out["mode"] == "A" and out["lineage"] == "mock/deterministic"


def test_verify_cap_enforced(tmp_path):
    s = _store(tmp_path, k1=(["A"], 1))
    run_independent_verify("c", "x\n", "k1", store=s, checker=MockChecker(), month=M)
    out = run_independent_verify("c", "x\n", "k1", store=s, checker=MockChecker(), month=M)
    assert out["allowed"] is False and "cap" in out["reason"]


def test_verify_fail_passthrough(tmp_path):
    s = _store(tmp_path, k1=(["A"], None))
    out = run_independent_verify("c", "y = 1  # BUG\n", "k1", store=s, checker=MockChecker(), month=M)
    assert out["allowed"] and out["passed"] is False and out["defects_outside"]


class _RaisingChecker:
    name = "boom"
    lineage = "test/raises"

    def verify(self, criteria, artifact):
        raise RuntimeError("kaboom")


def test_verify_checker_raise_becomes_fail_verdict(tmp_path):
    # A custom checker that raises must not crash the server: it becomes a FAIL
    # verdict (mirroring the backends), and the attempt is still metered uniformly.
    s = _store(tmp_path, k1=(["A"], 5))
    out = run_independent_verify("c", "code", "k1", store=s, checker=_RaisingChecker(), month=M)
    assert out["allowed"] and out["passed"] is False
    assert "kaboom" in out["fix_instructions"]
    assert out["usage_this_month"] == 1                       # attempt consumed, uniform


def test_stub_mode_entitlement(tmp_path):
    s = _store(tmp_path, k1=(["B"], None))
    out = run_stub_mode("B", "k1", store=s, month=M)
    assert out["allowed"] and out["status"] == "not_yet_available"
    assert run_stub_mode("C", "k1", store=s, month=M)["allowed"] is False  # not entitled to C
