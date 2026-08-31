from __future__ import annotations

from typing import Any, Iterable, Mapping

from .hooks import HookEnforcement, HookEvent, HookRegistry, HookRunResult
from .protocol import HarnessAdapter
from .types import ExecutionBinding, OperationResult, RetryDisposition, SessionRef


class HarnessService:
    """Provider-neutral execution surface over adapters and deterministic Hooks.

    This service does not decide task authority. Consequential start/send/resume/
    stop operations require the corresponding canonical-run enforcement Hook to
    be installed and then pass that Hook. Session/binding identity checks and
    Hooks may only narrow or block an operation; they never grant missing
    authority. Low-level adapters remain capability primitives beneath this
    guarded service boundary.
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

    def _require_canonical_enforcement(
        self,
        event: HookEvent,
        operation: str,
    ) -> OperationResult | None:
        if self.hooks.has_enforcement(event, HookEnforcement.CANONICAL_RUN):
            return None
        return OperationResult.failure(
            "CANONICAL_GUARD_REQUIRED",
            "Consequential harness operation requires canonical run enforcement.",
            data={"operation": operation, "event": event.value},
            retry=RetryDisposition.UNSAFE,
        )

    def _require_destructive_enforcement(
        self,
        event: HookEvent,
        operation: str,
    ) -> OperationResult | None:
        if self.hooks.has_enforcement(
            event, HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION
        ):
            return None
        return OperationResult.failure(
            "DESTRUCTIVE_GUARD_REQUIRED",
            "Destructive harness operation requires destructive/external action enforcement.",
            data={"operation": operation, "event": event.value},
            retry=RetryDisposition.UNSAFE,
        )

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
        destructive: bool | None = None,
        external: bool | None = None,
    ) -> dict[str, Any]:
        context: dict[str, Any] = {
            "operation": operation,
            "adapter_id": adapter_id,
        }
        if destructive is not None:
            context["destructive"] = destructive
        if external is not None:
            context["external"] = external
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
        canonical_adapter_id = str(adapter.adapter_id).strip()

        enforcement_error = self._require_canonical_enforcement(
            HookEvent.RUN_STARTING, "start"
        )
        if enforcement_error is not None:
            return enforcement_error

        before = self.hooks.run(
            HookEvent.RUN_STARTING,
            self._context(
                "start",
                adapter_id=canonical_adapter_id,
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
            self._context("start", adapter_id=canonical_adapter_id, binding=binding),
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

        enforcement_error = self._require_canonical_enforcement(
            HookEvent.BEFORE_SEND, "send"
        )
        if enforcement_error is not None:
            return enforcement_error

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

        enforcement_error = self._require_canonical_enforcement(
            HookEvent.BEFORE_RESUME, "resume"
        )
        if enforcement_error is not None:
            return enforcement_error

        before = self.hooks.run(
            HookEvent.BEFORE_RESUME,
            self._context(
                "resume",
                adapter_id=session_ref.adapter,
                binding=binding,
                session_ref=session_ref,
            ),
        )
        if not before.permitted:
            return self._hook_block("resume", before)
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

        # `stop` is definitionally a destructive operation (irreversible
        # termination of in-flight session state). The two booleans are a fixed
        # literal set by this code path -- declaration-at-the-operation, never
        # inferred (addendum Q2). This gate and firing site run *before* the
        # canonical-run check.
        destructive_enforcement_error = self._require_destructive_enforcement(
            HookEvent.BEFORE_DESTRUCTIVE_ACTION, "stop"
        )
        if destructive_enforcement_error is not None:
            return destructive_enforcement_error

        destructive_before = self.hooks.run(
            HookEvent.BEFORE_DESTRUCTIVE_ACTION,
            self._context(
                "stop",
                adapter_id=session_ref.adapter,
                binding=binding,
                session_ref=session_ref,
                details={"reason": reason},
                destructive=True,
                external=False,
            ),
        )
        if not destructive_before.permitted:
            return self._hook_block("stop", destructive_before)

        enforcement_error = self._require_canonical_enforcement(
            HookEvent.SESSION_STOPPING, "stop"
        )
        if enforcement_error is not None:
            return enforcement_error

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
