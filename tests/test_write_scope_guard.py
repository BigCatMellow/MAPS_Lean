"""Tests for the 6.4 write-scope Hook guard.

Covers `work/notes/2026-09-15-6.4-write-credential-guard-design.md`: the
guard consults the task's real `output_paths` through a duck-typed `source`,
reuses `runtime.helpers.common.path_in_scope` rather than reimplementing
scope math, denies writes outside that scope, and allows writes inside it
with `evidence_refs`. Unlike the sibling caller-declared-action guard, there
is no production firing call site yet (see `ComposedButUnwiredTest`) --
`HarnessService` has no operation corresponding to "a file write happens."
"""

from pathlib import Path
import re
import tempfile
import unittest

from runtime.harness import HookDirective, HookEvent, HookRegistry
from runtime.harness.hooks import HookEnforcement
from runtime.harness.service import HarnessService
from runtime.policy.write_scope_guard import (
    WriteScopeGuard,
    register_write_scope_guards,
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


def _ctx(write_paths, *, task_id="TASK-1", run_id="RUN-1", binding=True):
    context = {} if write_paths is _MISSING else {"write_paths": write_paths}
    if binding:
        context["binding"] = {"task_id": task_id, "run_id": run_id}
    return context


_MISSING = object()


class ClassificationContractTest(unittest.TestCase):
    def setUp(self):
        self.guard = WriteScopeGuard(_DictSource({}), repo_root="/repo")

    def test_enum_member_exists(self):
        self.assertEqual(HookEnforcement.WRITE_SCOPE.value, "WRITE_SCOPE")

    def test_missing_write_paths_fails_closed(self):
        outcome = self.guard(_ctx(_MISSING))
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "WRITE_PATHS_REQUIRED")

    def test_invalid_write_paths_are_denied(self):
        for value in ("src/foo.py", [], [1, 2], ["", "  "], None, {}):
            with self.subTest(value=value):
                outcome = self.guard(_ctx(value))
                self.assertEqual(outcome.directive, HookDirective.DENY)
                self.assertEqual(
                    outcome.annotations["guard_code"], "WRITE_PATHS_INVALID"
                )

    def test_missing_binding_is_denied(self):
        outcome = self.guard(_ctx(["src/foo.py"], binding=False))
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(
            outcome.annotations["guard_code"], "WRITE_BINDING_REQUIRED"
        )

    def test_unreadable_task_is_denied(self):
        outcome = self.guard(_ctx(["src/foo.py"], task_id="MISSING"))
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(
            outcome.annotations["guard_code"], "WRITE_POLICY_UNAVAILABLE"
        )

    def test_never_requires_approval(self):
        for value in (["src/foo.py"], _MISSING, "bad"):
            outcome = self.guard(_ctx(value))
            self.assertNotEqual(outcome.directive, HookDirective.REQUIRE_APPROVAL)


class ScopeEnvelopeTest(unittest.TestCase):
    def _guard(self, output_paths):
        task = {"task_id": "TASK-1", "output_paths": output_paths}
        return WriteScopeGuard(_DictSource({"TASK-1": task}), repo_root="/repo")

    def test_undeclared_output_paths_is_denied(self):
        for value in ([], None):
            with self.subTest(value=value):
                outcome = self._guard(value)(_ctx(["src/foo.py"]))
                self.assertEqual(outcome.directive, HookDirective.DENY)
                self.assertEqual(
                    outcome.annotations["guard_code"], "WRITE_SCOPE_UNDECLARED"
                )

    def test_path_outside_scope_is_denied(self):
        outcome = self._guard(["src"])(_ctx(["docs/readme.md"]))
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(
            outcome.annotations["guard_code"], "WRITE_OUTSIDE_TASK_SCOPE"
        )

    def test_one_path_outside_scope_denies_even_if_others_in_scope(self):
        outcome = self._guard(["src"])(_ctx(["src/foo.py", "docs/readme.md"]))
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(
            outcome.annotations["guard_code"], "WRITE_OUTSIDE_TASK_SCOPE"
        )

    def test_path_inside_scope_allows_with_evidence(self):
        outcome = self._guard(["src"])(_ctx(["src/foo.py"]))
        self.assertEqual(outcome.directive, HookDirective.ALLOW)
        self.assertEqual(
            outcome.annotations["guard_code"], "WRITE_WITHIN_TASK_SCOPE"
        )
        self.assertEqual(
            outcome.evidence_refs,
            ("task:TASK-1", "run:RUN-1", "paths:src/foo.py"),
        )

    def test_nested_path_inside_scope_allows(self):
        outcome = self._guard(["src"])(_ctx(["src/pkg/mod.py"]))
        self.assertEqual(outcome.directive, HookDirective.ALLOW)


