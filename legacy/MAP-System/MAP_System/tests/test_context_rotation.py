#!/usr/bin/env python3
"""End-to-end safety tests for TASK-271 context rotation."""

from __future__ import annotations

from datetime import datetime, timezone
import multiprocessing
from pathlib import Path
import sqlite3
import sys
import tempfile
import time
from unittest import mock

import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

import MAP_System.scripts.context_rotation as context_rotation  # noqa: E402
from MAP_System.db import claims as claims_module  # noqa: E402
from MAP_System.scripts.context_rotation import (  # noqa: E402
    RotationError,
    _atomic_write,
    _empty_master,
    abandon_rotation,
    acknowledge_rotation,
    finalize_rotation,
    parse_master,
    prepare_rotation,
    render_master,
    rotation_advice,
    rotation_lock,
    validate_continuity,
)


FIXED = datetime(2026, 7, 22, 10, 0, tzinfo=timezone.utc)
LIVE_REPLACEMENT = {"new-agent": "new-session"}


def make_root(base: Path) -> Path:
    root = base / "MAP_System"
    for part in ("shared", "handoffs", ".locks", "migration", "tasks", "workflow"):
        (root / part).mkdir(parents=True, exist_ok=True)
    db = root / "map.db"
    with sqlite3.connect(db) as conn:
        conn.executescript(
            """
            CREATE TABLE agents (
                agent_id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                agent_type TEXT NOT NULL DEFAULT 'core',
                status TEXT NOT NULL DEFAULT 'available',
                reason TEXT,
                resume_after TEXT,
                updated_at TEXT
            );
            CREATE TABLE tasks (
                task_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                owner TEXT,
                claimed_by TEXT,
                lease_expires_at TEXT,
                heartbeat_at TEXT,
                updated_at TEXT
            );
            """
        )
        conn.execute(
            "INSERT INTO agents(agent_id,label,status,updated_at) VALUES ('old-agent','Old Agent','available','old')"
        )
        conn.execute(
            "INSERT INTO tasks VALUES ('TASK-X','IN_PROGRESS','old-agent','old-agent',NULL,NULL,'old')"
        )
    state = _empty_master()
    state["updated_at"] = "2026-07-22T00:00:00Z"
    _atomic_write(root / "shared" / "context-continuity.md", render_master(state).encode())
    return root


def make_draft(root: Path, *, touched: list[str] | None = None) -> Path:
    touched_path = root.parent / "work.txt"
    touched_path.write_text("original\n", encoding="utf-8")
    draft = {
        "kind": "STATE_SNAPSHOT",
        "snapshot_version": 2,
        "created_at": "replaced-by-prepare",
        "project_id": "TEST",
        "agent_id": "old-agent",
        "session_id": "old-session",
        "status": "handing_off",
        "task_context": {
            "current_task": "TASK-X",
            "owned_tasks": ["TASK-X"],
            "pending_reviews": [],
            "recent_events": [],
            "touched_paths": touched if touched is not None else ["work.txt"],
        },
        "active_constraints": [{"scope": "task", "rule": "preserve claim", "source": "test"}],
        "forward_tasks": [{"task_id": "TASK-X", "next_action": "continue", "owner": "old-agent", "reason": "rotate", "paths": []}],
        "blockers": [],
        "lexicon": {"rotation": "verified context reset"},
        "resume_commands": ["echo resume"],
        "validation": ["focused tests pass"],
        "rotation": {
            "reason": "threshold",
            "summary": "Implementation is in progress and the claim must move safely.",
            "next_action": "Continue TASK-X from the touched file.",
            "used_tokens": 150000,
            "threshold_tokens": 150000,
            "metric_source": "manual_test",
        },
    }
    path = root.parent / "draft.yaml"
    path.write_text(yaml.safe_dump(draft, sort_keys=False), encoding="utf-8")
    return path


def prepared(base: Path):
    root = make_root(base)
    entry = prepare_rotation(make_draft(root), agent="old-agent", root=root, now=FIXED)
    return root, entry


def expect_rotation_error(callable_) -> str:
    try:
        callable_()
    except RotationError as exc:
        return str(exc)
    raise AssertionError("expected RotationError")


