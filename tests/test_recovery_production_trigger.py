"""Tests for the bounded RnS production trigger call site.

Covers `runtime/recovery/production.py` and the two `runtime/cli.py` call
sites it feeds (the new `recovery-tick` subcommand and the `claim` branch's
piggybacked pass), per
`work/notes/2026-08-24-rns-production-trigger-loop-design.md`.
"""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from dataclasses import asdict, replace
import io
from io import StringIO
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import tokenize
import unittest
from unittest import mock

from runtime.cli import main as cli_main
from runtime.communication import HcomError
from runtime.state import TaskStore
from runtime.environment import (
    CommandOutcome,
    EnvironmentFingerprint,
    EnvironmentKind,
    NetworkMode,
    ObservationState,
    VersionObservation,
    load_environment_spec,
)
from runtime.recovery.production import (
    CLAIM_PIGGYBACK_HCOM_TIMEOUT_SECONDS,
    DEFAULT_HCOM_TIMEOUT_SECONDS,
    DEFAULT_MAX_VALIDATIONS_PER_TICK,
    DEFAULT_VALIDATION_TICK_BUDGET_SECONDS,
    DEFAULT_VALIDATION_TIER_BUDGET_SECONDS,
    VALIDATION_SKIP_REASONS,
    VALIDATION_TIER,
    RunBoundValidator,
    run_recovery_tick,
    run_recovery_tick_isolated,
)

# Keys whose value legitimately differs between two runs of the same claim.
# Every timestamp column belongs here: `now_z()` truncates to whole seconds, so
# any wall-clock gap between the two comparison arms below can straddle a second
# boundary and red the test intermittently. `normalize()` additionally blanks
# ANY key ending in `_at`, so a timestamp column added later cannot silently
# reintroduce that flake.
VOLATILE_TASK_KEYS = (
    "task_id",
    "created_at",
    "updated_at",
    "claimed_at",
    "heartbeat_at",
    "lease_expires_at",
)


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


# Modules whose mere import would mean a daemon/scheduler/background worker (or
# out-of-scope harness wiring) had been introduced. Matched as import
# *statements*, so `from threading import Thread` is caught as well as
# `import threading`.
FORBIDDEN_MODULES = (
    "threading",
    "multiprocessing",
    "asyncio",
    "concurrent",
    "sched",
    "signal",
    "subprocess",
    "crontab",
    "apscheduler",
    "schedule",
)
FORBIDDEN_SUBSTRINGS = (
    "hookevent",
    "hookregistry",
    "harnessservice",
    "hcomharnessadapter",
    "daemon",
    "time . sleep",
    "while true",
)


def code_text_from_source(source: str) -> str:
    """Source text with comments and string literals stripped.

    Keeps the source-level guard below honest: prose in a docstring that names
    a forbidden mechanism (to say it is deliberately absent) must not read as
    that mechanism being present, and must not mask a real occurrence either.
    """
    pieces: list[str] = []
    readline = io.BytesIO(source.encode("utf-8")).readline
    for token in tokenize.tokenize(readline):
        if token.type in (tokenize.COMMENT, tokenize.STRING):
            continue
        pieces.append(token.string)
    return " ".join(pieces).lower()


def code_text(path: Path) -> str:
    return code_text_from_source(path.read_text(encoding="utf-8"))


