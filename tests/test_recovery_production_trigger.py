"""Tests for the bounded RnS production trigger call site.

Covers `runtime/recovery/production.py` and the two `runtime/cli.py` call
sites it feeds (the new `recovery-tick` subcommand and the `claim` branch's
piggybacked pass), per
`work/notes/2026-08-24-rns-production-trigger-loop-design.md`.
"""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from dataclasses import asdict
from io import StringIO
import json
import os
from pathlib import Path
import tempfile
import tokenize
import unittest
from unittest import mock

from runtime.cli import main as cli_main
from runtime.communication import HcomError
from runtime.recovery.production import run_recovery_tick, run_recovery_tick_isolated
from runtime.state import TaskStore

VOLATILE_TASK_KEYS = ("task_id", "created_at", "updated_at", "claimed_at", "lease_expires_at")


def ready_contract(output_path: str) -> dict:
    return {
        "title": f"Task for {output_path}",
        "outcome": "Observable result.",
        "task_type": "IMPLEMENTATION",
        "owner": "owner-a",
        "risk": "LOW",
        "decision_authority": "Implementation inside declared scope.",
        "verification": "Run deterministic test.",
        "evidence_expected": "Passing test output.",
        "review_required": "OWNER_CHECK",
        "escalation": "Stop on scope changes.",
        "inputs": ["README.md"],
        "sources": ["AGENTS.md"],
        "dependencies": [],
        "output_paths": [output_path],
        "non_goals": ["Do not widen scope."],
        "acceptance_criteria": ["Result is verified."],
        "stop_conditions": ["Required evidence is unavailable."],
    }


class FakeHcom:
    """Minimal stand-in for HcomAdapter's supervisor-facing surface."""

    def __init__(self, *, sessions=None, error: Exception | None = None, **kwargs):
        self.kwargs = kwargs
        self.sessions = list(sessions or [])
        self.error = error
        self.list_calls: list[bool] = []

    def list_sessions(self, *, include_stopped: bool = False):
        self.list_calls.append(include_stopped)
        if self.error is not None:
            raise self.error
        return list(self.sessions)


class RecordingSupervisor:
    """Records the exact sequence of supervisor calls a single pass makes."""

    calls: list[str] = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        RecordingSupervisor.calls.append("construct")

    def observe_silent_stops(self, bindings, *, now=None):
        RecordingSupervisor.calls.append(f"observe:{sorted(bindings.items())}")
        return ["incident-1"]

    def tick(self, *, now=None):
        RecordingSupervisor.calls.append("tick")
        return [{"action": "noop"}]


def code_text(path: Path) -> str:
    """Source text with comments and string literals stripped.

    Keeps the source-level guard below honest: prose in a docstring that names
    a forbidden mechanism (to say it is deliberately absent) must not read as
    that mechanism being present, and must not mask a real occurrence either.
    """
    pieces: list[str] = []
    with open(path, "rb") as handle:
        for token in tokenize.tokenize(handle.readline):
            if token.type in (tokenize.COMMENT, tokenize.STRING):
                continue
            pieces.append(token.string)
    return " ".join(pieces).lower()


class TriggerHelperTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = TaskStore(self.root / "maps.db")
        self.state_path = self.root / "recovery.json"
        RecordingSupervisor.calls = []

    def tearDown(self):
        self.tmp.cleanup()

    def test_runs_exactly_one_observe_then_one_tick_and_returns(self):
        """One bounded pass: construct once, observe once, tick once, exit."""
        with mock.patch(
            "runtime.recovery.production.RecoverySupervisor", RecordingSupervisor
        ):
            result = run_recovery_tick(
                self.store,
                bindings={"worker-1": "session-1"},
                recovery_state_path=self.state_path,
            )
        self.assertEqual(
            RecordingSupervisor.calls,
            ["construct", "observe:[('worker-1', 'session-1')]", "tick"],
        )
        self.assertEqual(result["ok"], True)
        self.assertEqual(result["opened_incidents"], ["incident-1"])
        self.assertEqual(result["actions"], [{"action": "noop"}])

    def test_harness_service_and_environment_reader_are_not_wired(self):
        """This call site builds no HarnessService/environment reader (out of scope)."""
        captured = {}

        class CapturingSupervisor(RecordingSupervisor):
            def __init__(self, **kwargs):
                captured.update(kwargs)
                super().__init__(**kwargs)

        with mock.patch(
            "runtime.recovery.production.RecoverySupervisor", CapturingSupervisor
        ):
            run_recovery_tick(self.store, recovery_state_path=self.state_path)
        self.assertIsNone(captured.get("harness_service"))
        self.assertIsNone(captured.get("environment_reader"))
        self.assertIs(captured["task_reader"], self.store)

    def test_real_supervisor_pass_completes_against_an_empty_hcom(self):
        """The real RecoverySupervisor is constructible and returns from one pass."""
        fake = FakeHcom()
        with mock.patch(
            "runtime.recovery.production.HcomAdapter", lambda **kw: fake
        ):
            result = run_recovery_tick(self.store, recovery_state_path=self.state_path)
        self.assertEqual(result, {"ok": True, "error": "", "opened_incidents": [], "actions": []})
        # One hcom session listing per pass: observe_silent_stops, then tick.
        self.assertEqual(fake.list_calls, [True, True])

    def test_isolated_variant_contains_failures(self):
        fake = FakeHcom(error=HcomError("hcom executable not found: hcom"))
        with mock.patch(
            "runtime.recovery.production.HcomAdapter", lambda **kw: fake
        ):
            result = run_recovery_tick_isolated(
                self.store, recovery_state_path=self.state_path
            )
        self.assertFalse(result["ok"])
        self.assertIn("hcom executable not found", result["error"])
        self.assertEqual(result["opened_incidents"], [])
        self.assertEqual(result["actions"], [])

    def test_unisolated_variant_still_raises(self):
        fake = FakeHcom(error=HcomError("boom"))
        with mock.patch(
            "runtime.recovery.production.HcomAdapter", lambda **kw: fake
        ):
            with self.assertRaises(HcomError):
                run_recovery_tick(self.store, recovery_state_path=self.state_path)


class CliTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.previous_cwd = Path.cwd()
        os.chdir(self.root)
        self.db = self.root / "maps.db"
        self.store = TaskStore(self.db)
        RecordingSupervisor.calls = []

    def tearDown(self):
        os.chdir(self.previous_cwd)
        self.tmp.cleanup()

    def run_cli(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli_main(argv)
        return code, out.getvalue(), err.getvalue()

    def create_ready(self, task_id: str, store: TaskStore | None = None) -> None:
        store = store or self.store
        self.assertTrue(store.create_task(task_id=task_id).ok)
        self.assertTrue(
            store.update_contract(task_id, ready_contract(f"{task_id}.out")).ok
        )
        self.assertTrue(store.promote_ready(task_id, actor="shaper").ok)


class RecoveryTickCommandTests(CliTestBase):
    def test_subcommand_runs_one_bounded_pass_and_exits(self):
        fake = FakeHcom()
        with mock.patch("runtime.recovery.production.HcomAdapter", lambda **kw: fake):
            code, out, err = self.run_cli(["--db", str(self.db), "recovery-tick"])
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(
            payload, {"ok": True, "error": "", "opened_incidents": [], "actions": []}
        )
        self.assertEqual(err, "")
        self.assertEqual(fake.list_calls, [True, True])

    def test_subcommand_passes_hcom_overrides_and_bindings_through(self):
        captured: dict = {}

        def factory(**kwargs):
            captured.update(kwargs)
            return FakeHcom()

        with mock.patch("runtime.recovery.production.HcomAdapter", factory), mock.patch(
            "runtime.recovery.production.RecoverySupervisor", RecordingSupervisor
        ):
            code, out, _ = self.run_cli([
                "--db", str(self.db),
                "recovery-tick",
                "--hcom-dir", str(self.root / "custom-hcom"),
                "--hcom-executable", "/usr/bin/hcom-alt",
                "--binding", "worker-1=session-1",
                "--binding", "worker-2=session-2",
            ])
        self.assertEqual(code, 0)
        self.assertEqual(captured["hcom_dir"], str(self.root / "custom-hcom"))
        self.assertEqual(captured["executable"], "/usr/bin/hcom-alt")
        self.assertIn(
            "observe:[('worker-1', 'session-1'), ('worker-2', 'session-2')]",
            RecordingSupervisor.calls,
        )
        self.assertEqual(json.loads(out)["ok"], True)

    def test_subcommand_defaults_match_hcom_adapter_defaults(self):
        captured: dict = {}

        def factory(**kwargs):
            captured.update(kwargs)
            return FakeHcom()

        with mock.patch("runtime.recovery.production.HcomAdapter", factory):
            self.run_cli(["--db", str(self.db), "recovery-tick"])
        self.assertEqual(captured, {"hcom_dir": ".hcom", "executable": "hcom"})

    def test_subcommand_rejects_malformed_binding(self):
        code, out, _ = self.run_cli(
            ["--db", str(self.db), "recovery-tick", "--binding", "worker-1"]
        )
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(out)["code"], "INVALID_RECOVERY_BINDING")

    def test_subcommand_reports_failure_without_raising(self):
        fake = FakeHcom(error=HcomError("hcom executable not found: hcom"))
        with mock.patch("runtime.recovery.production.HcomAdapter", lambda **kw: fake):
            code, out, _ = self.run_cli(["--db", str(self.db), "recovery-tick"])
        self.assertEqual(code, 2)
        payload = json.loads(out)
        self.assertFalse(payload["ok"])
        self.assertIn("hcom executable not found", payload["error"])


