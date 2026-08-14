#!/usr/bin/env python3
"""Focused tests for the Command Center authority-freshness display (TASK-314).

Covers `authority_status_summary()` / GET /api/map/authority's three display
states (fresh, stale, unavailable) without touching the real map-authority
gateway -- `subprocess.run` is mocked, matching the existing pattern in
test_local_ollama_lane.py's test_ui_discovery_forces_loopback_despite_ambient_host.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
SERVER_PATH = ROOT / "templates" / "install" / "command-center-ui" / "app" / "server.py"


def _load_server():
    spec = importlib.util.spec_from_file_location("task314_server", SERVER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(os.environ, {"COMMAND_CENTER_UI_WORKSPACE": str(REPO)}, clear=False):
        spec.loader.exec_module(module)
    return module


def _fake_status_run(payload: dict, *, returncode: int = 0, stderr: str = ""):
    def fake_run(argv, **kwargs):
        return SimpleNamespace(returncode=returncode, stdout=json.dumps(payload), stderr=stderr)

    return fake_run


def test_fresh_state_reports_ok_and_fresh_label() -> None:
    module = _load_server()
    payload = {
        "authority": {
            "mode": "mirror",
            "authority_host": "192.168.1.153",
            "authority_revision": "sha256:deadbeef",
            "last_successful_sync_at": "2026-07-30T23:57:07Z",
            "freshness": "FRESH",
            "last_error": "",
        }
    }
    with mock.patch("subprocess.run", side_effect=_fake_status_run(payload)):
        summary = module.authority_status_summary()
    assert summary["ok"] is True
    assert summary["freshness"] == "FRESH"
    assert summary["freshness_label"] == "fresh"
    assert summary["authority_host"] == "192.168.1.153"
    assert summary["authority_revision"] == "sha256:deadbeef"
    assert summary["last_error"] is None


def test_stale_state_reports_ok_true_but_stale_label() -> None:
    module = _load_server()
    payload = {
        "authority": {
            "mode": "mirror",
            "authority_host": "192.168.1.153",
            "authority_revision": "sha256:deadbeef",
            "last_successful_sync_at": "2026-07-30T20:00:00Z",
            "freshness": "STALE",
            "last_error": "",
        }
    }
    with mock.patch("subprocess.run", side_effect=_fake_status_run(payload)):
        summary = module.authority_status_summary()
    assert summary["ok"] is True
    assert summary["freshness"] == "STALE"
    assert summary["freshness_label"] == "stale"


def test_unavailable_when_gateway_call_fails() -> None:
    module = _load_server()

    def fake_run(argv, **kwargs):
        return SimpleNamespace(returncode=1, stdout="", stderr="authority request failed (1): ")

    with mock.patch("subprocess.run", side_effect=fake_run):
        summary = module.authority_status_summary()
    assert summary["ok"] is False
    assert summary["freshness"] == "UNAVAILABLE"
    assert summary["freshness_label"] == "unavailable"
    assert "error" in summary


def test_unavailable_when_authority_object_missing_freshness() -> None:
    module = _load_server()
    payload = {"authority": {"mode": "mirror"}}
    with mock.patch("subprocess.run", side_effect=_fake_status_run(payload)):
        summary = module.authority_status_summary()
    assert summary["freshness"] == "UNAVAILABLE"
    assert summary["freshness_label"] == "unavailable"


def test_endpoint_is_wired_to_authority_status_summary() -> None:
    server_text = SERVER_PATH.read_text(encoding="utf-8")
    assert '"/api/map/authority"' in server_text
    assert "authority_status_summary()" in server_text


def main() -> int:
    for test in [
        test_fresh_state_reports_ok_and_fresh_label,
        test_stale_state_reports_ok_true_but_stale_label,
        test_unavailable_when_gateway_call_fails,
        test_unavailable_when_authority_object_missing_freshness,
        test_endpoint_is_wired_to_authority_status_summary,
    ]:
        test()
        print(f"PASS {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
