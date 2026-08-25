reviewer: /root/pr167_reviewer
head_sha: 71d1357eb824c075355902257b7d7ed14d3adaa5
independent: true
summary: APPROVED — PR #167 adds exactly one design-only note (work/notes/2026-08-25-sec4-skill-lifecycle-persistence-design.md) for SEC4/6.10, and every factual claim in its Finding section was independently re-verified by fresh grep/read of runtime/skills/lifecycle.py (161 lines, 7-member enum, transition() confirmed a pure validator that returns its own target argument with no persistence and no history object), tests/test_skill_lifecycle.py (8 legal edges, 41 illegal pairs, actor rules on both ->APPROVED edges, no-actor APPROVED->ACTIVE and QUARANTINED->RETIRED, SUPERSEDED/RETIRED terminal — all confirmed), runtime/skills/catalog.py (catalog_key format quoted exactly right, SkillTrustState still single-member UNASSESSED, trust_state hashed into SkillCatalog.fingerprint and never reassigned), runtime/state/schema.sql (grep -in "skill" returns zero hits, so no Skill table exists), runtime/trust.py and runtime/skills/__init__.py; the proposed mechanism genuinely mirrors the real operational_lessons / operational_lesson_decisions pattern at schema.sql 641-734 (immutable CHECK-locked base row, append-only decision table, composed-not-stored status via _compose() plus re-validation in get_operational_lesson(), and the named no_repromote/no_reretire triggers) rather than inventing a storage mechanism; it respects roadmap section 7 by reusing the existing TaskStore rather than creating a second authority database (7.2), storing references/hashes only and no Skill bodies (6.3), refusing a knowledge graph (7.6) and refusing any daemon or reconciler (7.1/7.9); it matches the SEC3 precedent note's Finding/Decision/Non-goals/behavior-questions/Roadmap-impact structure with 8 genuinely open, implementation-relevant questions; CAPABILITY_CHECKLIST.md is untouched with SEC4 (line 60) and 6.10 (line 119) both still IN PROGRESS; two non-blocking nits are recorded below (a "30+ tables" count that is actually 29, and an "unwired" phrasing that is true of the lifecycle mapping but not of runtime/trust.py as a whole, since runtime/context_builder.py already consumes skill_trust_class).

# Review: PR #167 SEC4/6.10 Skill lifecycle persistence design

- Note reviewed: `work/notes/2026-08-25-sec4-skill-lifecycle-persistence-design.md`
- Precedent structure compared against: `work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md`
- Reviewed by: `/root/pr167_reviewer`
- Verdict: `APPROVED`

## 1. Diff scope

`git rev-parse HEAD` in this worktree returns `71d1357eb824c075355902257b7d7ed14d3adaa5`, matching the PR head.

`git diff origin/main...HEAD --stat`:

```
work/notes/2026-08-25-sec4-skill-lifecycle-persistence-design.md | 320 +++++++++++++++++++++
1 file changed, 320 insertions(+)
```

Exactly one file, 320 insertions, 0 deletions, and one commit on the branch. Nothing under `runtime/`, `tests/`, `work/roadmaps/`, or `scripts/` is touched. Confirmed independently that `git diff origin/main...HEAD -- work/roadmaps/CAPABILITY_CHECKLIST.md` is empty.

## 2. Groundedness — every Finding-section claim re-verified independently

Each item below was checked by my own read/grep, not by trusting the note's cited commands.

