from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import subprocess
from typing import Callable, Mapping, Sequence

from runtime.harness.hooks import HookDirective, HookOutcome
from runtime.harness.types import OperationResult, RetryDisposition
from runtime.state.observability import redact_sensitive_text

from .spec import EnvironmentSpec

_TIERS = ("quick", "normal", "full")


class ValidationTierError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class CommandOutcome:
    command: str
    found: bool
    returncode: int | None
    output: str

    @property
    def passed(self) -> bool:
        return self.found and self.returncode == 0

    def to_dict(self) -> dict[str, object]:
        return {
            "command": self.command,
            "found": self.found,
            "returncode": self.returncode,
            "output": self.output,
            "passed": self.passed,
        }


CommandExecutor = Callable[[str, Path], CommandOutcome]


def _default_executor(command: str, repo_root: Path) -> CommandOutcome:
    # command is one EnvironmentSpec.validation.<tier> entry: operator-declared
    # trusted content (same trust boundary as setup_commands/maintenance_commands),
    # never caller/task-supplied input. shell=True is required because real tier
    # commands rely on shell syntax (e.g. "VAR=value some-command ..." env-var
    # prefixes) that plain argv execution cannot express.
    try:
        result = subprocess.run(
            command,
            shell=True,  # nosec B602
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=600,
        )
    except FileNotFoundError:
        return CommandOutcome(command=command, found=False, returncode=None, output="")
    except subprocess.SubprocessError as exc:
        return CommandOutcome(command=command, found=True, returncode=None, output=str(exc))
    output = (result.stdout or "") + (result.stderr or "")
    return CommandOutcome(
        command=command, found=True, returncode=result.returncode, output=output.strip()
    )


def _redact_outcome(outcome: CommandOutcome) -> CommandOutcome:
    """Apply the shared secret-redaction boundary regardless of which executor ran.

    Redaction must not depend on a particular `CommandExecutor` implementation
    remembering to call it, so it is applied here, once, to every outcome.
    """

    return CommandOutcome(
        command=outcome.command,
        found=outcome.found,
        returncode=outcome.returncode,
        output=redact_sensitive_text(outcome.output),
    )


@dataclass(frozen=True, slots=True)
class ValidationTierResult:
    tier: str
    environment_spec_hash: str
    passed: bool
    ran: tuple[CommandOutcome, ...] = field(default_factory=tuple)
    skipped: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "tier": self.tier,
            "environment_spec_hash": self.environment_spec_hash,
            "passed": self.passed,
            "ran": [outcome.to_dict() for outcome in self.ran],
            "skipped": list(self.skipped),
        }

    def to_operation_result(self) -> OperationResult:
        data = self.to_dict()
        if self.passed:
            return OperationResult.success(
                "VALIDATION_PASSED",
                f"All declared {self.tier} validation commands passed.",
                data=data,
                retry=RetryDisposition.SAFE,
            )
        failing = next((outcome for outcome in self.ran if not outcome.passed), None)
        summary = (
            f"{self.tier} validation command failed: {failing.command}"
            if failing is not None
            else f"{self.tier} validation did not complete."
        )
        return OperationResult.failure(
            "VALIDATION_FAILED",
            summary,
            data=data,
            retry=RetryDisposition.UNSAFE,
        )


def run_validation_tier(
    spec: EnvironmentSpec,
    tier: str,
    *,
    repo_root: str | Path,
    executor: CommandExecutor | None = None,
) -> ValidationTierResult:
    """Run one EnvironmentSpec-declared validation tier, stopping at first failure.

    Commands are declared, trusted operator/environment-authoring content (the
    same trust boundary `EnvironmentSpec.setup_commands` already relies on),
    not caller input. Output is best-effort secret-redacted before being kept
    as evidence.
    """

    if tier not in _TIERS:
        raise ValidationTierError(f"tier must be one of {_TIERS}, got {tier!r}")
    commands = getattr(spec.validation, tier)
    root = Path(repo_root).resolve()
    if not root.is_dir():
        raise ValidationTierError("repo_root must be a directory")
    run = executor or _default_executor

    ran: list[CommandOutcome] = []
    for index, command in enumerate(commands):
        outcome = _redact_outcome(run(command, root))
        ran.append(outcome)
        if not outcome.passed:
            return ValidationTierResult(
                tier=tier,
                environment_spec_hash=spec.sha256,
                passed=False,
                ran=tuple(ran),
                skipped=tuple(commands[index + 1 :]),
            )
    return ValidationTierResult(
        tier=tier, environment_spec_hash=spec.sha256, passed=True, ran=tuple(ran)
    )


def make_validation_hook(
    spec: EnvironmentSpec,
    tier: str,
    *,
    repo_root: str | Path,
    executor: CommandExecutor | None = None,
) -> Callable[[Mapping[str, object]], HookOutcome]:
    """Build a Hook callback that runs one declared validation tier on invocation.

    The returned callback ignores its Hook context; it exists to let trusted
    composition code register immediate (`tier="quick"`) or review-time
    (`tier="full"`) validation against one EnvironmentSpec at a chosen Hook
    event (e.g. `AFTER_WRITE`), per Harness Mechanics H4 / Environment &
    Reproducibility E4. It only narrows (DENY/ANNOTATE); it never grants
    authority the registry did not already have.
    """

    def _callback(_context: Mapping[str, object]) -> HookOutcome:
        result = run_validation_tier(spec, tier, repo_root=repo_root, executor=executor)
        if result.passed:
            return HookOutcome(
                HookDirective.ALLOW,
                annotations={"validation_tier": result.to_dict()},
            )
        failing = next((outcome for outcome in result.ran if not outcome.passed), None)
        reason = (
            f"{tier} validation command failed: {failing.command}"
            if failing is not None
            else f"{tier} validation did not complete."
        )
        return HookOutcome(
            HookDirective.DENY,
            reason=reason,
            annotations={"validation_tier": result.to_dict()},
        )

    return _callback
