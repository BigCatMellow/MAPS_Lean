#!/usr/bin/env python3
"""Regression test for the pre-dispatch gate-input schema migration.

See `MAP_System/artifacts/research/SUMMARY-external-blueprint-gap-review-2026-07-21.md`
(gap 4, "Four of six core-agent approval gates are unreachable") and
`MAP_System/artifacts/planning/pre-dispatch-gate-input-migration.md` for the
fix plan this test pins.

`evaluate_pre_dispatch()` in `pre_dispatch_policy.py` correctly honours
`decision_class`, `risk_class`, `risk_severity`, `task_tier`, and
`requires_operator_approval` *when they are present on the task dict* --
`test_pre_dispatch_policy.py` already proves this at the function level for
three of the five. Before the Phase 1 migration (`pre-dispatch-gate-input-migration.md`),
the gap was one layer up: the `tasks` table had no columns for any of these
five fields, `load_task_from_db()`'s SELECT did not name them, and
`map_task.py create` never set them. Unlike the eight predicate-backed fields
(`destructive_action`, `final_review`, ...), these five have *no
text-heuristic fallback at all* -- if the column doesn't carry the value, the
gate cannot fire, no matter how the task is worded.

Phase 1 landed 2026-07-21: `tasks` now carries all five columns
(`decision_class`, `risk_class`, `risk_severity`, `task_tier` as nullable
TEXT; `requires_operator_approval` as `INTEGER NOT NULL DEFAULT 0`),
`load_task_from_db()` selects them, `map_task.py create` accepts them as
optional flags, and the runner's own loader (`graph/runner.py`
`load_tasks_from_sqlite`) selects them too. The existing 253 tasks were
deliberately NOT backfilled (see the migration plan's "Backfilling existing
253 tasks" section) -- classification is a human/agent judgment call at
creation time, not something derivable from title/description text, and a
wrong auto-classification recorded as if deliberate would be worse than
staying unclassified.

Phase 2 landed 2026-07-21 (same day): the eight predicate-backed fields
(`destructive_action`, `final_review`, `final_decision`, `broad_architecture`,
`broad_rewrite`, `canonical_map_mutation`, `shell_required`,
`trust_boundary_crossing`) got the same schema/loader/create-flag/mirror
treatment. Unlike the Phase 1 five, each of these already had a working text
heuristic (`is_destructive()`, `is_final_review()`, etc.) that ran when the
field was absent -- the migration does not add a first fallback where none
existed, it makes the *explicit* field reachable and checked first, so a
neutrally-worded task no longer depends on phrasing alone (see niko's
"clean up the deployment mirror" vs "git reset --hard" demonstration in
`pre-dispatch-gate-input-migration.md`'s originating discussion). Also
nullable, also not backfilled, same reasoning.

This file is wired into `run_tests.sh`. All tests below assert the now-fixed
state; a failure here is a real regression, not an expected gap -- do not
"fix" a failure by loosening an assertion back toward the pre-migration
behavior.

Run directly: `MAP_System/.venv/bin/python MAP_System/tests/test_pre_dispatch_gate_inputs.py`
"""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(REPO))

from MAP_System.scripts.pre_dispatch_policy import evaluate_pre_dispatch, load_task_from_db  # noqa: E402

GATE_INPUT_FIELDS = (
    "decision_class",
    "risk_class",
    "risk_severity",
    "task_tier",
    "requires_operator_approval",
)

# Phase 2 (pre-dispatch-gate-input-migration.md): the eight predicate-backed
# fields. Unlike GATE_INPUT_FIELDS, each of these already degrades to a
# working text heuristic when unset (is_destructive(), is_final_review(),
# etc.) -- the migration makes explicit declaration reachable and authoritative
# (checked first, before any heuristic), it does not add a first fallback
# where none existed.
GATE_PREDICATE_FIELDS = (
    "destructive_action",
    "final_review",
    "final_decision",
    "broad_architecture",
    "broad_rewrite",
    "canonical_map_mutation",
    "shell_required",
    "trust_boundary_crossing",
)