- **`lifecycle.py` shape.** `wc -l runtime/skills/lifecycle.py` = 161. Read in full: it contains `SkillLifecycleState` (7 members), `SkillLifecycleError`, `_ACTOR_REQUIRED_TRANSITIONS`, `_ALLOWED_TRANSITIONS`, `transition()`, `initial_transition_from_gate_report()` — and nothing else. Imports are `__future__.annotations`, `enum.Enum`, and `.gate`. No `sqlite3`, no `Path`, no file I/O, no class holding state. Claim accurate.
- **`transition()` is a pure validator returning its own argument.** Confirmed by reading the function body: it type-checks both arguments, looks up `_ALLOWED_TRANSITIONS.get(current, frozenset())`, applies the actor requirement, and ends with a bare `return target`. It writes nothing anywhere and appends to no history structure. The note's stronger framing ("stricter than in-memory — both halves are missing") is correct, not rhetorical.
- **No production caller of either function.** `grep -rn "skills.lifecycle\|SkillLifecycleState\|initial_transition_from_gate_report" --include=*.py .` returns only: the module itself, `runtime/skills/__init__.py` (re-export), `runtime/trust.py` (enum only), `tests/test_skill_lifecycle.py`, and `tests/test_trust.py`. No production call site of `transition()` or `initial_transition_from_gate_report()` exists. Claim accurate.
- **Test contract.** Read `tests/test_skill_lifecycle.py` (184 lines) in full. `LEGAL_EDGES` is a hand-written set of exactly 8 edges, independent of the module's own table; `test_every_illegal_transition_raises` iterates all 7x7 = 49 pairs and skips the 8 legal ones, giving the 41 the note cites. `test_discovered_cannot_skip_quarantine_review_to_approved` and `test_discovered_cannot_skip_review_to_active` exist. Both `*->APPROVED` actor tests assert on `None`, `""`, and `"   "`. `test_approved_to_active_does_not_require_actor` and `test_quarantined_to_retired_does_not_require_actor` exist. `test_terminal_states_have_zero_outgoing_transitions` covers `SUPERSEDED`/`RETIRED`. `test_transition_rejects_non_enum_values` covers non-enum arguments. Three gate-report tests drive real `assess_skill()` output: CLEAR -> `VALIDATED`, REVIEW_REQUIRED -> `VALIDATED`, QUARANTINE -> `QUARANTINED`. Every test-contract claim in the note is accurate.
- **`catalog_key` format.** `runtime/skills/catalog.py:82-87` reads `f"{self.provenance.source_id}:{self.descriptor.skill_id}" f"@sha256:{self.descriptor.content_sha256}"`. The note quotes it as `f"{source_id}:{skill_id}@sha256:{content_sha256}"` — the concatenation is identical. Content-addressed, so an edited Skill yields a different key. Claim accurate.
- **`SkillTrustState` / fingerprint.** `catalog.py:30-33` has exactly one member `UNASSESSED` with the "A future reviewed trust lifecycle may add states" comment; `SkillProvenance.trust_state` defaults to it (line 73); `SkillCatalog.__post_init__` hashes `entry.provenance.trust_state.value` into the fingerprint (line 121). `grep -rn "trust_state" --include=*.py .` shows no site that ever assigns a non-default value. Claim accurate.
- **Zero Skill tables.** `grep -in "skill" runtime/state/schema.sql` returns nothing at all (exit status 1). There is genuinely no place in the schema for a Skill's lifecycle state. Claim accurate.
- **Checklist wording.** `work/roadmaps/CAPABILITY_CHECKLIST.md` line 60 contains verbatim "a pure, unpersisted primitive with no durable storage of a Skill's current state and no real operator-authority wiring", and line 119 contains verbatim "unpersisted — no durable lifecycle state or real authority wiring yet". Both quotations in the note are exact, including the note's own correct distinction between the two lines' wording.

No blocking factual error found in the Finding section. Two non-blocking inaccuracies are recorded in section 6.

## 3. Does the proposed mechanism really mirror the operational-learning pattern?

Read `runtime/state/schema.sql` lines 641-734 and `runtime/state/operational_learning_storage.py`. The pattern the note describes exists exactly as described:

