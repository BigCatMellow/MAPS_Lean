from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from runtime.communication import HcomError
from runtime.harness import (
    ExecutionBinding,
    HookRegistry,
    OperationResult,
    SessionRef,
)
from runtime.harness.adapters import HcomHarnessAdapter
from runtime.harness.service import HarnessService
from runtime.policy.harness_guard import CanonicalRunGuard, register_canonical_run_guards
from runtime.recovery import RecoveryStore, RecoverySupervisor, session_is_live
from runtime.recovery.store import parse_time
from runtime.state import TaskStore


class FakeTasks:
    def __init__(self, tasks):
        self.tasks = {task["task_id"]: dict(task) for task in tasks}

    def get_task(self, task_id):
        task = self.tasks.get(task_id)
        return dict(task) if task else None

    def list_tasks(self, *, statuses=None, project_id=None):
        rows = list(self.tasks.values())
        if statuses:
            rows = [row for row in rows if row.get("status") in statuses]
        return [dict(row) for row in rows]


class FakeHcom:
    def __init__(self, sessions=None):
        self.sessions = sessions or []
        self.resumes = []
        self.fail = False

    def list_sessions(self, *, include_stopped=False):
        return [dict(item) for item in self.sessions]

    def resume(self, name, *, headless=False, terminal=None, go=True):
        self.resumes.append(
            {"name": name, "headless": headless, "terminal": terminal, "go": go}
        )
        if self.fail:
            raise HcomError("resume failed")
        return object()


def active_task(worker="worker-1"):
    return {
        "task_id": "TASK-1",
        "status": "ACTIVE",
        "claimed_by": worker,
        "owner": "owner",
    }


class RecoverySupervisorTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.store = RecoveryStore(Path(self.td.name) / "recovery.json")
        self.now = datetime(2026, 8, 14, 20, 0, tzinfo=timezone.utc)

    def supervisor(self, tasks=None, sessions=None, **kwargs):
        self.hcom = FakeHcom(sessions)
        return RecoverySupervisor(
            task_reader=FakeTasks(tasks or [active_task()]),
            hcom=self.hcom,
            recovery_store=self.store,
            backoff_seconds=(60, 120),
            silent_stop_probe_delay_seconds=30,
            **kwargs,
        )

    def schedule_due(self, **changes):
        values = {
            "task_id": "TASK-1",
            "worker_id": "worker-1",
            "session_name": "session-1",
            "reason": "scheduled",
            "resume_after": (self.now - timedelta(seconds=1)).isoformat(),
        }
        values.update(changes)
        return self.store.schedule(**values)

    def test_due_stopped_session_resumes_headlessly(self):
        incident = self.schedule_due()
        sup = self.supervisor(sessions=[{"name": "session-1", "status": "stopped"}])
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["action"], "resume")
        self.assertEqual(self.hcom.resumes, [{"name": "session-1", "headless": True, "terminal": None, "go": True}])
        state = self.store.load()["incidents"][incident.incident_id]
        self.assertEqual(state["attempt"], 1)
        self.assertEqual(state["state"], "probing")

    def test_not_due_does_nothing(self):
        self.schedule_due(resume_after=(self.now + timedelta(minutes=5)).isoformat())
        sup = self.supervisor(sessions=[{"name": "session-1", "status": "stopped"}])
        self.assertEqual(sup.tick(now=self.now), [])
        self.assertEqual(self.hcom.resumes, [])

    def test_live_session_resolves_without_resume(self):
        incident = self.schedule_due()
        sup = self.supervisor(sessions=[{"name": "session-1", "status": "active", "process_bound": True}])
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["action"], "resolve")
        self.assertEqual(self.hcom.resumes, [])
        self.assertEqual(self.store.load()["incidents"][incident.incident_id]["state"], "resolved")

    def test_changed_claim_suppresses(self):
        incident = self.schedule_due()
        sup = self.supervisor(tasks=[active_task("other-worker")], sessions=[])
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["reason"], "claim_changed")
        self.assertEqual(self.store.load()["incidents"][incident.incident_id]["state"], "suppressed")
        self.assertEqual(self.hcom.resumes, [])

    def test_non_active_task_suppresses(self):
        task = active_task()
        task["status"] = "READY_FOR_REVIEW"
        self.schedule_due()
        sup = self.supervisor(tasks=[task], sessions=[])
        self.assertEqual(sup.tick(now=self.now)[0]["reason"], "task_not_active")
        self.assertEqual(self.hcom.resumes, [])

    def test_terminal_session_never_resumes(self):
        incident = self.schedule_due()
        self.store.mark_terminal("session-1", "session_superseded")
        sup = self.supervisor(sessions=[])
        self.assertEqual(sup.tick(now=self.now)[0]["reason"], "terminal_session")
        self.assertEqual(self.store.load()["incidents"][incident.incident_id]["state"], "suppressed")
        self.assertEqual(self.hcom.resumes, [])

    def test_resume_failures_use_capped_retry_budget(self):
        incident = self.schedule_due()
        sup = self.supervisor(sessions=[])
        self.hcom.fail = True
        first = sup.tick(now=self.now)
        self.assertEqual(first[0]["action"], "resume_failed")
        second_time = self.now + timedelta(seconds=61)
        second = sup.tick(now=second_time)
        self.assertEqual(second[0]["action"], "resume_failed")
        third_time = second_time + timedelta(seconds=121)
        third = sup.tick(now=third_time)
        self.assertEqual(third[0]["action"], "fail")
        self.assertEqual(self.store.load()["incidents"][incident.incident_id]["state"], "failed")

    def test_silent_stop_requires_prior_live_and_binding(self):
        sup = self.supervisor(sessions=[{"name": "session-1", "status": "active", "process_bound": True}])
        self.assertEqual(sup.observe_silent_stops({"worker-1": "session-1"}, now=self.now), [])
        self.hcom.sessions = [{"name": "session-1", "status": "stopped", "process_bound": False}]
        opened = sup.observe_silent_stops({"worker-1": "session-1"}, now=self.now + timedelta(seconds=5))
        self.assertEqual(len(opened), 1)
        incident = self.store.load()["incidents"][opened[0]]
        self.assertEqual(incident["reason"], "silent_stop")
        self.assertEqual(incident["task_id"], "TASK-1")

    def test_first_observation_of_dead_session_does_not_invent_incident(self):
        sup = self.supervisor(sessions=[{"name": "session-1", "status": "stopped"}])
        self.assertEqual(sup.observe_silent_stops({"worker-1": "session-1"}, now=self.now), [])
        self.assertEqual(self.store.load()["incidents"], {})

    def test_session_liveness_uses_process_binding_when_present(self):
        self.assertTrue(session_is_live({"status": "listening", "process_bound": True, "status_age_seconds": 99999}))
        self.assertFalse(session_is_live({"status": "listening", "process_bound": False}))
        self.assertFalse(session_is_live({"status": "listening", "status_age_seconds": 2000}))

    def test_recovery_source_contains_no_task_mutations_or_wezterm(self):
        source = Path(__file__).parents[1] / "runtime" / "recovery" / "supervisor.py"
        text = source.read_text(encoding="utf-8")
        for forbidden in (
            "claim_task(",
            "submit_task(",
            "record_review(",
            "promote_ready(",
            "update_contract(",
            "wezterm",
        ):
            self.assertNotIn(forbidden, text.lower())


