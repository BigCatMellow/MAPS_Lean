from __future__ import annotations

from typing import Any


class RunSessionTraceMixin:
    """Derived trace enrichment for explicit append-only execution lineage."""

    def trace_task(self, task_id: str) -> dict[str, Any] | None:
        trace = super().trace_task(task_id)
        if trace is None:
            return None

        runs = trace.get("runs")
        if isinstance(runs, list):
            for run in runs:
                if isinstance(run, dict):
                    run_id = str(run.get("run_id") or "").strip()
                    if run_id:
                        run["session_lineage"] = self.resolve_run_session(run_id)
                        run["helper_lineage"] = self.list_run_helper_links(run_id)
                        run["recovery_lineage"] = self.list_run_recovery_links(run_id)
                    else:
                        run["session_lineage"] = None
                        run["helper_lineage"] = []
                        run["recovery_lineage"] = []

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
            coverage["run_helper_lineage"] = {
                "included": True,
                "complete": False,
                "source": "run_helper_links",
                "reason": (
                    "explicit MAPS run/helper invocation relationships are included; "
                    "legacy or external helper activity may remain unknown"
                ),
            }
            coverage["run_recovery_lineage"] = {
                "included": True,
                "complete": False,
                "source": "run_recovery_links",
                "reason": (
                    "explicit predecessor/replacement run relationships are included; "
                    "RecoveryStore incident state remains a separate evidence source"
                ),
            }
        return trace
