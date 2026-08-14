#!/usr/bin/env python3
"""Declare an agent's work-state (TASK-084 / IDEA-0007 declared-idle protocol).

    declare_standby.py <agent>          -> standby / awaiting_work (queue empty;
                                           RnS check-ins leave you alone)
    declare_standby.py <agent> --back   -> available (working again)
    declare_standby.py <agent> --terminal session_superseded
                                        -> inactive / session_superseded
    declare_standby.py <agent> --terminal disposable_session_ended
                                        -> inactive / disposable_session_ended
                                           (dead on purpose, TASK-186/IDEA-0009;
                                           RnS never probes, resumes, or nudges)
    declare_standby.py <agent> --resume-at 2026-08-03T07:05:00-04:00
                                        -> standby / scheduled; RnS (TASK-083)
                                           nudges this agent back to available
                                           once that time passes and its
                                           session is live, same machinery as
                                           an auto-detected rate-limit reset,
                                           but explicitly operator-requested
                                           rather than limit-triggered.

Writes SQLite FIRST (the agents table is the source of truth; status.json is
an exporter mirror -- see SYN-0001), then exports so all views agree.
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
EXPORTER = ROOT / "migration" / "export_to_files.py"
EVENT_LOG = ROOT / "events" / "events.jsonl"
TASK_ID = "TASK-083"
SENDER = "declare_standby"

try:
    from MAP_System.scripts.limit_watcher import parse_resume_after
except ModuleNotFoundError:  # direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from limit_watcher import parse_resume_after


def append_scheduled_event(agent: str, resume_after: str) -> None:
    event = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "type": "PROGRESS",
        "task_id": TASK_ID,
        "sender": SENDER,
        "summary": (
            f"{agent} placed in standby with an operator-scheduled resume at "
            f"{resume_after} (not a detected rate limit). RnS will nudge it "
            "back to available once that time passes and its session is live."
        ),
        "artifact_paths": [],
    }
    EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with EVENT_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")
    con = sqlite3.connect(DB)
    con.execute(
        "INSERT OR IGNORE INTO events (event_type, task_id, sender_id, summary, artifact_paths, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (event["type"], event["task_id"], None, event["summary"], json.dumps(event["artifact_paths"]),
         event["created_at"]),
    )
    con.commit()
    con.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("agent", help="agent id, e.g. claude-lab-rose")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--back", action="store_true",
                       help="return to available instead of declaring standby")
    group.add_argument("--terminal",
                       choices=("session_superseded", "disposable_session_ended"),
                       help="mark the session durably dead on purpose "
                            "(inactive/<value>; RnS suppresses probes and nudges, "
                            "TASK-186/IDEA-0009)")
    group.add_argument("--resume-at", metavar="ISO-8601",
                       help="schedule an operator-requested resume at this future "
                            "timestamp (standby/scheduled); RnS nudges this agent "
                            "back once it's due and the session is live, using the "
                            "same machinery as a detected rate-limit reset -- not a "
                            "generic reminder system, this only affects RnS's own "
                            "nudge behavior for this agent")
    args = parser.parse_args()

    resume_after = None
    if args.back:
        status, reason = "available", None
    elif args.terminal:
        status, reason = "inactive", args.terminal
    elif args.resume_at:
        parsed = parse_resume_after(args.resume_at)
        if parsed is None:
            print(f"error: --resume-at {args.resume_at!r} is not a parseable "
                  "ISO-8601 timestamp", file=sys.stderr)
            return 1
        if parsed <= datetime.now(timezone.utc).astimezone(parsed.tzinfo):
            print(f"error: --resume-at {args.resume_at!r} is not in the future",
                  file=sys.stderr)
            return 1
        status, reason = "standby", "scheduled"
        resume_after = parsed.isoformat(timespec="seconds")
    else:
        status, reason = "standby", "awaiting_work"

    con = sqlite3.connect(DB)
    row = con.execute("SELECT 1 FROM agents WHERE agent_id=?", (args.agent,)).fetchone()
    if row is None:
        print(f"error: unknown agent {args.agent!r} (not in SQLite agents table)",
              file=sys.stderr)
        return 1
    con.execute(
        "UPDATE agents SET status=?, reason=?, resume_after=?, "
        "updated_at=CURRENT_TIMESTAMP WHERE agent_id=?",
        (status, reason, resume_after, args.agent))
    con.commit()
    con.close()

    result = subprocess.run([sys.executable, str(EXPORTER)],
                            capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"warning: SQLite updated but export failed: {result.stderr.strip()}",
              file=sys.stderr)
        return 1

    if resume_after is not None:
        append_scheduled_event(args.agent, resume_after)

    print(f"{args.agent}: {status}" + (f" ({reason})" if reason else "") +
          (f" resume_after={resume_after}" if resume_after else "") +
          " -- SQLite updated, mirrors exported")
    return 0


if __name__ == "__main__":
    sys.exit(main())
