from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "emergence_script",
    Path(__file__).resolve().parents[1] / "scripts" / "emergence.py",
)
emergence = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(emergence)


class EmergenceCaptureTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self._orig_root = emergence.ROOT
        emergence.ROOT = Path(self._tmp.name)
        self.addCleanup(self._restore_root)

    def _restore_root(self) -> None:
        emergence.ROOT = self._orig_root

    def test_capture_creates_well_formed_file(self) -> None:
        path = emergence.capture(
            "insight",
            "Notable thing observed",
            "Observed X happening during Y.",
            "session Z, file foo.py",
            "Could reduce friction in W.",
            "Try Q on the next occurrence.",
        )
        self.assertTrue(path.exists())
        self.assertTrue(path.parent.samefile(emergence.ROOT / "work" / "insights"))
        text = path.read_text(encoding="utf-8")
        self.assertIn("Notable thing observed", text)
        self.assertIn("## Observation", text)
        self.assertIn("Observed X happening during Y.", text)
        self.assertIn("## Source / context", text)
        self.assertIn("session Z, file foo.py", text)
        self.assertIn("## Potential value", text)
        self.assertIn("Could reduce friction in W.", text)
        self.assertIn("## Smallest next test", text)
        self.assertIn("Try Q on the next occurrence.", text)
        self.assertIn("INSIGHT-", text)

    def test_capture_id_is_stable_and_well_formed(self) -> None:
        path = emergence.capture(
            "idea", "Title", "obs", "src", "val", "next"
        )
        text = path.read_text(encoding="utf-8")
        first_line = text.splitlines()[0]
        self.assertTrue(first_line.startswith("# IDEA-"))
        record_id = first_line[2:].split(":")[0]
        self.assertRegex(record_id, r"^IDEA-[0-9a-f]{8}$")
        # Re-reading the file should always report the same ID.
        text2 = path.read_text(encoding="utf-8")
        self.assertEqual(text, text2)

    def test_list_reads_records_back(self) -> None:
        emergence.capture("insight", "First", "o", "s", "v", "n")
        emergence.capture("idea", "Second", "o", "s", "v", "n")
        records = emergence.list_records()
        self.assertEqual(len(records), 2)
        kinds = {r["kind"] for r in records}
        self.assertEqual(kinds, {"insight", "idea"})
        titles = {r["title"] for r in records}
        self.assertEqual(titles, {"First", "Second"})

        insight_only = emergence.list_records("insight")
        self.assertEqual(len(insight_only), 1)
        self.assertEqual(insight_only[0]["title"], "First")

    def test_two_captures_never_collide_on_id(self) -> None:
        ids = set()
        for i in range(50):
            path = emergence.capture(
                "experiment", f"Test {i}", "o", "s", "v", "n"
            )
            text = path.read_text(encoding="utf-8")
            record_id = text.splitlines()[0][2:].split(":")[0]
            self.assertNotIn(record_id, ids)
            ids.add(record_id)

    def test_capture_rejects_unknown_kind(self) -> None:
        with self.assertRaises(ValueError):
            emergence.capture(
                "synthesis", "Title", "o", "s", "v", "n"
            )


if __name__ == "__main__":
    unittest.main()