def test_threshold_boundaries_and_proportional_guard() -> None:
    assert rotation_advice(119999)["state"] == "below_threshold"
    assert rotation_advice(120000)["state"] == "checkpoint_due"
    assert rotation_advice(150000)["state"] == "rotation_due"
    small = rotation_advice(75000, context_window=100000)
    assert small["state"] == "rotation_due"
    assert small["soft_at"] == 60000 and small["rotate_at"] == 75000
    assert rotation_advice(None)["state"] == "unknown"


def test_prepare_writes_snapshot_and_master_in_lockstep() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root, entry = prepared(Path(tmp))
        assert entry["phase"] == "prepared"
        assert (root.parent / entry["snapshot_path"]).is_file()
        state = parse_master(root / "shared" / "context-continuity.md")
        assert state["revision"] == 1
        assert state["rotations"]["old-agent"]["snapshot_sha256"] == entry["snapshot_sha256"]
        assert validate_continuity(root=root)["ok"] is True


def test_generated_master_path_does_not_self_trigger_drift() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = make_root(Path(tmp))
        draft = make_draft(root, touched=["MAP_System/shared/context-continuity.md"])
        entry = prepare_rotation(draft, agent="old-agent", root=root, now=FIXED)
        snapshot = yaml.safe_load((root.parent / entry["snapshot_path"]).read_text())
        evidence = snapshot["integrity"]["touched_paths"][0]
        assert evidence["state"] == "tracked_by_ledger_revision"
        assert validate_continuity(root=root)["ok"] is True


def test_abandon_preserves_failed_attempt_then_allows_reprepare() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root, first = prepared(Path(tmp))
        abandoned = abandon_rotation(
            old_agent="old-agent", reason="draft became stale", root=root, now=FIXED,
        )
        assert abandoned["phase"] == "abandoned"
        second = prepare_rotation(
            make_draft(root), agent="old-agent", root=root,
            now=datetime(2026, 7, 22, 10, 1, tzinfo=timezone.utc),
        )
        state = parse_master(root / "shared" / "context-continuity.md")
        assert second["phase"] == "prepared"
        assert state["history"][0]["snapshot_sha256"] == first["snapshot_sha256"]
        assert state["history"][0]["phase"] == "abandoned"
        assert validate_continuity(root=root)["ok"] is True


def test_prepare_refuses_incomplete_claim_inventory() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = make_root(Path(tmp))
        draft = yaml.safe_load(make_draft(root).read_text())
        draft["task_context"]["owned_tasks"] = []
        path = root.parent / "bad.yaml"
        path.write_text(yaml.safe_dump(draft), encoding="utf-8")
        message = expect_rotation_error(lambda: prepare_rotation(path, agent="old-agent", root=root))
        assert "exactly match live" in message
        assert parse_master(root / "shared" / "context-continuity.md")["revision"] == 0


def test_prepare_redacts_secrets_before_durable_snapshot() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = make_root(Path(tmp))
        draft_path = make_draft(root)
        draft = yaml.safe_load(draft_path.read_text())
        fake_key = "sk-" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4"
        draft["rotation"]["summary"] = f"Do not persist {fake_key}"
        draft_path.write_text(yaml.safe_dump(draft), encoding="utf-8")
        entry = prepare_rotation(draft_path, agent="old-agent", root=root, now=FIXED)
        text = (root.parent / entry["snapshot_path"]).read_text()
        assert fake_key not in text
        assert "[REDACTED:openai_key]" in text


def test_snapshot_tamper_and_pre_ack_canonical_drift_are_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root, entry = prepared(Path(tmp))
        snapshot_path = root.parent / entry["snapshot_path"]
        snapshot_path.write_text(snapshot_path.read_text() + "# tamper\n", encoding="utf-8")
        result = validate_continuity(root=root)
        assert result["ok"] is False
        assert any("snapshot hash drift" in issue for issue in result["issues"])

    with tempfile.TemporaryDirectory() as tmp:
        root, _ = prepared(Path(tmp))
        with sqlite3.connect(root / "map.db") as conn:
            conn.execute("UPDATE tasks SET updated_at='drift' WHERE task_id='TASK-X'")
        result = validate_continuity(root=root)
        assert "old-agent:canonical_task_drift" in result["issues"]


