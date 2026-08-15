from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping
from uuid import uuid4
import re

_CODE = re.compile(r"^[A-Z][A-Z0-9_]*$")


def _require_text(value: str, label: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{label} cannot be empty")
    return normalized


def new_operation_id() -> str:
    """Return an opaque operation correlation identifier."""

    return f"op-{uuid4().hex}"


class RetryDisposition(str, Enum):
    """Whether repeating an operation is known to be safe."""

    SAFE = "SAFE"
    UNSAFE = "UNSAFE"
    UNKNOWN = "UNKNOWN"


class NormalizedSessionState(str, Enum):
    """Provider-neutral session state vocabulary.

    UNKNOWN is intentionally first-class. Provider state must not be coerced
    into a stronger claim when the adapter cannot prove it.
    """

    STARTING = "STARTING"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    IDLE = "IDLE"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    UNREACHABLE = "UNREACHABLE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class OperationResult:
    """Bounded, unambiguous result envelope for harness-facing operations.

    ``ok`` reports whether the requested operation succeeded at its own layer;
    it does not imply task completion. ``mutated`` distinguishes reads from
    side effects, ``complete`` distinguishes final from partial/paginated
    responses, and ``retry`` prevents callers from assuming repeat safety.
    """

    ok: bool
    code: str
    summary: str
    data: Mapping[str, Any] = field(default_factory=dict)
    evidence_refs: tuple[str, ...] = ()
    mutated: bool = False
    complete: bool = True
    next: str | None = None
    operation_id: str = field(default_factory=new_operation_id)
    retry: RetryDisposition = RetryDisposition.UNKNOWN

    def __post_init__(self) -> None:
        code = _require_text(self.code, "code")
        if not _CODE.fullmatch(code):
            raise ValueError("code must be an uppercase machine-readable token")
        summary = _require_text(self.summary, "summary")
        operation_id = _require_text(self.operation_id, "operation_id")

        evidence_refs = tuple(_require_text(ref, "evidence reference") for ref in self.evidence_refs)
        next_token = self.next
        if next_token is not None:
            next_token = _require_text(next_token, "next")

        object.__setattr__(self, "code", code)
        object.__setattr__(self, "summary", summary)
        object.__setattr__(self, "operation_id", operation_id)
        object.__setattr__(self, "evidence_refs", evidence_refs)
        object.__setattr__(self, "next", next_token)
        object.__setattr__(self, "data", MappingProxyType(dict(self.data)))

    @classmethod
    def success(
        cls,
        code: str,
        summary: str,
        *,
        data: Mapping[str, Any] | None = None,
        evidence_refs: tuple[str, ...] = (),
        mutated: bool = False,
        complete: bool = True,
        next: str | None = None,
        operation_id: str | None = None,
        retry: RetryDisposition = RetryDisposition.UNKNOWN,
    ) -> "OperationResult":
        kwargs: dict[str, Any] = {}
        if operation_id is not None:
            kwargs["operation_id"] = operation_id
        return cls(
            ok=True,
            code=code,
            summary=summary,
            data=data or {},
            evidence_refs=evidence_refs,
            mutated=mutated,
            complete=complete,
            next=next,
            retry=retry,
            **kwargs,
        )

    @classmethod
    def failure(
        cls,
        code: str,
        summary: str,
        *,
        data: Mapping[str, Any] | None = None,
        evidence_refs: tuple[str, ...] = (),
        mutated: bool = False,
        complete: bool = True,
        operation_id: str | None = None,
        retry: RetryDisposition = RetryDisposition.UNKNOWN,
    ) -> "OperationResult":
        kwargs: dict[str, Any] = {}
        if operation_id is not None:
            kwargs["operation_id"] = operation_id
        return cls(
            ok=False,
            code=code,
            summary=summary,
            data=data or {},
            evidence_refs=evidence_refs,
            mutated=mutated,
            complete=complete,
            retry=retry,
            **kwargs,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "code": self.code,
            "summary": self.summary,
            "data": dict(self.data),
            "evidence_refs": list(self.evidence_refs),
            "mutated": self.mutated,
            "complete": self.complete,
            "next": self.next,
            "operation_id": self.operation_id,
            "retry": self.retry.value,
        }


@dataclass(frozen=True, slots=True)
class SessionRef:
    """Provider/session identity without any implied task authority."""

    session_id: str
    worker_id: str
    adapter: str
    project_id: str
    remote_ref: str | None = None

    def __post_init__(self) -> None:
        for field_name in ("session_id", "worker_id", "adapter", "project_id"):
            object.__setattr__(self, field_name, _require_text(getattr(self, field_name), field_name))
        if self.remote_ref is not None:
            object.__setattr__(self, "remote_ref", _require_text(self.remote_ref, "remote_ref"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "worker_id": self.worker_id,
            "adapter": self.adapter,
            "project_id": self.project_id,
            "remote_ref": self.remote_ref,
        }


@dataclass(frozen=True, slots=True)
class ExecutionBinding:
    """Explicit references connecting a task revision, run, and worker.

    Scope and policy are intentionally not copied here. Their canonical stores
    remain authoritative and callers must re-check them for consequential work.
    """

    task_id: str
    run_id: str
    worker_id: str
    task_revision: str
    project_id: str
    session_id: str | None = None
    context_hashes: tuple[str, ...] = ()
    environment_spec_hash: str | None = None

    def __post_init__(self) -> None:
        for field_name in ("task_id", "run_id", "worker_id", "task_revision", "project_id"):
            object.__setattr__(self, field_name, _require_text(getattr(self, field_name), field_name))
        if self.session_id is not None:
            object.__setattr__(self, "session_id", _require_text(self.session_id, "session_id"))
        if self.environment_spec_hash is not None:
            object.__setattr__(
                self,
                "environment_spec_hash",
                _require_text(self.environment_spec_hash, "environment_spec_hash"),
            )
        object.__setattr__(
            self,
            "context_hashes",
            tuple(_require_text(value, "context hash") for value in self.context_hashes),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "run_id": self.run_id,
            "worker_id": self.worker_id,
            "task_revision": self.task_revision,
            "project_id": self.project_id,
            "session_id": self.session_id,
            "context_hashes": list(self.context_hashes),
            "environment_spec_hash": self.environment_spec_hash,
        }


@dataclass(frozen=True, slots=True)
class SessionStatus:
    """Observed provider-neutral session status.

    ``recoverable=None`` means UNKNOWN; callers must not convert missing
    evidence into a positive or negative recovery claim.
    """

    ref: SessionRef
    state: NormalizedSessionState
    observed_at: str
    last_activity_at: str | None = None
    raw_state: str | None = None
    recoverable: bool | None = None
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "observed_at", _require_text(self.observed_at, "observed_at"))
        if self.last_activity_at is not None:
            object.__setattr__(
                self,
                "last_activity_at",
                _require_text(self.last_activity_at, "last_activity_at"),
            )
        if self.raw_state is not None:
            object.__setattr__(self, "raw_state", _require_text(self.raw_state, "raw_state"))
        object.__setattr__(
            self,
            "evidence_refs",
            tuple(_require_text(ref, "evidence reference") for ref in self.evidence_refs),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "ref": self.ref.to_dict(),
            "state": self.state.value,
            "observed_at": self.observed_at,
            "last_activity_at": self.last_activity_at,
            "raw_state": self.raw_state,
            "recoverable": self.recoverable,
            "evidence_refs": list(self.evidence_refs),
        }
