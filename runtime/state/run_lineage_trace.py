from __future__ import annotations

from typing import Any


class RunSessionTraceMixin:
    """Derived trace enrichment for append-only run/session lineage."""

    def trace_task(self, task_id: str) -> dict[str, Any] | None:
        trace = super().trace_task(task_id)
        if trace is None:
            return None

        runs = trace.get("runs")
        if isinstance(runs, list):
            for run in runs:
                if isinstance(run, dict):
                    run_id = str(run.get("run_id") or "").strip()
                    run["session_lineage"] = (
                        self.resolve_run_session(run_id) if run_id else None
                    )

        coverage = trace.setdefault("coverage", {})
        if isinstance(coverage, dict):
            coverage["run_session_lineage"] = {
                "included": True,
                "complete": False,
                "source": "run_session_links",
                "reason": (
                    "explicit MAPS run/session relationships are included; "
                    "absence does not prove that no external provider session existed"
                ),
            }
        return trace
