#!/usr/bin/env python3
"""Focused no-model tests for the visible local Ollama advisory lane."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(REPO))

from MAP_System.scripts import local_assistant_health as health  # noqa: E402


def test_health_uses_local_host_and_drilled_lane() -> None:
    def fake_run(argv: list[str], *, timeout: float = 5.0):
        if argv[0] == "ollama":
            return health.CommandResult(
                found=True,
                returncode=0,
                stdout="NAME ID SIZE MODIFIED\nqwen3.5:4b abc 3GB now\nqwen3.5:9b def 6GB now\n",
            )
        return health.CommandResult(found=True, returncode=0, stdout="aider test")

    with mock.patch.object(health, "run_command", side_effect=fake_run):
        report = health.build_report(1)
    assert report["status"] == "ok"
    assert report["ollama"]["host"] == "127.0.0.1:11434"
    assert report["approved_draft_models"] == ["qwen3.5:4b"]
    assert report["advisory_lane"]["visibility"] == "operator-visible terminal only"


def test_health_reports_no_lane_when_drilled_model_is_absent() -> None:
    def fake_run(argv: list[str], *, timeout: float = 5.0):
        if argv[0] == "ollama":
            return health.CommandResult(found=True, returncode=0, stdout="NAME ID SIZE MODIFIED\nqwen3.5:9b def 6GB now\n")
        return health.CommandResult(found=True, returncode=0, stdout="aider test")

    with mock.patch.object(health, "run_command", side_effect=fake_run):
        report = health.build_report(1)
    assert report["status"] == "attention"
    assert report["missing_models"] == ["qwen3.5:4b"]
    assert report["advisory_lane"]["status"] == "unavailable"


def test_visible_launcher_and_ui_are_local_only() -> None:
    # TASK-294: four assertions below were inverted by two later, legitimate
    # changes and were never updated, so this test started failing against
    # correct code rather than catching a regression (found by
    # lili-replacement-nisa's 2026-07-28 health baseline; TASK-265's reviewer
    # missed it because it re-ran only the `test_command_center_*`-prefixed
    # suite and this file predates and does not match that naming prefix).
    #
    # - OLLAMA_URL: DEC-029 (2026-07-23) consolidated the loopback endpoint
    #   into one `OLLAMA_HOST_PORT`-derived constant. That exact-literal
    #   assertion below no longer matched by construction, not because the
    #   security property (loopback, non-env-overridable) changed.
    # - ollama-goose / pi-lab-new: DEC-030 (2026-07-23) made the live copy
    #   authoritative for feature content with merge direction live to
    #   template; TASK-265 (RELEASED, independently reviewed and APPROVED)
    #   executed exactly that merge, which is what brought these two
    #   already-live BASE_LOCAL_AGENT_DEFS launcher entries into the
    #   template copy this test reads. They are visible, operator-triggered
    #   terminal launchers (parallel to the pre-existing `claude-lab-new`/
    #   `codex-lab-new` entries in the same dict), not a hidden model
    #   invocation path, and do not touch `VISIBLE_OLLAMA_MODELS` (still
    #   qwen3.5:4b-only, asserted below) or the Ollama advisory-lane gate
    #   this test module exists to protect. Do not re-invert these to
    #   "not in server_text": that would silently fail a future, actually-
    #   unauthorized regression back into passing.
    # - SUMMARY_MODEL / "if SUMMARY_MODEL is not None": TASK-312 (2026-07-30,
    #   fresh WS-3 baseline run) found these two assertions stale again --
    #   server.py grew a SUMMARY_PROVIDER concept (off/ollama/antigravity,
    #   configurable via COMMAND_CENTER_UI_SUMMARY_PROVIDER or
    #   runtime/ui-settings.json, not just a bare SUMMARY_MODEL env var) after
    #   TASK-294 was originally written, so `if SUMMARY_MODEL is not None:`
    #   no longer exists as a gate anywhere in server.py. The security
    #   properties are therefore asserted below from the imported module's
    #   computed values, not from another exact source spelling:
    #   summarization defaults OFF and the egress endpoint stays loopback.
    launcher = ROOT / "templates" / "install" / "bin" / "ai-command-center-ollama-model"
    server = ROOT / "templates" / "install" / "command-center-ui" / "app" / "server.py"
    installer = REPO / "install-map-system.sh"
    text = launcher.read_text(encoding="utf-8")
    server_text = server.read_text(encoding="utf-8")
    assert "qwen3.5:4b" in text
    assert "OLLAMA_HOST=127.0.0.1:11434" in text
    assert "wezterm" in text
    assert "VISIBLE_OLLAMA_MODELS" in server_text
    assert '"qwen3.5:4b"' in server_text
    assert "ollama-goose" in server_text
    assert '"pi-lab-new"' in server_text

    spec = importlib.util.spec_from_file_location("task294_behavior_server", server)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(
        os.environ,
        {"COMMAND_CENTER_UI_WORKSPACE": str(REPO)},
        clear=True,
    ):
        spec.loader.exec_module(module)

    assert module.OLLAMA_HOST_PORT == "127.0.0.1:11434"
    assert module.OLLAMA_URL == "http://127.0.0.1:11434"
    assert module.SUMMARY_PROVIDER == "off"
    assert module.SUMMARY_MODEL is None
    assert module.SUMMARIZER.status()["enabled"] is False
    assert "ai-command-center-ollama-model" in installer.read_text(encoding="utf-8")


def test_ui_discovery_forces_loopback_despite_ambient_host() -> None:
    server_path = ROOT / "templates" / "install" / "command-center-ui" / "app" / "server.py"
    spec = importlib.util.spec_from_file_location("task228_server", server_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    observed: dict[str, object] = {}

    def fake_run(*args: object, **kwargs: object) -> SimpleNamespace:
        observed["argv"] = args[0]
        observed["env"] = kwargs.get("env")
        return SimpleNamespace(
            returncode=0,
            stdout=(
                "NAME ID SIZE MODIFIED\n"
                "qwen3.5:4b abc 3 GB now\n"
                "qwen3.5:9b def 6 GB now\n"
            ),
        )

    with mock.patch.dict(
        os.environ,
        {"COMMAND_CENTER_UI_WORKSPACE": str(REPO), "OLLAMA_HOST": "http://remote.invalid:11434"},
        clear=False,
    ), mock.patch("subprocess.run", side_effect=fake_run):
        spec.loader.exec_module(module)
        definitions = module.local_agent_defs()

    assert observed["argv"] == ["ollama", "list"]
    assert isinstance(observed["env"], dict)
    assert observed["env"]["OLLAMA_HOST"] == "127.0.0.1:11434"
    assert "ollama-model-qwen3-5-4b" in definitions
    assert all("qwen3-5-9b" not in key for key in definitions)


def test_launcher_is_shell_valid_without_running_a_model() -> None:
    launcher = ROOT / "templates" / "install" / "bin" / "ai-command-center-ollama-model"
    result = subprocess.run(["sh", "-n", str(launcher)], check=False)
    assert result.returncode == 0


def main() -> int:
    for test in [
        test_health_uses_local_host_and_drilled_lane,
        test_health_reports_no_lane_when_drilled_model_is_absent,
        test_visible_launcher_and_ui_are_local_only,
        test_ui_discovery_forces_loopback_despite_ambient_host,
        test_launcher_is_shell_valid_without_running_a_model,
    ]:
        test()
        print(f"PASS {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