class FakeEnvironmentReader:
    def __init__(self, evidence=None, *, raise_error=False):
        self.evidence = evidence if evidence is not None else []
        self.raise_error = raise_error
        self.calls = []

    def list_run_environment_evidence(self, run_id):
        self.calls.append(run_id)
        if self.raise_error:
            raise RuntimeError("simulated environment evidence lookup failure")
        return list(self.evidence)


class RecoveryRunBindingAndEvidenceTests(unittest.TestCase):
    """Stage 1 (run_id binding) + Stage 2 Option A (advisory evidence surfacing).

    Per work/notes/2026-08-17-recovery-equivalence-authority-design.md, this is
    explicitly advisory-only: environment evidence must never change a
    recovery decision, only appear alongside it.
    """

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.store = RecoveryStore(Path(self.td.name) / "recovery.json")
        self.now = datetime(2026, 8, 17, 20, 0, tzinfo=timezone.utc)

    def supervisor(self, tasks=None, sessions=None, **kwargs):
        self.hcom = FakeHcom(sessions)
        return RecoverySupervisor(
            task_reader=FakeTasks(tasks or [active_task()]),
            hcom=self.hcom,
            recovery_store=self.store,
            backoff_seconds=(60, 120),
            silent_stop_probe_delay_seconds=30,
            **kwargs,
        )

    def schedule_due(self, **changes):
        values = {
            "task_id": "TASK-1",
            "worker_id": "worker-1",
            "session_name": "session-1",
            "reason": "scheduled",
            "resume_after": (self.now - timedelta(seconds=1)).isoformat(),
        }
        values.update(changes)
        return self.store.schedule(**values)

    def test_run_id_defaults_to_none_when_not_supplied(self):
        incident = self.schedule_due()
        self.assertIsNone(incident.run_id)
        stored = self.store.load()["incidents"][incident.incident_id]
        self.assertIsNone(stored["run_id"])

    def test_run_id_can_be_bound_at_schedule_time(self):
        incident = self.schedule_due(run_id="RUN-1")
        self.assertEqual(incident.run_id, "RUN-1")
        stored = self.store.load()["incidents"][incident.incident_id]
        self.assertEqual(stored["run_id"], "RUN-1")

    def test_no_environment_reader_configured_means_no_evidence_key_populated(self):
        self.schedule_due(run_id="RUN-1")
        sup = self.supervisor(sessions=[{"name": "session-1", "status": "stopped"}])
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["action"], "resume")
        self.assertIsNone(actions[0]["environment_evidence"])

    def test_evidence_absent_without_run_id_even_with_reader_present(self):
        self.schedule_due()  # no run_id
        reader = FakeEnvironmentReader(evidence=[{"compatibility_state": "DRIFTED"}])
        sup = self.supervisor(
            sessions=[{"name": "session-1", "status": "stopped"}],
            environment_reader=reader,
        )
        actions = sup.tick(now=self.now)
        self.assertIsNone(actions[0]["environment_evidence"])
        self.assertEqual(reader.calls, [])

    def test_evidence_surfaced_when_run_id_and_reader_both_present(self):
        self.schedule_due(run_id="RUN-1")
        reader = FakeEnvironmentReader(
            evidence=[{"compatibility_state": "INCOMPATIBLE", "run_id": "RUN-1"}]
        )
        sup = self.supervisor(
            sessions=[{"name": "session-1", "status": "stopped"}],
            environment_reader=reader,
        )
        actions = sup.tick(now=self.now)
        self.assertEqual(reader.calls, ["RUN-1"])
        self.assertEqual(
            actions[0]["environment_evidence"],
            [{"compatibility_state": "INCOMPATIBLE", "run_id": "RUN-1"}],
        )
        # The resume action itself still fired -- evidence is additive only.
        self.assertEqual(actions[0]["action"], "resume")
        self.assertEqual(len(self.hcom.resumes), 1)

    def test_evidence_lookup_failure_does_not_break_tick(self):
        self.schedule_due(run_id="RUN-1")
        reader = FakeEnvironmentReader(raise_error=True)
        sup = self.supervisor(
            sessions=[{"name": "session-1", "status": "stopped"}],
            environment_reader=reader,
        )
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["action"], "resume")
        self.assertIsNone(actions[0]["environment_evidence"])
        self.assertEqual(len(self.hcom.resumes), 1)

    def test_incompatible_evidence_never_changes_the_recovery_decision(self):
        """The core safety property: identical scenario, only evidence differs."""

        def run(reader):
            store = RecoveryStore(Path(self.td.name) / f"recovery-{id(reader)}.json")
            store.schedule(
                task_id="TASK-1",
                worker_id="worker-1",
                session_name="session-1",
                reason="scheduled",
                resume_after=(self.now - timedelta(seconds=1)).isoformat(),
                run_id="RUN-1",
            )
            hcom = FakeHcom(sessions=[{"name": "session-1", "status": "stopped"}])
            sup = RecoverySupervisor(
                task_reader=FakeTasks([active_task()]),
                hcom=hcom,
                recovery_store=store,
                backoff_seconds=(60, 120),
                environment_reader=reader,
            )
            actions = sup.tick(now=self.now)
            return actions, hcom.resumes

        no_evidence_actions, no_evidence_resumes = run(None)
        incompatible_actions, incompatible_resumes = run(
            FakeEnvironmentReader(evidence=[{"compatibility_state": "INCOMPATIBLE"}])
        )

        self.assertEqual(no_evidence_resumes, incompatible_resumes)
        for a, b in zip(no_evidence_actions, incompatible_actions):
            a = dict(a)
            b = dict(b)
            # incident_id is a random uuid4 per schedule() call, distinct
            # across the two independent runs by construction -- not part
            # of the decision this test is verifying.
            del a["environment_evidence"], a["incident_id"]
            del b["environment_evidence"], b["incident_id"]
            self.assertEqual(a, b)


