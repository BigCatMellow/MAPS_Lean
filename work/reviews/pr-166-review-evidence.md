reviewer: agent-ac105c6ef1fd943f3 (independent PR #166 reviewer; did not author the design note and made no change to it)
head_sha: f6ee2edf478e6966c3d2488bc0ba577ffa0fa25b
independent: true
summary: CHANGES_REQUESTED — PR #166 is correctly docs-only (one added file, 340 lines, nothing under runtime/ or tests/), its §1 claims about `runtime/trust.py`, the module docstring quote, PR #148's selected seam, the absence of any Hook path or non-`context_builder` consumer of `trust_class`, and every cited line number all check out verbatim against the reviewed tree, the roadmap §7 non-goals are respected, and the note matches the SEC3 note's rigor shape (Finding / Decision / Non-goals / open behavior questions / roadmap impact / fail-closed posture); but the note's centerpiece behavior change — §2b.1's "the gate re-derives the class from the item's own status/reason field", the one claimed allow/deny difference — is not implementable against the actual data shape, because `project_applicable_lessons()` (runtime/operational_learning.py:413-422) builds each projected item as exactly `lesson_id`/`claim`/`source_kind`/`source_refs`/`promotion_decision_ref`/`authority` and carries no status or reason forward, and that same function already routes RETIRED/CANDIDATE/SUPERSEDED records into `withheld` at lines 381-386 before `_lesson_guidance()` ever sees them, so §1d's stated threat ("a hand-edited or poisoned lesson store") is already handled upstream and the residual case (a projection bug) is precisely the case the proposed gate cannot detect; relatedly §4d's open question is answerable from the same file the note claims to have verified against (withheld items are `{"lesson_id", "reason"}` only, with no lesson text at line 410), and that answer inverts §4a's own stated tie-break, which leans DENY on the premise that the withheld bucket carries lesson text — so the note's departure from #148's WITHHOLD default rests on a premise its own cited code contradicts.

# Review: PR #166 — memory trust enforcement gate design note (roadmap 6.22)

- Branch reviewed: `memory-trust-gate-design`, current head `f6ee2ed` ("Design memory trust enforcement gate on the Context Builder seam (roadmap 6.22)"), rebased onto `origin/main` at `65e140b`.
- Reviewed in an isolated worktree; after `git fetch origin memory-trust-gate-design` and `git checkout -B memory-trust-gate-design origin/memory-trust-gate-design`, `git rev-parse HEAD` printed `f6ee2edf478e6966c3d2488bc0ba577ffa0fa25b`.
- Artifact under review: `work/notes/2026-08-25-memory-trust-enforcement-gate-design.md`, read in full.
- Prior decision treated as source of truth for the seam: `work/notes/2026-08-21-memory-trust-enforcement-design.md` (PR #148), read in full.
- Rigor reference: `work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md`.
- Verdict: `CHANGES_REQUESTED`
- I did not author the note and did not modify it, `runtime/`, `tests/`, or any roadmap or checklist file. The only file this review adds is this one.

## 1. Diff scope — PASS

```
$ git diff origin/main...HEAD --stat
 ...6-08-25-memory-trust-enforcement-gate-design.md | 340 +++++++++++++++++++++
 1 file changed, 340 insertions(+)
```

Exactly one added file under `work/notes/`. No `runtime/`, no `tests/`, no roadmap or checklist file. The hard-fail condition is not triggered.

The note's own header says it was verified against `origin/main@8923adb`. That commit is an ancestor of the reviewed head, and the only main commit between `8923adb` and the rebase base `65e140b` is `65e140b` itself ("Add SEC4/6.10 Skill lifecycle persistence design note (design-only) (#167)"), which is docs-only:

```
$ git log --oneline 8923adb..65e140b -- runtime/context_builder.py runtime/trust.py
(empty)
```

So no line number or code claim in the note went stale across the rebase. Every check below was run against the reviewed tree, not against `8923adb`.

## 2. §1a — vocabulary and docstring quote — PASS

`runtime/trust.py:49-60` declares `MemoryTrustClass` with exactly the eleven members the note lists, in the order the note lists them (`UNTRUSTED_INPUT`, `OBSERVATION`, `CLAIM`, `CANDIDATE_LESSON`, `REVIEWED_GUIDANCE`, `APPROVED_SKILL`, `ACTIVE_INSTRUCTION`, `CANONICAL_POLICY`, `SUPERSEDED`, `RETIRED`, `QUARANTINED`), with the docstring the note quotes. The three read-only mappings exist as named (`skill_trust_class` at line 82, `skill_lifecycle_trust_class` at 127, `operational_learning_trust_class` at 166), as does `TrustClassError`.

The block quote in §1a is verbatim from the module docstring, including "it is NOT wired into any decision-gating code path" and the parenthetical example. Nothing is elided in a way that changes its meaning.

## 3. §1b — PR #148's seam — PASS

`gh pr view 148 --json title,state,mergedAt,headRefName` returns title "Design memory trust enforcement seam", state `MERGED`, `mergedAt` `2026-08-21T11:23:37Z`, `headRefName` `rns-harness-callsite-task` — all four details as the note states.

The quoted "Decision" paragraph matches `work/notes/2026-08-21-memory-trust-enforcement-design.md` line 27 onward verbatim, and the seam the note attributes to #148 (Context Builder memory-like evidence: operational-learning `guidance` / `withheld_guidance`, plus Skill selection metadata under `skills`) is exactly what that section says. No drift. The note does not re-open the seam choice.

The "deliberately not Hook-based" characterization also checks out:

```
$ grep -in "hook" runtime/context_builder.py
(no matches, exit 1)

$ grep -rn "build_context_plan" --include=*.py . | grep -v ^./tests/
runtime/cli.py:9, runtime/cli.py:333
runtime/context_builder.py:280   (the definition)
runtime/flow_start.py:7, runtime/flow_start.py:80
```

`runtime/cli.py:333` and `runtime/flow_start.py:80` are the only production call sites, both plain function calls, exactly as claimed. The SEC3 comparison is also accurate: `runtime/policy/destructive_action_guard.py` exists and references `HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION` (declared at `runtime/harness/hooks.py:52`).

## 4. §1c — nothing reads `trust_class` for a decision — PASS

Grepped repo-wide, not only `runtime/`:

- `grep -rn "trust_class" --include=*.py .` outside `runtime/context_builder.py` returns only the three producer definitions in `runtime/trust.py` plus assertions in `tests/test_trust.py` and `tests/test_context_builder.py`. The test references are assertions about emitted values, not decision code.
- `grep -rn "MemoryTrustClass" --include=*.py .` outside `runtime/trust.py`, `runtime/context_builder.py`, and `tests/` matches only two docstring lines in `runtime/incident_taxonomy.py` (14, 26) — prose, no code path.
- No `.json`, `.yaml`, `.yml`, or `.sh` file outside `legacy/` mentions `trust_class`.

Inside `runtime/context_builder.py`, the only read of a stamped `trust_class` is the coverage computation at lines 399-403, and the quoted snippet in the note is character-for-character the code there. The result is surfaced under `coverage` at line 444. It is a presence check; no branch consumes its value. The note's characterization ("observability, not a gate") is correct.

## 5. Cited line numbers — PASS

Each cited location was opened and matched:

- `_lesson_guidance()` at 125-165 — definition at 125, `return guidance, withheld` at 165.
- The unconditional stamp `trust_class=operational_learning_trust_class("ACTIVE").value` at 155.
- `_withheld_lesson_with_trust_class()` at 168-178, with the `CANDIDATE_NOT_PROMOTED`/`RETIRED`/`SUPERSEDED` reason mapping and `stale_trust_metadata` for `EXPIRED`/`REVIEW_DUE`, as described.
- `_select_skills()` at 216-272, with `skill_trust_class(entry.provenance.trust_state).value` at 252 (guarded by `except TrustClassError: continue`) and the hardcoded `"budget_class": "SHOULD_LOAD"` at 269.
- `build_context_plan()`'s memory-like block at 393-403.

§2b.2's supporting claims also hold: `SkillTrustState` has only `UNASSESSED`, which maps to `OBSERVATION`, so every matched Skill today is simultaneously `OBSERVATION` and `SHOULD_LOAD`. §4c is accurate about the test impact — `tests/test_context_builder.py:202` (`test_matching_skill_budget_class_is_should_load`) and line 522 are the assertions a demotion to `ON_DEMAND` would break.

## 6. Non-goals and rigor shape — PASS

§3 forbids a policy engine or DSL or configurable threshold, a second authority database or persisted trust store or lineage graph, knowledge-graph or inferred or LLM classification, and any daemon or background process — matching roadmap §7 and #148's bounds. Nothing elsewhere in the note quietly reintroduces one: the admission table is specified as a fixed dict literal, the class is read only through the existing read-only mappings, and §3 additionally rules out new Hook plumbing and `HarnessService` routing, which is consistent with §1b.

Structurally the note carries every element the SEC3 note has (`Finding`, a `Decision`-equivalent §2, `Non-goals` §3, `Behavior questions the implementation task must answer` as §4, `Roadmap impact` §5) plus an explicit fail-closed posture section (§2d) that correctly scopes fail-closed to "this optional memory item does not enter the load set", not "the plan fails". §5's refusal to flip 6.22 to `DONE`, and §3's instruction to narrow rather than delete the checklist's "Still missing" clause, are appropriately conservative.

## 7. Finding A (blocking) — §2b.1's mechanism has no data to read

§1d asserts the defect as: `_lesson_guidance()` stamps `REVIEWED_GUIDANCE` on every item in `projection["projected"]` unconditionally, "the item's own `status` field is never consulted at stamp time". The first half is literally true (lines 152-158 apply the stamp with no condition). The second half is misleading, and §2b.1 then builds the note's single most important claim on it:

> "The gate re-derives the class from the item's *own* status/reason field via the existing `operational_learning_trust_class()` mapping rather than accepting the unconditional `"ACTIVE"` stamp at line 155. A projected lesson whose own status says `RETIRED` maps to `RETIRED` → `WITHHOLD` ... That is the allow/deny difference."

A projected item has no status field to re-derive from. `project_applicable_lessons()` constructs each projected item at `runtime/operational_learning.py:413-422` with exactly six keys — `lesson_id`, `claim`, `source_kind`, `source_refs`, `promotion_decision_ref`, `authority` — and the record's `status` is consumed and discarded during projection. `operational_learning_trust_class()` maps a status string; there is no status string on the item to give it.

Worse for the motivating story, the routing the gate proposes to add already happens one layer up. `runtime/operational_learning.py:381-386` sends any record whose status is `RETIRED` or `CANDIDATE`, or which has a non-null `superseded_by`, into `withheld` with a reason before `projected` is built at all — after `validate_lesson_record()` has normalized it. So a "hand-edited or poisoned lesson store", one of the two threats §1d names, does not reach the projected bucket by that route; it is status-routed like any other record. The remaining threat §1d names is a projection bug, and that is exactly the case the proposed gate cannot catch, because the field it would consult is one the buggy projection did not emit.

The note is therefore describing behavior change #1 — its only claimed allow/deny difference on the guidance path — as though the input were available when it is not. Making §2b.1 real requires `project_applicable_lessons()` to carry the record's status (or the derived reason) onto projected items, which is a change to a system of record's projection contract, outside the #148 seam, and in tension with §3's "no changes to ... operational-learning statuses as systems of record" posture. That choice is material to scope and is not surfaced anywhere in the note — not in §2b, not in §2c's plug-in list, not as an open question in §4.

What the note should do instead of being fixed by me: either narrow §1d and §2b.1 to what is actually reachable (the laundering risk is real, but its live surface is the *stamp* asserting `REVIEWED_GUIDANCE` for items whose provenance the gate cannot independently check — not a status disagreement the gate can detect), or state plainly that the design requires an upstream shape change and add it to §4 as an open scope question with its own justification. Behavior change #2 (`OBSERVATION` Skills demoted from `SHOULD_LOAD`) and #3 (drop `QUARANTINED`/`UNTRUSTED_INPUT`) are unaffected by this finding and are both grounded in code as written; #2 in particular is a genuine, currently-visible enforcement gain.

## 8. Finding B (blocking) — §4a's tie-break rests on a premise the code contradicts

§4a chooses `DENY` over #148's stated `WITHHOLD` default for undeterminable trust class, and gives this tie-break:

> "The tie-break question is whether a withheld-but-named unknown item is itself a poisoning surface; if the withheld bucket carries the lesson *text*, it is, and `DENY` wins."

§4d then defers the antecedent to the implementation: "The implementation must read what `project_applicable_lessons()`'s withheld items actually contain". That question is already answered in the same function the note cites elsewhere. `runtime/operational_learning.py:410` appends withheld items as:

```
withheld.append({"lesson_id": record["lesson_id"], "reason": reason})
```

Two keys. No `claim`, no lesson text of any kind. `_withheld_lesson_with_trust_class()` then adds only `trust_class` and possibly `stale_trust_metadata`, and `build_context_plan()` adds `budget_class`. The withheld bucket is already a pure reference, exactly the "safe" shape §2a's `WITHHOLD` outcome needs.

By the note's own tie-break rule, then, `DENY` does not win: the withheld bucket is not a poisoning surface, so the note's departure from #148's explicit fail-closed rule ("Missing trust class on memory-like evidence: mark item withheld, or omit it if no safe withheld bucket exists" — a safe withheld bucket demonstrably exists) is unsupported. §2a's table row for missing/unparseable, and §4b's `DENY` for `UNTRUSTED_INPUT`/`QUARANTINED`, inherit the same problem, and §4b's proposed remedy ("a separate `denied_memory` list that carries identifiers **without** carrying the untrusted text") describes a structure the existing withheld bucket already is.

To be fair to the note, it does honestly surface that it is departing from #148 here and does not hide the conflict — §4a names #148's weaker rule explicitly and says the implementation must pick and justify one. That candor is why this is a correction rather than a misrepresentation. But leaving §4d open when it is answerable in one grep, and then leaning the default the opposite way on the unverified branch of that question, falls below the rigor bar the SEC3 note sets, where every open question is genuinely undecidable from current code rather than merely unchecked.

## 9. Non-blocking observations

- §2a describes the admission rule as "a single ordering over the enum — the four classes at or above `REVIEWED_GUIDANCE` load". That is not the enum's declaration order: `SUPERSEDED`, `RETIRED`, and `QUARANTINED` are declared *after* `CANONICAL_POLICY` yet do not load. The table is unambiguous and normative, so this is prose imprecision only, but an implementer told to encode "an ordering over the enum" could get it wrong; better to say the table is the rule.
- §2a's admission table is otherwise a faithful derivation of #148's class/action table. One soft edge: #148 admits `ACTIVE_INSTRUCTION` "only if a separate Skill loader task proves the source active", while §2a grants it unconditional `LOAD`. No current mapping produces `ACTIVE_INSTRUCTION`, so nothing is reachable today, but the conditional in #148 is dropped without comment.
- §1d's second bullet and §2b.2 are correct and are, in my reading, the strongest part of the note: the `OBSERVATION`-plus-`SHOULD_LOAD` combination is a real, presently-emitted contradiction of #148's table that nothing enforces, and demoting it is a concrete decision made from `MemoryTrustClass`. If §1d were rebuilt around that case alone, the note would stand.

## 10. Test suite

The PR is docs-only, so the suite must pass untouched. Run as a blocking foreground call with the CI command from `.github/workflows/runtime-stack-tests.yml:54`:

```
$ python3 -m unittest discover -s tests
----------------------------------------------------------------------
Ran 806 tests in 981.794s

OK (skipped=6)
```

806 tests, `OK (skipped=6)`, process exit code 0, at head `f6ee2ed` with no working-tree modification other than this evidence file. The suite is unaffected, as expected for a docs-only PR.

Note that `python3 -m unittest discover -s tests -t .` fails at load with `ImportError: Start directory is not importable` because `tests/` has no `__init__.py`; the CI form (`-s tests`, no `-t`) is the one that works.

`scripts/check_review_evidence.py` takes a PR number as its sole positional argument (`--help` is rejected with "pr_number must be numeric"), and it walks HEAD backward past trailing evidence-only commits, so `head_sha` above is set to `f6ee2ed`, the commit that adds the design note, not to the SHA of the commit adding this file.

## 11. What would clear this review

1. §1d and §2b.1 reconciled with the actual projected-item shape — either narrowed to what the gate can really observe, or explicitly acknowledging that an upstream change to `project_applicable_lessons()`'s output is required, with that scope expansion argued rather than implied.
2. §4d closed with the answer already in the code (withheld items carry no lesson text), and §4a's default re-decided in light of it — which, on the note's own stated tie-break, points back to #148's `WITHHOLD`.

Nothing else in the note needs to change for me to approve it. The diff scope, the §1 verification, the non-goals, and the roadmap posture are all sound.
