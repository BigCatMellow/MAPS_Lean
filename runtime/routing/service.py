from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Iterable, Mapping

from runtime.policy.halt import HaltStore
from runtime.policy.models import WorkerProfile
from runtime.state import TaskStore
from .langgraph_runtime import run_checkpointed_route

if TYPE_CHECKING:
    from runtime.environment.fingerprint import CompatibilityReport


def route_project(
    store: TaskStore,
    workers: Iterable[WorkerProfile],
    *,
    project_id: str = "default",
    halt_path: str | Path = ".maps/state/halt.json",
    checkpoint_path: str | Path = ".maps/state/langgraph-checkpoints.db",
    thread_id: str | None = None,
    environment_reports: Mapping[str, CompatibilityReport] | None = None,
) -> dict:
    """Read canonical state and return a checkpointed recommendation.

    This function performs no task-state mutation.
    """
    tasks = store.list_tasks(
        project_id=project_id,
        statuses=("READY", "CHANGES_REQUESTED", "READY_FOR_REVIEW"),
    )
    halt = HaltStore(halt_path).load()
    return run_checkpointed_route(
        tasks=tasks,
        workers=list(workers),
        halt=halt,
        checkpoint_path=checkpoint_path,
        thread_id=thread_id or f"maps-routing:{project_id}",
        task_db_path=store.db_path,
        environment_reports=environment_reports,
    )
