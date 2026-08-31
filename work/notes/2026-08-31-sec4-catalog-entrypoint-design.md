# Design: SEC4 / 6.10 — the first production Skill-catalog entrypoint

Date: 2026-08-31
Owner: `lola` (MAPS_Lean lane), coordinator `miga`
Status: **design-only**. No runtime behavior changed by this note.
Parents:
- `work/notes/2026-08-31-sec4-half2-authority-wiring-design.md` (#190) — Half 2
  authority wiring; its scope boundary explicitly *defers* "committing
  `cli.py` / `flow_start.py` to build a `SkillCatalog` and deciding the catalog
  composition root … that is roadmap 6.11 (context budgets) territory."
- `work/notes/2026-08-25-sec4-skill-lifecycle-persistence-design.md` — Half 1.
- `work/notes/2026-08-31-roadmap-trajectory-check-10.md` §5a item 3.

This note makes the deferred decision so a bounded impl PR can proceed without
guessing (rules 9/10). It answers three questions:

- **(a)** what skills root / sources a real run discovers;
- **(b)** which entrypoint builds + registers the catalog;
- **(c)** the roadmap-6.11 context-budget interaction — does the Context
  Builder load Skill *bodies* by default? (bounded here, not fully designed.)

---

## Re-verified facts at HEAD `fbe88bc` (rule 14)

- `runtime/skills/catalog.py::build_skill_catalog(sources, *, store=None)`,
  `register_skill_catalog(catalog, store, *, now=None)`, and
  `load_catalog_skill(entry, store=None)` all exist and all accept a store
  (PR #192). `/usr/bin/grep -rn 'build_skill_catalog\|register_skill_catalog\|load_catalog_skill' --include=*.py`
  outside `tests/` → only the definitions + `runtime/skills/__init__.py`
  re-exports + docstring mentions. **Zero production callers.**
- `runtime/context_builder.py::build_context_plan(store, task_id, *, repo_root, skill_catalog=None)`
  is the only consumer of a `SkillCatalog`, via `_select_skills`. Both
  production callers — `runtime/cli.py:373` (`maps context`) and
  `runtime/flow_start.py:80` (`maps flow start`) — pass **no** `skill_catalog`,
  so `_select_skills` receives `None` and returns `[]` in every real flow.
- `_select_skills` reads only descriptor/provenance **metadata**. It never
  calls `load_skill` / `load_catalog_skill`; no Skill body ever enters the
  plan today. (Its own docstring, `context_builder.py:335-346`.)
- Trust projection is wired: `entry.provenance.lifecycle_state` →
  `context_builder._skill_trust_class` (`None → OBSERVATION`) →
  `runtime/trust.py::skill_lifecycle_trust_class` →
  `runtime/policy/memory_trust_gate.py::admit_memory_evidence`. Table
  (`_SKILL_LIFECYCLE_STATE_TO_MEMORY_TRUST_CLASS` + `_ADMISSION_TABLE`):
  - `None`/`DISCOVERED` → `OBSERVATION` → **WITHHOLD** (emitted as `ON_DEMAND`
    metadata with a `withheld_reason`, not in the default load set);
  - `VALIDATED` → `REVIEWED_GUIDANCE` → LOAD (metadata only — still no body);
  - `APPROVED` → `APPROVED_SKILL` → LOAD; `ACTIVE` → `ACTIVE_INSTRUCTION` →
    LOAD;
  - **`QUARANTINED` → `QUARANTINED` → DENY** (entry dropped from the plan
    entirely, counted under `coverage`);
  - `SUPERSEDED` → `SUPERSEDED` → WITHHOLD; `RETIRED` → `RETIRED` → WITHHOLD.
- The only Skill directory in the repo is `.claude/skills/` (one Skill:
  `.claude/skills/pilot/SKILL.md`). There is **no** MAPS-owned `skills/` root
  and no config key naming one. `discover_skills(root)` returns `()` for a
  missing root (does not raise).
- `runtime/flow_start.py::flow_start(store, task_id, *, repo_root, …)` already
  holds both a `TaskStore` (which carries the Skill-lifecycle mixin) and a
  `repo_root`, and already calls `build_context_plan` at step 2.

---

## (a) Skills root / sources

**Decision: a single `BUNDLED` source rooted at `<repo_root>/.claude/skills/`,
discovered fresh on each entrypoint call. No config key, no multi-source list,
no `THIRD_PARTY` sources yet.**

Rationale:

- `.claude/skills/` is the only Skill directory that exists. Inventing a
  second root (`skills/` at repo top, a `MAPS_SKILLS_ROOT` env var, a
  `.maps/config` key) is unbounded config surface for a subsystem with one
  Skill — rule 8 (smallest change).
- `SkillCatalogSource(source_id="bundled", root=repo_root/".claude/skills",
  kind=SkillSourceKind.BUNDLED)` is the whole source list. `source_ref`
  defaults to the resolved absolute path, which is fine for a bundled source.
- `discover_skills` returning `()` for an absent `.claude/skills/` means a
  checkout without that directory produces an empty catalog and the flow is
  byte-identical to today. No new failure mode.
- Third-party / local-install sources are SEC4's capability-declaration-manifest
  half (`NOT STARTED`), out of scope here. When they land they append
  `SkillCatalogSource` entries; nothing in this design blocks that.

**Open sub-question deliberately left:** whether the discovered root should be
`repo_root/.claude/skills` or a MAPS-namespaced path once MAPS ships its own
bundled Skills. Resolution: revisit when MAPS adds a second Skill; until then
`.claude/skills/` is the documented default and the impl PR names it in one
place (the new composition function) so a later move is a one-line change.

---

## (b) Which entrypoint builds + registers the catalog

**Decision: a new thin composition function
`runtime/skills/catalog.py::build_project_skill_catalog(repo_root, store, *, now=None) -> SkillCatalog`,
wired into `runtime/flow_start.py` ONLY. `maps context` (`cli.py:373`) stays
unchanged in this slice.**

```python
def build_project_skill_catalog(repo_root, store, *, now=None) -> SkillCatalog:
    source = SkillCatalogSource(
        source_id="bundled",
        root=Path(repo_root) / ".claude" / "skills",
        kind=SkillSourceKind.BUNDLED,
    )
    catalog = build_skill_catalog([source], store=store)
    register_skill_catalog(catalog, store, now=now)   # idempotent, gate-driven
    return catalog
```

`flow_start` step 2 becomes:

```python
skill_catalog = build_project_skill_catalog(repo_root, store)
context_plan = build_context_plan(store, task_id, repo_root=repo_root,
                                  skill_catalog=skill_catalog)
```

Why `flow_start` and not the alternatives:

| Candidate | Verdict |
|---|---|
| **`flow_start.py`** (`maps flow start`) | **Chosen.** It is the deterministic lifecycle-composition entrypoint (claim → context plan → run manifest); adding "discover + register Skills" to that composition is in character. It already has `store` + `repo_root`. It is invoked deliberately by a dispatcher, not on every read. |
| `cli.py:373` (`maps context`) | Deferred. `maps context` is a read-only inspection command an operator runs ad-hoc; making it write lifecycle-subject rows (`register_skill_catalog` records subjects) as a side effect of *inspecting* a plan is a surprising write-on-read. Wire it in a follow-up once the write is understood, or give it a read-only `store` that skips `register_skill_catalog`. |
| A new standalone module / daemon | Rejected (rule 13). No recurring machinery; a function on `catalog.py` is enough. |
| Inside `build_context_plan` itself | Rejected. That would put Skill discovery + a durable write inside the pure-ish plan builder and hit *both* callers at once — exactly the "forces a production catalog into existence" move #190 deferred. Passing `skill_catalog=` from one caller keeps the plan builder a pure consumer. |

**Subject-write note (Q4 of #190):** `register_skill_catalog` calls
`assess_skill(descriptor)` and `store.record_skill_lifecycle_subject(...)` for
each not-yet-recorded entry. With one Skill this is one gate run + one insert
per fresh `maps flow start`, idempotent thereafter (content-addressed
`catalog_key`). Acceptable cost. If a future multi-Skill catalog makes this
heavy, the pre-check already skips recorded entries; a bulk path is a later
optimisation, not a design constraint.

---

## (c) Roadmap-6.11 interaction — does the Context Builder load Skill bodies?

**Bounded answer: NO. This slice loads no Skill body and changes no
budget-class semantics. It only makes `lifecycle_state` real, which lets the
existing trust gate act on it.**

What actually changes for a real `maps flow start` after this slice:

- A **matched** Skill (name/description token overlaps task signals) whose
  composed state is `None`/`DISCOVERED`/`VALIDATED`/`SUPERSEDED`/`RETIRED`
  appears in the plan's `skills` list as **metadata only**, at `ON_DEMAND`
  budget class where the gate says WITHHOLD — i.e. exactly the current S6
  behaviour, no body, not in the default load set.
- A matched **`QUARANTINED`** Skill is **dropped from the plan** and counted
  under `coverage` (`admit_memory_evidence` → DENY). **This is the first real
  refusal reachable in a real run**: a Skill a `BLOCK`-severity gate finding
  quarantined can no longer be surfaced as context evidence for a live task.
- An unmatched Skill is omitted as today (S6 exit gate preserved).
- No call to `load_skill` / `load_catalog_skill` is added anywhere. Skill
  procedure-body text still cannot enter a context plan.

**The genuinely deferred 6.11 question, stated so it is not lost:** *should
`build_context_plan` (or a later loader) call `load_catalog_skill` to pull a
matched, LOAD-classed Skill's **body** into context, and at what budget class?*
That is roadmap **6.9 / S6 "progressive loading of matched Skill bodies"** —
the trajectory note §5b item 3. It needs its own design because it decides:
(i) whether Skill instruction text becomes authoritative context, (ii) the
budget-class / size accounting for a loaded body, (iii) the interaction with
`load_catalog_skill`'s refusal (a Skill that passes selection but is
`RETIRED` at load time). **This slice deliberately stops before all three**
and leaves `load_catalog_skill` reachable only as tested library code plus the
selection-layer DENY above.

---

## Smallest-first slice — what the impl PR does

1. `runtime/skills/catalog.py`: add `build_project_skill_catalog(repo_root, store, *, now=None)` (≈8 lines); export from `runtime/skills/__init__.py`.
2. `runtime/flow_start.py`: build the catalog and pass `skill_catalog=` to `build_context_plan`. One import, ~2 lines in `flow_start`. `flow_start`'s docstring step 2 updated ("build a read-only context plan, including matched bundled Skills gated by their durable lifecycle state").
3. Tests (`tests/test_flow_start.py` + wherever flow-start context-plan behaviour is asserted):
   - `maps flow start` on a task whose signals match the `pilot` Skill, with a `QUARANTINED` subject recorded for that Skill's `catalog_key` in the store → the plan's `skills` list excludes it and `coverage` counts the DENY.
   - same task, subject `VALIDATED` → Skill appears as metadata (no body).
   - no `.claude/skills/` dir → empty catalog, plan identical to pre-slice.
   - `register_skill_catalog` idempotence across two `flow_start` calls.
4. `work/roadmaps/CAPABILITY_CHECKLIST.md` 6.10 / SEC4 evidence text: **no
   status flip** — records that the refusal is now reachable via `maps flow
   start` selection-layer DENY, while `maps context`, progressive body loading
   (6.9/S6), and the capability-declaration manifest remain open.

**Explicitly NOT in the impl PR:** operator-identity registry / SEC4 Half 3;
`record_skill_lifecycle_transition` production caller; `maps context` wiring;
any `load_skill` / `load_catalog_skill` call in a production path; schema
changes; multi-source / third-party catalog sources.

---

## #192 non-blocking nits — folded into this note's PR

All four are doc/annotation-level (per `miga`); folded here rather than a
separate PR.

| # | Nit (as dispatched) | Finding at HEAD `fbe88bc` | Fix |
|---|---|---|---|
| 1 | `runtime/memory/memory_trust_gate.py` comment references deleted `SkillTrustState` | **Not reproducible.** The file is `runtime/policy/memory_trust_gate.py`; its comment (`:47-49`) already says "until a durable store is wired into `build_skill_catalog()`" — no `SkillTrustState` reference. Likely conflated with nit 3. | None needed; note in PR. |
| 2 | `build_skill_catalog` rebuilds `catalog_key` inline instead of using the property | Real: `catalog.py:196-199` formats the key by hand; `SkillCatalogEntry.catalog_key` (`:86-91`) is the canonical formula. They agree today but can drift. | Extract a module-level `_catalog_key(source_id, descriptor)` helper; call it from both `build_skill_catalog` and `SkillCatalogEntry.catalog_key`. ~5 lines, no behaviour change. |
| 3 | `runtime/skills/lifecycle.py` docstring still names `SkillTrustState` | Real: `lifecycle.py:11,18` + the "persistence … left for a future task" framing (`:7-9`) are stale post-#171/#192. | Update the docstring prose: persistence exists (`runtime/state/skill_lifecycle_storage.py`), `SkillTrustState` was collapsed into `SkillLifecycleState` (#192). Docstring only — transition graph, actor rules, public functions untouched; `tests/test_skill_lifecycle.py` unchanged. |
| 4 | `register_skill_catalog` has a bare `-> list` annotation | Real: `catalog.py:226`. | `-> list["MutationResult"]` (import under `TYPE_CHECKING` from `runtime.state.common`, matching the existing `SkillLifecycleStorageMixin` TYPE_CHECKING pattern in this file). |

Nit 2 is the only one touching real (non-docstring) code; it is a pure
refactor with test coverage via the existing round-trip tests. Per `miga`'s
instruction it stays folded unless review judges it too heavy for a note PR —
in which case it splits to its own one-file PR.

---

## Verification for the impl PR (next slice, not this note)

`python3 -m unittest tests.test_flow_start tests.test_skills_catalog
tests.test_context_builder` as one blocking foreground call; assert the
`QUARANTINED`-via-store refusal through `maps flow start`.
`python3 -m runtime.smoke` exit 0.

---

## Resume prompt

The catalog-entrypoint decision is made. Implement the smallest-first slice:
add `runtime/skills/catalog.py::build_project_skill_catalog(repo_root, store,
*, now=None)` (one `BUNDLED` source at `<repo_root>/.claude/skills/`,
`build_skill_catalog(store=store)` then `register_skill_catalog`), wire it into
`runtime/flow_start.py` step 2 so `build_context_plan` receives
`skill_catalog=`, and leave `maps context` (`cli.py:373`) untouched. The
observable new behaviour: a matched `QUARANTINED` Skill is DENY'd out of the
`maps flow start` context plan (first real refusal in a real run); everything
else stays metadata-only — no Skill body is loaded, that is 6.9/S6 progressive
loading and needs its own design (question (c) above bounds it). Fold the four
#192 nits: nit 1 is a no-op (misattributed — `runtime/policy/memory_trust_gate.py`
is already correct), nit 2 is an `_catalog_key` helper extraction, nit 3 is a
`lifecycle.py` docstring refresh, nit 4 is `register_skill_catalog -> list["MutationResult"]`.
Update `CAPABILITY_CHECKLIST.md` 6.10 / SEC4 evidence text — no status flip.
Independent review, no self-merge.
