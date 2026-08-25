reviewer: /root/pr161_reviewer
head_sha: 50c3aaef3c0829cdaa4d181027520afd613a4f74
independent: true
summary: APPROVED — PR #161 adds exactly one design-only note (work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md) for SEC3/6.4, verified against a fresh independent grep/read of runtime/harness/hooks.py, runtime/harness/service.py, runtime/policy/harness_guard.py, and runtime/skills/gate.py; all of its Finding-section claims are factually accurate, its proposed two-boolean context contract plus a single new HookEnforcement member does not smuggle in a policy engine/second authority DB/daemon/action registry per roadmap section 7, and it matches the required Finding/Decision/Non-goals/Behavior-questions/Roadmap-impact structure of the pr154/pr160-pattern reference note with no hand-waving.

# Review: PR #161 SEC3/6.4 destructive-external-action Hook guard design

- Note reviewed: `work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md`
- Reference structure: `work/notes/2026-08-21-rns-harness-validation-callsite-design.md`
- Reviewer: `/root/pr161_reviewer`
- Verdict: `APPROVED`

## 1. Diff scope

`git diff origin/main...50c3aaef3c0829cdaa4d181027520afd613a4f74 --stat` shows exactly one file changed:

```
work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md | 186 +++++++++++++++++++++
1 file changed, 186 insertions(+)
```

No file under `runtime/`, `tests/`, or any roadmap status file (`work/roadmaps/CAPABILITY_CHECKLIST.md`, `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md`) is touched. Confirmed separately that `work/roadmaps/CAPABILITY_CHECKLIST.md`'s SEC3 (line 59) and 6.4 (line 113) rows both still read `IN PROGRESS` in this worktree's checkout and are unmodified by this PR — no roadmap item is marked DONE.

## 2. Groundedness — independently re-verified every Finding-section claim

- `grep -rn "BEFORE_DESTRUCTIVE_ACTION\|BEFORE_EXTERNAL_ACTION"` across the whole repo (not just runtime/) returns: the enum declaration itself in `runtime/harness/hooks.py:18-19`, generic `HookRegistry` ordering/deny tests in `tests/test_harness_hooks.py` that use `BEFORE_EXTERNAL_ACTION` as an arbitrary event name (not a real guard), and prose references in prior work/notes and work/tasks files (all *about* the same known gap, not code). No production call site fires either event — matches the note's claim exactly.
- Read `runtime/harness/hooks.py`: `class HookEnforcement(str, Enum)` (line 48) has exactly one member, `CANONICAL_RUN = "CANONICAL_RUN"` (line 51). Matches.
- Read `runtime/harness/service.py`: `_require_canonical_enforcement()` (line 64) is the only place that calls `self.hooks.has_enforcement(event, HookEnforcement.CANONICAL_RUN)` and is invoked before `start`/`send`/`resume`/`stop`. It only ever checks for `CANONICAL_RUN`. Matches.
- `grep -rln "ToolSpec\|ToolDeclaration\|action_type\|ActionType" runtime/` returns nothing. Matches the note's "no action/tool declaration registry exists" claim.
- Read `runtime/skills/gate.py`: `_DESTRUCTIVE_RE` (line 84) is a regex (`rm -rf`, `DROP TABLE/DATABASE`) applied to Skill source `text` inside a Skill-content linting function that appends `DESTRUCTIVE_OPERATION` findings at `SkillGateSeverity.REVIEW`. It operates on static Skill content, not on a live harness operation about to execute — the note's characterization ("static text linting of Skill content... not a runtime classification of an action about to execute... cannot be reused for SEC3") is accurate.
- Read `runtime/policy/harness_guard.py` in full: `CanonicalRunGuard._extract_binding()` (line 44) reads `context.get("binding")` as an explicit `Mapping`, denies with `BINDING_REQUIRED` if absent — this is exactly the "explicit context field, not inferred" pattern the note cites as precedent for `context["destructive"]`/`context["external"]`. `register_canonical_run_guards()` registers `FAIL_CLOSED` (raises if the guard's `HookSpec.failure_policy` isn't `FAIL_CLOSED`, per `_register_enforcement` at hooks.py:206) and `HookSideEffect.READ_ONLY` (harness_guard.py:207). The note's characterization ("reads explicit context['binding'], FAIL_CLOSED, READ_ONLY") is accurate.

