# Review Guide

Use this guide when reviewing MAP tasks, artifacts, or code changes.

## Review Goal

Reviews protect project truth and user work. They should find concrete issues,
verify acceptance criteria, and avoid creating vague extra work.

## Verdicts

- `APPROVED` - acceptance criteria are met and no blocker or required findings remain.
- `CHANGES_REQUESTED` - required fixes are needed before approval.
- `BLOCKED` - review cannot complete because required context, files, or verification are missing.

## Severity Levels

- `BLOCKER` - unsafe, data-losing, security-sensitive, or prevents basic function.
- `REQUIRED` - must be fixed to satisfy task intent or acceptance criteria.
- `RECOMMENDED` - useful improvement, but not required for this task.
- `OPTIONAL` - polish or future consideration.

Only `BLOCKER` and `REQUIRED` findings should block approval.

## Claim Before Reviewing (TASK-199 / IDEA-0017)

Multiple agents can see the same SUBMITTED task and start a full independent
review before either one finalizes — an hcom "I'm taking this review"
message can lose the race against a broadcast, and duplicate review work
gets thrown away. Before starting substantive review work on a task, claim
it atomically:

```python
from MAP_System.db.claims import claim_review
claim_review("TASK-NNN", "your-agent-id")  # True = claimed, False = already claimed / self-review / not SUBMITTED
```

`claim_review` returns `False` in exactly four cases: the task doesn't
exist, it isn't `SUBMITTED`, the reviewer is the task owner (self-review),
or another reviewer already holds an open claim. Those are the only
meanings of `False` — any other integrity failure now raises rather than
returning quietly.

Do not read `False` as "already claimed" without checking which of the
four applies. On 2026-07-22 a reviewer got `False`, read it as
already-claimed exactly as this guide then instructed, and stood down —
but the reviews table was empty and there was no claim at all. The real
cause was an unregistered reviewer hitting a foreign-key violation that
was being flattened into that same `False` (fixed in TASK-270). If you get
`False` and the queue looks like it should be open, check
`get_open_review_claim` for an actual claimant before standing down. A
reviewer that stands down for an invisible reason leaves the submission
with nobody reviewing it.

