"""Static contract checks for the CommandCenterUI attention popup."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "templates" / "install" / "command-center-ui" / "src"


class CommandCenterAttentionPopupTests(unittest.TestCase):
    def setUp(self):
        self.html = (UI / "chat.html").read_text(encoding="utf-8")
        self.js = (UI / "chat.js").read_text(encoding="utf-8")
        self.css = (UI / "chat.css").read_text(encoding="utf-8")

    def test_popup_has_explicit_operator_actions(self):
        for element_id in (
            "attention-popup",
            "attention-popup-reply",
            "attention-popup-open",
            "attention-popup-snooze",
            "attention-popup-dismiss",
        ):
            self.assertIn(f'id="{element_id}"', self.html)
        self.assertIn('role="dialog"', self.html)

    def test_popup_queues_all_existing_attention_types(self):
        self.assertIn('popupItem("request"', self.js)
        self.assertIn('popupItem("gate"', self.js)
        self.assertIn('popupItem("prompt"', self.js)
        self.assertIn("const visible = popupQueue.filter", self.js)
        self.assertIn("ATTENTION_POPUP_SNOOZE_MS", self.js)

    def test_popup_never_approves_or_sends_automatically(self):
        popup_script = self.js.split("function renderAttentionPopup()", 1)[1].split("function gateItem", 1)[0]
        self.assertNotIn("/api/gate/decide", popup_script)
        self.assertNotIn("/api/chat/send", popup_script)
        self.assertIn("jumpToAttentionMessage(item, true)", popup_script)

    def test_popup_is_visually_distinct(self):
        self.assertIn(".attention-popup {", self.css)
        self.assertIn("position: fixed", self.css)
        self.assertIn("z-index: 30", self.css)


if __name__ == "__main__":
    unittest.main()
