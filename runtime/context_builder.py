from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from runtime.state import TaskStore
from runtime.operational_learning import OperationalLearningError, project_applicable_lessons
from runtime.policy.memory_trust_gate import (
    MemoryAdmission,
    admit_memory_evidence,
)
from runtime.skills.capability_policy import capabilities_within_envelope
from runtime.skills.catalog import SkillCatalog, SkillCatalogError, load_catalog_skill
from runtime.skills.format import SkillParseError
from runtime.skills.lifecycle import SkillLifecycleState
from runtime.trust import (
    MemoryTrustClass,
    TrustClassError,
    operational_learning_trust_class,
    skill_lifecycle_trust_class,
)


def _skill_trust_class(
    lifecycle_state: SkillLifecycleState | None,
) -> MemoryTrustClass:
    """Project a Skill's composed lifecycle state onto `MemoryTrustClass`.

    `None` (no durable subject row -- discovered but not yet gate-assessed)
    maps to `OBSERVATION`, exactly as the former `SkillTrustState.UNASSESSED`
    did. Any real `SkillLifecycleState` delegates to the single canonical
    projection in `runtime.trust`. `TrustClassError` from a malformed value
    is left to propagate to the caller's guard.
    """

    if lifecycle_state is None:
        return MemoryTrustClass.OBSERVATION
    return skill_lifecycle_trust_class(lifecycle_state)

_PATH_SUFFIXES = {
    ".cfg",
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".py",
    ".sh",
    ".sql",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}


def _looks_like_url(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme and parsed.netloc)


def _looks_like_path(value: str) -> bool:
    if value.startswith(("./", "../", "/")) or "/" in value or "\\" in value:
        return True
    return Path(value).suffix.lower() in _PATH_SUFFIXES


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _describe_reference(root: Path, value: str, role: str) -> dict[str, Any]:
    value = value.strip()
    if _looks_like_url(value):
        return {
            "role": role,
            "value": value,
            "kind": "reference",
            "status": "external_reference",
        }

    raw = Path(value)
    candidate = raw if raw.is_absolute() else root / raw
    resolved = candidate.resolve(strict=False)
    try:
        relative = resolved.relative_to(root)
    except ValueError:
        if _looks_like_path(value) or candidate.exists():
            return {
                "role": role,
                "value": value,
                "kind": "path",
                "status": "outside_repo",
            }
        return {
            "role": role,
            "value": value,
            "kind": "reference",
            "status": "descriptive_reference",
        }

    repo_path = relative.as_posix() or "."
    if resolved.is_file():
        return {
            "role": role,
            "value": value,
            "kind": "file",
            "status": "available",
            "path": repo_path,
            "sha256": _sha256(resolved),
            "bytes": resolved.stat().st_size,
        }
    if resolved.is_dir():
        return {
            "role": role,
            "value": value,
            "kind": "path",
            "status": "directory_not_expanded",
            "path": repo_path,
        }
    if _looks_like_path(value):
        return {
            "role": role,
            "value": value,
            "kind": "path",
            "status": "missing",
            "path": repo_path,
        }
    return {
        "role": role,
        "value": value,
        "kind": "reference",
        "status": "descriptive_reference",
    }


_BUDGET_MUST_LOAD = "MUST_LOAD"
_BUDGET_SHOULD_LOAD = "SHOULD_LOAD"
_BUDGET_ON_DEMAND = "ON_DEMAND"

# Per-producer default for the unknown/malformed trust-class case, settled in
# §2e of `work/notes/2026-08-25-memory-trust-enforcement-gate-design.md` by
# whether that producer's withheld form carries content. Withheld lessons are
# `{lesson_id, reason}` only (`runtime/operational_learning.py:410`) -- a
# reference, no attack surface -- so they WITHHOLD, matching #148's stated
# fail-closed rule. Skill entries emit `name`/`description` text inline, so a
# withheld Skill entry in that shape *is* instruction-bearing text in the
# plan; the unknown case there DENYs instead. Neither is ever LOAD.
_UNKNOWN_LESSON_ADMISSION = MemoryAdmission.WITHHOLD
_UNKNOWN_SKILL_ADMISSION = MemoryAdmission.DENY


