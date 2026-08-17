from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from pathlib import Path
import re
import subprocess
from types import MappingProxyType
from typing import Callable, Mapping, Sequence

from .spec import EnvironmentSpec, NetworkMode


class ObservationState(str, Enum):
    OBSERVED = "OBSERVED"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class EnvironmentKind(str, Enum):
    LOCAL = "LOCAL"


class CompatibilityState(str, Enum):
    COMPATIBLE = "COMPATIBLE"
    COMPATIBLE_WITH_WARNINGS = "COMPATIBLE_WITH_WARNINGS"
    DRIFTED = "DRIFTED"
    INCOMPATIBLE = "INCOMPATIBLE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class CommandResult:
    found: bool
    returncode: int | None
    stdout: str = ""


CommandRunner = Callable[[Sequence[str]], CommandResult]


@dataclass(frozen=True, slots=True)
class VersionObservation:
    state: ObservationState
    version: str | None = None

    def __post_init__(self) -> None:
        if self.state == ObservationState.OBSERVED and not self.version:
            raise ValueError("OBSERVED version requires version text")
        if self.state != ObservationState.OBSERVED and self.version is not None:
            raise ValueError("non-observed version cannot carry version text")

    def to_dict(self) -> dict[str, str | None]:
        return {"state": self.state.value, "version": self.version}


