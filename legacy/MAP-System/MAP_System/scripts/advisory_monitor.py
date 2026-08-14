#!/usr/bin/env python3
"""Real-time advisory monitor for MAP coordination health (proposal-only).

Purpose (operator directive, 2026-07-18): catch "we are doing something
wrong" WHILE work happens, instead of at a later code review or a batch
audit — and surface E/I candidates continuously rather than only at
project end.

Design constraints (from book-lessons-agent-system.md and the ClearFront
delivery audit):
- READ-ONLY. Reads map.db (read-only), events.jsonl, agents/status.json.
  Never claims, edits, approves, or mutates any state.
- DETERMINISTIC FIRST. Every check here is a mechanical rule with a clear
  signature — no model call. A model helper is only for genuine novelty
  judgment ("is this recurrence worth a NEW insight?"), layered on top,
  never in the mechanical path. This is exactly the "don't let a model
  call become an unreviewed control plane" rule.
- PROPOSAL-ONLY. Output is candidate findings a core agent triages into a
  fix, an E/I insight, or a dismissal. The monitor promotes nothing.
- VISIBLE. Structured stdout (and optional JSON) meant for the Command
  Center / an operator, not a hidden log.

Exit code: 0 = no findings, 1 = at least one finding (so it can gate a
visible check or a wake). Findings are NOT failures of this script; they
are things a human/core agent should look at.

Usage:
    python3 MAP_System/scripts/advisory_monitor.py [--json] [--stale-hours N]
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "map.db"
EVENTS = ROOT / "events" / "events.jsonl"
STATUS = ROOT / "agents" / "status.json"

SEV_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

# Statuses after which no further action is owed on a task. APPROVED is
# deliberately NOT here: an APPROVED task still needs a release, and that is
# exactly where tasks owned by departed agents accumulate.
TERMINAL_STATUSES = ("DONE", "RELEASED", "RETIRED")

# Agent statuses that mean the owner still exists and is working. 'busy' is a
# documented live working state — an agent mid-task is not a stale owner, and
# reporting one as departed would be false. Only non-live states are findings.
LIVE_OWNER_STATUSES = ("available", "busy")

# Owner states that mean the owner is gone rather than merely occupied.
GONE_OWNER_STATUSES = ("inactive",)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip().replace("Z", "+00:00").replace(" ", "T", 1)
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def finding(sev: str, kind: str, subject: str, observed: str, impact: str, suggestion: str) -> dict:
    return {
        "severity": sev,
        "kind": kind,
        "subject": subject,
        "observed": observed,
        "impact": impact,
        "suggestion": suggestion,
    }


def describe_claim(claimed_by, lease_raw, lease_dt, heartbeat) -> str:
    """A source-accurate description of a claim's actual state — no invented facts.

    Each element reports exactly what the row holds: a set claimant, whether a
    lease is present/parseable, and whether a heartbeat timestamp exists.
    """
    parts = []
    parts.append(f"claimant {claimed_by}" if claimed_by else "no claimant")
    if lease_raw is None:
        parts.append("no lease")
    elif lease_dt is None:
        parts.append(f"unparseable lease ({lease_raw!r})")
    else:
        parts.append(f"lease {lease_dt.isoformat()}")
    parts.append("heartbeat present" if heartbeat else "no heartbeat")
    return ", ".join(parts)


def check_orphaned_or_expired_claims(conn, now, findings):
    """IN_PROGRESS tasks whose claim is not live.

    An active claim requires BOTH a set claimant AND a parseable, unexpired
    lease. Any other IN_PROGRESS state (no claimant, no/unparseable lease, or
    an expired lease) is a finding — this is the class that lets a task sit
    'in progress' for days with nobody actually on it. Every finding describes
    the row's real state rather than asserting a fixed one.
    """
    for row in conn.execute(
        "SELECT task_id, claimed_by, lease_expires_at, heartbeat_at, owner "
        "FROM tasks WHERE status = 'IN_PROGRESS'"
    ):
        task_id, claimed_by, lease_raw, heartbeat, owner = row
        lease_dt = parse_iso(lease_raw)
        state = describe_claim(claimed_by, lease_raw, lease_dt, heartbeat)
        live = bool(claimed_by) and lease_dt is not None and lease_dt >= now

        if live:
            continue  # healthy: claimant + unexpired lease
        if lease_dt is not None and lease_dt < now:
            age_h = (now - lease_dt).total_seconds() / 3600
            findings.append(finding(
                "HIGH", "expired-lease", task_id,
                f"{task_id} is IN_PROGRESS with an expired lease ({age_h:.1f}h past): {state}"
                f" (nominal owner: {owner or 'unset'}).",
                "The claim looks live but the lease lapsed; expire_leases() should have returned"
                " it to READY and did not, or has not run.",
                "Run reconciliation (expire_leases) or reclaim explicitly; check why the lease was"
                " not renewed (agent down without handoff?).",
            ))
        else:
            # No claimant, or a claimant with no/unparseable lease: not a live claim.
            findings.append(finding(
                "HIGH", "orphaned-in-progress", task_id,
                f"{task_id} is IN_PROGRESS without a live claim: {state}"
                f" (nominal owner: {owner or 'unset'}).",
                "The task looks active but has no valid unexpired lease, so nobody is provably on"
                " it; the runner shows work that will never progress and a resuming agent may skip"
                " it as 'someone else's'.",
                "Reconcile: reclaim with a real owner+lease, or move it to READY/BLOCKED with a"
                " handoff. Confirm against the owner's actual availability.",
            ))


def check_aging_transitions(conn, now, stale_hours, findings):
    """SUBMITTED or CHANGES_REQUESTED tasks sitting past the staleness window."""
    for status, kind, verb in (
        ("SUBMITTED", "review-aging", "awaiting review"),
        ("CHANGES_REQUESTED", "rework-aging", "awaiting rework"),
    ):
        for row in conn.execute(
            "SELECT task_id, owner, updated_at FROM tasks WHERE status = ?", (status,)
        ):
            task_id, owner, updated = row
            updated_dt = parse_iso(updated)
            if not updated_dt:
                continue
            age_h = (now - updated_dt).total_seconds() / 3600
            if age_h >= stale_hours:
                findings.append(finding(
                    "MEDIUM", kind, task_id,
                    f"{task_id} has been {verb} for {age_h:.1f}h (owner {owner or 'unset'}).",
                    "A stalled review/rework blocks the release loop and can hide an unstated"
                    " blocker or a dropped handoff.",
                    f"Confirm a reviewer/owner is assigned and available; if blocked, record the"
                    f" reason. Threshold is {stale_hours}h (advisory, tune per lane).",
                ))


def interpret_event_summary(stdout, returncode):
    """Pure interpretation of validate_events output → a finding dict or None.

    Split from the subprocess call so it is deterministically testable with
    fixture summaries (clean / errors / new-warnings / no-summary).
    """
    summary = ""
    for line in (stdout or "").splitlines():
        if line.startswith("SUMMARY"):
            summary = line
    errors = ("errors=0" not in summary) if summary else (returncode != 0)
    new_warn = bool(summary) and "new_warnings=0" not in summary
    if not (errors or new_warn):
        return None
    return finding(
        "HIGH" if errors else "MEDIUM", "event-log-health", "events.jsonl",
        f"validate_events reports a problem: {summary or 'nonzero exit'}.",
        "A malformed or newly-warning event corrupts the durable activity record the whole"
        " system reads for state and recovery.",
        "Inspect the flagged line(s); fix or remove. Non-task global events and missing"
        " canonical fields are the usual causes.",
    )


def check_event_log_health(findings):
    """Surface event-log validation errors/new warnings the moment they exist.

    This is the exact miss from 2026-07-18: a malformed global event was only
    caught by manually running the validator. A monitor makes it immediate.
    """
    validator = ROOT / "scripts" / "validate_events.py"
    if not validator.exists():
        return
    try:
        result = subprocess.run(
            [sys.executable, str(validator), "--fail-on-new"],
            capture_output=True, text=True, timeout=60, cwd=ROOT,
        )
    except (OSError, subprocess.TimeoutExpired):
        return
    found = interpret_event_summary(result.stdout, result.returncode)
    if found:
        findings.append(found)


def load_status_board(path=None) -> dict:
    """Read agents/status.json into {agent_id: status}, or {} if unreadable.

    status.json is a curated board, not a full mirror of the agents table, so
    an agent missing from it is context rather than a defect on its own.
    """
    try:
        raw = json.loads((path or STATUS).read_text()).get("agents", {})
    except (OSError, json.JSONDecodeError, AttributeError):
        return {}
    return {agent: (entry or {}).get("status") for agent, entry in raw.items()}


def check_owner_liveness(conn, findings, board=None):
    """Nonterminal tasks whose owner is no longer able to act on them.

    Operator directive 2026-07-23: tasks get stranded owned by agents that no
    longer exist. Such tasks are not mechanically stuck — release_task.py has
    no owner gate — but nothing surfaces them, so they age unnoticed and the
    owner-keyed no-self-review guard compares against a ghost.

    Canonical source is the agents table; agents/status.json is cross-checked
    because the two rosters are maintained separately and can disagree.
    Proposal-only, like every check here: it reports, it never reassigns.
    """
    if board is None:
        board = load_status_board()
    db_status = {row[0]: row[1] for row in conn.execute("SELECT agent_id, status FROM agents")}

    placeholders = ",".join("?" * len(TERMINAL_STATUSES))
    for task_id, status, owner in conn.execute(
        f"SELECT task_id, status, owner FROM tasks WHERE status NOT IN ({placeholders})",
        TERMINAL_STATUSES,
    ):
        canonical = db_status.get(owner) if owner else None
        if owner and canonical in LIVE_OWNER_STATUSES:
            continue  # healthy: the owner exists and is working

        mirror = board.get(owner) if owner else None
        if mirror is None:
            cross = "absent from status.json"
        elif mirror != canonical:
            cross = f"status.json disagrees: '{mirror}'"
        else:
            cross = f"status.json agrees: '{mirror}'"

        # Impact and remediation are written per case. A departed owner and a
        # parked one are different situations, and saying "departed" about an
        # agent that is merely standing by would be false.
        gone_impact = (
            "Nothing detects a departed owner, so the task ages unnoticed with no one"
            " accountable for its next transition; per INS-0039 an owner-keyed"
            " no-self-review guard also compares against an identity that cannot object."
        )
        gone_suggestion = (
            "Confirm the owner is really gone, then route the next transition to a live"
            " agent (an APPROVED task can be released by any agent — release_task.py has"
            " no owner gate). Reassigning the owner field itself needs the sanctioned verb"
            " from TASK-273; do not hand-edit SQLite."
        )

        if not owner:
            kind, sev, owner_state = "owner-unset", "HIGH", "no owner is recorded"
            impact, suggestion = gone_impact, gone_suggestion
        elif canonical is None:
            kind, sev = "owner-unknown", "HIGH"
            owner_state = f"owner {owner} is absent from the agents table"
            impact, suggestion = gone_impact, gone_suggestion
        elif canonical in GONE_OWNER_STATUSES:
            kind, sev = "owner-inactive", "HIGH"
            owner_state = f"owner {owner} is '{canonical}'"
            impact, suggestion = gone_impact, gone_suggestion
        else:
            kind, sev = "owner-parked", "MEDIUM"
            owner_state = f"owner {owner} is '{canonical}'"
            impact = (
                f"The owner still exists but is '{canonical}', so nobody is actively moving"
                " the task; the session may return and resume it, or may never come back."
                " This is an attention signal, not evidence that the owner is gone."
            )
            suggestion = (
                "Confirm whether the owner is coming back before doing anything. If it is,"
                " leave the task alone. If it is not, route the next transition to a live"
                " agent (an APPROVED task can be released by any agent). Reassigning the"
                " owner field needs the sanctioned verb from TASK-273."
            )

        findings.append(finding(
            sev, kind, task_id,
            f"{task_id} is {status} but {owner_state} ({cross}).",
            impact, suggestion,
        ))


def check_agent_mirror_drift(conn, findings, board=None):
    """agents/status.json (mirror) vs the agents table (SQLite, canonical)."""
    if board is None:
        board = load_status_board()
    if not board:
        return
    db_status = {
        row[0]: row[1]
        for row in conn.execute("SELECT agent_id, status FROM agents")
    }
    for agent, mirror in board.items():
        canonical = db_status.get(agent)
        if canonical is not None and mirror is not None and mirror != canonical:
            findings.append(finding(
                "MEDIUM", "agent-mirror-drift", agent,
                f"{agent}: status.json says '{mirror}', map.db says '{canonical}'.",
                "The durable board and its SQLite source disagree; a reader may trust a stale"
                " availability and route work to a down agent (or skip a live one).",
                "Re-export mirrors (migration/export_to_files.py) and check which write path"
                " skipped the sync.",
            ))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    parser.add_argument("--stale-hours", type=float, default=24.0,
                        help="age (h) before a SUBMITTED/CHANGES_REQUESTED task is flagged")
    args = parser.parse_args()

    now = now_utc()
    findings: list[dict] = []

    # Read-only DB connection (immutable URI so a bug here can never write).
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        board = load_status_board()
        check_orphaned_or_expired_claims(conn, now, findings)
        check_aging_transitions(conn, now, args.stale_hours, findings)
        check_owner_liveness(conn, findings, board)
        check_agent_mirror_drift(conn, findings, board)
    finally:
        conn.close()
    check_event_log_health(findings)

    findings.sort(key=lambda f: SEV_ORDER.get(f["severity"], 9))

    if args.json:
        print(json.dumps({"generated_at": now.isoformat(), "findings": findings}, indent=2))
    else:
        print(f"MAP advisory monitor — {now.isoformat()}")
        if not findings:
            print("no findings; coordination state looks healthy.")
        for f in findings:
            print(f"\n[{f['severity']}] {f['kind']} — {f['subject']}")
            print(f"  OBSERVED:   {f['observed']}")
            print(f"  IMPACT:     {f['impact']}")
            print(f"  SUGGESTION: {f['suggestion']}")
        print(f"\n{len(findings)} finding(s). Proposal-only: a core agent triages"
              " each into a fix, an E/I insight, or a dismissal.")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