class _AdmissionTally:
    """Counts of what the trust gate decided, surfaced under `coverage`."""

    def __init__(self) -> None:
        self.admitted = 0
        self.withheld = 0
        self.denied = 0
        self.reasons: dict[str, int] = {}

    def record(self, admission: MemoryAdmission, code: str) -> None:
        if admission is MemoryAdmission.LOAD:
            self.admitted += 1
        elif admission is MemoryAdmission.WITHHOLD:
            self.withheld += 1
        else:
            self.denied += 1
        self.reasons[code] = self.reasons.get(code, 0) + 1

    def merge(self, other: "_AdmissionTally") -> None:
        self.admitted += other.admitted
        self.withheld += other.withheld
        self.denied += other.denied
        for code, count in other.reasons.items():
            self.reasons[code] = self.reasons.get(code, 0) + count


def _lesson_guidance(
    store: TaskStore, task: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], _AdmissionTally]:
    """Attributed GUIDANCE_ONLY evidence from operator-promoted ACTIVE lessons.

    Injection-0/1 (work/notes/2026-08-17-operational-learning-authority-design.md
    section 5): reuses `project_applicable_lessons()`'s existing shape and
    `GUIDANCE_ONLY` label verbatim; never merged into instructions/boundaries.
    Fails closed (empty guidance) rather than breaking the rest of the plan
    if lesson storage or projection is unavailable/invalid.

    Trust gate (roadmap 6.22): bucket membership and `budget_class` are now
    *outputs of* `admit_memory_evidence()` and of nothing else, rather than
    being assigned by the caller in parallel with the trust class. A withheld
    lesson feeds the same gate and can only be demoted further, never
    promoted to the default load set.
    """
    tally = _AdmissionTally()
    try:
        lessons = store.list_active_operational_lessons()
    except Exception:
        return [], [], tally
    context = {
        "project_id": task["project_id"],
        "task_type": task["task_type"],
        "risk": task["risk"],
        "paths": list(task["output_paths"]),
    }
    at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    try:
        projection = project_applicable_lessons(lessons, context, at=at)
    except OperationalLearningError:
        return [], [], tally
    try:
        projected = [
            dict(
                item,
                trust_class=operational_learning_trust_class("ACTIVE").value,
            )
            for item in projection["projected"]
        ]
        already_withheld = [
            _withheld_lesson_with_trust_class(item)
            for item in projection["withheld"]
        ]
    except (TrustClassError, TypeError, KeyError):
        return [], [], tally

    guidance: list[dict[str, Any]] = []
    withheld: list[dict[str, Any]] = []
    for item in projected:
        _route_lesson(item, guidance, withheld, tally, floor_withheld=False)
    for item in already_withheld:
        _route_lesson(item, guidance, withheld, tally, floor_withheld=True)
    return guidance, withheld, tally


def _route_lesson(
    item: dict[str, Any],
    guidance: list[dict[str, Any]],
    withheld: list[dict[str, Any]],
    tally: _AdmissionTally,
    *,
    floor_withheld: bool,
) -> None:
    """Route one lesson by the gate's decision; never promote a withheld item."""

    decision = admit_memory_evidence(
        item.get("trust_class"),
        stale=bool(item.get("stale_trust_metadata", False)),
        unknown_admission=_UNKNOWN_LESSON_ADMISSION,
    )
    admission = decision.admission
    code = decision.code
    if floor_withheld and admission is MemoryAdmission.LOAD:
        admission = MemoryAdmission.WITHHOLD
        code = _WITHHELD_UPSTREAM_CODE
    tally.record(admission, code)
    if admission is MemoryAdmission.DENY:
        return
    if admission is MemoryAdmission.LOAD:
        guidance.append(dict(item, budget_class=_BUDGET_SHOULD_LOAD))
        return
    payload = dict(item, budget_class=_BUDGET_ON_DEMAND)
    payload.setdefault("withheld_reason", code)
    withheld.append(payload)


