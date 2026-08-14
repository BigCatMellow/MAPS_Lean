"""Regression checks for the collapsible Command Center attention history."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "MAP_System/templates/install/command-center-ui/src"
LIVE = ROOT.parents[1] / "CommandCenterUI/src"


class AttentionHistoryTests(unittest.TestCase):
    def test_attention_history_is_a_default_collapsed_section(self):
        html = (TEMPLATE / "chat.html").read_text(encoding="utf-8")
        self.assertIn('id="attention-section"', html)
        self.assertIn('data-sidebar-section="attention"', html)
        self.assertIn('data-default-collapsed="true"', html)
        self.assertIn("Attention needed", html)
        self.assertNotIn('data-default-collapsed="true" hidden', html)

    def test_popup_open_expands_attention_history(self):
        js = (TEMPLATE / "chat.js").read_text(encoding="utf-8")
        self.assertIn("function openAttentionHistory", js)
        self.assertIn('sidebar:attention:collapsed", "0"', js)
        self.assertIn("else openAttentionHistory();", js)
        self.assertIn("attentionSection.hidden = false;", js)

    @unittest.skip(
        "chat.html/js/css were retired live-side 2026-07-29 in favor of "
        "orchestrator.html/js/css (see command-center-ui/README.md and "
        "TASK-306's evidence record). The template's chat.* files are "
        "preserved as historical legacy content, not part of the live "
        "bundle. See MAP_System/scripts/command_center_version.py for the "
        "current live/template parity check."
    )
    def test_live_files_match_installer_template(self):
        for filename in ("chat.html", "chat.js", "chat.css"):
            self.assertEqual(
                (TEMPLATE / filename).read_text(encoding="utf-8"),
                (LIVE / filename).read_text(encoding="utf-8"),
                filename,
            )


if __name__ == "__main__":
    unittest.main()
