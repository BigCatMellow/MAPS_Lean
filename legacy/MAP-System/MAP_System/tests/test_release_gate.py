#!/usr/bin/env python3
"""Regression tests for HPOM-006 release gate enforcement."""

from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
SCHEMA = ROOT / "migration" / "schema.sql"
RELEASE_TASK = ROOT / "scripts" / "release_task.py"
MAP_TASK = ROOT / "scripts" / "map_task.py"
EXPORTER = ROOT / "migration" / "export_to_files.py"

VALID_CHECKLIST = """\
# Release Checklist: TASK-R

## Header

```
task_id:      TASK-R
released_by:  codex-live
release_date: 2026-06-29
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Ready to release.
"""

INCOMPLETE_CHECKLIST = VALID_CHECKLIST.replace(
    "- [x] Follow-up tasks created",
    "- [ ] Follow-up tasks created",
)

MISSING_EMERGENCE_CHECKLIST = VALID_CHECKLIST.replace(
    "- [x] Emergence capture considered\n", ""
)

STRUCTURED_CHECKLIST_TEMPLATE = VALID_CHECKLIST.replace(
    "- [x] Emergence capture considered",
    "- [x] Emergence capture considered — mechanism: {mechanism}; evidence/reason: {evidence}",
)

INCOMPLETE_STRUCTURED_EMERGENCE_CHECKLIST = VALID_CHECKLIST.replace(
    "- [x] Emergence capture considered",
    "- [x] Emergence capture considered — mechanism: neither; evidence/reason: "
    "[why neither was warranted]",
)

# TASK-288/DEC-032: the low-risk release tier only requires the emergence-
# capture line (DEC-026's mechanically-non-optional check), not the other
# four boxes.
LOW_RISK_CHECKLIST = """\
# Release Checklist: TASK-R

## Header

```
task_id:      TASK-R
released_by:  codex-live
release_date: 2026-06-29
```

## Checklist

- [x] Emergence capture considered

## Summary

Low-risk release, no shared/templates/canonical output paths touched.
"""

LOW_RISK_MISSING_EMERGENCE_CHECKLIST = """\
# Release Checklist: TASK-R

## Header

```
task_id:      TASK-R
released_by:  codex-live
release_date: 2026-06-29
```

## Summary

Low-risk release, no shared/templates/canonical output paths touched.
"""


def init_db(
    path: Path,
    *,
    status: str = "APPROVED",
    output_paths: tuple[str, ...] = ("MAP_System/shared/foo.md",),
    risk_class: str | None = None,
    risk_severity: str | None = None,
    task_tier: str | None = None,
) -> None:
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO agents (agent_id, label, agent_type, status) VALUES "
            "('codex-live', 'Codex Live', 'core', 'available')"
        )
        conn.execute(
            """
            INSERT INTO tasks
              (task_id, project_id, title, description, task_type, role,
               status, owner, attempt, max_attempts, risk_class, risk_severity, task_tier)
            VALUES
              ('TASK-R', 'TEST', 'Release task', 'desc', 'implementation',
               'implementer', ?, 'codex-live', 0, 3, ?, ?, ?)
            """,
            (status, risk_class, risk_severity, task_tier),
        )
        for output_path in output_paths:
            conn.execute(
                "INSERT INTO task_output_paths (task_id, path) VALUES ('TASK-R', ?)",
                (output_path,),
            )


def run_release_task(db: Path, out: Path, checklist: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable, str(RELEASE_TASK),
            "TASK-R",
            "--released-by", "codex-live",
            "--checklist", str(checklist),
            "--db", str(db),
            "--output-dir", str(out),
            "--event-log", str(out / "events" / "events.jsonl"),
        ],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_map_task_release(db: Path, out: Path, checklist: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable, str(MAP_TASK),
            "--db", str(db),
            "--output-dir", str(out),
            "--event-log", str(out / "events" / "events.jsonl"),
            "release", "TASK-R",
            "--released-by", "codex-live",
            "--checklist", str(checklist),
        ],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def export_mirrors(db: Path, out: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(EXPORTER), "--db", str(db), "--output-dir", str(out)],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0, result.stderr


def task_state(path: Path) -> tuple[str, int]:
    with sqlite3.connect(path) as conn:
        status = conn.execute("SELECT status FROM tasks WHERE task_id='TASK-R'").fetchone()[0]
        count = conn.execute("SELECT count(*) FROM task_release_records WHERE task_id='TASK-R'").fetchone()[0]
    return status, count


