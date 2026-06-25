from demo.run_demo import main


def test_demo_runs_green_with_mock_backend(capsys):
    # The demo doubles as a smoke test: mechanism invariants must hold offline.
    rc = main(["--backend", "mock"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Provision a metered API key" in out
    assert "Monthly-cap enforcement" in out
    assert "THE EDGE" in out
    assert "mechanism invariants" in out and "PASS" in out


def test_demo_uses_throwaway_store(tmp_path, monkeypatch):
    # The demo must NEVER touch the real key store — it builds its own temp store.
    monkeypatch.setenv("LOOP_VERIFY_STORE", str(tmp_path / "real-keys.json"))
    assert main(["--backend", "mock"]) == 0
    assert not (tmp_path / "real-keys.json").exists()
