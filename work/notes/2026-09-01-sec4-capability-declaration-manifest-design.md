# SEC4 — capability-declaration manifest for Skills (design)

**STATUS: DESIGN ONLY. Changes no runtime code, no schema, no checklist status.**
Design review only. Scopes "SEC4's other half" (the SEC3 row's "Still NOT built:
the capability-declaration manifest half"), dispatched as trajectory-check-#12
(PR #214) §5 next-3 item #1.

All facts re-verified against merged code at `origin/main` `5230c73` (rule 14).

---

## 1. Re-verified facts

### 1a. The capability vocabulary already exists in the roadmap — nowhere in code

`work/roadmaps/agent-harness-capabilities/04-agentic-security.md` §5.1
("Capability declaration") lists the intended tokens:

```
filesystem-read  filesystem-write  shell
network-read  network-general
github-read  github-write  database-read  database-write
process-stop  external-deploy  secret-use:<capability-name>
```

with the note "Capability names are descriptive, not authority grants." §5.2
defines the run-authorization intersection
(`worker capabilities ∩ task scope ∩ policy ∩ operator approvals ∩ environment`)
and §6.5 ("Before tool activation") says "Check Skill/Capability Pack declared
requirements against run authority." §16 states the target property:

> PROPERTY: Skill text cannot grant undeclared capability.

`/usr/bin/grep -rn "filesystem-write\|network-general\|capability.declar\|declared_capab" runtime/`
→ **no hits**. No `SkillDescriptor` field, no catalog field, no gate finding, no
storage column carries a declared-capability set today. §23 backlog items 6
("Define external tool/MCP provenance manifest") and 8 ("Add executable resource
inspection to Skill gate") are the adjacent backlog; item 8 is partly done (the
gate does static resource inspection — 1c), item 6 is a distinct surface (MCP
servers, not Skills — see §6 out-of-scope).

### 1b. What SEC4's lifecycle half already ships (the wiring the manifest plugs into)

Re-verified at `5230c73`:

- `runtime/skills/format.py::SkillDescriptor` (lines 25–44) — `skill_id`, `name`,
  `description`, `root`, `content_sha256` (whole-directory hash),
  `declared_metadata_keys`, and typed resource-path tuples (`resource_paths`,
  `script_paths`, `reference_paths`, `asset_paths`, `example_paths`). Docstring:
  "contains no procedure body and no authority or approval state."
- `runtime/skills/format.py::_parse_frontmatter_lines` (lines 81–120) —
  **deliberately does not interpret nested/custom frontmatter**: "v1 does not
  interpret it during discovery … without … turning custom metadata into
  executable/authoritative state." Custom top-level keys are recorded in
  `declared_metadata_keys` but their values are not parsed.
- `runtime/skills/gate.py::assess_skill` (lines 262–400) — static, single
  hash-verified byte-snapshot assessment. Emits `SkillGateFinding`s at
  `INFO`/`REVIEW`/`BLOCK` severity; disposition is `QUARANTINE` if any `BLOCK`,
  else `REVIEW_REQUIRED` if any `REVIEW`, else `CLEAR` (lines 386–391).
  Docstring: "The report is advisory gate evidence … neither `REVIEW_REQUIRED`
  nor `QUARANTINE` mutates any persistent trust state." `runtime/skills/gate_hardened.py`
  re-exports it as the complete implementation and monkeypatches
  `_gate_module.assess_skill` — `runtime/skills/catalog.py:284`
  imports `from .gate_hardened import assess_skill`.
- `runtime/skills/catalog.py::build_project_skill_catalog(repo_root, store)`
  (lines 229–261) — the **first production entrypoint that builds a catalog with
  a store**, wired into `runtime/flow_start.py` (`maps flow start`) per
  `work/notes/2026-08-31-sec4-catalog-entrypoint-design.md`. One `BUNDLED`
  source at `<repo_root>/.claude/skills/`. Calls `register_skill_catalog(...)`
  then rebuilds with the store.
- `runtime/skills/catalog.py::register_skill_catalog` (lines 264–294) — the
  production caller of `record_skill_lifecycle_subject()`. For every
  not-yet-recorded entry it runs `assess_skill(entry.descriptor)` and passes the
  `SkillGateReport` to the store.
- `runtime/skills/lifecycle.py::initial_transition_from_gate_report` (lines
  151–164) — `QUARANTINE` disposition → `SkillLifecycleState.QUARANTINED`; any
  other disposition → `VALIDATED`. "thin, obviously-correct reading of
  `report.disposition`."
- `runtime/state/skill_lifecycle_storage.py::record_skill_lifecycle_subject`
  (lines 189–266) — starting state "is derived from the gate report by the
  existing `initial_transition_from_gate_report()`; it is never caller-supplied."
  Append-only `skill_lifecycle_subjects` / `skill_lifecycle_decisions` tables.
- `runtime/skills/catalog.py::load_catalog_skill` (lines 306–334) +
  `_NON_ACTIVATABLE_LIFECYCLE_STATES` (lines 297–303) — refuses activation
  (`SkillCatalogError`) when composed state is `QUARANTINED`/`RETIRED`/`SUPERSEDED`.
- `runtime/context_builder.py::_select_skills` (lines 328–397) — a matched
  Skill's `lifecycle_state` → `runtime/trust.py::skill_lifecycle_trust_class`
  (`QUARANTINED` → `MemoryTrustClass.QUARANTINED`, line 107) →
  `runtime/policy/memory_trust_gate.py::admit_memory_evidence`
  (`MemoryTrustClass.QUARANTINED: MemoryAdmission.DENY`, line 68) → the entry is
  **dropped from the flow-start context plan** and counted under `coverage`
  (line 387–388).

**Consequence for this design:** a single new `BLOCK`-severity gate finding is
the *entire* enforcement path. `assess_skill` `BLOCK` → `QUARANTINE` →
`QUARANTINED` subject state → (a) `load_catalog_skill` refuses activation and
(b) `_select_skills` DENYs it out of a real `maps flow start` context plan. **No
schema change, no lifecycle-storage change, no new authority store, no new
`HookEnforcement` type.**

### 1c. What the static gate already infers (the detectors the manifest is checked against)

`runtime/skills/gate.py` regexes + resource checks, with their current severity:

| Detector (const / check) | Finding code | Severity | Capability class it evidences |
|---|---|---|---|
| `_NETWORK_ACCESS_RE` on a script resource | `SCRIPT_NETWORK_ACCESS` | REVIEW | `network-read` / `network-general` |
| `_NETWORK_PIPE_EXEC_RE` (`curl … \| sh`) | `NETWORK_PIPE_EXEC` | BLOCK | `network-general` + `shell` |
| `_CREDENTIAL_HARVEST_RE` (`os.environ`, `/proc/self/environ`, …) | `CREDENTIAL_ENVIRONMENT_ACCESS` | REVIEW | `secret-use:environment` |
| `_DESTRUCTIVE_RE` (`rm -rf`, `DROP TABLE`) | `DESTRUCTIVE_OPERATION` | REVIEW | `filesystem-write` (destructive) / `database-write` |
| `_PRIVILEGE_RE` (`sudo`, `chmod 777`, `mount`) | `PRIVILEGE_OPERATION` | REVIEW | `shell` (elevated) |
| script resource present | `EXECUTABLE_RESOURCE_PRESENT` | REVIEW | `shell` |
| sensitive resource filename (`.env`, `id_rsa`, `*.pem`) | `SENSITIVE_RESOURCE_NAME` | BLOCK | `secret-use:*` |

The gate has **no notion of "declared vs. detected"** today — every detection is
an unconditional finding regardless of what the Skill claims about itself.

### 1d. `task_policy` / `DestructiveExternalActionGuard` — a different axis

`runtime/state/schema.sql` `task_policy` (six booleans: `requires_operator_approval`,
`destructive_action`, `external_side_effect`, `security_sensitive`,
`broad_architecture`, `paid_execution`) is **per-task runtime authority** — what
the *running task* is authorized to do. `runtime/policy/destructive_action_guard.py::DestructiveExternalActionGuard`
reads it live and denies an action outside that envelope
(`ACTION_OUTSIDE_TASK_ENVELOPE` / `OPERATOR_REAUTHORIZATION_ABSENT`). PR #211
added `validate_ready`'s consistency rule linking the envelope booleans to the
reauth flag.

The Skill capability manifest is a **different axis**: it is per-Skill
*supply-chain* metadata — what the *procedural content* claims it needs —
evaluated statically at gate time, feeding lifecycle state. They are not
duplicate authority (rule 12): the Skill manifest never authorizes anything at
runtime; it only decides whether the Skill's content is admissible. The two axes
*compose* at §6.5 ("before tool activation": run authority ∩ Skill declared
requirements) — but that intersection is a **later slice**, not this one (§5,
§6).

---

## 2. Point 1 — what a capability-declaration manifest IS for this system

A **flat, per-Skill list of capability tokens** (from the §5.1 vocabulary,
1a) that the Skill's author asserts the Skill's procedure + resources require.
Descriptive, not an authority grant — exactly as §5.1 says.

**Shape (recommended):** a single UTF-8 sidecar file in the Skill bundle,
`capabilities` (no extension) or `CAPABILITIES.txt`, one token per line,
`#`-comments and blank lines ignored, tokens drawn from a fixed closed set
(the §5.1 list, plus `secret-use:<name>` with a bounded `<name>` charset). An
absent file means "no manifest".

**Why a sidecar, not frontmatter, for the first slice:**

- It is **already covered by `content_sha256`** (`SkillDescriptor` hashes the
  whole directory) and already carried through the hash-verified snapshot
  `assess_skill` reads (`by_relative` in `gate.py:272`). No `format.py` change
  is needed to make the bytes available to the gate.
- `format.py::_parse_frontmatter_lines` **deliberately refuses** to interpret
  nested/list frontmatter and treats custom top-level keys as review-worthy
  (`CUSTOM_METADATA_PRESENT`, REVIEW, `gate.py:342-351`). Putting the manifest
  in frontmatter means either a list value (which v1 does not parse) or a
  delimited scalar (fragile), plus a `format.py` change to promote the key from
  "custom, review-worthy" to "known, structured". That is a larger, format-layer
  change — reasonable as an *eventual* home (§4 "later slices"), wrong for slice 1.
- A sidecar keeps the manifest a **first-class resource** the gate can point a
  finding's `path` at (`capabilities`), which reads well in a review.

**What it is NOT:** not a new `SkillDescriptor` field for slice 1 (that couples
the format layer to the capability vocabulary; do it only once the vocabulary is
proven — §4); not YAML; not per-resource (whole-Skill granularity is enough for
the exit gate); not a runtime object.

---

## 3. Point 2 — what it gates and where (the enforcement seam)

**Seam: `runtime/skills/gate.py::assess_skill`** — the existing static
single-snapshot assessor. It already reads every resource in the verified
snapshot; the manifest parse + comparison is added there, emitting new findings
that flow through the **unchanged** disposition → lifecycle → refusal chain
(1b).

New findings (slice 1):

| Condition | Proposed code | Severity | Effect |
|---|---|---|---|
| A detector in 1c fires for a capability class, and no manifest token covers that class | `UNDECLARED_CAPABILITY` | **BLOCK** | → `QUARANTINE` → `QUARANTINED` → `load_catalog_skill` refuses + `_select_skills` DENYs. **Realizes the §16 PROPERTY.** |
| A script/network/credential detector fires and there is **no manifest file at all** | `CAPABILITY_MANIFEST_ABSENT` | REVIEW | → `REVIEW_REQUIRED` (not quarantine) — a Skill with executable content but no manifest is review-worthy, not auto-blocked, so existing manifest-less bundled Skills degrade to "needs review" not "broken". |
| Manifest file present but unparseable / unknown token / malformed `secret-use:` | `CAPABILITY_MANIFEST_MALFORMED` | **BLOCK** | fail-closed — a manifest you cannot read is not a manifest. |
| Manifest declares a capability class no detector evidences | `OVER_DECLARED_CAPABILITY` | INFO | visible, non-blocking — over-asking is noise, not a threat, but a reviewer should see it (and a Skill declaring *everything* to dodge `UNDECLARED_CAPABILITY` then trips this on every unused token, making the evasion obvious). |

**Mapping detector → capability class** is a fixed table in `gate.py` (the 1c
table, inverted). It is intentionally coarse: `network-read` and
`network-general` both satisfy a network detection for slice 1 (the manifest
says "this Skill touches the network", the gate does not adjudicate read
vs. general — that refinement is a later slice).

**Why `assess_skill` and not `load_catalog_skill` / `build_project_skill_catalog`:**
those are lookup/activation points that consume lifecycle state; they do not
re-assess content. Putting the check in `assess_skill` means it runs exactly
once per content revision (at `register_skill_catalog` time), is captured in the
stored `gate_report` JSON (`skill_lifecycle_storage.py:266`), and needs no new
call site. `load_catalog_skill`'s refusal already covers the activation side for
free once the state is `QUARANTINED`.

---

## 4. Point 3 — relationship to the existing static `gate.py` lint

**Complement, not replace.** Precise division:

- The **lint stays the detector** — the 1c regexes/resource checks are the
  ground truth for "what capability does this content actually exercise". They
  are not removed or weakened.
- The **manifest is the expectation the detector output is checked against.**
  Today every detection is an unconditional `REVIEW`/`BLOCK` finding. After slice
  1, a detection that **matches a declared capability** is *downgraded to INFO*
  (`DECLARED_CAPABILITY_USE`) — the Skill said it would do this, a human already
  reasoned about it when authoring/reviewing the manifest, so it is no longer a
  standing review item. A detection with **no matching declaration** escalates
  to `UNDECLARED_CAPABILITY` BLOCK.

  Net: the manifest lets a legitimately network-using Skill reach `CLEAR`/`VALIDATED`
  by declaring `network-general`, instead of being permanently stuck at
  `REVIEW_REQUIRED` for `SCRIPT_NETWORK_ACCESS`. That is the manifest earning its
  place — it converts "static detection = perpetual review noise" into "static
  detection vs. declaration = a real signal".

- The lint is **not** "the enforcement of the manifest" and the manifest is
  **not** "the enforcement of the lint" — they are two inputs to the same
  `SkillGateReport`, and the report's existing disposition logic is the
  enforcement.

`_DESTRUCTIVE_RE` / `_CREDENTIAL_HARVEST_RE` (the codes the dispatch names) are
exactly the detectors whose findings get the declared/undeclared treatment:
`DESTRUCTIVE_OPERATION` + declared `filesystem-write` → INFO; undeclared →
`UNDECLARED_CAPABILITY` BLOCK.

---

## 5. Point 4 — relationship to SEC3 `task_policy` + `DestructiveExternalActionGuard`

Covered in 1d. Restated as the design rule:

> The Skill capability manifest is **gate-time supply-chain metadata**. It feeds
> `SkillLifecycleState` and nothing else. It MUST NOT be read by any runtime
> guard, MUST NOT be written into `task_policy`, and MUST NOT create a second
> place where "this action is authorized" is decided.

The composition with `task_policy` (a Skill that declares `process-stop` should
only be activatable for a task whose `task_policy.destructive_action` is set —
§5.2 / §6.5) is **explicitly a later slice** and would live at the tool-activation
seam (`load_catalog_skill` gaining a `task_policy`-aware caller), not in the
manifest format. Slice 1 stops at "undeclared capability ⇒ quarantine".

One interaction to record for the reviewer: `DestructiveExternalActionGuard`
takes `destructive`/`external` as **caller-declared booleans at the call site**
(the SEC3 "declaration-at-the-operation" pattern). The Skill manifest is the
analogous "declaration-at-the-artifact". Same philosophy, different lifecycle
stage — kept deliberately separate so a Skill's self-declaration can never
influence a running task's envelope.

---

## 6. Point 5 — smallest first slice

**Goal: make ONE concrete property true in a real `maps flow start` run:**

> A bundled Skill whose script resource contains `curl … | sh` (or any 1c
> detector hit) and which has **no `capabilities` sidecar declaring the matching
> capability** is `QUARANTINED` at `register_skill_catalog` time and is DENY'd
> out of the `maps flow start` context plan (counted under `coverage`), and
> `load_catalog_skill` refuses to activate it.

### Slice-1 implementation surface (for the eventual impl task — NOT this note)

1. **`runtime/skills/gate.py`**:
   - A `_CAPABILITY_TOKENS` frozenset (the §5.1 vocabulary) + a `secret-use:`
     validator.
   - `_parse_capability_manifest(text) -> frozenset[str] | MALFORMED`.
   - A fixed `_DETECTOR_CAPABILITY` map (1c table inverted).
   - In `assess_skill`: locate `capabilities` in `by_relative`; parse; for each
     detector finding, compare against the declared set; emit
     `DECLARED_CAPABILITY_USE` (INFO) / `UNDECLARED_CAPABILITY` (BLOCK) /
     `CAPABILITY_MANIFEST_ABSENT` (REVIEW) / `CAPABILITY_MANIFEST_MALFORMED`
     (BLOCK) / `OVER_DECLARED_CAPABILITY` (INFO).
   - The existing detector findings (`SCRIPT_NETWORK_ACCESS` etc.) are still
     emitted but at their existing severity only when *undeclared*; when declared
     they are replaced by the INFO `DECLARED_CAPABILITY_USE`.
2. **`runtime/skills/format.py`**: add `"capabilities"` (and/or `CAPABILITIES.txt`)
   to whatever resource-classification produces `resource_paths` so the sidecar
   is a recognized non-script resource, not an `EXECUTABLE_RESOURCE_PRESENT`
   false positive. (Verify against `format.py`'s resource classifier — it keys
   on suffix/mode; a plain extensionless text file should already land in
   `resource_paths`. If so, no `format.py` change.)
3. **Tests** (`tests/test_skills_quality_gate*.py` + a new
   `tests/test_skill_capability_manifest.py`): declared→INFO; undeclared→BLOCK→QUARANTINE
   disposition; absent-manifest-with-script→REVIEW; malformed→BLOCK;
   over-declared→INFO; a clean Skill with a correct manifest → `CLEAR`; an
   end-to-end `build_project_skill_catalog` + `_select_skills` test showing the
   undeclared Skill dropped from the plan.
4. **`work/roadmaps/CAPABILITY_CHECKLIST.md`** SEC4 + SEC3 rows: one evidence
   clause each ("capability-declaration manifest slice 1: `capabilities` sidecar
   + `UNDECLARED_CAPABILITY` gate finding"), **no status flip** (the exit gate —
   "unreviewed executable Skill/tool content cannot become active silently" — is
   materially closer but MCP/tool manifests + the runtime intersection remain).

### Bundled-Skill migration

The repo's own `.claude/skills/` Skills that ship scripts will hit
`CAPABILITY_MANIFEST_ABSENT` (REVIEW, not BLOCK) on first run after the impl —
they stay activatable (`VALIDATED`), just flagged. Authoring their `capabilities`
files is a follow-up chore, not a blocker. **No Skill is auto-broken by slice 1.**

### Does slice 1 need a schema change? **No.**

Confirmed against `runtime/state/skill_lifecycle_storage.py` (1b): the starting
state is derived from the `SkillGateReport` disposition; the full report is
already persisted as JSON in the existing `gate_report` column. A new finding
code needs no column. The `skill_lifecycle_subjects` / `_decisions` tables are
untouched.

---

## 7. Point 6 — out of scope + OPERATOR DECISION REQUIRED

### Explicitly out of scope for this design / slice 1

- **MCP / external tool-server manifests** (roadmap §9, §23 backlog item 6).
  Tool servers are not Skills, have no `SkillDescriptor` or `content_sha256`,
  and their capability surface (transport, network, credentials) is a different
  inventory (`04-agentic-security.md` §9 list). A separate note.
- **Runtime capability intersection** (§5.2 / §6.5 — Skill declared requirements
  ∩ task authority at activation). Needs a `task_policy`-aware caller of
  `load_catalog_skill`; later slice.
- **Per-capability granularity** (`network-read` vs `network-general`,
  `filesystem-write` scoped to paths). Slice 1 is whole-Skill, coarse class.
- **Capability Packs** (S7 / 6.12, `NOT STARTED`, gated on S6). The manifest
  format should be *reusable* by a future Capability Pack but slice 1 targets
  Skills only.
- **Behavioral evaluation** of declared capabilities (§8 "behavioral tests" —
  does the Skill actually stay within its declaration at run time). Separate.
- **The operator-identity registry** (`authorized_operators`, SEC4 Half 3) —
  already its own design note
  (`2026-08-31-sec4-operator-lifecycle-transitions-and-identity-design.md`),
  design-pending on an unmade operator decision. Not re-opened here.
- Moving the manifest into structured frontmatter / a `SkillDescriptor` field
  (eventual home once the vocabulary is proven — §2).

### OPERATOR DECISION REQUIRED — third-party Skill manifest trust root

For a `BUNDLED` / `LOCAL` Skill (`SkillSourceKind`), the `capabilities` file is
in-repo: operator authority over it = checkout control, the same trust basis as
`spec_ref` for environment contracts (`work/notes/2026-08-31-env-evidence-writer-authority-redecision-design.md`).

For a **`THIRD_PARTY`** Skill (`SkillSourceKind.THIRD_PARTY`, defined but with no
production source today), the manifest would ship *inside the imported bundle* —
authored by the same untrusted party as the procedure. A malicious third-party
Skill simply declares every capability it uses and passes `UNDECLARED_CAPABILITY`
cleanly. `OVER_DECLARED_CAPABILITY` (INFO) makes a "declare everything" bundle
visible, and a `THIRD_PARTY` Skill starts `QUARANTINED`/`VALIDATED` and needs an
operator `maps skill approve` regardless — so the manifest is still useful as
*reviewer-facing evidence*. But whether a third-party Skill's **self-authored
manifest is ever sufficient on its own**, or whether an operator must
**countersign** a capability declaration for any non-in-repo source before that
Skill can leave `QUARANTINED`, is a trust-root policy question.

**Recommended answer (not adopted here):** slice 1 targets `BUNDLED` only (which
is all `build_project_skill_catalog` produces today), and the third-party
countersign question is deferred to the same operator-decision batch as the SEC4
Half 3 trust-root decision — they are the same shape of question (who is
authoritative for a non-in-repo trust assertion). Flagged to @mono.

This design does **not** answer it.

---

## 8. Recommendation

Adopt §6 slice 1: a `capabilities` sidecar file + declared-vs-detected
comparison in `assess_skill`, emitting `UNDECLARED_CAPABILITY` (BLOCK). It
realizes the roadmap's §16 PROPERTY ("Skill text cannot grant undeclared
capability") for `BUNDLED` Skills in a real `maps flow start`, with **no schema
change, no new authority store, no new hook type, no runtime guard** — the
entire enforcement rides the existing gate → disposition → lifecycle →
refusal/DENY chain (1b). The third-party trust-root question is flagged as an
operator decision, batched with SEC4 Half 3.

---

## Resume prompt

You are implementing SEC4 capability-declaration manifest **slice 1** for
MAPS_Lean. Work in a worktree off `origin/main`; `git fetch origin main` first.
Re-verify every callsite at your HEAD (rule 14).

Source of truth: this note
(`work/notes/2026-09-01-sec4-capability-declaration-manifest-design.md`) §6
"Smallest first slice", and the files it cites: `runtime/skills/gate.py`
(`assess_skill`, the 1c detector table), `runtime/skills/format.py`
(`SkillDescriptor` resource classification), `runtime/skills/catalog.py`
(`register_skill_catalog`, `load_catalog_skill`),
`runtime/skills/lifecycle.py::initial_transition_from_gate_report`,
`runtime/context_builder.py::_select_skills`, and the §5.1 capability vocabulary
in `work/roadmaps/agent-harness-capabilities/04-agentic-security.md`.

Implement exactly §6: a `capabilities` sidecar (one §5.1 token per line,
`#`-comments ok), parsed in `assess_skill`; a fixed detector→capability map;
findings `DECLARED_CAPABILITY_USE` (INFO) / `UNDECLARED_CAPABILITY` (BLOCK) /
`CAPABILITY_MANIFEST_ABSENT` (REVIEW) / `CAPABILITY_MANIFEST_MALFORMED` (BLOCK) /
`OVER_DECLARED_CAPABILITY` (INFO); a declared detection is downgraded to the INFO
code. Tests including an end-to-end `build_project_skill_catalog` +
`_select_skills` showing an undeclared-capability Skill dropped from the plan.
One checklist evidence clause on the SEC4 and SEC3 rows, **no status flip**.

MUST NOT: change `schema.sql` or any `skill_lifecycle_*` table; add a
`SkillDescriptor` field (sidecar only for slice 1); read the manifest from any
runtime guard or write it into `task_policy`; touch
`DestructiveExternalActionGuard` or `initial_transition_from_gate_report`
logic; implement the runtime capability-intersection (§7 out of scope); target
`THIRD_PARTY` Skills (§7 operator decision).

Tests (one blocking foreground `python3 -m unittest` — no Monitor, no
background): `tests.test_skills_quality_gate tests.test_skills_quality_gate_metadata
tests.test_skill_capability_manifest tests.test_skills_catalog
tests.test_context_builder` (or the closest existing modules) + a targeted
`tests.test_cli_skill` run. `python3 -m runtime.smoke` exits 0. Push before any
full-suite run; rely on CI.

Then: PR into `main` (never push to main). Do NOT spawn your own reviewer — ping
the coordinator. Independent review; reviewer commits
`work/reviews/pr-<N>-review-evidence.md`. Do NOT self-merge. Report the PR
number to the coordinator.

STOP conditions (flag the coordinator): the sidecar turns out to need a
`format.py` resource-classifier change that is larger than one allowlist entry;
adding the finding reveals bundled Skills that would be BLOCK-quarantined (not
just REVIEW-flagged) by slice 1; or the detector→capability mapping is genuinely
ambiguous for a real bundled Skill in a way this note did not anticipate.
