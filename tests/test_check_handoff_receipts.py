"""Tests for scripts/check_handoff_receipts.py (CLAUDE.md rule 20 mechanical
safeguard: every work/handoffs/ file must be registered, and every non-legacy
registered handoff must carry its required receipt block)."""

import importlib.util
import pathlib
import tempfile
import unittest

_MODULE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "scripts"
    / "check_handoff_receipts.py"
)
_spec = importlib.util.spec_from_file_location("check_handoff_receipts", _MODULE_PATH)
chr_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(chr_mod)  # type: ignore[union-attr]

REGISTER_HEADER = (
    "# Durable handoff register\n\n"
    "## Handoff lifecycle\n\n"
    "| Handoff status | Meaning | Required pointer |\n"
    "| --- | --- | --- |\n"
    "| `OPEN` | Handoff exists but no receiving agent/session has durably "
    "confirmed review. | Handoff path. |\n"
    "| `CLOSED` | Done. | Final result/evidence pointer. |\n\n"
    "## Register\n\n"
    "Keep newest/recently changed handoffs first.\n\n"
    "| Handoff ID | Handoff status | Handoff | Reviewed | Continued at |\n"
    "| --- | --- | --- | --- | --- |\n"
)


def _handoffs_tree(root: pathlib.Path, register_rows: str,
                    files: dict[str, str]) -> pathlib.Path:
    hd = root / "work" / "handoffs"
    hd.mkdir(parents=True, exist_ok=True)
    (hd / "README.md").write_text(REGISTER_HEADER + register_rows, encoding="utf-8")
    for rel, body in files.items():
        (hd / rel).write_text(body, encoding="utf-8")
    return hd


class CheckHandoffReceiptsTests(unittest.TestCase):
    def _scan(self, register_rows: str, files: dict[str, str]) -> list[str]:
        with tempfile.TemporaryDirectory() as td:
            hd = _handoffs_tree(pathlib.Path(td), register_rows, files)
            return chr_mod.scan(handoffs_dir=hd)

    def test_clean_legacy_row_without_receipt_passes(self):
        failures = self._scan(
            "| `LEGACY-MAPS-20260101` | `CONTINUED` | "
            "[`2026-01-01-old.md`](2026-01-01-old.md) | 2026-09-13 by nepo | "
            "next file |\n",
            {"2026-01-01-old.md": "# Old handoff\n\nNo receipt here.\n"},
        )
        self.assertEqual(failures, [])

    def test_clean_new_row_with_receipt_passes(self):
        failures = self._scan(
            "| `MAPS-HO-20260913-thing` | `OPEN` | "
            "[`thing-handoff.md`](thing-handoff.md) | NOT YET | NOT YET |\n",
            {"thing-handoff.md": (
                "# Handoff: thing\n\n"
                "Handoff ID: MAPS-HO-20260913-thing\n"
                "Handoff status: OPEN\n"
                "Reviewed: NOT YET\n"
                "Continued at: NOT YET\n"
            )},
        )
        self.assertEqual(failures, [])

    def test_unregistered_file_fails(self):
        failures = self._scan(
            "",
            {"orphan-handoff.md": "# Orphan\n\nNo one registered this.\n"},
        )
        self.assertEqual(len(failures), 1)
        self.assertIn("orphan-handoff.md", failures[0])
        self.assertIn("not registered", failures[0])

    def test_non_legacy_row_missing_receipt_fails(self):
        failures = self._scan(
            "| `MAPS-HO-20260913-thing` | `OPEN` | "
            "[`thing-handoff.md`](thing-handoff.md) | NOT YET | NOT YET |\n",
            {"thing-handoff.md": "# Handoff: thing\n\nNo receipt block at all.\n"},
        )
        self.assertEqual(len(failures), 1)
        self.assertIn("thing-handoff.md", failures[0])
        self.assertIn("missing the required receipt", failures[0])

    def test_legacy_prefix_row_missing_receipt_is_exempt(self):
        failures = self._scan(
            "| `LEGACY-MAPS-20260101` | `CLOSED` | "
            "[`old.md`](old.md) | 2026-09-13 by nepo | done |\n",
            {"old.md": "# Old handoff\n\nNo receipt, and that's fine.\n"},
        )
        self.assertEqual(failures, [])

    def test_receipt_id_mismatch_fails(self):
        failures = self._scan(
            "| `MAPS-HO-20260913-thing` | `OPEN` | "
            "[`thing-handoff.md`](thing-handoff.md) | NOT YET | NOT YET |\n",
            {"thing-handoff.md": (
                "# Handoff: thing\n\n"
                "Handoff ID: MAPS-HO-20260913-DIFFERENT\n"
                "Handoff status: OPEN\n"
            )},
        )
        self.assertEqual(len(failures), 1)
        self.assertIn("must match", failures[0])

    def test_lifecycle_table_rows_are_not_mistaken_for_register_entries(self):
        # The lifecycle table above '## Register' also has '| `WORD` | ...'
        # shaped rows (e.g. '| `OPEN` | ...'); a file literally named
        # 'OPEN.md' must not be considered "registered" by that table row.
        failures = self._scan(
            "",
            {"OPEN.md": "# Should not be satisfied by the lifecycle table\n"},
        )
        self.assertEqual(len(failures), 1)
        self.assertIn("OPEN.md", failures[0])

    def test_readme_itself_is_never_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            hd = _handoffs_tree(pathlib.Path(td), "", {})
            failures = chr_mod.scan(handoffs_dir=hd)
        self.assertEqual(failures, [])

    def test_missing_register_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            hd = pathlib.Path(td) / "work" / "handoffs"
            hd.mkdir(parents=True)
            failures = chr_mod.scan(handoffs_dir=hd)
        self.assertEqual(len(failures), 1)
        self.assertIn("not found", failures[0])


if __name__ == "__main__":
    unittest.main()