| Element the note claims exists | Verified at |
|---|---|
| Immutable base row locked by `CHECK (status = 'CANDIDATE')` | `schema.sql:649-667` (`operational_lessons`, `status TEXT NOT NULL CHECK (status = 'CANDIDATE')`) |
| `BEFORE UPDATE` / `BEFORE DELETE` triggers raising ABORT on the base row | `trg_operational_lessons_no_update`, `trg_operational_lessons_no_delete` |
| Append-only decision table with `decision_kind`, JSON `decision_payload`, non-empty `decided_by`, `decided_at` | `operational_lesson_decisions`, `decided_by TEXT NOT NULL CHECK (length(trim(decided_by)) BETWEEN 1 AND 128)` |
| Decision table also update/delete-trigger-locked | `trg_operational_lesson_decisions_no_update` / `..._no_delete` |
| Effective status derived by `_compose(base_row, decisions)`, never stored | `operational_learning_storage.py:192` (`_compose`), called at lines 143 and 168 |
| Composed record re-validated through the pure validator as defense in depth | `get_operational_lesson()` at line 143-144 returns `validate_lesson_record(composed)` |
| Illegal sequences refused in Python (`ALREADY_PROMOTED`, `LESSON_RETIRED`) and again by triggers | Python codes at lines 244-250; triggers `trg_operational_lesson_decisions_no_repromote` and `..._no_reretire` |
| State machine `CANDIDATE -> ACTIVE -> RETIRED` with explicit actor | `runtime/operational_learning.py:14` `_STATUSES = {"CANDIDATE", "ACTIVE", "RETIRED"}`; `promote_operational_lesson(lesson_id, *, decision_ref, promoted_by, ...)` |
| Storage records the claimed actor without adjudicating it | `promote_operational_lesson()` rejects only an empty `promoted_by` (`INVALID_ACTOR`) and performs no further identity verification |
| `MutationResult(ok, code, message)` return shape used by every mixin | `runtime/state/common.py:33-37` |
| Mixin registered on `TaskStore` alongside its peers | `runtime/state/store.py:10` imports `OperationalLessonStorageMixin`, line 24 lists it in the `TaskStore` bases |

The proposal is a faithful reuse, not an invented mechanism. The one genuinely new element — composing effective state by replaying decisions through the *existing pure* `transition()` rather than reimplementing the graph in SQL or in the mixin — is a correct application of rule 12 and is the direct analogue of `get_operational_lesson()` re-running `validate_lesson_record()`.

## 4. Roadmap constraint compliance

Read `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` section 7 (7.1-7.10, "Explicitly rejected-by-default architecture") and `work/roadmaps/agent-harness-capabilities/02-procedural-knowledge-and-skills.md` sections 6.2, 6.3, and 7.

- **7.2 second task/session authority database — respected.** Both proposed tables go into the existing `runtime/state/schema.sql` served by the existing `TaskStore`, accessed via a new mixin registered exactly like `OperationalLessonStorageMixin`. No new DB file, no new connection logic, no sidecar registry. This is the same store that already holds `operational_lessons`, which is likewise not task/session state, so the precedent is real.
- **6.3 no Skill bodies in SQLite — respected.** The `skill_lifecycle_subjects` column list is references, hashes, timestamps, and a `gate_report` JSON snapshot of `SkillGateReport.to_dict()`. The note calls out the absence of `SKILL.md` bodies explicitly and quotes 6.3 accurately ("Prefer manifests/indexes derived from filesystem + small approval metadata rather than copying entire Skill content into SQLite" / "store references/hashes, not duplicate Skill bodies"). The gate report is a findings/verdict summary, not procedure text — a fair reading.
- **7.6 knowledge graph — respected.** An explicit non-goal, with the `SUPERSEDED` successor pointer deliberately capped at "at most one nullable reference on a decision payload — not a graph, not a dependency index, not a queryable ontology", and open question 8 declines to commit to even that.
- **7.1 / 7.9 daemon or background reconciler — respected.** An explicit non-goal. The mechanism is plain synchronous read/write from the code path that already discovers/assesses Skills, and the drift story is structural (changed content yields a different `catalog_key` with no `APPROVED` decision behind it) rather than a poller. This is a genuinely daemon-free answer to drift, not a daemon renamed.
- **6.2 authority — respected.** Nothing in the design grants task authority from an `APPROVED` Skill; the design is about recording a lifecycle state, and the first real refusal is explicitly deferred to Half 2.
- **Skills roadmap section 7 (hash/version re-evaluation, no silent auto-update) — respected and correctly quoted.** Content-addressed `catalog_key` is exactly the mechanism section 7 asks for.

No roadmap-rejected construct is smuggled in. No status row is flipped to DONE.

## 5. Rigor and structure parity with the SEC3 precedent