def test_ack_requires_live_fresh_identity_exact_hash_and_no_drift() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root, entry = prepared(Path(tmp))
        base = dict(
            old_agent="old-agent",
            replacement_agent="new-agent",
            replacement_session="new-session",
            root=root,
            now=FIXED,
        )
        assert "not live" in expect_rotation_error(
            lambda: acknowledge_rotation(**base, snapshot_sha256=entry["snapshot_sha256"], live_agents={})
        )
        assert "does not match" in expect_rotation_error(
            lambda: acknowledge_rotation(
                **base, snapshot_sha256=entry["snapshot_sha256"],
                live_agents={"new-agent": "wrong-session"},
            )
        )
        assert "wrong snapshot" in expect_rotation_error(
            lambda: acknowledge_rotation(
                **base, snapshot_sha256="0" * 64, live_agents=LIVE_REPLACEMENT,
            )
        )
        acked = acknowledge_rotation(
            **base, snapshot_sha256=entry["snapshot_sha256"], live_agents=LIVE_REPLACEMENT
        )
        assert acked["phase"] == "acknowledged"
        assert acked["ack"]["replacement_session"] == "new-session"


def test_volatile_shared_path_append_does_not_block_ack_but_shrink_does() -> None:
    # Reproduces the 2026-07-27 REPAIR-0009-adjacent finding: events.jsonl
    # (a VOLATILE_SHARED_PATHS append-only log) legitimately gains lines
    # between prepare and ack from unrelated concurrent agent/background
    # activity. That must not force an abandon+reprepare cycle. A shrink
    # on the same path (truncation/corruption) must still block.
    with tempfile.TemporaryDirectory() as tmp:
        root = make_root(Path(tmp))
        events_path = root / "events" / "events.jsonl"
        events_path.parent.mkdir(parents=True, exist_ok=True)
        events_path.write_text('{"created_at":"t1","type":"PROGRESS"}\n', encoding="utf-8")
        entry = prepare_rotation(
            make_draft(root, touched=["MAP_System/events/events.jsonl"]),
            agent="old-agent", root=root, now=FIXED,
        )
        # Unrelated concurrent activity appends a line before ack runs.
        with events_path.open("a", encoding="utf-8") as handle:
            handle.write('{"created_at":"t2","type":"PROGRESS","sender":"limit_watcher"}\n')
        acked = acknowledge_rotation(
            old_agent="old-agent", replacement_agent="new-agent",
            replacement_session="new-session", root=root, now=FIXED,
            snapshot_sha256=entry["snapshot_sha256"], live_agents=LIVE_REPLACEMENT,
        )
        assert acked["phase"] == "acknowledged"

        # A shrink on the same append-only path is a different story.
        root2 = make_root(Path(tmp) / "shrink")
        events_path2 = root2 / "events" / "events.jsonl"
        events_path2.parent.mkdir(parents=True, exist_ok=True)
        events_path2.write_text('{"a":1}\n{"b":2}\n{"c":3}\n', encoding="utf-8")
        entry2 = prepare_rotation(
            make_draft(root2, touched=["MAP_System/events/events.jsonl"]),
            agent="old-agent", root=root2, now=FIXED,
        )
        events_path2.write_text('{"a":1}\n', encoding="utf-8")  # truncated
        message = expect_rotation_error(lambda: acknowledge_rotation(
            old_agent="old-agent", replacement_agent="new-agent",
            replacement_session="new-session", root=root2, now=FIXED,
            snapshot_sha256=entry2["snapshot_sha256"], live_agents=LIVE_REPLACEMENT,
        ))
        assert "append_only_shrunk" in message


