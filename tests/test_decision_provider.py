import os
import unittest
from unittest.mock import patch

from runtime.decision import (
    ChoiceDecision,
    DecisionBroker,
    DecisionConfig,
)
from runtime.policy import WorkerProfile
from runtime.routing import recommend_route


def task(task_id="TASK-1", **changes):
    value = {
        "task_id": task_id,
        "title": task_id,
        "project_id": "default",
        "status": "READY",
        "agi_status": "AGI READY",
        "task_type": "IMPLEMENTATION",
        "risk": "LOW",
        "objective": f"Complete {task_id}",
        "output_paths": ["runtime/example.py"],
        "policy": {},
    }
    value.update(changes)
    return value


class FakeProvider:
    provider_name = "fake"

    def __init__(self, picks=None, *, confidence=0.9, raises=False):
        self.picks = list(picks or [])
        self.confidence = confidence
        self.raises = raises
        self.calls = []

    def choose(self, *, state, question, choices):
        self.calls.append(tuple(choices))
        if self.raises:
            raise RuntimeError("provider unavailable")
        choice = self.picks.pop(0) if self.picks else next(iter(choices))
        return ChoiceDecision(
            choice=choice,
            confidence=self.confidence,
            probabilities={
                key: (self.confidence if key == choice else 0.0)
                for key in choices
            },
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

    def broker(self, provider, mode="active", min_confidence=0.8):
        return DecisionBroker(
            DecisionConfig(
                provider="jev",
                mode=mode,
                model="test",
                min_confidence=min_confidence,
            ),
            provider=provider,
        )

    def test_default_off_preserves_existing_router_behavior(self):
        result = recommend_route(
            [task()],
            [self.expensive, self.cheap],
        )
        self.assertEqual(result.worker_id, "cheap")
        self.assertIsNone(result.decision_evidence)

    def test_shadow_is_automatic_but_does_not_change_worker(self):
        provider = FakeProvider(["expensive"])
        result = recommend_route(
            [task()],
            [self.expensive, self.cheap],
            decision_broker=self.broker(provider, mode="shadow"),
        )
        self.assertEqual(result.worker_id, "cheap")
        evidence = result.decision_evidence["worker_selection"]
        self.assertEqual(evidence["suggested"], "expensive")
        self.assertEqual(evidence["selected"], "cheap")
        self.assertFalse(evidence["applied"])
        self.assertEqual(len(provider.calls), 1)

    def test_active_can_choose_only_from_eligible_workers(self):
        provider = FakeProvider(["expensive"])
        result = recommend_route(
            [task()],
            [self.expensive, self.cheap],
            decision_broker=self.broker(provider),
        )
        self.assertEqual(result.worker_id, "expensive")
        self.assertTrue(result.decision_evidence["worker_selection"]["applied"])

    def test_active_low_confidence_falls_back_and_recommends_escalation(self):
        provider = FakeProvider(["expensive"], confidence=0.55)
        result = recommend_route(
            [task()],
            [self.expensive, self.cheap],
            decision_broker=self.broker(provider, min_confidence=0.8),
        )
        self.assertEqual(result.worker_id, "cheap")
        evidence = result.decision_evidence["worker_selection"]
        self.assertEqual(evidence["status"], "low_confidence")
        self.assertTrue(evidence["escalation_recommended"])

    def test_next_task_selection_is_automatic(self):
        provider = FakeProvider(["TASK-2"])
        result = recommend_route(
            [task("TASK-1"), task("TASK-2")],
            [self.cheap],
            decision_broker=self.broker(provider),
        )
        self.assertEqual(result.task_id, "TASK-2")
        self.assertEqual(result.worker_id, "cheap")
        self.assertIn("next_task_selection", result.decision_evidence)
        self.assertEqual(len(provider.calls), 1)

    def test_task_and_worker_judgments_both_run_when_both_are_choices(self):
        provider = FakeProvider(["TASK-2", "expensive"])
        result = recommend_route(
            [task("TASK-1"), task("TASK-2")],
            [self.expensive, self.cheap],
            decision_broker=self.broker(provider),
        )
        self.assertEqual(result.task_id, "TASK-2")
        self.assertEqual(result.worker_id, "expensive")
        self.assertEqual(
            set(result.decision_evidence),
            {"next_task_selection", "worker_selection"},
        )
        self.assertEqual(len(provider.calls), 2)

    def test_ineligible_provider_choice_falls_back_deterministically(self):
        provider = FakeProvider(["not-eligible"])
        result = recommend_route(
            [task()],
            [self.expensive, self.cheap],
            decision_broker=self.broker(provider),
        )
        self.assertEqual(result.worker_id, "cheap")
        self.assertEqual(
            result.decision_evidence["worker_selection"]["status"],
            "invalid",
        )

    def test_provider_failure_falls_back_deterministically(self):
        provider = FakeProvider(raises=True)
        result = recommend_route(
            [task()],
            [self.expensive, self.cheap],
            decision_broker=self.broker(provider),
        )
        self.assertEqual(result.worker_id, "cheap")
        evidence = result.decision_evidence["worker_selection"]
        self.assertEqual(evidence["status"], "error")
        self.assertEqual(evidence["error_type"], "RuntimeError")

    def test_policy_filter_happens_before_broker(self):
        provider = FakeProvider(["ineligible-helper"])
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
            decision_broker=self.broker(provider),
        )
        self.assertEqual(result.worker_id, "cheap")
        self.assertNotIn("ineligible-helper", provider.calls[0])

    def test_broker_reuses_identical_judgment_in_process(self):
        provider = FakeProvider(["b"])
        broker = self.broker(provider)
        kwargs = {
            "decision_type": "test",
            "state": {"x": 1},
            "question": "Choose",
            "choices": {"a": None, "b": None},
            "deterministic_choice": "a",
        }
        first = broker.choose(**kwargs)
        second = broker.choose(**kwargs)
        self.assertEqual(first.selected, "b")
        self.assertEqual(second.selected, "b")
        self.assertEqual(len(provider.calls), 1)
        self.assertTrue(second.evidence["cache_hit"])

    def test_environment_enables_jev_automatically_in_shadow_mode(self):
        with patch.dict(
            os.environ,
            {
                "MAPS_DECISION_PROVIDER": "jev",
                "TYPESAFE_API_KEY": "not-used-by-this-test",
            },
            clear=False,
        ):
            os.environ.pop("MAPS_DECISION_MODE", None)
            config = DecisionConfig.from_environment()
        self.assertEqual(config.provider, "jev")
        self.assertEqual(config.mode, "shadow")
        self.assertEqual(config.model, "jev-latest")

    def test_provider_off_cannot_have_active_mode(self):
        with self.assertRaises(ValueError):
            DecisionConfig(provider="off", mode="active").validate()


if __name__ == "__main__":
    unittest.main()
