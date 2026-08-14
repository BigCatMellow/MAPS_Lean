"""Regression checks for human-readable Command Center message intent controls."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "MAP_System/templates/install/command-center-ui/src"
LIVE = ROOT.parents[1] / "CommandCenterUI/src"


class MessageIntentCopyTests(unittest.TestCase):
    def test_plain_language_options_preserve_protocol_values(self):
        html = (TEMPLATE / "chat.html").read_text(encoding="utf-8")
        self.assertIn('value="inform">Update', html)
        self.assertIn('value="request">Needs reply', html)
        self.assertIn('value="ack">Acknowledge', html)

    def test_contextual_help_explains_each_choice(self):
        js = (TEMPLATE / "chat.js").read_text(encoding="utf-8")
        self.assertIn("message-intent-help", js)
        self.assertIn("No reply expected", js)
        self.assertIn("Reply expected", js)
        self.assertIn("Replying to a request", js)

    def test_popup_options_are_rendered_as_bullets(self):
        js = (TEMPLATE / "chat.js").read_text(encoding="utf-8")
        self.assertIn('Options:\\n${items.map((item) => `• ${item}`).join("\\n")}', js)
        self.assertIn("split(/\\n|;|", js)

    @unittest.skip(
        "chat.html/js/css were retired live-side 2026-07-29 in favor of "
        "orchestrator.html/js/css (see command-center-ui/README.md and "
        "TASK-306's evidence record). The template's chat.* files are "
        "preserved as historical legacy content, not part of the live "
        "bundle. See MAP_System/scripts/command_center_version.py for the "
        "current live/template parity check."
    )
    def test_live_composer_matches_installer_template(self):
        for filename in ("chat.html", "chat.js", "chat.css"):
            self.assertEqual(
                (TEMPLATE / filename).read_text(encoding="utf-8"),
                (LIVE / filename).read_text(encoding="utf-8"),
                filename,
            )


if __name__ == "__main__":
    unittest.main()