_WITHHELD_UPSTREAM_CODE = "WITHHELD_UPSTREAM"


def _withheld_lesson_with_trust_class(item: dict[str, Any]) -> dict[str, Any]:
    reason = str(item["reason"])
    trust_class = {
        "CANDIDATE_NOT_PROMOTED": MemoryTrustClass.CANDIDATE_LESSON,
        "RETIRED": MemoryTrustClass.RETIRED,
        "SUPERSEDED": MemoryTrustClass.SUPERSEDED,
    }.get(reason, operational_learning_trust_class("ACTIVE"))
    payload = dict(item, trust_class=trust_class.value)
    if reason in {"EXPIRED", "REVIEW_DUE"}:
        payload["stale_trust_metadata"] = True
    return payload


_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
_MIN_TOKEN_LEN = 3


def _text_tokens(text: str) -> set[str]:
    return {
        word
        for word in _TOKEN_PATTERN.findall(text.lower())
        if len(word) >= _MIN_TOKEN_LEN
    }


def _path_segment_tokens(path: str) -> set[str]:
    tokens: set[str] = set()
    for segment in Path(path).parts:
        if segment in ("/", ".", ".."):
            continue
        tokens |= _text_tokens(Path(segment).stem)
    return tokens


def _skill_task_signal_tokens(task: dict[str, Any]) -> set[str]:
    tokens: set[str] = set()
    task_type = task.get("task_type")
    if isinstance(task_type, str) and task_type.strip():
        tokens |= _text_tokens(task_type)
    project_id = task.get("project_id")
    if isinstance(project_id, str) and project_id.strip():
        tokens |= _text_tokens(project_id)
    for path in task.get("output_paths") or []:
        if isinstance(path, str) and path.strip():
            tokens |= _path_segment_tokens(path)
    return tokens