def guard_trips(text: str) -> bool:
    """Shared guard predicate, so the tripwire tests exercise the real check."""
    for module in FORBIDDEN_MODULES:
        if re.search(rf"(?:^|\s)(?:import|from)\s+(?:[\w.]+\s*\.\s*)?{module}\b", text):
            return True
    return any(forbidden in text for forbidden in FORBIDDEN_SUBSTRINGS)


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

    def test_subcommand_uses_the_full_default_timeout(self):
        """The standalone pass is deliberate, so it keeps HcomAdapter's default."""
        captured: dict = {}

        def factory(**kwargs):
            captured.update(kwargs)
            return FakeHcom()

        with mock.patch("runtime.recovery.production.HcomAdapter", factory):
            self.run_cli(["--db", str(self.db), "recovery-tick"])
        self.assertEqual(captured["timeout_seconds"], DEFAULT_HCOM_TIMEOUT_SECONDS)

    def test_subcommand_timeout_is_overridable(self):
        captured: dict = {}

        def factory(**kwargs):
            captured.update(kwargs)
            return FakeHcom()

        with mock.patch("runtime.recovery.production.HcomAdapter", factory):
            self.run_cli(
                ["--db", str(self.db), "recovery-tick", "--hcom-timeout-seconds", "1.5"]
            )
        self.assertEqual(captured["timeout_seconds"], 1.5)

    def test_subcommand_defaults_match_hcom_adapter_defaults(self):
        captured: dict = {}

        def factory(**kwargs):
            captured.update(kwargs)
            return FakeHcom()

        with mock.patch("runtime.recovery.production.HcomAdapter", factory):
            self.run_cli(["--db", str(self.db), "recovery-tick"])
        self.assertEqual(
            captured,
            {"hcom_dir": ".hcom", "executable": "hcom", "timeout_seconds": 30.0},
        )
        # ...and those really are HcomAdapter's own defaults, not new values.
        import inspect

        from runtime.communication import HcomAdapter

        adapter_defaults = {
            name: parameter.default
            for name, parameter in inspect.signature(HcomAdapter).parameters.items()
        }
        self.assertEqual(adapter_defaults["hcom_dir"], ".hcom")
        self.assertEqual(adapter_defaults["executable"], "hcom")
        self.assertEqual(adapter_defaults["timeout_seconds"], 30.0)

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
            for key in list(task):
                if key in VOLATILE_TASK_KEYS or key.endswith("_at"):
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

    def test_claim_piggyback_uses_a_short_hcom_timeout(self):
        """A slow/unresponsive hcom must not meaningfully stall `claim`."""
        self.create_ready("task-a")
        captured: dict = {}

        def factory(**kwargs):
            captured.update(kwargs)
            return FakeHcom()

        with mock.patch("runtime.recovery.production.HcomAdapter", factory):
            code, payload, _ = self.claim_payload("task-a")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(
            captured["timeout_seconds"], CLAIM_PIGGYBACK_HCOM_TIMEOUT_SECONDS
        )
        # Materially shorter than the adapter default the standalone pass uses,
        # so the worst case a claim can inherit stays small.
        self.assertLess(CLAIM_PIGGYBACK_HCOM_TIMEOUT_SECONDS, 5.0)
        self.assertLess(
            CLAIM_PIGGYBACK_HCOM_TIMEOUT_SECONDS, DEFAULT_HCOM_TIMEOUT_SECONDS / 4
        )

    def test_claim_survives_an_hcom_timeout(self):
        """A timed-out recovery pass is contained exactly like any other failure."""
        self.create_ready("task-a")
        fake = FakeHcom(error=HcomError("hcom command timed out: hcom list --json"))
        with mock.patch("runtime.recovery.production.HcomAdapter", lambda **kw: fake):
            code, payload, err = self.claim_payload("task-a")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["code"], "CLAIMED")
        self.assertIn("timed out", err)

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
            # Import forms are matched by pattern, not substring: a plain
            # `import threading` check is trivially evaded by
            # `from threading import Thread`, and this test's entire job is to
            # be a tripwire.
            for module in FORBIDDEN_MODULES:
                pattern = rf"(?:^|\s)(?:import|from)\s+(?:[\w.]+\s*\.\s*)?{module}\b"
                match = re.search(pattern, text)
                self.assertIsNone(
                    match,
                    f"{relative} must not import {module!r}"
                    + (f" (matched {match.group(0)!r})" if match else ""),
                )
            for forbidden in FORBIDDEN_SUBSTRINGS:
                self.assertNotIn(forbidden, text, f"{relative} must not contain {forbidden!r}")

    def test_the_guard_actually_trips(self):
        """The guard is a real tripwire, not decoration."""
        for violation in (
            "import threading",
            "from threading import Thread",
            "from concurrent.futures import ThreadPoolExecutor",
            "import multiprocessing.pool",
            "import asyncio",
            "from apscheduler.schedulers.background import BackgroundScheduler",
            "x = HookEvent.BEFORE_RESUME",
            "while True: pass",
            "time.sleep(60)",
        ):
            self.assertTrue(
                guard_trips(code_text_from_source(violation)),
                f"guard failed to trip on {violation!r}",
            )

    def test_the_guard_does_not_trip_on_innocuous_source(self):
        for benign in (
            "import json",
            "from pathlib import Path",
            "from runtime.recovery.store import RecoveryStore",
            "value = 'a daemon is deliberately absent here'",
            "# no scheduler, no cron, no daemon, no threading",
        ):
            self.assertFalse(
                guard_trips(code_text_from_source(benign)),
                f"guard wrongly tripped on {benign!r}",
            )

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


