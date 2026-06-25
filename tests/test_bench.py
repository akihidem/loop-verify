from bench.edge_bench import load_fixtures, run_bench
from loop_verify.checker import MockChecker
from loop_verify.checker.base import CriterionResult, Verdict


def test_fixtures_have_both_truth_values():
    fx = load_fixtures()
    assert any(f["has_defect"] for f in fx)
    assert any(not f["has_defect"] for f in fx)


def test_bench_machinery_with_perfect_checker():
    fx = load_fixtures()
    truth = {f["artifact"]: f["has_defect"] for f in fx}

    class Scripted:
        name = "scripted"
        lineage = "oracle"

        def verify(self, criteria, artifact):
            defective = truth.get(artifact, False)
            return Verdict(
                verdict="FAIL" if defective else "PASS",
                criteria=[CriterionResult(1, not defective)],
            )

    rep = run_bench(fx, Scripted())
    assert rep["verdict"] == "GO"
    assert rep["recall"] == 1.0 and rep["false_positive"] == 0.0
    assert rep["n"] == len(fx)


def test_bench_machinery_runs_with_mock():
    # Marker-blind mock on marker-free fixtures: machinery must still produce a valid report.
    rep = run_bench(load_fixtures(), MockChecker())
    assert rep["verdict"] in ("GO", "NO-GO")
    assert 0.0 <= rep["recall"] <= 1.0 and 0.0 <= rep["false_positive"] <= 1.0
