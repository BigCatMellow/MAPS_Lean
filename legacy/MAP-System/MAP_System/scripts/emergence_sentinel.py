#!/usr/bin/env python3
"""Deterministic E/I signal scanner and non-promoting candidate queue."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "events" / "events.jsonl"
QUEUE = ROOT / "emergence" / "candidates"
STATE = ROOT / "agents" / "emergence-sentinel-state.json"
ACTIONS = {"accepted", "merged", "parked", "dismissed"}

# INS-0050: a task that builds a monitoring/logging system (liveness,
# limit-watching, reconciliation) legitimately emits many events describing
# what it observes about OTHER agents/tasks under its own task_id forever
# after release. Those are operational log noise, not a signal that the
# task's own progress is repeatedly blocked or reworked. Found live
# 2026-07-27: TASK-083 showed 54 "blockers", all limit_watcher/limit-watcher
# entries about other agents (206/219 of all BLOCKED events repo-wide come
# from this one sender) -- a permanent false-positive outlier that had to be
# manually recognized and dismissed every scan cycle.
SYSTEM_SENDERS = {"limit_watcher", "limit-watcher", "liveness_reaper", "langgraph-runner", "reconcile"}


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_events(path: Path) -> list[dict]:
    result = []
    if not path.exists():
        return result
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict) and item.get("task_id"):
            result.append(item)
    return result


def detect(events: list[dict]) -> list[dict]:
    by_task: dict[str, Counter] = defaultdict(Counter)
    refs: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, event in enumerate(events, 1):
        if str(event.get("sender", "")) in SYSTEM_SENDERS:
            continue
        kind = str(event.get("type", "")).upper()
        task = event["task_id"]
        by_task[task][kind] += 1
        refs[(task, kind)].append(index)
    signals = []
    for task, counts in sorted(by_task.items()):
        if counts["CHANGES_REQUESTED"] >= 2:
            signals.append({
                "signal_type": "repeated_rework",
                "subject": task,
                "summary": f"{task} received {counts['CHANGES_REQUESTED']} changes-requested events; inspect for a reusable prevention lesson.",
                "evidence_refs": [f"MAP_System/events/events.jsonl:{n}" for n in refs[(task, "CHANGES_REQUESTED")]],
            })
        if counts["BLOCKED"] >= 2:
            signals.append({
                "signal_type": "repeated_blocker",
                "subject": task,
                "summary": f"{task} recorded {counts['BLOCKED']} blockers; inspect whether the blocking condition should become operational learning.",
                "evidence_refs": [f"MAP_System/events/events.jsonl:{n}" for n in refs[(task, "BLOCKED")]],
            })
    return signals


def dedup_key(signal: dict) -> str:
    raw = f"{signal['signal_type']}|{signal['subject']}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def existing(queue: Path) -> dict[str, dict]:
    found = {}
    for path in queue.glob("CAND-*.json"):
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
            found[item["dedup_key"]] = item
        except (OSError, KeyError, json.JSONDecodeError):
            continue
    return found


def write_state(state_path: Path, **changes) -> dict:
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        state = {"schema_version": 1}
    state.update(changes)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return state


def read_state(state_path: Path) -> dict:
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        return state if isinstance(state, dict) else {"schema_version": 1}
    except (OSError, json.JSONDecodeError):
        return {"schema_version": 1}


def scan(events_path: Path, queue: Path, state_path: Path) -> dict:
    started = time.monotonic()
    now = stamp()
    queue.mkdir(parents=True, exist_ok=True)
    current = read_state(state_path)
    if current.get("stop_requested"):
        state = write_state(state_path, status="stopped", last_run=now)
        return {"ok": False, "stopped": True, "created": [], "signals": 0, "state": state}
    write_state(state_path, status="scanning", last_run=now, last_error=None)
    try:
        signals = detect(load_events(events_path))
        known = existing(queue)
        created = []
        for signal in signals:
            key = dedup_key(signal)
            if key in known:
                continue
            candidate_id = f"CAND-{key.upper()}"
            record = {
                "candidate_id": candidate_id,
                "status": "new",
                "signal_type": signal["signal_type"],
                "subject": signal["subject"],
                "summary": signal["summary"],
                "evidence_refs": signal["evidence_refs"],
                "dedup_key": key,
                "detected_at": now,
                "curated_at": None,
                "curated_by": None,
                "resolution_reason": None,
                "resolution_ref": None,
            }
            (queue / f"{candidate_id}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
            known[key] = record
            created.append(candidate_id)
        total = list(existing(queue).values())
        runtime = round((time.monotonic() - started) * 1000, 2)
        state = write_state(
            state_path, status="idle", last_success=stamp(), last_error=None,
            candidates_new=sum(x.get("status") == "new" for x in total),
            candidates_total=len(total), runtime_ms=runtime,
        )
        return {"ok": True, "created": created, "signals": len(signals), "state": state}
    except Exception as exc:
        write_state(state_path, status="error", last_error=str(exc), runtime_ms=round((time.monotonic() - started) * 1000, 2))
        raise


def curate(path: Path, action: str, actor: str, reason: str, resolution_ref: str | None) -> dict:
    if action not in ACTIONS:
        raise ValueError(f"invalid action: {action}")
    item = json.loads(path.read_text(encoding="utf-8"))
    item.update({
        "status": action, "curated_at": stamp(), "curated_by": actor,
        "resolution_reason": reason, "resolution_ref": resolution_ref,
    })
    path.write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
    return item


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    scan_p = sub.add_parser("scan")
    scan_p.add_argument("--events", type=Path, default=EVENTS)
    scan_p.add_argument("--queue", type=Path, default=QUEUE)
    scan_p.add_argument("--state", type=Path, default=STATE)
    scan_p.add_argument("--pretty", action="store_true")
    list_p = sub.add_parser("list")
    list_p.add_argument("--queue", type=Path, default=QUEUE)
    list_p.add_argument("--pretty", action="store_true")
    curate_p = sub.add_parser("curate")
    curate_p.add_argument("candidate_id")
    curate_p.add_argument("--queue", type=Path, default=QUEUE)
    curate_p.add_argument("--action", required=True, choices=sorted(ACTIONS))
    curate_p.add_argument("--actor", required=True)
    curate_p.add_argument("--reason", required=True)
    curate_p.add_argument("--resolution-ref")
    curate_p.add_argument("--pretty", action="store_true")
    control_p = sub.add_parser("control")
    control_p.add_argument("action", choices=("stop", "resume"))
    control_p.add_argument("--state", type=Path, default=STATE)
    control_p.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "scan":
            result = scan(args.events, args.queue, args.state)
        elif args.command == "list":
            result = {"candidates": sorted(existing(args.queue).values(), key=lambda x: x["candidate_id"])}
        elif args.command == "curate":
            result = curate(args.queue / f"{args.candidate_id}.json", args.action, args.actor, args.reason, args.resolution_ref)
        else:
            stopped = args.action == "stop"
            result = write_state(args.state, stop_requested=stopped, status="stopped" if stopped else "idle", last_error=None)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
    print(json.dumps(result, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
