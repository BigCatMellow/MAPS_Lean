from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from runtime.operational_learning import OperationalLearningError, project_applicable_lessons
from runtime.state import TaskStore

_PATH_SUFFIXES = {
    ".cfg",
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".py",
    ".sh",
    ".sql",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}


def _looks_like_url(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme and parsed.netloc)


def _looks_like_path(value: str) -> bool:
    if value.startswith(("./", "../", "/")) or "/" in value or "\\" in value:
        return True
    return Path(value).suffix.lower() in _PATH_SUFFIXES


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _describe_reference(root: Path, value: str, role: str) -> dict[str, Any]:
    value = value.strip()
    if _looks_like_url(value):
        return {
            "role": role,
            "value": value,
            "kind": "reference",
            "status": "external_reference",
        }

    raw = Path(value)
    candidate = raw if raw.is_absolute() else root / raw
    resolved = candidate.resolve(strict=False)
    try:
        relative = resolved.relative_to(root)
    except ValueError:
        if _looks_like_path(value) or candidate.exists():
            return {
                "role": role,
                "value": value,
                "kind": "path",
                "status": "outside_repo",
            }
        return {
            "role": role,
            "value": value,
            "kind": "reference",
            "status": "descriptive_reference",
        }

    repo_path = relative.as_posix() or "."
    if resolved.is_file():
        return {
            "role": role,
            "value": value,
            "kind": "file",
            "status": "available",
            "path": repo_path,
            "sha256": _sha256(resolved),
            "bytes": resolved.stat().st_size,
        }
    if resolved.is_dir():
        return {
            "role": role,
            "value": value,
            "kind": "path",
            "status": "directory_not_expanded",
            "path": repo_path,
        }
    if _looks_like_path(value):
        return {
            "role": role,
            "value": value,
            "kind": "path",
            "status": "missing",
            "path": repo_path,
        }
    return {
        "role": role,
        "value": value,
        "kind": "reference",
        "status": "descriptive_reference",
    }


def _lesson_guidance(
    store: TaskStore, task: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Attributed GUIDANCE_ONLY evidence from operator-promoted ACTIVE lessons.

    Injection-0/1 (work/notes/2026-08-17-operational-learning-authority-design.md
    section 5): reuses `project_applicable_lessons()`'s existing shape and
    `GUIDANCE_ONLY` label verbatim; never merged into instructions/boundaries.
    Fails closed (empty guidance) rather than breaking the rest of the plan
    if lesson storage or projection is unavailable/invalid.
    """
    try:
        lessons = store.list_active_operational_lessons()
    except Exception:
        return [], []
    context = {
        "project_id": task["project_id"],
        "task_type": task["task_type"],
        "risk": task["risk"],
        "paths": list(task["output_paths"]),
    }
    at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    try:
        projection = project_applicable_lessons(lessons, context, at=at)
    except OperationalLearningError:
        return [], []
    return list(projection["projected"]), list(projection["withheld"])


def build_context_plan(
    store: TaskStore,
    task_id: str,
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any] | None:
    """Build a disposable context plan from explicit relationships only."""

    task = store.get_task(task_id)
    if task is None:
        return None
    root = Path(repo_root).resolve()
    if not root.is_dir():
        raise ValueError("repo_root must be a directory")

    authority: list[dict[str, Any]] = []
    agents = root / "AGENTS.md"
    if agents.is_file():
        authority.append(_describe_reference(root, "AGENTS.md", "authority"))

    required: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for role, values in (("input", task["inputs"]), ("source", task["sources"])):
        for value in values:
            key = (role, value)
            if key in seen:
                continue
            seen.add(key)
            if value.strip() == "AGENTS.md" and agents.is_file():
                continue
            required.append(_describe_reference(root, value, role))

    dependencies: list[dict[str, Any]] = []
    for dependency_id in task["dependencies"]:
        dependency = store.get_task(dependency_id)
        if dependency is None:
            dependencies.append(
                {
                    "task_id": dependency_id,
                    "status": "MISSING",
                    "agi_status": "UNKNOWN",
                }
            )
            continue
        dependencies.append(
            {
                "task_id": dependency_id,
                "status": dependency["status"],
                "agi_status": dependency["agi_status"],
                "title": dependency["title"],
                "outcome": dependency["outcome"],
            }
        )

    unresolved = [
        item
        for item in [*authority, *required]
        if item["status"] in {"missing", "outside_repo", "directory_not_expanded"}
    ]

    guidance, withheld_guidance = _lesson_guidance(store, task)

    return {
        "task_id": task_id,
        "task_revision": store.compute_task_revision(task_id),
        "authority": authority,
        "required": required,
        "guidance": guidance,
        "withheld_guidance": withheld_guidance,
        "dependencies": dependencies,
        "boundaries": {
            "decision_authority": task["decision_authority"],
            "output_paths": task["output_paths"],
            "non_goals": task["non_goals"],
            "acceptance_criteria": task["acceptance_criteria"],
            "stop_conditions": task["stop_conditions"],
            "verification": task["verification"],
            "evidence_expected": task["evidence_expected"],
            "review_required": task["review_required"],
            "escalation": task["escalation"],
        },
        "unresolved": unresolved,
        "coverage": {
            "explicit_task_relationships": True,
            "root_agents_authority": bool(authority),
            "file_contents_included": False,
            "semantic_retrieval_used": False,
            "repository_scan_used": False,
            "note": (
                "v1 identifies exact trustworthy inputs to read; it does not "
                "search for unreferenced context"
            ),
        },
    }
