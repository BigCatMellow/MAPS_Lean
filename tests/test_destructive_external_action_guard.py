"""Tests for the SEC3 / 6.4 destructive/external action Hook guard.

Covers the impl-readiness addendum
`work/notes/2026-08-31-sec3-guard-impl-readiness-design.md` (behavior Qs 1-6):
the guard now consults the task's `task_policy` authority model through a
duck-typed `source`, denies actions outside the policy envelope, denies when a
recorded human reauthorization is absent, and allows in-envelope actions with
`evidence_refs`. `HarnessService.stop()` is the first firing call site for
`BEFORE_DESTRUCTIVE_ACTION`.
"""

from pathlib import Path
import tempfile
import unittest

from runtime.harness import (
    ExecutionBinding,
    HookDirective,
    HookEvent,
    HookRegistry,
    SessionRef,
)
from runtime.harness.hooks import HookEnforcement
from runtime.harness.service import HarnessService
from runtime.harness import OperationResult
from runtime.policy.destructive_action_guard import (
    DestructiveExternalActionGuard,
    register_destructive_external_action_guards,
)
from runtime.recovery.production import build_canonical_harness_service
from runtime.state import TaskStore


ROOT = Path(__file__).resolve().parents[1]


class _DictSource:
    """Minimal duck-typed `get_task` source."""

    def __init__(self, tasks):
        self._tasks = tasks

    def get_task(self, task_id):
        task = self._tasks.get(task_id)
        return dict(task) if task is not None else None


def _ctx(destructive, external, *, task_id="TASK-1", run_id="RUN-1", binding=True):
    context = {"destructive": destructive, "external": external}
    if binding:
        context["binding"] = {"task_id": task_id, "run_id": run_id}
    return context


class ClassificationContractTest(unittest.TestCase):
    def setUp(self):
        self.guard = DestructiveExternalActionGuard(_DictSource({}))

    def test_enum_member_exists(self):
        self.assertEqual(
            HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION.value,
            "DESTRUCTIVE_EXTERNAL_ACTION",
        )

    def test_missing_keys_fail_closed(self):
        for context in ({}, {"destructive": False}, {"external": False}):
            outcome = self.guard(context)
            self.assertEqual(outcome.directive, HookDirective.DENY)
            self.assertEqual(
                outcome.annotations["guard_code"], "CLASSIFICATION_REQUIRED"
            )

    def test_non_boolean_classification_is_denied(self):
        for value in ("true", 1, None, [], {}):
            with self.subTest(value=value):
                outcome = self.guard({"destructive": value, "external": False})
                self.assertEqual(outcome.directive, HookDirective.DENY)
                self.assertEqual(
                    outcome.annotations["guard_code"], "CLASSIFICATION_INVALID"
                )

    def test_both_explicitly_false_allows(self):
        outcome = self.guard({"destructive": False, "external": False})
        self.assertEqual(outcome.directive, HookDirective.ALLOW)
        self.assertEqual(
            outcome.annotations["guard_code"], "ACTION_NOT_CONSEQUENTIAL"
        )

    def test_consequential_action_without_binding_is_denied(self):
        outcome = self.guard(_ctx(True, False, binding=False))
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(
            outcome.annotations["guard_code"], "CLASSIFICATION_BINDING_REQUIRED"
        )

    def test_unreadable_task_is_denied(self):
        outcome = self.guard(_ctx(True, False, task_id="MISSING"))
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(
            outcome.annotations["guard_code"], "ACTION_POLICY_UNAVAILABLE"
        )

    def test_never_requires_approval(self):
        for destructive in (True, False):
            for external in (True, False):
                outcome = self.guard(_ctx(destructive, external))
                self.assertNotEqual(
                    outcome.directive, HookDirective.REQUIRE_APPROVAL
                )