def init_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.executescript((ROOT / "migration" / "schema.sql").read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO agents (agent_id, label, agent_type, status) "
            "VALUES ('codex-lab-test', 'Codex Test', 'core', 'available')"
        )


def insert_task(
    path: Path,
    task_id: str,
    *,
    title: str,
    description: str,
    decision_class: str | None = None,
    risk_class: str | None = None,
    risk_severity: str | None = None,
    task_tier: str | None = None,
    requires_operator_approval: bool = False,
    destructive_action: bool | None = None,
    final_review: bool | None = None,
    final_decision: bool | None = None,
    broad_architecture: bool | None = None,
    broad_rewrite: bool | None = None,
    canonical_map_mutation: bool | None = None,
    shell_required: bool | None = None,
    trust_boundary_crossing: bool | None = None,
) -> None:
    def as_col(value: bool | None) -> int | None:
        return None if value is None else int(value)

    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            INSERT INTO tasks
              (task_id, project_id, title, description, task_type, role, status, owner, attempt, max_attempts,
               decision_class, risk_class, risk_severity, task_tier, requires_operator_approval,
               destructive_action, final_review, final_decision, broad_architecture, broad_rewrite,
               canonical_map_mutation, shell_required, trust_boundary_crossing)
            VALUES (?, 'TEST', ?, ?, 'implementation', 'engineer', 'READY', 'command-center', 0, 3,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                title,
                description,
                decision_class,
                risk_class,
                risk_severity,
                task_tier,
                int(requires_operator_approval),
                as_col(destructive_action),
                as_col(final_review),
                as_col(final_decision),
                as_col(broad_architecture),
                as_col(broad_rewrite),
                as_col(canonical_map_mutation),
                as_col(shell_required),
                as_col(trust_boundary_crossing),
            ),
        )


def load_from_fresh_db(
    task_id: str,
    *,
    title: str,
    description: str,
    decision_class: str | None = None,
    risk_class: str | None = None,
    risk_severity: str | None = None,
    task_tier: str | None = None,
    requires_operator_approval: bool = False,
    destructive_action: bool | None = None,
    final_review: bool | None = None,
    final_decision: bool | None = None,
    broad_architecture: bool | None = None,
    broad_rewrite: bool | None = None,
    canonical_map_mutation: bool | None = None,
    shell_required: bool | None = None,
    trust_boundary_crossing: bool | None = None,
) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        init_db(db)
        insert_task(
            db,
            task_id,
            title=title,
            description=description,
            decision_class=decision_class,
            risk_class=risk_class,
            risk_severity=risk_severity,
            destructive_action=destructive_action,
            final_review=final_review,
            final_decision=final_decision,
            broad_architecture=broad_architecture,
            broad_rewrite=broad_rewrite,
            canonical_map_mutation=canonical_map_mutation,
            shell_required=shell_required,
            trust_boundary_crossing=trust_boundary_crossing,
            task_tier=task_tier,
            requires_operator_approval=requires_operator_approval,
        )
        return load_task_from_db(task_id, db)


def test_tasks_table_has_gate_input_columns() -> None:
    """Schema-level reality post-migration: all five fields are real columns.

    Formerly `test_tasks_table_has_no_gate_input_columns`, asserting the
    opposite -- pre-migration, this was "cannot be populated", proven by the
    column set itself. The Phase 1 migration (`pre-dispatch-gate-input-migration.md`)
    added all five as additive/nullable columns (see `migration/schema.sql`).
    """
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        init_db(db)
        with sqlite3.connect(db) as conn:
            columns = {row[1] for row in conn.execute("PRAGMA table_info(tasks)")}
    missing = [field for field in GATE_INPUT_FIELDS if field not in columns]
    assert missing == [], (
        f"expected all of {GATE_INPUT_FIELDS} to be `tasks` columns; missing {missing} -- "
        "the Phase 1 schema migration (pre-dispatch-gate-input-migration.md) "
        "should have added them to migration/schema.sql"
    )


