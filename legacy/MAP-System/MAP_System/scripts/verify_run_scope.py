#!/usr/bin/env python3
"""TASK-283: deterministic run-path scope contracts and retry budgets.

This module provides three checks, kept deliberately separate because they
have different strength and different points in the lifecycle:

1. ``validate_scope_contract`` -- a dispatch-preflight check. It can prove a
   readable/writable/forbidden contract is *self-consistent* (no path
   escapes the repo, writable and forbidden do not overlap) before model
   work starts. It cannot prove the worker will actually respect the
   contract.
2. ``verify_post_run_diff`` -- a post-run check. Given a manifest's declared
   scope and the paths a run actually changed, it can *detect* an
   out-of-scope or forbidden write after the fact. Detection is not
   prevention: nothing in this module stops a write from happening.
3. ``check_budget`` / ``write_escalation_artifact`` -- given a run
   manifest's declared ``runtime_limits`` and the actual attempt/
   tool-failure/runtime counts, detect exhaustion and record a durable
   escalation artifact instead of allowing an unbounded retry loop.

None of this is genuine harness containment. There is no OS-level sandbox,
filesystem permission boundary, or process-level enforcement anywhere in
this workspace that would stop a worker from writing outside its declared
scope or exceeding its declared budget -- see
``artifacts/tests/task283-scope-budget-delivery-note.md`` for the explicit
three-tier distinction (prompt-level guidance / post-run detection / genuine
harness containment) this task's acceptance criteria require, and
``REPAIR-0009``'s and this workspace's repeated caution: "Do not claim path
containment until the runtime enforces it."
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

RUNTIME_POLICY_PATH = ROOT / "workflow" / "runtime_policy.yaml"
DEFAULT_ESCALATION_DIR = ROOT / "artifacts" / "escalations"


def _normalize(raw: str) -> str:
    return raw.strip().replace("\\", "/").rstrip("/")


def _resolves_inside_repo(raw: str, repo: Path) -> bool:
    candidate = Path(raw)
    full = candidate if candidate.is_absolute() else (repo / raw)
    try:
        full.resolve().relative_to(repo.resolve())
    except ValueError:
        return False
    return True


def _overlaps(a: str, b: str) -> bool:
    """True if path ``a`` is ``b``, or a's a subpath/superpath of ``b``."""
    a, b = _normalize(a), _normalize(b)
    if a == "." or b == ".":
        return True
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def validate_scope_contract(
    *,
    readable: list[str] | None = None,
    writable: list[str] | None = None,
    forbidden: list[str] | None = None,
    repo: Path = REPO,
) -> list[str]:
    """Return a list of issues; empty means the contract is self-consistent.

    Checks only internal consistency of the declared contract -- it cannot
    verify a worker will honor it. Tasks/manifests with no scope contract at
    all are out of scope for this function; callers decide whether an
    absent contract is acceptable.
    """
    readable = readable or []
    writable = writable or []
    forbidden = forbidden or []
    issues: list[str] = []

    for label, paths in (("readable", readable), ("writable", writable), ("forbidden", forbidden)):
        for path in paths:
            if not path or not path.strip():
                issues.append(f"{label} path is empty")
            elif not _resolves_inside_repo(path, repo):
                issues.append(f"{label} path escapes the repository: {path!r}")

    for w in writable:
        for f in forbidden:
            if _overlaps(w, f):
                issues.append(f"writable path {w!r} overlaps forbidden path {f!r}")

    if writable and readable:
        for w in writable:
            if not any(_overlaps(w, r) for r in readable):
                issues.append(
                    f"writable path {w!r} is not covered by any declared readable path"
                )

    return issues