# --------------------------------------------------------------------------
# Advisory resume-path validation tier
# (work/notes/2026-08-25-rns-validation-tier-hookin-design.md)
# --------------------------------------------------------------------------

SPEC_PATH = (
    Path(__file__).resolve().parents[1]
    / "runtime"
    / "environment"
    / "specs"
    / "maps-runtime-ci.json"
)


def env_contract(output_path: str) -> dict:
    return dict(ready_contract(output_path), review_required="INDEPENDENT_REVIEW")


class ValidatorTestBase(unittest.TestCase):
    """Builds a real run with real run-bound environment evidence."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        (self.repo / "runtime").mkdir(parents=True)
        (self.repo / "src").mkdir()
        (self.repo / "runtime" / "requirements.txt").write_text(
            "langgraph\n", encoding="utf-8"
        )
        self.store = TaskStore(self.root / "maps.db")
        self.assertTrue(self.store.create_task(task_id="TASK-V").ok)
        self.assertTrue(
            self.store.update_contract("TASK-V", env_contract("src")).ok
        )
        self.assertTrue(self.store.promote_ready("TASK-V", actor="shaper").ok)
        self.assertTrue(
            self.store.claim_task("TASK-V", "worker-1", lease_seconds=600).ok
        )
        run = self.store.create_run_manifest(
            "TASK-V",
            "worker-1",
            repo_root=self.repo,
            created_by="dispatcher",
            readable_paths=["."],
            writable_paths=["src"],
            base_revision="abc123",
        )
        self.assertTrue(run.ok, run.message)
        self.run_id = run.task["run_id"]
        self.spec = load_environment_spec(SPEC_PATH)

    def fingerprint(self, spec=None):
        selected = spec or self.spec
        observed = VersionObservation(ObservationState.OBSERVED, "3.12.4")
        return EnvironmentFingerprint(
            environment_spec_hash=selected.sha256,
            environment_kind=EnvironmentKind.LOCAL,
            runtimes={"python": observed},
            tools={
                "bash": VersionObservation(ObservationState.OBSERVED, "5.2.26"),
                "git": VersionObservation(ObservationState.OBSERVED, "2.45.1"),
                "python": observed,
            },
            repo_revision="abc123",
            worktree_dirty=False,
            dependency_hashes={"runtime/requirements.txt": "a" * 64},
            network_mode=NetworkMode.REQUIRED_GENERAL,
            allowed_domains=(),
            service_availability={},
            secret_availability={},
            observed_at="2026-08-25T17:00:00Z",
        )

    def record_evidence(self, spec=None, *, spec_ref="specs/maps-runtime-ci.json"):
        selected = spec or self.spec
        result = self.store.record_run_environment_evidence(
            self.run_id,
            spec=selected,
            fingerprint=self.fingerprint(selected),
            spec_ref=spec_ref,
            recorded_by="dispatcher",
        )
        self.assertTrue(result.ok, result.message)
        return result

    def validator(self, **kwargs):
        kwargs.setdefault("environment_reader", self.store)
        kwargs.setdefault("repo_root", self.repo)
        return RunBoundValidator(**kwargs)


def passing_executor(command, repo_root):
    return CommandOutcome(command=command, found=True, returncode=0, output="ok")


class StubReader:
    """Evidence reader stand-in for rows the real, insert-only store cannot produce."""

    def __init__(self, rows):
        self.rows = rows
        self.calls: list = []

    def list_run_environment_evidence(self, run_id):
        self.calls.append(run_id)
        return [dict(row) for row in self.rows]


class FakeClock:
    """Deterministic monotonic stand-in: yields each reading, then holds the last."""

    def __init__(self, readings):
        self.readings = list(readings)
        self.index = 0

    def __call__(self):
        value = self.readings[min(self.index, len(self.readings) - 1)]
        self.index += 1
        return value


class RunBoundValidatorTests(ValidatorTestBase):
    def test_no_run_id_bound_reports_and_runs_nothing(self):
        ran = []
        result = self.validator(executor=lambda c, r: ran.append(c)).validate_for_run(None)
        self.assertEqual(result, {"attempted": False, "reason": "no_run_id_bound"})
        self.assertNotIn("passed", result)
        self.assertEqual(ran, [])

    def test_no_spec_bound_is_the_answer_when_no_evidence_exists(self):
        """The honest default production case: the evidence table has no writers yet."""
        ran = []
        validator = self.validator(executor=lambda c, r: ran.append(c))
        result = validator.validate_for_run(self.run_id)
        self.assertEqual(result, {"attempted": False, "reason": "no_spec_bound"})
        self.assertNotIn("passed", result)
        self.assertEqual(ran, [])
        self.assertEqual(validator.validations_run, 0)

    def test_a_run_bound_spec_runs_the_quick_tier_and_records_a_result(self):
        self.record_evidence()
        ran = []

        def executor(command, repo_root):
            ran.append((command, Path(repo_root)))
            return CommandOutcome(command=command, found=True, returncode=0, output="ok")

        result = self.validator(executor=executor).validate_for_run(self.run_id)
        self.assertTrue(result["attempted"])
        self.assertTrue(result["passed"])
        self.assertEqual(result["tier"], "quick")
        self.assertEqual(result["environment_spec_hash"], self.spec.sha256)
        self.assertEqual(
            [command for command, _ in ran], list(self.spec.validation.quick)
        )
        self.assertTrue(self.spec.validation.quick, "fixture must declare commands")
        # Commands run in the explicitly-named checkout, never an ambient cwd.
        for _command, root in ran:
            self.assertEqual(root, self.repo.resolve())
        self.assertEqual(
            [outcome["command"] for outcome in result["result"]["ran"]],
            list(self.spec.validation.quick),
        )

    def test_command_output_is_secret_redacted_in_the_recorded_result(self):
        self.record_evidence()

        def leaking(command, repo_root):
            return CommandOutcome(
                command=command,
                found=True,
                returncode=1,
                output="token=sk-live-abcdef1234567890",
            )

        result = self.validator(executor=leaking).validate_for_run(self.run_id)
        self.assertTrue(result["attempted"])
        self.assertFalse(result["passed"])
        self.assertNotIn("sk-live-abcdef1234567890", json.dumps(result))

    def test_disagreeing_evidence_rows_report_spec_ambiguous_and_run_nothing(self):
        self.record_evidence()
        other = replace(self.spec, environment_id="other-environment")
        self.assertNotEqual(other.sha256, self.spec.sha256)
        self.record_evidence(other)
        ran = []
        result = self.validator(executor=lambda c, r: ran.append(c)).validate_for_run(
            self.run_id
        )
        self.assertEqual(result["attempted"], False)
        self.assertEqual(result["reason"], "spec_ambiguous")
        self.assertEqual(ran, [])

    def test_agreeing_evidence_rows_use_the_last_one_and_run(self):
        self.record_evidence()
        self.record_evidence()
        result = self.validator(executor=passing_executor).validate_for_run(self.run_id)
        self.assertTrue(result["attempted"])
        self.assertEqual(result["environment_spec_hash"], self.spec.sha256)

    def test_evidence_rows_cannot_be_tampered_with_in_place(self):
        """The stored snapshot is immutable, which is why the hash check is a backstop.

        Rows are insert-only by database trigger, so the `spec_hash_mismatch`
        path below can only be reached through a reader that is not the real
        store -- but the check stays, because the validator is duck-typed and
        must not execute a snapshot it cannot vouch for.
        """
        self.record_evidence()
        with sqlite3.connect(self.root / "maps.db") as conn:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(
                    "UPDATE run_environment_evidence SET spec_snapshot = ?",
                    (json.dumps({"nonsense": True}),),
                )

    def test_a_snapshot_disagreeing_with_its_hash_is_rejected_rather_than_executed(self):
        tampered = json.loads(json.dumps(self.spec.to_dict()))
        tampered["validation"]["quick"] = ["rm -rf /"]
        rows = [
            {
                "environment_spec_hash": self.spec.sha256,
                "spec_snapshot": tampered,
            }
        ]
        ran = []
        result = self.validator(
            environment_reader=StubReader(rows),
            executor=lambda c, r: ran.append(c),
        ).validate_for_run(self.run_id)
        self.assertEqual(result["attempted"], False)
        self.assertEqual(result["reason"], "spec_hash_mismatch")
        self.assertEqual(ran, [])

    def test_an_unparseable_snapshot_reports_and_runs_nothing(self):
        rows = [{"environment_spec_hash": "a" * 64, "spec_snapshot": {"nonsense": True}}]
        ran = []
        result = self.validator(
            environment_reader=StubReader(rows),
            executor=lambda c, r: ran.append(c),
        ).validate_for_run(self.run_id)
        self.assertEqual(result["attempted"], False)
        self.assertEqual(result["reason"], "spec_unparseable")
        self.assertEqual(ran, [])

    def test_a_non_object_snapshot_reports_and_runs_nothing(self):
        rows = [{"environment_spec_hash": "a" * 64, "spec_snapshot": "not-an-object"}]
        ran = []
        result = self.validator(
            environment_reader=StubReader(rows),
            executor=lambda c, r: ran.append(c),
        ).validate_for_run(self.run_id)
        self.assertEqual(result["attempted"], False)
        self.assertEqual(result["reason"], "spec_unparseable")
        self.assertEqual(ran, [])

    def test_a_missing_repo_root_reports_and_runs_nothing(self):
        self.record_evidence()
        ran = []
        result = self.validator(
            repo_root=self.root / "does-not-exist",
            executor=lambda c, r: ran.append(c),
        ).validate_for_run(self.run_id)
        self.assertEqual(result["attempted"], False)
        self.assertEqual(result["reason"], "no_repo_root")
        self.assertEqual(ran, [])

    def test_a_reader_failure_is_contained_and_redacted(self):
        class Exploding:
            def list_run_environment_evidence(self, run_id):
                raise RuntimeError("password=hunter2-hunter2-hunter2")

        result = self.validator(environment_reader=Exploding()).validate_for_run("RUN-X")
        self.assertEqual(result["attempted"], False)
        self.assertEqual(result["reason"], "validation_error")
        self.assertIn("RuntimeError", result["detail"])
        self.assertNotIn("hunter2-hunter2-hunter2", result["detail"])

    def test_an_exploding_executor_is_contained(self):
        self.record_evidence()

        def boom(command, repo_root):
            raise OSError("no such file")

        result = self.validator(executor=boom).validate_for_run(self.run_id)
        self.assertEqual(result["attempted"], False)
        self.assertEqual(result["reason"], "validation_error")

    def test_every_reported_reason_is_in_the_closed_vocabulary(self):
        """Q4: reasons are a closed set, and never coexist with a `passed` key."""
        self.record_evidence()
        seen = set()
        cases = [
            self.validator().validate_for_run(None),
            self.validator(repo_root=self.root / "nope").validate_for_run(self.run_id),
            self.validator(max_validations=0).validate_for_run(self.run_id),
        ]
        for result in cases:
            self.assertFalse(result["attempted"])
            self.assertNotIn("passed", result)
            self.assertIn(result["reason"], VALIDATION_SKIP_REASONS)
            seen.add(result["reason"])
        self.assertEqual(
            seen, {"no_run_id_bound", "no_repo_root", "budget_exceeded"}
        )


class ValidationBudgetTests(ValidatorTestBase):
    """Q2/Q3: bounded work, so a slow tier cannot become an unbounded stall."""

    def test_the_per_tick_count_cap_is_enforced(self):
        self.record_evidence()
        validator = self.validator(executor=passing_executor, max_validations=2)
        first = validator.validate_for_run(self.run_id)
        second = validator.validate_for_run(self.run_id)
        third = validator.validate_for_run(self.run_id)
        self.assertTrue(first["attempted"])
        self.assertTrue(second["attempted"])
        self.assertFalse(third["attempted"])
        self.assertEqual(third["reason"], "budget_exceeded")
        self.assertIn("cap of 2", third["detail"])
        self.assertEqual(validator.validations_run, 2)

    def test_the_tier_wall_clock_budget_stops_the_next_command(self):
        """A slow tier is cut off mid-tier, and reports rather than claiming a pass."""
        self.record_evidence()
        self.assertGreaterEqual(len(self.spec.validation.quick), 2)
        # started=0, first command starts at t=0 (inside the 10s budget), the
        # second would start at t=20 and is refused.
        ran = []

        def slow(command, repo_root):
            ran.append(command)
            return CommandOutcome(command=command, found=True, returncode=0, output="ok")

        validator = self.validator(
            executor=slow,
            tier_budget_seconds=10.0,
            clock=FakeClock([0.0, 0.0, 20.0]),
        )
        result = validator.validate_for_run(self.run_id)
        self.assertEqual(result["attempted"], False)
        self.assertEqual(result["reason"], "budget_exceeded")
        self.assertNotIn("passed", result)
        # It really did stop early rather than running the whole tier.
        self.assertEqual(len(ran), 1)
        self.assertLess(len(ran), len(self.spec.validation.quick))

    def test_the_per_tick_wall_clock_budget_stops_later_incidents(self):
        self.record_evidence()
        # The first tier runs entirely at t=0, then the clock jumps to 500s, so
        # the whole per-tick budget is consumed by that one incident.
        validator = self.validator(
            executor=passing_executor,
            tick_budget_seconds=100.0,
            clock=FakeClock([0.0, 0.0, 0.0, 0.0, 500.0]),
        )
        first = validator.validate_for_run(self.run_id)
        self.assertTrue(first["attempted"])
        self.assertGreaterEqual(validator.seconds_used, 100.0)
        second = validator.validate_for_run(self.run_id)
        self.assertEqual(second["attempted"], False)
        self.assertEqual(second["reason"], "budget_exceeded")
        self.assertIn("wall-clock", second["detail"])

    def test_the_declared_budget_constants_are_actually_bounded(self):
        self.assertLessEqual(DEFAULT_VALIDATION_TIER_BUDGET_SECONDS, 120.0)
        self.assertLessEqual(DEFAULT_VALIDATION_TICK_BUDGET_SECONDS, 300.0)
        self.assertLessEqual(DEFAULT_MAX_VALIDATIONS_PER_TICK, 10)
        self.assertEqual(VALIDATION_TIER, "quick")


class ValidationCompositionTests(ValidatorTestBase):
    def test_no_validator_is_constructed_without_an_explicit_repo_root(self):
        captured: dict = {}

        class Capturing(RecordingSupervisor):
            def __init__(self, **kwargs):
                captured.update(kwargs)
                super().__init__(**kwargs)

        with mock.patch(
            "runtime.recovery.production.RecoverySupervisor", Capturing
        ):
            run_recovery_tick(self.store, recovery_state_path=self.root / "r.json")
        self.assertIsNone(captured["resume_validator"])

    def test_an_explicit_repo_root_constructs_a_run_bound_validator(self):
        captured: dict = {}

        class Capturing(RecordingSupervisor):
            def __init__(self, **kwargs):
                captured.update(kwargs)
                super().__init__(**kwargs)

        with mock.patch(
            "runtime.recovery.production.RecoverySupervisor", Capturing
        ):
            run_recovery_tick(
                self.store,
                recovery_state_path=self.root / "r.json",
                validation_repo_root=self.repo,
            )
        validator = captured["resume_validator"]
        self.assertIsInstance(validator, RunBoundValidator)
        # The spec source is the caller's own store, not an ambient one.
        self.assertIs(validator.environment_reader, self.store)
        self.assertEqual(validator.repo_root, self.repo)
        self.assertEqual(validator.tier, "quick")
        # environment_reader on the supervisor stays unwired (#165) -- it is not
        # even passed -- so the evidence table is read at most once per incident.
        self.assertIsNone(captured.get("environment_reader"))
        self.assertNotIn("environment_reader", captured)

    def test_no_ambient_spec_source_exists_in_the_composition_root(self):
        """Non-goal 2/3: no file-loaded spec, no cwd/git-derived repo root."""
        source = (
            Path(__file__).parents[1] / "runtime" / "recovery" / "production.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "load_environment_spec",
            "rev-parse",
            "Path.cwd",
            "os.getcwd",
        ):
            self.assertNotIn(forbidden, source)


class ValidationCliWiringTests(CliTestBase):
    def test_recovery_tick_repo_root_defaults_to_none_not_cwd(self):
        """N6: deliberately unlike `context`/`flow start`, whose --repo-root default is '.'."""
        captured: dict = {}
        real = run_recovery_tick_isolated

        def spy(*args, **kwargs):
            captured.update(kwargs)
            return real(*args, **kwargs)

        fake = FakeHcom()
        with mock.patch("runtime.recovery.production.HcomAdapter", lambda **kw: fake), \
                mock.patch("runtime.cli.run_recovery_tick_isolated", spy):
            code, _out, _err = self.run_cli(["--db", str(self.db), "recovery-tick"])
        self.assertEqual(code, 0)
        self.assertIsNone(captured["validation_repo_root"])
        self.assertNotEqual(captured["validation_repo_root"], ".")

    def test_recovery_tick_passes_an_explicit_repo_root_through(self):
        captured: dict = {}
        real = run_recovery_tick_isolated

        def spy(*args, **kwargs):
            captured.update(kwargs)
            return real(*args, **kwargs)

        fake = FakeHcom()
        with mock.patch("runtime.recovery.production.HcomAdapter", lambda **kw: fake), \
                mock.patch("runtime.cli.run_recovery_tick_isolated", spy):
            code, _out, _err = self.run_cli(
                ["--db", str(self.db), "recovery-tick", "--repo-root", str(self.root)]
            )
        self.assertEqual(code, 0)
        self.assertEqual(captured["validation_repo_root"], str(self.root))

    def test_claim_piggyback_never_enables_validation(self):
        """Q2: the latency bound #165 established must not be reopened by validation."""
        captured: dict = {}
        real = run_recovery_tick_isolated

        def spy(*args, **kwargs):
            captured.update(kwargs)
            return real(*args, **kwargs)

        self.create_ready("task-a")
        fake = FakeHcom()
        with mock.patch("runtime.recovery.production.HcomAdapter", lambda **kw: fake), \
                mock.patch("runtime.cli.run_recovery_tick_isolated", spy):
            code, out, _err = self.run_cli(
                ["--db", str(self.db), "claim", "task-a", "worker-1"]
            )
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out)["ok"])
        # No repo root is supplied, so no validator is constructed and the
        # claim path executes zero declared commands regardless of what any
        # run's evidence declares.
        self.assertIsNone(captured.get("validation_repo_root"))

    def test_claim_runs_no_declared_command_even_with_run_bound_evidence(self):
        """End-to-end: a claim cannot be stalled by a run's declared validation tier."""
        executed: list = []

        def tripwire(command, repo_root):
            executed.append(command)
            return CommandOutcome(
                command=command, found=True, returncode=0, output="ok"
            )

        self.create_ready("task-a")
        fake = FakeHcom()
        with mock.patch("runtime.recovery.production.HcomAdapter", lambda **kw: fake), \
                mock.patch(
                    "runtime.recovery.production._default_executor", tripwire
                ):
            code, out, _err = self.run_cli(
                ["--db", str(self.db), "claim", "task-a", "worker-1"]
            )
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out)["ok"])
        self.assertEqual(executed, [])


if __name__ == "__main__":
    unittest.main()