def test_loaded_task_carries_gate_input_keys() -> None:
    """A task loaded through the real production path (`load_task_from_db`)
    now carries all five keys -- `None`/`False` for an unclassified task
    (the common case; the existing 253 tasks were deliberately not
    backfilled), populated when set at creation time via `map_task.py
    create`'s new flags."""
    unclassified = load_from_fresh_db(
        "TASK-P",
        title="Ratify the write-path centralization decision",
        description="Record a binding MAP-wide policy on single-writer map.db access.",
    )
    missing = [field for field in GATE_INPUT_FIELDS if field not in unclassified]
    assert missing == [], f"expected all gate-input keys on a DB-loaded task, missing: {missing}"
    assert unclassified["decision_class"] is None
    assert unclassified["risk_class"] is None
    assert unclassified["risk_severity"] is None
    assert unclassified["task_tier"] is None
    assert unclassified["requires_operator_approval"] in (0, False)

    classified = load_from_fresh_db(
        "TASK-Q",
        title="Rotate the production database credential",
        description="Rotate the shared production DB credential and update the secrets store.",
        risk_class="SECURITY",
        requires_operator_approval=True,
    )
    assert classified["risk_class"] == "SECURITY"
    assert bool(classified["requires_operator_approval"]) is True


def test_security_risk_task_loaded_from_db_requires_approval() -> None:
    """Per RISK_SYSTEM.md, credential rotation is squarely `risk_class:
    SECURITY` territory. Pre-migration, this classification could never reach
    `evaluate_pre_dispatch` because `map.db` had nowhere to put it, and
    "rotate credential" trips no destructive-text heuristic either -- the task
    would have sailed through as ALLOW_WITHIN_TIER regardless of intent. Post-
    migration, creating the task with `risk_class="SECURITY"` set (as
    `map_task.py create --risk-class SECURITY` now allows) must gate it."""
    task = load_from_fresh_db(
        "TASK-P",
        title="Rotate the production database credential",
        description="Rotate the shared production DB credential and update the secrets store.",
        risk_class="SECURITY",
    )

    # What SHOULD happen once risk_class can travel through -- proves the
    # policy function's own logic is correct; this was never the gap.
    intended = evaluate_pre_dispatch(dict(task, risk_class="SECURITY"), "codex-lab-test", worker_tier=1)
    assert intended["decision"] == "require_approval"
    assert "REQUIRE_SECURITY_STRUCTURAL_APPROVAL" in intended["reasons"]

    # What actually happens with a task loaded from the real schema, now that
    # risk_class was set at creation time and travels through the real path.
    actual = evaluate_pre_dispatch(task, "codex-lab-test", worker_tier=1)
    assert actual["decision"] == "require_approval", (
        "REGRESSION (pre-dispatch-gate-input-migration.md Phase 1): a "
        f"credential-rotation task created with risk_class=SECURITY returns "
        f"{actual['decision']!r} (reasons={actual['reasons']!r}) instead of "
        "require_approval when loaded from map.db"
    )
    assert "REQUIRE_SECURITY_STRUCTURAL_APPROVAL" in actual["reasons"]


