from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from types import MappingProxyType
from typing import Any, Mapping


class EnvironmentSpecError(ValueError):
    pass


class NetworkMode(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    REQUIRED_RESTRICTED = "REQUIRED_RESTRICTED"
    REQUIRED_GENERAL = "REQUIRED_GENERAL"
    UNKNOWN = "UNKNOWN"


_IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.:+-]{0,127}$")
_DOMAIN_RE = re.compile(r"^(?:\*\.)?[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?$")


def _required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EnvironmentSpecError(f"{field_name} must be non-empty text")
    return value.strip()


def _expect_object(value: object, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise EnvironmentSpecError(f"{field_name} must be an object")
    return value


def _reject_unknown(mapping: Mapping[str, Any], allowed: set[str], field_name: str) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise EnvironmentSpecError(
            f"{field_name} contains unknown fields: {', '.join(unknown)}"
        )


def _identifier(value: object, field_name: str) -> str:
    text = _required_text(value, field_name)
    if not _IDENTIFIER_RE.fullmatch(text):
        raise EnvironmentSpecError(
            f"{field_name} must be a capability/tool-style identifier, not a value"
        )
    return text


def _identifiers(value: object, field_name: str, *, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise EnvironmentSpecError(f"{field_name} must be a list")
    items = tuple(_identifier(item, field_name) for item in value)
    if not allow_empty and not items:
        raise EnvironmentSpecError(f"{field_name} cannot be empty")
    if len(set(items)) != len(items):
        raise EnvironmentSpecError(f"{field_name} contains duplicates")
    return tuple(sorted(items))


def _commands(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise EnvironmentSpecError(f"{field_name} must be a list of commands")
    commands = tuple(_required_text(item, field_name) for item in value)
    return commands


def _repo_path(value: object, field_name: str) -> str:
    text = _required_text(value, field_name)
    if "\\" in text:
        raise EnvironmentSpecError(f"{field_name} must use portable '/' separators")
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts or text in {".", "./"}:
        raise EnvironmentSpecError(f"{field_name} must be a safe repo-relative path")
    normalized = path.as_posix()
    if normalized.startswith("../") or normalized.startswith("/"):
        raise EnvironmentSpecError(f"{field_name} must be a safe repo-relative path")
    return normalized


def _repo_paths(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise EnvironmentSpecError(f"{field_name} must be a list")
    paths = tuple(_repo_path(item, field_name) for item in value)
    if len(set(paths)) != len(paths):
        raise EnvironmentSpecError(f"{field_name} contains duplicates")
    return tuple(sorted(paths))


def _domains(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise EnvironmentSpecError(f"{field_name} must be a list")
    domains: list[str] = []
    for item in value:
        domain = _required_text(item, field_name).lower()
        if "://" in domain or "/" in domain or ":" in domain:
            raise EnvironmentSpecError(
                f"{field_name} entries must be domain names, not URLs or endpoints"
            )
        if not _DOMAIN_RE.fullmatch(domain):
            raise EnvironmentSpecError(f"invalid domain in {field_name}: {domain}")
        domains.append(domain)
    if len(set(domains)) != len(domains):
        raise EnvironmentSpecError(f"{field_name} contains duplicates")
    return tuple(sorted(domains))


@dataclass(frozen=True, slots=True)
class RepositoryEnvironment:
    base_revision: str | None
    require_clean_worktree: bool


@dataclass(frozen=True, slots=True)
class ValidationTiers:
    quick: tuple[str, ...]
    normal: tuple[str, ...]
    full: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EnvironmentSpec:
    environment_id: str
    version: int
    repository: RepositoryEnvironment
    runtimes: Mapping[str, str]
    required_tools: tuple[str, ...]
    setup_commands: tuple[str, ...]
    maintenance_commands: tuple[str, ...]
    validation: ValidationTiers
    network_mode: NetworkMode
    allowed_domains: tuple[str, ...]
    services: tuple[str, ...]
    required_secret_names: tuple[str, ...]
    dependency_inputs: tuple[str, ...]
    sha256: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "environment_id", _identifier(self.environment_id, "environment_id"))
        if self.version != 1:
            raise EnvironmentSpecError("EnvironmentSpec v1 requires version == 1")
        object.__setattr__(self, "runtimes", MappingProxyType(dict(sorted(self.runtimes.items()))))
        canonical = json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        object.__setattr__(self, "sha256", hashlib.sha256(canonical).hexdigest())

    def to_dict(self) -> dict[str, object]:
        return {
            "environment_id": self.environment_id,
            "version": self.version,
            "repository": {
                "base_revision": self.repository.base_revision,
                "require_clean_worktree": self.repository.require_clean_worktree,
            },
            "runtimes": dict(self.runtimes),
            "required_tools": list(self.required_tools),
            "setup": {"commands": list(self.setup_commands)},
            "maintenance": {"commands": list(self.maintenance_commands)},
            "validation": {
                "quick": list(self.validation.quick),
                "normal": list(self.validation.normal),
                "full": list(self.validation.full),
            },
            "network": {
                "mode": self.network_mode.value,
                "allowed_domains": list(self.allowed_domains),
            },
            "services": list(self.services),
            "secrets": {"required_names": list(self.required_secret_names)},
            "artifacts": {"dependency_inputs": list(self.dependency_inputs)},
        }


def parse_environment_spec(data: Mapping[str, Any]) -> EnvironmentSpec:
    _reject_unknown(
        data,
        {
            "environment_id",
            "version",
            "repository",
            "runtimes",
            "required_tools",
            "setup",
            "maintenance",
            "validation",
            "network",
            "services",
            "secrets",
            "artifacts",
        },
        "EnvironmentSpec",
    )

    environment_id = _identifier(data.get("environment_id"), "environment_id")
    version = data.get("version")
    if not isinstance(version, int) or isinstance(version, bool):
        raise EnvironmentSpecError("version must be integer 1")
    if version != 1:
        raise EnvironmentSpecError("EnvironmentSpec v1 requires version == 1")

    repository_data = _expect_object(data.get("repository"), "repository")
    _reject_unknown(repository_data, {"base_revision", "require_clean_worktree"}, "repository")
    base_revision_raw = repository_data.get("base_revision")
    if base_revision_raw is None:
        base_revision = None
    else:
        base_revision = _required_text(base_revision_raw, "repository.base_revision")
    clean = repository_data.get("require_clean_worktree")
    if not isinstance(clean, bool):
        raise EnvironmentSpecError("repository.require_clean_worktree must be boolean")
    repository = RepositoryEnvironment(base_revision=base_revision, require_clean_worktree=clean)

    runtimes_data = _expect_object(data.get("runtimes"), "runtimes")
    if not runtimes_data:
        raise EnvironmentSpecError("runtimes cannot be empty")
    runtimes: dict[str, str] = {}
    for raw_name, raw_constraint in runtimes_data.items():
        name = _identifier(raw_name, "runtime name")
        constraint = _required_text(raw_constraint, f"runtimes.{name}")
        runtimes[name] = constraint

    required_tools = _identifiers(
        data.get("required_tools"), "required_tools", allow_empty=False
    )

    setup = _expect_object(data.get("setup"), "setup")
    _reject_unknown(setup, {"commands"}, "setup")
    setup_commands = _commands(setup.get("commands"), "setup.commands")

    maintenance = _expect_object(data.get("maintenance", {"commands": []}), "maintenance")
    _reject_unknown(maintenance, {"commands"}, "maintenance")
    maintenance_commands = _commands(
        maintenance.get("commands"), "maintenance.commands"
    )

    validation_data = _expect_object(data.get("validation"), "validation")
    _reject_unknown(validation_data, {"quick", "normal", "full"}, "validation")
    missing_tiers = [tier for tier in ("quick", "normal", "full") if tier not in validation_data]
    if missing_tiers:
        raise EnvironmentSpecError(
            "validation missing tiers: " + ", ".join(missing_tiers)
        )
    validation = ValidationTiers(
        quick=_commands(validation_data["quick"], "validation.quick"),
        normal=_commands(validation_data["normal"], "validation.normal"),
        full=_commands(validation_data["full"], "validation.full"),
    )

    network_data = _expect_object(data.get("network"), "network")
    _reject_unknown(network_data, {"mode", "allowed_domains"}, "network")
    try:
        network_mode = NetworkMode(_required_text(network_data.get("mode"), "network.mode"))
    except ValueError as exc:
        raise EnvironmentSpecError(str(exc)) from exc
    allowed_domains = _domains(
        network_data.get("allowed_domains", []), "network.allowed_domains"
    )
    if network_mode == NetworkMode.NOT_REQUIRED and allowed_domains:
        raise EnvironmentSpecError("NOT_REQUIRED network cannot declare allowed_domains")
    if network_mode == NetworkMode.REQUIRED_RESTRICTED and not allowed_domains:
        raise EnvironmentSpecError(
            "REQUIRED_RESTRICTED network requires at least one allowed domain"
        )

    services = _identifiers(data.get("services", []), "services")

    secrets = _expect_object(data.get("secrets"), "secrets")
    _reject_unknown(secrets, {"required_names"}, "secrets")
    required_secret_names = _identifiers(
        secrets.get("required_names"), "secrets.required_names"
    )

    artifacts = _expect_object(data.get("artifacts"), "artifacts")
    _reject_unknown(artifacts, {"dependency_inputs"}, "artifacts")
    dependency_inputs = _repo_paths(
        artifacts.get("dependency_inputs"), "artifacts.dependency_inputs"
    )

    return EnvironmentSpec(
        environment_id=environment_id,
        version=version,
        repository=repository,
        runtimes=runtimes,
        required_tools=required_tools,
        setup_commands=setup_commands,
        maintenance_commands=maintenance_commands,
        validation=validation,
        network_mode=network_mode,
        allowed_domains=allowed_domains,
        services=services,
        required_secret_names=required_secret_names,
        dependency_inputs=dependency_inputs,
    )


def load_environment_spec(path: str | Path) -> EnvironmentSpec:
    spec_path = Path(path)
    try:
        raw = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EnvironmentSpecError(f"cannot load EnvironmentSpec: {exc}") from exc
    if not isinstance(raw, Mapping):
        raise EnvironmentSpecError("EnvironmentSpec root must be an object")
    return parse_environment_spec(raw)
