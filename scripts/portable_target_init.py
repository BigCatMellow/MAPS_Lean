#!/usr/bin/env python3
"""Preview or initialize only missing portable-v1 Markdown in an external Git repo.

Never installs dependencies, executes target code, alters Git settings, or grants
review/merge/task authority. Requires --apply for every write.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from pathlib import Path

from portable_target_preflight import PreflightError, inspect

DIRS = ("tasks", "reviews", "handoffs")
README = """# Portable MAPS convention

This directory belongs to this target repository, not to the sibling MAPS_L
clone. The roadmap is `roadmap.md`; task contracts, independent review notes,
and handoffs belong in their respective subdirectories. Existing files remain
authoritative. Initialization grants no new task, review, or merge authority.
"""


def initialize(maps_root: str, target_root: str, *, apply: bool = False) -> dict:
    """Validate first; on apply only create missing target-owned convention files.

    All writes are relative to opened directory descriptors with O_NOFOLLOW to
    avoid following target-controlled symlinks between inspection and creation.
    Existing files are never opened for writing.
    """
    report = inspect(maps_root, target_root)
    maps = Path(report["maps_clone_root"])
    target = Path(report["target_repo_root"])
    roadmap = (maps / "templates" / "portable-deployment"
               / "target-roadmap.md").read_bytes()
    planned = [
        ".maps/",
        ".maps/README.md",
        ".maps/roadmap.md",
        *[f".maps/{name}/" for name in DIRS],
    ]
    result = {
        "mode": "APPLY" if apply else "PREVIEW",
        "maps_clone_root": str(maps),
        "target_repo_root": str(target),
        "planned_paths": planned,
        "created": [],
        "existing": [],
        "limits": "Only missing target .maps convention; no project readiness or approval.",
    }
    if not apply:
        return result

    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    root_fd = os.open(target, directory_flags)
    try:
        try:
            os.mkdir(".maps", dir_fd=root_fd)
            result["created"].append(".maps/")
        except FileExistsError:
            result["existing"].append(".maps/")
        maps_fd = os.open(".maps", directory_flags, dir_fd=root_fd)
        try:
            for name in DIRS:
                try:
                    os.mkdir(name, dir_fd=maps_fd)
                    result["created"].append(f".maps/{name}/")
                except FileExistsError:
                    # Confirm existing entry is a real directory, not a link.
                    dfd = os.open(name, directory_flags, dir_fd=maps_fd)
                    os.close(dfd)
                    result["existing"].append(f".maps/{name}/")

            for name, data in (("README.md", README.encode("utf-8")),
                               ("roadmap.md", roadmap)):
                try:
                    fd = os.open(
                        name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                        0o644, dir_fd=maps_fd,
                    )
                except FileExistsError:
                    # A file may appear after preflight. Refuse a newly
                    # introduced symlink/non-regular file; never follow it.
                    old_fd = os.open(
                        name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=maps_fd
                    )
                    try:
                        if not stat.S_ISREG(os.fstat(old_fd).st_mode):
                            raise PreflightError(
                                f"unexpected convention path type: .maps/{name}"
                            )
                    finally:
                        os.close(old_fd)
                    result["existing"].append(f".maps/{name}")
                    continue
                with os.fdopen(fd, "wb") as output:
                    output.write(data)
                result["created"].append(f".maps/{name}")
        finally:
            os.close(maps_fd)
    finally:
        os.close(root_fd)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--maps-root", required=True)
    parser.add_argument("--target-repo", required=True)
    parser.add_argument("--apply", action="store_true",
                        help="create only missing .maps convention files")
    args = parser.parse_args(argv)
    try:
        result = initialize(args.maps_root, args.target_repo, apply=args.apply)
    except (PreflightError, OSError) as exc:
        print(f"portable init refused: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
