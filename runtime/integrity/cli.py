from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from runtime.integrity import (
    check_run_budget,
    verify_git_run,
    write_budget_escalation,
)
from runtime.state import MutationResult, TaskStore

DEFAULT_DB = ".maps/state/maps.db"


def emit(value: object) -> int:
    if isinstance(value, MutationResult):
        payload = asdict(value)
        ok = value.ok
    else:
        payload = value
        ok = not (isinstance(value, dict) and value.get("ok") is False)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if ok else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MAPS execution-integrity CLI")
    parser.add_argument("--db", default=DEFAULT_DB)
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("run-create", help="freeze one ACTIVE worker run")
    create.add_argument("task_id")
    create.add_argument("worker_id")
    create.add_argument("--repo", default=".")
    create.add_argument("--created-by", required=True)
    create.add_argument("--session-id")
    create.add_argument("--context", action="append", default=[])
    create.add_argument("--read", action="append", default=["."])
    create.add_argument("--write", action="append")
    create.add_argument("--forbid", action="append", default=[])
    create.add_argument("--base-revision")
    create.add_argument(
        "--require-worktree-binding",
        action="store_true",
        help="fail run creation unless --repo has readable Git worktree identity",
    )
    create.add_argument("--runtime-seconds", type=int)
    create.add_argument("--max-tool-failures", type=int)
    create.add_argument("--max-attempts", type=int)

    show = sub.add_parser("run-show")
    show.add_argument("run_id")

    stale = sub.add_parser("run-stale")
    stale.add_argument("run_id")
    stale.add_argument("--repo", default=".")

    verify = sub.add_parser("run-verify-git")
    verify.add_argument("run_id")
    verify.add_argument("--repo", default=".")

    budget = sub.add_parser("run-budget-check")
    budget.add_argument("run_id")
    budget.add_argument("--attempts", type=int)
    budget.add_argument("--tool-failures", type=int)
    budget.add_argument("--runtime-seconds", type=int)
    budget.add_argument(
        "--write-escalation",
        action="store_true",
        help="write a durable JSON artifact only if the declared budget is exhausted",
    )
    budget.add_argument("--escalation-dir", default=".maps/state/escalations")

    link = sub.add_parser("continuity-link")
    link.add_argument("predecessor_id")
    link.add_argument("replacement_id")
    link.add_argument("--reason", required=True)

    component = sub.add_parser("continuity-show")
    component.add_argument("identity")

    criteria = sub.add_parser("criteria")
    criteria.add_argument("task_id")

    claim = sub.add_parser("criterion-claim")
    claim.add_argument("task_id")
    claim.add_argument("criterion_id", type=int)
    claim.add_argument("status", choices=["complete", "partial", "blocked"])
    claim.add_argument("--author", required=True)
    claim.add_argument("--repo", default=".")
    claim.add_argument("--evidence", action="append", default=[])
    claim.add_argument("--run-id")

    verdict = sub.add_parser("criterion-verdict")
    verdict.add_argument("claim_id", type=int)
    verdict.add_argument("status", choices=["confirmed", "rejected"])
    verdict.add_argument("--reviewer", required=True)
    verdict.add_argument("--notes", default="")

    args = parser.parse_args(argv)
    store = TaskStore(args.db)

    if args.command == "run-create":
        limits = {
            key: value
            for key, value in {
                "runtime_seconds": args.runtime_seconds,
                "max_tool_failures": args.max_tool_failures,
                "max_attempts": args.max_attempts,
            }.items()
            if value is not None
        }
        return emit(
            store.create_run_manifest(
                args.task_id,
                args.worker_id,
                repo_root=Path(args.repo),
                created_by=args.created_by,
                session_id=args.session_id,
                context_paths=args.context,
                readable_paths=args.read,
                writable_paths=args.write,
                forbidden_paths=args.forbid,
                runtime_limits=limits,
                base_revision=args.base_revision,
                require_worktree_binding=args.require_worktree_binding,
            )
        )
    if args.command == "run-show":
        value = store.get_run_manifest(args.run_id)
        return emit(value if value is not None else {"ok": False, "reason": "run_not_found"})
    if args.command == "run-stale":
        value = store.check_run_stale(args.run_id, repo_root=args.repo)
        value["ok"] = not value["stale"]
        return emit(value)
    if args.command == "run-verify-git":
        return emit(verify_git_run(store, args.run_id, repo_root=args.repo))
    if args.command == "run-budget-check":
        try:
            value = check_run_budget(
                store,
                args.run_id,
                actual_attempts=args.attempts,
                actual_tool_failures=args.tool_failures,
                actual_runtime_seconds=args.runtime_seconds,
            )
        except ValueError as exc:
            return emit({"ok": False, "reason": "invalid_budget_measurement", "error": str(exc)})
        if args.write_escalation and value.get("reason") == "budget_exhausted":
            value["escalation_path"] = str(
                write_budget_escalation(value, out_dir=args.escalation_dir)
            )
        return emit(value)
    if args.command == "continuity-link":
        return emit(
            store.record_continuity_link(
                args.predecessor_id, args.replacement_id, reason=args.reason
            )
        )
    if args.command == "continuity-show":
        return emit({"identity": args.identity, "component": sorted(store.continuity_component(args.identity))})
    if args.command == "criteria":
        return emit(store.list_acceptance_criteria(args.task_id))
    if args.command == "criterion-claim":
        return emit(
            store.record_criterion_claim(
                args.task_id,
                args.criterion_id,
                args.status,
                author_id=args.author,
                evidence_refs=args.evidence,
                repo_root=args.repo,
                run_id=args.run_id,
            )
        )
    if args.command == "criterion-verdict":
        return emit(
            store.record_criterion_verdict(
                args.claim_id,
                args.status,
                reviewer_id=args.reviewer,
                notes=args.notes,
            )
        )
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
