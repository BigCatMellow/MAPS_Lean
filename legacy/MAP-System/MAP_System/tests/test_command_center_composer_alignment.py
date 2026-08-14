"""Regression checks for Command Center composer control alignment."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "MAP_System/templates/install/command-center-ui/src"
LIVE = ROOT.parents[1] / "CommandCenterUI/src"


class ComposerAlignmentTests(unittest.TestCase):
    def test_input_and_send_align_with_message_type_dropdown(self):
        css = (TEMPLATE / "chat.css").read_text(encoding="utf-8")
        self.assertIn("align-items: flex-start", css)
        self.assertIn(".composer > textarea,\n.composer > #send", css)

    @unittest.skip(
        "chat.css was retired live-side 2026-07-29 in favor of orchestrator.css "
        "(see command-center-ui/README.md and TASK-306's evidence record). "
        "The template's chat.css is preserved as historical legacy content, "
        "not part of the live bundle. See "
        "MAP_System/scripts/command_center_version.py for the current "
        "live/template parity check."
    )
    def test_live_styles_match_installer_template(self):
        self.assertEqual(
            (TEMPLATE / "chat.css").read_text(encoding="utf-8"),
            (LIVE / "chat.css").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