def verify_post_run_diff(
    *,
    writable: list[str],
    forbidden: list[str],
    changed_paths: list[str],
) -> dict[str, Any]:
    """Classify actually-changed paths against a manifest's declared scope.

    ``changed_paths`` is supplied by the caller (e.g. from ``git status
    --porcelain`` or a directory-snapshot diff) -- this function does no
    filesystem or git inspection itself, so it stays testable without a
    real repository and the caller stays in control of what "changed"
    means for their run.
    """
    out_of_scope: list[str] = []
    forbidden_writes: list[str] = []
    for path in changed_paths:
        normalized = _normalize(path)
        if any(_overlaps(normalized, f) for f in forbidden):
            forbidden_writes.append(path)
            continue
        if writable and not any(_overlaps(normalized, w) for w in writable):
            out_of_scope.append(path)
    return {
        "ok": not out_of_scope and not forbidden_writes,
        "out_of_scope_writes": sorted(out_of_scope),
        "forbidden_writes": sorted(forbidden_writes),
        "checked_paths": len(changed_paths),
    }


def check_budget(
    *,
    runtime_limits: dict[str, Any],
    actual_attempts: int | None = None,
    actual_tool_failures: int | None = None,
    actual_runtime_seconds: int | None = None,
) -> dict[str, Any] | None:
    """Return an escalation record if any declared budget is exceeded, else None.

    A limit that was never declared in ``runtime_limits`` is not enforced --
    this mirrors ``run_manifest.py``'s own convention of only recording the
    limits a caller explicitly supplied.
    """
    exceeded: list[dict[str, Any]] = []
    checks = (
        ("max_attempts", actual_attempts, "attempts"),
        ("max_tool_failures", actual_tool_failures, "tool failures"),
        ("runtime_seconds", actual_runtime_seconds, "runtime seconds"),
    )
    for limit_key, actual, label in checks:
        limit = runtime_limits.get(limit_key)
        if limit is None or actual is None:
            continue
        if actual >= limit:
            exceeded.append({
                "metric": limit_key, "label": label, "limit": limit, "actual": actual,
            })
    if not exceeded:
        return None
    return {
        "kind": "budget_exhaustion",
        "exceeded": exceeded,
        "runtime_limits": runtime_limits,
    }


def write_escalation_artifact(
    record: dict[str, Any],
    *,
    task_id: str,
    run_id: str | None = None,
    out_dir: Path = DEFAULT_ESCALATION_DIR,
) -> Path:
    """Persist a durable escalation artifact instead of allowing an unbounded retry loop.

    This function only writes the artifact -- it does not itself halt, pause,
    or claim any task. Acting on the escalation (pausing further attempts,
    notifying an operator) is the caller's responsibility, same as every
    other MAP escalation path (``events.jsonl`` ``BLOCKED``/``QUESTION``
    records, hcom ``--intent request``).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = f"-{run_id}" if run_id else ""
    path = out_dir / f"ESCALATION-{task_id}{suffix}-{stamp}.json"
    payload = {
        "task_id": task_id,
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        **record,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_scope_policy(path: Path = RUNTIME_POLICY_PATH) -> dict[str, Any]:
    """Read the ``scope_budget_contracts`` section of runtime_policy.yaml, if present."""
    import yaml

    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return {}
    section = data.get("scope_budget_contracts", {})
    return section if isinstance(section, dict) else {}


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    contract = sub.add_parser("check-contract")
    contract.add_argument("--readable", action="append", default=[])
    contract.add_argument("--writable", action="append", default=[])
    contract.add_argument("--forbidden", action="append", default=[])

    diff = sub.add_parser("check-diff")
    diff.add_argument("--writable", action="append", default=[])
    diff.add_argument("--forbidden", action="append", default=[])
    diff.add_argument("--changed", action="append", default=[])

    args = parser.parse_args(argv)
    if args.command == "check-contract":
        issues = validate_scope_contract(
            readable=args.readable, writable=args.writable, forbidden=args.forbidden,
        )
        print(json.dumps({"issues": issues, "valid": not issues}, indent=2))
        return 0 if not issues else 1
    if args.command == "check-diff":
        result = verify_post_run_diff(
            writable=args.writable, forbidden=args.forbidden, changed_paths=args.changed,
        )
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