def _lineage_contract(output_path="src"):
    return {
        "title": "Recovery run_id lineage",
        "outcome": "Silent-stop incidents carry an exact run_id when one is bound",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "MEDIUM",
        "decision_authority": "bounded implementation",
        "verification": "recovery supervisor tests",
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
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class RecoveryRunIdResolutionTests(unittest.TestCase):
    """observe_silent_stops resolves run_id via the exact, non-heuristic
    (project_id, adapter_id, session_id) -> run_id reverse lookup on
    `run_session_links` (RunSessionLineageMixin.resolve_session_run), using a
    real TaskStore rather than a fake, so the schema's UNIQUE constraint is
    actually exercised.
    """

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        self.task_store = TaskStore(self.root / "maps.db")
        self.recovery_store = RecoveryStore(self.root / "recovery.json")
        self.now = datetime(2026, 8, 17, 20, 0, tzinfo=timezone.utc)

    def make_active_run(self, *, worker="worker-1", session_id="sess-1"):
        created = self.task_store.create_task(title="x", project_id="proj-1")
        self.assertTrue(created.ok)
        task_id = created.task["task_id"]
        self.assertTrue(
            self.task_store.update_contract(task_id, _lineage_contract()).ok
        )
        self.assertTrue(self.task_store.promote_ready(task_id).ok)
        self.assertTrue(
            self.task_store.claim_task(task_id, worker, lease_seconds=600).ok
        )
        writable_paths = self.task_store.get_task(task_id)["output_paths"]
        manifest = self.task_store.create_run_manifest(
            task_id,
            worker,
            repo_root=self.repo,
            created_by="dispatcher",
            readable_paths=["."],
            writable_paths=writable_paths,
        )
        self.assertTrue(manifest.ok, manifest.message)
        run_id = manifest.task["run_id"]
        link = self.task_store.record_run_session_link(
            run_id,
            worker,
            adapter_id="hcom",
            session_id=session_id,
            evidence_ref=f"provider:event:{session_id}",
            created_by="dispatcher",
        )
        self.assertTrue(link.ok, link.message)
        return task_id, run_id

    def supervisor(self, sessions):
        self.hcom = FakeHcom(sessions)
        return RecoverySupervisor(
            task_reader=self.task_store,
            hcom=self.hcom,
            recovery_store=self.recovery_store,
            backoff_seconds=(60, 120),
            silent_stop_probe_delay_seconds=30,
        )

    def test_silent_stop_binds_exact_run_id_via_reverse_session_lookup(self):
        task_id, run_id = self.make_active_run(worker="worker-1", session_id="sess-1")
        sup = self.supervisor(
            sessions=[
                {
                    "name": "session-1",
                    "session_id": "sess-1",
                    "status": "active",
                    "process_bound": True,
                }
            ]
        )
        self.assertEqual(
            sup.observe_silent_stops({"worker-1": "session-1"}, now=self.now), []
        )
        self.hcom.sessions = [
            {
                "name": "session-1",
                "session_id": "sess-1",
                "status": "stopped",
                "process_bound": False,
            }
        ]
        opened = sup.observe_silent_stops(
            {"worker-1": "session-1"}, now=self.now + timedelta(seconds=5)
        )
        self.assertEqual(len(opened), 1)
        incident = self.recovery_store.load()["incidents"][opened[0]]
        self.assertEqual(incident["task_id"], task_id)
        self.assertEqual(incident["run_id"], run_id)

    def test_silent_stop_leaves_run_id_none_when_no_matching_link(self):
        # A task/run exists, but the hcom session_id observed at stop time
        # does not match any run_session_links row for this project/adapter --
        # e.g. the session was never durably attached. No exact match exists,
        # so resolution must not guess; it must return None without raising.
        task_id, _run_id = self.make_active_run(worker="worker-1", session_id="sess-1")
        sup = self.supervisor(
            sessions=[
                {
                    "name": "session-1",
                    "session_id": "sess-unbound",
                    "status": "active",
                    "process_bound": True,
                }
            ]
        )
        self.assertEqual(
            sup.observe_silent_stops({"worker-1": "session-1"}, now=self.now), []
        )
        self.hcom.sessions = [
            {
                "name": "session-1",
                "session_id": "sess-unbound",
                "status": "stopped",
                "process_bound": False,
            }
        ]
        opened = sup.observe_silent_stops(
            {"worker-1": "session-1"}, now=self.now + timedelta(seconds=5)
        )
        self.assertEqual(len(opened), 1)
        incident = self.recovery_store.load()["incidents"][opened[0]]
        self.assertEqual(incident["task_id"], task_id)
        self.assertIsNone(incident["run_id"])

    def test_silent_stop_leaves_run_id_none_when_hcom_session_lacks_session_id(self):
        # hcom's own `name` field must never be substituted for its distinct
        # `session_id` field -- if the session record has no session_id at
        # all, resolution must decline rather than looking up by name.
        task_id, _run_id = self.make_active_run(worker="worker-1", session_id="sess-1")
        sup = self.supervisor(
            sessions=[{"name": "session-1", "status": "active", "process_bound": True}]
        )
        self.assertEqual(
            sup.observe_silent_stops({"worker-1": "session-1"}, now=self.now), []
        )
        self.hcom.sessions = [
            {"name": "session-1", "status": "stopped", "process_bound": False}
        ]
        opened = sup.observe_silent_stops(
            {"worker-1": "session-1"}, now=self.now + timedelta(seconds=5)
        )
        self.assertEqual(len(opened), 1)
        incident = self.recovery_store.load()["incidents"][opened[0]]
        self.assertEqual(incident["task_id"], task_id)
        self.assertIsNone(incident["run_id"])

    def make_active_run_without_link(self, *, worker="worker-1"):
        created = self.task_store.create_task(title="x", project_id="proj-1")
        self.assertTrue(created.ok)
        task_id = created.task["task_id"]
        self.assertTrue(
            self.task_store.update_contract(task_id, _lineage_contract()).ok
        )
        self.assertTrue(self.task_store.promote_ready(task_id).ok)
        self.assertTrue(
            self.task_store.claim_task(task_id, worker, lease_seconds=600).ok
        )
        writable_paths = self.task_store.get_task(task_id)["output_paths"]
        manifest = self.task_store.create_run_manifest(
            task_id,
            worker,
            repo_root=self.repo,
            created_by="dispatcher",
            readable_paths=["."],
            writable_paths=writable_paths,
        )
        self.assertTrue(manifest.ok, manifest.message)
        return task_id, manifest.task["run_id"], manifest.task["task_revision"]

    def test_silent_stop_binds_run_id_written_via_hcom_harness_adapter_attach(self):
        # Proves the reader (resolve_session_run, consumed here) is actually
        # reachable end to end from the writer HcomHarnessAdapter.attach()
        # now calls -- not just independently correct in isolation.
        task_id, run_id, task_revision = self.make_active_run_without_link(
            worker="worker-1"
        )
        adapter = HcomHarnessAdapter(
            FakeHcom([]), project_id="proj-1", lineage_writer=self.task_store
        )
        binding = ExecutionBinding(
            task_id=task_id,
            run_id=run_id,
            worker_id="worker-1",
            task_revision=task_revision,
            project_id="proj-1",
            session_id="sess-1",
        )
        session_ref = SessionRef(
            session_id="sess-1",
            worker_id="worker-1",
            adapter="hcom",
            project_id="proj-1",
            remote_ref="session-1",
        )
        attach_result = adapter.attach(binding, session_ref)
        self.assertTrue(attach_result.ok, attach_result.summary)

        sup = self.supervisor(
            sessions=[
                {
                    "name": "session-1",
                    "session_id": "sess-1",
                    "status": "active",
                    "process_bound": True,
                }
            ]
        )
        self.assertEqual(
            sup.observe_silent_stops({"worker-1": "session-1"}, now=self.now), []
        )
        self.hcom.sessions = [
            {
                "name": "session-1",
                "session_id": "sess-1",
                "status": "stopped",
                "process_bound": False,
            }
        ]
        opened = sup.observe_silent_stops(
            {"worker-1": "session-1"}, now=self.now + timedelta(seconds=5)
        )
        self.assertEqual(len(opened), 1)
        incident = self.recovery_store.load()["incidents"][opened[0]]
        self.assertEqual(incident["task_id"], task_id)
        self.assertEqual(incident["run_id"], run_id)


class FakeHarnessServiceResume:
    """Duck-typed HarnessService stand-in exposing only resume(binding, session_ref)."""

    def __init__(self, *, raise_error=False, result=None):
        self.raise_error = raise_error
        self.result = result
        self.calls = []

    def resume(self, binding, session_ref):
        self.calls.append((binding, session_ref))
        if self.raise_error:
            raise RuntimeError("simulated harness resume failure")
        if self.result is not None:
            return self.result
        return OperationResult.success(
            "SESSION_RESUMED", "hcom resume request completed.", mutated=True
        )


class RecoveryHarnessResumeCallSiteTests(unittest.TestCase):
    """RnS harness resume production call site.

    Per work/notes/2026-08-21-rns-harness-validation-callsite-design.md, this
    is the first behavior-changing production call site: tick()'s resume
    attempt is routed through HarnessService.resume() (via the real,
    already-implemented HcomHarnessAdapter) instead of the direct
    self.hcom.resume(...) call, whenever the incident's existing
    session/run lineage lets a real ExecutionBinding/SessionRef be built.
    Behavior is preserved for every outcome except an explicit canonical-run
    denial (a real, installed CANONICAL_RUN Hook actively denying) -- see
    work/tasks/rns-harness-resume-callsite.md's Decisions section. Uses a
    real TaskStore so the durable run/session lineage lookup
    (resolve_run_session) is actually exercised, not faked.
    """

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        self.task_store = TaskStore(self.root / "maps.db")
        self.recovery_store = RecoveryStore(self.root / "recovery.json")
        self.now = datetime(2026, 8, 19, 20, 0, tzinfo=timezone.utc)

    def make_bound_run(self, *, worker="worker-1", session_id="sess-1", attach=True):
        created = self.task_store.create_task(title="x", project_id="proj-1")
        self.assertTrue(created.ok)
        task_id = created.task["task_id"]
        self.assertTrue(
            self.task_store.update_contract(task_id, _lineage_contract()).ok
        )
        self.assertTrue(self.task_store.promote_ready(task_id).ok)
        self.assertTrue(
            self.task_store.claim_task(task_id, worker, lease_seconds=600).ok
        )
        writable_paths = self.task_store.get_task(task_id)["output_paths"]
        manifest = self.task_store.create_run_manifest(
            task_id,
            worker,
            repo_root=self.repo,
            created_by="dispatcher",
            readable_paths=["."],
            writable_paths=writable_paths,
        )
        self.assertTrue(manifest.ok, manifest.message)
        run_id = manifest.task["run_id"]
        if attach:
            adapter = HcomHarnessAdapter(
                FakeHcom([]), project_id="proj-1", lineage_writer=self.task_store
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
            attach_result = adapter.attach(binding, session_ref)
            self.assertTrue(attach_result.ok, attach_result.summary)
        return task_id, run_id

    def schedule_due(self, *, task_id, worker_id="worker-1", session_name="session-1", run_id=None, store=None):
        store = store or self.recovery_store
        return store.schedule(
            task_id=task_id,
            worker_id=worker_id,
            session_name=session_name,
            reason="scheduled",
            resume_after=(self.now - timedelta(seconds=1)).isoformat(),
            run_id=run_id,
        )

    def supervisor(self, sessions, *, store=None, **kwargs):
        self.hcom = FakeHcom(sessions)
        return RecoverySupervisor(
            task_reader=self.task_store,
            hcom=self.hcom,
            recovery_store=store or self.recovery_store,
            backoff_seconds=(60, 120),
            silent_stop_probe_delay_seconds=30,
            **kwargs,
        )

    def test_no_harness_service_configured_direct_resume_unchanged(self):
        """Not configured: tick() behaves identically to before this task, key is None."""
        task_id, run_id = self.make_bound_run()
        self.schedule_due(task_id=task_id, run_id=run_id)
        sup = self.supervisor(sessions=[{"name": "session-1", "status": "stopped"}])
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["action"], "resume")
        self.assertIsNone(actions[0]["harness_resume"])
        self.assertEqual(len(self.hcom.resumes), 1)

    def test_missing_run_binding_falls_back_to_direct_resume(self):
        """Configured but no run_id bound: harness path can't be built, direct resume proceeds unchanged."""
        task_id, _run_id = self.make_bound_run()
        self.schedule_due(task_id=task_id, run_id=None)
        harness = FakeHarnessServiceResume()
        sup = self.supervisor(
            sessions=[{"name": "session-1", "status": "stopped"}],
            harness_service=harness,
        )
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["action"], "resume")
        self.assertEqual(
            actions[0]["harness_resume"],
            {"attempted": False, "reason": "no_run_id_bound"},
        )
        self.assertEqual(harness.calls, [])
        self.assertEqual(len(self.hcom.resumes), 1)

    def test_ambiguous_binding_falls_back_to_direct_resume(self):
        """Run bound but no durable hcom session lineage: same fallback as a missing run_id."""
        task_id, run_id = self.make_bound_run(attach=False)
        self.schedule_due(task_id=task_id, run_id=run_id)
        harness = FakeHarnessServiceResume()
        sup = self.supervisor(
            sessions=[{"name": "session-1", "status": "stopped"}],
            harness_service=harness,
        )
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["action"], "resume")
        self.assertEqual(
            actions[0]["harness_resume"],
            {"attempted": False, "reason": "session_not_durably_bound"},
        )
        self.assertEqual(harness.calls, [])
        self.assertEqual(len(self.hcom.resumes), 1)

    def test_successful_resume_routes_through_harness_adapter_not_direct_path(self):
        """Binding constructible: resume reaches hcom via the real HcomHarnessAdapter, not self.hcom directly."""
        task_id, run_id = self.make_bound_run(attach=True)
        self.schedule_due(task_id=task_id, run_id=run_id)

        harness_backend = FakeHcom(sessions=[{"name": "session-1", "status": "stopped", "session_id": "sess-1"}])
        adapter = HcomHarnessAdapter(harness_backend, project_id="proj-1", lineage_writer=self.task_store)
        hooks = HookRegistry()
        register_canonical_run_guards(
            hooks, CanonicalRunGuard(self.task_store, repo_root=self.repo)
        )
        harness_service = HarnessService([adapter], hooks=hooks)

        # self.hcom below is the direct-path adapter passed to RecoverySupervisor;
        # it must never be called once the harness path succeeds.
        sup = self.supervisor(sessions=[], harness_service=harness_service)
        actions = sup.tick(now=self.now)

        self.assertEqual(actions[0]["action"], "resume")
        self.assertEqual(actions[0]["error"], "")
        self.assertEqual(
            actions[0]["harness_resume"],
            {
                "attempted": True,
                "ok": True,
                "code": "SESSION_RESUMED",
                "summary": "hcom resume request completed.",
            },
        )
        # The real hcom call happened exactly once, through the harness
        # adapter's own backend, with the same headless/go intent the direct
        # path used to send -- and the direct path was never invoked.
        self.assertEqual(
            harness_backend.resumes,
            [{"name": "session-1", "headless": True, "terminal": None, "go": True}],
        )
        self.assertEqual(self.hcom.resumes, [])

    def test_canonical_run_denial_surfaces_in_evidence_without_direct_fallback(self):
        """An explicit canonical-run denial (HOOK_DENIED) is surfaced and does not fall back."""
        task_id, run_id = self.make_bound_run(attach=True)
        self.schedule_due(task_id=task_id, run_id=run_id)
        denial = OperationResult.failure(
            "HOOK_DENIED", "Deterministic Hook denied the operation."
        )
        harness = FakeHarnessServiceResume(result=denial)
        sup = self.supervisor(
            sessions=[{"name": "session-1", "status": "stopped"}],
            harness_service=harness,
        )
        actions = sup.tick(now=self.now)
        self.assertEqual(len(harness.calls), 1)
        self.assertEqual(actions[0]["action"], "resume_denied")
        self.assertEqual(actions[0]["error"], "Deterministic Hook denied the operation.")
        self.assertEqual(
            actions[0]["harness_resume"],
            {
                "attempted": True,
                "ok": False,
                "code": "HOOK_DENIED",
                "summary": "Deterministic Hook denied the operation.",
            },
        )
        # No task-truth mutation and no direct-path resume: a denial is a
        # real behavior change from the pre-existing direct call, and it is
        # the only such change this call site makes.
        self.assertEqual(self.hcom.resumes, [])
        incident_id = actions[0]["incident_id"]
        stored = self.recovery_store.load()["incidents"][incident_id]
        # A canonical denial parks the incident in a distinct `denied` state
        # carrying the deny code -- NOT `probing` laundered through the
        # transient retry ladder.
        self.assertEqual(stored["state"], "denied")
        self.assertEqual(stored["last_error"], "Deterministic Hook denied the operation.")
        # The transient retry attempt counter is UNTOUCHED; the denial is
        # tracked on its own separate counter instead.
        self.assertEqual(stored["attempt"], 0)
        self.assertEqual(actions[0]["attempt"], 0)
        self.assertEqual(stored["canonical_denials"], 1)
        # Rescheduled on the flat silent-stop probe interval (30s in this
        # fixture), not the escalating backoff ladder (60s, 120s).
        self.assertEqual(
            parse_time(stored["next_attempt_at"]),
            self.now + timedelta(seconds=30),
        )

    def test_canonical_denial_does_not_consume_transient_retry_budget(self):
        """Repeated canonical denials never reach `retry_budget_exhausted`; they
        hit their own separate `canonical_denial_persistent` ceiling instead,
        and the transient `attempt` counter stays at 0 throughout."""
        task_id, run_id = self.make_bound_run(attach=True)
        self.schedule_due(task_id=task_id, run_id=run_id)
        denial = OperationResult.failure("HOOK_DENIED", "LEASE_EXPIRED: claim lease has expired")
        harness = FakeHarnessServiceResume(result=denial)
        sup = self.supervisor(
            sessions=[{"name": "session-1", "status": "stopped"}],
            harness_service=harness,
        )
        incident_id = None
        # backoff_seconds=(60, 120) -> transient budget is 2. The ceiling for
        # consecutive canonical denials is _MAX_CONSECUTIVE_CANONICAL_DENIALS
        # (3), which is deliberately independent of that budget.
        for i in range(2):
            actions = sup.tick(now=self.now + timedelta(seconds=60 * i))
            incident_id = actions[0]["incident_id"]
            self.assertEqual(actions[0]["action"], "resume_denied")
            stored = self.recovery_store.load()["incidents"][incident_id]
            self.assertEqual(stored["state"], "denied")
            self.assertEqual(stored["attempt"], 0)
            self.assertEqual(stored["canonical_denials"], i + 1)

        # Third consecutive denial hits the canonical ceiling -> a distinct
        # terminal code, NOT retry_budget_exhausted.
        actions = sup.tick(now=self.now + timedelta(seconds=600))
        self.assertEqual(actions[0]["action"], "fail")
        self.assertEqual(actions[0]["reason"], "canonical_denial_persistent")
        stored = self.recovery_store.load()["incidents"][incident_id]
        self.assertEqual(stored["state"], "failed")
        self.assertEqual(stored["last_error"], "canonical_denial_persistent")
        self.assertEqual(stored["attempt"], 0)
        self.assertEqual(self.hcom.resumes, [])

    def test_canonical_denial_streak_resets_on_a_non_denied_outcome(self):
        """A `denied` incident that later resumes cleanly clears its denial
        streak and returns to normal `probing`/`resolved` handling."""
        task_id, run_id = self.make_bound_run(attach=True)
        self.schedule_due(task_id=task_id, run_id=run_id)
        harness = FakeHarnessServiceResume(
            result=OperationResult.failure("HOOK_DENIED", "denied once")
        )
        sup = self.supervisor(
            sessions=[{"name": "session-1", "status": "stopped"}],
            harness_service=harness,
        )
        actions = sup.tick(now=self.now)
        incident_id = actions[0]["incident_id"]
        self.assertEqual(self.recovery_store.load()["incidents"][incident_id]["canonical_denials"], 1)

        # Next tick: the guard now allows the resume.
        harness.result = OperationResult.success(
            "SESSION_RESUMED", "hcom resume request completed.", mutated=True
        )
        actions = sup.tick(now=self.now + timedelta(seconds=60))
        self.assertEqual(actions[0]["action"], "resume")
        stored = self.recovery_store.load()["incidents"][incident_id]
        self.assertEqual(stored["canonical_denials"], 0)
        self.assertEqual(stored["state"], "probing")
        self.assertEqual(stored["attempt"], 1)

    def test_non_canonical_retry_budget_exhausted_still_fires(self):
        """A genuine transient failure (not a canonical denial) still consumes
        the transient budget and terminates as retry_budget_exhausted."""
        task_id, run_id = self.make_bound_run(attach=True)
        self.schedule_due(task_id=task_id, run_id=run_id)
        # No harness_service -> the direct hcom path; make it fail every time.
        self.hcom = FakeHcom([{"name": "session-1", "status": "stopped"}])
        self.hcom.fail = True
        sup = RecoverySupervisor(
            task_reader=self.task_store,
            hcom=self.hcom,
            recovery_store=self.recovery_store,
            backoff_seconds=(60, 120),
            silent_stop_probe_delay_seconds=30,
        )
        a1 = sup.tick(now=self.now)
        self.assertEqual(a1[0]["action"], "resume_failed")
        a2 = sup.tick(now=self.now + timedelta(seconds=120))
        self.assertEqual(a2[0]["action"], "resume_failed")
        a3 = sup.tick(now=self.now + timedelta(seconds=600))
        self.assertEqual(a3[0]["action"], "fail")
        self.assertEqual(a3[0]["reason"], "retry_budget_exhausted")
        stored = self.recovery_store.load()["incidents"][a3[0]["incident_id"]]
        self.assertEqual(stored["last_error"], "retry_budget_exhausted")

    def test_missing_canonical_guard_falls_back_to_direct_resume(self):
        """CANONICAL_GUARD_REQUIRED (no CANONICAL_RUN Hook installed) is not a concrete
        mismatch -- it falls back to direct resume instead of denying."""
        task_id, run_id = self.make_bound_run(attach=True)
        self.schedule_due(task_id=task_id, run_id=run_id)
        no_guard = OperationResult.failure(
            "CANONICAL_GUARD_REQUIRED",
            "Consequential harness operation requires canonical run enforcement.",
        )
        harness = FakeHarnessServiceResume(result=no_guard)
        sup = self.supervisor(
            sessions=[{"name": "session-1", "status": "stopped"}],
            harness_service=harness,
        )
        actions = sup.tick(now=self.now)
        self.assertEqual(len(harness.calls), 1)
        self.assertEqual(actions[0]["action"], "resume")
        self.assertEqual(actions[0]["error"], "")
        self.assertEqual(
            actions[0]["harness_resume"],
            {
                "attempted": True,
                "ok": False,
                "code": "CANONICAL_GUARD_REQUIRED",
                "summary": "Consequential harness operation requires canonical run enforcement.",
            },
        )
        self.assertEqual(len(self.hcom.resumes), 1)

    def test_harness_call_exception_falls_back_to_direct_resume(self):
        """The real resume attempt still completes if calling the harness_service raises."""
        task_id, run_id = self.make_bound_run(attach=True)
        self.schedule_due(task_id=task_id, run_id=run_id)
        harness = FakeHarnessServiceResume(raise_error=True)
        sup = self.supervisor(
            sessions=[{"name": "session-1", "status": "stopped"}],
            harness_service=harness,
        )
        actions = sup.tick(now=self.now)
        self.assertEqual(len(harness.calls), 1)
        self.assertEqual(actions[0]["action"], "resume")
        self.assertEqual(actions[0]["error"], "")
        self.assertEqual(
            actions[0]["harness_resume"],
            {
                "attempted": True,
                "ok": False,
                "code": "HARNESS_CALL_ERROR",
                "summary": "simulated harness resume failure",
            },
        )
        self.assertEqual(len(self.hcom.resumes), 1)

    def test_environment_evidence_unaffected_by_harness_routing(self):
        """_advisory_environment_evidence's behavior is untouched by this task."""
        task_id, run_id = self.make_bound_run(attach=True)
        self.schedule_due(task_id=task_id, run_id=run_id)
        reader = FakeEnvironmentReader(evidence=[{"kind": "note", "detail": "ok"}])
        harness = FakeHarnessServiceResume()
        sup = self.supervisor(
            sessions=[{"name": "session-1", "status": "stopped"}],
            environment_reader=reader,
            harness_service=harness,
        )
        actions = sup.tick(now=self.now)
        self.assertEqual(reader.calls, [run_id])
        self.assertEqual(
            actions[0]["environment_evidence"], [{"kind": "note", "detail": "ok"}]
        )
        self.assertEqual(actions[0]["action"], "resume")

    def test_no_validation_tier_commands_or_task_mutation_in_source(self):
        """No validation-tier wiring or task-truth mutation was introduced by this task."""
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