def _select_skills(
    skill_catalog: SkillCatalog | None,
    task: dict[str, Any],
    store: TaskStore | None = None,
) -> tuple[list[dict[str, Any]], _AdmissionTally]:
    """Attributed, provenance-labeled Skill selection evidence.

    Fails closed: an absent/empty catalog, or any error while deriving task
    signals, yields no skills rather than breaking the rest of the plan.
    Matching uses only the metadata the v1 Skill format actually exposes
    (name/description text) against task signal tokens (task_type, project_id,
    output-path segments); an unmatched Skill is simply omitted, satisfying
    the S6 exit gate that unrelated Skills demonstrably stay out of context. A
    matched Skill's `lifecycle_state` is always its real composed provenance
    value (or `None` when no durable subject row exists) -- selection never
    implies vetting that hasn't happened.

    Progressive body loading (roadmap 6.9 / S6 slice 1): for a matched Skill
    whose trust-gate decision is `LOAD` -- and only then -- this calls the
    existing `load_catalog_skill(entry, store)` and attaches the
    hash-verified `SKILL.md` body (`item["body"]` + `item["body_sha256"]`).
    This advances 6.9 from the "startup" level (name/description metadata) to
    "activation" (full SKILL.md) for exactly the Skills already trusted to
    load. `WITHHOLD`/`ON_DEMAND` and `DENY` Skills get no body, unchanged. No
    new retrieval: the body comes only from an entry already selected here.
    `scripts`/`references`/`examples` content (the "execution" level) is still
    not loaded. If body activation raises (`SkillCatalogError` -- e.g. a
    QUARANTINED state slipping past the gate -- or `SkillParseError`/
    `SkillChangedError` on a post-discovery content change), the item is kept
    metadata-only with `item["body_withheld_reason"]` and the plan is not
    broken. With `store=None` (e.g. `maps context`, which passes no catalog)
    no body is ever loaded.

    Trust gate (roadmap 6.22): a matched Skill's `budget_class` is now the
    output of `admit_memory_evidence()` rather than a hardcoded
    `SHOULD_LOAD`. A `None` lifecycle state maps to `OBSERVATION`, which #148's
    class/action table says must not influence loaded instructions, so a
    matched-but-unassessed Skill is emitted as `ON_DEMAND` metadata with a
    `withheld_reason` and is no longer part of the default load set. An
    unmappable lifecycle state is a `DENY`: the entry is dropped and counted,
    rather than silently skipped as before. That branch is defense in depth
    -- `lifecycle_state` is a real `SkillLifecycleState` or `None`, both of
    which project cleanly -- kept so a future malformed value fails closed.
    """

    tally = _AdmissionTally()
    if skill_catalog is None or not skill_catalog.entries:
        return [], tally
    try:
        signals = _skill_task_signal_tokens(task)
    except Exception:
        return [], tally
    if not signals:
        return [], tally

    selected: list[dict[str, Any]] = []
    for entry in skill_catalog.entries:
        descriptor = entry.descriptor
        skill_tokens = _text_tokens(descriptor.name) | _text_tokens(descriptor.description)
        matched = sorted(signals & skill_tokens)
        if not matched:
            continue
        # SEC4 capability-manifest slice 2: a matched Skill whose `capabilities`
        # manifest declares a capability the running task's task_policy envelope
        # does not permit is DENY'd from the plan -- before the trust gate, so
        # an out-of-envelope Skill is never body-loaded. task["policy"] is read
        # as the task's already-decided envelope (attached by store.get_task);
        # the manifest is never written back. Seam is _select_skills, not
        # load_catalog_skill (which has no task context).
        within, _offending = capabilities_within_envelope(
            descriptor.declared_capabilities, task.get("policy")
        )
        if not within:
            tally.record(
                MemoryAdmission.DENY, "SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE"
            )
            continue
        lifecycle_state = entry.provenance.lifecycle_state
        try:
            trust_class: str | None = _skill_trust_class(lifecycle_state).value
        except TrustClassError:
            trust_class = None
        decision = admit_memory_evidence(
            trust_class,
            stale=False,
            unknown_admission=_UNKNOWN_SKILL_ADMISSION,
        )
        tally.record(decision.admission, decision.code)
        if decision.admission is MemoryAdmission.DENY:
            continue
        item: dict[str, Any] = {
            "skill_id": descriptor.skill_id,
            "name": descriptor.name,
            "description": descriptor.description,
            "source_id": entry.provenance.source_id,
            "lifecycle_state": (
                lifecycle_state.value if lifecycle_state is not None else None
            ),
            "trust_class": trust_class,
            "selection_reason": (
                "Matched task signal(s) "
                + ", ".join(matched)
                + " against Skill name/description"
            ),
            "catalog_key": entry.catalog_key,
            "budget_class": (
                _BUDGET_SHOULD_LOAD
                if decision.admission is MemoryAdmission.LOAD
                else _BUDGET_ON_DEMAND
            ),
        }
        if decision.admission is MemoryAdmission.WITHHOLD:
            item["withheld_reason"] = decision.code
        if decision.admission is MemoryAdmission.LOAD and store is not None:
            try:
                document = load_catalog_skill(entry, store)
            except (SkillCatalogError, SkillParseError) as exc:
                item["body_withheld_reason"] = type(exc).__name__
            else:
                item["body"] = document.body
                item["body_sha256"] = document.descriptor.content_sha256
        selected.append(item)
    return selected, tally