def test_authority_decision_task_loaded_from_db_requires_approval() -> None:
    """Per DECISION_CLASSES.md, this is squarely `decision_class: AUTHORITY`
    (changes who may decide things) and requires command-center approval.
    Post-migration, creating the task with `decision_class="AUTHORITY"` set
    must gate it."""
    task = load_from_fresh_db(
        "TASK-P",
        title="Ratify the write-path centralization decision",
        description="Record a binding MAP-wide policy on single-writer map.db access.",
        decision_class="AUTHORITY",
    )

    intended = evaluate_pre_dispatch(dict(task, decision_class="AUTHORITY"), "codex-lab-test", worker_tier=1)
    assert intended["decision"] == "require_approval"
    assert "REQUIRE_COMMAND_CENTER_DECISION" in intended["reasons"]

    actual = evaluate_pre_dispatch(task, "codex-lab-test", worker_tier=1)
    assert actual["decision"] == "require_approval", (
        "REGRESSION (pre-dispatch-gate-input-migration.md Phase 1): an "
        f"authority-decision task created with decision_class=AUTHORITY returns "
        f"{actual['decision']!r} (reasons={actual['reasons']!r}) instead of "
        "require_approval when loaded from map.db"
    )
    assert "REQUIRE_COMMAND_CENTER_DECISION" in actual["reasons"]


def test_operator_tier_task_loaded_from_db_requires_approval() -> None:
    """Per `map-task-tiering-spec.md`, `task_tier: operator` is a routing tier
    meaning "needs an explicit operator response", not a core agent's
    judgment call. It has no text fallback whatsoever. Post-migration,
    creating the task with `task_tier="operator"` set must gate it."""
    task = load_from_fresh_db(
        "TASK-P",
        title="Decide incidents table design",
        description=(
            "Two defensible designs (new `incidents` table vs a `task_type` "
            "discriminator) with no clear technical winner; needs an explicit "
            "operator response."
        ),
        task_tier="operator",
    )

    intended = evaluate_pre_dispatch(dict(task, task_tier="operator"), "codex-lab-test", worker_tier=1)
    assert intended["decision"] == "require_approval"
    assert "REQUIRE_OPERATOR_TIER_APPROVAL" in intended["reasons"]

    actual = evaluate_pre_dispatch(task, "codex-lab-test", worker_tier=1)
    assert actual["decision"] == "require_approval", (
        "REGRESSION (pre-dispatch-gate-input-migration.md Phase 1): an "
        f"operator-tier task created with task_tier=operator returns "
        f"{actual['decision']!r} (reasons={actual['reasons']!r}) instead of "
        "require_approval when loaded from map.db"
    )
    assert "REQUIRE_OPERATOR_TIER_APPROVAL" in actual["reasons"]


def test_requires_operator_approval_task_loaded_from_db_requires_approval() -> None:
    """The starkest of the four: `requires_operator_approval` has zero
    text-heuristic fallback (unlike `destructive_action`, which is partially
    covered by `is_destructive()`'s phrase matching). Literally writing
    "requires operator approval" in the description does nothing on its own
    -- only the boolean field is ever read. Post-migration, creating the task
    with `requires_operator_approval=True` set must gate it."""
    task = load_from_fresh_db(
        "TASK-P",
        title="Publish the emergence coverage feature release checklist",
        description="This work requires operator approval and sign-off before it ships externally.",
        requires_operator_approval=True,
    )

    intended = evaluate_pre_dispatch(dict(task, requires_operator_approval=True), "codex-lab-test", worker_tier=1)
    assert intended["decision"] == "require_approval"
    assert "REQUIRE_OPERATOR_APPROVAL" in intended["reasons"]

    actual = evaluate_pre_dispatch(task, "codex-lab-test", worker_tier=1)
    assert actual["decision"] == "require_approval", (
        "REGRESSION (pre-dispatch-gate-input-migration.md Phase 1): a task "
        f"created with requires_operator_approval=True returns "
        f"{actual['decision']!r} (reasons={actual['reasons']!r}) instead of "
        "require_approval when loaded from map.db"
    )
    assert "REQUIRE_OPERATOR_APPROVAL" in actual["reasons"]


# --- Phase 2 (pre-dispatch-gate-input-migration.md): the eight
# predicate-backed fields. Each already had a working text heuristic before
# this migration; the point of these tests is specifically that the explicit
# field gates a NEUTRALLY-WORDED task that would otherwise sail through on
# phrasing alone -- proving the gate no longer depends on how the task author
# happened to word the title/description. Every baseline task below uses a
# deliberately neutral title/description chosen to trip none of the eight
# text heuristics in pre_dispatch_policy.py.