class PolicyEnvelopeTest(unittest.TestCase):
    def _guard(self, policy):
        task = {"task_id": "TASK-1", "policy": {
            "destructive_action": False,
            "external_side_effect": False,
            "requires_operator_approval": False,
            "approved_by": None,
            "approved_at": None,
            **policy,
        }}
        return DestructiveExternalActionGuard(_DictSource({"TASK-1": task}))

    def test_destructive_outside_envelope_is_denied(self):
        outcome = self._guard({"destructive_action": False})(_ctx(True, False))
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(
            outcome.annotations["guard_code"], "ACTION_OUTSIDE_TASK_ENVELOPE"
        )

    def test_external_outside_envelope_is_denied(self):
        outcome = self._guard({"external_side_effect": False})(_ctx(False, True))
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(
            outcome.annotations["guard_code"], "ACTION_OUTSIDE_TASK_ENVELOPE"
        )

    def test_in_envelope_no_approval_needed_allows_with_evidence(self):
        outcome = self._guard({"destructive_action": True})(_ctx(True, False))
        self.assertEqual(outcome.directive, HookDirective.ALLOW)
        self.assertEqual(
            outcome.annotations["guard_code"], "ACTION_WITHIN_TASK_ENVELOPE"
        )
        self.assertEqual(
            outcome.evidence_refs,
            ("task:TASK-1", "run:RUN-1", "action_classes:destructive"),
        )

    def test_in_envelope_but_reauthorization_absent_is_denied(self):
        guard = self._guard(
            {"destructive_action": True, "requires_operator_approval": True}
        )
        outcome = guard(_ctx(True, False))
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(
            outcome.annotations["guard_code"], "OPERATOR_REAUTHORIZATION_ABSENT"
        )

    def test_recorded_reauthorization_allows(self):
        guard = self._guard(
            {
                "destructive_action": True,
                "requires_operator_approval": True,
                "approved_by": "operator-1",
                "approved_at": "2026-08-31T00:00:00Z",
            }
        )
        outcome = guard(_ctx(True, False))
        self.assertEqual(outcome.directive, HookDirective.ALLOW)


class RegistrationTest(unittest.TestCase):
    def test_registration_records_enforcement_on_both_events(self):
        registry = HookRegistry()
        register_destructive_external_action_guards(
            registry, DestructiveExternalActionGuard(_DictSource({}))
        )
        for event in (
            HookEvent.BEFORE_DESTRUCTIVE_ACTION,
            HookEvent.BEFORE_EXTERNAL_ACTION,
        ):
            self.assertTrue(
                registry.has_enforcement(
                    event, HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION
                )
            )

    def test_registration_rejects_a_foreign_guard(self):
        class Sneaky(DestructiveExternalActionGuard):
            pass

        with self.assertRaises(TypeError):
            register_destructive_external_action_guards(
                HookRegistry(), Sneaky(_DictSource({}))
            )


class TaskStoreRoundTripTest(unittest.TestCase):
    """Round-trip policy + `maps approve` through a real temp-file TaskStore."""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.store = TaskStore(Path(self.td.name) / "maps.db")
        created = self.store.create_task(title="destructive work", project_id="proj-1")
        self.assertTrue(created.ok)
        self.task_id = created.task["task_id"]
        self.guard = DestructiveExternalActionGuard(self.store)

    def _ctx(self):
        return _ctx(True, False, task_id=self.task_id, run_id="RUN-9")

    def test_outside_envelope_then_in_envelope_then_reauthorization(self):
        # (1) default policy -> destructive_action is False -> outside envelope.
        outcome = self.guard(self._ctx())
        self.assertEqual(
            outcome.annotations["guard_code"], "ACTION_OUTSIDE_TASK_ENVELOPE"
        )

        # (2) bring the action into the envelope, but also cross inherited
        # authority -> reauthorization absent.
        self.assertTrue(
            self.store.update_contract(
                self.task_id,
                {
                    "policy": {
                        "destructive_action": True,
                        "requires_operator_approval": True,
                    }
                },
            ).ok
        )
        outcome = self.guard(self._ctx())
        self.assertEqual(
            outcome.annotations["guard_code"], "OPERATOR_REAUTHORIZATION_ABSENT"
        )

        # (3) `maps approve <task_id> --approved-by ... --note ...`
        approved = self.store.record_operator_approval(
            self.task_id, approved_by="operator-1", note="kill authorised"
        )
        self.assertTrue(approved.ok, approved.message)
        outcome = self.guard(self._ctx())
        self.assertEqual(outcome.directive, HookDirective.ALLOW)
        self.assertEqual(
            outcome.annotations["guard_code"], "ACTION_WITHIN_TASK_ENVELOPE"
        )


