from __future__ import annotations

import os
from pathlib import Path
from typing import Any, TypedDict

from runtime.policy.halt import HaltRecord
from runtime.policy.models import WorkerProfile
from .router import recommend_route


class RoutingState(TypedDict, total=False):
    tasks: list[dict[str, Any]]
    workers: list[dict[str, Any]]
    halt: dict[str, Any]
    recommendation: dict[str, Any]


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
        recommendation = recommend_route(state.get("tasks", []), workers, halt)
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
    with SqliteSaver.from_conn_string(str(checkpoint_path)) as saver:
        graph = build_graph(checkpointer=saver)
        result = graph.invoke(
            initial,
            {"configurable": {"thread_id": thread_id}},
        )
    return dict(result["recommendation"])
