import importlib


def _reload_server(monkeypatch, **env):
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    import loop_verify.server as srv
    return importlib.reload(srv)


def test_server_registers_only_the_tool_surface(monkeypatch):
    srv = _reload_server(monkeypatch)
    # Constructing the http app must not raise (catches wiring breaks without a network).
    app = srv.mcp.streamable_http_app()
    assert app is not None


def test_server_binds_host_and_port_from_env(monkeypatch):
    srv = _reload_server(monkeypatch, LOOP_VERIFY_HOST="0.0.0.0", LOOP_VERIFY_PORT="9123")
    assert srv.mcp.settings.host == "0.0.0.0"
    assert srv.mcp.settings.port == 9123


def test_bad_port_env_falls_back_not_crashes(monkeypatch):
    # A bad LOOP_VERIFY_PORT must warn and fall back to the default, not crash startup.
    srv = _reload_server(monkeypatch, LOOP_VERIFY_PORT="not-a-number")
    assert srv.mcp.settings.port == 8000


def test_info_lists_backends(monkeypatch):
    srv = _reload_server(monkeypatch)
    out = srv.info()
    assert "codex" in out["backends"] and "gemini" in out["backends"]
    assert out["version"]


def test_localhost_default_is_protected(monkeypatch):
    # Default localhost bind -> FastMCP's DNS-rebinding protection (localhost allowlist).
    monkeypatch.delenv("LOOP_VERIFY_HOST", raising=False)
    srv = _reload_server(monkeypatch)
    sec = srv.mcp.settings.transport_security
    assert sec.enable_dns_rebinding_protection is True
    assert all("localhost" in h or "127.0.0.1" in h or "::1" in h for h in sec.allowed_hosts)


def test_bind_all_interfaces_opens_host_check(monkeypatch):
    # Binding 0.0.0.0 at construction -> FastMCP opens the Host check (operator opted in
    # to exposure). Tighten it with LOOP_VERIFY_ALLOWED_HOSTS if you want an allowlist.
    srv = _reload_server(monkeypatch, LOOP_VERIFY_HOST="0.0.0.0")
    assert srv.mcp.settings.transport_security is None


def test_allowed_hosts_env_opens_specific_host(monkeypatch):
    srv = _reload_server(monkeypatch, LOOP_VERIFY_ALLOWED_HOSTS="myhost:8000, other:9000")
    sec = srv.mcp.settings.transport_security
    assert "myhost:8000" in sec.allowed_hosts and "other:9000" in sec.allowed_hosts
    assert "http://myhost:8000" in sec.allowed_origins and "https://other:9000" in sec.allowed_origins


def test_allowed_hosts_wildcard_disables_protection(monkeypatch):
    srv = _reload_server(monkeypatch, LOOP_VERIFY_ALLOWED_HOSTS="*")
    assert srv.mcp.settings.transport_security.enable_dns_rebinding_protection is False
