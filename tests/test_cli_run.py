"""CLI tests for `maps run bind-session` -- the lineage-bootstrap wiring.

Per work/notes/2026-09-02-lineage-bootstrap-wiring-scoping.md ("The impl slice"):
a thin wrapper over `store.record_run_session_link(...)` -- NO HarnessService,
NO adapter. These tests round-trip the verb against a real temp-file
`TaskStore`, pin every `record_run_session_link` failure code the store can
return (not just the process exit code), and prove end-to-end that one
CLI-written ATTACH row lets `RecoverySupervisor` route a resume through the
real guarded `HarnessService` (the deadlock the note traces).
"""

from __future__ import annotations

from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
import io
import json
import sqlite3
import tempfile
import unittest

from runtime.cli import main
from runtime.harness import HookRegistry
from runtime.harness.adapters import HcomHarnessAdapter
from runtime.harness.service import HarnessService
from runtime.policy.harness_guard import CanonicalRunGuard, register_canonical_run_guards
from runtime.recovery import RecoveryStore, RecoverySupervisor
from runtime.state import TaskStore

from tests.test_recovery_supervisor import FakeHcom, _lineage_contract


class _RunCliMixin(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        self.db = self.root / "maps.db"
        self.store = TaskStore(self.db)

    def run_maps(self, *args: str) -> tuple[int, object]:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(['--db', str(self.db), *args])
        text = buffer.getvalue()
        return code, (json.loads(text) if text.strip() else None)

    def bind(self, run_id: str, **overrides) -> tuple[int, object]:
        opts = {
            'worker-id': 'worker-1',
            'session-id': 'sess-1',
            'evidence-ref': 'hcom:attach:sess-1',
        }
        opts.update({k.replace('_', '-'): v for k, v in overrides.items()})
        args = ['run', 'bind-session', run_id]
        for key, value in opts.items():
            if value is not None:
                args += [f'--{key}', value]
        return self.run_maps(*args)

    def seed_active_run(self, *, worker='worker-1', manifest_session_id=None):
        created = self.store.create_task(title='x', project_id='proj-1')
        self.assertTrue(created.ok)
        task_id = created.task['task_id']
        self.assertTrue(self.store.update_contract(task_id, _lineage_contract()).ok)
        self.assertTrue(self.store.promote_ready(task_id).ok)
        self.assertTrue(self.store.claim_task(task_id, worker, lease_seconds=600).ok)
        manifest = self.store.create_run_manifest(
            task_id,
            worker,
            repo_root=self.repo,
            created_by='dispatcher',
            session_id=manifest_session_id,
            readable_paths=['.'],
            writable_paths=self.store.get_task(task_id)['output_paths'],
        )
        self.assertTrue(manifest.ok, manifest.message)
        return task_id, manifest.task['run_id']

    def expire_lease(self, task_id: str):
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        with sqlite3.connect(self.db) as conn:
            conn.execute(
                "UPDATE tasks SET lease_expires_at = ? WHERE task_id = ?",
                (past, task_id),
            )

    def force_status(self, task_id: str, status: str):
        with sqlite3.connect(self.db) as conn:
            conn.execute(
                "UPDATE tasks SET status = ? WHERE task_id = ?", (status, task_id)
            )


class RunBindSessionRoundTripTests(_RunCliMixin):
    def test_bind_session_makes_lineage_explicit(self):
        task_id, run_id = self.seed_active_run()
        self.assertNotEqual(
            self.store.resolve_run_session(run_id)['state'], 'EXPLICIT'
        )

        code, payload = self.bind(run_id)
        self.assertEqual(code, 0, payload)
        self.assertTrue(payload['ok'])
        self.assertEqual(payload['code'], 'SESSION_ATTACHED')

        resolved = self.store.resolve_run_session(run_id)
        self.assertEqual(resolved['state'], 'EXPLICIT')
        self.assertEqual(resolved['current']['session_id'], 'sess-1')
        self.assertEqual(resolved['current']['adapter_id'], 'hcom')

    def test_adapter_defaults_to_hcom(self):
        _task_id, run_id = self.seed_active_run()
        code, _payload = self.run_maps(
            'run', 'bind-session', run_id,
            '--worker-id', 'worker-1',
            '--session-id', 'sess-1',
            '--evidence-ref', 'hcom:attach:sess-1',
        )
        self.assertEqual(code, 0)
        self.assertEqual(
            self.store.resolve_run_session(run_id)['current']['adapter_id'], 'hcom'
        )

    def test_created_by_defaults_to_verb_name(self):
        _task_id, run_id = self.seed_active_run()
        self.assertEqual(self.bind(run_id)[0], 0)
        history = self.store.resolve_run_session(run_id)['history']
        self.assertEqual(history[0]['created_by'], 'maps-run-bind-session')


class RunBindSessionFailureCodeTests(_RunCliMixin):
    def test_run_not_found(self):
        code, payload = self.bind('run-does-not-exist')
        self.assertEqual(code, 2)
        self.assertEqual(payload['code'], 'RUN_NOT_FOUND')
        self.assertTrue(payload['message'])

    def test_run_worker_mismatch(self):
        _task_id, run_id = self.seed_active_run(worker='worker-1')
        code, payload = self.bind(run_id, worker_id='someone-else')
        self.assertEqual(code, 2)
        self.assertEqual(payload['code'], 'RUN_WORKER_MISMATCH')

    def test_run_not_owned_when_task_left_active(self):
        task_id, run_id = self.seed_active_run()
        self.force_status(task_id, 'READY_FOR_REVIEW')
        code, payload = self.bind(run_id)
        self.assertEqual(code, 2)
        self.assertEqual(payload['code'], 'RUN_NOT_OWNED')

    def test_lease_expired(self):
        task_id, run_id = self.seed_active_run()
        self.expire_lease(task_id)
        code, payload = self.bind(run_id)
        self.assertEqual(code, 2)
        self.assertEqual(payload['code'], 'LEASE_EXPIRED')

    def test_session_already_bound(self):
        _task_id, run_id = self.seed_active_run()
        self.assertEqual(self.bind(run_id)[0], 0)
        code, payload = self.bind(run_id)
        self.assertEqual(code, 2)
        self.assertEqual(payload['code'], 'SESSION_ALREADY_BOUND')

    def test_manifest_session_conflict(self):
        _task_id, run_id = self.seed_active_run(manifest_session_id='legacy-sess')
        code, payload = self.bind(run_id, session_id='different-sess')
        self.assertEqual(code, 2)
        self.assertEqual(payload['code'], 'MANIFEST_SESSION_CONFLICT')

    def test_invalid_session_link_on_empty_evidence_ref(self):
        _task_id, run_id = self.seed_active_run()
        code, payload = self.bind(run_id, evidence_ref='')
        self.assertEqual(code, 2)
        self.assertEqual(payload['code'], 'INVALID_SESSION_LINK')


class RunBindSessionUnblocksSupervisorRoutingTests(_RunCliMixin):
    """End-to-end: one CLI-written ATTACH row is enough for
    `RecoverySupervisor.tick()` to route a resume through the real guarded
    `HarnessService`, where `CanonicalRunGuard` then actually runs -- the
    lineage-bootstrap deadlock the scoping note (#257) traces.

    Per the #257 reviewer nits: the lease is SEEDED expired explicitly (no
    reliance on timing) and the assertion is on the denial CLASS
    (`HOOK_DENIED` -> `resume_denied`), not a pinned deny code.
    """

    def _supervisor(self, run_id, task_id):
        now = datetime(2026, 9, 2, 20, 0, tzinfo=timezone.utc)
        recovery_store = RecoveryStore(self.root / "recovery.json")
        recovery_store.schedule(
            task_id=task_id,
            worker_id="worker-1",
            session_name="session-1",
            reason="scheduled",
            resume_after=(now - timedelta(seconds=1)).isoformat(),
            run_id=run_id,
        )
        backend = FakeHcom(
            sessions=[{"name": "session-1", "status": "stopped", "session_id": "sess-1"}]
        )
        adapter = HcomHarnessAdapter(
            backend, project_id="proj-1", lineage_writer=self.store
        )
        hooks = HookRegistry()
        register_canonical_run_guards(
            hooks, CanonicalRunGuard(self.store, repo_root=self.repo)
        )
        harness_service = HarnessService([adapter], hooks=hooks)
        sup = RecoverySupervisor(
            task_reader=self.store,
            hcom=FakeHcom([]),
            recovery_store=recovery_store,
            backoff_seconds=(60, 120),
            silent_stop_probe_delay_seconds=30,
            harness_service=harness_service,
        )
        return sup, now

    def test_without_bind_session_the_harness_path_cannot_be_built(self):
        task_id, run_id = self.seed_active_run()
        sup, now = self._supervisor(run_id, task_id)
        actions = sup.tick(now=now)
        self.assertEqual(
            actions[0]["harness_resume"],
            {"attempted": False, "reason": "session_not_durably_bound"},
        )

    def test_bind_session_then_guard_denies_on_expired_lease(self):
        task_id, run_id = self.seed_active_run()
        self.assertEqual(self.bind(run_id)[0], 0)
        self.expire_lease(task_id)

        sup, now = self._supervisor(run_id, task_id)
        actions = sup.tick(now=now)

        harness_resume = actions[0]["harness_resume"]
        self.assertTrue(harness_resume["attempted"])
        self.assertFalse(harness_resume["ok"])
        # Denial CLASS, not the specific LEASE_EXPIRED string.
        self.assertEqual(harness_resume["code"], "HOOK_DENIED")
        self.assertEqual(actions[0]["action"], "resume_denied")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
