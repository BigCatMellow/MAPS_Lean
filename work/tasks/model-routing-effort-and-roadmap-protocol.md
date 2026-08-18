# Task: Model routing effort axis and roadmap/checklist protocol

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `MAINTENANCE`
- Owner: `FOUNDRY`
- Risk: `LOW`
- Goal: add two new sections to `playbook/MODEL_CAPABILITY_ROUTING.md`, additive only, covering (A) reasoning-effort-level routing as an axis independent of worker class, and (B) a standing protocol for building and maintaining roadmap/checklist status documents (verification rigor, worker class/effort, self-certification review, status-drift prevention, single canonical status file).

## Inputs and source of truth

- Inputs:
  - `playbook/MODEL_CAPABILITY_ROUTING.md` (full read, existing tone/format);
  - `playbook/INDEX.md` (how this playbook doc relates to others);
  - `templates/task.md` (task-doc shape);
  - an existing `work/reviews/pr-*-review-evidence.md` file (evidence-file shape);
  - `scripts/check_review_evidence.py` (what independent review enforcement checks);
  - operator's stated content requirements for both new sections (given in the assigning message).
- Authoritative sources: the operator's task instructions for required content points; `MODEL_CAPABILITY_ROUTING.md`'s existing prose/format for style; live GitHub state for PR/CI/merge mechanics.
- Evidence labels: direct repository reads in this session are `VERIFIED` at the inspected ref.
- Dependencies / preconditions: none. Docs-only change; no runtime code touched.

## Change boundary

- MAY CHANGE:
  - `playbook/MODEL_CAPABILITY_ROUTING.md` (additive only — new subsections; no rewriting/removal of existing content);
  - `work/tasks/model-routing-effort-and-roadmap-protocol.md` (this file);
  - a new branch and PR against `main`;
  - `work/reviews/pr-<N>-review-evidence.md` (written by the independent reviewer, not by FOUNDRY).
- MUST NOT CHANGE:
  - any existing prose/headers/content already in `playbook/MODEL_CAPABILITY_ROUTING.md`;
  - `playbook/INDEX.md` or any other playbook file;
  - `work/roadmaps/` files (this task documents the *protocol*, it does not itself build `CAPABILITY_CHECKLIST.md`);
  - runtime code, tests, schemas, or any non-docs path.
- MAY CHANGE IF NECESSARY: none; broader edits require task amendment first.
- OPERATOR APPROVAL REQUIRED: none beyond what is already authorized by this task.

## Decision authority

- Owner may decide: exact wording/structure/heading placement of the two new subsections, so long as they cover every required content point and match the file's existing tone.
- Owner must escalate: any request to change existing sections, to expand scope beyond `MODEL_CAPABILITY_ROUTING.md`, or to skip independent review before merge.

## Acceptance criteria

- [x] `playbook/MODEL_CAPABILITY_ROUTING.md` has a new subsection on effort-level routing, placed near "Suggested worker classes", stating: effort level is orthogonal to worker class; low/medium effort maps to mechanical/narrow/pattern-following work; high effort maps to multi-source integration or expensive-to-discover-later mistakes; xhigh/max maps to architecture/authority-boundary decisions and second-pass skeptical review; and explicitly states an independent reviewer should run at equal-or-higher effort than the implementer it reviews, never lower.
- [x] `playbook/MODEL_CAPABILITY_ROUTING.md` has a new subsection on roadmap/checklist construction and maintenance, stating: writing/updating a status claim is Core-agent-class work at high effort minimum; every status claim needs a one-line independently-checkable evidence citation; a checklist about a session's own completed work is a self-certification risk requiring the same independent-SENTINEL-style-review-before-merge treatment as code; a PR that changes what a checklist item's status should be must update the status line in the same PR, not a follow-up; and there should be one canonical status-checklist file per program, with sub-roadmaps staying as design-detail references.
- [x] No existing content in `playbook/MODEL_CAPABILITY_ROUTING.md` was removed or rewritten — diff is purely additive.
- [x] Change is docs-only (no runtime/test files touched).
- [x] PR opened against `main`; CI checks `test` and `review-evidence` both pass.
- [x] `work/reviews/pr-<N>-review-evidence.md` exists, bound to the exact PR head SHA, written by a fresh independent reviewer (not FOUNDRY self-certifying).
- [x] PR merged via `gh pr merge <N> --squash --delete-branch`.

## Verification and evidence

- Verification:
  - visual diff review confirming additive-only change;
  - `scripts/check_review_evidence.py <N>` passes;
  - CI `test` and `review-evidence` checks green on the PR;
  - independent reviewer's evidence file explicitly confirms accuracy, fit with existing doc, no contradictions, and that this task's acceptance criteria are genuinely met.
- Evidence to preserve: PR number, head SHA, review-evidence file, CI run links.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Ordered procedure:
  1. read `MODEL_CAPABILITY_ROUTING.md` in full and skim `INDEX.md`;
  2. write this task doc;
  3. implement the two additive subsections;
  4. push branch, open PR;
  5. dispatch a fresh independent review agent to write the evidence file;
  6. confirm CI green, merge with `--squash --delete-branch`.
- Failure branches:
  - IF the independent reviewer finds a genuine inaccuracy or contradiction THEN fix it and re-request review rather than merge;
  - IF CI `review-evidence` check fails THEN do not merge until the evidence file is present and correctly bound to head SHA;
  - IF a merge conflict with concurrent work appears THEN stop and report rather than force-push/rebase destructively.
- Rollback / recovery: revert the merge commit if a defect is found post-merge; no runtime state affected.
- External side effects: GitHub branch, PR, and merge commit only.
- Effort limit: single additive docs PR; no redesign of the routing doc.

## Stop / escalate

Stop rather than guess if: GitHub is unreachable, there's a merge conflict with concurrent work on `main`, or the independent reviewer identifies a genuine defect requiring scope beyond this task.

Escalate to: operator, for any of the above.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This task documents the protocol only; it does not itself build `work/roadmaps/CAPABILITY_CHECKLIST.md`. That remains separate future work, now governed by the new protocol section once merged.

## Completion / handoff

- Completed: task doc, implementation, PR, independent review, merge (update once each step lands).
- Not completed: n/a once merged.
- Current blocker: none.
- Next action if not DONE: proceed to next step in the ordered procedure above.
