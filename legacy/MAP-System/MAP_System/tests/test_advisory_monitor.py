#!/usr/bin/env python3
"""Focused tests for advisory_monitor.py detection logic (TASK-236).

Every check is exercised in isolation against fixture data, so a regression
is attributable to one check rather than to whatever the live board happened
to contain: orphaned/expired claims, aging transitions, owner liveness,
agent mirror drift, and event-log health — plus a clean-state case proving
none of them false-positives on a healthy board.

Event-log health is tested through `interpret_event_summary`, the pure half
of that check; the subprocess half only shells out to the validator.

Run: python3 MAP_System/tests/test_advisory_monitor.py
"""
import sqlite3
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import advisory_monitor as mon  # noqa: E402


def fixture_conn(rows, agents=None):
    """In-memory tasks (+ optional agents) table with the columns checks read."""
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE tasks (task_id TEXT, status TEXT, claimed_by TEXT, "
        "lease_expires_at TEXT, heartbeat_at TEXT, owner TEXT, updated_at TEXT)"
    )
    conn.executemany(
        "INSERT INTO tasks (task_id,status,claimed_by,lease_expires_at,"
        "heartbeat_at,owner,updated_at) VALUES (?,?,?,?,?,?,?)", rows
    )
    conn.execute("CREATE TABLE agents (agent_id TEXT, status TEXT)")
    conn.executemany(
        "INSERT INTO agents (agent_id,status) VALUES (?,?)", list((agents or {}).items())
    )
    return conn