def test_finalize_refuses_before_ack_then_transfers_claim_and_supersedes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root, entry = prepared(Path(tmp))
        assert "acknowledgement is missing" in expect_rotation_error(
            lambda: finalize_rotation(old_agent="old-agent", root=root, exporter=lambda: None)
        )
        acknowledge_rotation(
            old_agent="old-agent", replacement_agent="new-agent",
            replacement_session="new-session", snapshot_sha256=entry["snapshot_sha256"],
            root=root, live_agents=LIVE_REPLACEMENT, now=FIXED,
        )
        assert "no longer live" in expect_rotation_error(
            lambda: finalize_rotation(
                old_agent="old-agent", root=root, exporter=lambda: None,
                live_agents={}, now=FIXED,
            )
        )
        final = finalize_rotation(
            old_agent="old-agent", root=root, exporter=lambda: None,
            session_closer=lambda agent: None,
            live_agents=LIVE_REPLACEMENT, now=FIXED,
        )
        assert final["phase"] == "finalized"
        with sqlite3.connect(root / "map.db") as conn:
            task = conn.execute("SELECT owner,claimed_by,status FROM tasks WHERE task_id='TASK-X'").fetchone()
            old = conn.execute("SELECT status,reason FROM agents WHERE agent_id='old-agent'").fetchone()
            new = conn.execute("SELECT status,reason FROM agents WHERE agent_id='new-agent'").fetchone()
        assert task == ("new-agent", "new-agent", "IN_PROGRESS")
        assert old == ("inactive", "session_superseded")
        assert new == ("available", None)


def test_finalize_closes_old_agent_session_only_after_success() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root, entry = prepared(Path(tmp))
        acknowledge_rotation(
            old_agent="old-agent", replacement_agent="new-agent",
            replacement_session="new-session", snapshot_sha256=entry["snapshot_sha256"],
            root=root, live_agents=LIVE_REPLACEMENT, now=FIXED,
        )
        closed: list = []
        expect_rotation_error(lambda: finalize_rotation(
            old_agent="old-agent", root=root,
            exporter=lambda: (_ for _ in ()).throw(RuntimeError("synthetic export failure")),
            session_closer=lambda agent: closed.append(agent),
            live_agents=LIVE_REPLACEMENT, now=FIXED,
        ))
        assert closed == [], "a rolled-back finalize must never close the old session's tab"

        final = finalize_rotation(
            old_agent="old-agent", root=root, exporter=lambda: None,
            session_closer=lambda agent: closed.append(agent),
            live_agents=LIVE_REPLACEMENT, now=FIXED,
        )
        assert final["phase"] == "finalized"
        assert closed == ["old-agent"]


def test_finalize_default_session_closer_is_best_effort_on_missing_hcom() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root, entry = prepared(Path(tmp))
        acknowledge_rotation(
            old_agent="old-agent", replacement_agent="new-agent",
            replacement_session="new-session", snapshot_sha256=entry["snapshot_sha256"],
            root=root, live_agents=LIVE_REPLACEMENT, now=FIXED,
        )
        with mock.patch.object(context_rotation.shutil, "which", return_value=None):
            final = finalize_rotation(
                old_agent="old-agent", root=root, exporter=lambda: None,
                live_agents=LIVE_REPLACEMENT, now=FIXED,
            )
        assert final["phase"] == "finalized"


def test_export_failure_rolls_back_claim_and_agent_lifecycle() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root, entry = prepared(Path(tmp))
        acknowledge_rotation(
            old_agent="old-agent", replacement_agent="new-agent",
            replacement_session="new-session", snapshot_sha256=entry["snapshot_sha256"],
            root=root, live_agents=LIVE_REPLACEMENT, now=FIXED,
        )
        calls = 0

        def fail_export():
            nonlocal calls
            calls += 1
            raise RuntimeError("synthetic export failure")

        message = expect_rotation_error(
            lambda: finalize_rotation(
                old_agent="old-agent", root=root, exporter=fail_export,
                live_agents=LIVE_REPLACEMENT,
            )
        )
        assert "rolled back" in message and calls == 2
        with sqlite3.connect(root / "map.db") as conn:
            task = conn.execute("SELECT owner,claimed_by FROM tasks WHERE task_id='TASK-X'").fetchone()
            old = conn.execute("SELECT status,reason FROM agents WHERE agent_id='old-agent'").fetchone()
        assert task == ("old-agent", "old-agent")
        assert old == ("available", None)
        assert parse_master(root / "shared" / "context-continuity.md")["rotations"]["old-agent"]["phase"] == "acknowledged"


