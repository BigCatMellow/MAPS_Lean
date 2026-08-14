from pathlib import Path
import unittest

from runtime.smoke import run_smoke


class SmokeInstallTests(unittest.TestCase):
    def test_disposable_state_smoke_reaches_done(self):
        result = run_smoke()
        lifecycle = result["sqlite_task_lifecycle"]
        self.assertTrue(lifecycle["ok"])
        self.assertEqual(lifecycle["status"], "DONE")
        self.assertEqual(lifecycle["settings"]["foreign_keys"], 1)
        self.assertEqual(str(lifecycle["settings"]["journal_mode"]).lower(), "wal")

    def test_smoke_has_no_legacy_or_migration_execution_dependency(self):
        source = Path(__file__).parents[1] / "runtime" / "smoke.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("legacy/", text)
        self.assertNotIn("migration/", text)
        self.assertNotIn("MAP_System", text)

    def test_installer_is_preview_first_and_non_system(self):
        source = Path(__file__).parents[1] / "scripts" / "install_maps.sh"
        text = source.read_text(encoding="utf-8")
        self.assertIn("APPLY=0", text)
        self.assertIn("--apply", text)
        self.assertIn("Mode: PREVIEW", text)
        self.assertNotIn("sudo ", text)
        self.assertNotIn("apt install", text)
        self.assertNotIn("wezterm", text.lower())
        self.assertNotIn("legacy/", text)
        self.assertNotIn("migration/", text)

    def test_installer_does_not_embed_credentials(self):
        source = Path(__file__).parents[1] / "scripts" / "install_maps.sh"
        text = source.read_text(encoding="utf-8").lower()
        for secret_assignment in (
            "openai_api_key=",
            "anthropic_api_key=",
            "api_key=",
            "token=",
        ):
            self.assertNotIn(secret_assignment, text)


if __name__ == "__main__":
    unittest.main()