class RecordingValidator:
    """Minimal `resume_validator` stand-in: records run_ids, returns a fixed dict."""

    def __init__(self, result=None, *, error=None):
        self.result = result
        self.error = error
        self.calls: list = []

    def validate_for_run(self, run_id):
        self.calls.append(run_id)
        if self.error is not None:
            raise self.error
        return self.result


FAILING_VALIDATION = {
    "attempted": True,
    "passed": False,
    "tier": "quick",
    "environment_spec_hash": "f" * 64,
    "result": {
        "tier": "quick",
        "environment_spec_hash": "f" * 64,
        "passed": False,
        "ran": [
            {
                "command": "pytest -q",
                "found": True,
                "returncode": 1,
                "output": "1 failed",
                "passed": False,
            }
        ],
        "skipped": [],
    },
}


class ResumeValidationAdvisoryTests(unittest.TestCase):
    """The `resume_validator` observation point is advisory and never gates a resume.

    Per `work/notes/2026-08-25-rns-validation-tier-hookin-design.md` Q1/Q6/Q8.
    """

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.now = datetime(2026, 8, 25, 20, 0, tzinfo=timezone.utc)
        self.counter = 0

    def supervisor(self, *, sessions=None, tasks=None, **kwargs):
        # A fresh store per supervisor so a control run and a validated run
        # start from byte-identical incident state.
        self.counter += 1
        store = RecoveryStore(Path(self.td.name) / f"recovery-{self.counter}.json")
        store.schedule(
            task_id="TASK-1",
            worker_id="worker-1",
            session_name="session-1",
            reason="scheduled",
            resume_after=(self.now - timedelta(seconds=1)).isoformat(),
            run_id="RUN-1",
        )
        hcom = FakeHcom(
            sessions
            if sessions is not None
            else [{"name": "session-1", "status": "stopped"}]
        )
        sup = RecoverySupervisor(
            task_reader=FakeTasks(tasks or [active_task()]),
            hcom=hcom,
            recovery_store=store,
            backoff_seconds=(60, 120),
            silent_stop_probe_delay_seconds=30,
            **kwargs,
        )
        return sup, hcom, store

    @staticmethod
    def _bookkeeping(action, state):
        incident = next(iter(state["incidents"].values()))
        return (
            action["action"],
            action["attempt"],
            action["error"],
            incident["state"],
            incident["last_error"],
            incident["next_attempt_at"],
            incident["attempt"],
        )

    def test_no_validator_configured_leaves_the_key_none_everywhere(self):
        """Default (no validator): every action dict carries resume_validation=None."""
        sup, hcom, _store = self.supervisor()
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["action"], "resume")
        self.assertIsNone(actions[0]["resume_validation"])
        self.assertEqual(len(hcom.resumes), 1)

    def test_a_failing_validation_changes_nothing_about_the_resume(self):
        """Q1: a failed quick tier is flagged, and the resume proceeds identically."""
        control_sup, control_hcom, control_store = self.supervisor()
        control_actions = control_sup.tick(now=self.now)
        control = self._bookkeeping(control_actions[0], control_store.load())

        validator = RecordingValidator(FAILING_VALIDATION)
        sup, hcom, store = self.supervisor(resume_validator=validator)
        actions = sup.tick(now=self.now)

        # The failure is genuinely observed...
        self.assertEqual(validator.calls, ["RUN-1"])
        self.assertEqual(actions[0]["resume_validation"], FAILING_VALIDATION)
        self.assertIs(actions[0]["resume_validation"]["passed"], False)
        # ...and changes nothing at all about the resume or the bookkeeping.
        self.assertEqual(self._bookkeeping(actions[0], store.load()), control)
        self.assertEqual(hcom.resumes, control_hcom.resumes)
        self.assertEqual(len(hcom.resumes), 1)

    def test_a_passing_validation_is_recorded_on_the_resume_action(self):
        passing = {"attempted": True, "passed": True, "tier": "quick"}
        validator = RecordingValidator(passing)
        sup, hcom, _store = self.supervisor(resume_validator=validator)
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["resume_validation"], passing)
        self.assertEqual(len(hcom.resumes), 1)

    def test_a_skip_result_is_passed_through_verbatim(self):
        """The common production case: no run-bound spec exists, so nothing ran."""
        skip = {"attempted": False, "reason": "no_spec_bound"}
        validator = RecordingValidator(skip)
        sup, _hcom, _store = self.supervisor(resume_validator=validator)
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["resume_validation"], skip)
        self.assertNotIn("passed", actions[0]["resume_validation"])

    def test_an_exploding_validator_cannot_break_the_tick(self):
        """Q6: contained, reported as validation_error, resume still happens."""
        validator = RecordingValidator(
            error=RuntimeError("token=sk-live-abcdef1234567890")
        )
        sup, hcom, _store = self.supervisor(resume_validator=validator)
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["action"], "resume")
        self.assertEqual(
            actions[0]["resume_validation"],
            {"attempted": False, "reason": "validation_error"},
        )
        # Caller-supplied exception text is deliberately not propagated: it has
        # not passed through any redaction boundary this module controls.
        self.assertNotIn("sk-live", repr(actions[0]))
        self.assertEqual(len(hcom.resumes), 1)

    def test_a_hcom_resume_failure_still_records_the_validation(self):
        validator = RecordingValidator(FAILING_VALIDATION)
        sup, hcom, _store = self.supervisor(resume_validator=validator)
        hcom.fail = True
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["action"], "resume_failed")
        self.assertEqual(actions[0]["resume_validation"], FAILING_VALIDATION)

    def test_suppressed_incident_runs_no_validation(self):
        """Q8: a suppressed incident carries resume_validation=None and calls nothing."""
        validator = RecordingValidator(FAILING_VALIDATION)
        sup, _hcom, _store = self.supervisor(
            tasks=[dict(active_task(), status="DONE")], resume_validator=validator
        )
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["action"], "suppress")
        self.assertIsNone(actions[0]["resume_validation"])
        self.assertEqual(validator.calls, [])

    def test_resolved_incident_runs_no_validation(self):
        validator = RecordingValidator(FAILING_VALIDATION)
        sup, _hcom, _store = self.supervisor(
            sessions=[{"name": "session-1", "status": "active", "process_bound": True}],
            resume_validator=validator,
        )
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["action"], "resolve")
        self.assertIsNone(actions[0]["resume_validation"])
        self.assertEqual(validator.calls, [])

    def test_retry_budget_exhausted_incident_runs_no_validation(self):
        validator = RecordingValidator(FAILING_VALIDATION)
        sup, _hcom, store = self.supervisor(resume_validator=validator)
        state = store.load()
        for incident in state["incidents"].values():
            incident["attempt"] = 2
        store.save(state)
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["action"], "fail")
        self.assertIsNone(actions[0]["resume_validation"])
        self.assertEqual(validator.calls, [])

    def test_not_yet_due_incident_runs_no_validation(self):
        validator = RecordingValidator(FAILING_VALIDATION)
        sup, _hcom, _store = self.supervisor(resume_validator=validator)
        actions = sup.tick(now=self.now - timedelta(hours=1))
        self.assertEqual(actions, [])
        self.assertEqual(validator.calls, [])

    def test_validator_receives_the_incidents_own_bound_run_id(self):
        """No ambient run: the validator only ever sees the incident's own run_id."""
        validator = RecordingValidator({"attempted": False, "reason": "no_spec_bound"})
        sup, _hcom, store = self.supervisor(resume_validator=validator)
        state = store.load()
        for incident in state["incidents"].values():
            incident["run_id"] = None
        store.save(state)
        sup.tick(now=self.now)
        self.assertEqual(validator.calls, [None])


