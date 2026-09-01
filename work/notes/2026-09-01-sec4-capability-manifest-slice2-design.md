# SEC4 capability-declaration manifest — slice 2: runtime capability intersection (design)

**STATUS: DESIGN ONLY. Changes no runtime code, no schema, no checklist status.**
Design/scoping only (phase 1). Do **not** implement until this note lands and
the coordinator confirms the slice.

Scopes slice 2 of
`work/notes/2026-09-01-sec4-capability-declaration-manifest-design.md` — the
"Runtime capability intersection (§5.2 / §6.5)" item that note's §7 deferred as
"a later slice". Slice 1 (`capabilities` sidecar + `UNDECLARED_CAPABILITY` gate
finding feeding `SkillLifecycleState`) merged as PR #219.

All facts re-verified against `origin/main` `059ab45` (rule 14).

---

## 1. Re-verified facts

### 1a. Slice 1, as merged (PR #219)

`runtime/skills/gate.py` (lines 105–248):

- `_CAPABILITY_MANIFEST_FILENAME = "capabilities"`; `_CAPABILITY_TOKENS`
  frozenset = the roadmap `04-agentic-security.md` §5.1 vocabulary
  (`filesystem-read/-write`, `shell`, `network-read/-general`,
  `github-read/-write`, `database-read/-write`, `process-stop`,
  `external-deploy`); `_SECRET_USE_RE = ^secret-use:[a-z0-9][a-z0-9-]*$`.