class _StopOnlyAdapter:
    adapter_id = "hcom"

    def __init__(self):
        self.stops = []

    def stop(self, binding, reason):
        self.stops.append((binding.run_id, reason))
        return OperationResult.success("STOPPED", "Stopped.", mutated=True)


class ComposedServiceStopTest(unittest.TestCase):
    """A composed `HarnessService.stop()` gates on the destructive guard."""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.store = TaskStore(self.root / "maps.db")
        created = self.store.create_task(title="x", project_id="proj-1")
        self.task_id = created.task["task_id"]

    def _binding(self):
        return ExecutionBinding(
            task_id=self.task_id,
            run_id="RUN-1",
            worker_id="worker-1",
            task_revision="rev-1",
            project_id="proj-1",
            session_id="sess-1",
        )

    def _ref(self):
        return SessionRef(
            session_id="sess-1",
            worker_id="worker-1",
            adapter="hcom",
            project_id="proj-1",
            remote_ref="s-1",
        )

    def test_no_guard_registered_requires_destructive_guard(self):
        service = HarnessService([_StopOnlyAdapter()])
        result = service.stop(self._binding(), self._ref(), "recovery kill")
        self.assertEqual(result.code, "DESTRUCTIVE_GUARD_REQUIRED")

    def test_composed_service_denies_when_guard_denies(self):
        # Default policy: destructive_action is False -> guard denies the stop
        # before the canonical check even runs.
        service = build_canonical_harness_service(
            self.store, project_id="proj-1", repo_root=self.repo
        )
        result = service.stop(self._binding(), self._ref(), "recovery kill")
        self.assertEqual(result.code, "HOOK_DENIED")
        self.assertIn(
            "outside the task's policy envelope",
            " ".join(result.data["blocking_reasons"]),
        )


class ProductionWiringTest(unittest.TestCase):
    """The guard is now wired -- exactly at the sites the addendum names."""

    def _runtime_sources(self):
        return sorted(ROOT.joinpath("runtime").rglob("*.py"))

    def test_only_expected_files_reference_the_enforcement_member(self):
        allowed = {
            ROOT / "runtime" / "harness" / "hooks.py",
            ROOT / "runtime" / "harness" / "service.py",
            ROOT / "runtime" / "policy" / "destructive_action_guard.py",
            ROOT / "runtime" / "policy" / "__init__.py",
        }
        offenders = [
            str(path.relative_to(ROOT))
            for path in self._runtime_sources()
            if path not in allowed
            and "DESTRUCTIVE_EXTERNAL_ACTION" in path.read_text(encoding="utf-8")
        ]
        self.assertEqual(offenders, [])

    def test_guard_is_composed_only_in_production_composition_root(self):
        offenders = [
            str(path.relative_to(ROOT))
            for path in self._runtime_sources()
            if path.name not in {"destructive_action_guard.py", "__init__.py", "production.py"}
            and (
                "DestructiveExternalActionGuard" in path.read_text(encoding="utf-8")
                or "register_destructive_external_action_guards"
                in path.read_text(encoding="utf-8")
            )
        ]
        self.assertEqual(offenders, [])

    def test_stop_is_the_only_destructive_firing_site(self):
        service_text = (
            ROOT / "runtime" / "harness" / "service.py"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            service_text.count("HookEvent.BEFORE_DESTRUCTIVE_ACTION"), 2
        )  # the enforcement gate + the hooks.run firing call
        self.assertNotIn("HookEvent.BEFORE_EXTERNAL_ACTION", service_text)


if __name__ == "__main__":
    unittest.main()
