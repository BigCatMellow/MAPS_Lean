#!/usr/bin/env python3
"""TASK-285 offline evidence-linked workstream digest pilot."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
DEFAULT_DB = ROOT / "map.db"
DEFAULT_TASKS = ROOT / "tasks"
DEFAULT_GRAPH = ROOT / "workflow" / "task_graph.json"
DEFAULT_EVENTS = ROOT / "events" / "events.jsonl"
DEFAULT_DECISIONS = ROOT / "shared" / "decisions.md"
DEFAULT_REPORT = ROOT / "artifacts" / "experiments" / "task285-workstream-digest-pilot.md"

WORKSTREAM_ID = "map-task-lifecycle-integrity"
MIN_RELEASED_TASKS = 5
RELATED_TASK_IDS = ("TASK-143", "TASK-199", "TASK-266", "TASK-270", "TASK-273")
OPEN_RISK_TASK_ID = "TASK-274"

CLAIM_SPECS = (
    {
        "id": "decision-one-owner",
        "category": "decision",
        "statement": "One accountable owner is required for each active task.",
        "path": "MAP_System/shared/decisions.md",
        "anchor": "DEC-003: One Owner Per Active Task",
    },
    {
        "id": "decision-sqlite-claim-authority",
        "category": "decision",
        "statement": "SQLite is the canonical coordinator for atomic task claims.",
        "path": "MAP_System/shared/decisions.md",
        "anchor": "DEC-009: SQLite Is The Task Claiming Coordinator",
    },
    {
        "id": "failure-mirror-drift",
        "category": "repeated_failure",
        "statement": "Manual SQLite, task-file, and task-graph synchronization drift required a reconciliation gate.",
        "path": "MAP_System/tasks/TASK-143.json",
        "anchor": "manual SQLite/file sync drift",
    },
    {
        "id": "failure-duplicate-review-work",
        "category": "repeated_failure",
        "statement": "Independent reviewers duplicated full reviews before atomic review claiming existed.",
        "path": "MAP_System/tasks/TASK-199.json",
        "anchor": "duplicated review effort",
    },
    {
        "id": "failure-orphaned-task",
        "category": "repeated_failure",
        "statement": "An IN_PROGRESS task with no claimant or lease was structurally unreachable by sanctioned recovery paths.",
        "path": "MAP_System/tasks/TASK-266.json",
        "anchor": "structurally unreachable",
    },
    {
        "id": "failure-reviewer-false-negative",
        "category": "repeated_failure",
        "statement": "An unregistered reviewer was falsely told an open review was already claimed.",
        "path": "MAP_System/tasks/TASK-270.json",
        "anchor": "false negative",
    },
    {
        "id": "failure-stale-owner",
        "category": "repeated_failure",
        "statement": "Owner identity became permanent and unsanctioned to repair after agents disappeared.",
        "path": "MAP_System/tasks/TASK-273.json",
        "anchor": "permanent and unfixable",
    },
)

KEY_FILE_PATHS = (
    "MAP_System/db/claims.py",
    "MAP_System/scripts/map_task.py",
    "MAP_System/scripts/validate_task_mirrors.py",
    "MAP_System/notes/review-guide.md",
    "MAP_System/tests/test_recover_orphan.py",
    "MAP_System/tests/test_reassign_owner.py",
    "MAP_System/tests/test_review_claims.py",
    "MAP_System/tests/test_validate_task_mirrors.py",
)

FROZEN_REQUIRED_FACT_IDS = tuple(spec["id"] for spec in CLAIM_SPECS) + (
    "key-files",
    "risk-submission-authorship",
)


def digest(path: Path) -> str | None:
    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    if path.is_dir():
        manifest = []
        for child in sorted(path.rglob("*"), key=lambda item: item.relative_to(path).as_posix()):
            relative = child.relative_to(path).as_posix()
            if child.is_file():
                manifest.append(
                    {
                        "path": relative,
                        "type": "file",
                        "sha256": hashlib.sha256(child.read_bytes()).hexdigest(),
                    }
                )
            elif child.is_dir():
                manifest.append({"path": relative, "type": "directory"})
            elif child.is_symlink():
                manifest.append(
                    {
                        "path": relative,
                        "type": "symlink",
                        "target": child.readlink().as_posix(),
                    }
                )
        encoded = json.dumps(
            manifest, sort_keys=True, separators=(",", ":")
        ).encode()
        return hashlib.sha256(encoded).hexdigest()
    return None


def source_type(path: Path) -> str:
    if path.is_file():
        return "file"
    if path.is_dir():
        return "directory_manifest"
    if path.is_symlink():
        return "symlink"
    return "missing"


def resolve(raw: str, repo: Path) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    if raw.startswith("MAP_System/"):
        return repo / raw
    return repo / "MAP_System" / raw


def display(path: Path, repo: Path) -> str:
    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        return str(path)


def source_ref(
    raw: str,
    kind: str,
    repo: Path,
    *,
    anchor: str | None = None,
    expected_sha256: str | None = None,
) -> dict[str, Any]:
    path = resolve(raw, repo)
    classified_type = source_type(path)
    actual = digest(path)
    if actual is None:
        state = "missing"
    elif expected_sha256 and expected_sha256 != actual:
        state = "stale"
    elif (
        anchor
        and classified_type == "file"
        and anchor not in path.read_text(encoding="utf-8", errors="replace")
    ):
        state = "anchor_missing"
    elif anchor and classified_type != "file":
        state = "anchor_unsupported"
    else:
        state = "available"
    return {
        "kind": kind,
        "path": display(path, repo),
        "source_type": classified_type,
        "anchor": anchor,
        "state": state,
        "sha256": actual,
        "expected_sha256": expected_sha256,
    }


def sqlite_statuses(db_path: Path) -> dict[str, str]:
    uri = f"{db_path.resolve().as_uri()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        return {
            str(task_id): str(status)
            for task_id, status in connection.execute(
                "SELECT task_id, status FROM tasks ORDER BY task_id"
            )
        }


def graph_statuses(graph_path: Path) -> dict[str, str]:
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    return {
        str(row["task_id"]): str(row.get("status", ""))
        for row in graph.get("tasks", [])
        if isinstance(row, dict) and row.get("task_id")
    }


def load_tasks(tasks_dir: Path) -> dict[str, dict[str, Any]]:
    tasks = {}
    for path in sorted(tasks_dir.glob("TASK-*.json")):
        task = json.loads(path.read_text(encoding="utf-8"))
        tasks[str(task["task_id"])] = task
    return tasks


def lifecycle_evidence(
    task_id: str,
    tasks: dict[str, dict[str, Any]],
    db_states: dict[str, str],
    graph_states: dict[str, str],
) -> dict[str, Any]:
    statuses = {
        "task_json": tasks.get(task_id, {}).get("status"),
        "sqlite": db_states.get(task_id),
        "task_graph": graph_states.get(task_id),
    }
    missing = [source for source, status in statuses.items() if status is None]
    contradictory = len({status for status in statuses.values() if status is not None}) > 1
    return {
        "statuses": statuses,
        "missing_sources": missing,
        "contradictory": contradictory,
        "released": not missing
        and not contradictory
        and all(status == "RELEASED" for status in statuses.values()),
    }


def submission_refs(events_path: Path, task_id: str, repo: Path) -> list[dict[str, Any]]:
    refs = []
    if not events_path.is_file():
        return refs
    file_sha = digest(events_path)
    for line_number, line in enumerate(
        events_path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
    ):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("task_id") == task_id and event.get("type") == "SUBMISSION":
            refs.append(
                {
                    "kind": "submission",
                    "path": display(events_path, repo),
                    "anchor": f"jsonl_line:{line_number}",
                    "state": "available",
                    "sha256": file_sha,
                    "event_sha256": hashlib.sha256(line.encode()).hexdigest(),
                }
            )
    return refs


def review_refs(task_id: str, reviews_dir: Path, repo: Path) -> list[dict[str, Any]]:
    token = task_id.lower().replace("-", "")
    return [
        source_ref(display(path, repo), "review", repo)
        for path in sorted(reviews_dir.glob("*.md"))
        if token in path.name.lower().replace("-", "")
    ]


def evidence_issues(refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"kind": ref["state"], "path": ref["path"], "anchor": ref.get("anchor")}
        for ref in refs
        if ref["state"] != "available"
    ]


def _expected_for(raw: str, repo: Path, prior_manifest: dict[str, str]) -> str | None:
    """Look up a prior build's recorded hash for a source, by resolved display path."""
    return prior_manifest.get(display(resolve(raw, repo), repo))


