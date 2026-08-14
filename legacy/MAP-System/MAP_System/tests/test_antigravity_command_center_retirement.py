"""Regression checks for TASK-320's Command Center retirement boundary."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
TEMPLATE_BIN = ROOT / "templates" / "install" / "bin"
TEMPLATE_WEZTERM = ROOT / "templates" / "install" / "wezterm" / "ai-command-center-lab.lua"
TEMPLATE_UI = ROOT / "templates" / "install" / "command-center-ui" / "src" / "orchestrator.js"
PLAN = ROOT / "artifacts" / "planning" / "map-2-research-adoption-implementation-program-2026-08-09.md"
CAPABILITIES = ROOT / "shared" / "agent-capability-matrix.md"


class AntigravityCommandCenterRetirementTests(unittest.TestCase):
    def test_active_startup_surfaces_do_not_reference_antigravity(self) -> None:
        paths = [
            TEMPLATE_WEZTERM,
            TEMPLATE_BIN / "ai-command-center-lab-codex",
            TEMPLATE_BIN / "ai-command-center-lab-claude",
            TEMPLATE_BIN / "ai-command-center-lab-pi",
            TEMPLATE_BIN / "ai-command-center-lab-librarian",
        ]
        for path in paths:
            self.assertNotIn("antigravity", path.read_text(encoding="utf-8").lower(), path)

    def test_legacy_command_center_surfaces_cannot_launch_antigravity(self) -> None:
        for name in ("ai-command-center-cli", "ai-command-center-shell", "agent-deck"):
            path = SCRIPTS / name
            self.assertNotIn("antigravity", path.read_text(encoding="utf-8").lower(), path)

        retired = (SCRIPTS / "ai-command-center-antigravity").read_text(encoding="utf-8").lower()
        self.assertIn("retired from the ai command center", retired)
        self.assertNotIn("exec /home/home/.local/bin/ai antigravity", retired)

    def test_command_center_ui_copy_has_no_antigravity_label(self) -> None:
        self.assertNotIn("antigravity", TEMPLATE_UI.read_text(encoding="utf-8").lower())
        live = Path.home() / "Projects" / "CommandCenterUI" / "src" / "orchestrator.js"
        if live.is_file():
            self.assertNotIn("antigravity", live.read_text(encoding="utf-8").lower())

    def test_plan_and_current_capability_routing_do_not_assign_antigravity(self) -> None:
        self.assertNotIn("antigravity", PLAN.read_text(encoding="utf-8").lower())
        capabilities = CAPABILITIES.read_text(encoding="utf-8").lower()
        self.assertIn("antigravity was retired", capabilities)
        self.assertNotIn("| antigravity |", capabilities)

    def test_generic_provider_wrapper_is_preserved_outside_command_center(self) -> None:
        self.assertTrue((SCRIPTS / "antigravity-wrapper").is_file())

    def test_biggie_live_startup_config_excludes_antigravity_when_present(self) -> None:
        live = Path.home() / ".config" / "wezterm" / "ai-command-center-lab.lua"
        if live.is_file():
            self.assertNotIn("antigravity", live.read_text(encoding="utf-8").lower())

        retired_launcher = Path.home() / ".local" / "bin" / "ai-command-center-lab-antigravity"
        if retired_launcher.is_file():
            text = retired_launcher.read_text(encoding="utf-8").lower()
            self.assertIn("retired from the ai command center", text)
            self.assertNotIn("exec \"$hcom\" antigravity", text)


if __name__ == "__main__":
    unittest.main()
