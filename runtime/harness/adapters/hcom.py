from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from runtime.communication import (
    HcomAdapter,
    HcomCommandError,
    HcomError,
    HcomProtocolError,
)

from ..types import (
    ExecutionBinding,
    NormalizedSessionState,
    OperationResult,
    RetryDisposition,
    SessionRef,
    SessionStatus,
)

_STATUS_MAP = {
    "starting": NormalizedSessionState.STARTING,
    "active": NormalizedSessionState.RUNNING,
    "running": NormalizedSessionState.RUNNING,
    "listening": NormalizedSessionState.WAITING,
    "waiting": NormalizedSessionState.WAITING,
    "idle": NormalizedSessionState.IDLE,
    "stopping": NormalizedSessionState.STOPPING,
    "stopped": NormalizedSessionState.STOPPED,
    "exited": NormalizedSessionState.STOPPED,
    "dead": NormalizedSessionState.STOPPED,
    "failed": NormalizedSessionState.FAILED,
    "error": NormalizedSessionState.FAILED,
    "offline": NormalizedSessionState.UNREACHABLE,
    "unreachable": NormalizedSessionState.UNREACHABLE,
}


class HcomHarnessAdapter:
    """Normalize explicit hcom session operations into the harness contract.

    This adapter owns no task authority. Callers must validate task/run/policy
    state before invoking consequential operations such as ``send`` or ``stop``.
    """

    adapter_id = "hcom"

    def __init__(self, backend: HcomAdapter, *, project_id: str):
        project_id = project_id.strip()
        if not project_id:
            raise ValueError("project_id cannot be empty")
        self.backend = backend
        self.project_id = project_id

    @staticmethod
    def _unsupported(summary: str) -> OperationResult:
        return OperationResult.failure(
            "UNSUPPORTED",
            summary,
            retry=RetryDisposition.UNSAFE,
        )

    def _provider_failure(self, exc: Exception) -> OperationResult:
        if isinstance(exc, HcomProtocolError):
            code = "PROTOCOL_ERROR"
        elif isinstance(exc, HcomCommandError):
            code = "COMMAND_FAILED"
        else:
            code = "TRANSPORT_ERROR"
        data: dict[str, Any] = {"error_type": type(exc).__name__}
        if isinstance(exc, HcomCommandError):
            data["returncode"] = exc.result.returncode
        return OperationResult.failure(
            code,
            "hcom operation failed.",
            data=data,
            retry=RetryDisposition.UNKNOWN,
        )

    def _project_error(self, project_id: str) -> OperationResult | None:
        if project_id != self.project_id:
            return OperationResult.failure(
                "PROJECT_MISMATCH",
                "Session/binding belongs to a different hcom project.",
                retry=RetryDisposition.UNSAFE,
            )
        return None

    def _session_records(self) -> list[dict[str, Any]] | OperationResult:
        try:
            return self.backend.list_sessions(include_stopped=True)
        except HcomError as exc:
            return self._provider_failure(exc)

    def _find_by_session_id(
        self, session_id: str
    ) -> tuple[dict[str, Any] | None, OperationResult | None]:
        records = self._session_records()
        if isinstance(records, OperationResult):
            return None, records

        matches = [
            item for item in records if str(item.get("session_id", "")).strip() == session_id
        ]
        if len(matches) > 1:
            return None, OperationResult.failure(
                "AMBIGUOUS_SESSION",
                "More than one hcom session has the requested session_id.",
                retry=RetryDisposition.UNSAFE,
            )
        if not matches:
            return None, None
        return matches[0], None

    @staticmethod
    def _state(raw_state: str | None) -> NormalizedSessionState:
        if raw_state is None:
            return NormalizedSessionState.UNKNOWN
        return _STATUS_MAP.get(raw_state.strip().lower(), NormalizedSessionState.UNKNOWN)

    @staticmethod
    def _now_z() -> str:
        return (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )

    def start(
        self,
        binding: ExecutionBinding,
        launch_spec: Mapping[str, Any],
    ) -> OperationResult:
        project_error = self._project_error(binding.project_id)
        if project_error is not None:
            return project_error
        return self._unsupported(
            "hcom start is not normalized until spawn returns a structured session identity."
        )

    def attach(
        self,
        binding: ExecutionBinding,
        session_ref: SessionRef,
    ) -> OperationResult:
        project_error = self._project_error(binding.project_id)
        if project_error is not None:
            return project_error
        if session_ref.adapter != self.adapter_id:
            return OperationResult.failure(
                "ADAPTER_MISMATCH",
                "SessionRef belongs to a different adapter.",
                retry=RetryDisposition.UNSAFE,
            )
        if session_ref.project_id != binding.project_id:
            return OperationResult.failure(
                "PROJECT_MISMATCH",
                "SessionRef and binding belong to different projects.",
                retry=RetryDisposition.UNSAFE,
            )
        return self._unsupported(
            "hcom attachment requires durable run/session lineage before it can be represented honestly."
        )

    def inspect(self, session_ref: SessionRef) -> OperationResult:
        if session_ref.adapter != self.adapter_id:
            return OperationResult.failure(
                "ADAPTER_MISMATCH",
                "SessionRef belongs to a different adapter.",
                retry=RetryDisposition.UNSAFE,
            )
        project_error = self._project_error(session_ref.project_id)
        if project_error is not None:
            return project_error

        record, error = self._find_by_session_id(session_ref.session_id)
        if error is not None:
            return error
        if record is None:
            return OperationResult.success(
                "SESSION_NOT_FOUND",
                "hcom inspection completed; no matching session was found.",
                data={"session_id": session_ref.session_id},
                retry=RetryDisposition.SAFE,
            )

        raw_state_value = record.get("status")
        raw_state = None if raw_state_value is None else str(raw_state_value)
        remote_name = str(record.get("name", "")).strip() or session_ref.remote_ref
        if session_ref.remote_ref is not None and remote_name != session_ref.remote_ref:
            return OperationResult.failure(
                "SESSION_IDENTITY_MISMATCH",
                "hcom session_id resolved to a different session name.",
                retry=RetryDisposition.UNSAFE,
            )

        ref = SessionRef(
            session_id=session_ref.session_id,
            worker_id=session_ref.worker_id,
            adapter=self.adapter_id,
            project_id=self.project_id,
            remote_ref=remote_name,
        )
        status = SessionStatus(
            ref=ref,
            state=self._state(raw_state),
            observed_at=self._now_z(),
            raw_state=raw_state,
            recoverable=None,
        )
        return OperationResult.success(
            "SESSION_INSPECTED",
            "hcom session inspection completed.",
            data={"status": status.to_dict()},
            retry=RetryDisposition.SAFE,
        )

    def _binding_session(
        self, binding: ExecutionBinding
    ) -> tuple[dict[str, Any] | None, OperationResult | None]:
        project_error = self._project_error(binding.project_id)
        if project_error is not None:
            return None, project_error
        if binding.session_id is None:
            return None, OperationResult.failure(
                "SESSION_REQUIRED",
                "This hcom operation requires an explicit session_id in the execution binding.",
                retry=RetryDisposition.UNSAFE,
            )
        record, error = self._find_by_session_id(binding.session_id)
        if error is not None:
            return None, error
        if record is None:
            return None, OperationResult.failure(
                "SESSION_NOT_FOUND",
                "No matching hcom session exists for the execution binding.",
                retry=RetryDisposition.SAFE,
            )
        name = str(record.get("name", "")).strip()
        if not name:
            return None, OperationResult.failure(
                "SESSION_NAME_MISSING",
                "Matching hcom session has no usable name.",
                retry=RetryDisposition.UNSAFE,
            )
        return record, None

    def send(
        self,
        binding: ExecutionBinding,
        payload: Mapping[str, Any],
    ) -> OperationResult:
        record, error = self._binding_session(binding)
        if error is not None:
            return error
        assert record is not None

        message = str(payload.get("message", ""))
        if not message.strip():
            return OperationResult.failure(
                "INVALID_ARGUMENT",
                "hcom send requires a non-empty message.",
                retry=RetryDisposition.UNSAFE,
            )
        intent = str(payload.get("intent", "inform"))
        thread_value = payload.get("thread")
        from_value = payload.get("from_name")
        thread = None if thread_value is None else str(thread_value)
        from_name = None if from_value is None else str(from_value)

        try:
            self.backend.send(
                str(record["name"]),
                message,
                intent=intent,
                thread=thread,
                from_name=from_name,
            )
        except (HcomError, ValueError) as exc:
            if isinstance(exc, HcomError):
                return self._provider_failure(exc)
            return OperationResult.failure(
                "INVALID_ARGUMENT",
                "hcom send arguments were rejected.",
                data={"error_type": type(exc).__name__},
                retry=RetryDisposition.UNSAFE,
            )

        return OperationResult.success(
            "SENT",
            "Message accepted by hcom.",
            data={
                "session_id": binding.session_id,
                "remote_name": str(record["name"]),
            },
            mutated=True,
            retry=RetryDisposition.UNKNOWN,
        )

    def heartbeat(self, binding: ExecutionBinding) -> OperationResult:
        project_error = self._project_error(binding.project_id)
        if project_error is not None:
            return project_error
        return self._unsupported(
            "hcom session liveness is not a MAPS task-claim heartbeat; use inspect instead."
        )

    def resume(self, binding: ExecutionBinding) -> OperationResult:
        project_error = self._project_error(binding.project_id)
        if project_error is not None:
            return project_error
        return self._unsupported(
            "hcom resume mode is not normalized yet; no headless/terminal behavior is guessed."
        )

    def stop(self, binding: ExecutionBinding, reason: str) -> OperationResult:
        if not reason.strip():
            return OperationResult.failure(
                "INVALID_ARGUMENT",
                "Stopping a session requires an explicit reason.",
                retry=RetryDisposition.UNSAFE,
            )
        record, error = self._binding_session(binding)
        if error is not None:
            return error
        assert record is not None

        try:
            self.backend.stop(str(record["name"]))
        except (HcomError, ValueError) as exc:
            if isinstance(exc, HcomError):
                return self._provider_failure(exc)
            return OperationResult.failure(
                "INVALID_ARGUMENT",
                "hcom stop arguments were rejected.",
                data={"error_type": type(exc).__name__},
                retry=RetryDisposition.UNSAFE,
            )

        return OperationResult.success(
            "STOP_REQUESTED",
            "hcom stop request completed.",
            data={
                "session_id": binding.session_id,
                "remote_name": str(record["name"]),
                "reason": reason.strip(),
            },
            mutated=True,
            retry=RetryDisposition.UNKNOWN,
        )

    def collect(self, binding: ExecutionBinding) -> OperationResult:
        project_error = self._project_error(binding.project_id)
        if project_error is not None:
            return project_error
        return self._unsupported(
            "hcom has no normalized structured result-collection contract yet."
        )