@dataclass(frozen=True, slots=True)
class EnvironmentFingerprint:
    environment_spec_hash: str
    environment_kind: EnvironmentKind
    runtimes: Mapping[str, VersionObservation]
    tools: Mapping[str, VersionObservation]
    repo_revision: str | None
    worktree_dirty: bool | None
    dependency_hashes: Mapping[str, str | None]
    network_mode: NetworkMode
    allowed_domains: tuple[str, ...]
    service_availability: Mapping[str, bool | None]
    secret_availability: Mapping[str, bool | None]
    observed_at: str
    sha256: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "runtimes",
            MappingProxyType(dict(sorted(self.runtimes.items()))),
        )
        object.__setattr__(
            self,
            "tools",
            MappingProxyType(dict(sorted(self.tools.items()))),
        )
        object.__setattr__(
            self,
            "dependency_hashes",
            MappingProxyType(dict(sorted(self.dependency_hashes.items()))),
        )
        object.__setattr__(
            self,
            "service_availability",
            MappingProxyType(dict(sorted(self.service_availability.items()))),
        )
        object.__setattr__(
            self,
            "secret_availability",
            MappingProxyType(dict(sorted(self.secret_availability.items()))),
        )
        object.__setattr__(
            self,
            "allowed_domains",
            tuple(sorted(dict.fromkeys(domain.lower() for domain in self.allowed_domains))),
        )
        canonical = json.dumps(
            self._identity_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        object.__setattr__(self, "sha256", hashlib.sha256(canonical).hexdigest())

    def _identity_dict(self) -> dict[str, object]:
        return {
            "environment_spec_hash": self.environment_spec_hash,
            "environment_kind": self.environment_kind.value,
            "runtimes": {
                name: observation.to_dict()
                for name, observation in self.runtimes.items()
            },
            "tools": {
                name: observation.to_dict()
                for name, observation in self.tools.items()
            },
            "repo_revision": self.repo_revision,
            "worktree_dirty": self.worktree_dirty,
            "dependency_hashes": dict(self.dependency_hashes),
            "network": {
                "mode": self.network_mode.value,
                "allowed_domains": list(self.allowed_domains),
            },
            "service_availability": dict(self.service_availability),
            "secret_availability": dict(self.secret_availability),
        }

    def to_dict(self) -> dict[str, object]:
        payload = self._identity_dict()
        payload["observed_at"] = self.observed_at
        payload["sha256"] = self.sha256
        return payload


@dataclass(frozen=True, slots=True)
class CompatibilityReport:
    state: CompatibilityState
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    environment_spec_hash: str
    fingerprint_sha256: str
    reference_fingerprint_sha256: str | None = None

    @property
    def compatible(self) -> bool:
        return self.state in {
            CompatibilityState.COMPATIBLE,
            CompatibilityState.COMPATIBLE_WITH_WARNINGS,
        }

    def to_dict(self) -> dict[str, object]:
        return {
            "state": self.state.value,
            "compatible": self.compatible,
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
            "environment_spec_hash": self.environment_spec_hash,
            "fingerprint_sha256": self.fingerprint_sha256,
            "reference_fingerprint_sha256": self.reference_fingerprint_sha256,
        }


_VERSION_RE = re.compile(r"(?<!\d)(\d+(?:\.\d+){1,3})(?!\d)")
_CONSTRAINT_RE = re.compile(r"^(>=|<=|>|<|==)?\s*(\d+(?:\.\d+){0,3})$")


def _default_command_runner(argv: Sequence[str]) -> CommandResult:
    try:
        result = subprocess.run(
            list(argv),
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        return CommandResult(found=False, returncode=None)
    except (OSError, subprocess.SubprocessError):
        return CommandResult(found=True, returncode=None)
    output = (result.stdout or result.stderr or "").strip()
    return CommandResult(found=True, returncode=result.returncode, stdout=output)


def _extract_version(output: str) -> str | None:
    match = _VERSION_RE.search(output)
    return match.group(1) if match else None


def _observe_version(name: str, runner: CommandRunner) -> VersionObservation:
    result = runner((name, "--version"))
    if not result.found:
        return VersionObservation(ObservationState.MISSING)
    if result.returncode != 0:
        return VersionObservation(ObservationState.UNKNOWN)
    version = _extract_version(result.stdout)
    if version is None:
        return VersionObservation(ObservationState.UNKNOWN)
    return VersionObservation(ObservationState.OBSERVED, version)


def _git_fact(
    runner: CommandRunner,
    repo_root: Path,
    *args: str,
) -> CommandResult:
    return runner(("git", "-C", str(repo_root), *args))


def _file_sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iso_z(value: datetime) -> str:
    normalized = value.astimezone(timezone.utc).replace(microsecond=0)
    return normalized.isoformat().replace("+00:00", "Z")


def _declared_availability(
    declared_names: Sequence[str],
    supplied: Mapping[str, bool | None] | None,
    label: str,
) -> dict[str, bool | None]:
    values = dict(supplied or {})
    unknown_keys = sorted(set(values) - set(declared_names))
    if unknown_keys:
        raise ValueError(
            f"{label} supplied for undeclared names: " + ", ".join(unknown_keys)
        )
    for name, value in values.items():
        if value not in {True, False, None}:
            raise ValueError(f"{label} for {name} must be true, false, or unknown")
    return {name: values.get(name) for name in declared_names}


def inspect_local_environment(
    spec: EnvironmentSpec,
    *,
    repo_root: str | Path,
    command_runner: CommandRunner | None = None,
    network_mode: NetworkMode = NetworkMode.UNKNOWN,
    allowed_domains: Sequence[str] = (),
    service_availability: Mapping[str, bool | None] | None = None,
    secret_availability: Mapping[str, bool | None] | None = None,
    now: Callable[[], datetime] | None = None,
) -> EnvironmentFingerprint:
    """Collect bounded read-only facts for one local execution environment.

    The inspector reads only facts declared by `spec`. Credential capabilities are
    supplied as boolean/unknown availability; no secret values or environment dump
    are read or returned. Setup/validation commands are never executed here.
    """

    root = Path(repo_root).resolve()
    runner = command_runner or _default_command_runner

    runtimes = {name: _observe_version(name, runner) for name in spec.runtimes}
    tools = {name: _observe_version(name, runner) for name in spec.required_tools}

    revision_result = _git_fact(runner, root, "rev-parse", "HEAD")
    repo_revision = (
        revision_result.stdout.strip()
        if revision_result.found
        and revision_result.returncode == 0
        and revision_result.stdout.strip()
        else None
    )
    status_result = _git_fact(runner, root, "status", "--porcelain")
    worktree_dirty = (
        bool(status_result.stdout.strip())
        if status_result.found and status_result.returncode == 0
        else None
    )

    dependency_hashes = {
        relative: _file_sha256(root / relative) for relative in spec.dependency_inputs
    }

    services = _declared_availability(
        spec.services,
        service_availability,
        "service availability",
    )
    secrets = _declared_availability(
        spec.required_secret_names,
        secret_availability,
        "secret capability availability",
    )

    normalized_domains: list[str] = []
    for raw in allowed_domains:
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError("observed allowed_domains must contain non-empty domain names")
        value = raw.strip().lower()
        if "://" in value or "/" in value:
            raise ValueError("observed allowed_domains must contain domain names, not URLs")
        normalized_domains.append(value)

    timestamp = _iso_z((now or (lambda: datetime.now(timezone.utc)))())
    return EnvironmentFingerprint(
        environment_spec_hash=spec.sha256,
        environment_kind=EnvironmentKind.LOCAL,
        runtimes=runtimes,
        tools=tools,
        repo_revision=repo_revision,
        worktree_dirty=worktree_dirty,
        dependency_hashes=dependency_hashes,
        network_mode=network_mode,
        allowed_domains=tuple(normalized_domains),
        service_availability=services,
        secret_availability=secrets,
        observed_at=timestamp,
    )


def _parse_version(value: str) -> tuple[int, ...] | None:
    if not re.fullmatch(r"\d+(?:\.\d+){0,3}", value.strip()):
        return None
    return tuple(int(part) for part in value.split("."))


def _compare_versions(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    width = max(len(left), len(right))
    lhs = left + (0,) * (width - len(left))
    rhs = right + (0,) * (width - len(right))
    return (lhs > rhs) - (lhs < rhs)


def version_satisfies(observed: str, constraint: str) -> bool | None:
    """Evaluate the narrow v1 runtime-constraint syntax.

    Supported: `3.12`, `==3.12`, and comma-separated `< <= > >=` numeric clauses.
    Unsupported syntax returns None so callers surface UNKNOWN rather than guess.
    """

    observed_version = _parse_version(observed)
    if observed_version is None:
        return None
    clauses = [part.strip() for part in constraint.split(",") if part.strip()]
    if not clauses:
        return None

    for clause in clauses:
        match = _CONSTRAINT_RE.fullmatch(clause)
        if not match:
            return None
        operator = match.group(1)
        target_text = match.group(2)
        target = _parse_version(target_text)
        if target is None:
            return None
        if operator in {None, "=="}:
            if observed_version[: len(target)] != target:
                return False
            continue
        comparison = _compare_versions(observed_version, target)
        if operator == ">=" and comparison < 0:
            return False
        if operator == ">" and comparison <= 0:
            return False
        if operator == "<=" and comparison > 0:
            return False
        if operator == "<" and comparison >= 0:
            return False
    return True


def evaluate_environment_compatibility(
    spec: EnvironmentSpec,
    observed: EnvironmentFingerprint,
    *,
    reference: EnvironmentFingerprint | None = None,
) -> CompatibilityReport:
    incompatible: list[str] = []
    drifted: list[str] = []
    unknown: list[str] = []
    warnings: list[str] = []

    if observed.environment_spec_hash != spec.sha256:
        drifted.append("ENVIRONMENT_SPEC_HASH_MISMATCH")
    if reference is not None and reference.environment_spec_hash != spec.sha256:
        drifted.append("REFERENCE_SPEC_HASH_MISMATCH")

    for name, constraint in spec.runtimes.items():
        item = observed.runtimes.get(name)
        if item is None or item.state == ObservationState.UNKNOWN:
            unknown.append(f"RUNTIME_UNKNOWN:{name}")
            continue
        if item.state == ObservationState.MISSING:
            incompatible.append(f"RUNTIME_MISSING:{name}")
            continue
        assert item.version is not None
        satisfies = version_satisfies(item.version, constraint)
        if satisfies is None:
            unknown.append(f"RUNTIME_CONSTRAINT_UNSUPPORTED:{name}")
        elif not satisfies:
            incompatible.append(f"RUNTIME_INCOMPATIBLE:{name}")
        if reference is not None:
            prior = reference.runtimes.get(name)
            if (
                prior is not None
                and prior.state == ObservationState.OBSERVED
                and prior.version != item.version
                and satisfies is True
            ):
                warnings.append(f"RUNTIME_VERSION_CHANGED:{name}")

    for name in spec.required_tools:
        item = observed.tools.get(name)
        if item is None or item.state == ObservationState.UNKNOWN:
            unknown.append(f"TOOL_VERSION_UNKNOWN:{name}")
            continue
        if item.state == ObservationState.MISSING:
            incompatible.append(f"TOOL_MISSING:{name}")
            continue
        if reference is not None:
            prior = reference.tools.get(name)
            if (
                prior is not None
                and prior.state == ObservationState.OBSERVED
                and prior.version != item.version
            ):
                warnings.append(f"TOOL_VERSION_CHANGED:{name}")

    if spec.repository.base_revision is not None:
        if observed.repo_revision is None:
            unknown.append("REPO_REVISION_UNKNOWN")
        elif observed.repo_revision != spec.repository.base_revision:
            drifted.append("REPO_BASE_REVISION_DRIFT")
    if spec.repository.require_clean_worktree:
        if observed.worktree_dirty is None:
            unknown.append("WORKTREE_STATE_UNKNOWN")
        elif observed.worktree_dirty:
            drifted.append("WORKTREE_DIRTY")

    if reference is not None:
        if reference.repo_revision is None or observed.repo_revision is None:
            unknown.append("REFERENCE_REPO_REVISION_UNKNOWN")
        elif reference.repo_revision != observed.repo_revision:
            drifted.append("REPO_REVISION_CHANGED")
        if (
            not spec.repository.require_clean_worktree
            and reference.worktree_dirty is not None
            and observed.worktree_dirty is not None
            and reference.worktree_dirty != observed.worktree_dirty
        ):
            warnings.append("WORKTREE_DIRTY_STATE_CHANGED")

    for path in spec.dependency_inputs:
        current_hash = observed.dependency_hashes.get(path)
        if current_hash is None:
            incompatible.append(f"DEPENDENCY_INPUT_MISSING:{path}")
            continue
        if reference is not None:
            prior_hash = reference.dependency_hashes.get(path)
            if prior_hash is None:
                unknown.append(f"REFERENCE_DEPENDENCY_UNKNOWN:{path}")
            elif prior_hash != current_hash:
                drifted.append(f"DEPENDENCY_INPUT_CHANGED:{path}")

    if spec.network_mode == NetworkMode.UNKNOWN:
        unknown.append("SPEC_NETWORK_REQUIREMENT_UNKNOWN")
    elif spec.network_mode == NetworkMode.NOT_REQUIRED:
        if observed.network_mode in {
            NetworkMode.REQUIRED_GENERAL,
            NetworkMode.REQUIRED_RESTRICTED,
        }:
            warnings.append("NETWORK_BROADER_THAN_REQUIRED")
    elif spec.network_mode == NetworkMode.REQUIRED_GENERAL:
        if observed.network_mode == NetworkMode.UNKNOWN:
            unknown.append("NETWORK_MODE_UNKNOWN")
        elif observed.network_mode != NetworkMode.REQUIRED_GENERAL:
            incompatible.append("GENERAL_NETWORK_NOT_AVAILABLE")
    elif spec.network_mode == NetworkMode.REQUIRED_RESTRICTED:
        if observed.network_mode == NetworkMode.UNKNOWN:
            unknown.append("NETWORK_MODE_UNKNOWN")
        elif observed.network_mode == NetworkMode.NOT_REQUIRED:
            incompatible.append("RESTRICTED_NETWORK_NOT_AVAILABLE")
        elif observed.network_mode == NetworkMode.REQUIRED_GENERAL:
            warnings.append("NETWORK_BROADER_THAN_REQUIRED")
        else:
            missing_domains = sorted(
                set(spec.allowed_domains) - set(observed.allowed_domains)
            )
            if missing_domains:
                incompatible.append(
                    "NETWORK_DOMAINS_MISSING:" + ",".join(missing_domains)
                )

    for name in spec.required_secret_names:
        state = observed.secret_availability.get(name)
        if state is False:
            incompatible.append(f"SECRET_CAPABILITY_MISSING:{name}")
        elif state is None:
            unknown.append(f"SECRET_CAPABILITY_UNKNOWN:{name}")

    for name in spec.services:
        state = observed.service_availability.get(name)
        if state is False:
            incompatible.append(f"SERVICE_MISSING:{name}")
        elif state is None:
            unknown.append(f"SERVICE_UNKNOWN:{name}")

    if incompatible:
        state = CompatibilityState.INCOMPATIBLE
        reasons = tuple(sorted(dict.fromkeys(incompatible + drifted + unknown)))
    elif drifted:
        state = CompatibilityState.DRIFTED
        reasons = tuple(sorted(dict.fromkeys(drifted + unknown)))
    elif unknown:
        state = CompatibilityState.UNKNOWN
        reasons = tuple(sorted(dict.fromkeys(unknown)))
    elif warnings:
        state = CompatibilityState.COMPATIBLE_WITH_WARNINGS
        reasons = ()
    else:
        state = CompatibilityState.COMPATIBLE
        reasons = ()

    return CompatibilityReport(
        state=state,
        reasons=reasons,
        warnings=tuple(sorted(dict.fromkeys(warnings))),
        environment_spec_hash=spec.sha256,
        fingerprint_sha256=observed.sha256,
        reference_fingerprint_sha256=reference.sha256 if reference else None,
    )