def extract_manifest(digest_row: dict[str, Any]) -> dict[str, str]:
    """Flatten a digest's backlinks into {display_path: sha256}, for the next build's staleness check.

    Only entries with a real content hash are kept -- ``sha256`` is ``None``
    for missing/unsupported sources, and comparing against ``None`` would
    never detect a real change. Callers pass the result back into
    ``build_digest(prior_manifest=...)`` to turn a rebuild into a refresh
    that can actually see what changed since the prior build.
    """
    manifest: dict[str, str] = {}
    fact_rows = [
        *digest_row.get("decisions", []),
        *digest_row.get("repeated_failures", []),
        digest_row.get("key_files", {}),
        *digest_row.get("open_risks", []),
        *digest_row.get("withheld_claims", []),
    ]
    for row in fact_rows:
        for ref in row.get("backlinks", []):
            if ref.get("path") and ref.get("sha256"):
                manifest[ref["path"]] = ref["sha256"]
    for task in digest_row.get("tasks", []):
        for ref in task.get("backlinks", []):
            if ref.get("path") and ref.get("sha256"):
                manifest[ref["path"]] = ref["sha256"]
    return manifest


def build_digest(
    *,
    repo: Path = REPO,
    tasks_dir: Path = DEFAULT_TASKS,
    db_path: Path = DEFAULT_DB,
    graph_path: Path = DEFAULT_GRAPH,
    events_path: Path = DEFAULT_EVENTS,
    prior_manifest: dict[str, str] | None = None,
) -> dict[str, Any]:
    prior_manifest = prior_manifest or {}
    tasks = load_tasks(tasks_dir)
    db_states = sqlite_statuses(db_path)
    graph_states = graph_statuses(graph_path)
    task_rows = []
    issues = []

    for task_id in RELATED_TASK_IDS:
        lifecycle = lifecycle_evidence(task_id, tasks, db_states, graph_states)
        task = tasks.get(task_id, {})
        task_json_raw = display(tasks_dir / f"{task_id}.json", repo)
        task_ref = source_ref(
            task_json_raw, "released_task", repo,
            expected_sha256=_expected_for(task_json_raw, repo, prior_manifest),
        )
        submissions = submission_refs(events_path, task_id, repo)
        reviews = review_refs(
            task_id, repo / "MAP_System" / "artifacts" / "reviews", repo
        )
        primary = [
            source_ref(
                str(path), "primary", repo,
                expected_sha256=_expected_for(str(path), repo, prior_manifest),
            )
            for path in task.get("output_paths", [])
        ]
        refs = [task_ref, *submissions, *reviews, *primary]
        if not submissions:
            issues.append(
                {
                    "kind": "missing_submission_evidence",
                    "task_id": task_id,
                    "path": display(events_path, repo),
                }
            )
        if not reviews:
            issues.append({"kind": "missing_review_evidence", "task_id": task_id})
        issues.extend(
            {"task_id": task_id, **issue} for issue in evidence_issues(refs)
        )
        if not lifecycle["released"]:
            issues.append(
                {
                    "kind": "lifecycle_not_released",
                    "task_id": task_id,
                    "detail": lifecycle,
                }
            )
        task_rows.append(
            {
                "task_id": task_id,
                "title": task.get("title"),
                "lifecycle": lifecycle,
                "backlinks": refs,
            }
        )

    claims = []
    withheld_claims = []
    for spec in CLAIM_SPECS:
        ref = source_ref(
            spec["path"], spec["category"], repo, anchor=spec["anchor"],
            expected_sha256=_expected_for(spec["path"], repo, prior_manifest),
        )
        row = {
            "id": spec["id"],
            "category": spec["category"],
            "statement": spec["statement"],
            "backlinks": [ref],
        }
        if ref["state"] == "available":
            claims.append(row)
        else:
            withheld_claims.append(row)
            issues.extend(evidence_issues([ref]))

    key_refs = [
        source_ref(
            path, "key_file", repo,
            expected_sha256=_expected_for(path, repo, prior_manifest),
        )
        for path in KEY_FILE_PATHS
    ]
    issues.extend(evidence_issues(key_refs))
    open_lifecycle = lifecycle_evidence(
        OPEN_RISK_TASK_ID, tasks, db_states, graph_states
    )
    risk_raw = display(tasks_dir / f"{OPEN_RISK_TASK_ID}.json", repo)
    risk_ref = source_ref(
        risk_raw, "open_risk", repo,
        expected_sha256=_expected_for(risk_raw, repo, prior_manifest),
    )
    issues.extend(evidence_issues([risk_ref]))
    if open_lifecycle["missing_sources"] or open_lifecycle["contradictory"]:
        issues.append(
            {
                "kind": "open_risk_lifecycle_unverifiable",
                "task_id": OPEN_RISK_TASK_ID,
                "detail": open_lifecycle,
            }
        )
    open_risks = []
    if not open_lifecycle["released"]:
        open_risks.append(
            {
                "id": "risk-submission-authorship",
                "statement": "Durable submission authorship and author-keyed review separation remain unfinished.",
                "task_id": OPEN_RISK_TASK_ID,
                "status": open_lifecycle["statuses"],
                "backlinks": [risk_ref],
            }
        )

    released_count = sum(row["lifecycle"]["released"] for row in task_rows)
    eligible = released_count >= MIN_RELEASED_TASKS and not any(
        issue["kind"] == "lifecycle_not_released" for issue in issues
    )
    return {
        "schema_version": 1,
        "mode": "offline_disposable_projection",
        "canonical": False,
        "production_routing_enabled": False,
        "raw_evidence_required": True,
        "workstream_id": WORKSTREAM_ID,
        "eligibility": {
            "minimum_related_released_tasks": MIN_RELEASED_TASKS,
            "declared_related_tasks": list(RELATED_TASK_IDS),
            "verified_released_tasks": released_count,
            "eligible": eligible,
        },
        "tasks": task_rows,
        "decisions": [row for row in claims if row["category"] == "decision"],
        "repeated_failures": [
            row for row in claims if row["category"] == "repeated_failure"
        ],
        "key_files": {
            "id": "key-files",
            "statement": "Files repeatedly changed or relied on by this workstream.",
            "backlinks": key_refs,
        },
        "open_risks": open_risks,
        "withheld_claims": withheld_claims,
        "evidence_issues": issues,
    }


