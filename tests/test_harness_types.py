from pathlib import Path
import unittest

from runtime.harness import (
    ExecutionBinding,
    HarnessAdapter,
    NormalizedSessionState,
    OperationResult,
    RetryDisposition,
    SessionRef,
    SessionStatus,
)


class DummyAdapter:
    adapter_id = "dummy"

    def start(self, binding, launch_spec):
        return OperationResult.success("STARTED", "Started.", mutated=True)

    def attach(self, binding, session_ref):
        return OperationResult.success("ATTACHED", "Attached.", mutated=True)

    def send(self, binding, payload):
        return OperationResult.success("SENT", "Sent.", mutated=True)

    def inspect(self, session_ref):
        return OperationResult.success("INSPECTED", "Inspected.")

    def heartbeat(self, binding):
        return OperationResult.success("HEARTBEAT", "Heartbeat recorded.", mutated=True)

    def resume(self, binding):
        return OperationResult.success("RESUMED", "Resumed.", mutated=True)

    def stop(self, binding, reason):
        return OperationResult.success("STOPPED", "Stopped.", mutated=True)

    def collect(self, binding):
        return OperationResult.success("COLLECTED", "Collected.")


class HarnessTypeTests(unittest.TestCase):
    def test_operation_result_distinguishes_no_output_from_failure(self):
        no_output = OperationResult.success(
            "SUCCESS_NO_OUTPUT",
            "Command completed successfully and produced no output.",
            retry=RetryDisposition.SAFE,
        )
        failure = OperationResult.failure(
            "TRANSPORT_ERROR",
            "Provider transport failed.",
            retry=RetryDisposition.UNKNOWN,
        )

        self.assertTrue(no_output.ok)
        self.assertFalse(failure.ok)
        self.assertEqual(no_output.code, "SUCCESS_NO_OUTPUT")
        self.assertEqual(failure.code, "TRANSPORT_ERROR")

    def test_operation_result_preserves_partial_mutation_and_retry_semantics(self):
        result = OperationResult.success(
            "PAGE",
            "First page returned.",
            data={"items": [1, 2]},
            evidence_refs=("event:7",),
            mutated=False,
            complete=False,
            next="cursor-2",
            operation_id="op-test",
            retry=RetryDisposition.SAFE,
        )

        payload = result.to_dict()
        self.assertEqual(payload["operation_id"], "op-test")
        self.assertFalse(payload["complete"])
        self.assertEqual(payload["next"], "cursor-2")
        self.assertFalse(payload["mutated"])
        self.assertEqual(payload["retry"], "SAFE")
        self.assertEqual(payload["evidence_refs"], ["event:7"])

    def test_operation_result_copies_and_freezes_top_level_data(self):
        source = {"value": 1}
        result = OperationResult.success("OK", "Done.", data=source)
        source["value"] = 2

        self.assertEqual(result.data["value"], 1)
        with self.assertRaises(TypeError):
            result.data["value"] = 3

    def test_operation_result_recursively_freezes_nested_data(self):
        source = {"items": [{"value": 1}]}
        result = OperationResult.success("OK", "Done.", data=source)

        source["items"][0]["value"] = 2
        source["items"].append({"value": 3})

        self.assertEqual(result.data["items"][0]["value"], 1)
        self.assertEqual(len(result.data["items"]), 1)
        with self.assertRaises(TypeError):
            result.data["items"][0]["value"] = 4
        with self.assertRaises(AttributeError):
            result.data["items"].append({"value": 5})

    def test_operation_result_to_dict_does_not_alias_nested_data(self):
        result = OperationResult.success(
            "OK",
            "Done.",
            data={"items": [{"value": 1}]},
        )

        payload = result.to_dict()
        payload["data"]["items"][0]["value"] = 2
        payload["data"]["items"].append({"value": 3})

        self.assertEqual(result.data["items"][0]["value"], 1)
        self.assertEqual(len(result.data["items"]), 1)

    def test_operation_result_rejects_non_json_like_nested_data(self):
        with self.assertRaises(TypeError):
            OperationResult.success("OK", "Done.", data={"items": {1, 2}})

    def test_operation_result_generates_opaque_operation_id(self):
        first = OperationResult.success("OK", "Done.")
        second = OperationResult.success("OK", "Done.")
        self.assertTrue(first.operation_id.startswith("op-"))
        self.assertNotEqual(first.operation_id, second.operation_id)

    def test_operation_result_rejects_ambiguous_machine_codes(self):
        with self.assertRaises(ValueError):
            OperationResult.success("not ok", "Done.")
        with self.assertRaises(ValueError):
            OperationResult.success("OK", " ")
        with self.assertRaises(ValueError):
            OperationResult.success("OK", "Done.", next=" ")

    def test_execution_binding_references_authority_without_copying_it(self):
        binding = ExecutionBinding(
            task_id="TASK-1",
            run_id="RUN-1",
            worker_id="worker-1",
            task_revision="rev-abc",
            project_id="project-1",
            session_id="session-1",
            context_hashes=("sha256:abc",),
            environment_spec_hash="sha256:def",
            harness_config_hash="sha256:ghi",
        )
        payload = binding.to_dict()

        self.assertEqual(payload["task_id"], "TASK-1")
        self.assertEqual(payload["session_id"], "session-1")
        self.assertEqual(payload["harness_config_hash"], "sha256:ghi")
        self.assertNotIn("writable_scope", payload)
        self.assertNotIn("policy", payload)

    def test_execution_binding_harness_config_hash_accepts_none_and_rejects_empty(self):
        binding = ExecutionBinding(
            task_id="TASK-1",
            run_id="RUN-1",
            worker_id="worker-1",
            task_revision="rev-abc",
            project_id="project-1",
        )
        self.assertIsNone(binding.harness_config_hash)

        with self.assertRaises(ValueError):
            ExecutionBinding(
                task_id="TASK-1",
                run_id="RUN-1",
                worker_id="worker-1",
                task_revision="rev-abc",
                project_id="project-1",
                harness_config_hash="   ",
            )

    def test_session_status_preserves_unknown_recoverability(self):
        ref = SessionRef(
            session_id="session-1",
            worker_id="worker-1",
            adapter="hcom",
            project_id="project-1",
        )
        status = SessionStatus(
            ref=ref,
            state=NormalizedSessionState.UNKNOWN,
            observed_at="2026-08-15T12:00:00-04:00",
            raw_state="provider-maybe",
        )

        payload = status.to_dict()
        self.assertEqual(payload["state"], "UNKNOWN")
        self.assertIsNone(payload["recoverable"])
        self.assertEqual(payload["ref"]["adapter"], "hcom")

    def test_dummy_adapter_satisfies_runtime_protocol(self):
        self.assertIsInstance(DummyAdapter(), HarnessAdapter)

    def test_harness_contract_has_no_task_store_dependency(self):
        root = Path(__file__).parents[1] / "runtime" / "harness"
        text = "\n".join(
            path.read_text(encoding="utf-8") for path in sorted(root.glob("*.py"))
        )
        self.assertNotIn("runtime.state", text)
        self.assertNotIn("TaskStore", text)
        self.assertNotIn("maps.db", text)


if __name__ == "__main__":
    unittest.main()
