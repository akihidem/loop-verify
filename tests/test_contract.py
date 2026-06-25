from loop_verify.checker import MockChecker
from loop_verify.checker.base import CriterionResult, Verdict
from loop_verify.checker.parse import parse_verdict

PASS_OUT = """agent chatter here...
Verdict: PASS
Per criterion:
- [criterion 1] OK
- [criterion 2] OK
Defects outside the criteria: none
Fix instructions:
"""

FAIL_OUT = """Verdict: FAIL
Per criterion:
- [criterion 1] OK
- [criterion 2] NG — off by one, misses n
Defects outside the criteria:
- no input validation
Fix instructions: use range(1, n+1)
"""


def test_parse_pass():
    v = parse_verdict(PASS_OUT)
    assert v.verdict == "PASS" and v.passed
    assert len(v.criteria) == 2 and all(c.ok for c in v.criteria)


def test_parse_fail_with_defects():
    v = parse_verdict(FAIL_OUT)
    assert v.verdict == "FAIL" and not v.passed
    assert v.criteria[1].index == 2 and not v.criteria[1].ok
    assert any("validation" in d for d in v.defects_outside)
    assert "range(1, n+1)" in v.fix_instructions


def test_parse_garbage_fails_closed():
    v = parse_verdict("no verdict at all")
    assert v.verdict == "FAIL" and not v.passed


def test_parse_takes_last_verdict():
    v = parse_verdict("Verdict: PASS\nblah\nVerdict: FAIL\nPer criterion:\n- [1] NG — x\n")
    assert v.verdict == "FAIL"


def test_verdict_to_dict():
    v = Verdict(verdict="PASS", criteria=[CriterionResult(1, True)])
    d = v.to_dict()
    assert d["passed"] is True and d["verdict"] == "PASS"
    assert d["criteria"][0]["index"] == 1


def test_mock_clean_pass():
    assert MockChecker().verify("c", "def f():\n    return 1\n").passed


def test_mock_marker_fail():
    v = MockChecker().verify("c", "x = 1  # BUG here\n")
    assert not v.passed and v.defects_outside
