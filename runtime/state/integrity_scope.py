from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Sequence


class ExecutionScopeHardeningMixin:
    """Mechanical scope checks layered ahead of ExecutionIntegrityMixin.

    The run manifest remains evidence, not an OS sandbox. These checks make the
    declared writable/forbidden contract self-consistent and make post-run Git
    verification report both out-of-scope and explicitly forbidden changes.
    """

    @classmethod
    def _scopes_overlap(cls, left: str, right: str) -> bool:
        return cls._scope_contains(left, right) or cls._scope_contains(right, left)

    @classmethod
    def _validate_scope_contract(
        cls,
        *,
        readable: Sequence[str],
        writable: Sequence[str],
        forbidden: Sequence[str],
    ) -> tuple[str, ...]:
        issues: list[str] = []
        if not readable:
            issues.append("readable scope cannot be empty")
        if not writable:
            issues.append("writable scope cannot be empty")
        for path in writable:
            if not cls._covered_by_any(path, readable):
                issues.append(f"writable path is not readable: {path}")
            for blocked in forbidden:
                if cls._scopes_overlap(path, blocked):
                    issues.append(
                        f"writable path overlaps forbidden path: {path} <> {blocked}"
                    )
        return tuple(dict.fromkeys(issues))

    def verify_run_changes(
        self,
        run_id: str,
        changed_paths: Iterable[str | Path],
        *,
        repo_root: str | Path,
    ) -> dict[str, Any]:
        manifest = self.get_run_manifest(run_id)
        if manifest is None:
            return {
                "ok": False,
                "run_id": run_id,
                "reason": "run_not_found",
                "out_of_scope": [],
                "forbidden_changes": [],
            }
        try:
            changed = self._normalize_scopes(changed_paths, repo_root)
        except ValueError as exc:
            return {
                "ok": False,
                "run_id": run_id,
                "reason": "path_outside_repo",
                "error": str(exc),
                "out_of_scope": [],
                "forbidden_changes": [],
            }

        writable = tuple(manifest["writable_scope"])
        forbidden = tuple(manifest["forbidden_scope"])
        forbidden_changes = [
            path for path in changed if self._covered_by_any(path, forbidden)
        ]
        out_of_scope = [
            path for path in changed if not self._covered_by_any(path, writable)
        ]
        return {
            "ok": not out_of_scope and not forbidden_changes,
            "run_id": run_id,
            "changed_paths": list(changed),
            "writable_scope": list(writable),
            "forbidden_scope": list(forbidden),
            "out_of_scope": out_of_scope,
            "forbidden_changes": forbidden_changes,
        }
