from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence

from .common import HelperError, HelperResult, HelperRunStore, new_result, validate_active_scope


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

    def _git_changes(self, repo: Path, targets: Sequence[Path] | None = None) -> set[str]:
        argv = [self.git_executable, "-C", str(repo), "status", "--porcelain"]
        if targets is not None:
            argv.extend(("--", *[str(path.relative_to(repo)) for path in targets]))
        result = subprocess.run(
            argv,
            text=True,
            capture_output=True,
            shell=False,
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            raise HelperError(result.stderr.strip() or "git status failed")
        changed: set[str] = set()
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            path = line[3:].strip() if len(line) > 3 else line.strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            changed.add(path)
        return changed

    def run(
        self,
        *,
        task: Mapping[str, Any],
        repo: str | Path,
        targets: Sequence[str | Path],
        message: str,
        scope_summary: str,
        model: str | None = None,
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
        dirty_targets = self._git_changes(repo_path, resolved)
        if dirty_targets:
            raise HelperError(
                "Aider target has uncommitted changes: " + ", ".join(sorted(dirty_targets))
            )
        before_changes = self._git_changes(repo_path)

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

        after_changes = self._git_changes(repo_path)
        new_changes = sorted(after_changes - before_changes)
        if new_changes:
            try:
                validate_active_scope(task, new_changes, repo=repo_path)
            except HelperError as exc:
                raise HelperError(
                    "Aider produced out-of-scope repository changes; do not auto-revert. "
                    "Inspect and repair manually. " + str(exc)
                ) from exc

        record = new_result(
            task_id=str(task["task_id"]),
            helper="aider" if not model else f"aider:{model}",
            status="completed",
            summary=scope_summary,
            output_paths=tuple(str(path.relative_to(repo_path)) for path in resolved),
        )
        self.run_store.append(record)
        return record
