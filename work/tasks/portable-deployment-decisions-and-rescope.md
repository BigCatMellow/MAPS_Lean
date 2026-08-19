# Task: Record portable-deployment operator decisions and rescope roadmap 06

- Status: `READY_FOR_REVIEW`
- AGI status: `UNCHECKED`
- Type: `PLANNING`
- Owner: agent (this session)
- Risk: `LOW`
- Goal: record the operator's five Mission-meeting decisions from roadmap
  `06-portable-deployment.md` (#128) plus the chosen first pilot target
  (Chain Shovel) as a decision note, and rescope the roadmap's `D2`
  placeholder into concrete `D2a`/`D2b`/`D2c` design/planning phases now
  that the architecture fork is resolved. Docs-only.

## Inputs and source of truth

- Inputs: `work/roadmaps/agent-harness-capabilities/06-portable-deployment.md`
  (#128, merged), specifically its "Mission meeting" section's five
  "Operator decisions needed" items; the operator's decisions as relayed for
  this task.
- Authoritative sources: the operator's stated decisions (relayed in this
  task's dispatch) are authoritative for what was decided; roadmap 06 is
  authoritative for what was previously open/unresolved.
- Evidence labels: operator decisions are `REPORTED` (relayed by the
  dispatching session, not independently re-confirmed with the operator by
  this task) — standard for a decision-recording task; the roadmap content
  being amended is `VERIFIED` (read directly from the merged file).
- Dependencies / preconditions: roadmap 06 / PR #128 must already be merged
  to `main`. Confirmed via `git log`.

## Change boundary

- MAY CHANGE: `work/notes/2026-08-19-portable-deployment-operator-decisions.md`
  (new file), `work/roadmaps/agent-harness-capabilities/06-portable-deployment.md`
  (Mission meeting + Phase 1 sections only), `work/roadmaps/CAPABILITY_CHECKLIST.md`
  (Portable Deployment section + §6.35 row only), this task file.
- MUST NOT CHANGE: any `runtime/` code, any other roadmap file, any other
  section of `06-portable-deployment.md` (Current reality, Definition of
  DONE, Boundaries' scope lists, Backward plan, Later/TRIGGERED, Checkpoints
  are left as-is except where a decision resolution note is appended
  inline), Chain Shovel's own repository (no access from this session).
- MAY CHANGE IF NECESSARY: none.
- OPERATOR APPROVAL REQUIRED: none beyond the decisions already relayed —
  this task only records them and re-derives their scoping consequences for
  the roadmap; it does not make new substantive decisions of its own.

## Decision authority

- Owner may decide: exact wording/structure of the decision note; how `D2`
  is split into sub-phases (D2a/b/c naming, ordering, and what each covers)
  as a direct, traceable consequence of the five recorded decisions.
- Owner must escalate: any case where the relayed operator decisions seem to
  conflict with roadmap 06's Definition of DONE or Boundaries (none found —
  all five decisions are consistent with the existing document).

## Acceptance criteria

- [x] Decision note exists at
  `work/notes/2026-08-19-portable-deployment-operator-decisions.md`, records
  all five decisions plus the Chain Shovel pilot-target choice, each with a
  one-line reasoning restatement, in this repo's own notes-file voice.
- [x] Roadmap 06's Mission meeting section marks all five operator decisions
  as resolved with inline decision text and a link to the new note.
- [x] Roadmap 06's "First wave selected" text and Phase 1 now name `D2a`,
  `D2b`, `D2c` as concrete design/planning phases (not implementation),
  each with a real one-paragraph description of what it covers.
- [x] `CAPABILITY_CHECKLIST.md`'s Portable Deployment section and §6.35 row
  reflect the `D2a`/`D2b`/`D2c` split, all marked `NOT STARTED`.
- [ ] Independent review confirms the decision note accurately reflects the
  relayed decisions, the roadmap update is genuinely useful (not vague
  restatement), and nothing here commits to building beyond design/planning.
- [ ] CI green on the PR.

## Verification and evidence

- Verification: manual read-through of the diff against roadmap 06's prior
  Mission-meeting text to confirm every one of the five items is addressed;
  `git diff` review; independent SENTINEL review agent dispatch.
- Evidence to preserve: this PR's diff, the independent reviewer's
  `work/reviews/pr-<N>-review-evidence.md` artifact, CI status.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: MAPS_Lean repo only; docs-only change, no runtime
  target.
- Ordered procedure: write decision note → update roadmap 06 → update
  `CAPABILITY_CHECKLIST.md` → write this task file → push branch → open PR
  → dispatch independent reviewer → confirm CI green → merge (squash,
  delete branch).
- Failure branches: IF the independent reviewer finds the decision note
  misrepresents a decision, THEN correct the note before merge, not after.
  IF CI fails for a reason unrelated to this diff, THEN investigate before
  assuming it's safe to merge anyway.
- Rollback / recovery: revert the merge commit if a factual error is found
  post-merge; no other rollback needed (docs-only, no runtime side effects).
- Security / privacy controls: N/A.
- External side effects: none — no code runs, no external repo (Chain
  Shovel or otherwise) is touched.
- Effort limit: single-session, docs-only task.
- Approved reference: roadmap 06 (#128) is the approved reference for scope;
  the operator's relayed decisions are the approved reference for content.

## Stop / escalate

Stop rather than guess if:

- the relayed operator decisions turn out to be ambiguous about which of
  roadmap 06's five numbered questions they answer;
- rescoping `D2` into `D2a`/`D2b`/`D2c` would require a substantive new
  design decision not already implied by the five recorded operator
  decisions (in that case, flag it as a new open question rather than
  silently deciding it here).

Escalate to: operator (via the dispatching session).