class RegistrationTest(unittest.TestCase):
    def test_registration_records_enforcement_on_before_write(self):
        registry = HookRegistry()
        register_write_scope_guards(
            registry, WriteScopeGuard(_DictSource({}), repo_root="/repo")
        )
        self.assertTrue(
            registry.has_enforcement(HookEvent.BEFORE_WRITE, HookEnforcement.WRITE_SCOPE)
        )
        self.assertFalse(
            registry.has_enforcement(HookEvent.AFTER_WRITE, HookEnforcement.WRITE_SCOPE)
        )

    def test_registration_rejects_a_foreign_guard(self):
        class Sneaky(WriteScopeGuard):
            pass

        with self.assertRaises(TypeError):
            register_write_scope_guards(
                HookRegistry(), Sneaky(_DictSource({}), repo_root="/repo")
            )


class TaskStoreRoundTripTest(unittest.TestCase):
    """Round-trip real `output_paths` through a real temp-file TaskStore."""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.store = TaskStore(Path(self.td.name) / "maps.db")
        created = self.store.create_task(title="write scope work", project_id="proj-1")
        self.assertTrue(created.ok)
        self.task_id = created.task["task_id"]
        self.guard = WriteScopeGuard(self.store, repo_root=self.td.name)

    def _ctx(self, paths):
        return _ctx(paths, task_id=self.task_id, run_id="RUN-9")

    def test_undeclared_then_scoped_then_outside(self):
        # (1) fresh task has no output_paths -> undeclared.
        outcome = self.guard(self._ctx(["src/foo.py"]))
        self.assertEqual(
            outcome.annotations["guard_code"], "WRITE_SCOPE_UNDECLARED"
        )

        # (2) declare a real output scope.
        self.assertTrue(
            self.store.update_contract(
                self.task_id, {"output_paths": ["src"]}
            ).ok
        )
        outcome = self.guard(self._ctx(["src/foo.py"]))
        self.assertEqual(outcome.directive, HookDirective.ALLOW)

        # (3) a path outside the declared scope is denied.
        outcome = self.guard(self._ctx(["docs/readme.md"]))
        self.assertEqual(
            outcome.annotations["guard_code"], "WRITE_OUTSIDE_TASK_SCOPE"
        )


class ComposedButUnwiredTest(unittest.TestCase):
    """The guard is composed in production but has no firing call site yet."""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.repo = Path(self.td.name) / "repo"
        self.repo.mkdir()
        self.store = TaskStore(Path(self.td.name) / "maps.db")

    def test_guard_is_composed_in_the_production_root(self):
        service = build_canonical_harness_service(
            self.store, project_id="proj-1", repo_root=self.repo
        )
        registry = service.hooks
        self.assertTrue(
            registry.has_enforcement(HookEvent.BEFORE_WRITE, HookEnforcement.WRITE_SCOPE)
        )

    def test_no_operation_fires_before_write(self):
        # HarnessService mediates start/send/resume/stop only -- confirms
        # the design note's finding stays true: no operation corresponds to
        # "a file write happens", so BEFORE_WRITE is composed but unfired.
        service_text = (
            ROOT / "runtime" / "harness" / "service.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("HookEvent.BEFORE_WRITE", service_text)
        self.assertNotIn("HookEvent.AFTER_WRITE", service_text)


class ProductionWiringTest(unittest.TestCase):
    """Mirrors the sibling guard's isolation tests, scoped to this guard."""

    def _runtime_sources(self):
        return sorted(ROOT.joinpath("runtime").rglob("*.py"))

    def test_only_expected_files_reference_the_enforcement_member(self):
        # Exact-token match, not substring: `runtime/state/integrity.py`
        # legitimately carries an unrelated pre-existing `WRITE_SCOPE_EXCEEDS_TASK`
        # result code (the real `verify_git_run`/`create_run_manifest` scope
        # check, see the design note's correction) which a bare substring scan
        # would misfire on.
        pattern = re.compile(r"\bWRITE_SCOPE\b")
        allowed = {
            ROOT / "runtime" / "harness" / "hooks.py",
            ROOT / "runtime" / "policy" / "write_scope_guard.py",
            ROOT / "runtime" / "policy" / "__init__.py",
            ROOT / "runtime" / "recovery" / "production.py",
        }
        offenders = [
            str(path.relative_to(ROOT))
            for path in self._runtime_sources()
            if path not in allowed
            and pattern.search(path.read_text(encoding="utf-8"))
        ]
        self.assertEqual(offenders, [])

    def test_guard_is_composed_only_in_production_composition_root(self):
        offenders = [
            str(path.relative_to(ROOT))
            for path in self._runtime_sources()
            if path.name not in {"write_scope_guard.py", "__init__.py", "production.py"}
            and (
                "WriteScopeGuard" in path.read_text(encoding="utf-8")
                or "register_write_scope_guards" in path.read_text(encoding="utf-8")
            )
        ]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