def test_master_commit_failure_rolls_back_claim_and_exported_state() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root, entry = prepared(Path(tmp))
        acknowledge_rotation(
            old_agent="old-agent", replacement_agent="new-agent",
            replacement_session="new-session", snapshot_sha256=entry["snapshot_sha256"],
            root=root, live_agents=LIVE_REPLACEMENT, now=FIXED,
        )
        exports = 0

        def count_export():
            nonlocal exports
            exports += 1

        def fail_master(_path, _data):
            raise OSError("synthetic master failure")

        message = expect_rotation_error(lambda: finalize_rotation(
            old_agent="old-agent", root=root, exporter=count_export,
            master_writer=fail_master, live_agents=LIVE_REPLACEMENT, now=FIXED,
        ))
        assert "master ledger failure" in message and exports == 2
        with sqlite3.connect(root / "map.db") as conn:
            task = conn.execute("SELECT owner,claimed_by FROM tasks WHERE task_id='TASK-X'").fetchone()
            old = conn.execute("SELECT status,reason FROM agents WHERE agent_id='old-agent'").fetchone()
        assert task == ("old-agent", "old-agent")
        assert old == ("available", None)
        assert parse_master(root / "shared" / "context-continuity.md")["rotations"]["old-agent"]["phase"] == "acknowledged"


def _fake_authority_operation(db_path: Path, calls: list) -> "callable":
    """Stand in for the map-authority subprocess call in mirror-mode tests.

    Performs the same write claims.py would perform on the real authority
    host (RUKI), so these tests exercise the actual routing decision in
    context_rotation.py -- not just that a mock got called -- without needing
    a live SSH gateway.
    """

    def run(operation: str, args: list[str], *, root: Path = context_rotation.ROOT) -> dict:
        calls.append((operation, list(args)))
        if operation == "register-agent":
            claims_module.register_agent(args[0], db_path=db_path)
            return {"ok": True}
        if operation == "rotation-transfer":
            old_agent, replacement_agent, *task_ids = args
            try:
                snapshot = claims_module.transfer_rotation_claims(
                    old_agent, replacement_agent, task_ids, db_path=db_path
                )
            except ValueError as exc:
                return {"ok": False, "error": str(exc)}
            return {"ok": True, **snapshot}
        if operation == "rotation-restore":
            (transfer_id,) = args
            try:
                claims_module.restore_rotation_claims(transfer_id, db_path=db_path)
            except ValueError as exc:
                return {"ok": False, "error": str(exc)}
            return {"ok": True}
        raise AssertionError(f"unexpected map-authority operation: {operation}")

    return run


def test_ack_and_finalize_route_writes_through_map_authority_on_mirror_host() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root, entry = prepared(Path(tmp))
        db_path = root / "map.db"
        calls: list = []
        with (
            mock.patch.object(context_rotation, "_is_mirror_write", return_value=True),
            mock.patch.object(
                context_rotation, "_run_authority_operation", _fake_authority_operation(db_path, calls)
            ),
        ):
            acknowledge_rotation(
                old_agent="old-agent", replacement_agent="new-agent",
                replacement_session="new-session", snapshot_sha256=entry["snapshot_sha256"],
                root=root, live_agents=LIVE_REPLACEMENT, now=FIXED,
            )
            final = finalize_rotation(
                old_agent="old-agent", root=root, exporter=lambda: None,
                session_closer=lambda agent: None,
                live_agents=LIVE_REPLACEMENT, now=FIXED,
            )
        assert final["phase"] == "finalized"
        assert ("register-agent", ["new-agent"]) in calls
        assert any(operation == "rotation-transfer" for operation, _ in calls)
        # No operation ever reached a direct sqlite3 write against the "mirror"
        # db_path -- if it had, this call would be indistinguishable from the
        # real bug (sqlite3.OperationalError: attempt to write a readonly
        # database) that motivated routing through the gateway in the first
        # place, since the fake performs writes through the same claims.py
        # functions the real authority host would call.
        with sqlite3.connect(db_path) as conn:
            task = conn.execute("SELECT owner,claimed_by,status FROM tasks WHERE task_id='TASK-X'").fetchone()
            old = conn.execute("SELECT status,reason FROM agents WHERE agent_id='old-agent'").fetchone()
            new = conn.execute("SELECT status,reason FROM agents WHERE agent_id='new-agent'").fetchone()
        assert task == ("new-agent", "new-agent", "IN_PROGRESS")
        assert old == ("inactive", "session_superseded")
        assert new == ("available", None)


