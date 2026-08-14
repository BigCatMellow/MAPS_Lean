#!/usr/bin/env python3
"""Focused regressions for TASK-302 fixed-roster CCL startup.

These are static content checks against the wezterm config and launcher
scripts -- there is no way to actually drive a GUI wezterm session inside a
test. That is a real limitation (see the delivery note's residual risk),
not something this suite claims to close.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "templates" / "install"
LUA = INSTALL / "wezterm" / "ai-command-center-lab.lua"
CODEX_LAUNCHER = INSTALL / "bin" / "ai-command-center-lab-codex"
CLAUDE_LAUNCHER = INSTALL / "bin" / "ai-command-center-lab-claude"
PI_LAUNCHER = INSTALL / "bin" / "ai-command-center-lab-pi"
LIBRARIAN_LAUNCHER = INSTALL / "bin" / "ai-command-center-lab-librarian"
SHELL_LAUNCHER = INSTALL / "bin" / "ai-command-center-lab-shell"
NEW_AGENT_LAUNCHER = INSTALL / "bin" / "ai-command-center-new-agent"
MONITOR_LAUNCHER = INSTALL / "bin" / "ai-command-center-monitor"
LIFECYCLE_NOTE = ROOT / "notes" / "command-center-orchestrator-lifecycle.md"


def _gui_startup_body(lua_text: str) -> str:
    match = re.search(
        r'wezterm\.on\("gui-startup".*?\n(.*?)\nend\)', lua_text, re.DOTALL
    )
    assert match, "gui-startup handler not found in ai-command-center-lab.lua"
    return match.group(1)


def test_default_topology_starts_operator_surfaces() -> None:
    body = _gui_startup_body(LUA.read_text(encoding="utf-8"))
    assert "ai-command-center-lab-shell" in body
    assert "ai-command-center-lab-codex" in body
    assert "ai-command-center-new-agent" in body
    assert "ai-command-center-monitor" in body


def test_default_topology_starts_fixed_instruction_bearing_agents() -> None:
    body = _gui_startup_body(LUA.read_text(encoding="utf-8"))
    assert "ai-command-center-lab-codex" in body
    assert "ai-command-center-lab-claude" in body
    assert "ai-command-center-lab-pi" in body
    assert "ai-command-center-lab-librarian" in body


def test_default_topology_does_not_start_retired_antigravity() -> None:
    body = _gui_startup_body(LUA.read_text(encoding="utf-8"))
    assert "antigravity" not in body.lower()
    for launcher in (CODEX_LAUNCHER, CLAUDE_LAUNCHER, PI_LAUNCHER, LIBRARIAN_LAUNCHER):
        assert "antigravity" not in launcher.read_text(encoding="utf-8").lower()


def test_gui_startup_uses_mux_window_api_supported_by_installed_wezterm() -> None:
    text = LUA.read_text(encoding="utf-8")
    assert "window:spawn_tab({" in text
    assert "gui_window():set_title" not in text
    assert "tab(window, \"Codex Lab\"" in text


def test_on_demand_launchers_still_exist_and_are_unchanged_scripts() -> None:
    for launcher in (CLAUDE_LAUNCHER, PI_LAUNCHER, LIBRARIAN_LAUNCHER):
        assert launcher.is_file(), f"{launcher} must remain available on demand"
        text = launcher.read_text(encoding="utf-8")
        assert text.startswith("#!/bin/sh"), f"{launcher} must remain a runnable script"


def test_fixed_agent_launchers_confirm_hcom_launch() -> None:
    for launcher in (CODEX_LAUNCHER, CLAUDE_LAUNCHER, PI_LAUNCHER, LIBRARIAN_LAUNCHER):
        text = launcher.read_text(encoding="utf-8")
        assert "--go" in text, f"{launcher} must bypass hcom's preview-only mode"


def test_codex_prompt_no_longer_claims_sole_orchestrator_startup() -> None:
    prompt = CODEX_LAUNCHER.read_text(encoding="utf-8")
    assert "sole core orchestrator at startup" not in prompt
    assert "deciding whether any of them needs to start" not in prompt
    assert "Codex lab agent for the AI Command Center Lab" in prompt
    assert "Read AGENTS.md and MAP_System/AGENTS.md first" in prompt


def test_no_headless_launch_path_anywhere_in_ccl_scripts() -> None:
    guard_phrases = ("never --headless", "never use", "do not use --headless")
    for path in (CODEX_LAUNCHER, CLAUDE_LAUNCHER, PI_LAUNCHER, LIBRARIAN_LAUNCHER):
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        assert "--headless" not in text or any(phrase in lowered for phrase in guard_phrases), (
            f"{path} must not introduce a headless launch path"
        )
    # The orchestrator prompt must positively instruct against headless spawns.
    prompt = CODEX_LAUNCHER.read_text(encoding="utf-8")
    assert "never --headless" in prompt


def test_shell_and_monitor_launchers_unaffected() -> None:
    assert SHELL_LAUNCHER.is_file()
    assert NEW_AGENT_LAUNCHER.is_file()
    assert MONITOR_LAUNCHER.is_file()
    body = _gui_startup_body(LUA.read_text(encoding="utf-8"))
    assert "ai-command-center-lab-shell" in body
    assert "ai-command-center-new-agent" in body
    assert "ai-command-center-monitor" in body


def test_lua_config_is_syntactically_valid() -> None:
    lua_interpreter = None
    for candidate in ("lua5.4", "lua5.3", "lua", "luajit"):
        found = subprocess.run(
            ["sh", "-c", f"command -v {candidate}"], capture_output=True, text=True
        )
        if found.returncode == 0:
            lua_interpreter = candidate
            break
    if lua_interpreter is None:
        # No lua interpreter available in this environment; fall back to a
        # bounded structural check instead of skipping silently.
        text = LUA.read_text(encoding="utf-8")
        assert text.count("wezterm.on(") == text.count("end)")
        return
    result = subprocess.run(
        [lua_interpreter, "-e", f'assert(loadfile("{LUA}"))'],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr


def test_codex_launcher_shell_syntax_is_valid() -> None:
    for launcher in (CODEX_LAUNCHER, NEW_AGENT_LAUNCHER):
        result = subprocess.run(["sh", "-n", str(launcher)], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr


def test_new_agent_launcher_is_plain_language_and_visible() -> None:
    text = NEW_AGENT_LAUNCHER.read_text(encoding="utf-8")
    assert "What should the new agent do?" in text
    assert '"$AI" helper start "$provider"' in text
    assert "--headless" not in text
    lua = LUA.read_text(encoding="utf-8")
    assert 'key = "n"' in lua
    assert 'mods = "CTRL|SHIFT"' in lua


def test_lifecycle_note_documents_migration_rollback_and_residual_risk() -> None:
    text = LIFECYCLE_NOTE.read_text(encoding="utf-8")
    for heading in ("## Migration", "## Rollback", "## Residual risk", "## Orchestrator routing vs. autonomous authority"):
        assert heading in text, f"lifecycle note missing required section: {heading}"


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)} command-center-orchestrator-startup tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
