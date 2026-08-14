from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
from typing import Any, Mapping

from .common import HelperError, HelperResult, HelperRunStore, new_result, validate_active_scope

_MODEL = re.compile(r"^[A-Za-z0-9_.:/-]+$")


class OllamaHelper:
    def __init__(
        self,
        *,
        executable: str | Path = "ollama",
        host: str | None = None,
        timeout_seconds: float = 180.0,
        run_store: HelperRunStore | None = None,
    ):
        self.executable = str(executable)
        self.host = host
        self.timeout_seconds = timeout_seconds
        self.run_store = run_store or HelperRunStore()

    def environment(self) -> dict[str, str]:
        env = os.environ.copy()
        if self.host:
            env["OLLAMA_HOST"] = self.host
        return env

    def health(self) -> None:
        try:
            result = subprocess.run(
                [self.executable, "ls"],
                text=True,
                capture_output=True,
                shell=False,
                env=self.environment(),
                timeout=15,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            raise HelperError(f"Ollama unavailable: {exc}") from exc
        if result.returncode != 0:
            raise HelperError(result.stderr.strip() or "ollama ls failed")

    def run(
        self,
        *,
        task: Mapping[str, Any],
        repo: str | Path,
        model: str,
        prompt: str,
        output_path: str | Path,
        scope_summary: str,
    ) -> HelperResult:
        model = model.strip()
        if not _MODEL.fullmatch(model):
            raise HelperError(f"invalid Ollama model name: {model!r}")
        if not prompt.strip():
            raise HelperError("prompt cannot be empty")
        if not scope_summary.strip():
            raise HelperError("scope_summary is required")
        validate_active_scope(task, [output_path], repo=repo)
        self.health()

        try:
            result = subprocess.run(
                [self.executable, "run", model],
                input=prompt,
                text=True,
                capture_output=True,
                shell=False,
                env=self.environment(),
                timeout=self.timeout_seconds,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            raise HelperError(f"ollama run failed: {exc}") from exc
        if result.returncode != 0:
            raise HelperError(result.stderr.strip() or f"ollama run exit {result.returncode}")

        repo_path = Path(repo).resolve()
        target = Path(output_path)
        if not target.is_absolute():
            target = repo_path / target
        target = target.resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(result.stdout, encoding="utf-8")

        record = new_result(
            task_id=str(task["task_id"]),
            helper=f"ollama:{model}",
            status="completed",
            summary=scope_summary,
            output_paths=(str(target.relative_to(repo_path)),),
        )
        self.run_store.append(record)
        return record
