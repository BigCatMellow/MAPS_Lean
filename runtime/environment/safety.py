from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from . import fingerprint as _fingerprint_module
from .fingerprint import EnvironmentFingerprint, inspect_local_environment as _inspect_local_environment
from .spec import EnvironmentSpec, NetworkMode


def _validate_dependency_containment(spec: EnvironmentSpec, repo_root: str | Path) -> Path:
    """Reject dependency inputs that escape or traverse symlinks from the repo."""

    root = Path(repo_root).resolve()
    for relative in spec.dependency_inputs:
        candidate = root / relative
        cursor = root
        try:
            for part in Path(relative).parts:
                cursor = cursor / part
                if cursor.is_symlink():
                    raise ValueError("dependency input traverses a symlink")
            resolved = candidate.resolve(strict=False)
            resolved.relative_to(root)
        except (OSError, RuntimeError, ValueError) as exc:
            raise ValueError(
                f"dependency input resolves outside repository boundary: {relative}"
            ) from exc
    return root


def inspect_local_environment(
    spec: EnvironmentSpec,
    *,
    repo_root: str | Path,
    command_runner: Any = None,
    network_mode: NetworkMode = NetworkMode.UNKNOWN,
    allowed_domains: Sequence[str] = (),
    service_availability: Mapping[str, bool | None] | None = None,
    secret_availability: Mapping[str, bool | None] | None = None,
    now: Any = None,
) -> EnvironmentFingerprint:
    """Collect a local fingerprint without following dependency inputs outside the repo."""

    root = _validate_dependency_containment(spec, repo_root)
    return _inspect_local_environment(
        spec,
        repo_root=root,
        command_runner=command_runner,
        network_mode=network_mode,
        allowed_domains=allowed_domains,
        service_availability=service_availability,
        secret_availability=secret_availability,
        now=now,
    )


# Ensure direct imports from runtime.environment.fingerprint receive the same
# containment-checked public implementation after package initialization.
_fingerprint_module.inspect_local_environment = inspect_local_environment
