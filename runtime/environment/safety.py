from __future__ import annotations

import hashlib
import os
from pathlib import Path
import stat
from types import SimpleNamespace
from typing import Any, Mapping, Sequence

from . import fingerprint as _fingerprint_module
from .fingerprint import (
    EnvironmentFingerprint,
    inspect_local_environment as _inspect_local_environment,
)
from .spec import EnvironmentSpec, NetworkMode


def _validate_dependency_containment(spec: EnvironmentSpec, repo_root: str | Path) -> Path:
    """Reject dependency inputs that already escape or traverse symlinks."""

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


def _safe_dependency_sha256(root: Path, relative: str) -> str | None:
    """Hash one dependency without following any path component symlink.

    Directory descriptors anchor traversal beneath the already-open repository.
    The final hash is read from the opened file descriptor, so path replacement
    after opening cannot redirect the read to another file.
    """

    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if nofollow is None or directory is None:
        raise ValueError(
            "platform cannot safely inspect dependency inputs without no-follow directory opens"
        )

    root_fd: int | None = None
    current_fd: int | None = None
    file_fd: int | None = None
    try:
        root_fd = os.open(
            str(root),
            os.O_RDONLY | directory | nofollow,
        )
        current_fd = root_fd
        parts = Path(relative).parts
        if not parts:
            raise ValueError("dependency input path is empty")

        for part in parts[:-1]:
            next_fd = os.open(
                part,
                os.O_RDONLY | directory | nofollow,
                dir_fd=current_fd,
            )
            if current_fd != root_fd:
                os.close(current_fd)
            current_fd = next_fd

        try:
            file_fd = os.open(
                parts[-1],
                os.O_RDONLY | nofollow,
                dir_fd=current_fd,
            )
        except FileNotFoundError:
            return None

        info = os.fstat(file_fd)
        if not stat.S_ISREG(info.st_mode):
            return None

        digest = hashlib.sha256()
        while True:
            chunk = os.read(file_fd, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        return digest.hexdigest()
    except FileNotFoundError:
        return None
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError(
            f"dependency input could not be opened safely within repository boundary: {relative}"
        ) from exc
    finally:
        if file_fd is not None:
            os.close(file_fd)
        if current_fd is not None and current_fd != root_fd:
            os.close(current_fd)
        if root_fd is not None:
            os.close(root_fd)


def _safe_dependency_hashes(
    spec: EnvironmentSpec,
    root: Path,
) -> dict[str, str | None]:
    return {
        relative: _safe_dependency_sha256(root, relative)
        for relative in spec.dependency_inputs
    }


def _probe_view_without_dependency_reads(spec: EnvironmentSpec) -> SimpleNamespace:
    """Expose only fields consumed by the lower-level inspector.

    `sha256` remains the real full EnvironmentSpec identity while dependency
    inputs are empty so the lower-level pathname reader cannot run.
    """

    return SimpleNamespace(
        sha256=spec.sha256,
        runtimes=spec.runtimes,
        required_tools=spec.required_tools,
        dependency_inputs=(),
        services=spec.services,
        required_secret_names=spec.required_secret_names,
    )


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
    dependency_hashes = _safe_dependency_hashes(spec, root)

    observed = _inspect_local_environment(
        _probe_view_without_dependency_reads(spec),
        repo_root=root,
        command_runner=command_runner,
        network_mode=network_mode,
        allowed_domains=allowed_domains,
        service_availability=service_availability,
        secret_availability=secret_availability,
        now=now,
    )
    return EnvironmentFingerprint(
        environment_spec_hash=spec.sha256,
        environment_kind=observed.environment_kind,
        runtimes=observed.runtimes,
        tools=observed.tools,
        repo_revision=observed.repo_revision,
        worktree_dirty=observed.worktree_dirty,
        dependency_hashes=dependency_hashes,
        network_mode=observed.network_mode,
        allowed_domains=observed.allowed_domains,
        service_availability=observed.service_availability,
        secret_availability=observed.secret_availability,
        observed_at=observed.observed_at,
    )


# Ensure direct imports from runtime.environment.fingerprint receive the same
# use-time-safe public implementation after package initialization.
_fingerprint_module.inspect_local_environment = inspect_local_environment
