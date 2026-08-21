from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from runtime.routing.environment_reports import select_fresh_environment_reports
from runtime.state import TaskStore


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_REF = "runtime/environment/specs/maps-runtime-ci.json"


def _report(spec_hash: str, state: str = "INCOMPATIBLE") -> dict[str, object]:
    return {
        "state": state,
        "reasons": ["missing_python"],
        "warnings": [],
        "environment_spec_hash": spec_hash,
        "fingerprint_sha256": "fingerprint-hash",
        "reference_fingerprint_sha256": None,
    }


class RoutingEnvironmentReportSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = TaskStore(Path(self.tmp.name) / "maps.db")
        created = self.store.create_task(task_id="TASK-1", project_id="default")
        self.assertTrue(created.ok, created)
        from runtime.environment.spec import load_environment_spec

        self.spec = load_environment_spec(REPO_ROOT / SPEC_REF)
        self.now = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)

    def _envelope(self, **changes) -> dict[str, object]:
        value: dict[str, object] = {
            "task_id": "TASK-1",
            "project_id": "default",
            "spec_ref": SPEC_REF,
            "task_revision": self.store.compute_task_revision("TASK-1"),
            "produced_at": (self.now - timedelta(seconds=60)).isoformat(),
            "max_age_seconds": 900,
            "report": _report(self.spec.sha256),
        }
        value.update(changes)
        return value

    def test_fresh_envelope_selects_report_for_router(self) -> None:
        selected = select_fresh_environment_reports(
            {"TASK-1": self._envelope()},
            store=self.store,
            repo_root=REPO_ROOT,
            now=self.now,
        )

        self.assertEqual(selected.diagnostics, {"TASK-1": "fresh"})
        self.assertEqual(selected.reports["TASK-1"].state.value, "INCOMPATIBLE")

    def test_stale_report_is_omitted_not_converted_to_incompatible(self) -> None:
        selected = select_fresh_environment_reports(
            {
                "TASK-1": self._envelope(
                    produced_at=(self.now - timedelta(seconds=901)).isoformat(),
                    max_age_seconds=900,
                )
            },
            store=self.store,
            repo_root=REPO_ROOT,
            now=self.now,
        )

        self.assertEqual(selected.reports, {})
        self.assertEqual(selected.diagnostics, {"TASK-1": "report_stale"})

    def test_task_revision_mismatch_is_omitted(self) -> None:
        selected = select_fresh_environment_reports(
            {"TASK-1": self._envelope(task_revision="old-revision")},
            store=self.store,
            repo_root=REPO_ROOT,
            now=self.now,
        )

        self.assertEqual(selected.reports, {})
        self.assertEqual(
            selected.diagnostics, {"TASK-1": "task_revision_mismatch"}
        )

    def test_spec_hash_mismatch_is_omitted(self) -> None:
        selected = select_fresh_environment_reports(
            {
                "TASK-1": self._envelope(
                    report=_report("wrong-spec-hash"),
                )
            },
            store=self.store,
            repo_root=REPO_ROOT,
            now=self.now,
        )

        self.assertEqual(selected.reports, {})
        self.assertEqual(selected.diagnostics, {"TASK-1": "spec_hash_mismatch"})

    def test_malformed_envelope_fails_closed_per_entry(self) -> None:
        selected = select_fresh_environment_reports(
            {"TASK-1": {"task_id": "TASK-1"}},
            store=self.store,
            repo_root=REPO_ROOT,
            now=self.now,
        )

        self.assertEqual(selected.reports, {})
        self.assertEqual(selected.diagnostics, {"TASK-1": "malformed_envelope"})


if __name__ == "__main__":
    unittest.main()