def test_incomplete_checklist_blocks_release() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        db = base / "map.db"
        out = base / "out"
        checklist = base / "release.md"
        init_db(db)
        checklist.write_text(INCOMPLETE_CHECKLIST, encoding="utf-8")

        result = run_release_task(db, out, checklist)

        assert result.returncode != 0, result.stdout
        assert "incomplete" in result.stderr.lower(), result.stderr
        assert task_state(db) == ("APPROVED", 0)


def test_missing_emergence_line_blocks_release() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        db = base / "map.db"
        out = base / "out"
        checklist = base / "release.md"
        init_db(db)
        checklist.write_text(MISSING_EMERGENCE_CHECKLIST, encoding="utf-8")

        result = run_release_task(db, out, checklist)

        assert result.returncode != 0, result.stdout
        assert "emergence capture considered" in result.stderr.lower(), result.stderr
        assert task_state(db) == ("APPROVED", 0)


def test_structured_emergence_evidence_accepts_all_named_mechanisms() -> None:
    cases = (
        ("sentinel scan", "map_emergence.py validate: 124 artifacts checked"),
        ("Discovery Agent pass", "EXP-0003 bounded phase-boundary pass; no candidate"),
        ("neither", "documentation-only correction produced no reusable new lesson"),
    )
    for mechanism, evidence in cases:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            db = base / "map.db"
            out = base / "out"
            checklist = base / "release.md"
            init_db(db)
            checklist.write_text(
                STRUCTURED_CHECKLIST_TEMPLATE.format(
                    mechanism=mechanism,
                    evidence=evidence,
                ),
                encoding="utf-8",
            )
            export_mirrors(db, out)

            result = run_release_task(db, out, checklist)

            assert result.returncode == 0, (mechanism, result.stderr)
            assert task_state(db) == ("RELEASED", 1)


def test_incomplete_structured_emergence_evidence_blocks_release() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        db = base / "map.db"
        out = base / "out"
        checklist = base / "release.md"
        init_db(db)
        checklist.write_text(
            INCOMPLETE_STRUCTURED_EMERGENCE_CHECKLIST,
            encoding="utf-8",
        )

        result = run_release_task(db, out, checklist)

        assert result.returncode != 0, result.stdout
        assert "emergence capture considered" in result.stderr.lower(), result.stderr
        assert task_state(db) == ("APPROVED", 0)


def test_release_task_marks_released_with_record() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        db = base / "map.db"
        out = base / "out"
        checklist = base / "release.md"
        init_db(db)
        checklist.write_text(VALID_CHECKLIST, encoding="utf-8")
        export_mirrors(db, out)

        result = run_release_task(db, out, checklist)

        assert result.returncode == 0, result.stderr
        assert task_state(db) == ("RELEASED", 1)


def test_map_task_release_subcommand() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        db = base / "map.db"
        out = base / "out"
        checklist = base / "release.md"
        init_db(db)
        checklist.write_text(VALID_CHECKLIST, encoding="utf-8")
        export_mirrors(db, out)

        result = run_map_task_release(db, out, checklist)

        assert result.returncode == 0, result.stderr
        assert task_state(db) == ("RELEASED", 1)


def test_low_risk_release_skips_full_checklist() -> None:
    """TASK-288/DEC-032: a task touching no canonical path and carrying no
    high-risk classification releases with only the emergence-capture line,
    not all five REQUIRED_CHECKS_FULL boxes."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        db = base / "map.db"
        out = base / "out"
        checklist = base / "release.md"
        init_db(db, output_paths=("MAP_System/scripts/some_module.py",))
        checklist.write_text(LOW_RISK_CHECKLIST, encoding="utf-8")
        export_mirrors(db, out)

        result = run_release_task(db, out, checklist)

        assert result.returncode == 0, result.stderr
        assert task_state(db) == ("RELEASED", 1)
        with sqlite3.connect(db) as conn:
            tier = conn.execute(
                "SELECT release_tier FROM task_release_records WHERE task_id='TASK-R'"
            ).fetchone()[0]
        assert tier == "low", tier


def test_low_risk_release_still_requires_emergence_line() -> None:
    """The emergence-capture check is DEC-026's floor: no risk tier waives it."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        db = base / "map.db"
        out = base / "out"
        checklist = base / "release.md"
        init_db(db, output_paths=("MAP_System/scripts/some_module.py",))
        checklist.write_text(LOW_RISK_MISSING_EMERGENCE_CHECKLIST, encoding="utf-8")
        export_mirrors(db, out)

        result = run_release_task(db, out, checklist)

        assert result.returncode != 0, result.stdout
        assert "emergence capture considered" in result.stderr.lower(), result.stderr
        assert task_state(db) == ("APPROVED", 0)