def test_finalize_export_failure_rolls_back_through_map_authority_on_mirror_host() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root, entry = prepared(Path(tmp))
        db_path = root / "map.db"
        calls: list = []
        with (
            mock.patch.object(context_rotation, "_is_mirror_write", return_value=True),
            mock.patch.object(
                context_rotation, "_run_authority_operation", _fake_authority_operation(db_path, calls)
            ),
        ):
            acknowledge_rotation(
                old_agent="old-agent", replacement_agent="new-agent",
                replacement_session="new-session", snapshot_sha256=entry["snapshot_sha256"],
                root=root, live_agents=LIVE_REPLACEMENT, now=FIXED,
            )

            def fail_export():
                raise RuntimeError("synthetic export failure")

            message = expect_rotation_error(
                lambda: finalize_rotation(
                    old_agent="old-agent", root=root, exporter=fail_export,
                    live_agents=LIVE_REPLACEMENT,
                )
            )
        assert "rolled back" in message
        assert any(operation == "rotation-restore" for operation, _ in calls)
        with sqlite3.connect(db_path) as conn:
            task = conn.execute("SELECT owner,claimed_by FROM tasks WHERE task_id='TASK-X'").fetchone()
            old = conn.execute("SELECT status,reason FROM agents WHERE agent_id='old-agent'").fetchone()
        assert task == ("old-agent", "old-agent")
        assert old == ("available", None)
        assert parse_master(root / "shared" / "context-continuity.md")["rotations"]["old-agent"]["phase"] == "acknowledged"


def _lock_worker(lock_path: str, marker: str) -> None:
    with rotation_lock(Path(lock_path)):
        Path(marker).write_text("acquired", encoding="utf-8")


def test_file_lock_serializes_master_writers() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        lock = Path(tmp) / "rotation.lock"
        marker = Path(tmp) / "child.txt"
        with rotation_lock(lock):
            process = multiprocessing.Process(target=_lock_worker, args=(str(lock), str(marker)))
            process.start()
            time.sleep(0.15)
            assert not marker.exists(), "child acquired lock before parent released it"
        process.join(timeout=3)
        assert process.exitcode == 0 and marker.read_text() == "acquired"


def test_manual_master_edit_is_render_drift() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root, _ = prepared(Path(tmp))
        master = root / "shared" / "context-continuity.md"
        master.write_text(master.read_text() + "manual drift\n", encoding="utf-8")
        assert "master_render_drift" in validate_continuity(root=root)["issues"]


def test_ack_refuses_master_render_drift_without_overwriting_evidence() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root, entry = prepared(Path(tmp))
        master = root / "shared" / "context-continuity.md"
        master.write_text(master.read_text() + "manual drift\n", encoding="utf-8")
        before = master.read_bytes()
        message = expect_rotation_error(lambda: acknowledge_rotation(
            old_agent="old-agent", replacement_agent="new-agent",
            replacement_session="new-session", snapshot_sha256=entry["snapshot_sha256"],
            root=root, live_agents=LIVE_REPLACEMENT, now=FIXED,
        ))
        assert "master_render_drift" in message
        assert master.read_bytes() == before


