from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys

from runtime.policy import HaltStore, WorkerProfile
from runtime.routing import route_project
from runtime.routing.langgraph_runtime import _deserialize_environment_reports
from runtime.state import TaskStore

DEFAULT_DB = ".maps/state/maps.db"
DEFAULT_HALT = ".maps/state/halt.json"
DEFAULT_CHECKPOINT = ".maps/state/langgraph-checkpoints.db"


def read_workers(path: str) -> list[WorkerProfile]:
    with open(path, "r", encoding="utf-8") as handle:
        value = json.load(handle)
    if isinstance(value, dict):
        value = value.get("workers", [])
    if not isinstance(value, list):
        raise ValueError("workers JSON must be a list or an object with a workers list")
    return [WorkerProfile.from_mapping(item) for item in value]


def read_environment_reports(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        value = json.load(handle)
    if isinstance(value, dict) and "environment_reports" in value:
        value = value["environment_reports"]
    if not isinstance(value, dict):
        raise ValueError(
            "environment reports JSON must be an object or contain environment_reports"
        )
    return _deserialize_environment_reports(value)


def emit(value: object) -> int:
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MAPS Lean routing/policy CLI")
    parser.add_argument("--db", default=DEFAULT_DB)
    parser.add_argument("--halt-path", default=DEFAULT_HALT)
    sub = parser.add_subparsers(dest="command", required=True)

    route = sub.add_parser("route", help="produce one read-only LangGraph recommendation")
    route.add_argument("--workers-json", required=True)
    route.add_argument("--project-id", default="default")
    route.add_argument("--checkpoint-db", default=DEFAULT_CHECKPOINT)
    route.add_argument("--thread-id")
    route.add_argument(
        "--environment-reports-json",
        help=(
            "JSON object mapping task IDs to CompatibilityReport values; this "
            "is caller-supplied evidence, not environment inspection"
        ),
    )

    approve = sub.add_parser(
        "approve", help="record operator approval for an explicitly gated task"
    )
    approve.add_argument("task_id")
    approve.add_argument("--approved-by", required=True)
    approve.add_argument("--note", required=True)

    sub.add_parser("halt-show")

    halt_set = sub.add_parser("halt-set")
    halt_set.add_argument(
        "state", choices=["halt_paid_dispatch", "halt_all_dispatch", "repair_only"]
    )
    halt_set.add_argument("--reason", required=True)
    halt_set.add_argument("--actor", required=True)
    halt_set.add_argument(
        "--authority", required=True, choices=["operator", "core", "system"]
    )
    halt_set.add_argument("--scope", default="global", choices=["global", "project", "task"])
    halt_set.add_argument("--target")
    halt_set.add_argument(
        "--clear-requires", default="operator", choices=["operator", "core", "system"]
    )

    halt_clear = sub.add_parser("halt-clear")
    halt_clear.add_argument("--actor", required=True)
    halt_clear.add_argument(
        "--authority", required=True, choices=["operator", "core", "system"]
    )
    halt_clear.add_argument("--reason", required=True)

    args = parser.parse_args(argv)
    halt_store = HaltStore(args.halt_path)

    try:
        if args.command == "route":
            workers = read_workers(args.workers_json)
            environment_reports = (
                read_environment_reports(args.environment_reports_json)
                if args.environment_reports_json
                else None
            )
            store = TaskStore(args.db)
            return emit(
                route_project(
                    store,
                    workers,
                    project_id=args.project_id,
                    halt_path=args.halt_path,
                    checkpoint_path=args.checkpoint_db,
                    thread_id=args.thread_id,
                    environment_reports=environment_reports,
                )
            )
        if args.command == "approve":
            result = TaskStore(args.db).record_operator_approval(
                args.task_id,
                approved_by=args.approved_by,
                note=args.note,
            )
            return emit(asdict(result))
        if args.command == "halt-show":
            return emit(halt_store.load().to_dict())
        if args.command == "halt-set":
            record = halt_store.set(
                state=args.state,
                reason=args.reason,
                actor=args.actor,
                authority=args.authority,
                scope=args.scope,
                target=args.target,
                clear_requires=args.clear_requires,
            )
            return emit(record.to_dict())
        if args.command == "halt-clear":
            return emit(
                halt_store.clear(
                    actor=args.actor,
                    authority=args.authority,
                    reason=args.reason,
                ).to_dict()
            )
    except (ValueError, PermissionError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {"ok": False, "error": type(exc).__name__, "message": str(exc)},
                indent=2,
            ),
            file=sys.stderr,
        )
        return 2
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
