import unittest

from runtime.decision import ChoiceDecision
from runtime.policy import WorkerProfile
from runtime.routing import recommend_route


def task():
    return {
        "task_id": "TASK-DECISION",
        "project_id": "default",
        "status": "READY",
        "agi_status": "AGI READY",
        "task_type": "IMPLEMENTATION",
        "risk": "LOW",
        "output_paths": ["runtime/example.py"],
        "policy": {},
    }


class FakeProvider:
    provider_name = "fake"

    def __init__(self, choice="expensive", *, raises=False):
        self.choice = choice
        self.raises = raises
        self.calls = 0

    def choose(self, *, state, question, choices):
        self.calls += 1
        if self.raises:
            raise RuntimeError("provider unavailable")
        return ChoiceDecision(
            choice=self.choice,
            confidence=0.9,
            probabilities={key: (0.9 if key == self.choice else 0.1) for key in choices},
            provider=self.provider_name,
            model="fake-v1",
        )


class DecisionProviderTests(unittest.TestCase):
    def setUp(self):
        self.cheap = WorkerProfile(
            "cheap",
            "bounded",
            supported_task_types=("IMPLEMENTATION",),
            max_risk="LOW",
            cost_rank=1,
        )
        self.expensive = WorkerProfile(
            "expensive",
            "core",
            supported_task_types=("IMPLEMENTATION",),
            max_risk="HIGH",
            cost_rank=20,
        )

    def test_default_off_preserves_existing_router_behavior(self):
        provider = FakeProvider()
        result = recommend_route(
            [task()],
            [self.expensive, self.cheap],
            decision_provider=provider,
        )
        self.assertEqual(result.worker_id, "cheap")
        self.assertIsNone(result.decision_evidence)
        self.assertEqual(provider.calls, 0)

    def test_shadow_records_recommendation_without_changing_worker(self):
        provider = FakeProvider("expensive")
        result = recommend_route(
            [task()],
            [self.expensive, self.cheap],
            decision_provider=provider,
            decision_mode="shadow",
        )
        self.assertEqual(result.worker_id, "cheap")
        self.assertEqual(result.decision_evidence["suggested_worker_id"], "expensive")
        self.assertEqual(result.decision_evidence["selected_worker_id"], "cheap")
        self.assertEqual(result.decision_evidence["mode"], "shadow")

    def test_active_can_choose_only_from_eligible_workers(self):
        provider = FakeProvider("expensive")
        result = recommend_route(
            [task()],
            [self.expensive, self.cheap],
            decision_provider=provider,
            decision_mode="active",
        )
        self.assertEqual(result.worker_id, "expensive")
        self.assertEqual(result.decision_evidence["status"], "ok")

    def test_ineligible_provider_choice_falls_back_deterministically(self):
        provider = FakeProvider("not-eligible")
        result = recommend_route(
            [task()],
            [self.expensive, self.cheap],
            decision_provider=provider,
            decision_mode="active",
        )
        self.assertEqual(result.worker_id, "cheap")
        self.assertEqual(result.decision_evidence["status"], "invalid")

    def test_provider_failure_falls_back_deterministically(self):
        provider = FakeProvider(raises=True)
        result = recommend_route(
            [task()],
            [self.expensive, self.cheap],
            decision_provider=provider,
            decision_mode="active",
        )
        self.assertEqual(result.worker_id, "cheap")
        self.assertEqual(result.decision_evidence["status"], "error")
        self.assertEqual(result.decision_evidence["error_type"], "RuntimeError")

    def test_policy_filter_happens_before_provider(self):
        provider = FakeProvider("ineligible-helper")
        ineligible = WorkerProfile(
            "ineligible-helper",
            "helper",
            supported_task_types=("MAINTENANCE",),
            max_risk="LOW",
            cost_rank=0,
        )
        result = recommend_route(
            [task()],
            [ineligible, self.cheap, self.expensive],
            decision_provider=provider,
            decision_mode="active",
        )
        self.assertEqual(result.worker_id, "cheap")
        self.assertEqual(result.decision_evidence["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
