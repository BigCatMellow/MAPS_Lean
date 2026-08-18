from __future__ import annotations

from .protocol import HarnessAdapter
from .types import ExecutionBinding, OperationResult, SessionRef

_OPERATIONS = (
    "start",
    "attach",
    "send",
    "inspect",
    "heartbeat",
    "resume",
    "stop",
    "collect",
)


class AdapterContractMixin:
    """Behavioral contract every `HarnessAdapter` implementation must satisfy.

    Mix this into a concrete `unittest.TestCase` for one adapter, setting
    `self.adapter`, `self.binding`, `self.session_ref`, `self.launch_spec`,
    `self.payload`, and `self.stop_reason` in `setUp`. This mixin is not
    itself a `unittest.TestCase`, so plain test discovery does not collect it
    on its own -- only a concrete subclass that also inherits `TestCase`.

    Deliberately narrow: it only proves the structural/behavioral guarantees
    a caller needs to treat any adapter interchangeably through
    `HarnessService` (H1's normalized-result contract, reachable without
    raising). It does not assert adapter-specific business outcomes (e.g.
    what a particular provider's `send` should return) -- that stays in the
    adapter's own test module. It also does not forbid a failure result from
    carrying `mutated=True`; `HarnessService` relies on exactly that to
    preserve evidence of a partial mutation after a post-start Hook denial,
    so a generic contract must not outlaw it.
    """

    adapter: object
    binding: ExecutionBinding
    session_ref: SessionRef
    launch_spec: dict
    payload: dict
    stop_reason: str

    def _call(self, operation: str):
        if operation == "start":
            return self.adapter.start(self.binding, self.launch_spec)
        if operation == "attach":
            return self.adapter.attach(self.binding, self.session_ref)
        if operation == "send":
            return self.adapter.send(self.binding, self.payload)
        if operation == "inspect":
            return self.adapter.inspect(self.session_ref)
        if operation == "stop":
            return self.adapter.stop(self.binding, self.stop_reason)
        return getattr(self.adapter, operation)(self.binding)

    def test_adapter_satisfies_the_harness_adapter_protocol(self):
        self.assertIsInstance(self.adapter, HarnessAdapter)

    def test_adapter_id_is_a_stable_nonempty_string(self):
        adapter_id = self.adapter.adapter_id
        self.assertIsInstance(adapter_id, str)
        self.assertTrue(adapter_id.strip())
        self.assertEqual(adapter_id, self.adapter.adapter_id)

    def test_every_operation_returns_an_operation_result_without_raising(self):
        for operation in _OPERATIONS:
            with self.subTest(operation=operation):
                try:
                    result = self._call(operation)
                except Exception as exc:  # pragma: no cover - failure path under test
                    self.fail(
                        f"{operation}() raised {exc!r} instead of returning a "
                        "failure OperationResult"
                    )
                self.assertIsInstance(
                    result,
                    OperationResult,
                    f"{operation}() must return an OperationResult, got {type(result)!r}",
                )
