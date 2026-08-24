from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

from runtime.context_builder import build_context_plan
from runtime.evaluation import IncidentCategory, RegressionCaseError, freeze_regression_case
from runtime.flow_review import flow_review_start
from runtime.flow_start import flow_start_from_runtime_limit_args
from runtime.run_record import RunRecordError, build_run_record
from runtime.state import MutationResult, TaskStore, ValidationResult
from runtime.status import build_status

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


def _read_text(path: str) -> str:
    if path == '-':
        return sys.stdin.read()
    return Path(path).read_text(encoding='utf-8')


def _emit(value: MutationResult | ValidationResult | dict | list) -> int:
    if isinstance(value, (MutationResult, ValidationResult)):
        payload = asdict(value)
        ok = value.ok
    else:
        payload = value
        ok = value.get('ok', True) if isinstance(value, dict) else True
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

    run_record = sub.add_parser(
        'run-record',
        help='export one sanitized portable Run Record for an exact task/run binding',
    )
    run_record.add_argument('task_id')
    run_record.add_argument('run_id')

    freeze_case = sub.add_parser(
        'freeze-case',
        help='emit a deterministic frozen regression case from an exact Run Record',
    )
    freeze_case.add_argument('task_id')
    freeze_case.add_argument('run_id')
    freeze_case.add_argument(
        '--category',
        required=True,
        choices=[item.value for item in IncidentCategory],
    )
    freeze_case.add_argument(
        '--fixture-file',
        required=True,
        help='sanitized fixture text file or - for stdin',
    )
    freeze_case.add_argument(
        '--expect',
        action='append',
        required=True,
        help='expected property ID; repeat for multiple properties',
    )
    freeze_case.add_argument('--tag', action='append', default=[])
    freeze_case.add_argument('--frozen-by', required=True)

    context = sub.add_parser(
        'context',
        help='show a read-only explicit context plan for a task',
    )
    context.add_argument('task_id')
    context.add_argument('--repo-root', default='.')

    status = sub.add_parser('status', help='show a read-only operator status summary')
    status.add_argument('--recent-limit', type=int, default=10)

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

    outcome_record = sub.add_parser(
        'outcome-record',
        help='append a post-completion real-world outcome observation',
    )
    outcome_record.add_argument('task_id')
    outcome_record.add_argument(
        'outcome_status', choices=['SUCCESS', 'PARTIAL', 'FAILURE', 'UNKNOWN']
    )
    outcome_record.add_argument('--source', required=True)
    outcome_record.add_argument(
        '--actor-class',
        default='UNKNOWN',
        choices=['OPERATOR', 'CORE_AGENT', 'HELPER', 'SYSTEM', 'UNKNOWN'],
    )
    outcome_record.add_argument('--actor-id', default='')
    outcome_record.add_argument('--run-id')
    outcome_record.add_argument('--failure-class', default='')
    outcome_record.add_argument('--escaped-defect', action='store_true')
    outcome_record.add_argument('--rework-count', type=int, default=0)
    outcome_record.add_argument('--operator-intervention-count', type=int, default=0)
    outcome_record.add_argument('--notes', default='')
    outcome_record.add_argument('--supersedes', type=int)

    outcomes = sub.add_parser('outcomes', help='show append-only outcome history')
    outcomes.add_argument('task_id')

    events = sub.add_parser('events', help='show task event history')
    events.add_argument('task_id')

    reviews = sub.add_parser('reviews', help='show task review history')
    reviews.add_argument('task_id')

    flow = sub.add_parser('flow', help='run deterministic lifecycle flows')
    flow_sub = flow.add_subparsers(dest='flow_command', required=True)
    flow_start = flow_sub.add_parser(
        'start',
        help='claim, plan context, and bind a run manifest without provider launch',
    )
    flow_start.add_argument('task_id')
    flow_start.add_argument('--worker-id', required=True)
    flow_start.add_argument('--repo-root', default='.')
    flow_start.add_argument('--created-by', default='maps-flow-start')
    flow_start.add_argument('--lease-seconds', type=int, default=900)
    flow_start.add_argument('--context-path', action='append', default=[])
    flow_start.add_argument('--readable-path', action='append', default=None)
    flow_start.add_argument('--writable-path', action='append', default=None)
    flow_start.add_argument('--forbidden-path', action='append', default=[])
    flow_start.add_argument(
        '--runtime-limit',
        action='append',
        default=[],
        help='runtime limit as KEY=INT; repeat for multiple limits',
    )
    flow_start.add_argument('--base-revision')
    flow_review_start = flow_sub.add_parser(
        'review-start',
        help='claim review work and optionally bind the immutable review subject',
    )
    flow_review_start.add_argument('task_id')
    flow_review_start.add_argument('--reviewer-id', required=True)
    flow_review_start.add_argument(
        '--freshness-mode',
        choices=['REVISION_BOUND', 'REDERIVED_AT_REVIEW', 'NON_CONSEQUENTIAL'],
    )
    flow_review_start.add_argument('--run-id')
    flow_review_start.add_argument('--artifact-ref', action='append', default=[])

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
    if args.command == 'run-record':
        try:
            return _emit(build_run_record(store, args.task_id, args.run_id))
        except RunRecordError as exc:
            return _emit(MutationResult(False, 'INVALID_RUN_RECORD_SOURCE', str(exc)))
    if args.command == 'freeze-case':
        try:
            record = build_run_record(store, args.task_id, args.run_id)
            fixture = _read_text(args.fixture_file)
            case = freeze_regression_case(
                record,
                category=args.category,
                sanitized_fixture=fixture,
                expected_properties=args.expect,
                frozen_by=args.frozen_by,
                tags=args.tag,
            )
            return _emit(case)
        except (OSError, RunRecordError, RegressionCaseError) as exc:
            return _emit(MutationResult(False, 'INVALID_REGRESSION_CASE', str(exc)))
    if args.command == 'context':
        try:
            plan = build_context_plan(store, args.task_id, repo_root=args.repo_root)
        except ValueError as exc:
            return _emit(MutationResult(False, 'INVALID_REPO_ROOT', str(exc)))
        if plan is None:
            return _emit(MutationResult(False, 'NOT_FOUND', f'{args.task_id} does not exist'))
        return _emit(plan)
    if args.command == 'status':
        try:
            return _emit(build_status(store, recent_limit=args.recent_limit))
        except ValueError as exc:
            return _emit(MutationResult(False, 'INVALID_STATUS_OPTIONS', str(exc)))
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
    if args.command == 'outcome-record':
        return _emit(store.record_outcome(
            args.task_id,
            args.outcome_status,
            source=args.source,
            actor_class=args.actor_class,
            actor_id=args.actor_id,
            run_id=args.run_id,
            failure_class=args.failure_class,
            escaped_defect=args.escaped_defect,
            rework_count=args.rework_count,
            operator_intervention_count=args.operator_intervention_count,
            notes=args.notes,
            supersedes_outcome_id=args.supersedes,
        ))
    if args.command == 'outcomes':
        return _emit(store.list_outcomes(args.task_id))
    if args.command == 'events':
        return _emit(store.list_events(args.task_id))
    if args.command == 'reviews':
        return _emit(store.list_reviews(args.task_id))
    if args.command == 'flow':
        if args.flow_command == 'start':
            return _emit(flow_start_from_runtime_limit_args(
                store,
                args.task_id,
                worker_id=args.worker_id,
                repo_root=args.repo_root,
                created_by=args.created_by,
                lease_seconds=args.lease_seconds,
                context_paths=args.context_path,
                readable_paths=(
                    args.readable_path if args.readable_path is not None else ('.',)
                ),
                writable_paths=args.writable_path,
                forbidden_paths=args.forbidden_path,
                runtime_limit_args=args.runtime_limit,
                base_revision=args.base_revision,
            ))
        if args.flow_command == 'review-start':
            return _emit(flow_review_start(
                store,
                args.task_id,
                reviewer_id=args.reviewer_id,
                freshness_mode=args.freshness_mode,
                run_id=args.run_id,
                artifact_refs=args.artifact_ref,
            ))
        raise AssertionError(args.flow_command)
    raise AssertionError(args.command)


if __name__ == '__main__':
    raise SystemExit(main())
