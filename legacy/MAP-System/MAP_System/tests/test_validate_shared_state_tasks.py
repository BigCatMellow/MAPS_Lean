#!/usr/bin/env python3
"""Tests for the shared-state active-lane table validator (TASK-276)."""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_shared_state_tasks.py"
SCHEMA_SCRIPT = ROOT / "scripts" / "validate_task_schema.py"
SCHEMA = ROOT / "migration" / "schema.sql"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Registered before exec so `from __future__ import annotations` dataclasses
    # in the loaded module can resolve their own module namespace.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validator = load(SCRIPT, "validate_shared_state_tasks")


def init_db(path: Path, tasks: dict[str, str]) -> None:
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO agents (agent_id, label, agent_type, status) VALUES "
            "('command-center', 'Command Center', 'core', 'available')"
        )
        for task_id, status in tasks.items():
            conn.execute(
                """
                INSERT INTO tasks
                  (task_id, project_id, title, description, task_type, role,
                   status, owner, attempt, max_attempts)
                VALUES (?, 'TEST', 'Lane task', 'desc', 'implementation',
                        'worker', ?, 'command-center', 0, 3)
                """,
                (task_id, status),
            )


HEADER = """<!-- hpom: file: shared/current-state.md -->

# Current State

## Active Execution Lanes - 2026-07-23 08:40 EDT

| Order | Task | State | Durable owner | `claimed_by` | Why now / gate |
|---|---|---|---|---|---|
"""

# Lines that mention task ids but must never be matched: the RELEASED-since
# paragraph, a collision narrative, a timestamped snapshot claim, and a second
# table under its own heading. This is criterion 4's fixture.
PROSE_TAIL = """
Released since the previous revision and deliberately absent from the table
above: TASK-300, TASK-301. The runner treats `DONE`, `APPROVED`, and `RELEASED`
dependencies as satisfied.

**Resolved gate (kept as a record).** `validate_task_graph` failed repo-wide with
`Output path collision: db/claims.py owned by TASK-300 and TASK-301`. It cleared
when TASK-300 reached APPROVED.

As of 2026-07-01, TASK-301 was READY and TASK-300 was IN_PROGRESS.

### Worker / Model Fit For The Recovery Queue

| Work | Accountable owner | Support tier |
|---|---|---|
| TASK-300 lifecycle authority seams | Codex core | Sonnet fits the contract check. |
| TASK-301 reconciliation | Core owner after rework | Sonnet review fits the scope. |
"""


def write_state(root: Path, rows: list[str], *, header: str = HEADER,
                tail: str = PROSE_TAIL) -> Path:
    path = root / "current-state.md"
    path.write_text(header + "\n".join(rows) + "\n" + tail, encoding="utf-8")
    return path


def setup(tmp: str, rows: list[str], tasks: dict[str, str], **kwargs):
    base = Path(tmp)
    db = base / "map.db"
    init_db(db, tasks)
    return write_state(base, rows, **kwargs), db


# Criterion 5, case 1: a correct table produces no findings.
def test_correct_table_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        state, db = setup(
            tmp,
            [
                "| 1 | TASK-300 | READY | `command-center` | none | reason |",
                "| 2 | TASK-301 | IN_PROGRESS | `codex-lab-kiri` | recorded | reason |",
            ],
            {"TASK-300": "READY", "TASK-301": "IN_PROGRESS"},
        )
        assert validator.validate(state, db) == []


# Criterion 5, case 2: a drifted row yields one finding with correct fields.
def test_drifted_row_reports_all_fields() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        state, db = setup(
            tmp,
            [
                "| 1 | TASK-300 | READY | `command-center` | none | reason |",
                "| 2 | TASK-301 | READY | `command-center` | none | reason |",
            ],
            {"TASK-300": "READY", "TASK-301": "RELEASED"},
        )
        findings = validator.validate(state, db)

        assert len(findings) == 1, findings
        found = findings[0]
        assert found.kind == "DRIFT"
        assert found.task_id == "TASK-301"
        assert found.claimed == "READY"
        assert found.actual == "RELEASED"
        assert found.file == str(state)
        assert found.line == 10, found.line  # second row; header block is 8 lines
        assert "TASK-301" in found.format()
        assert "RELEASED" in found.format()


# Criterion 5, case 3: a format change that matches nothing is an ERROR.
def test_zero_rows_is_an_error() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        state, db = setup(
            tmp,
            ["- TASK-300 is READY", "- TASK-301 is RELEASED"],
            {"TASK-300": "READY", "TASK-301": "RELEASED"},
        )
        findings = validator.validate(state, db)

        assert len(findings) == 1, findings
        assert findings[0].kind == "ERROR"
        assert "no numbered rows matched" in findings[0].message


def test_missing_heading_is_an_error() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        state, db = setup(
            tmp,
            ["| 1 | TASK-300 | READY | x | none | reason |"],
            {"TASK-300": "READY"},
            header=HEADER.replace("## Active Execution Lanes", "## Lanes"),
        )
        findings = validator.validate(state, db)

        assert len(findings) == 1, findings
        assert findings[0].kind == "ERROR"
        assert "heading not found" in findings[0].message


