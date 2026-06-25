from loop_verify.modes.registry import MODES, active_modes


def test_modes_present():
    assert set(MODES) == {"A", "B", "C", "D"}
    assert MODES["A"].status == "active"
    assert all(MODES[k].status == "stub" for k in ("B", "C", "D"))
    assert MODES["A"].tool == "independent_verify"


def test_active_modes_only_a():
    assert [m.key for m in active_modes()] == ["A"]
