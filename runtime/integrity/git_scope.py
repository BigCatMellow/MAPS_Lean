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


def _name_status_paths(raw: bytes) -> set[str]:
    """Parse `git diff --name-status -z`, preserving both sides of renames.

    `--name-only` reports only the destination for a detected rename, which can
    hide a deletion/move out of a forbidden or otherwise protected scope.
    """
    items = raw.split(b"\0")
    paths: set[str] = set()
    index = 0
    while index < len(items):
        status_raw = items[index]
        index += 1
        if not status_raw:
            continue
        status = status_raw.decode("ascii", errors="replace")
        if index >= len(items) or not items[index]:
            raise RuntimeError("git name-status output ended before path")
        first = items[index].decode("utf-8", errors="surrogateescape")
        index += 1
        paths.add(first)
        if status[:1] in {"R", "C"}:
            if index >= len(items) or not items[index]:
                raise RuntimeError("git rename/copy output ended before destination path")
            second = items[index].decode("utf-8", errors="surrogateescape")
            index += 1
            paths.add(second)
    return paths


def _resolved_git_path(repo: Path, raw: str) -> str:
    path = Path(raw)
    if not path.is_absolute():
        path = repo / path
    return str(path.resolve())


def collect_git_worktree_identity(repo_root: str | Path) -> dict[str, str]:
    """Return immutable-ish local Git worktree identity without mutating Git."""
    repo = Path(repo_root).resolve()
    top = Path(
        _git(repo, "rev-parse", "--show-toplevel")
        .decode("utf-8", errors="replace")
        .strip()
    ).resolve()
    if top != repo:
        raise RuntimeError(f"repo_root must be Git top-level: {top}")

    git_common_dir = _git(repo, "rev-parse", "--git-common-dir").decode(
        "utf-8", errors="replace"
    ).strip()
    git_dir = _git(repo, "rev-parse", "--git-dir").decode(
        "utf-8", errors="replace"
    ).strip()
    worktree_private_dir = _git(repo, "rev-parse", "--git-path", ".").decode(
        "utf-8", errors="replace"
    ).strip()
    head_revision = _git(repo, "rev-parse", "--verify", "HEAD^{commit}").decode(
        "utf-8", errors="replace"
    ).strip()

    return {
        "repo_root": str(top),
        "git_common_dir": _resolved_git_path(repo, git_common_dir),
        "git_dir": _resolved_git_path(repo, git_dir),
        "worktree_private_dir": _resolved_git_path(repo, worktree_private_dir),
        "head_revision": head_revision,
    }


WORKTREE_IDENTITY_FIELDS = (
    "repo_root",
    "git_common_dir",
    "git_dir",
    "worktree_private_dir",
)


def compare_worktree_identity(
    expected: dict[str, Any], actual: dict[str, Any]
) -> dict[str, Any]:
    """Single definition of "same Git worktree".

    Compares only the immutable identity fields (not ``head_revision``, which
    moves with normal work). Returns ``{"status": "match"}`` or
    ``{"status": "mismatch", "worktree_mismatch": {...}}`` where the detail
    mapping carries ``expected_<field>`` / ``actual_<field>`` keys for every
    field in :data:`WORKTREE_IDENTITY_FIELDS`.
    """
    if any(
        expected.get(field) != actual.get(field)
        for field in WORKTREE_IDENTITY_FIELDS
    ):
        detail = {
            f"expected_{field}": expected.get(field)
            for field in WORKTREE_IDENTITY_FIELDS
        }
        detail |= {
            f"actual_{field}": actual.get(field)
            for field in WORKTREE_IDENTITY_FIELDS
        }
        return {"status": "mismatch", "worktree_mismatch": detail}
    return {"status": "match"}


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
    changed = _name_status_paths(
        _git(repo, "diff", "--name-status", "-z", base, "--")
    )
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
            "forbidden_changes": [],
        }
    expected = manifest.get("worktree")
    if isinstance(expected, dict):
        try:
            actual = collect_git_worktree_identity(repo_root)
        except RuntimeError as exc:
            return {
                "ok": False,
                "run_id": run_id,
                "reason": "worktree_unavailable",
                "error": str(exc),
                "changed_paths": [],
                "out_of_scope": [],
                "forbidden_changes": [],
                "worktree_binding": "unavailable",
            }
        comparison = compare_worktree_identity(expected, actual)
        if comparison["status"] == "mismatch":
            return {
                "ok": False,
                "run_id": run_id,
                "reason": "worktree_mismatch",
                "changed_paths": [],
                "out_of_scope": [],
                "forbidden_changes": [],
                "worktree_binding": "mismatch",
                "worktree_mismatch": comparison["worktree_mismatch"],
            }
    changed = collect_git_changes(
        repo_root,
        base_revision=manifest.get("base_revision"),
    )
    result = store.verify_run_changes(run_id, changed, repo_root=repo_root)
    result["base_revision"] = manifest.get("base_revision") or "HEAD"
    result["worktree_binding"] = "verified" if isinstance(expected, dict) else "missing"
    return result