No factually wrong grep or code claim found anywhere in the Finding section.

## 3. Minimalism per roadmap section 7 non-goals

Read `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` section 7 (7.1–7.10, all "Rejected by default"). Cross-checked the proposed design against the specific rejected items it touches:

- 7.1 (large persistent daemon) — note's own Non-goals: "No daemon, no background scanning of pending actions, no always-on process." Consistent.
- 7.2 (second task/session authority database) — note's own Non-goals explicitly cites 7.2 by name and states the guard is "a fixed deterministic function of two booleans plus existing task/binding authority state — not a second authority database." The proposed mechanism reads existing binding/task authority state (mirroring `CanonicalRunGuard`) rather than creating new storage. Consistent.
- 7.6/7.7 (knowledge graph / semantic retrieval by default) — note's own Non-goals cites both by number and explicitly rejects a "queryable catalog" or "giant knowledge graph." Consistent — classification stays two caller-declared booleans on the existing frozen Hook context mapping (`_freeze_hook_value` already supports booleans, confirmed at hooks.py:60), not a new data structure.
- No policy engine or rules DSL is proposed — the "task policy" lookup is explicitly deferred to the implementation task as an open question (see section 5 below), not built here.
- The one new construct, `HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION`, is a single enum member added next to the existing `CANONICAL_RUN`, reusing `HookRegistry._register_enforcement()`, `has_enforcement()`, and `run()` verbatim (confirmed these are already generic over `HookEnforcement`, not `CANONICAL_RUN`-specific, at hooks.py:180-208). No registry-internals change proposed or needed.

No scope creep beyond a two-boolean context contract, one enum member, and a guard class shaped like the existing `CanonicalRunGuard`.

## 4. Rigor/style match against the pr154/pr160-pattern reference note

Compared section-by-section against `work/notes/2026-08-21-rns-harness-validation-callsite-design.md`:

| Reference note section | PR #161 note equivalent | Present? |
|---|---|---|
| `## Finding` (grounded current-state re-verification) | `## Finding` | Yes |
| `## Decision: ...` | `## Decision: context-supplied classification...` | Yes |
| Non-goals (explicit heading) | `## Non-goals` (explicit heading, 6 bullets, each tied to a named roadmap rejection or a concrete mechanism it refuses to add) | Yes |
| `## Behavior questions the implementation task must answer` | Same heading verbatim, 6 questions | Yes |
| `## Roadmap impact` | `## Roadmap impact` | Yes |

The reference note additionally has a `## Bounded follow-up implementation` section (allowed/must-not-do lists for the next task) that PR #161's note does not have as a separate heading — but the equivalent content is folded into `## Non-goals` (bullet 4: "No wiring of this guard into a real production call site in this task... The first real call site... is a separate, bounded follow-up task") and `## Roadmap impact` (names the two-step split explicitly, referencing PR #160 by number as the precedent). This is a minor structural difference, not a missing category of content — not a blocking finding.

Checked whether the six open questions in "Behavior questions the implementation task must answer" are genuinely open (not silently answered elsewhere in the same note) and genuinely implementation-relevant:
1. Source of "task policy" for ALLOW/DENY/REQUIRE_APPROVAL — genuinely undecided; the Decision section explicitly says "is an open question below, not decided here."
2. Which call sites get classified first, and who sets the flags — genuinely undecided; no call site is named as committed, only "e.g." examples.
3. One combined guard vs. two split guards — the note picks one for the design but explicitly flags this as needing confirmation once a real policy source exists; not padding, it's a real fork in the implementation.
4. Missing-key behavior — a recommendation ("fail closed... is the safer default") is given but the note explicitly still requires the implementation task to "decide and test it explicitly," consistent with question 1's non-decision.
5. Evidence-recording location — genuinely unaddressed elsewhere in the note.
6. Whether an approval mechanism already exists for `REQUIRE_APPROVAL` — genuinely unaddressed, and correctly flagged as a possible blocker requiring DENY-only as a fallback.

