from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence

from .common import (
    HelperError,
    HelperResult,
    HelperRunStore,
    new_helper_run_id,
    new_result,
    validate_active_scope,
    validate_helper_run_id,
)


class AiderHelper:
    def __init__(
        self,
        *,
        executable: str | Path = "aider",
        git_executable: str | Path = "git",
        timeout_seconds: float = 900.0,
        run_store: HelperRunStore | None = None,
    ):
        self.executable = str(executable)
        self.git_executable = str(git_executable)
        self.timeout_seconds = timeout_seconds
        self.run_store = run_store or HelperRunStore()

    @staticmethod
    def _parse_porcelain_z(raw: bytes) -> set[str]:
        """Parse `git status --porcelain=v1 -z` without path quoting ambiguity."""
        items = raw.split(b"\0")
        changed: set[str] = set()
        index = 0
        while index < len(items):
            record = items[index]
            index += 1
            if not record:
                continue
            if len(record) < 4 or record[2:3] != b" ":
                raise HelperError("unexpected git porcelain record")
            status = record[:2].decode("ascii", errors="replace")
            path = record[3:].decode("utf-8", errors="surrogateescape")
            changed.add(path)
            if "R" in status or "C" in status:
                if index >= len(items) or not items[index]:
                    raise HelperError("git rename/copy record missing source path")
                source = items[index].decode("utf-8", errors="surrogateescape")
                index += 1
                changed.add(source)
        return changed

    def _git_changes(self, repo: Path) -> set[str]:
        result = subprocess.run(
            [
                self.git_executable,
                "-C",
                str(repo),
                "status",
                "--porcelain=v1",
                "-z",
                "--untracked-files=all",
            ],
            capture_output=True,
            shell=False,
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            message = result.stderr.decode("utf-8", errors="replace").strip()
            raise HelperError(message or "git status failed")
        return self._parse_porcelain_z(result.stdout)

    def run(
        self,
        *,
        task: Mapping[str, Any],
        repo: str | Path,
        targets: Sequence[str | Path],
        message: str,
        scope_summary: str,
        model: str | None = None,
        helper_run_id: str | None = None,
    ) -> HelperResult:
        if not targets:
            raise HelperError("at least one Aider target is required")
        if not message.strip():
            raise HelperError("Aider message cannot be empty")
        if not scope_summary.strip():
            raise HelperError("scope_summary is required")

        repo_path = Path(repo).resolve()
        resolved = [
            (Path(path) if Path(path).is_absolute() else repo_path / Path(path)).resolve()
            for path in targets
        ]
        validate_active_scope(task, resolved, repo=repo_path)
        resolved_helper_run_id = (
            validate_helper_run_id(helper_run_id)
            if helper_run_id is not None
            else new_helper_run_id()
        )

        # Attribution must be provable. With a dirty worktree, a path-set diff
        # cannot prove that Aider did not modify an already-dirty unrelated file.
        # Refuse rather than guess or auto-revert someone else's work.
        before_changes = self._git_changes(repo_path)
        if before_changes:
            raise HelperError(
                "Aider helper requires a clean worktree so its changes are attributable; "
                "existing changes: " + ", ".join(sorted(before_changes))
            )

        # Intentionally no generic extra-args escape hatch. The wrapper fixes
        # the safety-relevant Aider options and exposes only model + message.
        argv = [
            self.executable,
            "--message",
            message,
            "--no-auto-commits",
            "--no-dirty-commits",
            "--no-stream",
        ]
        if model:
            argv.extend(("--model", model))
        argv.extend(str(path.relative_to(repo_path)) for path in resolved)

        try:
            result = subprocess.run(
                argv,
                cwd=repo_path,
                text=True,
                capture_output=True,
                shell=False,
                timeout=self.timeout_seconds,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            raise HelperError(f"Aider unavailable/timeout: {exc}") from exc
        if result.returncode != 0:
            raise HelperError(result.stderr.strip() or f"aider exit {result.returncode}")

        after_changes = sorted(self._git_changes(repo_path))
        if after_changes:
            try:
                validate_active_scope(task, after_changes, repo=repo_path)
            except HelperError as exc:
                raise HelperError(
                    "Aider produced out-of-scope repository changes; do not auto-revert. "
                    "Inspect and repair manually. " + str(exc)
                ) from exc

        record = new_result(
            helper_run_id=resolved_helper_run_id,
            task_id=str(task["task_id"]),
            helper="aider" if not model else f"aider:{model}",
            status="completed",
            summary=scope_summary,
            output_paths=tuple(str(path.relative_to(repo_path)) for path in resolved),
        )
        self.run_store.append(record)
        return record