`work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md` headings are: Finding / Decision / (one mechanism section) / Non-goals / Behavior questions the implementation task must answer / Roadmap impact.

The PR #167 note has: Finding / Decision / "What 'durable storage + real authority wiring' means as an implementation boundary" / Non-goals (8 bullets) / "Behavior questions the implementation task must answer" (same heading verbatim, 8 questions) / Roadmap impact. Full parity, with the mechanism section serving the same role as SEC3's, plus an explicit Half-1/Half-2 scope split with in-scope and out-of-scope lists.

I checked each of the 8 open questions for being genuinely open (not answered elsewhere in the same note) and genuinely implementation-relevant:

1. `catalog_key` vs `(source_id, skill_id)` as primary key — the note proposes one but explicitly leaves the `BUNDLED`-churn consequence undecided. Real fork, real cost named.
2. A Skill that vanishes from disk while its subject row is composed-`ACTIVE` — genuinely unaddressed elsewhere; three concrete candidate answers are listed and none is picked. Sharpened by the fact that the tables are trigger-locked immutable, so "delete the row" is not available.
3. Where `DISCOVERED` lives — the note states its proposal (absence of a row) and then requires the implementation to accept-and-document it or persist `DISCOVERED` subjects. That is a real semantic choice, not padding.
4. Who calls `record_skill_lifecycle_subject()` in production and when — explicitly not answered, and correctly identified as the analogue of the SEC3 note's call-site question.
5. Whether the actor requirement gains a real check in Half 2 or stays structural, and which side owns it — genuinely open; two plausible owners named, neither chosen.
6. What `SkillTrustState` becomes given three overlapping vocabularies — three alternatives listed, none chosen, with a rule-12 justification for forcing an explicit one-directional decision.
7. Whether populating `trust_state` from the store changes `SkillCatalog.fingerprint` — a concrete, verifiable hazard (line 121 does hash it today, and it is constant only by accident of `SkillTrustState` having one member). This is the sharpest question in the list and is not answered anywhere in the note.
8. Whether `SUPERSEDED` records its successor — deliberately not committed to, with the FK consequence (successor must be registered first) named.

None of the 8 are silently answered elsewhere in the note, and all 8 are decisions a Half-1 implementation would otherwise have to guess at. No padding found. No hand-waving found: every mechanism is named against a real existing symbol (`TaskStore`, `MutationResult`, `initial_transition_from_gate_report`, `SkillGateReport.to_dict()`, `json_valid`, `RAISE(ABORT, ...)`), and the pieces that are undecided are visibly parked in the questions list rather than asserted.

## 6. Findings

No blocking findings. Two non-blocking nits, neither of which changes any conclusion in the note:

- **N1 (cosmetic count).** The note describes `runtime/state/schema.sql` as "734 lines, 30+ tables". The line count is right (734), but `grep -c "CREATE TABLE" runtime/state/schema.sql` returns 29, not 30 or more. The load-bearing half of that sentence — that none of those tables is a Skill table — is verified correct.
- **N2 (phrasing, and a small omission worth carrying into Half 2).** The note calls `runtime/trust.py` "itself another unwired pure mapping". Read strictly, the antecedent is the `_SKILL_LIFECYCLE_STATE_TO_MEMORY_TRUST_CLASS` / `skill_lifecycle_trust_class()` pair, and that is accurate — `grep -rn "skill_lifecycle_trust_class"` finds only `runtime/trust.py` and `tests/test_trust.py`. But the module as a whole is *not* unwired: `runtime/context_builder.py:13-18` imports `skill_trust_class` and `operational_learning_trust_class` from it, and `context_builder.py:252,261` already projects `entry.provenance.trust_state` into the context plan as both a `trust_class` and a raw `trust_state` value. That matters for open question 6 (what `SkillTrustState` becomes) and question 7 (fingerprint sensitivity), because `runtime/context_builder.py` is a live consumer that would observe any change to `trust_state`, and the note's question list does not name it. Worth adding to the Half-2 task's list of affected call sites; not a reason to hold this design note.

## 7. Applicable review lenses

