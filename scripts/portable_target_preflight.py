#!/usr/bin/env python3
"""Read-only portable v1 target preflight. No writes, target execution, or imports."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

TARGET_PATHS = (
    ".maps/README.md",
    ".maps/roadmap.md",
    ".maps/tasks",
    ".maps/reviews",
    ".maps/handoffs",
)
TEMPLATES = (
    "target-task.md",
    "target-review-evidence.md",
    "target-roadmap.md",
)


class PreflightError(ValueError):
    """Untrusted or ambiguous root / convention path."""


def git_root(value: str, label: str) -> Path:
    if not value or not value.strip():
        raise PreflightError(f"{label}: explicit nonempty root required")
    supplied = Path(value).expanduser().absolute()
    try:
        root = supplied.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PreflightError(f"{label}: inaccessible root: {exc}") from exc
    if supplied != root:
        raise PreflightError(f"{label}: path must be canonical (no symlinks/..)")
    if not root.is_dir():
        raise PreflightError(f"{label}: not a directory")
    proc = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode:
        raise PreflightError(f"{label}: not an accessible Git worktree")
    try:
        top = Path(proc.stdout.strip()).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PreflightError(f"{label}: invalid Git worktree root: {exc}") from exc
    if top != root:
        raise PreflightError(f"{label}: must name Git worktree top level exactly")
    return root


def contained(root: Path, relative: str) -> Path:
    """Reject symlinked parents/leaves and paths escaping the inspected root."""
    candidate = root / relative
    current = root
    for part in Path(relative).parts:
        current = current / part
        if current.is_symlink():
            raise PreflightError(f"unsafe symlink in convention path: {relative}")
    resolved = candidate.resolve(strict=False)
    if not resolved.is_relative_to(root):
        raise PreflightError(f"convention path escapes root: {relative}")
    return candidate


def inspect(maps_root: str, target_root: str) -> dict:
    maps = git_root(maps_root, "MAPS_CLONE_ROOT")
    target = git_root(target_root, "TARGET_REPO_ROOT")
    if maps == target:
        raise PreflightError("MAPS_CLONE_ROOT and TARGET_REPO_ROOT must differ")
    if maps in target.parents or target in maps.parents:
        raise PreflightError("roots must not be nested")

    templates = maps / "templates" / "portable-deployment"
    for name in TEMPLATES:
        p = contained(maps, f"templates/portable-deployment/{name}")
        if not p.is_file():
            raise PreflightError(f"missing MAPS portable template: {name}")

    layout = {}
    for relative in TARGET_PATHS:
        p = contained(target, relative)
        expected_dir = relative in (
            ".maps/tasks", ".maps/reviews", ".maps/handoffs"
        )
        if not p.exists():
            state = "missing"
        elif p.is_dir() if expected_dir else p.is_file():
            state = "present"
        else:
            raise PreflightError(f"unexpected convention path type: {relative}")
        layout[relative] = state

    return {
        "mode": "READ_ONLY_PREFLIGHT",
        "maps_clone_root": str(maps),
        "target_repo_root": str(target),
        "target_layout": layout,
        "initialized": all(x == "present" for x in layout.values()),
        "limitations": (
            "Static path inspection only; no target task readiness, "
            "review independence, authority, CI, or execution verified."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--maps-root", required=True)
    parser.add_argument("--target-repo", required=True)
    args = parser.parse_args(argv)
    try:
        result = inspect(args.maps_root, args.target_repo)
    except (PreflightError, OSError) as exc:
        print(f"portable preflight refused: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
