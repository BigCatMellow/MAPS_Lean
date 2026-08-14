from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from runtime.communication import HcomError
from runtime.recovery import RecoveryStore, RecoverySupervisor, session_is_live


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


if __name__ == "__main__":
    unittest.main()
