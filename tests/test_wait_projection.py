import copy
import tempfile
from pathlib import Path
import unittest

from runtime.state import TaskStore
from runtime.wait_projection import project_task_waits


def task(
    task_id="TASK-1",
    *,
    status="READY",
    agi_status="AGI READY",
    dependencies=None,
    policy=None,
    submission=None,
    title="Task",
):
    return {
        "task_id": task_id,
        "title": title,
        "status": status,
        "agi_status": agi_status,
        "dependencies": list(dependencies or []),
        "policy": dict(
            policy
            or {
                "requires_operator_approval": False,
                "destructive_action": False,
                "external_side_effect": False,
                "security_sensitive": False,
                "broad_architecture": False,
                "paid_execution": False,
                "approved_by": None,
                "approved_at": None,
            }
        ),
        "submission": copy.deepcopy(submission),
    }


class FakeSource:
    def __init__(self, tasks=None, reviews=None):
        self.tasks = copy.deepcopy(tasks or {})
        self.reviews = copy.deepcopy(reviews or {})

    def get_task(self, task_id):
        value = self.tasks.get(task_id)
        return copy.deepcopy(value) if value is not None else None

    def list_reviews(self, task_id):
        return copy.deepcopy(self.reviews.get(task_id, []))


def codes(report):
    return [item["code"] for item in report["reasons"]]