def run():
    now = mon.now_utc()
    iso = lambda dt: dt.isoformat()
    passed = failed = 0

    def check(label, cond):
        nonlocal passed, failed
        if cond:
            passed += 1; print(f"PASS {label}")
        else:
            failed += 1; print(f"FAIL {label}")

    # 1. Orphaned IN_PROGRESS (the TASK-186 signature): no claimant/lease/heartbeat.
    f = []
    mon.check_orphaned_or_expired_claims(
        fixture_conn([("T-1", "IN_PROGRESS", None, None, None, "someone", None)]), now, f)
    check("orphaned in-progress flagged HIGH",
          len(f) == 1 and f[0]["kind"] == "orphaned-in-progress" and f[0]["severity"] == "HIGH")

    # 2. Expired lease: claimant set but lease in the past.
    f = []
    mon.check_orphaned_or_expired_claims(
        fixture_conn([("T-2", "IN_PROGRESS", "agent-x", iso(now - timedelta(hours=3)), None, "agent-x", None)]),
        now, f)
    check("expired lease flagged", len(f) == 1 and f[0]["kind"] == "expired-lease")

    # 3. Healthy live claim: claimant + future lease → no finding.
    f = []
    mon.check_orphaned_or_expired_claims(
        fixture_conn([("T-3", "IN_PROGRESS", "agent-y", iso(now + timedelta(minutes=20)), iso(now), "agent-y", None)]),
        now, f)
    check("healthy live claim produces no finding", f == [])

    # --- malformed / non-live claim states (lilo review, REQUIRED #2) ---
    # An active claim is a claimant AND a parseable, unexpired lease. Every
    # other shape is a finding, and each finding must describe the row's real
    # state without inventing facts.

    # 3a. Claimant set but no lease at all → not live.
    f = []
    mon.check_orphaned_or_expired_claims(
        fixture_conn([("T-3a", "IN_PROGRESS", "agent-z", None, None, "agent-z", None)]), now, f)
    check("claimant without lease flagged, described accurately",
          len(f) == 1 and f[0]["kind"] == "orphaned-in-progress"
          and "claimant agent-z" in f[0]["observed"] and "no lease" in f[0]["observed"])

    # 3b. Claimant with an unparseable lease → not live, and the raw value shows.
    f = []
    mon.check_orphaned_or_expired_claims(
        fixture_conn([("T-3b", "IN_PROGRESS", "agent-z", "not-a-date", None, "agent-z", None)]),
        now, f)
    check("claimant with malformed lease flagged and raw value reported",
          len(f) == 1 and "unparseable lease" in f[0]["observed"]
          and "not-a-date" in f[0]["observed"])

    # 3c. A future lease with no claimant is still not a live claim.
    f = []
    mon.check_orphaned_or_expired_claims(
        fixture_conn([("T-3c", "IN_PROGRESS", None, iso(now + timedelta(hours=1)), None, "o", None)]),
        now, f)
    check("lease without claimant flagged, not treated as live",
          len(f) == 1 and f[0]["kind"] == "orphaned-in-progress"
          and "no claimant" in f[0]["observed"])

    # 3d. Heartbeat-only: must NOT be described as "no heartbeat".
    f = []
    mon.check_orphaned_or_expired_claims(
        fixture_conn([("T-3d", "IN_PROGRESS", None, None, iso(now), "o", None)]), now, f)
    check("heartbeat-only state reports heartbeat present, not absent",
          len(f) == 1 and "heartbeat present" in f[0]["observed"]
          and "no heartbeat" not in f[0]["observed"])

    # 4. Aging SUBMITTED past the window → flagged; fresh → not.
    f = []
    conn = fixture_conn([
        ("T-4", "SUBMITTED", None, None, None, "o", iso(now - timedelta(hours=48))),
        ("T-5", "SUBMITTED", None, None, None, "o", iso(now - timedelta(hours=1))),
    ])
    mon.check_aging_transitions(conn, now, 24.0, f)
    check("aging SUBMITTED flagged, fresh one not",
          len(f) == 1 and f[0]["subject"] == "T-4" and f[0]["kind"] == "review-aging")

    # 5. Aging CHANGES_REQUESTED → rework-aging.
    f = []
    mon.check_aging_transitions(
        fixture_conn([("T-6", "CHANGES_REQUESTED", None, None, None, "o", iso(now - timedelta(hours=30)))]),
        now, 24.0, f)
    check("aging CHANGES_REQUESTED flagged as rework-aging",
          len(f) == 1 and f[0]["kind"] == "rework-aging")

    # --- owner liveness (operator-directed increment, 2026-07-23) ---

    # 6. Owner absent from the agents table entirely.
    f = []
    mon.check_owner_liveness(
        fixture_conn([("T-9", "APPROVED", None, None, None, "ghost", None)], agents={}), f, board={})
    check("owner absent from agents table flagged HIGH owner-unknown",
          len(f) == 1 and f[0]["kind"] == "owner-unknown" and f[0]["severity"] == "HIGH")

    # 7. Owner present but inactive — the stranded-task signature the operator hit.
    f = []
    mon.check_owner_liveness(
        fixture_conn([("T-10", "APPROVED", None, None, None, "gone", None)],
                     agents={"gone": "inactive"}), f, board={})
    check("inactive owner flagged HIGH owner-inactive",
          len(f) == 1 and f[0]["kind"] == "owner-inactive" and f[0]["severity"] == "HIGH")

    # 8. Owner on standby: not gone, just parked → MEDIUM, distinct kind, and
    #    the text must not claim the owner departed.
    f = []
    mon.check_owner_liveness(
        fixture_conn([("T-11", "APPROVED", None, None, None, "parked", None)],
                     agents={"parked": "standby"}), f, board={})
    check("standby owner flagged MEDIUM owner-parked",
          len(f) == 1 and f[0]["kind"] == "owner-parked" and f[0]["severity"] == "MEDIUM")
    check("standby finding does not claim the owner departed",
          len(f) == 1 and "departed" not in f[0]["impact"]
          and "may return" in f[0]["impact"])

    # 8a. A BUSY owner is live and working, not departed (lori re-review,
    #     REQUIRED). This branch has no live instance today — zero nonterminal
    #     tasks have a busy owner — so only a fixture can prove it.
    f = []
    mon.check_owner_liveness(
        fixture_conn([("T-11b", "IN_PROGRESS", "worker", None, None, "worker", None)],
                     agents={"worker": "busy"}), f, board={"worker": "busy"})
    check("busy owner produces no stale-owner finding", f == [])

    # 9. Available owner → no finding, and terminal tasks are never inspected
    #    even when their owner is long gone.
    f = []
    mon.check_owner_liveness(
        fixture_conn([
            ("T-12", "APPROVED", None, None, None, "live", None),
            ("T-13", "RELEASED", None, None, None, "gone", None),
            ("T-14", "DONE", None, None, None, "gone", None),
            ("T-15", "RETIRED", None, None, None, "gone", None),
        ], agents={"live": "available", "gone": "inactive"}), f, board={})
    check("available owner and terminal tasks produce no findings", f == [])

    # 10. The two rosters disagree: map.db is canonical, status.json is reported.
    f = []
    mon.check_owner_liveness(
        fixture_conn([("T-16", "APPROVED", None, None, None, "split", None)],
                     agents={"split": "inactive"}), f, board={"split": "available"})
    check("roster disagreement surfaced in the finding",
          len(f) == 1 and "status.json disagrees: 'available'" in f[0]["observed"])

    # 11. A task with no owner at all is its own defect.
    f = []
    mon.check_owner_liveness(
        fixture_conn([("T-17", "READY", None, None, None, None, None)], agents={}), f, board={})
    check("unset owner flagged as owner-unset",
          len(f) == 1 and f[0]["kind"] == "owner-unset")

    # --- agent mirror drift ---

    # 12. Mirror disagrees with SQLite → flagged; agreement and agents the board
    #     does not carry → silent (status.json is curated, not a full mirror).
    f = []
    conn = fixture_conn([], agents={"a1": "available", "a2": "inactive", "a3": "available"})
    mon.check_agent_mirror_drift(conn, f, board={"a1": "busy", "a2": "inactive"})
    check("mirror drift flagged only for the disagreeing agent",
          len(f) == 1 and f[0]["kind"] == "agent-mirror-drift" and f[0]["subject"] == "a1")

    # 13. Unreadable/empty board must not fabricate drift.
    f = []
    mon.check_agent_mirror_drift(fixture_conn([], agents={"a1": "available"}), f, board={})
    check("empty status board yields no drift findings", f == [])

    # --- event-log health (pure interpretation half) ---

    # 14. Clean summary → no finding.
    check("clean event summary yields no finding",
          mon.interpret_event_summary("SUMMARY errors=0 new_warnings=0", 0) is None)

    # 15. Errors → HIGH.
    ev = mon.interpret_event_summary("SUMMARY errors=3 new_warnings=0", 1)
    check("event errors flagged HIGH",
          ev is not None and ev["severity"] == "HIGH" and ev["kind"] == "event-log-health")

    # 16. New warnings only → MEDIUM.
    ev = mon.interpret_event_summary("SUMMARY errors=0 new_warnings=2", 0)
    check("new event warnings flagged MEDIUM", ev is not None and ev["severity"] == "MEDIUM")

    # 17. No SUMMARY line at all: fall back to the exit code.
    check("missing summary with clean exit yields no finding",
          mon.interpret_event_summary("", 0) is None)
    ev = mon.interpret_event_summary("", 1)
    check("missing summary with nonzero exit flagged HIGH",
          ev is not None and ev["severity"] == "HIGH")

    # --- clean state, every DB check together ---

    # 18. Clean board exercising EVERY check (lilo review, REQUIRED #1): a
    #     RELEASED task, a fresh in-progress claim, a fresh SUBMITTED task,
    #     live owners, an agreeing mirror, and a clean event summary → zero
    #     findings from any check, including the two that are not DB reads.
    f = []
    conn = fixture_conn([
        ("T-7", "RELEASED", None, None, None, "o", iso(now)),
        ("T-8", "IN_PROGRESS", "a", iso(now + timedelta(minutes=30)), iso(now), "a", None),
        ("T-8b", "SUBMITTED", None, None, None, "o", iso(now - timedelta(hours=1))),
        ("T-8c", "READY", None, None, None, "b", None),
    ], agents={"a": "available", "o": "available", "b": "busy"})
    board = {"a": "available", "b": "busy"}
    mon.check_orphaned_or_expired_claims(conn, now, f)
    mon.check_aging_transitions(conn, now, 24.0, f)
    mon.check_owner_liveness(conn, f, board=board)
    mon.check_agent_mirror_drift(conn, f, board=board)
    event_finding = mon.interpret_event_summary("SUMMARY errors=0 new_warnings=0", 0)
    if event_finding:
        f.append(event_finding)
    check("clean board yields no findings from any check", f == [])

    print(f"\n{passed}/{passed + failed} advisory-monitor tests passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(run())
