from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping, TypedDict

from runtime.policy.halt import HaltRecord
from runtime.policy.models import WorkerProfile
from .router import recommend_route

if TYPE_CHECKING:
    from runtime.environment.fingerprint import CompatibilityReport


class RoutingState(TypedDict, total=False):
    tasks: list[dict[str, Any]]
    workers: list[dict[str, Any]]
    halt: dict[str, Any]
    environment_reports: dict[str, dict[str, Any]]
    recommendation: dict[str, Any]


def _serialize_environment_reports(
    reports: Mapping[str, CompatibilityReport],
) -> dict[str, dict[str, Any]]:
    return {str(task_id): report.to_dict() for task_id, report in reports.items()}


def _deserialize_environment_reports(
    reports: Mapping[str, Mapping[str, Any]],
) -> dict[str, CompatibilityReport]:
    """Rebuild caller-supplied compatibility metadata from checkpoint state.

    This is intentionally a value conversion only: it never reads a local
    environment, computes a fingerprint, or validates a report's freshness.
    """

    # Keep environment imports local. The environment package intentionally
    # depends on state helpers, while routing must remain importable without
    # loading that optional evidence domain.
    from runtime.environment.fingerprint import CompatibilityReport, CompatibilityState

    deserialized: dict[str, CompatibilityReport] = {}
    for task_id, report in reports.items():
        state = report.get("state")
        reasons = report.get("reasons", [])
        warnings = report.get("warnings", [])
        spec_hash = report.get("environment_spec_hash")
        fingerprint_sha256 = report.get("fingerprint_sha256")
        reference_sha256 = report.get("reference_fingerprint_sha256")
        if not isinstance(state, str):
            raise ValueError("environment report state must be a string")
        if not isinstance(reasons, (list, tuple)) or not all(
            isinstance(item, str) for item in reasons
        ):
            raise ValueError("environment report reasons must be strings")
        if not isinstance(warnings, (list, tuple)) or not all(
            isinstance(item, str) for item in warnings
        ):
            raise ValueError("environment report warnings must be strings")
        if not isinstance(spec_hash, str) or not isinstance(fingerprint_sha256, str):
            raise ValueError("environment report hashes must be strings")
        if reference_sha256 is not None and not isinstance(reference_sha256, str):
            raise ValueError("environment report reference hash must be a string or null")
        deserialized[str(task_id)] = CompatibilityReport(
            state=CompatibilityState(state),
            reasons=tuple(reasons),
            warnings=tuple(warnings),
            environment_spec_hash=spec_hash,
            fingerprint_sha256=fingerprint_sha256,
            reference_fingerprint_sha256=reference_sha256,
        )
    return deserialized


def build_graph(checkpointer: Any = None):
    """Build the thin LangGraph wrapper around the deterministic router."""
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:
        raise RuntimeError(
            "LangGraph is not installed; run `python -m pip install -r runtime/requirements.txt`"
        ) from exc

    def recommend_node(state: RoutingState) -> dict[str, Any]:
        workers = [
            WorkerProfile.from_mapping(item) for item in state.get("workers", [])
        ]
        halt = (
            HaltRecord.from_mapping(state.get("halt", {}))
            if state.get("halt")
            else HaltRecord()
        )
        serialized_reports = state.get("environment_reports")
        environment_reports = (
            _deserialize_environment_reports(serialized_reports)
            if serialized_reports is not None
            else None
        )
        recommendation = recommend_route(
            state.get("tasks", []),
            workers,
            halt,
            environment_reports=environment_reports,
        )
        return {"recommendation": recommendation.to_dict()}

    builder = StateGraph(RoutingState)
    builder.add_node("recommend", recommend_node)
    builder.add_edge(START, "recommend")
    builder.add_edge("recommend", END)
    return builder.compile(checkpointer=checkpointer)


def run_checkpointed_route(
    *,
    tasks: list[dict[str, Any]],
    workers: list[WorkerProfile],
    halt: HaltRecord,
    checkpoint_path: str | Path = ".maps/state/langgraph-checkpoints.db",
    thread_id: str = "maps-routing",
    task_db_path: str | Path | None = None,
    environment_reports: Mapping[str, CompatibilityReport] | None = None,
) -> dict[str, Any]:
    checkpoint_path = Path(checkpoint_path)
    if task_db_path is not None and checkpoint_path.resolve() == Path(task_db_path).resolve():
        raise ValueError(
            "LangGraph checkpoint DB must be separate from MAPS task truth DB"
        )
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    # Current langgraph-checkpoint-sqlite guidance recommends strict msgpack
    # loading. Preserve an explicit operator override if one is already set.
    os.environ.setdefault("LANGGRAPH_STRICT_MSGPACK", "true")
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
    except ImportError as exc:
        raise RuntimeError(
            "SQLite LangGraph checkpointer is not installed; run "
            "`python -m pip install -r runtime/requirements.txt`"
        ) from exc

    initial: RoutingState = {
        "tasks": tasks,
        "workers": [worker.to_dict() for worker in workers],
        "halt": halt.to_dict(),
    }
    if environment_reports is not None:
        initial["environment_reports"] = _serialize_environment_reports(
            environment_reports
        )
    with SqliteSaver.from_conn_string(str(checkpoint_path)) as saver:
        graph = build_graph(checkpointer=saver)
        result = graph.invoke(
            initial,
            {"configurable": {"thread_id": thread_id}},
        )
    return dict(result["recommendation"])
