import pytest

from loop_verify.admin import main
from loop_verify.metering.store import Store

M = "2026-06"


def _args(tmp_path, *rest):
    return ["--store", str(tmp_path / "k.json"), *rest]


def test_add_key_then_persisted(tmp_path):
    rc = main(_args(tmp_path, "add-key", "k1", "--modes", "A,B", "--cap", "300"))
    assert rc == 0
    rec = Store(tmp_path / "k.json").get_key("k1")           # reloaded from disk
    assert rec["entitlements"] == ["A", "B"] and rec["monthly_cap"] == 300


def test_add_key_unlimited_when_cap_omitted(tmp_path):
    main(_args(tmp_path, "add-key", "k1", "--modes", "A"))
    assert Store(tmp_path / "k.json").get_key("k1")["monthly_cap"] is None


def test_add_key_refuses_overwrite_without_force(tmp_path):
    main(_args(tmp_path, "add-key", "k1", "--modes", "A", "--cap", "5"))
    with pytest.raises(SystemExit):
        main(_args(tmp_path, "add-key", "k1", "--modes", "A,B"))


def test_force_update_preserves_usage(tmp_path):
    # Re-provisioning must NOT silently reset quota or wipe the audit trail.
    main(_args(tmp_path, "add-key", "k1", "--modes", "A", "--cap", "5"))
    Store(tmp_path / "k.json").record_usage("k1", M, 3)
    rc = main(_args(tmp_path, "add-key", "k1", "--modes", "A,B", "--cap", "10", "--force"))
    assert rc == 0
    rec = Store(tmp_path / "k.json").get_key("k1")
    assert rec["entitlements"] == ["A", "B"] and rec["monthly_cap"] == 10
    assert rec["usage"].get(M) == 3                          # usage preserved across update


def test_add_key_rejects_unknown_mode(tmp_path):
    with pytest.raises(SystemExit):
        main(_args(tmp_path, "add-key", "k1", "--modes", "Z"))


def test_list_reports_usage(tmp_path, capsys):
    s = Store(tmp_path / "k.json")
    s.add_key("k1", ["A"], monthly_cap=5)
    s.record_usage("k1", M, 2)
    rc = main(_args(tmp_path, "list", "--month", M))
    assert rc == 0
    out = capsys.readouterr().out
    assert "k1" in out and '"usage_this_month": 2' in out


def test_show_missing_key_returns_nonzero(tmp_path):
    assert main(_args(tmp_path, "show", "ghost")) == 1