# Criterion 5, case 4: prose, narrative, snapshots, and the adjacent table must
# not fire. The tail alone contains six task-id mentions with statuses.
def test_prose_and_second_table_do_not_fire() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        state, db = setup(
            tmp,
            ["| 1 | TASK-300 | RELEASED | `command-center` | none | reason |"],
            {"TASK-300": "RELEASED", "TASK-301": "DONE"},
        )
        # TASK-301 is claimed READY and IN_PROGRESS in the prose tail while
        # map.db holds DONE. None of that is in scope.
        assert validator.validate(state, db) == []


# IDEA-0029 P1 rules 1 and 2: compound cells compare on the leading token and
# keep the annotation.
def test_compound_status_compares_on_leading_token() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        state, db = setup(
            tmp,
            ["| 1 | TASK-300 | READY, policy-gated | `command-center` | none | reason |"],
            {"TASK-300": "READY"},
        )
        assert validator.validate(state, db) == []


def test_compound_status_annotation_is_reported_on_drift() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        state, db = setup(
            tmp,
            ["| 1 | TASK-300 | READY, policy-gated | `command-center` | none | reason |"],
            {"TASK-300": "RELEASED"},
        )
        findings = validator.validate(state, db)

        assert len(findings) == 1, findings
        assert findings[0].annotation == "policy-gated"
        assert "policy-gated" in findings[0].format()


# IDEA-0029 P1 rule 3.
def test_unrecognised_status_token_is_an_error() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        state, db = setup(
            tmp,
            ["| 1 | TASK-300 | NEARLY_DONE | `command-center` | none | reason |"],
            {"TASK-300": "READY"},
        )
        findings = validator.validate(state, db)

        assert [f.kind for f in findings] == ["ERROR", "ERROR"], findings
        assert "unrecognised status token" in findings[0].message
        assert "coverage shortfall" in findings[1].message


def test_lowercase_status_is_an_error_not_a_skip() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        state, db = setup(
            tmp,
            ["| 1 | TASK-300 | ready | `command-center` | none | reason |"],
            {"TASK-300": "READY"},
        )
        findings = validator.validate(state, db)

        assert findings[0].kind == "ERROR"
        assert "no leading status token" in findings[0].message


# IDEA-0029 P1 rule 4: the guard deli asked for. Losing one row out of several
# must fail even though the zero-row guard cannot see it.
def test_single_lost_row_is_a_coverage_error() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        state, db = setup(
            tmp,
            [
                "| 1 | TASK-300 | READY | `command-center` | none | reason |",
                "| 2 | | RELEASED | `command-center` | none | task id dropped |",
            ],
            {"TASK-300": "READY", "TASK-301": "RELEASED"},
        )
        findings = validator.validate(state, db)

        kinds = [f.kind for f in findings]
        assert kinds == ["ERROR", "ERROR"], findings
        assert "no TASK-NNN id" in findings[0].message
        assert "2 numbered row(s) in the table, 1 compared" in findings[1].message


def test_row_naming_a_task_absent_from_db_is_an_error() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        state, db = setup(
            tmp,
            ["| 1 | TASK-999 | READY | `command-center` | none | reason |"],
            {"TASK-300": "READY"},
        )
        findings = validator.validate(state, db)

        assert findings[0].kind == "ERROR"
        assert "not in map.db" in findings[0].message


def test_db_is_opened_read_only() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        state, db = setup(
            tmp,
            ["| 1 | TASK-300 | READY | `command-center` | none | reason |"],
            {"TASK-300": "READY"},
        )
        before = db.stat().st_mtime_ns
        validator.validate(state, db)
        assert db.stat().st_mtime_ns == before


# The vocabulary is duplicated so the script stays standalone, per repo
# convention. This is what stops the copy from drifting.
def test_status_vocabulary_matches_validate_task_schema() -> None:
    schema_module = load(SCHEMA_SCRIPT, "validate_task_schema")
    assert validator.CANONICAL_STATUSES == schema_module.CANONICAL_STATUSES


def test_exit_codes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        state, db = setup(
            tmp,
            ["| 1 | TASK-300 | READY | `command-center` | none | reason |"],
            {"TASK-300": "READY"},
        )
        assert validator.main(["--state-file", str(state), "--db", str(db)]) == 0

    with tempfile.TemporaryDirectory() as tmp:
        state, db = setup(
            tmp,
            ["| 1 | TASK-300 | READY | `command-center` | none | reason |"],
            {"TASK-300": "RELEASED"},
        )
        assert validator.main(["--state-file", str(state), "--db", str(db)]) == 1


def main() -> int:
    for test in [
        test_correct_table_passes,
        test_drifted_row_reports_all_fields,
        test_zero_rows_is_an_error,
        test_missing_heading_is_an_error,
        test_prose_and_second_table_do_not_fire,
        test_compound_status_compares_on_leading_token,
        test_compound_status_annotation_is_reported_on_drift,
        test_unrecognised_status_token_is_an_error,
        test_lowercase_status_is_an_error_not_a_skip,
        test_single_lost_row_is_a_coverage_error,
        test_row_naming_a_task_absent_from_db_is_an_error,
        test_db_is_opened_read_only,
        test_status_vocabulary_matches_validate_task_schema,
        test_exit_codes,
    ]:
        test()
        print(f"PASS {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
