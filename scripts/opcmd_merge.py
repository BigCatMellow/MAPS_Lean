#!/usr/bin/env python3
"""Mechanical pre-merge operator-authorization gate for the OPCMD merge seat.

Design: work/notes/2026-09-04-merge-auth-mechanical-backstop-design.md (§3.1, §7).

A merge-runner must not invoke ``gh pr merge <N>`` unless it can point to a
concrete, external, operator-authored hcom message that authorizes merging that
specific PR (or explicitly designates the caller as the batch merge seat). This
wrapper resolves that authorization, checks it fail-closed, appends a ledger
entry, and only then runs the merge.

Ships DORMANT: nothing in the repo calls it. Opt-in for the ``gule`` / OPCMD seat.

Usage:
    python scripts/opcmd_merge.py --pr <N> --authz <hcom_message_id> \\
        [--dry-run] [--caller <name>] [--merge-arg ARG]...

Exit codes:
    0  gate passed (merge run, or --dry-run printed the plan)
    2  gate refused (no merge command printed / run)
    3  usage / environment error
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys

# Operator-authority identities. Seeded from the same source hcom's own
# "Authority: Prioritize @bigboss" uses. A coordinator / agent seat is never
# here -- coordinator marks are structurally excluded from authorizing a merge.
OPERATOR_IDENTITIES = {"bigboss"}

# Max age of a *batch designation* authz message (§3.1 step 3b staleness bound).
BATCH_DESIGNATION_MAX_AGE_HOURS = 12

# Phrases that designate the caller as the batch merge seat (step 3b).
_BATCH_DESIGNATION_PATTERNS = (
    r"merge the queue",
    r"you are the merge seat",
    r"you're the merge seat",
    r"designat\w* .{0,20}merge seat",
    r"merge seat for the (?:batch|queue)",
)

# HOLD / STOP tokens scanned for in post-authz messages (§3.1 step 4).
_HOLD_PATTERNS = (
    r"\bHOLD\b",
    r"\bSTOP\b",
    r"do\s*n['o]?t\s+merge",
    r"don't\s+merge",
    r"\bhold\s+the\s+merge",
    r"\babort\b",
)

# Tokens that void the *authz message itself* (§3.1 step 3b). Tighter than
# _HOLD_PATTERNS: a bare "do not merge" needs a PR target to matter and is
# handled by _dont_merge_pr_re, so it is NOT here -- otherwise "merge #40 now,
# do not merge #42" could not authorize #40.
_AUTHZ_VOIDING_PATTERNS = (
    r"\bHOLD\b",
    r"\bSTOP\b",
    r"\babort\b",
    r"\bhold\s+the\s+merge\b",
)

LEDGER_PATH = os.path.join("work", "coordination", "merge-ledger.jsonl")


class GateError(Exception):
    """Fail-closed gate refusal. Message is printed; exit code 2."""


class EnvError(Exception):
    """Environment / usage problem. Exit code 3."""


def _run(cmd):
    """Run a subprocess, return (returncode, stdout, stderr). Overridable in tests."""
    proc = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    return proc.returncode, proc.stdout, proc.stderr


# Indirection point for tests: monkeypatch opcmd_merge.run_command.
run_command = _run


def _hcom_events_json(sql):
    """Return a list of parsed event dicts for ``hcom events --sql <sql> --type message``."""
    rc, out, err = run_command(
        ["hcom", "events", "--sql", sql, "--type", "message", "--all"]
    )
    if rc != 0:
        raise EnvError(f"hcom events failed (rc={rc}): {err.strip() or out.strip()}")
    events = []
    for line in out.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def _assert_hcom_live(authz_id):
    """O1: positive liveness assertion for step 4. ``hcom events --sql "id > N"``
    returning empty is only trustworthy if hcom is actually readable and pointed
    at the right store. resolve_authz already proved a read works this run; here
    we additionally confirm the newest message event has ``id >= authz_id`` -- if
    the whole stream looks older than the authz message we quoted, the query is
    talking to the wrong db and a post-authz HOLD could be silently invisible."""
    rc, out, err = run_command(
        ["hcom", "events", "--type", "message", "--all", "--last", "1"]
    )
    if rc != 0:
        raise EnvError(f"hcom liveness check failed (rc={rc}): {err.strip()}")
    newest = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                newest = json.loads(line)
            except json.JSONDecodeError:
                pass
    if newest is None:
        raise EnvError(
            "hcom liveness check returned no message events; refusing (cannot "
            "verify absence of a post-authz HOLD)"
        )
    try:
        newest_id = int(newest.get("id"))
    except (TypeError, ValueError):
        return
    if newest_id < int(authz_id):
        raise EnvError(
            f"hcom's newest message id ({newest_id}) is older than the authz "
            f"message ({authz_id}); the HOLD scan is querying the wrong store"
        )


def _parse_ts(raw):
    """Parse an hcom event timestamp into an aware UTC datetime."""
    if raw is None:
        return None
    txt = str(raw).strip().replace("Z", "+00:00")
    try:
        dt = _dt.datetime.fromisoformat(txt)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_dt.timezone.utc)
    return dt.astimezone(_dt.timezone.utc)


def resolve_authz(authz_id):
    """Step 1: resolve the authz message. Raise GateError if not found."""
    events = _hcom_events_json(f"id={int(authz_id)}")
    for ev in events:
        if str(ev.get("id")) == str(authz_id) and ev.get("type") == "message":
            data = ev.get("data") or {}
            return {
                "id": ev.get("id"),
                "from": data.get("from"),
                "text": data.get("text") or "",
                "ts": ev.get("ts"),
            }
    raise GateError(
        f"authz message id={authz_id} not found as a message event (hcom events --sql)"
    )


def check_sender(msg):
    """Step 2: sender must be an operator-authority identity."""
    sender = (msg.get("from") or "").strip()
    if sender not in OPERATOR_IDENTITIES:
        raise GateError(
            f"authz sender {sender!r} is not an operator identity "
            f"(allowed: {sorted(OPERATOR_IDENTITIES)}). Coordinator/agent marks "
            f"cannot authorize a merge."
        )


def _names_pr(text, pr):
    """True if text references PR <pr> in a merge-intent context."""
    if re.search(rf"#\s*{pr}\b", text):
        return True
    # Bare number, but only within 40 chars of a merge verb, to avoid matching
    # unrelated digits. O2: for a low <pr> (single/double digit) this window is
    # loose in the fail-open direction; real PR numbers are 3+ digits (~#287) so
    # `\b287\b` is specific. A prohibiting "don't merge #<N>" is caught earlier by
    # check_authz_not_prohibiting regardless of how <pr> matched here.
    if re.search(
        rf"\bmerg\w*\b[^.\n]{{0,40}}\b{pr}\b|\b{pr}\b[^.\n]{{0,40}}\bmerg\w*\b",
        text,
        re.IGNORECASE,
    ):
        return True
    return False


def _is_batch_designation(text):
    return any(re.search(p, text, re.IGNORECASE) for p in _BATCH_DESIGNATION_PATTERNS)


def check_scope(msg, pr):
    """Step 3: authz text must name PR <pr>, or designate a fresh batch seat."""
    text = msg.get("text") or ""
    if _names_pr(text, pr):
        return "named-pr"
    if _is_batch_designation(text):
        ts = _parse_ts(msg.get("ts"))
        if ts is None:
            raise GateError(
                "batch-designation authz has an unparseable timestamp; refusing "
                "(cannot verify the 12h staleness bound)"
            )
        age = _dt.datetime.now(_dt.timezone.utc) - ts
        if age > _dt.timedelta(hours=BATCH_DESIGNATION_MAX_AGE_HOURS):
            raise GateError(
                f"batch-designation authz is stale ({age} old, bound is "
                f"{BATCH_DESIGNATION_MAX_AGE_HOURS}h)"
            )
        return "batch-designation"
    raise GateError(
        f"authz text does not name #{pr} in a merge context and is not a batch "
        f"merge-seat designation. Text: {text!r}"
    )


def _dont_merge_pr_re(pr):
    return re.compile(rf"do\w*\s*n[o']?t\s+merge\s+#?\s*{pr}\b", re.IGNORECASE)


def check_authz_not_prohibiting(msg, pr):
    """Between steps 3 and 4: the authz message itself must not prohibit merging
    this PR. `_names_pr` only checks that ``#<N>`` is *present*, not that it is in
    an authorizing context -- so an authz that says "don't merge #N" (alone, or
    alongside "merge #M") would otherwise pass. Fail closed on any HOLD/STOP token
    or an explicit "don't merge #<N>" in the authz text."""
    text = msg.get("text") or ""
    if _dont_merge_pr_re(pr).search(text):
        raise GateError(
            f"authz message (id={msg.get('id')}) explicitly says not to merge "
            f"#{pr}: {text!r}"
        )
    for pat in _AUTHZ_VOIDING_PATTERNS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            raise GateError(
                f"authz message (id={msg.get('id')}) contains a HOLD/STOP token "
                f"({m.group(0)!r}); refusing to treat it as a merge authorization: "
                f"{text!r}"
            )


def check_no_hold(authz_id, pr):
    """Step 4: refuse if any operator posted a HOLD/STOP after the authz message."""
    events = _hcom_events_json(f"id > {int(authz_id)}")
    _assert_hcom_live(authz_id)
    for ev in events:
        if ev.get("type") != "message":
            continue
        data = ev.get("data") or {}
        sender = (data.get("from") or "").strip()
        if sender not in OPERATOR_IDENTITIES:
            continue
        text = data.get("text") or ""
        if any(re.search(p, text, re.IGNORECASE) for p in _HOLD_PATTERNS):
            raise GateError(
                f"post-authz HOLD/STOP from operator {sender!r} "
                f"(msg id={ev.get('id')}): {text!r}"
            )
        if re.search(rf"do\w*\s*n[o']?t\s+merge\s+#?\s*{pr}\b", text, re.IGNORECASE):
            raise GateError(
                f"post-authz 'don't merge #{pr}' from operator {sender!r} "
                f"(msg id={ev.get('id')}): {text!r}"
            )


def _head_sha(pr):
    rc, out, err = run_command(
        ["gh", "pr", "view", str(pr), "--json", "headRefOid", "-q", ".headRefOid"]
    )
    if rc != 0:
        return None
    return out.strip() or None


def append_ledger(entry, ledger_path=LEDGER_PATH):
    """Step 5: append one JSON line to the append-only merge ledger."""
    os.makedirs(os.path.dirname(ledger_path), exist_ok=True)
    with open(ledger_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")


def _excerpt(text, limit=200):
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def build_merge_cmd(pr, merge_args):
    cmd = ["gh", "pr", "merge", str(pr), "--squash"]
    cmd.extend(merge_args or [])
    return cmd


def gate(pr, authz_id, caller, merge_args, dry_run, ledger_path=LEDGER_PATH):
    """Run steps 1-6. Return the ledger entry dict. Raise GateError to refuse."""
    msg = resolve_authz(authz_id)              # 1
    check_sender(msg)                          # 2
    scope = check_scope(msg, pr)               # 3
    check_authz_not_prohibiting(msg, pr)       # 3b: authz must not itself say "don't merge #N"
    check_no_hold(authz_id, pr)                # 4

    entry = {
        "ts": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "pr": int(pr),
        "authz_id": msg["id"],
        "authz_from": msg["from"],
        "authz_excerpt": _excerpt(msg["text"]),
        "scope": scope,
        "caller": caller,
        "head_sha": _head_sha(pr),
        "dry_run": bool(dry_run),
    }

    merge_cmd = build_merge_cmd(pr, merge_args)

    print("GATE PASSED")
    print(f"  authz_id : {msg['id']}")
    print(f"  authz_from: {msg['from']}")
    print(f"  scope    : {scope}")
    print(f'  authz quote: "{_excerpt(msg["text"])}"')
    print(f"  merge cmd : {' '.join(merge_cmd)}")

    if dry_run:
        entry["merged"] = False
        print(json.dumps(entry, sort_keys=True))
        print("--dry-run: stopping before merge.")
        return entry

    append_ledger(entry, ledger_path)          # 5
    print(json.dumps(entry, sort_keys=True))

    rc, out, err = run_command(merge_cmd)       # 6
    sys.stdout.write(out)
    sys.stderr.write(err)
    if rc != 0:
        raise EnvError(f"gh pr merge failed (rc={rc})")
    entry["merged"] = True
    return entry


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="opcmd_merge.py",
        description="Mechanical pre-merge operator-authorization gate.",
    )
    parser.add_argument("--pr", type=int, required=True, help="PR number to merge")
    parser.add_argument(
        "--authz",
        required=True,
        help="hcom message id of the operator authorization",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="run the gate, print the plan, do NOT merge or write the ledger",
    )
    parser.add_argument(
        "--caller",
        default=os.environ.get("HCOM_NAME") or os.environ.get("USER") or "unknown",
        help="identity of the merge-runner seat (for the ledger)",
    )
    parser.add_argument(
        "--merge-arg",
        action="append",
        default=[],
        dest="merge_args",
        help="extra arg passed through to `gh pr merge` (repeatable)",
    )
    args = parser.parse_args(argv)

    try:
        gate(
            pr=args.pr,
            authz_id=args.authz,
            caller=args.caller,
            merge_args=args.merge_args,
            dry_run=args.dry_run,
        )
    except GateError as exc:
        print(f"MERGE REFUSED: {exc}", file=sys.stderr)
        return 2
    except EnvError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