def _seed_rotation_transfer_db(db: Path) -> None:
    """Minimal agents/tasks schema plus a genuine old/replacement pair and an
    UNRELATED agent+task that the security tests below prove restore never
    touches."""
    with sqlite3.connect(db) as conn:
        conn.executescript(
            """
            CREATE TABLE agents (
                agent_id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                agent_type TEXT NOT NULL DEFAULT 'core',
                status TEXT NOT NULL DEFAULT 'available',
                reason TEXT,
                resume_after TEXT,
                updated_at TEXT
            );
            CREATE TABLE tasks (
                task_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                owner TEXT,
                claimed_by TEXT,
                lease_expires_at TEXT,
                heartbeat_at TEXT,
                updated_at TEXT
            );
            """
        )
        conn.execute(
            "INSERT INTO agents VALUES ('old-agent','Old Agent','core','available',NULL,NULL,'t0')"
        )
        conn.execute(
            "INSERT INTO agents VALUES ('new-agent','New Agent','core','available',NULL,NULL,'t0')"
        )
        conn.execute(
            "INSERT INTO tasks VALUES ('TASK-X','IN_PROGRESS','old-agent','old-agent',NULL,NULL,'t0')"
        )
        conn.execute(
            "INSERT INTO agents VALUES ('unrelated-agent','Unrelated','core','available',NULL,NULL,'untouched')"
        )
        conn.execute(
            "INSERT INTO tasks VALUES ('TASK-UNRELATED','IN_PROGRESS','unrelated-agent','unrelated-agent',NULL,NULL,'untouched')"
        )


def test_transfer_rotation_claims_locks_before_reading_snapshot_rows() -> None:
    """TASK-307 rework, attempt 3 (Smalls-side rereview, codex-lab-vumo): the
    pre-transfer snapshot must be read under the same write lock as the
    transfer, not before it - otherwise a concurrent writer could change a
    row between the snapshot SELECT and BEGIN IMMEDIATE, and a later restore
    would silently clobber that intervening legitimate write with stale
    pre-lock state. This proves the statement ORDER (BEGIN IMMEDIATE before
    any agents/tasks SELECT) rather than simulating real thread concurrency,
    because that ordering is exactly what makes SQLite's own locking provide
    the atomicity guarantee - a test with the old (buggy) code present would
    fail here, since the SELECTs ran before BEGIN IMMEDIATE."""
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        _seed_rotation_transfer_db(db)
        calls: list[str] = []

        class TracingConnection(sqlite3.Connection):
            def execute(self, sql, *args, **kwargs):
                calls.append(sql)
                return super().execute(sql, *args, **kwargs)

        real_connect = sqlite3.connect

        def connect_with_tracer(*args, **kwargs):
            kwargs.setdefault("factory", TracingConnection)
            return real_connect(*args, **kwargs)

        with mock.patch("sqlite3.connect", side_effect=connect_with_tracer):
            claims_module.transfer_rotation_claims(
                "old-agent", "new-agent", ["TASK-X"], db_path=db
            )

        begin_index = next(
            i for i, sql in enumerate(calls) if sql.strip().upper().startswith("BEGIN IMMEDIATE")
        )
        snapshot_select_indices = [
            i for i, sql in enumerate(calls)
            if sql.strip().upper().startswith("SELECT * FROM AGENTS")
            or sql.strip().upper().startswith("SELECT * FROM TASKS")
        ]
        assert snapshot_select_indices, f"expected agents/tasks snapshot SELECTs, got: {calls}"
        assert all(i > begin_index for i in snapshot_select_indices), (
            "snapshot rows must be read after BEGIN IMMEDIATE (the write lock), not before - "
            f"BEGIN IMMEDIATE at call index {begin_index}, snapshot SELECTs at "
            f"{snapshot_select_indices}, full call order: {calls}"
        )