class ClaimPiggybackTests(CliTestBase):
    def claim_payload(self, task_id: str) -> tuple[int, dict, str]:
        code, out, err = self.run_cli(["--db", str(self.db), "claim", task_id, "worker-a"])
        return code, json.loads(out), err

    @staticmethod
    def normalize(payload: dict) -> dict:
        normalized = json.loads(json.dumps(payload))
        task = normalized.get("task")
        if isinstance(task, dict):
            for key in VOLATILE_TASK_KEYS:
                if key in task:
                    task[key] = "<volatile>"
        return normalized

    def test_claim_triggers_one_recovery_pass_after_success(self):
        self.create_ready("task-a")
        fake = FakeHcom()
        with mock.patch("runtime.recovery.production.HcomAdapter", lambda **kw: fake):
            code, payload, _ = self.claim_payload("task-a")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(fake.list_calls, [True, True])

    def test_claim_does_not_trigger_recovery_when_the_claim_itself_fails(self):
        fake = FakeHcom()
        with mock.patch("runtime.recovery.production.HcomAdapter", lambda **kw: fake):
            code, payload, _ = self.claim_payload("missing-task")
        self.assertEqual(code, 2)
        self.assertFalse(payload["ok"])
        self.assertEqual(fake.list_calls, [])

    def test_claim_still_succeeds_when_recovery_tick_fails(self):
        self.create_ready("task-a")
        fake = FakeHcom(error=HcomError("hcom executable not found: hcom"))
        with mock.patch("runtime.recovery.production.HcomAdapter", lambda **kw: fake):
            code, payload, err = self.claim_payload("task-a")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["code"], "CLAIMED")
        task = self.store.get_task("task-a")
        self.assertEqual(task["status"], "ACTIVE")
        self.assertEqual(task["claimed_by"], "worker-a")
        # The failure is surfaced separately, on stderr only.
        self.assertIn("recovery-tick failed (claim unaffected)", err)
        self.assertIn("hcom executable not found", err)

    def test_claim_still_succeeds_when_recovery_tick_raises_unexpectedly(self):
        self.create_ready("task-a")
        with mock.patch(
            "runtime.recovery.production.HcomAdapter",
            mock.Mock(side_effect=RuntimeError("unexpected recovery explosion")),
        ):
            code, payload, err = self.claim_payload("task-a")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertIn("unexpected recovery explosion", err)

    def test_claim_success_output_unchanged_when_recovery_has_nothing_to_do(self):
        """A no-op recovery pass leaves `claim`'s stdout byte-identical to no pass at all."""
        # Two isolated DBs holding an identical task, so the only difference
        # between the runs is whether the recovery pass actually happened.
        control_db = self.root / "control.db"
        self.create_ready("task-a", TaskStore(control_db))
        self.create_ready("task-a")

        # Control: the pre-change behavior -- claim with no recovery trigger.
        with mock.patch("runtime.cli.run_recovery_tick_isolated") as never:
            control_code, control_out, control_err = self.run_cli(
                ["--db", str(control_db), "claim", "task-a", "worker-a"]
            )
        never.assert_called_once()  # the trigger exists, it just did nothing here

        # Live: the real helper, with an hcom that has nothing to report.
        with mock.patch(
            "runtime.recovery.production.HcomAdapter", lambda **kw: FakeHcom()
        ):
            live_code, live_out, live_err = self.run_cli(
                ["--db", str(self.db), "claim", "task-a", "worker-a"]
            )

        self.assertEqual(live_code, control_code)
        self.assertEqual(live_err, control_err)
        self.assertEqual(live_err, "")
        self.assertEqual(
            self.normalize(json.loads(live_out)),
            self.normalize(json.loads(control_out)),
        )
        # Exactly one JSON document on stdout, nothing appended by recovery.
        self.assertEqual(live_out, json.dumps(json.loads(live_out), indent=2, sort_keys=True) + "\n")

    def test_claim_success_payload_matches_direct_store_call(self):
        """`claim`'s emitted schema still equals asdict(store.claim_task(...))."""
        control_store = TaskStore(self.root / "control.db")
        self.create_ready("task-a", control_store)
        self.create_ready("task-a")
        direct = asdict(control_store.claim_task("task-a", "worker-a"))
        with mock.patch(
            "runtime.recovery.production.HcomAdapter", lambda **kw: FakeHcom()
        ):
            _, payload, _ = self.claim_payload("task-a")
        self.assertEqual(self.normalize(payload), self.normalize(direct))


