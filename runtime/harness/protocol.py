from __future__ import annotations

from typing import Any, Mapping, Protocol, runtime_checkable

from .types import ExecutionBinding, OperationResult, SessionRef


@runtime_checkable
class HarnessAdapter(Protocol):
    """Provider/runtime adapter contract.

    Implementations translate lifecycle operations for one execution mechanism.
    They do not grant task authority and should return ``UNSUPPORTED`` as a
    structured ``OperationResult`` when an operation is not available.
    """

    adapter_id: str

    def start(
        self,
        binding: ExecutionBinding,
        launch_spec: Mapping[str, Any],
    ) -> OperationResult: ...

    def attach(
        self,
        binding: ExecutionBinding,
        session_ref: SessionRef,
    ) -> OperationResult: ...

    def send(
        self,
        binding: ExecutionBinding,
        payload: Mapping[str, Any],
    ) -> OperationResult: ...

    def inspect(self, session_ref: SessionRef) -> OperationResult: ...

    def heartbeat(self, binding: ExecutionBinding) -> OperationResult: ...

    def resume(self, binding: ExecutionBinding) -> OperationResult: ...

    def stop(self, binding: ExecutionBinding, reason: str) -> OperationResult: ...

    def collect(self, binding: ExecutionBinding) -> OperationResult: ...
