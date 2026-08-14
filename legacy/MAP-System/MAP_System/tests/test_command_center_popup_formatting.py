"""Contract checks for readable structured attention-popup text."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "templates" / "install" / "command-center-ui" / "src"


class CommandCenterPopupFormattingTests(unittest.TestCase):
    def test_popup_formats_structured_request_fields(self):
        js = (UI / "chat.js").read_text(encoding="utf-8")
        self.assertIn("function formatPopupText(text)", js)
        self.assertIn("Issue|Options|Recommendation|Needed", js)
        self.assertIn('"\\n$1:"', js)
        self.assertIn("formatPopupText(item.text).slice(0, 360)", js)

    def test_popup_preserves_newlines_and_wraps_long_text(self):
        css = (UI / "chat.css").read_text(encoding="utf-8")
        self.assertIn(".attention-popup-text", css)
        self.assertIn("white-space: pre-wrap", css)
        self.assertIn("overflow-wrap: anywhere", css)
        self.assertIn("overflow-y: auto", css)


if __name__ == "__main__":
    unittest.main()