def test_tasks_table_has_gate_predicate_columns() -> None:
    """Schema-level reality: all eight Phase 2 predicate fields are columns."""
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        init_db(db)
        with sqlite3.connect(db) as conn:
            columns = {row[1] for row in conn.execute("PRAGMA table_info(tasks)")}
    missing = [field for field in GATE_PREDICATE_FIELDS if field not in columns]
    assert missing == [], (
        f"expected all of {GATE_PREDICATE_FIELDS} to be `tasks` columns; missing {missing} -- "
        "the Phase 2 schema migration (pre-dispatch-gate-input-migration.md) "
        "should have added them to migration/schema.sql"
    )


def test_destructive_action_gates_regardless_of_neutral_text() -> None:
    """Niko's own demonstration case: 'clean up the deployment mirror' reads
    as routine, but the action is destructive. Text alone never gated it;
    the explicit field must."""
    kwargs = dict(
        title="Clean up the deployment mirror",
        description="Remove the stale exports directory and regenerate it from source.",
    )
    baseline = load_from_fresh_db("TASK-D0", **kwargs)
    assert evaluate_pre_dispatch(baseline, "codex-lab-test", worker_tier=1)["decision"] == "allow", (
        "baseline task unexpectedly gated -- neutral text tripped a heuristic; fix the fixture, not the assertion"
    )

    flagged = load_from_fresh_db("TASK-D1", destructive_action=True, **kwargs)
    actual = evaluate_pre_dispatch(flagged, "codex-lab-test", worker_tier=1)
    assert actual["decision"] == "require_approval", (
        "REGRESSION (pre-dispatch-gate-input-migration.md Phase 2): a task "
        f"created with destructive_action=True returns {actual['decision']!r} "
        f"(reasons={actual['reasons']!r}) instead of require_approval, despite neutral wording"
    )
    assert "REQUIRE_CORE_DESTRUCTIVE_APPROVAL" in actual["reasons"]


def test_trust_boundary_crossing_gates_regardless_of_neutral_text() -> None:
    """A task that reaches outside MAP's usual boundary, worded blandly."""
    kwargs = dict(
        title="Update the vendor sync helper",
        description="Adjust how the helper coordinates with the paired external partner tool.",
    )
    baseline = load_from_fresh_db("TASK-T0", **kwargs)
    assert evaluate_pre_dispatch(baseline, "codex-lab-test", worker_tier=1)["decision"] == "allow", (
        "baseline task unexpectedly gated -- neutral text tripped a heuristic; fix the fixture, not the assertion"
    )

    flagged = load_from_fresh_db("TASK-T1", trust_boundary_crossing=True, **kwargs)
    actual = evaluate_pre_dispatch(flagged, "codex-lab-test", worker_tier=1)
    assert actual["decision"] == "require_approval", (
        "REGRESSION (pre-dispatch-gate-input-migration.md Phase 2): a task "
        f"created with trust_boundary_crossing=True returns {actual['decision']!r} "
        f"(reasons={actual['reasons']!r}) instead of require_approval, despite neutral wording"
    )
    assert "REQUIRE_UNKNOWN_TRUST_BOUNDARY_APPROVAL" in actual["reasons"]