class SupervisorSourceBoundaryTests(unittest.TestCase):
    def test_supervisor_source_never_names_the_declared_environment_spec_type(self):
        """`runtime/recovery/supervisor.py` must not contain the literal "EnvironmentSpec".

        This is the honest description of what the #160 guard
        (`test_no_validation_tier_commands_or_task_mutation_in_source`) checks:
        a lowercased substring scan over the *entire* source text -- code,
        comments and docstrings alike -- not an import check. Documenting the
        new `resume_validator` input the way `environment_reader` is
        documented, by naming the type it ultimately validates against, would
        turn both tests red with no import present anywhere, which is exactly
        why that input is specified by interface only. Stating the rule in the
        terms the guard actually enforces means a future edit that reintroduces
        the name in prose fails for a reason someone can read.
        """
        source = Path(__file__).parents[1] / "runtime" / "recovery" / "supervisor.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("EnvironmentSpec", text)
        self.assertNotIn("environmentspec", text.lower())
        # The composition root is allowed -- and required -- to name it, so the
        # assertion above is a real boundary rather than vacuously true.
        composition_root = (
            Path(__file__).parents[1] / "runtime" / "recovery" / "production.py"
        )
        self.assertIn("EnvironmentSpec", composition_root.read_text(encoding="utf-8"))

    def test_resume_validator_is_an_optional_keyword_only_input_defaulting_to_none(self):
        import inspect

        params = inspect.signature(RecoverySupervisor.__init__).parameters
        self.assertIn("resume_validator", params)
        self.assertEqual(params["resume_validator"].kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertIsNone(params["resume_validator"].default)


if __name__ == "__main__":
    unittest.main()