class TriggerSourceGuardTests(unittest.TestCase):
    """Source-level guard: no daemon/scheduler/Hook machinery was introduced."""

    def test_no_daemon_scheduler_or_hook_machinery_in_trigger_source(self):
        root = Path(__file__).parents[1]
        for relative in ("runtime/recovery/production.py", "runtime/cli.py"):
            text = code_text(root / relative)
            for forbidden in (
                "hookevent",
                "hookregistry",
                "harnessservice",
                "hcomharnessadapter",
                "import threading",
                "import multiprocessing",
                "import asyncio",
                "import sched",
                "import signal",
                "import subprocess",
                "crontab",
                "apscheduler",
                "daemon",
                "time . sleep",
                "while true",
            ):
                self.assertNotIn(forbidden, text, f"{relative} must not contain {forbidden!r}")

    def test_supervisor_public_signatures_untouched(self):
        """This task changed no RecoverySupervisor entrypoint signature."""
        import inspect

        from runtime.recovery.supervisor import RecoverySupervisor

        tick = inspect.signature(RecoverySupervisor.tick).parameters
        self.assertEqual(list(tick), ["self", "now"])
        self.assertEqual(tick["now"].kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertIsNone(tick["now"].default)

        observe = inspect.signature(RecoverySupervisor.observe_silent_stops).parameters
        self.assertEqual(list(observe), ["self", "bindings", "now"])
        self.assertEqual(
            observe["bindings"].kind, inspect.Parameter.POSITIONAL_OR_KEYWORD
        )
        self.assertIs(observe["bindings"].default, inspect.Parameter.empty)
        self.assertEqual(observe["now"].kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertIsNone(observe["now"].default)


if __name__ == "__main__":
    unittest.main()