def test_final_review_gates_regardless_of_neutral_text() -> None:
    """A helper (tier 2+) must never silently finalize a review-shaped task,
    even one that reads as ordinary implementation work."""
    kwargs = dict(
        title="Update the internal glossary spreadsheet",
        description="Adjust wording in a shared internal glossary spreadsheet for clarity.",
    )
    baseline = load_from_fresh_db("TASK-F0", **kwargs)
    assert evaluate_pre_dispatch(baseline, "codex-lab-test", worker_tier=2)["decision"] == "allow", (
        "baseline task unexpectedly gated -- neutral text tripped a heuristic; fix the fixture, not the assertion"
    )

    flagged = load_from_fresh_db("TASK-F1", final_review=True, **kwargs)
    actual = evaluate_pre_dispatch(flagged, "codex-lab-test", worker_tier=2)
    assert actual["decision"] == "reject", (
        "REGRESSION (pre-dispatch-gate-input-migration.md Phase 2): a helper-tier task "
        f"created with final_review=True returns {actual['decision']!r} "
        f"(reasons={actual['reasons']!r}) instead of reject, despite neutral wording"
    )
    assert "REJECT_HELPER_FINAL_REVIEW" in actual["reasons"]


def test_final_decision_gates_regardless_of_neutral_text() -> None:
    """A helper must never silently make a binding decision, worded neutrally
    or not."""
    kwargs = dict(
        title="Update the internal glossary spreadsheet",
        description="Adjust wording in a shared internal glossary spreadsheet for clarity.",
    )
    baseline = load_from_fresh_db("TASK-N0", **kwargs)
    assert evaluate_pre_dispatch(baseline, "codex-lab-test", worker_tier=2)["decision"] == "allow", (
        "baseline task unexpectedly gated -- neutral text tripped a heuristic; fix the fixture, not the assertion"
    )

    flagged = load_from_fresh_db("TASK-N1", final_decision=True, **kwargs)
    actual = evaluate_pre_dispatch(flagged, "codex-lab-test", worker_tier=2)
    assert actual["decision"] == "reject", (
        "REGRESSION (pre-dispatch-gate-input-migration.md Phase 2): a helper-tier task "
        f"created with final_decision=True returns {actual['decision']!r} "
        f"(reasons={actual['reasons']!r}) instead of reject, despite neutral wording"
    )
    assert "REJECT_HELPER_FINAL_DECISION" in actual["reasons"]


def test_broad_architecture_gates_regardless_of_neutral_text() -> None:
    """A helper must not own broad architecture work just because the task
    description undersells its scope."""
    kwargs = dict(
        title="Adjust the shared configuration loader",
        description="Change how the configuration loader is organized across the codebase.",
    )
    baseline = load_from_fresh_db("TASK-B0", **kwargs)
    assert evaluate_pre_dispatch(baseline, "codex-lab-test", worker_tier=2)["decision"] == "allow", (
        "baseline task unexpectedly gated -- neutral text tripped a heuristic; fix the fixture, not the assertion"
    )

    flagged = load_from_fresh_db("TASK-B1", broad_architecture=True, **kwargs)
    actual = evaluate_pre_dispatch(flagged, "codex-lab-test", worker_tier=2)
    assert actual["decision"] == "reject", (
        "REGRESSION (pre-dispatch-gate-input-migration.md Phase 2): a helper-tier task "
        f"created with broad_architecture=True returns {actual['decision']!r} "
        f"(reasons={actual['reasons']!r}) instead of reject, despite neutral wording"
    )
    assert "REJECT_HELPER_BROAD_ARCHITECTURE" in actual["reasons"]


def test_broad_rewrite_gates_regardless_of_neutral_text() -> None:
    """A helper must not take on a broad rewrite that a short description
    makes sound like a small tweak."""
    kwargs = dict(
        title="Touch up the export formatting helper",
        description="Improve how the export helper renders its output.",
    )
    baseline = load_from_fresh_db("TASK-W0", **kwargs)
    assert evaluate_pre_dispatch(baseline, "codex-lab-test", worker_tier=2)["decision"] == "allow", (
        "baseline task unexpectedly gated -- neutral text tripped a heuristic; fix the fixture, not the assertion"
    )

    flagged = load_from_fresh_db("TASK-W1", broad_rewrite=True, **kwargs)
    actual = evaluate_pre_dispatch(flagged, "codex-lab-test", worker_tier=2)
    assert actual["decision"] == "reject", (
        "REGRESSION (pre-dispatch-gate-input-migration.md Phase 2): a helper-tier task "
        f"created with broad_rewrite=True returns {actual['decision']!r} "
        f"(reasons={actual['reasons']!r}) instead of reject, despite neutral wording"
    )
    assert "REJECT_HELPER_BROAD_REWRITE" in actual["reasons"]


