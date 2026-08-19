from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from runtime.communication import HcomError
from runtime.harness import ExecutionBinding, OperationResult, SessionRef
from runtime.harness.adapters import HcomHarnessAdapter
from runtime.recovery import RecoveryStore, RecoverySupervisor, session_is_live
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


class RecoveryHarnessResumeShadowTests(unittest.TestCase):
    """Shadow-only harness resume observation (Option B shadow instrumentation).

    Per work/notes/2026-08-19-harness-production-wiring-gap.md (Option B
    recommendation) and work/reviews/pr-119-review-evidence.md's "Second
    opinion on Option B recommendation" (an explicit shadow-mode step before
    RnS's automated retry loop depends on the harness path), this must be
    provably shadow-only: never consulted by any branch in tick() to make or
    change a recovery decision. Uses a real TaskStore so the durable
    run/session lineage lookup (resolve_run_session) is actually exercised,
    not faked.
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

    def test_no_harness_service_configured_leaves_shadow_key_none(self):
        """(a) Not configured: tick() behaves identically, shadow key is None."""
        task_id, run_id = self.make_bound_run()
        self.schedule_due(task_id=task_id, run_id=run_id)
        sup = self.supervisor(sessions=[{"name": "session-1", "status": "stopped"}])
        actions = sup.tick(now=self.now)
        self.assertEqual(actions[0]["action"], "resume")
        self.assertIsNone(actions[0]["harness_resume_shadow"])
        self.assertEqual(len(self.hcom.resumes), 1)

    def test_no_run_id_bound_reports_not_attempted_real_resume_unaffected(self):
        """(b) Configured but no run_id bound: honest 'not attempted', real resume proceeds."""
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
            actions[0]["harness_resume_shadow"],
            {"attempted": False, "reason": "no_run_id_bound"},
        )
        self.assertEqual(harness.calls, [])
        self.assertEqual(len(self.hcom.resumes), 1)

    def test_harness_path_raises_but_real_resume_completes_identically(self):
        """(c) The core safety proof.

        Identical scenario run twice, differing only in whether a
        harness_service is configured and raises on resume(). The real
        hcom resume call, the resulting action/error/state transition, and
        the incident's persisted state must be byte-for-byte identical
        (aside from the shadow key itself and the per-run incident_id) --
        proving the shadow call never gates the real decision, empirically.
        """
        task_id, run_id = self.make_bound_run(attach=True)

        def run(harness_service):
            store = RecoveryStore(self.root / f"recovery-{id(harness_service)}.json")
            self.schedule_due(task_id=task_id, run_id=run_id, store=store)
            hcom = FakeHcom(sessions=[{"name": "session-1", "status": "stopped"}])
            sup = RecoverySupervisor(
                task_reader=self.task_store,
                hcom=hcom,
                recovery_store=store,
                backoff_seconds=(60, 120),
                harness_service=harness_service,
            )
            actions = sup.tick(now=self.now)
            incidents = store.load()["incidents"]
            return actions, hcom.resumes, incidents

        no_shadow_actions, no_shadow_resumes, no_shadow_incidents = run(None)
        failing_harness = FakeHarnessServiceResume(raise_error=True)
        failing_actions, failing_resumes, failing_incidents = run(failing_harness)

        # The shadow path was actually attempted and did raise -- otherwise
        # this test would not be exercising the property it claims to prove.
        self.assertEqual(len(failing_harness.calls), 1)

        self.assertEqual(no_shadow_resumes, failing_resumes)
        self.assertEqual(len(failing_resumes), 1)

        for a, b in zip(no_shadow_actions, failing_actions):
            a = dict(a)
            b = dict(b)
            del a["harness_resume_shadow"], a["incident_id"]
            del b["harness_resume_shadow"], b["incident_id"]
            self.assertEqual(a, b)

        self.assertEqual(failing_actions[0]["action"], "resume")
        self.assertEqual(failing_actions[0]["error"], "")
        self.assertEqual(
            failing_actions[0]["harness_resume_shadow"],
            {"attempted": False, "reason": "shadow_lookup_error"},
        )

        for no_shadow_incident, failing_incident in zip(
            no_shadow_incidents.values(), failing_incidents.values()
        ):
            no_shadow_incident = dict(no_shadow_incident)
            failing_incident = dict(failing_incident)
            # incident_id is a random uuid4 per schedule() call, distinct
            # across the two independent runs by construction -- not part
            # of the decision/state this test is verifying.
            del no_shadow_incident["incident_id"], failing_incident["incident_id"]
            self.assertEqual(no_shadow_incident, failing_incident)

    def test_harness_resume_shadow_observes_success_without_affecting_real_path(self):
        """A successful shadow call is also purely observational, additive data."""
        task_id, run_id = self.make_bound_run(attach=True)
        self.schedule_due(task_id=task_id, run_id=run_id)
        harness = FakeHarnessServiceResume()
        sup = self.supervisor(
            sessions=[{"name": "session-1", "status": "stopped"}],
            harness_service=harness,
        )
        actions = sup.tick(now=self.now)
        self.assertEqual(len(harness.calls), 1)
        self.assertEqual(actions[0]["action"], "resume")
        self.assertEqual(
            actions[0]["harness_resume_shadow"],
            {"attempted": True, "ok": True, "code": "SESSION_RESUMED", "summary": "hcom resume request completed."},
        )
        self.assertEqual(len(self.hcom.resumes), 1)


if __name__ == "__main__":
    unittest.main()
