# Helper Assignment — EXP-0005 Frozen Rubric and Retained Control

- Owner: codex-lab-lilo
- Helper tag: helper-review-steward-moku
- Status: COMPLETE — control corrected and independently reverified
- Experiment: `EXP-0005`
- Objective: Before any compact treatment exists, freeze the six-row answer
  rubric and retain the complete raw scenario control needed to inspect and
  reproduce the experiment's byte measurement.

## Fixed scenario

Use a new current recovery scenario that does not rely on the stale historical
TASK-227 live-state capture. The scenario must contain one task in
`CHANGES_REQUESTED`, its independent review, one released task that must not
be reopened, an authority boundary, helper boundary, and one explicit
live/durable availability uncertainty. The control must name the exact
point-in-time sources selected and why each is needed.

## Required output

`MAP_System/artifacts/experiments/orientation-manifest-refined-rubric-control-2026-07-18.md`

It must contain:

1. a frozen six-row rubric: task state/owner, first required read, later
   permitted mutation/rework, authority boundary, helper boundary, and
   recovery/uncertainty; each row needs required fact, canonical source,
   acceptable unknown, and fail condition;
2. the exact source list and capture time;
3. complete retained raw point-in-time control contents (not hashes alone),
   including any dynamic command output, in a clearly delimited section or
   attached text within the artifact;
4. SHA-256 values for each retained static source plus the full control;
5. the exact `wc -w -c` measurement command and the predeclared treatment
   threshold: at least 50% fewer bytes than this retained scenario control;
6. a statement that this establishes scenario-local comparison only and does
   not replace the mandatory startup contract.

## Boundaries

- Read-only source capture. Do not read a treatment, construct a treatment,
  change task state, alter a policy/index/runtime, or create a task.
- Do not omit raw source content merely because its hash is recorded.
- Report the output path, capture byte count, and stop state through one hcom
  `inform`, then return to visible listening.

## Owner check — correction required

The initial artifact records per-source hashes and a command that rebuilds a
control from **live** files, but it does not retain the complete static control
contents. That fails its required item 3 and cannot reproduce a future
point-in-time control if any source changes.

Before any treatment is constructed, amend only the named control artifact:

1. verify each live static source still matches the hash recorded at capture;
2. if every hash matches, include the complete static concatenation inside the
   artifact in a clearly delimited raw-control section, then recompute and
   record the full-control hash/byte count against that retained content plus
   the captured dynamic JSON;
3. if any source no longer matches, report that the frozen control is invalid
   and stop—do not rebuild it with changed content or silently revise the
   capture time;
4. state explicitly which outcome occurred and send a corrective hcom inform.

## Outcome

- All eight static hashes matched the captured values.
- The artifact now retains a lossless complete Base64 control attachment.
- Owner independently decoded it: SHA-256
  b3624f4e12f1cd73f2f6810e1a7d20520a4369e950fa8a618681134359fa9df8,
  5,762 words, 44,432 bytes.
- No treatment was constructed by this control author.