def detect_probe(probe: dict[str, Any]) -> str:
    if probe.get("actual_sha256") is None:
        return "missing"
    if probe.get("expected_sha256") != probe.get("actual_sha256"):
        return "stale"
    statuses = probe.get("statuses", {})
    if len(set(statuses.values())) > 1:
        return "contradictory"
    return "available"


def estimate_bytes(value: Any) -> int:
    return len(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


# Deterministic, dependency-free token estimate: maximal runs of word
# characters, or a single non-word/non-space symbol, count as one token
# each. This is a reproducible word/symbol-boundary tokenizer, not any
# specific model's BPE tokenizer -- named and documented as an estimate so
# the frozen metric does not overclaim what it measures (no tokenizer
# library, e.g. tiktoken, is available in this project's venv).
_TOKEN_RE = re.compile(r"\w+|[^\w\s]")


def estimate_tokens(text: str) -> int:
    return len(_TOKEN_RE.findall(text))


def estimate_value_tokens(value: Any) -> int:
    return estimate_tokens(json.dumps(value, sort_keys=True, separators=(",", ":")))


def evaluate(digest_row: dict[str, Any], repo: Path = REPO) -> dict[str, Any]:
    fact_rows = [
        *digest_row["decisions"],
        *digest_row["repeated_failures"],
        digest_row["key_files"],
        *digest_row["open_risks"],
    ]
    actual_ids = {row["id"] for row in fact_rows}
    expected_ids = set(FROZEN_REQUIRED_FACT_IDS)
    retained = expected_ids.intersection(actual_ids)
    traced = {
        row["id"]
        for row in fact_rows
        if row.get("backlinks")
        and all(ref.get("path") and ref.get("sha256") for ref in row["backlinks"])
    }
    probes = (
        {
            "id": "healthy",
            "expected": "available",
            "expected_sha256": "same",
            "actual_sha256": "same",
            "statuses": {"a": "RELEASED", "b": "RELEASED"},
        },
        {
            "id": "missing",
            "expected": "missing",
            "expected_sha256": "old",
            "actual_sha256": None,
        },
        {
            "id": "stale",
            "expected": "stale",
            "expected_sha256": "old",
            "actual_sha256": "new",
        },
        {
            "id": "contradictory",
            "expected": "contradictory",
            "expected_sha256": "same",
            "actual_sha256": "same",
            "statuses": {"task_json": "RELEASED", "sqlite": "APPROVED"},
        },
    )
    probe_rows = [
        {**probe, "actual": detect_probe(probe), "passed": detect_probe(probe) == probe["expected"]}
        for probe in probes
    ]
    unique_paths = {
        ref["path"]
        for task in digest_row["tasks"]
        for ref in task["backlinks"]
        if ref.get("sha256")
    }
    unique_paths.update(
        ref["path"]
        for row in fact_rows
        for ref in row.get("backlinks", [])
        if ref.get("sha256")
    )
    raw_files = [
        resolve(path, repo) for path in unique_paths if resolve(path, repo).is_file()
    ]
    raw_bytes = sum(path.stat().st_size for path in raw_files)
    raw_tokens = sum(
        estimate_tokens(path.read_text(encoding="utf-8", errors="replace"))
        for path in raw_files
    )
    compact = {
        key: digest_row[key]
        for key in (
            "workstream_id",
            "eligibility",
            "decisions",
            "repeated_failures",
            "key_files",
            "open_risks",
            "evidence_issues",
        )
    }
    compact_bytes = estimate_bytes(compact)
    compact_tokens = estimate_value_tokens(compact)
    frozen_input = {
        "required_fact_ids": FROZEN_REQUIRED_FACT_IDS,
        "probes": probes,
        "threshold": MIN_RELEASED_TASKS,
        "related_tasks": RELATED_TASK_IDS,
    }
    return {
        "frozen_evaluation_sha256": hashlib.sha256(
            json.dumps(frozen_input, sort_keys=True).encode()
        ).hexdigest(),
        "required_fact_retention": len(retained) / len(expected_ids),
        "source_traceability": len(traced.intersection(expected_ids)) / len(expected_ids),
        "stale_detection_accuracy": sum(row["passed"] for row in probe_rows)
        / len(probe_rows),
        "context_bytes_raw": raw_bytes,
        "context_bytes_digest": compact_bytes,
        "context_byte_reduction": 1 - compact_bytes / raw_bytes if raw_bytes else 0.0,
        "context_tokens_raw": raw_tokens,
        "context_tokens_digest": compact_tokens,
        "context_token_reduction": 1 - compact_tokens / raw_tokens if raw_tokens else 0.0,
        "retained_fact_ids": sorted(retained),
        "missing_fact_ids": sorted(expected_ids - retained),
        "probe_rows": probe_rows,
    }


def render(digest_row: dict[str, Any], metrics: dict[str, Any]) -> str:
    return f"""# TASK-285 Evidence-Linked Workstream Digest Pilot

- task_id: TASK-285
- generated_at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}
- workstream_id: {WORKSTREAM_ID}
- mode: offline_disposable_projection
- canonical: false
- production_routing_enabled: false
- frozen_evaluation_sha256: `{metrics['frozen_evaluation_sha256']}`

## Eligibility

The predeclared threshold is {MIN_RELEASED_TASKS} related tasks whose task JSON,
read-only SQLite status, and task-graph status all agree on `RELEASED`. This
single bounded workstream has {digest_row['eligibility']['verified_released_tasks']}
verified released tasks and eligibility is
`{str(digest_row['eligibility']['eligible']).lower()}`.

## Evidence Boundary

This digest is a retrieval projection, never task, decision, or project truth.
Every retained fact links to hashed raw evidence, and
`raw_evidence_required: true`. Missing, stale, anchor-missing, or contradictory
evidence is surfaced in `evidence_issues`; unsupported claims are withheld.

## Digest

```json
{json.dumps(digest_row, indent=2, sort_keys=True)}
```

## Frozen Evaluation

| Metric | Result |
|---|---:|
| required-fact retention | {metrics['required_fact_retention']:.2%} |
| source traceability | {metrics['source_traceability']:.2%} |
| stale/missing/contradiction detection | {metrics['stale_detection_accuracy']:.2%} |
| raw evidence tokens (estimate) | {metrics['context_tokens_raw']} |
| digest tokens (estimate) | {metrics['context_tokens_digest']} |
| context-token reduction | {metrics['context_token_reduction']:.2%} |
| raw evidence bytes | {metrics['context_bytes_raw']} |
| digest bytes | {metrics['context_bytes_digest']} |
| context-byte reduction | {metrics['context_byte_reduction']:.2%} |

The frozen evaluation fixes required fact IDs, lifecycle threshold, related
task IDs, and four evidence-health probes. Token counts are a deterministic
word/symbol-boundary estimate (`estimate_tokens`), not a specific model's
BPE tokenizer -- no tokenizer library is available in this project's venv,
and the metric name/report say "estimate" rather than overclaiming an exact
count. Byte counts are retained as an additional diagnostic. Raw evidence
bytes/tokens remain a point-in-time measurement because source files
continue to evolve.

## Refresh, Invalidation, Review, And Rollback

- Refresh by calling `build_digest(prior_manifest=extract_manifest(prior_digest))`
  (or the CLI's `--prior-report`) so a changed backlink hash is compared
  against the prior build and surfaced as `state: stale` in `evidence_issues`,
  withholding the affected claim rather than silently reporting it available.
  A plain rebuild with no prior manifest cannot detect staleness by itself --
  it only proves the *current* content is internally consistent.
- Refresh when any backlink hash or lifecycle status changes, a related task is
  released, or new submission/review/decision evidence appears.
- Invalidate when fewer than {MIN_RELEASED_TASKS} related tasks remain
  three-way `RELEASED`, any lifecycle source contradicts another, a required
  backlink is missing/stale, or a claim anchor disappears.
- Require independent review of claims, links, evidence-health findings, and
  frozen metrics before any production proposal.
- Roll back by deleting or rebuilding this disposable report. No task state,
  decision, source evidence, startup context, runner route, or Command Center
  behavior depends on it.

## Decision

Retain as an offline experiment. Do not enable production routing or substitute
this digest for opening canonical evidence.
"""


def load_prior_digest(report_path: Path) -> dict[str, Any] | None:
    """Extract the embedded digest JSON block from a prior rendered report."""
    if not report_path.is_file():
        return None
    text = report_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"## Digest\n\n```json\n(.*?)\n```", text, re.DOTALL)
    if not match:
        return None
    return json.loads(match.group(1))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--prior-report", type=Path, default=None,
        help="Path to a previously rendered report; its digest becomes the "
             "staleness baseline for this build (refresh mode).",
    )
    args = parser.parse_args()
    prior_manifest = {}
    if args.prior_report is not None:
        prior_digest = load_prior_digest(args.prior_report)
        if prior_digest is not None:
            prior_manifest = extract_manifest(prior_digest)
    digest_row = build_digest(prior_manifest=prior_manifest)
    metrics = evaluate(digest_row)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render(digest_row, metrics), encoding="utf-8")
    print(json.dumps(metrics, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
