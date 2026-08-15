from __future__ import annotations

from typing import Any, Iterable, Mapping

from .hooks import HookEvent, HookRegistry, HookRunResult
from .protocol import HarnessAdapter
from .types import ExecutionBinding, OperationResult, RetryDisposition, SessionRef


class HarnessService:
    """Provider-neutral execution surface over adapters and deterministic Hooks.

    This service does not decide task authority. Callers remain responsible for
    canonical task/policy/ownership checks before invoking consequential
    operations. Session/binding identity checks and Hooks may only narrow or
    block an operation; they never grant missing authority.
    """

    def __init__(
        self,
        adapters: Iterable[HarnessAdapter] = (),
        *,
        hooks: HookRegistry | None = None,
    ) -> None:
        self.hooks = hooks or HookRegistry()
        self._adapters: dict[str, HarnessAdapter] = {}
        for adapter in adapters:
            self.register_adapter(adapter)

    def register_adapter(self, adapter: HarnessAdapter) -> None:
        adapter_id = str(adapter.adapter_id).strip()
        if not adapter_id:
            raise ValueError("adapter_id cannot be empty")
        if adapter_id in self._adapters:
            raise ValueError(f"duplicate adapter_id: {adapter_id}")
        self._adapters[adapter_id] = adapter

    @property
    def adapter_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._adapters))

    def _get_adapter(
        self, adapter_id: str
    ) -> tuple[HarnessAdapter | None, OperationResult | None]:
        normalized = adapter_id.strip()
        if not normalized:
            return None, OperationResult.failure(
                "INVALID_ARGUMENT",
                "adapter_id is required.",
                retry=RetryDisposition.UNSAFE,
            )
        adapter = self._adapters.get(normalized)
        if adapter is None:
            return None, OperationResult.failure(
                "ADAPTER_NOT_FOUND",
                "No harness adapter is registered for the requested adapter_id.",
                data={"adapter_id": normalized},
                retry=RetryDisposition.UNSAFE,
            )
        return adapter, None

    @staticmethod
    def _validate_binding_session(
        binding: ExecutionBinding,
        session_ref: SessionRef,
        *,
        allow_unbound: bool = False,
    ) -> OperationResult | None:
        if binding.project_id != session_ref.project_id:
            return OperationResult.failure(
                "PROJECT_MISMATCH",
                "Execution binding and SessionRef belong to different projects.",
                retry=RetryDisposition.UNSAFE,
            )
        if binding.worker_id != session_ref.worker_id:
            return OperationResult.failure(
                "WORKER_MISMATCH",
                "Execution binding and SessionRef identify different workers.",
                retry=RetryDisposition.UNSAFE,
            )
        if binding.session_id is None:
            if allow_unbound:
                return None
            return OperationResult.failure(
                "SESSION_REQUIRED",
                "Execution binding does not contain an explicit session_id.",
                retry=RetryDisposition.UNSAFE,
            )
        if binding.session_id != session_ref.session_id:
            return OperationResult.failure(
                "SESSION_MISMATCH",
                "Execution binding and SessionRef identify different sessions.",
                retry=RetryDisposition.UNSAFE,
            )
        return None

    @staticmethod
    def _hook_block(
        operation: str,
        result: HookRunResult,
        *,
        mutated: bool = False,
        adapter_result: OperationResult | None = None,
    ) -> OperationResult:
        code = "HOOK_DENIED" if result.denied else "APPROVAL_REQUIRED"
        summary = (
            "Deterministic Hook denied the operation."
            if result.denied
            else "Deterministic Hook requires approval before the operation."
        )
        data: dict[str, Any] = {
            "operation": operation,
            "blocking_reasons": list(result.blocking_reasons),
        }
        if adapter_result is not None:
            data["adapter_result"] = adapter_result.to_dict()
        return OperationResult.failure(
            code,
            summary,
            data=data,
            evidence_refs=result.evidence_refs,
            mutated=mutated,
            retry=RetryDisposition.UNSAFE,
        )

    @staticmethod
    def _context(
        operation: str,
        *,
        adapter_id: str,
        binding: ExecutionBinding | None = None,
        session_ref: SessionRef | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        context: dict[str, Any] = {
            "operation": operation,
            "adapter_id": adapter_id,
        }
        if binding is not None:
            context["binding"] = binding.to_dict()
        if session_ref is not None:
            context["session_ref"] = session_ref.to_dict()
        if details:
            context["details"] = dict(details)
        return context

    def start(
        self,
        adapter_id: str,
        binding: ExecutionBinding,
        launch_spec: Mapping[str, Any],
    ) -> OperationResult:
        adapter, error = self._get_adapter(adapter_id)
        if error is not None:
            return error
        assert adapter is not None

        before = self.hooks.run(
            HookEvent.RUN_STARTING,
            self._context(
                "start",
                adapter_id=adapter_id,
                binding=binding,
                details={"launch_spec": dict(launch_spec)},
            ),
        )
        if not before.permitted:
            return self._hook_block("start", before)

        adapter_result = adapter.start(binding, launch_spec)
        if not adapter_result.ok:
            return adapter_result

        after = self.hooks.run(
            HookEvent.RUN_STARTED,
            self._context("start", adapter_id=adapter_id, binding=binding),
        )
        if not after.permitted:
            return self._hook_block(
                "start",
                after,
                mutated=adapter_result.mutated,
                adapter_result=adapter_result,
            )
        return adapter_result

    def attach(
        self,
        binding: ExecutionBinding,
        session_ref: SessionRef,
    ) -> OperationResult:
        mismatch = self._validate_binding_session(
            binding, session_ref, allow_unbound=True
        )
        if mismatch is not None:
            return mismatch
        adapter, error = self._get_adapter(session_ref.adapter)
        if error is not None:
            return error
        assert adapter is not None
        return adapter.attach(binding, session_ref)

    def inspect(self, session_ref: SessionRef) -> OperationResult:
        adapter, error = self._get_adapter(session_ref.adapter)
        if error is not None:
            return error
        assert adapter is not None
        return adapter.inspect(session_ref)

    def send(
        self,
        binding: ExecutionBinding,
        session_ref: SessionRef,
        payload: Mapping[str, Any],
    ) -> OperationResult:
        mismatch = self._validate_binding_session(binding, session_ref)
        if mismatch is not None:
            return mismatch
        adapter, error = self._get_adapter(session_ref.adapter)
        if error is not None:
            return error
        assert adapter is not None

        before = self.hooks.run(
            HookEvent.BEFORE_SEND,
            self._context(
                "send",
                adapter_id=session_ref.adapter,
                binding=binding,
                session_ref=session_ref,
                details={"payload": dict(payload)},
            ),
        )
        if not before.permitted:
            return self._hook_block("send", before)
        return adapter.send(binding, payload)

    def heartbeat(
        self,
        binding: ExecutionBinding,
        session_ref: SessionRef,
    ) -> OperationResult:
        mismatch = self._validate_binding_session(binding, session_ref)
        if mismatch is not None:
            return mismatch
        adapter, error = self._get_adapter(session_ref.adapter)
        if error is not None:
            return error
        assert adapter is not None
        return adapter.heartbeat(binding)

    def resume(
        self,
        binding: ExecutionBinding,
        session_ref: SessionRef,
    ) -> OperationResult:
        mismatch = self._validate_binding_session(binding, session_ref)
        if mismatch is not None:
            return mismatch
        adapter, error = self._get_adapter(session_ref.adapter)
        if error is not None:
            return error
        assert adapter is not None
        return adapter.resume(binding)

    def stop(
        self,
        binding: ExecutionBinding,
        session_ref: SessionRef,
        reason: str,
    ) -> OperationResult:
        mismatch = self._validate_binding_session(binding, session_ref)
        if mismatch is not None:
            return mismatch
        adapter, error = self._get_adapter(session_ref.adapter)
        if error is not None:
            return error
        assert adapter is not None

        before = self.hooks.run(
            HookEvent.SESSION_STOPPING,
            self._context(
                "stop",
                adapter_id=session_ref.adapter,
                binding=binding,
                session_ref=session_ref,
                details={"reason": reason},
            ),
        )
        if not before.permitted:
            return self._hook_block("stop", before)
        return adapter.stop(binding, reason)

    def collect(
        self,
        binding: ExecutionBinding,
        session_ref: SessionRef,
    ) -> OperationResult:
        mismatch = self._validate_binding_session(binding, session_ref)
        if mismatch is not None:
            return mismatch
        adapter, error = self._get_adapter(session_ref.adapter)
        if error is not None:
            return error
        assert adapter is not None
        return adapter.collect(binding)
