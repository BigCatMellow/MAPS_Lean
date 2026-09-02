# PR #251 review evidence — SEC4 Half 3 slice 2 scoping note

Independent verification-only review by maps-lean-gela (vame authored; gela is
independent of Half 3 — authored only the SEC4 capability-manifest thread
#215/#219, not the authorized-operator registry). Design-only note, 1 file
(`work/notes/2026-09-01-sec4-half3-slice2-scoping.md`), no runtime/schema/status
change.

## Checks (against origin/main 070dc65 + the #245 branch @ d86c6f2)

### 1. Does 2a need no schema + no operator decision? — YES (schema), DEFENSIBLE (decision)

- No schema / no new store primitive. `runtime/cli.py` (#245 branch)
  `_SKILL_TRANSITION_TARGETS` already maps all four verbs
  (`approve`→APPROVED, `activate`→ACTIVE, `retire`→RETIRED,
  `supersede`→SUPERSEDED); the registry gate at cli.py:569-573 is `approve`-only
  today. 2a is a pure `_dispatch_skill` edit — extend that guard over the verb
  family, no `record_skill_lifecycle_transition` signature change, CLI-side per
  the parent design note Q B3 ("CLI-side, so the store stays a faithful
  recorder").
- `runtime/skills/lifecycle.py` `_ACTOR_REQUIRED_TRANSITIONS` = only the two
  `*→APPROVED` edges; the note correctly frames the registry check as an
  independent CLI-layer authority gate, not a restatement of that graph rule.
- No operator decision — DEFENSIBLE. 2a is within-domain, opt-in-by-data,
  default-off, tightening-only, so it does not rise to an operator decision.
  **Non-blocking framing caveat:** 2a is a *new* increment proposed by this
  note, not a parent-note deferred item — only 2b/2d/2e trace to Q B4/Q B5's
  explicit "not in slice 1" list, and 2c to Q B2's third undecided bullet. §2's
  "Deferred surface — status of each candidate" framing slightly overstates 2a's
  pedigree. Recommend one clarifying sentence ("this extends beyond Q B5's
  approve-only slice, justified by Q B4's one-consistent-way principle"). Does
  not change the recommendation or the slice.

### 2. Is 2c correctly identified as operator-only and NOT reviewer-resolved? — YES

§2c matches parent note Q B2's third undecided bullet verbatim (empty-registry
= "identity checks disabled" (= today) vs "all approvals blocked" hard cutover).
The note NAMES it, does NOT implement it, and offers a
`--enforce-operator-identity` middle option *to the operator* rather than
choosing it. Rules 9 and 11 respected.

### 3. Are the deferrals reasonable? — YES

- 2b (`promote_operational_lesson`): `/usr/bin/grep -rn` → mixin definition +
  one docstring mention only, zero production callers. Fold in when it gets an
  entrypoint.
- 2d (rotation/re-auth after revoke): needs a schema decision + an operator nod;
  Q B5 explicitly excludes expiry/rotation from slice 1. Own note later.
- 2e (`actor_class=OPERATOR` mapping): additive, no operator decision, but no
  consumer of an `actor_class=OPERATOR` derivation exists — zero value now.

### 4. No status flip? — YES

Header "STATUS: DESIGN ONLY. No runtime code, no schema, no checklist status
change." §3 MAY-touch limits `CAPABILITY_CHECKLIST.md` to 6.10 evidence text
only; §3 MUST NOT bars any checklist STATUS flip.

## Non-blocking observations

1. §2a "Deferred surface" framing — 2a is a new proposed increment (see check 1).
2. `activate`/`retire`/`supersede` have `--actor` optional at argparse (unlike
   `approve`'s `required=True`); the note's §3 already prefers "keep it optional
   at argparse, enforce in dispatch" and the Stop-condition covers the
   argparse-required route.
3. The note cites the #245 branch, not a SHA; the 2a implementer must re-verify
   the gate shape at whatever #245 merges as (rule 14). The resume prompt's
   "Slice 1 ... is merged" handles sequencing.

## Verdict: APPROVE

`python3 -m runtime.smoke` → exit 0.

reviewer: maps-lean-gela
head_sha: 9dc6e47125594ff00341eda92e0ebd1fe51d9937
independent: true
summary: APPROVE — verification-only review of a design-only SEC4 Half 3 slice 2 scoping note; 2a (widen the opt-in-by-data operator gate from approve to activate/retire/supersede) is verified schema-free and CLI-only against the #245 branch, 2c (empty-registry fail-closed cutover) is correctly surfaced as the one remaining operator decision and not pre-resolved, the 2b/2d/2e deferrals each have a clean individually-scoped reason, and nothing flips status; one non-blocking framing note that 2a is a newly proposed increment rather than a parent-note deferred item.
