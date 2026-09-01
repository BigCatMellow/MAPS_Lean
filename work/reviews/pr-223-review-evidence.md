# PR #223 review evidence — SEC4 capability-manifest slice 2 design note

reviewer: maps-lean-luve
head_sha: e045ddfeaf5b36c09d35e4abf3cf099a90beac80
independent: true
summary: Independent verification-only review by maps-lean-luve (did not author — gela did). DESIGN ONLY, 1 file (work/notes/2026-09-01-sec4-capability-manifest-slice2-design.md, +385), no runtime/schema/checklist change. All 6 verification points pass. gela's key finding is ACCURATE against origin/main: load_catalog_skill(entry, store=None) has no task/task_policy parameter and no production caller (only __init__ re-export + docstrings), so the slice-1-assumed activation seam does not exist; _select_skills DOES already receive the full task dict incl. task["policy"] (build_context_plan store.get_task attaches all six task_policy booleans — verified at runtime — and passes task) and is already where slice 1's QUARANTINED→DENY context-plan drop happens. The proposed +1 DENY reason SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE at _select_skills reads task_policy as context and the manifest as declaration (check: declared ⊆ permitted) — it never writes task_policy, adds no authority store, and is not a HookRegistry/runtime-action guard, consistent with the spirit of slice-1 §5 (the seam move from load_catalog_skill to _select_skills is transparently argued and the manifest already influences _select_skills transitively via the lifecycle→trust chain). The §4 capability→task_policy mapping is coarse-correct and defensible — its most generous edges (network-read, filesystem-write, shell at baseline) each carry a rationale tied to an existing slice-1 detector. NO checklist status flip, NO phase-1 runtime change. §7 third-party trust-root NOT re-touched (BUNDLED-only, stays batched with SEC4 Half 3). Smallest-slice + MAY/MUST-NOT + acceptance + verification + Resume prompt (with STOP conditions) all present. VERDICT: APPROVE. 3 non-blocking review comments. NB: head_sha rebound by coordinator to the post-rebase commit (branch predated #221/#222; rebase clean, design note only).

## Verification (rule 14)

### (1) gela's key finding — ACCURATE
- `runtime/skills/catalog.py:306` `def load_catalog_skill(entry, store=None)` — no `task`/`task_policy` parameter.
- `/usr/bin/grep -rn "load_catalog_skill" runtime/ --include=*.py | grep -v test` → only `runtime/skills/__init__.py` re-export + docstring mentions. No production caller. Building one is 6.9/S6's job (correctly declared a STOP condition; the seam is moved rather than the dispatch stalled).
- `runtime/context_builder.py` `task = store.get_task(task_id)`; `runtime/state/policy.py` `task["policy"] = policy`. Runtime check: `get_task(tid)["policy"]` returns all six `task_policy` booleans + approval metadata. `_select_skills(skill_catalog, task)` already has `task["policy"]` and today reads only `_skill_task_signal_tokens(task)`.
- `_select_skills` per-entry loop already does `if decision.admission is MemoryAdmission.DENY: continue` (the slice-1 QUARANTINED drop). Slice 2 adds one more DENY branch at the same point.

### (2) proposed DENY respects slice-1 §5 design rule
Slice-1 §5: manifest "feeds `SkillLifecycleState` and nothing else … MUST NOT be read by any runtime guard, MUST NOT be written into `task_policy`, MUST NOT create a second place where 'this action is authorized' is decided."
- Not written into `task_policy` — read as *context*; the manifest is read as *declaration*; the op is a set-containment check. No write. ✓
- No second authority store — both inputs already exist. ✓
- No runtime guard reads the manifest — `_select_skills` is context-plan assembly, not a `HookRegistry` hook; never reaches `DestructiveExternalActionGuard`. ✓
- "feeds `SkillLifecycleState` and nothing else" — slice 2 stretches the literal wording, but: (a) slice-1 §5 itself names the `task_policy` composition as "explicitly a later slice"; (b) the manifest already influences `_select_skills` transitively today (manifest → BLOCK → QUARANTINE → `SkillLifecycleState` → trust → DENY); (c) `_select_skills` is the same lifecycle stage as slice-1's own enforcement, never a running-task envelope. Consistent with the intent of §5. Defensible.

### (3) §4 capability → `task_policy` mapping — scrutinized
Verified against slice-1's `_DETECTOR_CAPABILITY`, `_CAPABILITY_TOKENS`, `_SECRET_USE_RE`.
- `process-stop → destructive_action` — slice-1's own worked example. ✓
- `github-write` / `database-write` / `network-general` → `external_side_effect`; `external-deploy` → `external_side_effect` AND `destructive_action`; `secret-use:<name>` → `security_sensitive` — coherent.
- Baseline (always-permitted): `*-read`, `filesystem-write`, `shell` — each rationale tied to an existing slice-1 mechanism (destructive subset of `filesystem-write` is `DESTRUCTIVE_OPERATION` REVIEW; elevated `shell` is `PRIVILEGE_OPERATION` REVIEW; gating `filesystem-write` on `destructive_action` would DENY every implementation Skill). Coarse but defensible; whole-Skill granularity matches slice 1.
- `broad_architecture` / `paid_execution` unmapped — acknowledged; no §5.1 token corresponds.

### (4) NO checklist status flip, NO phase-1 runtime change
`git diff --stat`: 1 file, +385. STATUS line: "DESIGN ONLY. Changes no runtime code, no schema, no checklist status."

### (5) §7 third-party trust-root NOT re-touched
Slice 2 is `BUNDLED`-only; the third-party self-authored-manifest OPERATOR DECISION from slice-1 §7 stays batched with SEC4 Half 3. Not re-opened. ✓

### (6) slice structure complete
§5: one concrete property; a 5-item impl surface (`format.py` `declared_capabilities` field, new `capability_policy.py`, the `_select_skills` hook, tests incl. end-to-end + ≥5 mutations, checklist evidence); explicit MAY/MUST NOT; Acceptance; Verification. Resume prompt carries a MUST-NOT list + 3 STOP conditions. §8 does its own dispatch STOP-condition check.

## Non-blocking review comments (do not gate merge)
1. §4 `network-read` at baseline is the most generous edge — a Skill declaring only `network-read` still opens outbound connections on a task with no `external_side_effect`. Defensible under read-vs-mutate; the impl reviewer or a later granularity slice may want it gated.
2. The `_select_skills` seam formally departs from slice-1 §5's assumed `load_catalog_skill` seam — recommend the impl's checklist evidence clause state the seam explicitly.
3. `paid_execution` has no capability token and is silently ignored — worth a one-line "known gap" in the impl evidence.

## Verdict: APPROVE