- `_parse_capability_manifest(payload: bytes) -> frozenset[str] | _MANIFEST_MALFORMED`
  — non-UTF-8 or any non-blank/non-comment line that is not a recognized token
  → `_MANIFEST_MALFORMED`; comment-only file → `frozenset()` ("declares
  nothing", distinct from absent).
- `_DETECTOR_CAPABILITY` = the five **REVIEW-tier** static detectors →
  capability token (`SCRIPT_NETWORK_ACCESS→network-general`,
  `CREDENTIAL_ENVIRONMENT_ACCESS→secret-use:environment`,
  `DESTRUCTIVE_OPERATION→filesystem-write`, `PRIVILEGE_OPERATION→shell`,
  `EXECUTABLE_RESOURCE_PRESENT→shell`). `_SATISFYING_TOKENS` gives
  `network-general` the alias set `{network-general, network-read}`.
- `_apply_capability_manifest(findings, by_relative)` — reconciles detector
  findings against the sidecar, emitting `DECLARED_CAPABILITY_USE` (INFO) /
  `UNDECLARED_CAPABILITY` (BLOCK) / `CAPABILITY_MANIFEST_ABSENT` (REVIEW) /
  `CAPABILITY_MANIFEST_MALFORMED` (BLOCK) / `OVER_DECLARED_CAPABILITY` (INFO).
  Called once in `assess_skill` just before the finding dedup/sort.

**The declared set is not carried structurally.** It exists only transiently
inside `_apply_capability_manifest`; the `SkillGateReport` records it only as
free text inside finding `summary` strings, and the persisted `gate_report`
JSON (`skill_lifecycle_subjects.gate_report`) likewise. There is **no**
`declared_capabilities` field on `SkillDescriptor`, `SkillGateReport`,
`SkillGateFinding`, `SkillCatalogEntry`, or `SkillProvenance`
(`/usr/bin/grep -rn "declared_capab" runtime/` → the only hits are the
`_apply_capability_manifest` locals and this design note).

### 1b. The Skill-activation seam and its (missing) production caller

`runtime/skills/catalog.py::load_catalog_skill(entry, store=None)` (lines
306–334) is the design-note-named "activation seam". It:

- refuses activation (`SkillCatalogError`) when the composed
  `SkillLifecycleState` is `QUARANTINED`/`RETIRED`/`SUPERSEDED`
  (`_NON_ACTIVATABLE_LIFECYCLE_STATES`, lines 297–303);
- otherwise `return load_skill(entry.descriptor)` (hash-verifies the snapshot,
  reads the procedure body).

**It has no task context and no production caller.**
`/usr/bin/grep -rn "load_catalog_skill" runtime/ --include=*.py` (excl. tests) →
only the `runtime/skills/__init__.py` re-export and doc mentions. The signature
has no `task` / `task_policy` parameter.
`runtime/context_builder.py::_select_skills` (lines 328–413) states in its own
docstring: *"`load_skill`/`load_catalog_skill` (procedure body activation) is
never called, so no Skill instruction text can enter the plan."*

The natural future caller is **6.9/S6 progressive Skill-body loading**
(design note `2026-09-01-6.9-s6-progressive-skill-body-loading-design.md`,
PR #217) — not yet implemented.

### 1c. `_select_skills` already has the task policy envelope in scope

`runtime/context_builder.py::build_context_plan` line 474: `task = store.get_task(task_id)`.
`runtime/state/policy.py::PolicyStateMixin.get_task` attaches
`task["policy"]` — the full `task_policy` row:
`requires_operator_approval`, `destructive_action`, `external_side_effect`,
`security_sensitive`, `broad_architecture`, `paid_execution`, plus
`approved_by`/`approved_at`/`approval_note` (verified at runtime:
`get_task('T1')['policy']` returns all six booleans).

`build_context_plan` line 533: `skills, skill_tally = _select_skills(skill_catalog, task)`
— so **`_select_skills` already receives the full `task` dict including
`task["policy"]`**. It currently uses only
`_skill_task_signal_tokens(task)` (`task_type`, `project_id`, output-path
segments); it never reads `task["policy"]`.

`_select_skills` per-entry loop (lines 370–412): match signal tokens → trust
gate (`_skill_trust_class(lifecycle_state)` → `admit_memory_evidence`) →
`tally.record(...)` → `if decision.admission is MemoryAdmission.DENY: continue`
(dropped from the plan, counted under `coverage`). This is exactly where slice
1's `QUARANTINED → MemoryTrustClass.QUARANTINED → DENY` drop happens.

### 1d. `task_policy` — no schema change is available or needed

`runtime/state/schema.sql:116-128` `task_policy`: the six `INTEGER … CHECK (… IN (0,1))`
booleans, `approved_by`/`approved_at`/`approval_note`. Slice 2 reads these; it
adds no column. PR #211 already added the `validate_ready` consistency rule
(`destructive_action`/`external_side_effect` ⇒ `requires_operator_approval`).

### 1e. `DestructiveExternalActionGuard` — the axis slice 2 must not duplicate

`runtime/policy/destructive_action_guard.py::DestructiveExternalActionGuard`
reads the **live** task's `policy` and DENYs an action outside the envelope
(`ACTION_OUTSIDE_TASK_ENVELOPE` / `OPERATOR_REAUTHORIZATION_ABSENT`). It is
composed default-off in `build_canonical_harness_service` and fires only from
`HarnessService.stop()` (no production caller). It gates **runtime actions** via
caller-declared `destructive`/`external` booleans at the call site.

Slice 2 is a **different lifecycle stage**: it gates which **Skills are
surfaced into a context plan**, using the Skill's *declared* capabilities
against the task's *already-decided* envelope. It is a composition at
plan-assembly time, not a runtime action guard, and it never calls or modifies
`DestructiveExternalActionGuard`.

---

## 2. The seam

The slice-1 note assumed the intersection would live at `load_catalog_skill`
"gaining a `task_policy`-aware caller". Re-verification (1b) shows that caller
**does not exist and building it is out of scope** (it is 6.9/S6's job — a
STOP condition for this dispatch: *"load_catalog_skill has no path to task
context without a new production caller that is itself a larger design"*).

The seam that **is** reachable in a real `maps flow start` today is
`_select_skills` (1c): it already has both the `SkillCatalogEntry` and
`task["policy"]`, and it is already the place where a Skill gets DENY'd out of
the context plan (slice 1's QUARANTINED drop). Slice 2 adds one more DENY
reason there.

**Recommendation: slice 2 = the `_select_skills` context-plan-time
intersection.** When 6.9/S6 later gives `load_catalog_skill` a `task_policy`-aware
caller, the *same* intersection helper composes there too as activation-time
defense in depth — that is a 6.9/S6 follow-up, not slice 2.

This respects design rule §5:
- the manifest is **not written into `task_policy`** — `task["policy"]` is read
  as *context* (what the task is already authorized for), the manifest is read
  as the Skill's *declaration*; the check is `declared ⊆ permitted`;
- **no second authority store** — both inputs already exist (`task_policy` row,
  `capabilities` sidecar);
- **no runtime guard reads the manifest as authority** — `_select_skills` is
  plan-assembly, not an enforcement hook; the manifest never reaches
  `DestructiveExternalActionGuard` or any `HookRegistry`.

---

## 3. Carrying the declared set to the seam

`_select_skills` must know each matched Skill's declared capability set. Two
ways:

**(a) [recommended] a structural `SkillDescriptor.declared_capabilities` field.**
`runtime/skills/format.py::_descriptor_for_root` and `load_skill` parse the
`capabilities` sidecar (reusing `gate._parse_capability_manifest`, or a copy
moved to `format.py` to avoid a `skills.format → skills.gate` import cycle —
check the direction) into `declared_capabilities: tuple[str, ...]` (`()` when
absent; a malformed manifest also yields `()` here, but slice 1's gate already
`QUARANTINE`s a malformed manifest so such a Skill never reaches `_select_skills`
as non-DENY). Add the field to the `SkillChangedError` identity-equality checks
alongside `resource_paths`. Slice 1's `assess_skill` can then consume
`descriptor.declared_capabilities` instead of re-reading `by_relative` (a small,
optional slice-1 tidy — not required for slice 2). `_select_skills` reads
`entry.descriptor.declared_capabilities` — **pure metadata, no file I/O**,
matching its current "only descriptor/provenance metadata is read here"
contract. The slice-1 note deferred a `SkillDescriptor` field only "once the
vocabulary is proven"; slice 1 is merged, the vocabulary is proven.

**(b) [minimal] a bounded re-read helper.** `_select_skills` calls
`read_declared_capabilities(entry.descriptor)` which reads only
`<descriptor.root>/capabilities` and parses it. Smaller diff, but it puts a
file read into `_select_skills` (which today does none) — a docstring-scope
question, and the read is not hash-verified against `content_sha256` at
plan-time (acceptable: `_select_skills` already trusts discovery-time
`descriptor.name`/`description` without re-verification, and `load_skill` still
hash-verifies at activation).

**Recommend (a).** It keeps `_select_skills` pure, is a bounded `format.py`
change (~15 lines + test-fixture updates), and gives every downstream consumer
(6.9/S6 activation, future Capability Packs) the structural field for free.

---

## 4. The capability → `task_policy` permission mapping — the crux, review this hard

`_select_skills` DENYs a matched Skill when **any** declared capability token is
not permitted by the task's envelope. Proposed mapping (coarse, whole-Skill,
matching slice 1's granularity):

| Declared capability | Permitted when `task_policy` has… | Rationale |
|---|---|---|
| `filesystem-read`, `github-read`, `database-read`, `network-read` | **always** (baseline) | read-only; no envelope boolean gates reads |
| `filesystem-write` | **always** (baseline) | writing repo files is normal implementation work; the *destructive* subset is what slice-1's `DESTRUCTIVE_OPERATION` detector + review already flags. Gating it on `destructive_action` would DENY every implementation Skill. |
| `shell` | **always** (baseline) | the harness itself runs in a shell; too broad to hang on one boolean. Elevated shell (`sudo`/`chmod 777`) is slice-1's `PRIVILEGE_OPERATION` (REVIEW). |
| `network-general` | `external_side_effect` | arbitrary outbound calls are an external side effect |
| `github-write`, `database-write` | `external_side_effect` | mutating an external system of record |
| `process-stop` | `destructive_action` | the slice-1 note's own worked example |
| `external-deploy` | `external_side_effect` **and** `destructive_action` | highest-impact; both apply |
| `secret-use:<name>` | `security_sensitive` | credential access is the `security_sensitive` envelope's purpose |

Notes for the reviewer:
- This table is a **technical security mapping**, the analogue of slice 1's
  `_DETECTOR_CAPABILITY` map — decidable here, but it carries real judgment and
  should get the same scrutiny slice 1's detector map got. If a reviewer
  believes the baseline set (esp. `filesystem-write`, `shell`) is too generous,
  that is a review comment, not a re-scope.
- It is **not** an operator-authority question and does **not** re-touch the §7
  third-party trust-root `OPERATOR DECISION` (slice 2 is still `BUNDLED`-only —
  `build_project_skill_catalog` produces only `BUNDLED`; a `THIRD_PARTY` Skill
  would additionally need the countersign decision that stays batched with SEC4
  Half 3).
- `broad_architecture` and `paid_execution` do not map to any capability token
  and are ignored by the intersection.
- The mapping lives as a frozen dict in one module (proposed:
  `runtime/skills/capability_policy.py` or a constant in `context_builder.py`);
  it is imported, never duplicated (rule 12).

---

## 5. Smallest first slice

**Property made true in a real `maps flow start` run:**

> A matched Skill that declares a capability token the running task's
> `task_policy` envelope does not permit (per the §4 table) is **DENY'd from the
> context plan** — dropped from `plan["skills"]` and counted under
> `plan["coverage"]` with reason `SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE` —
> regardless of the Skill's trust class.

### Impl surface (for the eventual impl task — NOT this note)

1. **`runtime/skills/format.py`**: add `SkillDescriptor.declared_capabilities:
   tuple[str, ...]`; parse the `capabilities` sidecar at discovery
   (`_descriptor_for_root`) and in `load_skill`; include it in the identity
   checks. Reuse the slice-1 parser (resolve the import direction —
   `format.py` must not create a cycle with `gate.py`; if it would, move
   `_parse_capability_manifest` + `_CAPABILITY_TOKENS` + `_SECRET_USE_RE` to
   `format.py` and have `gate.py` import them).
2. **`runtime/skills/capability_policy.py`** (new, ~30 lines): the §4 mapping as
   a frozen dict + `capabilities_within_envelope(declared: Iterable[str],
   policy: Mapping[str, Any]) -> tuple[bool, tuple[str, ...]]` returning
   `(ok, offending_tokens)`. Pure, no I/O, no store.
3. **`runtime/context_builder.py::_select_skills`**: after the `matched` check
   and before the trust-class gate, compute
   `capabilities_within_envelope(entry.descriptor.declared_capabilities,
   task.get("policy") or {})`; on failure
   `tally.record(MemoryAdmission.DENY, "SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE")`
   and `continue`. Fail-open only on a *missing* policy dict (treat as
   all-false → a Skill declaring anything beyond baseline is DENY'd — that is
   fail-**closed** for the consequential tokens, which is correct).
4. **Tests**: `tests/test_skill_capability_manifest.py` +
   `tests/test_context_builder.py`: a `process-stop`-declaring Skill matched to
   a task with `destructive_action=False` → DENY'd, `coverage` reason present;
   same Skill + `destructive_action=True` → surfaces; a baseline-only
   (`filesystem-read`) Skill → unaffected by envelope; a `secret-use:x` Skill vs
   `security_sensitive` on/off; `network-general` vs `external_side_effect`;
   no-manifest Skill (`declared_capabilities == ()`) → never DENY'd on this
   axis; end-to-end `build_project_skill_catalog` + `build_context_plan`.
   ≥5 mutations on `capabilities_within_envelope` and the `_select_skills` hook.
5. **`work/roadmaps/CAPABILITY_CHECKLIST.md`** SEC4 + 6.10 (+ 6.24 least-
   privilege-intersection) rows: one evidence clause each — "capability
   manifest slice 2: `_select_skills` intersects declared capabilities against
   `task_policy` at context-plan time" — **no status flip**.

### MAY / MUST NOT

- **MAY change**: `runtime/skills/format.py`,
  `runtime/skills/capability_policy.py` (new),
  `runtime/context_builder.py::_select_skills`, `runtime/skills/gate.py` (only
  the optional tidy to consume `descriptor.declared_capabilities`), the named
  tests, and the SEC4/6.10/6.24 checklist evidence text.
- **MUST NOT**: change `schema.sql` or any `task_policy` / `skill_lifecycle_*`
  table; write the manifest into `task_policy`; add a new authority store; make
  `DestructiveExternalActionGuard` (or any `HookRegistry` guard) read the
  manifest; add a `task_policy`-aware parameter/caller to `load_catalog_skill`
  (that is 6.9/S6); target `THIRD_PARTY` Skills; flip any checklist status;
  change slice-1's finding codes or `_apply_capability_manifest` behavior.

### Acceptance

PR open; CI green; a `process-stop`-declaring Skill is dropped from the
`maps flow start` context plan for a non-destructive task and surfaces for a
destructive one; a no-manifest Skill is unaffected on this axis; slice-1 gate
behavior unchanged; `SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE` appears in
`plan["coverage"]`; no status flip.

### Verification

`python3 -m unittest tests.test_skill_capability_manifest
tests.test_context_builder tests.test_skills_catalog tests.test_skills_format` —
one blocking foreground run. `python3 -m runtime.smoke` exit 0.
`git diff --stat origin/main` = only the MAY-change files.

---

## 6. Out of scope for slice 2

- **Activation-time (`load_catalog_skill`) intersection** — composes for free
  once 6.9/S6 (PR #217) gives it a `task_policy`-aware caller; a 6.9/S6
  follow-up, not slice 2.
- **`DestructiveExternalActionGuard` composition** — different axis (1e);
  untouched.
- **Per-capability granularity** (`filesystem-write` scoped to paths,
  `network-general` to hosts) — slice 2 stays whole-Skill / coarse-class,
  matching slice 1.
- **`THIRD_PARTY` Skills + the §7 self-authored-manifest trust root** — still
  batched with SEC4 Half 3; slice 2 is `BUNDLED`-only.
- **MCP / tool-server capability manifests** — separate surface, separate note.
- **Capability Packs** (S7 / 6.12) — the `declared_capabilities` field should be
  reusable by a Pack, but slice 2 targets Skills.
- **Behavioral evaluation** — does the Skill stay within its declaration at run
  time (roadmap §8) — separate.

## 7. OPERATOR DECISION

**None new.** The §4 capability→`task_policy` mapping is a technical security
mapping (reviewer scrutiny, not operator sign-off). The §7 third-party
trust-root `OPERATOR DECISION` from the slice-1 note is **not re-touched** —
slice 2 is `BUNDLED`-only and the decision stays batched with SEC4 Half 3.

## 8. STOP-condition check (dispatch)

- *Schema change / new authority store?* — **No.** `task_policy` has the
  booleans; the sidecar exists; the mapping is a frozen dict in one module.
  Stays inside the approved envelope.
- *`load_catalog_skill` needs task context without a new caller?* — **Yes for
  the activation seam**, which is why slice 2 targets `_select_skills` instead
  (1c: it already has `task["policy"]`). The `load_catalog_skill` intersection
  is explicitly deferred to a 6.9/S6 follow-up. No STOP.
- *Operator authority question blocks the smallest slice?* — **No.** §7.

---

## Resume prompt

You are implementing SEC4 capability-declaration manifest **slice 2** for
MAPS_Lean — the runtime capability intersection at context-plan time. Work in a
worktree off `origin/main`; `git fetch origin main` first; re-verify every
callsite at your HEAD (rule 14).

Source of truth: this note
(`work/notes/2026-09-01-sec4-capability-manifest-slice2-design.md`) §3–§5, and
the files it cites: `runtime/skills/format.py` (`SkillDescriptor`,
`_descriptor_for_root`, `load_skill`), `runtime/skills/gate.py`
(`_parse_capability_manifest`, `_CAPABILITY_TOKENS`, `_SECRET_USE_RE` — resolve
the import direction), `runtime/context_builder.py::_select_skills` +
`build_context_plan` (line ~474 `store.get_task` attaches `task["policy"]`),
`runtime/state/schema.sql` `task_policy`, `work/roadmaps/agent-harness-capabilities/04-agentic-security.md`
§5.1/§5.2/§6.5.

Implement exactly §5 "Smallest first slice": (1) `SkillDescriptor.declared_capabilities`
parsed at discovery; (2) new `runtime/skills/capability_policy.py` with the §4
mapping + `capabilities_within_envelope()`; (3) `_select_skills` DENYs a matched
Skill whose declared capability is outside `task["policy"]` with reason
`SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE`, counted under `coverage`; (4) tests
incl. end-to-end + ≥5 mutations; (5) one checklist evidence clause on the SEC4 /
6.10 / 6.24 rows, **no status flip**.

MUST NOT: change `schema.sql` / `task_policy` / `skill_lifecycle_*`; write the
manifest into `task_policy`; add a new authority store; make any `HookRegistry`
guard read the manifest; add a `task_policy` param/caller to
`load_catalog_skill` (that is 6.9/S6); target `THIRD_PARTY` Skills; change
slice-1 finding codes or `_apply_capability_manifest`; flip any checklist
status.

Tests (one blocking foreground `python3 -m unittest`, no Monitor/background):
`tests.test_skill_capability_manifest tests.test_context_builder
tests.test_skills_catalog tests.test_skills_format`. `python3 -m runtime.smoke`
exits 0. Push before any full-suite run; rely on CI.

PR into `main` (never push). Do NOT spawn your own reviewer — ping the
coordinator. Independent review + mutation; reviewer commits the evidence file.
No self-merge.

STOP + flag the coordinator if: the §4 mapping turns out to DENY the repo's own
bundled Skills in a way that reveals the baseline set is wrong (semantics
question, not a silent fix); the `format.py` parser move creates an import
cycle that needs a larger refactor than moving three constants; or a real
`_select_skills` caller passes a task with no `policy` key (should be
impossible — `get_task` always attaches it — but verify).
