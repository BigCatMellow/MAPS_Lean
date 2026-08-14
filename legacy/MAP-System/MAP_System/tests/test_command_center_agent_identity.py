"""Regression checks for Command Center agent identity presentation."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "MAP_System/templates/install/command-center-ui/src"
LIVE = ROOT.parents[1] / "CommandCenterUI/src"


class AgentIdentityTests(unittest.TestCase):
    def test_agent_type_labels_and_pastel_styles_exist(self):
        js = (TEMPLATE / "chat.js").read_text(encoding="utf-8")
        css = (TEMPLATE / "chat.css").read_text(encoding="utf-8")
        self.assertIn("function agentIdentity", js)
        for label in ("Codex", "Claude", "Gemini", "Pi", "Operator"):
            self.assertIn(label, js)
        for agent_type in ("codex", "claude", "gemini", "pi", "operator"):
            self.assertIn(f".agent-type-{agent_type}", css)

    def test_chat_and_presence_use_identity_display(self):
        js = (TEMPLATE / "chat.js").read_text(encoding="utf-8")
        self.assertIn("identity.display", js)
        self.assertIn("agent-identity", js)
        self.assertIn("agent-type-${identity.type}", js)

    @unittest.skip(
        "chat.js/chat.css were retired live-side 2026-07-29 in favor of "
        "orchestrator.html/js/css (see MAP_System/templates/install/"
        "command-center-ui/README.md and TASK-306's evidence record). The "
        "template's chat.js/css are preserved as historical legacy content, "
        "not part of the live bundle, so this comparison no longer applies. "
        "See MAP_System/scripts/command_center_version.py for the current "
        "live/template parity check."
    )
    def test_live_files_match_installer_template(self):
        for filename in ("chat.js", "chat.css"):
            self.assertEqual(
                (TEMPLATE / filename).read_text(encoding="utf-8"),
                (LIVE / filename).read_text(encoding="utf-8"),
                filename,
            )


if __name__ == "__main__":
    unittest.main()