def test_canonical_path_forces_full_checklist_even_without_risk_fields() -> None:
    """CHANGE_CONTROL_SYSTEM.md's original rule: touching shared/ requires the
    full checklist even for a task with no risk_class/risk_severity/task_tier
    set at all (true of most of the pre-TASK-277 backlog)."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        db = base / "map.db"
        out = base / "out"
        checklist = base / "release.md"
        init_db(db, output_paths=("MAP_System/shared/current-state.md",))
        checklist.write_text(INCOMPLETE_CHECKLIST, encoding="utf-8")
        export_mirrors(db, out)

        result = run_release_task(db, out, checklist)

        assert result.returncode != 0, result.stdout
        assert "incomplete" in result.stderr.lower(), result.stderr
        assert task_state(db) == ("APPROVED", 0)


def test_non_conforming_canonical_root_doc_forces_full_checklist() -> None:
    """TASK-288 independent review (task288-review-valo, 2026-07-28): the
    AGENTS.md/CLAUDE.md/*_SYSTEM.md naming-convention regex missed real
    MAP_System root-level canonical docs like DESTRUCTIVE_ACTION_POLICY.md.
    CANONICAL_ROOT_DOC_BASENAMES covers these explicitly."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        db = base / "map.db"
        out = base / "out"
        checklist = base / "release.md"
        init_db(db, output_paths=("MAP_System/DESTRUCTIVE_ACTION_POLICY.md",))
        checklist.write_text(INCOMPLETE_CHECKLIST, encoding="utf-8")
        export_mirrors(db, out)

        result = run_release_task(db, out, checklist)

        assert result.returncode != 0, result.stdout
        assert "incomplete" in result.stderr.lower(), result.stderr
        assert task_state(db) == ("APPROVED", 0)


def test_high_risk_severity_forces_full_checklist_without_canonical_path() -> None:
    """notes/review-guide.md's High-risk tier: STRUCTURAL severity keeps the
    full checklist even when no shared/templates/canonical path is touched."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        db = base / "map.db"
        out = base / "out"
        checklist = base / "release.md"
        init_db(
            db,
            output_paths=("MAP_System/scripts/some_module.py",),
            risk_severity="STRUCTURAL",
        )
        checklist.write_text(INCOMPLETE_CHECKLIST, encoding="utf-8")
        export_mirrors(db, out)

        result = run_release_task(db, out, checklist)

        assert result.returncode != 0, result.stdout
        assert "incomplete" in result.stderr.lower(), result.stderr
        assert task_state(db) == ("APPROVED", 0)


def test_security_and_policy_tier_force_full_checklist_without_canonical_path() -> None:
    """Exercise the other two named High-risk signals in classify_release."""
    cases = (
        {"risk_class": "SECURITY"},
        {"task_tier": "policy"},
    )
    for risk_fields in cases:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            db = base / "map.db"
            out = base / "out"
            checklist = base / "release.md"
            init_db(
                db,
                output_paths=("MAP_System/scripts/some_module.py",),
                **risk_fields,
            )
            checklist.write_text(INCOMPLETE_CHECKLIST, encoding="utf-8")
            export_mirrors(db, out)

            result = run_release_task(db, out, checklist)

            assert result.returncode != 0, (risk_fields, result.stdout)
            assert "incomplete" in result.stderr.lower(), (risk_fields, result.stderr)
            assert task_state(db) == ("APPROVED", 0)


def main() -> int:
    tests = [
        test_incomplete_checklist_blocks_release,
        test_missing_emergence_line_blocks_release,
        test_structured_emergence_evidence_accepts_all_named_mechanisms,
        test_incomplete_structured_emergence_evidence_blocks_release,
        test_release_task_marks_released_with_record,
        test_map_task_release_subcommand,
        test_low_risk_release_skips_full_checklist,
        test_low_risk_release_still_requires_emergence_line,
        test_canonical_path_forces_full_checklist_even_without_risk_fields,
        test_non_conforming_canonical_root_doc_forces_full_checklist,
        test_high_risk_severity_forces_full_checklist_without_canonical_path,
        test_security_and_policy_tier_force_full_checklist_without_canonical_path,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
