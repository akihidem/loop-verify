import threading

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


def test_try_consume_basic(tmp_path):
    s = Store(tmp_path / "k.json")
    s.add_key("k1", ["A"], monthly_cap=2)
    assert s.try_consume("k1", M) == (True, 1)
    assert s.try_consume("k1", M) == (True, 2)
    assert s.try_consume("k1", M) == (False, 2)              # over cap: no increment
    assert s.usage("k1", M) == 2                              # counter not bumped on denial


def test_try_consume_unlimited_cap(tmp_path):
    s = Store(tmp_path / "k.json")
    s.add_key("k1", ["A"], monthly_cap=None)
    for i in range(1, 6):
        assert s.try_consume("k1", M) == (True, i)


def test_try_consume_unknown_key_fails_closed(tmp_path):
    # An unknown key must NOT be consumable and must NOT mint a record (fail closed).
    s = Store(tmp_path / "k.json")
    assert s.try_consume("ghost", M) == (False, 0)
    assert s.get_key("ghost") is None


def test_try_consume_is_atomic_under_concurrency(tmp_path):
    # Exactly `cap` reservations succeed even when many threads race — the
    # check-then-increment is serialized under the lock, so no overshoot.
    cap = 50
    s = Store(tmp_path / "k.json")
    s.add_key("k1", ["A"], monthly_cap=cap)

    results = []
    rlock = threading.Lock()
    start = threading.Event()

    def worker():
        start.wait()
        ok, _ = s.try_consume("k1", M)
        with rlock:
            results.append(ok)

    threads = [threading.Thread(target=worker) for _ in range(cap * 4)]
    for t in threads:
        t.start()
    start.set()
    for t in threads:
        t.join()

    assert sum(results) == cap                               # never more than cap granted
    assert s.usage("k1", M) == cap                           # counter matches grants exactly