`map_task.py approve`/`reject` best-effort releases any
open claim the acting reviewer holds, so no separate release call is
required in the normal flow. This is optional, not gated: a reviewer who
skips claiming can still approve/reject normally, and a second independent
review that reaches the terminal action first will still win cleanly (the
task's status transition itself was already atomic) — claiming just avoids
wasting the work of the reviewer who would otherwise lose that race.

## Review Process

1. Read the task file and acceptance criteria.
2. Read only the listed input and output paths first.
3. Check `shared/current-state.md` for known system issues.
4. Verify the claimed behavior with commands or file inspection when practical.
5. Write findings with file paths and concrete required actions.
6. Record approval or changes requested through the task system and event log.

## Good Findings

Good findings are specific:

- name the affected file;
- describe the observable problem;
- explain the risk;
- state what must change.

Poor findings are vague:

- "This feels wrong."
- "Improve quality."
- "Needs cleanup."
- "Consider refactoring" without a concrete risk.

## Output

Use `templates/review.md` for review artifacts.

## Risk-Tiered Review (2026-07-17)

Not every change needs the full pipeline (independent review +
reviewer-reproduced evidence + standalone release checklist). Applying
identical ceremony regardless of risk is itself a cost — an independent
process audit of ClearFront found 89 MAP events and 60 artifacts
generated across 8 released tasks, because a 78-line zero-dependency
file move went through the same process as a security-critical bundle
extractor. Calibrate the process weight to the risk tier instead:

- **High risk** — extraction/security-sensitive code, rule/state/engine
  logic changes, hidden-information or persistence surfaces,
  network-facing components, release packaging. Full pipeline: explicit
  acceptance criteria, independent review by a different core agent who
  reproduces evidence rather than only reading the report, standalone
  release checklist.
- **Medium risk** — cross-module refactors, substantial UI/interaction
  changes. Automated parity evidence required; one review at the
  change's completion rather than per intermediate step.
- **Low risk** — mechanical moves with no behavior change, content/art/
  styling, documentation. Owner verifies directly; batch several
  low-risk changes behind one review instead of a full cycle per
  change.

Pick the tier from the change's actual risk, not its file count or how
long it took to build. A worked example and the reasoning behind
choosing tiers lives in `Projects/ClearFront/shared/decisions.md`

**Release checklist weight follows this same tier mechanically** —
`scripts/release_task.py`'s `classify_release()` (TASK-288/DEC-032) skips the
standalone five-item checklist for a Low-risk release automatically, requiring
only the Emergence-capture-considered line. It does not read this section's
prose; it derives the tier from `task_output_paths` (touching `shared/`,
`templates/`, or a canonical `*_SYSTEM.md`/`AGENTS.md`/`CLAUDE.md` forces the
full checklist) and from `risk_class`/`risk_severity`/`task_tier` on the task
record. Set those fields accurately at task creation (`map_task.py create
--risk-class ... --risk-severity ... --task-tier ...`) so the mechanical
check matches the tier you actually picked — see
`CHANGE_CONTROL_SYSTEM.md`'s Release tier section for the exact precedence.
DEC-CF-008, adopted directly from that audit
(`Projects/ClearFront/artifacts/reviews/clearfront-independent-delivery-audit-2026-07-17.md`).

This complements, not replaces, Claim Before Reviewing and Debate above:
tier the change first, then apply the process weight that tier calls
for.

## Visual-Fidelity Review (INS-0031 / IDEA-0024 / PROMO-0012)

When a task's acceptance is "matches an approved visual mockup or redesign,"
tests-green and a correctly ported structure are necessary but NOT sufficient,
and must not be reported as "matches the design." The ClearFront UI port showed
why: three "matches the mockup" claims were each backed by passing tests and a
ported layout while the build still visibly diverged, costing ~3 operator-rework
rounds. Require, as explicit acceptance criteria and as review checks:

- **Frozen reference.** The approved mockup is stored as the task's reference
  artifact.
- **Screenshot-vs-reference before submission.** A screenshot of the REAL build
  is captured and compared to the frozen reference — not the test suite, not a
  written description.
- **Verify at the operator's target viewport width**, not just wide desktop.
  Single-viewport verification hides responsive breakage (the ClearFront defect
  only appeared at ~963px, not the 1440px that was screenshotted).
- **Porting hygiene.** When styling into an existing stylesheet, prefer
  class-scoped selectors; avoid reusing bare element selectors (aside, main,
  section) the legacy CSS already targets — they silently restyle new markup of
  the same element type.

## When to Invoke Debate (IDEA-0019 / TASK-204)

`hcom run debate` runs a structured multi-perspective critique. It is an
OPTIONAL pre-escalation tool, not a required review step.

Invoke it when:

- A task is CONFLICT-frozen (`scripts/flag_conflict.py`) and the resolution is
  genuinely contested — two defensible readings, no clear winner.
- A high-authority `DECISION_CLASSES` call is close and a single reviewer's
  verdict would feel under-tested.
- Two reviewers reach opposite verdicts and you would otherwise escalate
  straight to the operator.

Do NOT invoke it for routine reviews, clear-cut findings, or to avoid making a
call you can already make. Debate costs tokens and time; use it where
multi-perspective critique actually changes the outcome. If a debate informs
the result, cite it in the review/decision/conflict record.

## Extraction/Bundle-Rewrite Safety (INS-0049)

When a task extracts, decodes, or rewrites files from an external
bundle/archive/package onto disk, require both of the following as a paired
default — TASK-207 needed two separate CHANGES_REQUESTED rounds because they
were caught one at a time:

- **Path-traversal validation** on every derived output path (canonical form
  check, confirm the resolved path stays under the intended output
  directory).
- **Atomic staged writes**: extract to a fresh sibling tempdir and swap
  generated outputs into place only after validation succeeds, so a
  failed/interrupted run cannot leave partial or unsafe output.

A reviewer catching one of these rarely prompts a check for the other unless
it is named as a pair — check both in the same pass.

## Multi-Source-of-Truth Contradiction Handling (INS-0052)

When a task reads state from more than one mirrored source (task JSON files,
`map.db` SQLite, `workflow/task_graph.json`, or similar), a status mismatch
between those sources must be surfaced as an explicit contradiction, not
silently resolved by trusting one source and skipping the other. TASK-284's
`build_index` trusted task JSON's RELEASED state and silently skipped the
case where SQLite/task-graph disagreed — the same reviewer caught it twice.
Check specifically: does this code have a path where two sources disagree,
and if so, does it flag that instead of picking a winner silently?