class WaitProjectionTests(unittest.TestCase):
    def test_missing_task_returns_none(self):
        self.assertIsNone(project_task_waits(FakeSource(), "TASK-MISSING"))

    def test_done_is_terminal_not_waiting(self):
        source = FakeSource({"TASK-1": task(status="DONE", dependencies=["TASK-2"])})

        report = project_task_waits(source, "TASK-1")

        self.assertEqual(report["summary_state"], "NO_VERIFIED_WAIT")
        self.assertEqual(report["reasons"], [])
        self.assertFalse(report["runnable_claimed"])
        self.assertEqual(report["coverage"]["dependencies"], "NOT_APPLICABLE")

    def test_unresolved_and_missing_declared_dependencies_are_verified_waits(self):
        source = FakeSource(
            {
                "TASK-1": task(dependencies=["TASK-2", "TASK-3"]),
                "TASK-2": task("TASK-2", status="ACTIVE"),
            }
        )

        report = project_task_waits(source, "TASK-1")

        self.assertEqual(report["summary_state"], "WAITING")
        dependency_reasons = [
            item for item in report["reasons"] if item["code"] == "WAIT_DEPENDENCY"
        ]
        self.assertEqual(len(dependency_reasons), 2)
        details = {item["details"]["dependency_id"]: item["details"] for item in dependency_reasons}
        self.assertEqual(details["TASK-2"]["dependency_status"], "ACTIVE")
        self.assertEqual(details["TASK-3"]["dependency_status"], "MISSING")
        self.assertEqual(report["coverage"]["dependencies"], "VERIFIED")

    def test_done_dependency_removes_dependency_wait(self):
        source = FakeSource(
            {
                "TASK-1": task(dependencies=["TASK-2"]),
                "TASK-2": task("TASK-2", status="DONE"),
            }
        )

        report = project_task_waits(source, "TASK-1")

        self.assertEqual(report["summary_state"], "NO_VERIFIED_WAIT")
        self.assertNotIn("WAIT_DEPENDENCY", codes(report))

    def test_ready_for_review_without_open_review_is_unclaimed_wait(self):
        source = FakeSource(
            {
                "TASK-1": task(
                    status="READY_FOR_REVIEW",
                    submission={"submission_count": 2, "author_id": "worker-a"},
                )
            }
        )

        report = project_task_waits(source, "TASK-1")

        self.assertEqual(report["summary_state"], "WAITING")
        self.assertEqual(codes(report), ["WAIT_REVIEW_UNCLAIMED"])
        self.assertEqual(report["reasons"][0]["details"]["submission_count"], 2)
        self.assertEqual(report["coverage"]["review"], "VERIFIED")

    def test_ready_for_review_with_one_open_review_is_in_progress_wait(self):
        source = FakeSource(
            {
                "TASK-1": task(
                    status="READY_FOR_REVIEW",
                    submission={"submission_count": 1, "author_id": "worker-a"},
                )
            },
            {
                "TASK-1": [
                    {
                        "id": 7,
                        "reviewer_id": "reviewer-b",
                        "summary": "free text must not become cause",
                        "created_at": "2026-08-16T01:00:00Z",
                        "completed_at": None,
                    }
                ]
            },
        )

        report = project_task_waits(source, "TASK-1")

        self.assertEqual(report["summary_state"], "WAITING")
        self.assertEqual(codes(report), ["WAIT_REVIEW_IN_PROGRESS"])
        reason = report["reasons"][0]
        self.assertEqual(reason["details"]["review_id"], 7)
        self.assertEqual(reason["details"]["reviewer_id"], "reviewer-b")
        self.assertNotIn("summary", reason["details"])

    def test_ambiguous_open_reviews_preserve_unknown(self):
        source = FakeSource(
            {
                "TASK-1": task(
                    status="READY_FOR_REVIEW",
                    submission={"submission_count": 1, "author_id": "worker-a"},
                )
            },
            {
                "TASK-1": [
                    {"id": 1, "reviewer_id": "r1", "completed_at": None},
                    {"id": 2, "reviewer_id": "r2", "completed_at": None},
                ]
            },
        )

        report = project_task_waits(source, "TASK-1")

        self.assertEqual(report["summary_state"], "UNKNOWN")
        self.assertEqual(codes(report), ["REVIEW_GATE_AMBIGUOUS"])
        self.assertEqual(report["coverage"]["review"], "UNKNOWN")

    def test_ready_for_review_without_submission_preserves_unknown(self):
        source = FakeSource({"TASK-1": task(status="READY_FOR_REVIEW")})

        report = project_task_waits(source, "TASK-1")

        self.assertEqual(report["summary_state"], "UNKNOWN")
        self.assertEqual(codes(report), ["REVIEW_GATE_EVIDENCE_INCOMPLETE"])

    def test_operator_approval_wait_uses_existing_policy_trigger_logic(self):
        policy = {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": True,
            "security_sensitive": True,
            "broad_architecture": False,
            "paid_execution": False,
            "approved_by": None,
            "approved_at": None,
        }
        source = FakeSource({"TASK-1": task(policy=policy)})

        report = project_task_waits(source, "TASK-1")

        self.assertEqual(report["summary_state"], "WAITING")
        self.assertEqual(codes(report), ["WAIT_OPERATOR_APPROVAL"])
        self.assertEqual(
            report["reasons"][0]["details"]["approval_triggers"],
            ["external_side_effect", "security_sensitive"],
        )

    def test_recorded_operator_approval_removes_wait(self):
        policy = {
            "requires_operator_approval": True,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
            "approved_by": "operator",
            "approved_at": "2026-08-16T01:00:00Z",
        }
        source = FakeSource({"TASK-1": task(policy=policy)})

        report = project_task_waits(source, "TASK-1")

        self.assertEqual(report["summary_state"], "NO_VERIFIED_WAIT")
        self.assertNotIn("WAIT_OPERATOR_APPROVAL", codes(report))

    def test_partial_approval_identity_preserves_unknown(self):
        policy = {
            "requires_operator_approval": True,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
            "approved_by": "operator",
            "approved_at": None,
        }
        source = FakeSource({"TASK-1": task(policy=policy)})

        report = project_task_waits(source, "TASK-1")

        self.assertEqual(report["summary_state"], "UNKNOWN")
        self.assertEqual(codes(report), ["OPERATOR_APPROVAL_EVIDENCE_INCOMPLETE"])

    def test_approval_is_not_called_a_wait_when_task_is_not_agi_ready(self):
        policy = {
            "requires_operator_approval": True,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
            "approved_by": None,
            "approved_at": None,
        }
        source = FakeSource(
            {"TASK-1": task(policy=policy, agi_status="AGI FAIL — NEEDS_SHAPING")}
        )

        report = project_task_waits(source, "TASK-1")

        self.assertEqual(report["summary_state"], "NO_VERIFIED_WAIT")
        self.assertNotIn("WAIT_OPERATOR_APPROVAL", codes(report))

    def test_multiple_verified_wait_reasons_are_retained(self):
        policy = {
            "requires_operator_approval": True,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
            "approved_by": None,
            "approved_at": None,
        }
        source = FakeSource(
            {
                "TASK-1": task(dependencies=["TASK-2"], policy=policy),
                "TASK-2": task("TASK-2", status="ACTIVE"),
            }
        )

        report = project_task_waits(source, "TASK-1")

        self.assertEqual(report["summary_state"], "WAITING")
        self.assertEqual(codes(report), ["WAIT_DEPENDENCY", "WAIT_OPERATOR_APPROVAL"])

    def test_generic_blocked_cause_remains_unknown_and_prose_is_ignored(self):
        blocked = task(
            status="BLOCKED",
            title="Waiting on Alice because the network is down",
        )
        blocked["outcome"] = "Reviewer said the service is unavailable"
        source = FakeSource(
            {"TASK-1": blocked},
            {
                "TASK-1": [
                    {
                        "id": 99,
                        "reviewer_id": "r",
                        "verdict": "BLOCKED",
                        "summary": "Waiting for deployment credentials",
                        "completed_at": "2026-08-16T01:00:00Z",
                    }
                ]
            },
        )

        report = project_task_waits(source, "TASK-1")

        self.assertEqual(report["summary_state"], "UNKNOWN")
        self.assertEqual(codes(report), ["BLOCKED_CAUSE_UNPROVEN"])
        self.assertNotIn("credentials", repr(report).lower())
        self.assertNotIn("alice", repr(report).lower())

    def test_blocked_task_with_exact_dependency_keeps_blocked_summary_and_wait_reason(self):
        source = FakeSource(
            {
                "TASK-1": task(status="BLOCKED", dependencies=["TASK-2"]),
                "TASK-2": task("TASK-2", status="ACTIVE"),
            }
        )

        report = project_task_waits(source, "TASK-1")

        self.assertEqual(report["summary_state"], "BLOCKED")
        self.assertEqual(codes(report), ["WAIT_DEPENDENCY"])

    def test_active_without_structured_prerequisite_is_not_inferred_waiting(self):
        source = FakeSource({"TASK-1": task(status="ACTIVE")})

        report = project_task_waits(source, "TASK-1")

        self.assertEqual(report["summary_state"], "NO_VERIFIED_WAIT")
        self.assertEqual(report["reasons"], [])
        self.assertEqual(report["coverage"]["communication"], "UNKNOWN")
        self.assertEqual(report["coverage"]["recovery"], "UNKNOWN")
        self.assertEqual(report["coverage"]["helpers"], "UNKNOWN")
        self.assertFalse(report["runnable_claimed"])

    def test_projection_is_deterministic_for_unchanged_source(self):
        source = FakeSource(
            {
                "TASK-1": task(dependencies=["TASK-3", "TASK-2"]),
                "TASK-2": task("TASK-2", status="ACTIVE"),
                "TASK-3": task("TASK-3", status="READY"),
            }
        )

        self.assertEqual(
            project_task_waits(source, "TASK-1"),
            project_task_waits(source, "TASK-1"),
        )

    def test_real_task_store_projection_is_read_only(self):
        with tempfile.TemporaryDirectory() as td:
            store = TaskStore(Path(td) / "maps.db")
            created = store.create_task(title="read-only projection")
            self.assertTrue(created.ok)
            task_id = created.task["task_id"]
            before_task = store.get_task(task_id)
            before_events = store.list_events(task_id)

            report = project_task_waits(store, task_id)

            after_task = store.get_task(task_id)
            after_events = store.list_events(task_id)
            self.assertEqual(report["summary_state"], "NO_VERIFIED_WAIT")
            self.assertEqual(before_task, after_task)
            self.assertEqual(before_events, after_events)


if __name__ == "__main__":
    unittest.main()
