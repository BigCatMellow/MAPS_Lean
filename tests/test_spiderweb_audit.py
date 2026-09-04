import importlib.util
import io
import json
import pathlib
from contextlib import redirect_stdout
from datetime import date
import sys
import tempfile
import unittest

_MODULE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent / "scripts" / "check_spiderweb.py"
)
_spec = importlib.util.spec_from_file_location("check_spiderweb", _MODULE_PATH)
spiderweb = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
sys.modules[_spec.name] = spiderweb
_spec.loader.exec_module(spiderweb)


class SpiderwebAuditTests(unittest.TestCase):
    def _write(self, root: pathlib.Path, rel: str, text: str) -> pathlib.Path:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_active_links_build_bidirectional_graph(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(root, "AGENTS.md", "# Agents\n\n[Task](work/tasks/TASK-1.md)\n")
            self._write(
                root,
                "work/tasks/TASK-1.md",
                "# TASK-1: test\n\n[Decision](../../work/decisions/DEC-1.md)\n",
            )
            self._write(root, "work/decisions/DEC-1.md", "# DEC-1: decision\n")
            result = spiderweb.scan_repository(root, include_thin=False)
            rows = {row["path"]: row for row in result.artifacts}
            self.assertEqual(rows["work/tasks/TASK-1.md"]["incoming_active"], ["AGENTS.md"])
            self.assertEqual(
                rows["work/tasks/TASK-1.md"]["outgoing_active"],
                ["work/decisions/DEC-1.md"],
            )
            self.assertEqual(
                rows["work/decisions/DEC-1.md"]["incoming_active"],
                ["work/tasks/TASK-1.md"],
            )

    def test_broken_link_is_objective_finding(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(root, "AGENTS.md", "# Agents\n")
            self._write(root, "work/tasks/TASK-1.md", "# TASK-1\n\n[Missing](../nope.md)\n")
            result = spiderweb.scan_repository(root, include_thin=False)
            broken = [f for f in result.findings if f.code == "BROKEN_LINK"]
            self.assertEqual(len(broken), 1)
            self.assertEqual(broken[0].severity, "BROKEN")

    def test_duplicate_declared_stable_id_is_broken(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(root, "work/ideas/a.md", "# IDEA-123: A\n")
            self._write(root, "work/ideas/b.md", "# Other\n\n- ID: `IDEA-123`\n")
            result = spiderweb.scan_repository(root, include_thin=False)
            duplicates = [f for f in result.findings if f.code == "DUPLICATE_STABLE_ID"]
            self.assertEqual(len(duplicates), 1)
            self.assertIn("IDEA-123", duplicates[0].detail)

    def test_heading_reference_does_not_declare_stable_id(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(root, "work/ideas/a.md", "# IDEA-123: A\n")
            self._write(root, "work/notes/review.md", "# Review of IDEA-123\n")
            result = spiderweb.scan_repository(root, include_thin=False)
            self.assertFalse(
                any(f.code == "DUPLICATE_STABLE_ID" for f in result.findings)
            )

    def test_orphan_and_thin_candidates_are_advisory(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(root, "AGENTS.md", "# Agents\n\n[One](work/notes/one.md)\n")
            self._write(root, "work/notes/one.md", "# One\n")
            self._write(root, "work/notes/orphan.md", "# Orphan\n")
            result = spiderweb.scan_repository(root)
            codes = {(f.path, f.code) for f in result.findings}
            self.assertIn(("work/notes/one.md", "THIN_CONNECTION"), codes)
            self.assertIn(("work/notes/orphan.md", "ORPHAN_CANDIDATE"), codes)
            self.assertFalse(
                any(
                    f.severity == "BROKEN"
                    for f in result.findings
                    if f.code in {"THIN_CONNECTION", "ORPHAN_CANDIDATE"}
                )
            )

    def test_historical_only_connection_is_distinguished_from_orphan(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(
                root,
                "migration/legacy-runtime-source/history.md",
                "# History\n",
            )
            self._write(
                root,
                "work/notes/current.md",
                "# Current\n\n[Old](../../migration/legacy-runtime-source/history.md)\n",
            )
            result = spiderweb.scan_repository(root, include_thin=False)
            codes = {(f.path, f.code) for f in result.findings}
            self.assertIn(("work/notes/current.md", "HISTORICAL_ONLY"), codes)
            self.assertNotIn(("work/notes/current.md", "ORPHAN_CANDIDATE"), codes)

    def test_worktree_copies_are_excluded_by_default(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(root, "work/notes/real.md", "# Real\n")
            self._write(
                root,
                ".claude/worktrees/wt-a/work/notes/real.md",
                "# Real copy\n",
            )
            default = spiderweb.scan_repository(root, include_thin=False)
            with_wt = spiderweb.scan_repository(
                root, include_thin=False, include_worktrees=True
            )
            self.assertEqual(default.files_scanned, 1)
            self.assertEqual(with_wt.files_scanned, 2)

    def test_historical_files_are_opt_in(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(
                root,
                "migration/legacy-runtime-source/history.md",
                "# History\n",
            )
            without = spiderweb.scan_repository(root, include_thin=False)
            with_history = spiderweb.scan_repository(
                root, include_historical=True, include_thin=False
            )
            self.assertEqual(without.files_scanned, 0)
            self.assertEqual(with_history.files_scanned, 1)

    def test_not_promoted_without_current_disposition_is_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(
                root,
                "work/ideas/idea.md",
                "# IDEA-1: thing\n\n## Promotion\n\nNot promoted.\n",
            )
            result = spiderweb.scan_repository(root, include_thin=False)
            self.assertTrue(
                any(f.code == "UNRECONCILED_CAPTURE" for f in result.findings)
            )

    def test_current_disposition_suppresses_not_promoted_warning(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(
                root,
                "work/ideas/idea.md",
                "# IDEA-1: thing\n\n## Promotion\n\nNot promoted.\n\n"
                "## Current disposition\n\nTEST\n",
            )
            result = spiderweb.scan_repository(root, include_thin=False)
            self.assertFalse(
                any(f.code == "UNRECONCILED_CAPTURE" for f in result.findings)
            )

    def test_pending_experiment_past_end_date_is_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(
                root,
                "work/experiments/EXP-1.md",
                "# EXP-1\n\n- result: pending\n"
                "- window: 2026-07-21 through 2026-08-04\n",
            )
            result = spiderweb.scan_repository(
                root, as_of=date(2026, 8, 26), include_thin=False
            )
            findings = [
                f for f in result.findings if f.code == "OVERDUE_PENDING_EXPERIMENT"
            ]
            self.assertEqual(len(findings), 1)
            self.assertIn("2026-08-04", findings[0].detail)

    def test_fail_on_broken_is_optional(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(root, "work/note.md", "# Note\n\n[Missing](missing.md)\n")
            with redirect_stdout(io.StringIO()):
                advisory = spiderweb.main(["--root", str(root), "--no-thin"])
                strict = spiderweb.main(
                    ["--root", str(root), "--no-thin", "--fail-on-broken"]
                )
            self.assertEqual(advisory, 0)
            self.assertEqual(strict, 1)

    def test_json_output_is_machine_readable(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(root, "AGENTS.md", "# Agents\n")
            output = io.StringIO()
            with redirect_stdout(output):
                code = spiderweb.main(["--root", str(root), "--json"])
            self.assertEqual(code, 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["files_scanned"], 1)
            self.assertIn("findings", payload)
            self.assertIn("artifacts", payload)


if __name__ == "__main__":
    unittest.main()
