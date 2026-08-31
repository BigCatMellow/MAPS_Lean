"""Tests for the Hook/Harness production composition root.

Covers `runtime/recovery/production.py::build_canonical_harness_service` and the
opt-in keyword / `maps recovery-tick` flags that reach it, per
`work/notes/2026-08-26-hook-enforcement-composition-root-design.md`.

The design's load-bearing properties, each pinned by a test below:

- default (no opt-in) => no `HarnessService` constructed, byte-identical to the
  pre-existing direct-`hcom.resume()` fallback (§3b, §4.3);
- opt-in => production resume routes through `HarnessService.resume(binding,
  session_ref)` with a fully-populated `ExecutionBinding` (§1b);
- only `CanonicalRunGuard` is registered, never
  `DestructiveExternalActionGuard` (§3d);
- `--enforce-canonical-run` requires `--repo-root` and `--harness-project-id`
  and never infers either (§3c);
- the composition root did not touch `runtime/recovery/supervisor.py`, so the
  #160 source guard keeps passing unmodified (§4.3, §4.4).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from io import StringIO
from contextlib import redirect_stderr, redirect_stdout
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from runtime.cli import main as cli_main
from runtime.harness import ExecutionBinding, OperationResult, SessionRef
from runtime.harness.adapters import HcomHarnessAdapter
from runtime.harness.hooks import HookEnforcement, HookEvent
from runtime.harness.service import HarnessService
from runtime.recovery import RecoveryStore
from runtime.recovery.production import (
    build_canonical_harness_service,
    run_recovery_tick,
    run_recovery_tick_isolated,
)
from runtime.state import TaskStore


def _lineage_contract(output_path: str = "src") -> dict:
    return {
        "title": "Composition root",
        "outcome": "Silent-stop incidents carry an exact run_id when one is bound",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "MEDIUM",
        "decision_authority": "bounded implementation",
        "verification": "recovery composition-root tests",
        "evidence_expected": "passing tests",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "stop on ambiguous lineage",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": [output_path],
        "non_goals": ["no task authority change"],
        "acceptance_criteria": ["run_id binding is exact, never guessed"],
        "stop_conditions": ["lineage identity is ambiguous"],
    }


class FakeHcomBackend:
    """Supervisor/adapter-facing hcom stand-in."""

    def __init__(self, sessions=None):
        self.sessions = list(sessions or [])
        self.resumes: list = []

    def list_sessions(self, *, include_stopped: bool = False):
        return [dict(item) for item in self.sessions]

    def resume(self, name, *, headless=False, terminal=None, go=True):
        self.resumes.append({"name": name, "headless": headless, "go": go})
        return object()


class SpyHarnessService:
    """Records resume(binding, session_ref) calls; returns a fixed OperationResult."""

    def __init__(self, result=None):
        self.result = result or OperationResult.success(
            "SESSION_RESUMED", "hcom resume request completed.", mutated=True
        )
        self.calls: list = []

    def resume(self, binding, session_ref):
        self.calls.append((binding, session_ref))
        return self.result


class BuildCanonicalHarnessServiceTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.store = TaskStore(self.root / "maps.db")

    def test_composes_one_hcom_adapter_and_a_canonical_run_registry(self):
        service = build_canonical_harness_service(
            self.store, project_id="proj-1", repo_root=self.repo
        )
        self.assertIsInstance(service, HarnessService)
        # Exactly one adapter, keyed "hcom".
        self.assertEqual(service.adapter_ids, ("hcom",))
        # CanonicalRunGuard is registered as CANONICAL_RUN enforcement on every
        # lifecycle point register_canonical_run_guards installs, including the
        # resume path.
        for event in (
            HookEvent.RUN_STARTING,
            HookEvent.BEFORE_SEND,
            HookEvent.BEFORE_RESUME,
            HookEvent.SESSION_STOPPING,
        ):
            self.assertTrue(
                service.hooks.has_enforcement(event, HookEnforcement.CANONICAL_RUN),
                f"missing CANONICAL_RUN enforcement on {event}",
            )

    def test_registers_destructive_external_action_enforcement(self):
        """SEC3 / 6.4: `HarnessService.stop()` fires `BEFORE_DESTRUCTIVE_ACTION`,
        so the guard is now composed here (addendum Q2). Both events carry the
        enforcement role; only the destructive event has a firing call site.
        """
        service = build_canonical_harness_service(
            self.store, project_id="proj-1", repo_root=self.repo
        )
        for event in (
            HookEvent.BEFORE_DESTRUCTIVE_ACTION,
            HookEvent.BEFORE_EXTERNAL_ACTION,
        ):
            self.assertTrue(
                service.hooks.has_enforcement(
                    event, HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION
                )
            )

    def test_registers_memory_provenance_enforcement_on_before_send(self):
        """6.22 slice 1: `MemoryProvenanceGuard` is composed here on the
        already-fired `BEFORE_SEND`, mirroring the SEC3 destructive guard. No
        production `send()` caller exists yet, so it changes no live behavior.
        """
        service = build_canonical_harness_service(
            self.store, project_id="proj-1", repo_root=self.repo
        )
        self.assertTrue(
            service.hooks.has_enforcement(
                HookEvent.BEFORE_SEND, HookEnforcement.MEMORY_PROVENANCE
            )
        )

    def test_reuses_the_callers_store_as_the_canonical_run_source(self):
        """§3b/§4.5: the caller's TaskStore is reused; no second store is opened."""
        # production.py must not even name TaskStore -- construction reuses the
        # object handed in.
        source = (
            Path(__file__).parents[1] / "runtime" / "recovery" / "production.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("TaskStore(", source)

        service = build_canonical_harness_service(
            self.store, project_id="proj-1", repo_root=self.repo
        )
        adapter = service._adapters["hcom"]
        self.assertIs(adapter.lineage_writer, self.store)


class ProductionResumeRoutingTests(unittest.TestCase):
    """Opt-in routes tick()'s real resume through HarnessService.resume()."""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        (self.repo / "src").mkdir(parents=True)
        self.store = TaskStore(self.root / "maps.db")
        self.recovery_path = self.root / "recovery.json"
        self.now = datetime(2026, 8, 19, 20, 0, tzinfo=timezone.utc)

    def _bind_run(self, *, worker="worker-1", session_id="sess-1"):
        created = self.store.create_task(title="x", project_id="proj-1")
        self.assertTrue(created.ok)
        task_id = created.task["task_id"]
        self.assertTrue(self.store.update_contract(task_id, _lineage_contract()).ok)
        self.assertTrue(self.store.promote_ready(task_id).ok)
        self.assertTrue(self.store.claim_task(task_id, worker, lease_seconds=600).ok)
        writable = self.store.get_task(task_id)["output_paths"]
        manifest = self.store.create_run_manifest(
            task_id,
            worker,
            repo_root=self.repo,
            created_by="dispatcher",
            readable_paths=["."],
            writable_paths=writable,
        )
        self.assertTrue(manifest.ok, manifest.message)
        run_id = manifest.task["run_id"]
        adapter = HcomHarnessAdapter(
            FakeHcomBackend(), project_id="proj-1", lineage_writer=self.store
        )
        binding = ExecutionBinding(
            task_id=task_id,
            run_id=run_id,
            worker_id=worker,
            task_revision=manifest.task["task_revision"],
            project_id="proj-1",
            session_id=session_id,
        )
        session_ref = SessionRef(
            session_id=session_id,
            worker_id=worker,
            adapter="hcom",
            project_id="proj-1",
            remote_ref="session-1",
        )
        self.assertTrue(adapter.attach(binding, session_ref).ok)
        return task_id, run_id, manifest.task["task_revision"]

    def _schedule_due(self, *, task_id, run_id, worker_id="worker-1"):
        RecoveryStore(self.recovery_path).schedule(
            task_id=task_id,
            worker_id=worker_id,
            session_name="session-1",
            reason="scheduled",
            resume_after=(self.now - timedelta(seconds=1)).isoformat(),
            run_id=run_id,
        )

    def test_opt_in_routes_resume_through_harness_service_with_full_binding(self):
        task_id, run_id, task_revision = self._bind_run()
        self._schedule_due(task_id=task_id, run_id=run_id)
        spy = SpyHarnessService()

        with mock.patch(
            "runtime.recovery.production.build_canonical_harness_service",
            return_value=spy,
        ) as build, mock.patch(
            "runtime.recovery.production.HcomAdapter",
            lambda **kw: FakeHcomBackend(sessions=[]),
        ):
            result = run_recovery_tick(
                self.store,
                recovery_state_path=self.recovery_path,
                validation_repo_root=self.repo,
                harness_project_id="proj-1",
            )

        build.assert_called_once()
        self.assertEqual(build.call_args.kwargs["project_id"], "proj-1")
        self.assertEqual(build.call_args.kwargs["repo_root"], self.repo)

        self.assertEqual(len(spy.calls), 1)
        binding, session_ref = spy.calls[0]
        self.assertIsInstance(binding, ExecutionBinding)
        self.assertEqual(binding.project_id, "proj-1")
        self.assertEqual(binding.task_id, task_id)
        self.assertEqual(binding.run_id, run_id)
        self.assertEqual(binding.worker_id, "worker-1")
        self.assertEqual(binding.task_revision, task_revision)
        self.assertEqual(binding.session_id, "sess-1")
        self.assertEqual(session_ref.session_id, "sess-1")

        action = result["actions"][0]
        self.assertEqual(action["action"], "resume")
        self.assertEqual(action["harness_resume"]["code"], "SESSION_RESUMED")

    def test_default_no_opt_in_constructs_no_harness_service_and_falls_back(self):
        task_id, run_id, _ = self._bind_run()
        self._schedule_due(task_id=task_id, run_id=run_id)
        captured: dict = {}
        real = None

        from runtime.recovery import production as prod

        class CapturingSupervisor(prod.RecoverySupervisor):
            def __init__(self, **kwargs):
                captured.update(kwargs)
                super().__init__(**kwargs)

        backend = FakeHcomBackend(sessions=[{"name": "session-1", "status": "stopped"}])
        with mock.patch(
            "runtime.recovery.production.RecoverySupervisor", CapturingSupervisor
        ), mock.patch(
            "runtime.recovery.production.HcomAdapter", lambda **kw: backend
        ):
            with mock.patch(
                "runtime.recovery.production.build_canonical_harness_service",
                side_effect=AssertionError("must not be called without opt-in"),
            ):
                result = run_recovery_tick(
                    self.store, recovery_state_path=self.recovery_path
                )

        self.assertIsNone(captured["harness_service"])
        # Direct-resume fallback really executed.
        self.assertEqual(len(backend.resumes), 1)
        self.assertEqual(result["actions"][0]["action"], "resume")
        self.assertIsNone(result["actions"][0]["harness_resume"])

    def test_harness_project_id_without_repo_root_is_a_loud_error(self):
        with self.assertRaises(ValueError) as ctx:
            run_recovery_tick(
                self.store,
                recovery_state_path=self.recovery_path,
                harness_project_id="proj-1",
            )
        self.assertIn("validation_repo_root", str(ctx.exception))

    def test_isolated_variant_contains_the_missing_repo_root_error(self):
        out = run_recovery_tick_isolated(
            self.store,
            recovery_state_path=self.recovery_path,
            harness_project_id="proj-1",
        )
        self.assertFalse(out["ok"])
        self.assertIn("ValueError", out["error"])


class RecoveryTickEnforcementCliTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.db = self.root / "maps.db"
        TaskStore(self.db)  # initialise schema

    def run_cli(self, argv):
        out, err = StringIO(), StringIO()
        try:
            with redirect_stdout(out), redirect_stderr(err):
                code = cli_main(argv)
        except SystemExit as exc:  # argparse parser.error
            code = exc.code if isinstance(exc.code, int) else 2
        return code, out.getvalue(), err.getvalue()

    def test_enforce_without_repo_root_exits_nonzero_with_a_clear_message(self):
        code, _out, err = self.run_cli(
            ["--db", str(self.db), "recovery-tick", "--enforce-canonical-run",
             "--harness-project-id", "proj-1"]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("--repo-root", err)

    def test_enforce_without_harness_project_id_exits_nonzero(self):
        code, _out, err = self.run_cli(
            ["--db", str(self.db), "recovery-tick", "--enforce-canonical-run",
             "--repo-root", str(self.root)]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("--harness-project-id", err)

    def test_repo_root_alone_stays_advisory_and_opts_into_no_enforcement(self):
        captured: dict = {}
        real = run_recovery_tick_isolated

        def spy(*args, **kwargs):
            captured.update(kwargs)
            return real(*args, **kwargs)

        with mock.patch(
            "runtime.recovery.production.HcomAdapter",
            lambda **kw: FakeHcomBackend(),
        ), mock.patch("runtime.cli.run_recovery_tick_isolated", spy):
            code, _out, _err = self.run_cli(
                ["--db", str(self.db), "recovery-tick", "--repo-root", str(self.root)]
            )
        self.assertEqual(code, 0)
        self.assertEqual(captured["validation_repo_root"], str(self.root))
        self.assertIsNone(captured["harness_project_id"])

    def test_full_opt_in_threads_harness_project_id_through(self):
        captured: dict = {}
        real = run_recovery_tick_isolated

        def spy(*args, **kwargs):
            captured.update(kwargs)
            return real(*args, **kwargs)

        with mock.patch(
            "runtime.recovery.production.HcomAdapter",
            lambda **kw: FakeHcomBackend(),
        ), mock.patch("runtime.cli.run_recovery_tick_isolated", spy):
            code, _out, _err = self.run_cli(
                ["--db", str(self.db), "recovery-tick",
                 "--enforce-canonical-run",
                 "--repo-root", str(self.root),
                 "--harness-project-id", "proj-9"]
            )
        self.assertEqual(code, 0)
        self.assertEqual(captured["harness_project_id"], "proj-9")
        self.assertEqual(captured["validation_repo_root"], str(self.root))

    def test_claim_piggyback_never_opts_into_enforcement(self):
        captured: dict = {}
        real = run_recovery_tick_isolated

        def spy(*args, **kwargs):
            captured.update(kwargs)
            return real(*args, **kwargs)

        store = TaskStore(self.db)
        self.assertTrue(store.create_task(task_id="task-a").ok)
        contract = _lineage_contract("task-a.out")
        contract["review_required"] = "OWNER_CHECK"
        self.assertTrue(store.update_contract("task-a", contract).ok)
        self.assertTrue(store.promote_ready("task-a", actor="shaper").ok)

        with mock.patch(
            "runtime.recovery.production.HcomAdapter",
            lambda **kw: FakeHcomBackend(),
        ), mock.patch("runtime.cli.run_recovery_tick_isolated", spy):
            code, _out, _err = self.run_cli(
                ["--db", str(self.db), "claim", "task-a", "worker-a"]
            )
        self.assertEqual(code, 0)
        self.assertIsNone(captured.get("harness_project_id"))

    def test_enforce_validation_without_repo_root_exits_nonzero(self):
        code, _out, err = self.run_cli(
            ["--db", str(self.db), "recovery-tick", "--enforce-validation"]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("--repo-root", err)

    def test_enforce_validation_with_repo_root_threads_the_flag_through(self):
        captured: dict = {}
        real = run_recovery_tick_isolated

        def spy(*args, **kwargs):
            captured.update(kwargs)
            return real(*args, **kwargs)

        with mock.patch(
            "runtime.recovery.production.HcomAdapter",
            lambda **kw: FakeHcomBackend(),
        ), mock.patch("runtime.cli.run_recovery_tick_isolated", spy):
            code, _out, _err = self.run_cli(
                ["--db", str(self.db), "recovery-tick",
                 "--repo-root", str(self.root), "--enforce-validation"]
            )
        self.assertEqual(code, 0)
        self.assertTrue(captured["enforce_validation"])
        self.assertEqual(captured["validation_repo_root"], str(self.root))
        self.assertIsNone(captured["harness_project_id"])

    def test_recovery_tick_default_does_not_enable_the_validation_gate(self):
        captured: dict = {}
        real = run_recovery_tick_isolated

        def spy(*args, **kwargs):
            captured.update(kwargs)
            return real(*args, **kwargs)

        with mock.patch(
            "runtime.recovery.production.HcomAdapter",
            lambda **kw: FakeHcomBackend(),
        ), mock.patch("runtime.cli.run_recovery_tick_isolated", spy):
            code, _out, _err = self.run_cli(
                ["--db", str(self.db), "recovery-tick", "--repo-root", str(self.root)]
            )
        self.assertEqual(code, 0)
        self.assertFalse(captured["enforce_validation"])


class ProductionValidationGateWiringTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.db = self.root / "maps.db"
        TaskStore(self.db)

    def test_isolated_enforce_validation_without_repo_root_is_contained_valueerror(self):
        out = run_recovery_tick_isolated(
            TaskStore(self.db),
            recovery_state_path=self.root / "recovery.json",
            enforce_validation=True,
        )
        self.assertFalse(out["ok"])
        self.assertIn("ValueError", out["error"])
        self.assertIn("validation_repo_root", out["error"])

    def test_enforce_validation_threads_validation_blocks_resume_to_the_supervisor(self):
        from runtime.recovery import production as prod

        captured: dict = {}

        class CapturingSupervisor(prod.RecoverySupervisor):
            def __init__(self, **kwargs):
                captured.update(kwargs)
                super().__init__(**kwargs)

        backend = FakeHcomBackend(sessions=[])
        with mock.patch(
            "runtime.recovery.production.RecoverySupervisor", CapturingSupervisor
        ), mock.patch(
            "runtime.recovery.production.HcomAdapter", lambda **kw: backend
        ), mock.patch(
            "runtime.recovery.production.RunBoundValidator", lambda **kw: object()
        ):
            run_recovery_tick(
                TaskStore(self.db),
                recovery_state_path=self.root / "recovery.json",
                validation_repo_root=str(self.root),
                enforce_validation=True,
            )
        self.assertTrue(captured["validation_blocks_resume"])

    def test_default_leaves_validation_blocks_resume_false(self):
        from runtime.recovery import production as prod

        captured: dict = {}

        class CapturingSupervisor(prod.RecoverySupervisor):
            def __init__(self, **kwargs):
                captured.update(kwargs)
                super().__init__(**kwargs)

        backend = FakeHcomBackend(sessions=[])
        with mock.patch(
            "runtime.recovery.production.RecoverySupervisor", CapturingSupervisor
        ), mock.patch(
            "runtime.recovery.production.HcomAdapter", lambda **kw: backend
        ):
            run_recovery_tick(
                TaskStore(self.db),
                recovery_state_path=self.root / "recovery.json",
            )
        self.assertFalse(captured["validation_blocks_resume"])


class CompositionRootSourceBoundaryTests(unittest.TestCase):
    def test_supervisor_source_untouched_by_the_composition_root(self):
        """§4.3/§4.4: the composition root supplies a non-None argument to an
        existing parameter; it changes nothing in supervisor.py. This mirrors
        test_recovery_supervisor.py's #160 source guard so a regression here is
        caught even if that file is run separately.
        """
        source = Path(__file__).parents[1] / "runtime" / "recovery" / "supervisor.py"
        text = source.read_text(encoding="utf-8").lower()
        for forbidden in (
            "environmentspec",
            "make_validation_hook",
            "claim_task(",
            "submit_task(",
            "record_review(",
            "promote_ready(",
            "update_contract(",
        ):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