def build_context_plan(
    store: TaskStore,
    task_id: str,
    *,
    repo_root: str | Path = ".",
    skill_catalog: SkillCatalog | None = None,
) -> dict[str, Any] | None:
    """Build a disposable context plan from explicit relationships only.

    Budget classing (roadmap 6.11, `work/roadmaps/00-MASTER-MAPS-CAPABILITY-
    ROADMAP.md` "Context budgets / progressive context"): this is advisory
    metadata *classifying* items the plan already explicitly gathers -- it
    adds no new retrieval, file search, or content-fetching, per the
    section's guardrail ("Explicit-first Context Builder remains preferred
    until retrieval methods prove value in frozen evaluations"). Mapping
    from the roadmap's four classes onto this function's existing structure
    (each call documented, since some are not 1:1):

    - `authority` (AGENTS.md) -> MUST_LOAD. Matches the roadmap's own
      "active authority" example exactly.
    - `required` (task `inputs`/`sources`) -> MUST_LOAD for every item,
      regardless of resolution `status`. These came from the task's own
      declared inputs/sources by construction, so they are MUST_LOAD
      ("task contract" / "critical current files") whether or not the
      referenced file currently resolves; resolution failure is a
      correctness signal (see `unresolved` below), not a demotion in
      importance.
    - `boundaries` (decision_authority, output_paths, acceptance_criteria,
      stop_conditions, verification, evidence_expected, review_required,
      escalation) -> conceptually MUST_LOAD as a whole ("task contract" /
      "policy"). It is not itemized with a per-field `budget_class` tag:
      `boundaries` is already always present in full on every plan (there is
      no partial-boundaries case to distinguish), so a uniform per-field tag
      would carry no information beyond what this docstring already states.
    - `dependencies` -> SHOULD_LOAD. Matches the roadmap's own "direct
      dependencies" example exactly.
    - `guidance` / `withheld_guidance` / `skills` -> decided by the memory
      trust gate (roadmap 6.22), not tagged here. Each memory-like item is
      routed by `admit_memory_evidence()`: `LOAD` keeps it in `guidance` /
      `skills` at SHOULD_LOAD ("relevant decisions" / the roadmap's own
      "applicable Skill" example), `WITHHOLD` puts it in `withheld_guidance`
      (or leaves the Skill entry in `skills`) at ON_DEMAND with a
      `withheld_reason` -- "old trajectories" / material only pulled in if
      specifically pursued, not part of the default load set -- and `DENY`
      drops it from the plan entirely with a counted reason under `coverage`.
      Bucket membership and budget class are outputs of that one decision, so
      no producer can hand itself a SHOULD_LOAD tag alongside a low trust
      class.
    - `unresolved` items are *not* independently reclassified: this list is
      built by filtering `[*authority, *required]` by resolution `status`,
      so each entry is the same dict object as its `authority`/`required`
      counterpart and already carries that item's MUST_LOAD tag. That is a
      deliberate choice, not an oversight: `budget_class` here answers "how
      important would this be if available", not "is it currently
      loadable" -- a missing MUST_LOAD input does not become less important
      for being missing. No separate ON_DEMAND tag is layered on.
    """

    task = store.get_task(task_id)
    if task is None:
        return None
    root = Path(repo_root).resolve()
    if not root.is_dir():
        raise ValueError("repo_root must be a directory")

    authority: list[dict[str, Any]] = []
    agents = root / "AGENTS.md"
    if agents.is_file():
        authority_item = _describe_reference(root, "AGENTS.md", "authority")
        authority_item["budget_class"] = _BUDGET_MUST_LOAD
        authority.append(authority_item)

    required: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for role, values in (("input", task["inputs"]), ("source", task["sources"])):
        for value in values:
            key = (role, value)
            if key in seen:
                continue
            seen.add(key)
            if value.strip() == "AGENTS.md" and agents.is_file():
                continue
            required_item = _describe_reference(root, value, role)
            required_item["budget_class"] = _BUDGET_MUST_LOAD
            required.append(required_item)

    dependencies: list[dict[str, Any]] = []
    for dependency_id in task["dependencies"]:
        dependency = store.get_task(dependency_id)
        if dependency is None:
            dependencies.append(
                {
                    "task_id": dependency_id,
                    "status": "MISSING",
                    "agi_status": "UNKNOWN",
                    "budget_class": _BUDGET_SHOULD_LOAD,
                }
            )
            continue
        dependencies.append(
            {
                "task_id": dependency_id,
                "status": dependency["status"],
                "agi_status": dependency["agi_status"],
                "title": dependency["title"],
                "outcome": dependency["outcome"],
                "budget_class": _BUDGET_SHOULD_LOAD,
            }
        )

    unresolved = [
        item
        for item in [*authority, *required]
        if item["status"] in {"missing", "outside_repo", "directory_not_expanded"}
    ]

    guidance, withheld_guidance, memory_trust_tally = _lesson_guidance(store, task)
    skills, skill_tally = _select_skills(skill_catalog, task, store)
    memory_trust_tally.merge(skill_tally)
    memory_like = [*guidance, *withheld_guidance, *skills]
    memory_trust_classification_present = all(
        isinstance(item.get("trust_class"), str) and bool(item["trust_class"].strip())
        for item in memory_like
    )

    return {
        "task_id": task_id,
        "task_revision": store.compute_task_revision(task_id),
        "authority": authority,
        "required": required,
        "guidance": guidance,
        "withheld_guidance": withheld_guidance,
        "skills": skills,
        "dependencies": dependencies,
        "boundaries": {
            "decision_authority": task["decision_authority"],
            "output_paths": task["output_paths"],
            "non_goals": task["non_goals"],
            "acceptance_criteria": task["acceptance_criteria"],
            "stop_conditions": task["stop_conditions"],
            "verification": task["verification"],
            "evidence_expected": task["evidence_expected"],
            "review_required": task["review_required"],
            "escalation": task["escalation"],
        },
        "unresolved": unresolved,
        "coverage": {
            "explicit_task_relationships": True,
            "root_agents_authority": bool(authority),
            "file_contents_included": False,
            "semantic_retrieval_used": False,
            "repository_scan_used": False,
            "note": (
                "v1 identifies exact trustworthy inputs to read; it does not "
                "search for unreferenced context"
            ),
            "budget_classification_present": True,
            "skill_bodies_loaded": sum(1 for item in skills if "body" in item),
            "budget_classification_note": (
                "authority/required tagged MUST_LOAD, dependencies tagged "
                "SHOULD_LOAD; memory-like guidance/withheld_guidance/skills "
                "are tagged by the memory trust gate instead (roadmap 6.22), "
                "so their budget class is a real admission decision rather "
                "than advisory. No new retrieval mechanism is introduced "
                "(roadmap 6.11 guardrail)"
            ),
            "memory_trust_classification_present": memory_trust_classification_present,
            "memory_trust_classification_note": (
                "memory-like guidance/withheld_guidance/skills carry "
                "MemoryTrustClass metadata when present; malformed optional "
                "memory evidence fails closed without suppressing canonical "
                "authority or required task context"
            ),
            "memory_trust_gate_applied": True,
            "memory_trust_gate_admitted": memory_trust_tally.admitted,
            "memory_trust_gate_withheld": memory_trust_tally.withheld,
            "memory_trust_gate_denied": memory_trust_tally.denied,
            "memory_trust_gate_reasons": dict(memory_trust_tally.reasons),
            "memory_trust_gate_note": (
                "every memory-like item that reaches the trust gate passes "
                "admit_memory_evidence(); its MemoryTrustClass alone decides "
                "that item's bucket membership and budget_class "
                "(LOAD/WITHHOLD/DENY). Unresolved trust metadata never yields "
                "LOAD: lessons withhold (their withheld form carries only "
                "lesson_id/reason), Skill entries deny (their entry carries "
                "name/description text). One DENY is decided earlier and "
                "outside the trust gate: SEC4 capability-manifest slice 2 "
                "(#225) drops a matched Skill whose declared capabilities fall "
                "outside the task_policy envelope, reason "
                "SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE -- a "
                "capabilities_within_envelope() intersection, not a "
                "MemoryTrustClass decision. It is recorded in the same tally "
                "(so it shows in *_denied and *_reasons) but is distinguishable "
                "by its reason code. All denied items, from either path, are "
                "dropped from the plan and counted here"
            ),
        },
    }
