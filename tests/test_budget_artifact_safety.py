from pathlib import Path
import tempfile
import unittest

from runtime.integrity import write_budget_escalation


class BudgetArtifactSafetyTests(unittest.TestCase):
    def test_untrusted_ids_cannot_escape_escalation_directory(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "escalations"
            path = write_budget_escalation(
                {
                    "ok": False,
                    "reason": "budget_exhausted",
                    "task_id": "../../outside/task",
                    "run_id": "../run",
                    "exceeded": [{"metric": "max_attempts", "limit": 1, "actual": 1}],
                },
                out_dir=out,
            )
            self.assertEqual(path.parent.resolve(), out.resolve())
            self.assertTrue(path.is_file())
            self.assertFalse((root / "outside").exists())


if __name__ == "__main__":
    unittest.main()
