"""Static regression checks for AI Command Center Lab WezTerm tab titles."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "MAP_System/templates/install/wezterm/ai-command-center-lab.lua"
LIVE = Path.home() / ".config/wezterm/ai-command-center-lab.lua"


class CommandCenterLabTabTitleTests(unittest.TestCase):
    def test_agent_tabs_use_compact_name_and_agent_type(self):
        lua = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("local function agent_tab_title", lua)
        self.assertIn('"%s-%s"', lua)
        self.assertIn("title_case(name)", lua)
        self.assertIn("tool_labels[tool]", lua)
        self.assertIn('codex = "Codex"', lua)
        self.assertIn('claude = "Claude"', lua)
        self.assertNotIn("model_labels", lua)
        self.assertNotIn("effort_code", lua)

    def test_live_config_matches_installer_template_behavior(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        live = LIVE.read_text(encoding="utf-8")
        start = "local function title_case(value)"
        end = 'wezterm.on("update-right-status"'
        self.assertEqual(
            template[template.index(start):template.index(end)],
            live[live.index(start):live.index(end)],
        )


if __name__ == "__main__":
    unittest.main()
