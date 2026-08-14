from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence

from .common import HelperError, HelperResult, HelperRunStore, new_result, validate_active_scope

FORBIDDEN_FLAGS = {"--yes", "--yes-always", "--auto-commits", "--dirty-commits"}


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

    def _dirty_targets(self, repo: Path, targets: Sequence[Path]) -> list[str]:
        result = subprocess.run(
            [
                self.git_executable,
                "-C",
                str(repo),
                "status",
                "--porcelain",
                "--",
                *[str(path.relative_to(repo)) for path in targets],
            ],
            text=True,
            capture_output=True,
            shell=False,
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            raise HelperError(result.stderr.strip() or "git status failed")
        return [line[3:].strip() if len(line) > 3 else line.strip() for line in result.stdout.splitlines() if line.strip()]

    @staticmethod
    def _validate_extra_args(args: Sequence[str]) -> None:
        bad = [
            arg
            for arg in args
            if arg in FORBIDDEN_FLAGS
            or arg.startswith("--yes=")
            or arg.startswith("--yes-always=")
            or arg.startswith("--auto-commits=")
            or arg.startswith("--dirty-commits=")
        ]
        if bad:
            raise HelperError("forbidden Aider flag(s): " + ", ".join(bad))

    def run(
        self,
        *,
        task: Mapping[str, Any],
        repo: str | Path,
        targets: Sequence[str | Path],
        message: str,
        scope_summary: str,
        model: str | None = None,
        extra_args: Sequence[str] = (),
    ) -> HelperResult:
        if not targets:
            raise HelperError("at least one Aider target is required")
        if not message.strip():
            raise HelperError("Aider message cannot be empty")
        if not scope_summary.strip():
            raise HelperError("scope_summary is required")
        self._validate_extra_args(extra_args)

        repo_path = Path(repo).resolve()
        resolved = [
            (Path(path) if Path(path).is_absolute() else repo_path / Path(path)).resolve()
            for path in targets
        ]
        validate_active_scope(task, resolved, repo=repo_path)
        dirty = self._dirty_targets(repo_path, resolved)
        if dirty:
            raise HelperError("Aider target has uncommitted changes: " + ", ".join(dirty))

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
        argv.extend(extra_args)
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

        record = new_result(
            task_id=str(task["task_id"]),
            helper="aider" if not model else f"aider:{model}",
            status="completed",
            summary=scope_summary,
            output_paths=tuple(str(path.relative_to(repo_path)) for path in resolved),
        )
        self.run_store.append(record)
        return record