def test_canonical_map_mutation_gates_regardless_of_neutral_text() -> None:
    """A helper must not touch canonical MAP state just because the
    description avoids naming the specific file."""
    kwargs = dict(
        title="Refresh the shared status summary",
        description="Bring the shared status summary up to date with the latest known facts.",
    )
    baseline = load_from_fresh_db("TASK-C0", **kwargs)
    assert evaluate_pre_dispatch(baseline, "codex-lab-test", worker_tier=2)["decision"] == "allow", (
        "baseline task unexpectedly gated -- neutral text tripped a heuristic; fix the fixture, not the assertion"
    )

    flagged = load_from_fresh_db("TASK-C1", canonical_map_mutation=True, **kwargs)
    actual = evaluate_pre_dispatch(flagged, "codex-lab-test", worker_tier=2)
    assert actual["decision"] == "reject", (
        "REGRESSION (pre-dispatch-gate-input-migration.md Phase 2): a helper-tier task "
        f"created with canonical_map_mutation=True returns {actual['decision']!r} "
        f"(reasons={actual['reasons']!r}) instead of reject, despite neutral wording"
    )
    assert "REJECT_HELPER_CANONICAL_MUTATION" in actual["reasons"]


def test_shell_required_gates_regardless_of_neutral_text() -> None:
    """A helper must not be handed shell/network access on the strength of a
    description that never says so."""
    kwargs = dict(
        title="Prepare the deploy step",
        description="Set up the next part of the deploy step so it is ready to go.",
    )
    baseline = load_from_fresh_db("TASK-S0", **kwargs)
    assert evaluate_pre_dispatch(baseline, "codex-lab-test", worker_tier=2)["decision"] == "allow", (
        "baseline task unexpectedly gated -- neutral text tripped a heuristic; fix the fixture, not the assertion"
    )

    flagged = load_from_fresh_db("TASK-S1", shell_required=True, **kwargs)
    actual = evaluate_pre_dispatch(flagged, "codex-lab-test", worker_tier=2)
    assert actual["decision"] == "reject", (
        "REGRESSION (pre-dispatch-gate-input-migration.md Phase 2): a helper-tier task "
        f"created with shell_required=True returns {actual['decision']!r} "
        f"(reasons={actual['reasons']!r}) instead of reject, despite neutral wording"
    )
    assert "REJECT_HELPER_SHELL_NETWORK" in actual["reasons"]


def main() -> int:
    tests = [
        test_tasks_table_has_gate_input_columns,
        test_loaded_task_carries_gate_input_keys,
        test_security_risk_task_loaded_from_db_requires_approval,
        test_authority_decision_task_loaded_from_db_requires_approval,
        test_operator_tier_task_loaded_from_db_requires_approval,
        test_requires_operator_approval_task_loaded_from_db_requires_approval,
        test_tasks_table_has_gate_predicate_columns,
        test_destructive_action_gates_regardless_of_neutral_text,
        test_trust_boundary_crossing_gates_regardless_of_neutral_text,
        test_final_review_gates_regardless_of_neutral_text,
        test_final_decision_gates_regardless_of_neutral_text,
        test_broad_architecture_gates_regardless_of_neutral_text,
        test_broad_rewrite_gates_regardless_of_neutral_text,
        test_canonical_map_mutation_gates_regardless_of_neutral_text,
        test_shell_required_gates_regardless_of_neutral_text,
    ]
    failures = 0
    for test in tests:
        try:
            test()
        except AssertionError as exc:
            failures += 1
            print(f"FAIL {test.__name__}: {exc}")
        else:
            print(f"PASS {test.__name__}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
