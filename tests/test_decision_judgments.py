import unittest

from runtime.decision import (
    ChoiceDecision,
    DecisionBroker,
    DecisionConfig,
    diagnose_failure,
    annotate_recovery_actions,
    recovery_path_advisory,
    review_evidence_preflight,
)
from runtime.incident_taxonomy import IncidentClass


class FakeProvider:
    provider_name = "fake"

    def __init__(self, picks):
        self.picks = list(picks)
        self.calls = []

    def choose(self, *, state, question, choices):
        self.calls.append({"state": state, "choices": dict(choices)})
        pick = self.picks.pop(0)
        return ChoiceDecision(
            choice=pick,
            confidence=0.95,
            probabilities={key: (0.95 if key == pick else 0.0) for key in choices},
            provider="fake",
            model="fake-v1",
        )


def broker(provider, *, allow_content=False):
    return DecisionBroker(
        DecisionConfig(
            provider="jev",
            mode="active",
            model="test",
            min_confidence=0.8,
            allow_content=allow_content,
        ),
        provider=provider,
    )


class FakeStore:
    def get_task(self, task_id):
        return {
            "task_id": task_id,
            "risk": "MEDIUM",
            "verification": "pytest",
            "evidence_expected": "test output",
            "acceptance_criteria": ["tests pass"],
            "review_required": "INDEPENDENT",
        }

    def get_submission(self, task_id):
        return {
            "author_id": "worker",
            "submission_count": 1,
            "evidence": "pytest: 42 passed",
        }

    def get_criterion_claims(self, task_id):
        return []


class DecisionJudgmentTests(unittest.TestCase):
    def test_exact_incident_class_needs_no_provider(self):
        provider = FakeProvider([])
        result = diagnose_failure(
            "TOOL_FAILURE",
            broker=broker(provider),
        )
        self.assertEqual(result.selected, IncidentClass.TOOL_FAILURE.value)
        self.assertEqual(provider.calls, [])

    def test_unknown_failure_can_use_bounded_provider_classification(self):
        provider = FakeProvider([IncidentClass.ENVIRONMENT_DRIFT.value])
        result = diagnose_failure(
            "python disappeared after package refresh",
            broker=broker(provider),
        )
        self.assertEqual(result.selected, IncidentClass.ENVIRONMENT_DRIFT.value)
        self.assertEqual(len(provider.calls), 1)

    def test_recovery_path_is_advisory_only(self):
        provider = FakeProvider([
            IncidentClass.RECOVERY_FAILURE.value,
            "inspect_environment_or_validation",
        ])
        result = recovery_path_advisory(
            {"action": "resume_failed", "reason": "resume returned error"},
            task={"task_id": "T1", "status": "ACTIVE", "risk": "MEDIUM"},
            broker=broker(provider),
        )
        self.assertTrue(result["advisory_only"])
        self.assertEqual(
            result["recovery_path"]["selected"],
            "inspect_environment_or_validation",
        )

    def test_review_preflight_does_not_send_evidence_text_by_default(self):
        provider = FakeProvider(["appears_sufficient"])
        result = review_evidence_preflight(
            FakeStore(),
            "T1",
            broker=broker(provider, allow_content=False),
        )
        self.assertTrue(result["advisory_only"])
        self.assertFalse(result["content_included"])
        state = provider.calls[0]["state"]
        self.assertNotIn("evidence_text", state["submission"])
        self.assertEqual(state["submission"]["evidence_text_chars"], 17)

    def test_review_preflight_can_send_bounded_evidence_when_explicitly_enabled(self):
        provider = FakeProvider(["appears_sufficient"])
        result = review_evidence_preflight(
            FakeStore(),
            "T1",
            broker=broker(provider, allow_content=True),
        )
        self.assertTrue(result["content_included"])
        self.assertEqual(
            provider.calls[0]["state"]["submission"]["evidence_text"],
            "pytest: 42 passed",
        )


    def test_recovery_annotation_resolves_task_through_incident_index(self):
        provider = FakeProvider([
            IncidentClass.RECOVERY_FAILURE.value,
            "reassign_worker",
        ])

        class Tasks:
            def get_task(self, task_id):
                return {
                    "task_id": task_id,
                    "status": "ACTIVE",
                    "risk": "MEDIUM",
                    "claimed_by": "worker-1",
                }

        output = annotate_recovery_actions(
            [{"incident_id": "I1", "action": "resume_failed", "reason": "boom"}],
            Tasks(),
            broker=broker(provider),
            incident_index={"I1": {"task_id": "T1"}},
        )
        advisory = output[0]["decision_advisory"]
        task_state = provider.calls[0]["state"]["task"]
        self.assertEqual(task_state["task_id"], "T1")
        self.assertEqual(advisory["recovery_path"]["selected"], "reassign_worker")


if __name__ == "__main__":
    unittest.main()
