from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from runtime.routing.environment_reports import (
    select_fresh_environment_reports,
    select_recorded_environment_reports,
)
from runtime.state import TaskStore
from runtime.environment import (
    EnvironmentFingerprint,
    EnvironmentKind,
    NetworkMode,
    ObservationState,
    VersionObservation,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_REF = "runtime/environment/specs/maps-runtime-ci.json"


def _evidence_contract() -> dict:
    return {
        "title": "Recorded environment report task",
        "outcome": "Routing can source a report from recorded run evidence",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "MEDIUM",
        "decision_authority": "Implementation choices inside declared scope",
        "verification": "Run deterministic tests",
        "evidence_expected": "Passing test output",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "Stop on scope or authority uncertainty",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": ["src"],
        "non_goals": ["No unrelated changes"],
        "acceptance_criteria": ["environment evidence is projected for routing"],
        "stop_conditions": ["required evidence is missing"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


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


class RecordedEnvironmentReportSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = TaskStore(Path(self.tmp.name) / "maps.db")
        from runtime.environment.spec import load_environment_spec

        self.spec = load_environment_spec(REPO_ROOT / SPEC_REF)

    def _contracted_task(
        self, task_id: str = "TASK-REC", *, required: bool = False, max_age: int = 900
    ) -> str:
        created = self.store.create_task(task_id=task_id, project_id="default")
        self.assertTrue(created.ok, created)
        contract = _evidence_contract()
        contract["environment"] = {
            "spec_ref": SPEC_REF,
            "max_age_seconds": max_age,
            "required_for_routing": required,
        }
        shaped = self.store.update_contract(task_id, contract)
        self.assertTrue(shaped.ok, shaped.message)
        self.assertTrue(self.store.promote_ready(task_id, actor="tester").ok)
        self.assertTrue(self.store.claim_task(task_id, "worker", lease_seconds=600).ok)
        return task_id

    def _fingerprint(self, *, python_version: str = "3.12.4") -> EnvironmentFingerprint:
        observed = python_version is not None
        return EnvironmentFingerprint(
            environment_spec_hash=self.spec.sha256,
            environment_kind=EnvironmentKind.LOCAL,
            runtimes={
                "python": VersionObservation(
                    ObservationState.OBSERVED if observed else ObservationState.MISSING,
                    python_version,
                )
            },
            tools={
                "bash": VersionObservation(ObservationState.OBSERVED, "5.2.26"),
                "git": VersionObservation(ObservationState.OBSERVED, "2.45.1"),
                "python": VersionObservation(
                    ObservationState.OBSERVED, python_version or "3.12.4"
                ),
            },
            repo_revision="abc123",
            worktree_dirty=False,
            dependency_hashes={"runtime/requirements.txt": "a" * 64},
            network_mode=NetworkMode.REQUIRED_GENERAL,
            allowed_domains=(),
            service_availability={},
            secret_availability={},
            observed_at="2026-08-31T09:00:00Z",
        )

    def _record(self, task_id: str, fingerprint: EnvironmentFingerprint) -> None:
        run = self.store.create_run_manifest(
            task_id,
            "worker",
            repo_root=Path(self.tmp.name),
            created_by="dispatcher",
            readable_paths=["."],
        )
        self.assertTrue(run.ok, run.message)
        recorded = self.store.record_run_environment_evidence(
            run.task["run_id"],
            spec=self.spec,
            fingerprint=fingerprint,
            spec_ref=SPEC_REF,
            recorded_by="observer",
        )
        self.assertTrue(recorded.ok, recorded.message)

    def _select(self, task_ids, *, now=None):
        return select_recorded_environment_reports(
            self.store, task_ids, repo_root=REPO_ROOT, now=now
        )

    def test_fresh_recorded_report_is_projected(self) -> None:
        task_id = self._contracted_task()
        self._record(task_id, self._fingerprint())
        selected = self._select([task_id])
        self.assertEqual(selected.diagnostics, {task_id: "fresh"})
        self.assertEqual(selected.reports[task_id].state.value, "COMPATIBLE")

    def test_recorded_incompatible_report_is_projected_not_swallowed(self) -> None:
        task_id = self._contracted_task()
        self._record(task_id, self._fingerprint(python_version="3.11.9"))
        selected = self._select([task_id])
        self.assertEqual(selected.diagnostics, {task_id: "fresh"})
        self.assertEqual(selected.reports[task_id].state.value, "INCOMPATIBLE")

    def test_stale_recorded_report_is_dropped_not_converted(self) -> None:
        task_id = self._contracted_task()
        self._record(task_id, self._fingerprint(python_version="3.11.9"))
        # Evidence was written "now"; evaluate freshness far in the future.
        selected = self._select(
            [task_id], now=datetime.now(timezone.utc) + timedelta(days=1)
        )
        self.assertEqual(selected.reports, {})
        self.assertEqual(selected.diagnostics, {task_id: "report_stale"})

    def test_no_recorded_report_is_reported(self) -> None:
        task_id = self._contracted_task(required=True)
        selected = self._select([task_id])
        self.assertEqual(selected.reports, {})
        self.assertEqual(selected.diagnostics, {task_id: "no_recorded_report"})

    def test_task_without_environment_contract_is_reported(self) -> None:
        created = self.store.create_task(task_id="TASK-PLAIN", project_id="default")
        self.assertTrue(created.ok, created)
        selected = self._select(["TASK-PLAIN"])
        self.assertEqual(selected.reports, {})
        self.assertEqual(
            selected.diagnostics, {"TASK-PLAIN": "no_environment_contract"}
        )

    def test_missing_task_is_reported(self) -> None:
        selected = self._select(["TASK-GONE"])
        self.assertEqual(selected.diagnostics, {"TASK-GONE": "task_missing"})


if __name__ == "__main__":
    unittest.main()
