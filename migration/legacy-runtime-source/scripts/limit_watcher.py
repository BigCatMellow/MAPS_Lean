#!/usr/bin/env python3
"""Rise & Shine (RnS) limit watcher: auto-resume agents after usage limits.

v1 (TASK-080): nudge agents whose agents/status.json records out_of_tokens
with a passed ISO-8601 resume_after. One nudge per window, visible tabs only.

v2 (TASK-083, after the 2026-07-02 overnight incident): sessions usually hit
the wall with NO final turn -- they never write a status record -- and hcom
keeps listing the stopped session, so absence-based detection never fires.
v2 therefore:

- classifies liveness from `hcom list --json` status + status_age_seconds
  (a dead session stops updating; its age grows unbounded even while listed);
- opens an "incident" for any previously-live agent that goes not-live with
  no deliberate status.json record;
- tries to extract the actual reset time from the session transcript tail
  (the limit message lands there); if found, schedules the nudge for then;
- otherwise probe-resumes on a capped backoff schedule spanning the 5h
  window, giving up loudly after the last probe.

All resumes are visible (`hcom r <name> --terminal wezterm-tab --go`),
never headless. State: agents/limit-watcher-state.json. Events: canonical
shape in events/events.jsonl.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_FILE = ROOT / "agents" / "status.json"
STATE_FILE = ROOT / "agents" / "limit-watcher-state.json"
DB_FILE = ROOT / "map.db"  # source of truth for agent lifecycle (TASK-186)
EVENT_LOG = ROOT / "events" / "events.jsonl"
TASK_ID = "TASK-083"
# RnS is a service, not an interactive hcom agent. Attribute sends as an
# underscore-safe external identity; --name would require a registered agent
# session and the old hyphenated value was rejected by hcom.
SENDER = "limit_watcher"

LIVE_STATUSES = {"active", "listening", "waiting", "blocked"}
STALE_AGE_SECONDS = 1800  # status unchanged this long => presumed dead
PROBE_SCHEDULE_MINUTES = [15, 45, 90, 150, 240, 330]  # capped backoff per incident
TRANSCRIPT_TAIL_BYTES = 65536
CHECKIN_IDLE_SECONDS = 7200  # 2h live-but-idle with no claim/declaration => check-in
CHECKIN_SAFE_STATUSES = {"listening"}  # ONLY these hcom states are check-in eligible:
# blocked/waiting sessions are stuck on prompts or dependencies, not drifting
# (TASK-084 review finding 1)
STANDBY_REASONS = {"awaiting_work"}  # declared idle: never check-in-nudged
CHECKIN_TASK_ID = "TASK-084"  # check-in events attribute here, not to the RnS incident task
WORK_NUDGE_SECONDS = 1800  # while actionable work exists, ping an idle agent at most every 30min
WORK_NUDGE_MIN_IDLE = 120  # don't ping someone who went idle seconds ago (mid-turn gap)
WORK_TASK_ID = "TASK-095"  # work-dispatch events attribute here (operator #17759)
STALE_CLAIM_OWNER_NUDGE_SECONDS = 1800
STALE_CLAIM_TASK_ID = "TASK-119"
TERMINAL_SESSION_REASONS = {"session_superseded", "disposable_session_ended"}
TERMINAL_TASK_ID = "TASK-186"  # terminal-session suppression events (IDEA-0009)
CONTEXT_ROTATION_TASK_ID = "TASK-271"
ROTATION_DUE_RENOTIFY_SECONDS = 1800  # re-notify a session still over the
    # HARD threshold every 30min, matching WORK_NUDGE_SECONDS/
    # STALE_CLAIM_OWNER_NUDGE_SECONDS elsewhere in this file. checkpoint_due
    # (soft threshold) stays one-shot -- it's an early advisory, not the
    # action-forcing point. Without this, a session that decides to "finish
    # one more bounded step" after its single rotation_due notice never gets
    # reminded again no matter how far past 150k it runs (observed: 80% of
    # measured usage occurring above the hard threshold).
ACTIVE_SESSION_RESUME_RE = re.compile(r"\bstill active\b", re.IGNORECASE)
RECORDED_RESET_FAILURE_RETRY_SECONDS = 300
TRANSCRIPT_LIMIT_FRESH_SECONDS = 900
RESET_GRACE_MINUTES = 5
LIMIT_MARKER_RE = re.compile(
    r"you(?:'|’)ve hit your (?:session|usage) limit", re.IGNORECASE)

# Reasons that carry a recorded `resume_after` RnS will act on. "out_of_tokens"
# is auto-detected from a real provider rate-limit record (see
# detect_fresh_transcript_limits); "scheduled" is an operator-set arbitrary
# future resume (see declare_standby.py --resume-at, TASK-297-adjacent
# request). Both share the exact same due-check/nudge machinery below --
# only the reason differs, and the nudge prompt is picked accordingly so a
# scheduled resume is never misreported as a rate-limit event.
RECORDED_RESET_REASONS = {"out_of_tokens", "scheduled"}

NUDGE_PROMPT = (
    "Rise & Shine (RnS limit watcher, TASK-083): your session appears to have "
    "hit a usage limit and may have reset. Read MAP_System/handoffs/ for your "
    "latest handoff or STATE_SNAPSHOT, check MAP_System/agents/status.json, "
    "set yourself back to available, and resume your in-flight work. If you "
    "are still rate-limited, simply stop; the watcher will retry later."
)

SCHEDULED_NUDGE_PROMPT = (
    "Rise & Shine (RnS limit watcher, TASK-083): an operator scheduled this "
    "resume time for you -- this is not a detected usage limit, just a "
    "requested check-in. Read MAP_System/handoffs/ for your latest handoff "
    "or STATE_SNAPSHOT, check MAP_System/agents/status.json, set yourself "
    "back to available, and continue your in-flight work."
)


def nudge_prompt_for_reason(reason):
    """Pick the nudge prompt matching why this resume was scheduled."""
    return SCHEDULED_NUDGE_PROMPT if reason == "scheduled" else NUDGE_PROMPT


# ---------------------------------------------------------------- v1 logic

def parse_resume_after(value):
    """ISO-8601 string -> aware datetime, or None. Free text is never guessed."""
    if not value or not isinstance(value, str):
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.astimezone()
    return parsed


def decide_nudges(status_data, state, now):
    """Recorded-reset path: agents due a resume per their own status entry."""
    nudges = []
    unparseable = []
    nudged = state.get("nudged", {})
    failed = state.get("failed_nudges", {})
    warned = state.get("warned_unparseable", {})
    for name, entry in sorted(status_data.get("agents", {}).items()):
        if entry.get("status") != "standby" or entry.get("reason") not in RECORDED_RESET_REASONS:
            continue
        raw = entry.get("resume_after")
        parsed = parse_resume_after(raw)
        if parsed is None:
            if warned.get(name) != raw:
                unparseable.append((name, raw))
            continue
        if now < parsed or nudged.get(name) == raw:
            continue
        failure = failed.get(name, {})
        if failure.get("resume_after") == raw:
            last_failed = parse_resume_after(failure.get("last_failed_at"))
            if last_failed is not None and (
                now - last_failed).total_seconds() < RECORDED_RESET_FAILURE_RETRY_SECONDS:
                continue
        nudges.append((name, raw))
    return nudges, unparseable


def clear_recorded_reset_status(status_data, agent):
    """Clear a due out_of_tokens record after RnS confirms a live session."""
    entry = status_data.get("agents", {}).get(agent)
    if not isinstance(entry, dict):
        return False
    before = json.dumps(entry, sort_keys=True)
    entry["status"] = "available"
    entry["reason"] = None
    entry["resume_after"] = None
    notes = str(entry.get("notes") or "")
    marker = "[command-center-token-refresh]"
    if marker in notes:
        parts = [part.strip() for part in notes.split(" | ") if marker not in part]
        entry["notes"] = " | ".join(parts)
    return json.dumps(entry, sort_keys=True) != before


def persist_agent_availability(agent, status, reason, resume_after, dry_run=False):
    """Write agent availability through SQLite, then regenerate mirrors.

    RnS must remain useful when every model is exhausted, so this path is
    deterministic and self-contained.  SQLite is canonical; writing only
    status.json would be reverted by the next export.
    """
    if dry_run:
        print(f"[dry-run] would persist {agent}: {status}/{reason} resume_after={resume_after}")
        return True
    try:
        con = sqlite3.connect(ROOT / "map.db")
        cur = con.execute(
            "UPDATE agents SET status=?, reason=?, resume_after=?, "
            "updated_at=CURRENT_TIMESTAMP WHERE agent_id=?",
            (status, reason, resume_after, agent),
        )
        con.commit()
        con.close()
        if cur.rowcount != 1:
            return False
        exporter = ROOT / "migration" / "export_to_files.py"
        result = subprocess.run(
            [sys.executable, str(exporter)], capture_output=True, text=True,
            timeout=60,
        )
        return result.returncode == 0
    except (OSError, sqlite3.Error, subprocess.TimeoutExpired):
        return False


def live_due_recorded_resets(status_data, state, snapshot, now):
    """Agents whose recorded reset has passed and whose hcom session is live."""
    if snapshot is None:
        return []
    due = []
    for name, entry in sorted(status_data.get("agents", {}).items()):
        if entry.get("status") != "standby" or entry.get("reason") not in RECORDED_RESET_REASONS:
            continue
        raw = entry.get("resume_after")
        parsed = parse_resume_after(raw)
        if parsed is None or now < parsed:
            continue
        failure = state.get("failed_nudges", {}).get(name, {})
        if failure.get("resume_after") == raw:
            last_failed = parse_resume_after(failure.get("last_failed_at"))
            if last_failed is not None and (
                now - last_failed).total_seconds() < RECORDED_RESET_FAILURE_RETRY_SECONDS:
                continue
        if classify_live(snapshot.get(name, {})):
            due.append((name, raw))
    return due


def detect_silent_stops(prev_live, current_live, status_data, already_reported):
    """v1 pure helper, retained for compatibility/tests. v2 incidents subsume it."""
    stops = []
    agents = status_data.get("agents", {})
    for name in sorted(set(prev_live) - set(current_live)):
        entry = agents.get(name, {})
        if entry.get("status") not in (None, "available"):
            continue
        if name in already_reported:
            continue
        stops.append(name)
    return stops


# ---------------------------------------------------------------- v2 logic

def classify_live(entry):
    """An hcom agent entry counts as live if its status is a live state AND
    its session process still exists.

    `process_bound` is the authoritative signal when present (TASK-084): an
    idle-but-alive agent can sit listening for hours (check-in territory,
    not incident territory), while a dead session keeps its last status with
    the process gone. When hcom doesn't report process_bound, fall back to
    the staleness heuristic from the overnight incident (TASK-083): a status
    unchanged for 30+ minutes is presumed dead."""
    if entry.get("status") not in LIVE_STATUSES:
        return False
    bound = entry.get("process_bound")
    if bound is not None:
        return bool(bound)
    age = entry.get("status_age_seconds")
    if isinstance(age, (int, float)) and age > STALE_AGE_SECONDS:
        return False
    return True


def detect_presumed_down(prev_live, snapshot, status_data, incidents):
    """Previously-live agents now not-live, with no deliberate status.json
    record and no open incident. Absence and stale-but-listed both count."""
    down = []
    agents = status_data.get("agents", {})
    live_now = {n for n, e in snapshot.items() if classify_live(e)}
    for name in sorted(set(prev_live) - live_now):
        entry = agents.get(name, {})
        if entry.get("reason"):  # deliberately recorded (out_of_tokens, scheduled, etc.)
            continue
        if name in incidents:
            continue
        down.append(name)
    return down


def is_terminal_session(entry):
    """Durable status.json entry for a session that is dead on purpose
    (TASK-186 / IDEA-0009): superseded by a newer identity, or a disposable
    helper whose work ended. Terminal sessions must never be probed,
    incident-tracked, or nudged back to life."""
    return (entry.get("status") == "inactive"
            and entry.get("reason") in TERMINAL_SESSION_REASONS)


def load_durable_terminal_agents(db_path=None):
    """Terminal lifecycle marks read from SQLite, the declared source of truth.

    TASK-186 / option A (operator decision 2026-07-22). Terminality must NOT be
    resolved from status.json. `migration/export_to_files.py` documents that file
    as "an operational routing view, not a full dump", and lists both terminal
    reasons in NON_OPERATIONAL_REASONS, so it drops exactly the agents this
    feature exists to recognize -- unless they happen to own an active task.
    Measured on live state 2026-07-22, that made the terminal path fire for 2 of
    11 incident-holding agents and silently miss the other 9. Asking a routing
    view a lifecycle question was the defect; the agents table answers it.

    Returns {agent_id: reason}, restricted to TERMINAL_SESSION_REASONS. Opened
    read-only: RnS must never be the writer on this path. Returns {} on any DB
    error so the watcher keeps running (degrading to the status.json view)
    rather than dying when the database is locked or absent.
    """
    path = DB_FILE if db_path is None else db_path
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            rows = con.execute(
                "SELECT agent_id, reason FROM agents WHERE status = 'inactive'"
            ).fetchall()
        finally:
            con.close()
    except (OSError, sqlite3.Error):
        return {}
    return {agent: reason for agent, reason in rows
            if reason in TERMINAL_SESSION_REASONS}


def apply_durable_lifecycle(status_data, db_path=None):
    """Overlay SQLite terminal marks onto the status.json view (TASK-186 / A).

    Reinstates agents the exporter filtered out, so every downstream terminal
    check -- incident closure, suppression reporting, and the existing check-in /
    work-nudge / v1-nudge guards -- sees the same lifecycle fact regardless of
    whether the routing view happened to keep the row.

    In-memory only. The watcher never writes status.json (it is read at
    poll_once and all persistence goes through persist_agent_availability ->
    SQLite -> exporter), so this cannot leak dead identities back into the
    routing view or undo the exporter's filter.
    """
    terminal = load_durable_terminal_agents(db_path)
    if not terminal:
        return status_data
    agents = dict(status_data.get("agents", {}))
    for agent_id, reason in terminal.items():
        entry = dict(agents.get(agent_id, {}))
        entry["status"] = "inactive"
        entry["reason"] = reason
        agents[agent_id] = entry
    merged = dict(status_data)
    merged["agents"] = agents
    return merged


def close_terminal_incidents(state, status_data):
    """Pop open incidents whose agent is now durably terminal (IDEA-0009).
    Each popped incident is labeled closed_reason='terminal_session' so the
    closure is explicit, never a silent drop. Returns [(name, incident)]."""
    agents = status_data.get("agents", {})
    incidents = state.get("incidents", {})
    closed = []
    for name in sorted(n for n in incidents if is_terminal_session(agents.get(n, {}))):
        incident = incidents.pop(name)
        incident["closed_reason"] = "terminal_session"
        closed.append((name, incident))
    return closed


def detect_terminal_suppressions(prev_live, snapshot, status_data):
    """Previously-live agents now not-live whose durable record is terminal:
    the mirror of detect_presumed_down, selecting the sessions RnS must
    deliberately leave dead. IDEA-0009's reversibility condition requires
    every such suppression to be reported, never silent."""
    agents = status_data.get("agents", {})
    live_now = {n for n, e in snapshot.items() if classify_live(e)}
    return [name for name in sorted(set(prev_live) - live_now)
            if is_terminal_session(agents.get(name, {}))]


def prune_absent_session_tracking(state, status_data, snapshot):
    """Drop RnS tracking for historical sessions no longer known anywhere.

    RnS state persists across lab restarts, but hcom session names can be
    disposable helper/tab names. If a name is absent from both durable
    `agents/status.json` and the current hcom snapshot, it is not resumable by
    RnS anymore. Prune those stale names before incident detection/probing so
    old helper sessions do not keep producing probe resumes or fresh incidents.
    """
    known_agents = set(status_data.get("agents", {})) | set(snapshot)
    incidents = state.setdefault("incidents", {})

    pruned_incidents = sorted(name for name in incidents if name not in known_agents)
    for name in pruned_incidents:
        incidents.pop(name, None)

    previous_last_live = list(state.get("last_live", []))
    state["last_live"] = sorted(name for name in previous_last_live if name in known_agents)
    pruned_last_live = sorted(set(previous_last_live) - set(state["last_live"]))

    return {
        "pruned_incidents": pruned_incidents,
        "pruned_last_live": pruned_last_live,
    }


_RESET_PATTERNS = [
    # "resets 3pm", "resets at 3:30 pm", "reset at 11am"
    re.compile(r"reset[s]?\s*(?:at\s*)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)", re.IGNORECASE),
    # "resets at 15:00", "reset 09:30"
    re.compile(r"reset[s]?\s*(?:at\s*)?(\d{1,2}):(\d{2})(?!\s*(?:am|pm))", re.IGNORECASE),
]


def parse_reset_time_from_text(text, now):
    """Find the LAST limit-reset mention and convert to the next occurrence.
    Returns aware datetime or None. Never raises."""
    best = None
    for pat in _RESET_PATTERNS:
        for m in pat.finditer(text):
            best = m
    if best is None:
        return None
    try:
        hour = int(best.group(1))
        minute = int(best.group(2) or 0)
        ampm = (best.group(3) or "").lower() if best.lastindex >= 3 else ""
        if ampm == "pm" and hour != 12:
            hour += 12
        elif ampm == "am" and hour == 12:
            hour = 0
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return None
        candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate <= now:
            candidate += timedelta(days=1)
        return candidate
    except (ValueError, IndexError):
        return None


def read_transcript_reset(path, now):
    """Tail-read a session transcript for a reset time. Bounded, best-effort."""
    try:
        p = Path(path)
        size = p.stat().st_size
        with p.open("rb") as fh:
            fh.seek(max(0, size - TRANSCRIPT_TAIL_BYTES))
            text = fh.read().decode("utf-8", errors="replace")
    except OSError:
        return None
    return parse_reset_time_from_text(text, now)


def read_fresh_transcript_limit(path, now):
    """Return (resume_after, fingerprint) for a fresh provider-limit record.

    Transcript tails are JSONL for the supported interactive agents.  Requiring
    both the provider's explicit limit marker and a recent record timestamp
    prevents yesterday's reset message from being reinterpreted as tomorrow's
    reset.  The five-minute grace matches the operator's RnS convention.
    """
    try:
        p = Path(path)
        size = p.stat().st_size
        with p.open("rb") as fh:
            fh.seek(max(0, size - TRANSCRIPT_TAIL_BYTES))
            lines = fh.read().decode("utf-8", errors="replace").splitlines()
    except OSError:
        return None

    found = None
    for line in lines:
        if not LIMIT_MARKER_RE.search(line) or "reset" not in line.lower():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        # Provider provenance matters: tool output, user prompts, and hcom
        # relays can quote the exact same sentence. Claude marks its synthetic
        # quota records as rate_limit/429; Codex emits provider-facing errors
        # as event_msg records. Never infer a limit from arbitrary prose.
        payload = record.get("payload") if isinstance(record.get("payload"), dict) else {}
        provider_record = (
            record.get("error") == "rate_limit"
            or record.get("isApiErrorMessage") is True
            or record.get("apiErrorStatus") == 429
            or (record.get("type") == "event_msg"
                and payload.get("type") in {"agent_message", "error", "turn_aborted"})
        )
        if not provider_record:
            continue
        event_at = parse_resume_after(record.get("timestamp"))
        if event_at is None:
            continue
        age = (now - event_at.astimezone(now.tzinfo)).total_seconds()
        if age < -60 or age > TRANSCRIPT_LIMIT_FRESH_SECONDS:
            continue
        reset_at = parse_reset_time_from_text(line, event_at.astimezone(now.tzinfo))
        if reset_at is None:
            continue
        resume_after = reset_at + timedelta(minutes=RESET_GRACE_MINUTES)
        fingerprint = hashlib.sha256(line.encode("utf-8")).hexdigest()
        found = (resume_after, fingerprint)
    return found


def detect_fresh_transcript_limits(snapshot, status_data, state, now):
    """Find newly observed live-session limit records, once per transcript event."""
    if snapshot is None:
        return []
    known = status_data.get("agents", {})
    seen = state.get("transcript_limit_events", {})
    found = []
    for name, live in sorted(snapshot.items()):
        if name not in known or is_terminal_session(known.get(name, {})):
            continue
        transcript = live.get("transcript_path")
        if not transcript:
            continue
        result = read_fresh_transcript_limit(transcript, now)
        if result is None:
            continue
        resume_after, fingerprint = result
        if seen.get(name) == fingerprint:
            continue
        found.append((name, resume_after, fingerprint))
    return found


def probe_action(incident, now):
    """Pure: what should happen for an open incident right now?
    Returns 'wait' | 'nudge' | 'give_up'.

    Backoff anchoring (TASK-083 review finding 1): retries after a
    scheduled-reset nudge anchor to the reset nudge time, NOT detected_at —
    otherwise all earlier backoff slots are already overdue the moment the
    reset nudge fires, and consecutive polls burn probes back-to-back."""
    reset_at = parse_resume_after(incident.get("reset_at"))
    if reset_at is not None:
        if now < reset_at:
            return "wait"
        if not incident.get("reset_nudged"):
            return "nudge"
    probes = incident.get("probes_sent", 0)
    if probes >= len(PROBE_SCHEDULE_MINUTES):
        return "wait" if incident.get("gave_up") else "give_up"
    anchor = parse_resume_after(incident.get("reset_nudged_at")) \
        or parse_resume_after(incident.get("detected_at"))
    if anchor is None:
        return "give_up"
    due = anchor + timedelta(minutes=PROBE_SCHEDULE_MINUTES[probes])
    return "nudge" if now >= due else "wait"


def decide_checkins(snapshot, status_data, claimed_agents, state, now):
    """Pure (TASK-084 / IDEA-0007): live agents that are neither working a
    claimed task nor declared standby, idle past the check-in threshold.

    Safety boundaries from the idea card: a declared reason of any kind
    suppresses (awaiting_work, out_of_tokens, ...), an IN_PROGRESS claim
    suppresses, non-'available' durable status suppresses, and re-nudges are
    throttled to one per idle window."""
    due = []
    agents = status_data.get("agents", {})
    last_checkins = state.get("checkins", {})
    for name, entry in sorted(snapshot.items()):
        if not classify_live(entry):
            continue  # not live: RnS incident territory, not check-in territory
        if entry.get("status") not in CHECKIN_SAFE_STATUSES:
            continue  # active = working; blocked/waiting = stuck, not drifting
        age = entry.get("status_age_seconds")
        if not isinstance(age, (int, float)) or age < CHECKIN_IDLE_SECONDS:
            continue
        durable = agents.get(name, {})
        if durable.get("reason"):
            continue  # declared standby/limit/blocked/etc.
        if durable.get("status") not in (None, "available"):
            continue
        if name in claimed_agents:
            continue  # owns in-flight claimed work
        last = parse_resume_after(last_checkins.get(name))
        if last is not None and (now - last).total_seconds() < CHECKIN_IDLE_SECONDS:
            continue  # already nudged this window
        due.append(name)
    return due


def actionable_work():
    """Claimable/reviewable MAP work from SQLite, read-only; None on failure.

    Categories (TASK-095, operator #17759): READY tasks under max attempts,
    SUBMITTED tasks needing a non-owner review, CHANGES_REQUESTED rework, and
    IN_PROGRESS claims whose lease has expired (coordination needed)."""
    try:
        import sqlite3
        con = sqlite3.connect(f"file:{ROOT / 'map.db'}?mode=ro", uri=True)
        work = {
            "ready": con.execute(
                "SELECT task_id, title, owner FROM tasks WHERE status='READY'"
                " AND attempt < max_attempts ORDER BY task_id").fetchall(),
            "review": con.execute(
                "SELECT task_id, title, owner FROM tasks WHERE status='SUBMITTED'"
                " ORDER BY task_id").fetchall(),
            "rework": con.execute(
                "SELECT task_id, title, owner FROM tasks WHERE status='CHANGES_REQUESTED'"
                " ORDER BY task_id").fetchall(),
            "stale_claim": con.execute(
                "SELECT task_id, title, claimed_by FROM tasks WHERE status='IN_PROGRESS'"
                " AND lease_expires_at IS NOT NULL AND lease_expires_at < datetime('now')"
                " ORDER BY task_id").fetchall(),
        }
        con.close()
        return work if any(work.values()) else {}
    except Exception:
        return None


def stale_claims():
    """Expired IN_PROGRESS claims that can stall the visible queue.

    This is separate from actionable_work(): recovered/idle agents should not
    steal another agent's claim, but the claim owner should be asked to resume,
    submit, release/rework, or explicitly pause.
    """
    try:
        import sqlite3
        con = sqlite3.connect(f"file:{ROOT / 'map.db'}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        rows = con.execute(
            """
            SELECT task_id, title, owner, claimed_by, lease_expires_at
            FROM tasks
            WHERE status='IN_PROGRESS'
              AND claimed_by IS NOT NULL
              AND lease_expires_at IS NOT NULL
              AND lease_expires_at < datetime('now')
            ORDER BY task_id
            """
        ).fetchall()
        con.close()
        return [dict(row) for row in rows]
    except Exception:
        return None


def describe_work(work, agent):
    """Bounded, per-agent work list: reviews exclude the agent's own tasks."""
    parts = []
    if work.get("ready"):
        parts.append("claimable: " + ", ".join(t for t, _, _ in work["ready"][:5]))
    reviews = [t for t, _, owner in work.get("review", []) if owner != agent]
    if reviews:
        parts.append("needs non-owner review: " + ", ".join(reviews[:5]))
    rework = [t for t, _, owner in work.get("rework", []) if owner == agent]
    if rework:
        parts.append("your rework: " + ", ".join(rework[:5]))
    if work.get("stale_claim"):
        parts.append("stale claims needing coordination: "
                     + ", ".join(t for t, _, _ in work["stale_claim"][:5]))
    return "; ".join(parts)


def decide_work_nudges(snapshot, status_data, claimed_agents, work, state, now):
    """Pure: live listening agents with no claim and no declaration, while
    actionable work exists. Same suppression boundaries as decide_checkins
    (TASK-084) but on a shorter throttle and no 2h idle requirement — the
    point is 'the queue is not empty', not 'you drifted'."""
    if not work:
        return []
    due = []
    agents = status_data.get("agents", {})
    last_nudges = state.get("work_nudges", {})
    for name, entry in sorted(snapshot.items()):
        if not classify_live(entry):
            continue
        if entry.get("status") not in CHECKIN_SAFE_STATUSES:
            continue
        age = entry.get("status_age_seconds")
        if not isinstance(age, (int, float)) or age < WORK_NUDGE_MIN_IDLE:
            continue
        durable = agents.get(name, {})
        if durable.get("reason"):
            continue  # declared standby/limit/etc.
        if durable.get("status") not in (None, "available"):
            continue
        if name in claimed_agents:
            continue
        if not describe_work(work, name):
            continue  # everything actionable is this agent's own submission
        last = parse_resume_after(last_nudges.get(name))
        if last is not None and (now - last).total_seconds() < WORK_NUDGE_SECONDS:
            continue
        due.append(name)
    return due


def decide_stale_claim_owner_nudges(claims, state, now):
    """Pure: group expired claims by claimer and throttle per task.

    A stale claim can make the runner show no READY work even though the
    pipeline is stalled. RnS should not auto-reassign it, but it should ask the
    current claimer to make the state explicit.
    """
    if not claims:
        return {}
    last_nudges = state.get("stale_claim_owner_nudges", {})
    grouped = {}
    for claim in claims:
        task_id = claim.get("task_id")
        agent = claim.get("claimed_by") or claim.get("owner")
        if not task_id or not agent:
            continue
        last = parse_resume_after(last_nudges.get(task_id))
        if last is not None and (now - last).total_seconds() < STALE_CLAIM_OWNER_NUDGE_SECONDS:
            continue
        grouped.setdefault(agent, []).append(claim)
    return grouped


def claimed_agent_ids():
    """Agents currently holding IN_PROGRESS claims in SQLite; None on failure."""
    try:
        import sqlite3
        con = sqlite3.connect(ROOT / "map.db")
        rows = con.execute(
            "SELECT DISTINCT claimed_by FROM tasks "
            "WHERE status='IN_PROGRESS' AND claimed_by IS NOT NULL").fetchall()
        con.close()
        return {r[0] for r in rows}
    except Exception:
        return None


# ------------------------------------------------------------- side effects

def append_event(event_type, summary, artifact_paths=None, dry_run=False, task_id=None):
    event = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "type": event_type,
        "task_id": task_id or TASK_ID,
        "sender": SENDER,
        "summary": summary,
        "artifact_paths": artifact_paths or [],
    }
    if dry_run:
        print(f"[dry-run] event: {json.dumps(event)}")
        return
    with EVENT_LOG.open("a") as fh:
        fh.write(json.dumps(event) + "\n")


