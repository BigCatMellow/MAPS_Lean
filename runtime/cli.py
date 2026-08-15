from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

from runtime.state import MutationResult, TaskStore, ValidationResult

DEFAULT_DB = Path('.maps/state/maps.db')


def _read_contract(path: str) -> dict:
    if path == '-':
        data = json.load(sys.stdin)
    else:
        with open(path, 'r', encoding='utf-8') as handle:
            data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError('contract JSON must be an object')
    return data


def _emit(value: MutationResult | ValidationResult | dict | list) -> int:
    if isinstance(value, (MutationResult, ValidationResult)):
        payload = asdict(value)
        ok = value.ok
    else:
        payload = value
        ok = True
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if ok else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='MAPS Lean task-state CLI')
    parser.add_argument('--db', default=str(DEFAULT_DB), help='SQLite task-state path')
    sub = parser.add_subparsers(dest='command', required=True)

    sub.add_parser('init', help='create/open the task database')

    create = sub.add_parser('create', help='create a NEEDS_SHAPING task')
    create.add_argument('--task-id')
    create.add_argument('--project-id', default='default')
    create.add_argument('--title', default='')
    create.add_argument('--outcome', default='')
    create.add_argument('--type', dest='task_type', default='')
    create.add_argument('--owner', default='')
    create.add_argument('--risk', default='')
    create.add_argument('--max-attempts', type=int, default=3)

    shape = sub.add_parser('shape', help='replace supplied task-contract fields from JSON')
    shape.add_argument('task_id')
    shape.add_argument('--contract-json', required=True, help='JSON file path or - for stdin')

    check = sub.add_parser('check', help='run structural AGI READY validation')
    check.add_argument('task_id')

    promote = sub.add_parser('promote', help='atomically validate and promote to READY')
    promote.add_argument('task_id')
    promote.add_argument('--actor')

    show = sub.add_parser('show', help='show canonical task state')
    show.add_argument('task_id')

    trace = sub.add_parser(
        'trace',
        help='show a read-only canonical task trace with explicit source coverage',
    )
    trace.add_argument('task_id')

    claim = sub.add_parser('claim', help='claim READY/CHANGES_REQUESTED work')
    claim.add_argument('task_id')
    claim.add_argument('worker_id')
    claim.add_argument('--lease-seconds', type=int, default=900)

    heartbeat = sub.add_parser('heartbeat', help='renew the active claim lease')
    heartbeat.add_argument('task_id')
    heartbeat.add_argument('worker_id')
    heartbeat.add_argument('--lease-seconds', type=int, default=900)

    submit = sub.add_parser('submit', help='submit active work with durable evidence')
    submit.add_argument('task_id')
    submit.add_argument('worker_id')
    submit.add_argument('--evidence', required=True)

    review_claim = sub.add_parser('review-claim', help='claim review work')
    review_claim.add_argument('task_id')
    review_claim.add_argument('reviewer_id')

    review_record = sub.add_parser('review-record', help='record review verdict')
    review_record.add_argument('task_id')
    review_record.add_argument('reviewer_id')
    review_record.add_argument('verdict', choices=['APPROVED', 'CHANGES_REQUESTED', 'BLOCKED'])
    review_record.add_argument('--summary', required=True)

    events = sub.add_parser('events', help='show task event history')
    events.add_argument('task_id')

    reviews = sub.add_parser('reviews', help='show task review history')
    reviews.add_argument('task_id')

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = TaskStore(args.db)

    if args.command == 'init':
        return _emit({'ok': True, 'db': str(Path(args.db)), 'settings': store.connection_settings()})
    if args.command == 'create':
        return _emit(store.create_task(
            task_id=args.task_id,
            project_id=args.project_id,
            title=args.title,
            outcome=args.outcome,
            task_type=args.task_type,
            owner=args.owner,
            risk=args.risk,
            max_attempts=args.max_attempts,
        ))
    if args.command == 'shape':
        try:
            contract = _read_contract(args.contract_json)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            return _emit(MutationResult(False, 'INVALID_CONTRACT_FILE', str(exc)))
        return _emit(store.update_contract(args.task_id, contract))
    if args.command == 'check':
        return _emit(store.validate_ready(args.task_id))
    if args.command == 'promote':
        return _emit(store.promote_ready(args.task_id, actor=args.actor))
    if args.command == 'show':
        task = store.get_task(args.task_id)
        if task is None:
            return _emit(MutationResult(False, 'NOT_FOUND', f'{args.task_id} does not exist'))
        return _emit(task)
    if args.command == 'trace':
        trace = store.trace_task(args.task_id)
        if trace is None:
            return _emit(MutationResult(False, 'NOT_FOUND', f'{args.task_id} does not exist'))
        return _emit(trace)
    if args.command == 'claim':
        return _emit(store.claim_task(args.task_id, args.worker_id, lease_seconds=args.lease_seconds))
    if args.command == 'heartbeat':
        return _emit(store.heartbeat(args.task_id, args.worker_id, lease_seconds=args.lease_seconds))
    if args.command == 'submit':
        return _emit(store.submit_task(args.task_id, args.worker_id, args.evidence))
    if args.command == 'review-claim':
        return _emit(store.claim_review(args.task_id, args.reviewer_id))
    if args.command == 'review-record':
        return _emit(store.record_review(
            args.task_id,
            args.reviewer_id,
            args.verdict,
            args.summary,
        ))
    if args.command == 'events':
        return _emit(store.list_events(args.task_id))
    if args.command == 'reviews':
        return _emit(store.list_reviews(args.task_id))
    raise AssertionError(args.command)


if __name__ == '__main__':
    raise SystemExit(main())
