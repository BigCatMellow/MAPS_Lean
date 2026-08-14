from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from runtime.state import TaskStore


def ready_contract(**overrides):
    base = {
        'title': 'Implement thing',
        'outcome': 'The requested behavior is observable.',
        'task_type': 'IMPLEMENTATION',
        'owner': 'owner-a',
        'risk': 'MEDIUM',
        'decision_authority': 'Implementation choices inside the declared scope.',
        'verification': 'Run the named unit tests.',
        'evidence_expected': 'Passing test output.',
        'review_required': 'INDEPENDENT_REVIEW',
        'escalation': 'Stop on scope, security, or dependency changes.',
        'inputs': ['README.md'],
        'sources': ['AGENTS.md'],
        'dependencies': [],
        'output_paths': ['runtime/example.py'],
        'non_goals': ['Do not change product scope.'],
        'acceptance_criteria': ['Behavior passes a deterministic test.'],
        'stop_conditions': ['A required dependency is missing.'],
    }
    base.update(overrides)
    return base


class TaskStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / 'maps.db'
        self.store = TaskStore(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def create_shaped(self, *, task_id=None, **overrides):
        created = self.store.create_task(task_id=task_id)
        self.assertTrue(created.ok, created)
        tid = created.task['task_id']
        updated = self.store.update_contract(tid, ready_contract(**overrides))
        self.assertTrue(updated.ok, updated)
        return tid

    def test_sqlite_connection_safety_defaults(self):
        settings = self.store.connection_settings()
        self.assertEqual(settings['foreign_keys'], 1)
        self.assertEqual(str(settings['journal_mode']).lower(), 'wal')
        self.assertGreaterEqual(int(settings['busy_timeout']), 5000)

    def test_incomplete_task_cannot_promote(self):
        created = self.store.create_task(title='Too vague')
        result = self.store.promote_ready(created.task['task_id'], actor='shaper')
        self.assertFalse(result.ok)
        self.assertEqual(result.code, 'AGI_NOT_READY')
        self.assertEqual(result.task['status'], 'NEEDS_SHAPING')
        self.assertEqual(result.task['agi_status'], 'AGI FAIL — NEEDS_SHAPING')

    def test_complete_task_promotes_to_ready(self):
        tid = self.create_shaped()
        result = self.store.promote_ready(tid, actor='shaper')
        self.assertTrue(result.ok, result)
        self.assertEqual(result.task['status'], 'READY')
        self.assertEqual(result.task['agi_status'], 'AGI READY')

    def test_dependency_blocks_promotion_until_done(self):
        dep = self.store.create_task(title='dependency').task['task_id']
        tid = self.create_shaped(dependencies=[dep])
        validation = self.store.validate_ready(tid)
        self.assertFalse(validation.ok)
        self.assertEqual(validation.agi_status, 'AGI FAIL — BLOCKED_ON_DEPENDENCY')
        self.assertIn('not DONE', validation.reasons[0])

    def test_output_path_conflict_blocks_second_ready_task(self):
        first = self.create_shaped(task_id='TASK-A')
        self.assertTrue(self.store.promote_ready(first).ok)
        second = self.create_shaped(task_id='TASK-B')
        validation = self.store.validate_ready(second)
        self.assertFalse(validation.ok)
        self.assertTrue(any('already reserved by TASK-A' in reason for reason in validation.reasons))

    def test_contract_freezes_after_ready(self):
        tid = self.create_shaped()
        self.assertTrue(self.store.promote_ready(tid).ok)
        changed = self.store.update_contract(tid, {'output_paths': ['runtime/elsewhere.py']})
        self.assertFalse(changed.ok)
        self.assertEqual(changed.code, 'CONTRACT_FROZEN')

    def test_atomic_claim_race_has_exactly_one_winner(self):
        tid = self.create_shaped()
        self.assertTrue(self.store.promote_ready(tid).ok)

        def claim(worker):
            return TaskStore(self.db).claim_task(tid, worker, lease_seconds=60)

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(claim, ['worker-a', 'worker-b']))
        winners = [r for r in results if r.ok]
        losers = [r for r in results if not r.ok]
        self.assertEqual(len(winners), 1, results)
        self.assertEqual(len(losers), 1, results)
        self.assertIn(losers[0].code, {'LEASE_ACTIVE', 'NOT_CLAIMABLE'})
        task = self.store.get_task(tid)
        self.assertEqual(task['claimed_by'], winners[0].task['claimed_by'])
        self.assertEqual(task['owner'], 'owner-a')

    def test_live_lease_cannot_be_stolen(self):
        tid = self.create_shaped()
        self.assertTrue(self.store.promote_ready(tid).ok)
        now = datetime(2026, 8, 14, 12, tzinfo=timezone.utc)
        self.assertTrue(self.store.claim_task(tid, 'worker-a', now=now, lease_seconds=300).ok)
        stolen = self.store.claim_task(tid, 'worker-b', now=now + timedelta(seconds=60), lease_seconds=300)
        self.assertFalse(stolen.ok)
        self.assertEqual(stolen.code, 'LEASE_ACTIVE')
        self.assertEqual(self.store.get_task(tid)['claimed_by'], 'worker-a')

    def test_expired_lease_recovers_without_changing_owner(self):
        tid = self.create_shaped()
        self.assertTrue(self.store.promote_ready(tid).ok)
        now = datetime(2026, 8, 14, 12, tzinfo=timezone.utc)
        first = self.store.claim_task(tid, 'worker-a', now=now, lease_seconds=30)
        self.assertTrue(first.ok)
        recovered = self.store.claim_task(tid, 'worker-b', now=now + timedelta(seconds=31), lease_seconds=30)
        self.assertTrue(recovered.ok, recovered)
        self.assertEqual(recovered.code, 'RECOVERED')
        task = self.store.get_task(tid)
        self.assertEqual(task['claimed_by'], 'worker-b')
        self.assertEqual(task['owner'], 'owner-a')
        self.assertEqual(task['attempt'], 2)

    def test_explicit_numeric_id_advances_auto_allocator(self):
        explicit = self.store.create_task(task_id='TASK-0042')
        self.assertTrue(explicit.ok)
        automatic = self.store.create_task()
        self.assertTrue(automatic.ok)
        self.assertEqual(automatic.task['task_id'], 'TASK-0043')

    def test_concurrent_ready_promotion_cannot_reserve_same_output_path_twice(self):
        first = self.create_shaped(task_id='TASK-X', output_paths=['runtime/shared.py'])
        second = self.create_shaped(task_id='TASK-Y', output_paths=['runtime/shared.py'])

        def promote(task_id):
            return TaskStore(self.db).promote_ready(task_id, actor='shaper')

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(promote, [first, second]))
        self.assertEqual(sum(result.ok for result in results), 1, results)
        loser = next(result for result in results if not result.ok)
        self.assertEqual(loser.code, 'AGI_NOT_READY')
        self.assertIn('already reserved by', loser.message)


    def test_auto_ids_are_unique_under_concurrency(self):
        def create(_):
            return TaskStore(self.db).create_task().task['task_id']

        with ThreadPoolExecutor(max_workers=8) as pool:
            ids = list(pool.map(create, range(20)))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 20)

    def test_submission_author_cannot_claim_independent_review(self):
        tid = self.create_shaped()
        self.assertTrue(self.store.promote_ready(tid).ok)
        now = datetime(2026, 8, 14, 12, tzinfo=timezone.utc)
        self.assertTrue(self.store.claim_task(tid, 'worker-a', now=now, lease_seconds=300).ok)
        submitted = self.store.submit_task(tid, 'worker-a', 'unit tests passed', now=now + timedelta(seconds=10))
        self.assertTrue(submitted.ok, submitted)
        self_review = self.store.claim_review(tid, 'worker-a', now=now + timedelta(seconds=20))
        self.assertFalse(self_review.ok)
        self.assertEqual(self_review.code, 'SELF_REVIEW_FORBIDDEN')
        independent = self.store.claim_review(tid, 'reviewer-b', now=now + timedelta(seconds=20))
        self.assertTrue(independent.ok, independent)
        approved = self.store.record_review(
            tid,
            'reviewer-b',
            'APPROVED',
            'Acceptance criteria and evidence verified.',
            now=now + timedelta(seconds=30),
        )
        self.assertTrue(approved.ok, approved)
        self.assertEqual(approved.task['status'], 'DONE')
        self.assertEqual(self.store.get_submission(tid)['author_id'], 'worker-a')

    def test_dependency_can_promote_after_dependency_is_done(self):
        dep = self.create_shaped(task_id='TASK-DEP', review_required='OWNER_CHECK', output_paths=['dep.out'])
        self.assertTrue(self.store.promote_ready(dep).ok)
        now = datetime(2026, 8, 14, 12, tzinfo=timezone.utc)
        self.assertTrue(self.store.claim_task(dep, 'owner-a', now=now, lease_seconds=300).ok)
        self.assertTrue(self.store.submit_task(dep, 'owner-a', 'verified', now=now + timedelta(seconds=10)).ok)
        self.assertTrue(self.store.claim_review(dep, 'owner-a', now=now + timedelta(seconds=20)).ok)
        self.assertTrue(
            self.store.record_review(dep, 'owner-a', 'APPROVED', 'owner check passed', now=now + timedelta(seconds=30)).ok
        )

        child = self.create_shaped(task_id='TASK-CHILD', dependencies=[dep], output_paths=['child.out'])
        promoted = self.store.promote_ready(child)
        self.assertTrue(promoted.ok, promoted)
        self.assertEqual(promoted.task['status'], 'READY')

    def test_changes_requested_can_be_reclaimed_without_changing_owner(self):
        tid = self.create_shaped()
        self.assertTrue(self.store.promote_ready(tid).ok)
        now = datetime(2026, 8, 14, 12, tzinfo=timezone.utc)
        self.assertTrue(self.store.claim_task(tid, 'worker-a', now=now, lease_seconds=300).ok)
        self.assertTrue(self.store.submit_task(tid, 'worker-a', 'tests passed', now=now + timedelta(seconds=10)).ok)
        self.assertTrue(self.store.claim_review(tid, 'reviewer-b', now=now + timedelta(seconds=20)).ok)
        changes = self.store.record_review(
            tid,
            'reviewer-b',
            'CHANGES_REQUESTED',
            'Criterion 1 still fails.',
            now=now + timedelta(seconds=30),
        )
        self.assertTrue(changes.ok)
        reclaimed = self.store.claim_task(tid, 'worker-c', now=now + timedelta(seconds=40), lease_seconds=300)
        self.assertTrue(reclaimed.ok, reclaimed)
        self.assertEqual(reclaimed.task['status'], 'ACTIVE')
        self.assertEqual(reclaimed.task['owner'], 'owner-a')
        self.assertEqual(reclaimed.task['claimed_by'], 'worker-c')


if __name__ == '__main__':
    unittest.main()
