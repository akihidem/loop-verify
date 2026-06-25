from demo.run_demo import main


def test_demo_runs_green_with_mock_backend(capsys):
    # The demo doubles as a smoke test: invariants must hold offline.
    rc = main(["--backend", "mock"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "the validator contract" in out
    assert "THE EDGE" in out
    assert "invariants" in out and "PASS" in out