- `[x]` Functional / acceptance — diff is exactly the one design note; every Finding-section claim independently re-verified against source; the cited precedent pattern verified to exist as described.
- `[x]` Scope / non-goals — no second authority database, no Skill bodies in SQLite, no knowledge graph, no daemon; Half-1/Half-2 boundary explicitly drawn and SEC4's capability-manifest half explicitly excluded from both.
- `[x]` Authority / permission boundary — no roadmap status row changed; the note states plainly that it does not complete SEC4 or 6.10; the design preserves the "nothing reaches APPROVED without an explicit actor-bearing decision row" invariant across the persistence boundary, including by refusing a caller-supplied starting state in `record_skill_lifecycle_subject()`.
- `[x]` Destructive / data-loss — zero runtime and zero test changes; nothing in this PR can alter running behavior. The proposed tables are append-only and trigger-locked by design, and the note explicitly forbids deleting rows.
- `[ ]` Security / trust boundary at implementation depth — not applicable yet; no runtime code ships here, so there is no storage or gating behavior to assess for a fail-open defect. That belongs to the Half-1 and Half-2 reviews.

## 8. Evidence checked

- `git fetch origin sec4-skill-lifecycle-design && git checkout -B sec4-skill-lifecycle-design origin/sec4-skill-lifecycle-design`; `git rev-parse HEAD` = `71d1357eb824c075355902257b7d7ed14d3adaa5`.
- `git diff origin/main...HEAD --stat` — 1 file, 320 insertions, 0 deletions. `git log origin/main..HEAD --oneline` — 1 commit.
- `git diff origin/main...HEAD -- work/roadmaps/CAPABILITY_CHECKLIST.md` — empty.
- Read in full: `runtime/skills/lifecycle.py` (161 lines), `tests/test_skill_lifecycle.py` (184 lines), the design note under review (320 lines).
- Read: `runtime/skills/catalog.py` (`SkillTrustState`, `SkillProvenance`, `SkillCatalogEntry.catalog_key`, `SkillCatalog.__post_init__` fingerprint), `runtime/state/schema.sql` lines 635-734, `runtime/state/operational_learning_storage.py` (`_compose`, `get_operational_lesson`, `promote_operational_lesson`), `runtime/state/store.py` (mixin list), `runtime/state/common.py` (`MutationResult`), `runtime/trust.py` (all four mapping/function pairs), `runtime/skills/__init__.py` (re-exports and `__all__`), `runtime/context_builder.py` (trust imports and trust_state projection).
- `grep -in "skill" runtime/state/schema.sql` — zero hits.
- `grep -rn "skills.lifecycle\|SkillLifecycleState\|initial_transition_from_gate_report" --include=*.py .` — module, `runtime/skills/__init__.py`, `runtime/trust.py`, and two test files only.
- `grep -rn "skill_lifecycle_trust_class" --include=*.py .` — `runtime/trust.py` and `tests/test_trust.py` only.
- `grep -rn "trust_state" --include=*.py .` — no assignment site outside the dataclass default.
- `grep -c "CREATE TABLE" runtime/state/schema.sql` — 29.
- Read: `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` section 7 (7.1-7.10) in full; `work/roadmaps/agent-harness-capabilities/02-procedural-knowledge-and-skills.md` sections 6.2, 6.3, and 7 in full.
- Confirmed `work/roadmaps/CAPABILITY_CHECKLIST.md` line 60 (SEC4) and line 119 (6.10) both read `IN PROGRESS` and are unmodified by this PR.
- Confirmed the referenced files exist: `work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md`, `work/tasks/operational-learning-authority-design-wave4.md`, `work/tasks/skill-trust-lifecycle-wave11.md`.
- Structure compared heading-by-heading against `work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md`.

## 9. Reviewer limits

- Missing context/evidence: none. Every claim in scope was checkable against code in this worktree.
- Not assessed: whether the Half-1 schema as sketched would pass SQLite parsing verbatim (no DDL is shipped in this PR, so there is nothing executable to test); and the practical `BUNDLED`-Skill re-approval churn raised by the note's own open question 1, which needs operator input rather than code inspection.
- New requirements discovered: none beyond nit N2's suggestion to add `runtime/context_builder.py` to the Half-2 affected-call-site list.
