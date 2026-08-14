"""Regression checks for the active Command Center attention inbox."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "MAP_System" / "templates" / "install" / "command-center-ui"
LIVE = ROOT.parents[1] / "CommandCenterUI"


class OrchestratorAttentionTests(unittest.TestCase):
    def test_persistent_inbox_is_reachable_and_source_backed(self):
        html = (BUNDLE / "src/orchestrator.html").read_text(encoding="utf-8")
        js = (BUNDLE / "src/orchestrator.js").read_text(encoding="utf-8")
        for element_id in (
            "attention-btn",
            "attention-panel",
            "attention-list",
            "attention-panel-close",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function currentPopupQueue()", js)
        self.assertIn("function renderAttentionPanel()", js)
        self.assertIn("ignores local dismiss", js)

    def test_attention_reply_is_tied_to_the_original_request(self):
        js = (BUNDLE / "src/orchestrator.js").read_text(encoding="utf-8")
        self.assertIn("function beginAttentionReply(item)", js)
        self.assertIn('intent: state.pendingReply ? "ack" : "inform"', js)
        self.assertIn("reply_to: state.pendingReply?.id", js)

    def test_relayed_names_and_old_remote_blocks_are_supported(self):
        server = (BUNDLE / "app/server.py").read_text(encoding="utf-8")
        self.assertIn('HCOM_NAME_RE = re.compile(r"^[A-Za-z0-9_:-]{1,128}$")', server)
        self.assertIn('MENTION_RE = re.compile(r"(?<![\\w@])@([A-Za-z0-9_:-]{2,128})")', server)
        self.assertIn('age > 3600 and ":" not in name', server)

    def test_plain_language_cards_preserve_verbatim_messages(self):
        html = (BUNDLE / "src/orchestrator.html").read_text(encoding="utf-8")
        js = (BUNDLE / "src/orchestrator.js").read_text(encoding="utf-8")
        css = (BUNDLE / "src/orchestrator.css").read_text(encoding="utf-8")
        self.assertIn('id="simplifier-status"', html)
        self.assertIn("function appendReadableText", js)
        self.assertIn("Show original message", js)
        self.assertIn("raw.textContent = msg.text", js)
        self.assertIn(".readable-message", css)
        self.assertIn(".message-original", css)

    def test_background_model_simplifier_is_disabled(self):
        server = (BUNDLE / "app/server.py").read_text(encoding="utf-8")
        self.assertIn('SUMMARY_PROVIDER = "off"', server)
        self.assertIn("SUMMARY_MODEL = None", server)
        self.assertIn("SUMMARY_FALLBACK_MODEL = None", server)
        worker = server.split("def _worker", 1)[1].split("SUMMARIZER =", 1)[0]
        self.assertIn("return", worker)
        self.assertNotIn('"agy"', worker)
        self.assertNotIn("urllib", worker)
        self.assertNotIn("subprocess", worker)
        self.assertNotIn("/api/generate", worker)

    def test_live_ui_matches_installer_bundle(self):
        for relative in (
            "README.md",
            "app/server.py",
            "src/orchestrator.css",
            "src/orchestrator.html",
            "src/orchestrator.js",
        ):
            self.assertEqual(
                (BUNDLE / relative).read_bytes(),
                (LIVE / relative).read_bytes(),
                relative,
            )


if __name__ == "__main__":
    unittest.main()
