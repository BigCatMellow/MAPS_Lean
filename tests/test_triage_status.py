"""Tests for tools/triage_status.py -- the advisory triage-status backstop.

Slice 2 of the triage standard (work/notes/2026-09-03-triage-core-standard-design.md
§5.5). The tool is read-only; these tests pin its classification of FRICTION_LOG
entries (closed / unresolved / overdue), its repair-note check, and the CLI
contract (advisory exit 0, --strict opt-in, --json).
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout

from tools.triage_status import build_report, main, parse_friction_log


ROOT = Path(__file__).resolve().parents[1]

_CLOSED = """\
## 2026-08-01 — old resolved thing
- class: tool-gap
- opened: 2026-08-01
- signal: something broke
- countermeasure: a real fix in place
- verified: VERIFIED 2026-08-05
- follow-up: none
- 2026-08-10 follow-up (trajectory check #5): **CLOSED — verified.**
"""

_FRESH_UNRESOLVED = """\
## 2026-09-01 — recent open thing
- class: process-gap
- opened: 2026-09-01
- signal: a new gap
- countermeasure: none yet
- verified: UNVERIFIED
- follow-up: check next pass
- 2026-09-02 follow-up (trajectory check #21): pass 1 of 3; no recurrence.
"""

_OVERDUE_BY_PASSES = """\
## 2026-07-01 — stale open thing
- class: recurring-stall
- opened: 2026-07-01
- signal: keeps not closing
- countermeasure: proposed but unadopted
- verified: UNVERIFIED
- follow-up: still open
- 2026-07-10 follow-up (trajectory check #10): noted.
- 2026-07-20 follow-up (trajectory check #11): noted again.
- 2026-08-01 follow-up (trajectory check #12): still noted.
"""

_LEGACY_NO_OPENED = """\
## 2026-06-01 — legacy entry without opened field
- class: drift
- signal: old format
- countermeasure: none yet
- verified: UNVERIFIED
- follow-up: none
"""


def _log(*entries: str) -> str:
    return "# Friction log\n\nPreamble.\n\n" + "\n".join(entries)


class ParseTests(unittest.TestCase):
    def test_parses_headers_and_bodies(self):
        entries = parse_friction_log(_log(_CLOSED, _FRESH_UNRESOLVED))
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].title, "old resolved thing")
        self.assertEqual(entries[1].date, "2026-09-01")

    def test_opened_falls_back_to_header_date(self):
        (entry,) = parse_friction_log(_log(_LEGACY_NO_OPENED))
        self.assertEqual(entry.opened, "2026-06-01")

    def test_explicit_opened_field_wins(self):
        (entry,) = parse_friction_log(_log(_OVERDUE_BY_PASSES))
        self.assertEqual(entry.opened, "2026-07-01")
        self.assertEqual(entry.passes_seen, 3)


class ReportTests(unittest.TestCase):
    def _report(self, text: str, **kw):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "work" / "coordination").mkdir(parents=True)
            (root / "work" / "coordination" / "FRICTION_LOG.md").write_text(text, encoding="utf-8")
            (root / "work" / "notes").mkdir(parents=True)
            return build_report(root, today=date(2026, 9, 3), **kw)

    def test_closed_entry_is_not_flagged(self):
        report = self._report(_log(_CLOSED))
        self.assertEqual(report.closed, 1)
        self.assertEqual(report.unresolved, [])
        self.assertEqual(report.overdue, [])

    def test_fresh_unresolved_is_unresolved_but_not_overdue(self):
        report = self._report(_log(_FRESH_UNRESOLVED))
        self.assertEqual([e.title for e in report.unresolved], ["recent open thing"])
        self.assertEqual(report.overdue, [])

    def test_entry_seen_across_three_passes_is_overdue(self):
        report = self._report(_log(_OVERDUE_BY_PASSES))
        self.assertEqual([e.title for e in report.overdue], ["stale open thing"])

    def test_age_bound_marks_overdue_without_pass_refs(self):
        report = self._report(_log(_LEGACY_NO_OPENED), stale_days=30)
        # opened 2026-06-01, today 2026-09-03 -> ~94 days, 0 passes seen.
        self.assertEqual([e.title for e in report.overdue],
                         ["legacy entry without opened field"])

    def test_counts_and_mix(self):
        report = self._report(_log(_CLOSED, _FRESH_UNRESOLVED, _OVERDUE_BY_PASSES))
        self.assertEqual(report.total, 3)
        self.assertEqual(report.closed, 1)
        self.assertEqual(len(report.open_entries), 2)
        self.assertEqual(len(report.unresolved), 2)
        self.assertEqual(len(report.overdue), 1)

    def test_drift_repair_note_missing_regression_case_is_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "work" / "coordination").mkdir(parents=True)
            (root / "work" / "coordination" / "FRICTION_LOG.md").write_text(_log(_CLOSED), encoding="utf-8")
            notes = root / "work" / "notes"
            notes.mkdir(parents=True)
            (notes / "2026-08-18-x-repair.md").write_text(
                "# Repair\n- Severity: `DRIFT`\n- Prevention: a habit\n", encoding="utf-8"
            )
            (notes / "2026-08-19-y-repair.md").write_text(
                "# Repair\n- Severity: `BLOCKING`\n- countermeasure: fix\n"
                "- regression: frozen test added\n", encoding="utf-8"
            )
            report = build_report(root, today=date(2026, 9, 3))
        flagged = [Path(n.path).name for n in report.incomplete_repair_notes]
        self.assertEqual(flagged, ["2026-08-18-x-repair.md"])


class CliTests(unittest.TestCase):
    def _run(self, *argv: str) -> tuple[int, str]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["--root", str(ROOT), *argv])
        return code, buf.getvalue()

    def test_advisory_exit_zero_on_real_repo(self):
        code, text = self._run()
        self.assertEqual(code, 0)
        self.assertIn("FRICTION_LOG:", text)

    def test_json_mode_is_valid_json(self):
        code, text = self._run("--json")
        self.assertEqual(code, 0)
        payload = json.loads(text)
        self.assertIn("friction_log", payload)
        self.assertIn("overdue", payload["friction_log"])

    def test_strict_exits_nonzero_only_when_overdue(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "work" / "coordination").mkdir(parents=True)
            (root / "work" / "coordination" / "FRICTION_LOG.md").write_text(
                _log(_OVERDUE_BY_PASSES), encoding="utf-8"
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(["--root", str(root), "--strict"])
        self.assertEqual(code, 1)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
