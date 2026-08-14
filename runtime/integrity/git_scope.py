from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any


def _git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        shell=False,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(message or f"git {' '.join(args)} failed")
    return result.stdout


def _nul_paths(raw: bytes) -> set[str]:
    return {
        item.decode("utf-8", errors="surrogateescape")
        for item in raw.split(b"\0")
        if item
    }


def collect_git_changes(
    repo_root: str | Path,
    *,
    base_revision: str | None = None,
) -> set[str]:
    """Return changed/untracked paths without modifying the repository."""
    repo = Path(repo_root).resolve()
    top = Path(
        _git(repo, "rev-parse", "--show-toplevel")
        .decode("utf-8", errors="replace")
        .strip()
    ).resolve()
    if top != repo:
        raise RuntimeError(f"repo_root must be Git top-level: {top}")

    base = base_revision or "HEAD"
    _git(repo, "rev-parse", "--verify", f"{base}^{{commit}}")
    changed = _nul_paths(_git(repo, "diff", "--name-only", "-z", base, "--"))
    changed.update(
        _nul_paths(_git(repo, "ls-files", "--others", "--exclude-standard", "-z"))
    )
    return changed


def verify_git_run(store: Any, run_id: str, *, repo_root: str | Path) -> dict:
    """Compare the current Git worktree to one frozen run scope.

    Report only. Never reset, checkout, restore, clean, or otherwise repair the
    worktree automatically.
    """
    manifest = store.get_run_manifest(run_id)
    if manifest is None:
        return {
            "ok": False,
            "run_id": run_id,
            "reason": "run_not_found",
            "changed_paths": [],
            "out_of_scope": [],
        }
    changed = collect_git_changes(
        repo_root,
        base_revision=manifest.get("base_revision"),
    )
    result = store.verify_run_changes(run_id, changed, repo_root=repo_root)
    result["base_revision"] = manifest.get("base_revision") or "HEAD"
    return result