None of the six are answered elsewhere in the note (no contradiction or redundant restatement found), and all six are concrete decisions a real implementation PR would otherwise have to guess at. No padding found.

## 5. Internal consistency / hand-waving check

The proposed mechanism cites real, currently-existing names throughout rather than deferring to an unnamed future policy:
- `context["destructive"]` / `context["external"]` as two new boolean keys on the existing frozen Hook context mapping (`_freeze_hook_value`, hooks.py:57-75, already accepts bool).
- `HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION` as a literal new enum member next to `CANONICAL_RUN` (hooks.py:48-51).
- `DestructiveExternalActionGuard` explicitly modeled on the real `CanonicalRunGuard` class (harness_guard.py:27), same `FAIL_CLOSED`/`READ_ONLY` shape, same `_register_enforcement()`/`has_enforcement()`/`run()` machinery (hooks.py:183-227 and service.py:64-76) reused unchanged.
- The one genuinely unresolved piece — where "task policy" for ALLOW vs DENY vs REQUIRE_APPROVAL comes from — is not glossed over with a phrase like "some policy will decide." It is explicitly named as an open question in section "Behavior questions the implementation task must answer" (question 1), with the note stating up front it "deliberately does not invent a new field name or storage location for that authority." This is the correct way to flag an undecided piece: named, bounded, and pushed to the implementation task rather than asserted as already solved.

No hand-waving found. The mechanism concretely plugs into existing code by name at every point except the one piece it explicitly, visibly defers.

## Applicable review lenses

- `[x]` Functional / acceptance — confirmed diff is exactly the one design note, confirmed all Finding-section factual claims via independent grep/read of the actual code, confirmed structural parity with the reference note.
- `[x]` Scope / non-goals — confirmed no policy engine, second authority database, daemon, or action registry is proposed; confirmed roadmap section 7 items are correctly cited and respected.
- `[ ]` Security / trust boundary — not applicable at this stage; this PR ships no runtime code, so there is no guard behavior yet to assess for a fail-open/fail-closed defect. That assessment belongs to the eventual implementation-task review.
- `[x]` Destructive / data-loss — confirmed zero runtime/tests changes; nothing in this PR can affect running behavior.
- `[x]` Authority / permission boundary — confirmed no roadmap status row is changed to DONE and no claim of completed work beyond "design complete" appears anywhere in the note.

## Findings

No blocking findings.

## Evidence checked

- `git fetch origin && git checkout 50c3aaef3c0829cdaa4d181027520afd613a4f74` — HEAD verified via `git rev-parse HEAD` to be `50c3aaef3c0829cdaa4d181027520afd613a4f74`.
- `git diff origin/main...50c3aaef3c0829cdaa4d181027520afd613a4f74 --stat` — 1 file, 186 insertions, 0 deletions.
- `grep -rn "BEFORE_DESTRUCTIVE_ACTION\|BEFORE_EXTERNAL_ACTION" .` — matches only the enum declaration, generic registry tests, and prose in prior notes/roadmap files describing the same known gap; no production call site.
- `grep -rln "ToolSpec\|ToolDeclaration\|action_type\|ActionType" runtime/` — zero hits.
- Read in full: `runtime/harness/hooks.py` (HookEnforcement, HookRegistry, `_register_enforcement`), `runtime/harness/service.py` (`_require_canonical_enforcement` and its four call sites), `runtime/policy/harness_guard.py` (`CanonicalRunGuard` in full), `runtime/skills/gate.py` (`_DESTRUCTIVE_RE` and its use site).
- Read in full: `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` section 7 (7.1-7.10).
- Read in full: `work/notes/2026-08-21-rns-harness-validation-callsite-design.md` (reference structure) and the new note under review.
- Confirmed `work/roadmaps/CAPABILITY_CHECKLIST.md` SEC3/6.4 rows unmodified and still `IN PROGRESS`.

## Reviewer limits

- Missing context/evidence: none.
- New requirements discovered: none.
