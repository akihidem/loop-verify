from loop_verify.metering.gate import check_access
from loop_verify.metering.store import Store

M = "2026-06"


def test_store_roundtrip(tmp_path):
    s = Store(tmp_path / "k.json")
    s.add_key("k1", ["A"], monthly_cap=2)
    assert s.get_key("k1")["entitlements"] == ["A"]
    assert s.record_usage("k1", M) == 1
    assert s.record_usage("k1", M) == 2
    assert s.usage("k1", M) == 2


def test_store_persists(tmp_path):
    p = tmp_path / "k.json"
    Store(p).add_key("k1", ["A"])
    assert Store(p).get_key("k1") is not None  # reloaded from disk


def test_gate_unknown_key(tmp_path):
    s = Store(tmp_path / "k.json")
    assert not check_access(s, "nope", "A", M).allowed


def test_gate_mode_entitlement(tmp_path):
    s = Store(tmp_path / "k.json")
    s.add_key("k1", ["A"])
    assert check_access(s, "k1", "A", M).allowed
    assert not check_access(s, "k1", "B", M).allowed


def test_gate_monthly_cap(tmp_path):
    s = Store(tmp_path / "k.json")
    s.add_key("k1", ["A"], monthly_cap=1)
    assert check_access(s, "k1", "A", M).allowed
    s.record_usage("k1", M)
    assert not check_access(s, "k1", "A", M).allowed          # cap reached this month
    assert check_access(s, "k1", "A", "2026-07").allowed       # next month resets