def test_restore_rotation_claims_undoes_exactly_the_transferred_rows() -> None:
    """Positive case: a real transfer_id restores old-agent/new-agent/TASK-X
    to their pre-transfer values, and leaves the unrelated rows alone."""
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        _seed_rotation_transfer_db(db)
        snapshot = claims_module.transfer_rotation_claims(
            "old-agent", "new-agent", ["TASK-X"], db_path=db
        )
        claims_module.restore_rotation_claims(snapshot["transfer_id"], db_path=db)
        with sqlite3.connect(db) as conn:
            task = conn.execute("SELECT owner,claimed_by FROM tasks WHERE task_id='TASK-X'").fetchone()
            old = conn.execute("SELECT status,reason FROM agents WHERE agent_id='old-agent'").fetchone()
            unrelated_task = conn.execute(
                "SELECT owner,claimed_by,updated_at FROM tasks WHERE task_id='TASK-UNRELATED'"
            ).fetchone()
            unrelated_agent = conn.execute(
                "SELECT status,updated_at FROM agents WHERE agent_id='unrelated-agent'"
            ).fetchone()
        assert task == ("old-agent", "old-agent")
        assert old == ("available", None)
        assert unrelated_task == ("unrelated-agent", "unrelated-agent", "untouched")
        assert unrelated_agent == ("available", "untouched")


def test_restore_rotation_claims_rejects_unknown_transfer_id_and_mutates_nothing() -> None:
    """TASK-307 security fix, the core guarantee: a fabricated/never-issued
    transfer_id is refused rather than silently accepted, and no row -
    related or unrelated - changes."""
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        _seed_rotation_transfer_db(db)
        before = _snapshot_all_rows(db)

        try:
            claims_module.restore_rotation_claims("never-issued-transfer-id", db_path=db)
        except ValueError as exc:
            assert "unknown rotation transfer_id" in str(exc)
        else:
            raise AssertionError("restore_rotation_claims accepted an unknown transfer_id")

        assert _snapshot_all_rows(db) == before


def test_restore_rotation_claims_refuses_replay_after_first_restore() -> None:
    """A transfer_id can only restore once - replaying it (e.g. a caller
    resending the same request, or an attacker capturing and reusing a prior
    legitimate id) must fail closed, not silently re-apply."""
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        _seed_rotation_transfer_db(db)
        snapshot = claims_module.transfer_rotation_claims(
            "old-agent", "new-agent", ["TASK-X"], db_path=db
        )
        claims_module.restore_rotation_claims(snapshot["transfer_id"], db_path=db)
        after_first_restore = _snapshot_all_rows(db)

        try:
            claims_module.restore_rotation_claims(snapshot["transfer_id"], db_path=db)
        except ValueError as exc:
            assert "already restored" in str(exc)
        else:
            raise AssertionError("restore_rotation_claims replayed an already-consumed transfer_id")

        assert _snapshot_all_rows(db) == after_first_restore


def test_rotation_restore_gateway_operation_rejects_the_old_row_json_shape() -> None:
    """Interface-level guarantee: the map-authority gateway operation itself
    no longer accepts old-row/replacement-row/task-rows JSON at all (the
    original vulnerable shape) - only a single opaque transfer_id argument.
    This dispatch_authority() call never reaches restore_rotation_claims (the
    argument-count guard raises first), so it touches no database."""
    import MAP_System.scripts.map_authority as map_authority_module

    with mock.patch.object(
        map_authority_module, "load_authority_config", return_value={"mode": "authority"}
    ):
        try:
            map_authority_module.dispatch_authority(
                "rotation-restore",
                ['{"agent_id":"unrelated-agent","status":"available"}', "{}", "[]"],
            )
        except map_authority_module.AuthorityError as exc:
            assert "requires TRANSFER-ID" in str(exc)
        else:
            raise AssertionError("rotation-restore accepted the old 3-argument row-JSON shape")


def _snapshot_all_rows(db: Path) -> tuple:
    with sqlite3.connect(db) as conn:
        agents = conn.execute("SELECT * FROM agents ORDER BY agent_id").fetchall()
        tasks = conn.execute("SELECT * FROM tasks ORDER BY task_id").fetchall()
    return (agents, tasks)


def test_installed_prompts_name_rotation_policy_and_recovery() -> None:
    for name in ("ai-command-center-lab-claude", "ai-command-center-lab-codex"):
        text = (REPO / "MAP_System" / "templates" / "install" / "bin" / name).read_text()
        for phrase in ("150k", "60%", "75%", "recoverable", "abandon", "never clear"):
            assert phrase in text, f"{name} missing {phrase}"


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)} context-rotation tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
