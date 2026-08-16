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

        submission_attribution = self.submission_run_attribution(task_id)
        trace["submission_run_lineage"] = submission_attribution["attempts"]

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
            coverage["submission_run_lineage"] = {
                "included": True,
                "complete": bool(submission_attribution["complete"]),
                "source": "submission_run_links",
                "reason": (
                    "each known submission attempt is explicit or UNKNOWN; "
                    "unlinked legacy/omitted attempts are never inferred from timing or run count"
                ),
            }
        return trace