def hcom_snapshot():
    """{name: entry} from `hcom list --json`; {} if genuinely no agents;
    None only when hcom itself fails."""
    try:
        out = subprocess.run(["hcom", "list", "--json"],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError:
        return None
    snap = {}
    for entry in data if isinstance(data, list) else []:
        name = entry.get("name")
        if name:
            snap[name] = entry
    return snap


def send_nudge(agent, dry_run=False, kind="resume", prompt=NUDGE_PROMPT):
    announce = ["hcom", "send", f"@{agent}", "--intent", "inform", "--from", SENDER,
                "--", f"!NOTE RnS: {kind} nudge for {agent} (TASK-083)."]
    resume = ["hcom", "r", agent, "--terminal", "wezterm-tab", "--go",
              "--hcom-prompt", prompt]
    if dry_run:
        print(f"[dry-run] would announce + run: {' '.join(resume)}")
        return True
    try:
        subprocess.run(announce, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"warning: RnS announce failed for {agent}: {exc}", file=sys.stderr)
    try:
        result = subprocess.run(resume, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired as exc:
        print(f"warning: RnS resume timed out for {agent}: {exc}", file=sys.stderr)
        return False
    except OSError as exc:
        print(f"warning: RnS resume failed for {agent}: {exc}", file=sys.stderr)
        return False
    if is_active_session_resume_failure(result):
        return send_active_session_nudge(agent, dry_run=dry_run, kind=kind, prompt=prompt)
    return result.returncode == 0


def send_active_session_nudge(agent, dry_run=False, kind="resume", prompt=NUDGE_PROMPT):
    active_fallback = ["hcom", "send", f"@{agent}", "--intent", "inform", "--from", SENDER,
                       "--", (
                           f"!NOTE RnS active-session fallback for {agent} (TASK-083): "
                           f"{kind} nudge for a live session. {prompt}"
                       )]
    if dry_run:
        print(f"[dry-run] would active-session nudge {agent}: {kind}")
        return True
    try:
        fallback = subprocess.run(
            active_fallback, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"warning: RnS active-session fallback failed for {agent}: {exc}",
              file=sys.stderr)
        return False
    return fallback.returncode == 0


def is_active_session_resume_failure(result):
    if result.returncode == 0:
        return False
    text = f"{getattr(result, 'stdout', '') or ''}\n{getattr(result, 'stderr', '') or ''}"
    return ACTIVE_SESSION_RESUME_RE.search(text) is not None


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {}


def decide_context_rotation_notifications(token_status, live_agents, prior, now=None):
    """Return notices due for live sessions past a context threshold.

    Token status must describe the latest prompt/context footprint, never
    cumulative transcript traffic. A below-threshold/unknown row clears the
    prior marker so a genuinely fresh context can be notified later.

    `checkpoint_due` (soft threshold) fires once per transition, same as
    before -- it's an early advisory. `rotation_due` (hard threshold) also
    fires once per transition, but then RE-fires every
    `ROTATION_DUE_RENOTIFY_SECONDS` for as long as the session stays in that
    state, since a session that chooses to finish one more step instead of
    rotating should not go permanently silent about it.

    `prior`/the returned marker dict map agent -> {"fingerprint": str,
    "last_sent_at": iso8601 str}. A bare-string prior entry (pre-escalation
    format) is accepted for one transitional poll and treated as having no
    recorded send time, since old persisted state should not crash decoding.

    Mirrors the caller's commit-on-success discipline: `updated` (the second
    return value) is NOT mutated for an agent while its notice is `due` --
    the caller only writes the new marker in after `notify_agent` confirms
    delivery, same as every other nudge path in this file, so a failed send
    is retried next poll instead of being silently marked sent.
    """
    from context_rotation import rotation_advice

    if now is None:
        now = datetime.now().astimezone()

    due = []
    updated = dict(prior or {})
    present = set()
    for row in token_status.get("agents", []):
        agent = row.get("name")
        if not agent or agent not in live_agents:
            continue
        present.add(agent)
        metrics = row.get("metrics") or {}
        if row.get("tool") == "codex":
            used = metrics.get("last_tokens")
            window = metrics.get("context_window")
            source = "codex_last_context_tokens"
        elif row.get("tool") == "claude":
            used = metrics.get("latest_context_tokens")
            window = metrics.get("context_window")
            source = "claude_latest_prompt_input_estimate"
        else:
            updated.pop(agent, None)
            continue
        advice = {"agent": agent, "tool": row.get("tool"), "metric_source": source,
                  **rotation_advice(used, context_window=window)}
        state = advice["state"]
        if state not in {"checkpoint_due", "rotation_due"}:
            updated.pop(agent, None)
            continue
        fingerprint = f"{state}:{advice.get('soft_at')}:{advice.get('rotate_at')}"
        record = updated.get(agent)
        if isinstance(record, str):
            record = {"fingerprint": record, "last_sent_at": None}
        marker = {"fingerprint": fingerprint, "last_sent_at": now.isoformat(timespec="seconds")}
        if record is None or record.get("fingerprint") != fingerprint:
            advice["renotify"] = False
            due.append((advice, marker))
            continue
        if state == "rotation_due":
            last_sent = parse_resume_after(record.get("last_sent_at"))
            if last_sent is None or (now - last_sent).total_seconds() >= ROTATION_DUE_RENOTIFY_SECONDS:
                advice["renotify"] = True
                due.append((advice, marker))
    for agent in set(updated) - present:
        updated.pop(agent, None)
    return due, updated


def save_state(state, dry_run=False):
    if dry_run:
        return
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, raw_tmp = tempfile.mkstemp(prefix=f".{STATE_FILE.name}.", dir=STATE_FILE.parent)
    tmp = Path(raw_tmp)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, STATE_FILE)
    finally:
        if tmp.exists():
            tmp.unlink()


def poll_once(dry_run=False):
    try:
        status_data = json.loads(STATUS_FILE.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"warning: cannot read {STATUS_FILE}: {exc}", file=sys.stderr)
        return
    # TASK-186 option A: resolve lifecycle from SQLite before anything reads
    # status_data, so terminality does not depend on the exporter's routing
    # filter having kept the row.
    status_data = apply_durable_lifecycle(status_data)
    state = load_state()
    state.setdefault("nudged", {})
    state.setdefault("failed_nudges", {})
    state.setdefault("warned_unparseable", {})
    state.setdefault("incidents", {})
    state.setdefault("last_live", [])
    state.setdefault("transcript_limit_events", {})
    state.setdefault("context_rotation_notifications", {})
    now = datetime.now().astimezone()
    snapshot = hcom_snapshot()

    # TASK-271: deterministic, one-shot context checkpoint/rotation notices.
    # This runs inside the existing local watcher, so no model must remember to
    # poll itself and no extra headless agent is introduced.
    if snapshot is not None:
        try:
            from agent_token_status import build_status
            from context_rotation import notify_agent

            live_names = {name for name, value in snapshot.items() if classify_live(value)}
            due, next_markers = decide_context_rotation_notifications(
                build_status(recent_hours=0), live_names,
                state["context_rotation_notifications"],
            )
            for advice, marker in due:
                if dry_run:
                    print(f"[dry-run] would send context {advice['state']} notice to {advice['agent']}")
                    sent = True
                else:
                    sent = notify_agent(advice)
                if sent:
                    next_markers[advice["agent"]] = marker
                    state["context_rotation_notifications"] = dict(next_markers)
                    # The send is externally visible. Commit its marker
                    # before even the audit append so any later failure cannot
                    # cause the next poll to repeat the notice.
                    save_state(state, dry_run=dry_run)
                    repeat_note = " (re-notify, still over threshold)" if advice.get("renotify") else ""
                    append_event(
                        "PROGRESS",
                        f"Context rotation watcher sent {advice['state']} notice to "
                        f"{advice['agent']} at estimated {advice.get('used_tokens')} tokens "
                        f"(rotate_at={advice.get('rotate_at')}, source={advice.get('metric_source')})"
                        f"{repeat_note}.",
                        dry_run=dry_run, task_id=CONTEXT_ROTATION_TASK_ID,
                    )
            state["context_rotation_notifications"] = next_markers
            # Also persist marker removals when a fresh context drops below
            # threshold or a live agent disappears.
            save_state(state, dry_run=dry_run)
        except Exception as exc:
            print(f"warning: context rotation status check failed: {exc}", file=sys.stderr)

    # v3: detect the provider's explicit limit record while the terminal is
    # still process-bound.  This closes the no-surviving-agent gap: the local
    # service records and schedules recovery without waiting for a model turn
    # or for hcom liveness to decay.
    for agent, resume_after, fingerprint in detect_fresh_transcript_limits(
            snapshot, status_data, state, now):
        raw = resume_after.isoformat(timespec="seconds")
        if persist_agent_availability(
                agent, "standby", "out_of_tokens", raw, dry_run=dry_run):
            entry = status_data["agents"][agent]
            entry["status"] = "standby"
            entry["reason"] = "out_of_tokens"
            entry["resume_after"] = raw
            state["transcript_limit_events"][agent] = fingerprint
            append_event(
                "BLOCKED",
                f"RnS automatically detected a fresh session-limit record for {agent}; "
                f"durable resume scheduled for {raw} (local transcript monitor).",
                dry_run=dry_run,
            )
        else:
            append_event(
                "BLOCKED",
                f"RnS detected a fresh session-limit record for {agent} but could not "
                "persist its durable out_of_tokens state.",
                dry_run=dry_run,
            )

    # v1: recorded-reset path
    for agent, raw in live_due_recorded_resets(status_data, state, snapshot, now):
        reason = status_data.get("agents", {}).get(agent, {}).get("reason")
        kind = "scheduled-resume-live" if reason == "scheduled" else "recorded-reset-live"
        ok = send_active_session_nudge(
            agent, dry_run=dry_run, kind=kind, prompt=nudge_prompt_for_reason(reason))
        if ok:
            ok = persist_agent_availability(
                agent, "available", None, None, dry_run=dry_run)
            if ok:
                clear_recorded_reset_status(status_data, agent)
                state["nudged"][agent] = raw
                state["failed_nudges"].pop(agent, None)
        if not ok:
            state["failed_nudges"][agent] = {
                "resume_after": raw,
                "last_failed_at": now.isoformat(timespec="seconds"),
            }
        why = "scheduled resume" if reason == "scheduled" else "recorded resume"
        append_event("PROGRESS",
            f"RnS: {why} window passed for {agent} (resume_after {raw}); "
            f"hcom shows the session live, direct nudge {'sent and durable status cleared' if ok else 'FAILED'}.",
            dry_run=dry_run)

    nudges, unparseable = decide_nudges(status_data, state, now)
    for agent, raw in unparseable:
        reason = status_data.get("agents", {}).get(agent, {}).get("reason")
        append_event("BLOCKED",
            f"RnS: {agent} has reason={reason!r} but resume_after ({raw!r}) is not a "
            f"parseable timestamp; cannot schedule auto-resume.", dry_run=dry_run)
        state["warned_unparseable"][agent] = raw
    for agent, raw in nudges:
        reason = status_data.get("agents", {}).get(agent, {}).get("reason")
        kind = "scheduled-resume" if reason == "scheduled" else "recorded-reset"
        ok = send_nudge(agent, dry_run=dry_run, kind=kind, prompt=nudge_prompt_for_reason(reason))
        if ok:
            state["nudged"][agent] = raw
            state["failed_nudges"].pop(agent, None)
        else:
            state["failed_nudges"][agent] = {
                "resume_after": raw,
                "last_failed_at": now.isoformat(timespec="seconds"),
            }
        why = "scheduled resume" if reason == "scheduled" else "recorded resume"
        append_event("PROGRESS",
            f"RnS: {why} window passed for {agent} (resume_after {raw}); "
            f"visible resume nudge {'sent' if ok else 'FAILED'}.", dry_run=dry_run)

    # v2: presumed-down incidents
    if snapshot is not None:
        pruned = prune_absent_session_tracking(state, status_data, snapshot)
        if pruned["pruned_incidents"] or pruned["pruned_last_live"]:
            parts = []
            if pruned["pruned_incidents"]:
                parts.append("incidents=" + ",".join(pruned["pruned_incidents"][:8]))
            if pruned["pruned_last_live"]:
                parts.append("last_live=" + ",".join(pruned["pruned_last_live"][:8]))
            append_event(
                "PROGRESS",
                "RnS pruned stale session tracking absent from durable status and "
                f"current hcom snapshot ({'; '.join(parts)}).",
                dry_run=dry_run,
                task_id="TASK-176",
            )

        # terminal sessions (TASK-186 / IDEA-0009): sessions durably recorded
        # dead-on-purpose get open incidents closed and their absence reported
        # as a deliberate suppression — visibly, never silently.
        durable_agents = status_data.get("agents", {})
        for name, inc in close_terminal_incidents(state, status_data):
            reason = durable_agents.get(name, {}).get("reason")
            msg = (f"RnS: incident for {name} closed — session recorded as "
                   f"{reason} (terminal, IDEA-0009). No further probes.")
            print(f"[dry-run] {msg}" if dry_run else msg)
            append_event("PROGRESS", msg, dry_run=dry_run, task_id=TERMINAL_TASK_ID)

        state.setdefault("terminal_suppressed", {})
        for name in detect_terminal_suppressions(state["last_live"], snapshot,
                                                 status_data):
            reason = durable_agents.get(name, {}).get("reason")
            msg = (f"RnS: {name} not live, session recorded as {reason} "
                   f"(terminal, IDEA-0009) — no probe, incident, or nudge.")
            print(f"[dry-run] {msg}" if dry_run else msg)
            if name not in state["terminal_suppressed"]:
                state["terminal_suppressed"][name] = now.isoformat(timespec="seconds")
                append_event("PROGRESS", msg, dry_run=dry_run,
                             task_id=TERMINAL_TASK_ID)

        live_now = sorted(n for n, e in snapshot.items() if classify_live(e))

        # agents that rose again: close incidents
        for name in [n for n in list(state["incidents"]) if n in live_now]:
            inc = state["incidents"].pop(name)
            append_event("PROGRESS",
                f"RnS: {name} is live again (incident opened {inc.get('detected_at')}, "
                f"{inc.get('probes_sent', 0)} probe(s) sent). Incident closed.",
                dry_run=dry_run)

        # newly presumed-down agents: open incidents
        for name in detect_presumed_down(state["last_live"], snapshot,
                                         status_data, state["incidents"]):
            entry = snapshot.get(name, {})
            transcript = entry.get("transcript_path")
            reset_at = read_transcript_reset(transcript, now) if transcript else None
            state["incidents"][name] = {
                "detected_at": now.isoformat(timespec="seconds"),
                "reset_at": reset_at.isoformat(timespec="seconds") if reset_at else None,
                "probes_sent": 0, "reset_nudged": False, "gave_up": False,
            }
            append_event("BLOCKED",
                f"RnS: {name} presumed down without a status record (limit hit with "
                f"no final turn, or crash). "
                + (f"Reset time {reset_at.isoformat(timespec='seconds')} found in its "
                   f"transcript; nudge scheduled." if reset_at else
                   f"No reset time found; probing on backoff "
                   f"{PROBE_SCHEDULE_MINUTES} minutes."), dry_run=dry_run)

        # act on open incidents
        for name, inc in state["incidents"].items():
            action = probe_action(inc, now)
            if action == "nudge":
                reset_known = parse_resume_after(inc.get("reset_at")) is not None \
                    and not inc.get("reset_nudged")
                ok = send_nudge(name, dry_run=dry_run,
                                kind="scheduled-reset" if reset_known else "probe")
                if reset_known:
                    inc["reset_nudged"] = True
                    inc["reset_nudged_at"] = now.isoformat(timespec="seconds")
                else:
                    inc["probes_sent"] = inc.get("probes_sent", 0) + 1
                append_event("PROGRESS",
                    f"RnS: {'scheduled-reset' if reset_known else 'probe'} nudge "
                    f"{'sent' if ok else 'FAILED'} for {name} "
                    f"(probes so far: {inc.get('probes_sent', 0)}).", dry_run=dry_run)
            elif action == "give_up":
                inc["gave_up"] = True
                append_event("BLOCKED",
                    f"RnS: giving up on {name} after {inc.get('probes_sent', 0)} probes "
                    f"across the backoff window. Operator or peer attention needed.",
                    dry_run=dry_run)

        state["last_live"] = live_now

        # check-in path (TASK-084): message-only, never a spawn
        claimed = claimed_agent_ids()
        if claimed is not None:
            state.setdefault("checkins", {})
            for name in decide_checkins(snapshot, status_data, claimed, state, now):
                msg = (f"!NOTE RnS check-in: you've been idle "
                       f"{int(snapshot[name].get('status_age_seconds', 0) // 3600)}h+ with no "
                       f"claimed task and no standby declaration. Is there something you "
                       f"should be doing? If your queue is genuinely empty, run: python3 "
                       f"MAP_System/scripts/declare_standby.py {name}")
                if dry_run:
                    print(f"[dry-run] would check-in nudge {name}: {msg}")
                else:
                    subprocess.run(["hcom", "send", f"@{name}", "--intent", "request",
                                    "--from", SENDER, "--", msg],
                                   capture_output=True, text=True, timeout=30)
                state["checkins"][name] = now.isoformat(timespec="seconds")
                append_event("PROGRESS",
                    f"RnS check-in nudge sent to {name}: live but idle past "
                    f"{CHECKIN_IDLE_SECONDS // 3600}h with no claim and no standby "
                    f"declaration.", dry_run=dry_run, task_id=CHECKIN_TASK_ID)

        # work-dispatch path (TASK-095, operator #17759): message-only, never
        # a claim or spawn — agents decide what to pick up.
        if claimed is not None:
            work = actionable_work()
            if work is not None:
                state.setdefault("work_nudges", {})
                for name in decide_work_nudges(snapshot, status_data, claimed,
                                               work, state, now):
                    listing = describe_work(work, name)
                    msg = (f"!NOTE RnS work dispatch: the MAP queue is not empty and "
                           f"you hold no claim. {listing}. Claim what fits (reviews "
                           f"need a non-owner), or declare standby: python3 "
                           f"MAP_System/scripts/declare_standby.py {name}")
                    if dry_run:
                        print(f"[dry-run] would work-nudge {name}: {msg}")
                    else:
                        subprocess.run(["hcom", "send", f"@{name}", "--intent", "request",
                                        "--from", SENDER, "--", msg],
                                       capture_output=True, text=True, timeout=30)
                    state["work_nudges"][name] = now.isoformat(timespec="seconds")
                    append_event("PROGRESS",
                        f"RnS work-dispatch nudge sent to {name}: actionable MAP work "
                        f"exists ({listing[:160]}) and the agent is idle with no claim.",
                        dry_run=dry_run, task_id=WORK_TASK_ID)

            claims = stale_claims()
            if claims is not None:
                state.setdefault("stale_claim_owner_nudges", {})
                for name, agent_claims in decide_stale_claim_owner_nudges(claims, state, now).items():
                    task_ids = ", ".join(claim["task_id"] for claim in agent_claims[:5])
                    msg = (
                        "Issue: RnS sees stale IN_PROGRESS claim(s) with expired leases "
                        f"owned by you: {task_ids}. This can make recovered agents see "
                        "no READY work while the queue is actually stalled. "
                        "Options: resume and submit the task; release/rework the claim "
                        "so another agent can take it; or state that it is intentionally "
                        "paused and why. Recommendation: resume or release the claim now. "
                        "Needed: update the task state or reply with the pause reason."
                    )
                    if dry_run:
                        print(f"[dry-run] would stale-claim-owner nudge {name}: {msg}")
                    else:
                        subprocess.run(["hcom", "send", f"@{name}", "--intent", "request",
                                        "--from", SENDER, "--", msg],
                                       capture_output=True, text=True, timeout=30)
                    for claim in agent_claims:
                        state["stale_claim_owner_nudges"][claim["task_id"]] = now.isoformat(timespec="seconds")
                    append_event("PROGRESS",
                        f"RnS stale-claim owner nudge sent to {name}: expired IN_PROGRESS "
                        f"claim(s) {task_ids} need resume/submit/release/pause action.",
                        dry_run=dry_run, task_id=STALE_CLAIM_TASK_ID)

    save_state(state, dry_run=dry_run)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--interval", type=int, default=5400, help="poll seconds")
    parser.add_argument("--once", action="store_true", help="single poll, then exit")
    parser.add_argument("--dry-run", action="store_true", help="print actions, write nothing")
    args = parser.parse_args()

    if args.once:
        poll_once(dry_run=args.dry_run)
        return 0
    # The long-running watcher owns its pidfile (TASK-098): shell-written $!
    # values drifted from reality and caused repeated liveness confusion.
    if not args.dry_run:
        pidfile = ROOT / ".locks" / "limit-watcher.pid"
        try:
            pidfile.parent.mkdir(exist_ok=True)
            pidfile.write_text(f"{os.getpid()}\n")
        except OSError as exc:
            print(f"warning: cannot write pidfile {pidfile}: {exc}", file=sys.stderr)
    print(f"RnS limit watcher started: interval={args.interval}s status={STATUS_FILE}")
    while True:
        poll_once(dry_run=args.dry_run)
        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())
