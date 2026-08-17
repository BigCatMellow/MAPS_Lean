# Task: outcome-derived lesson candidate Wave 3

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/outcome-lesson-candidate-wave3`
- Risk: `MEDIUM`
- Goal: Build a deterministic, non-authoritative `CANDIDATE` lesson envelope from one canonical post-completion task outcome, explicit caller-supplied claim/applicability, and exact source refs without reading outcome notes as instructions, persisting lessons, or granting promotion authority.

## Inputs / source of truth

- root `AGENTS.md`;
- PR #43 lesson schema/projection at exact head `aeecf1b5775db1d5ac2484819620f476752f3654`;
- canonical TaskStore reads: `get_outcome()`, `get_task()`, `get_run_manifest()`;
- canonical `task_outcomes` semantics: append-only post-completion evidence that never alters original task/review truth.

## Change boundary

MAY CHANGE:
- `runtime/outcome_lesson_candidate.py`
- `tests/test_outcome_lesson_candidate.py`
- `work/tasks/outcome-lesson-candidate-wave3.md`
- `work/notes/2026-08-15-outcome-lesson-candidate.md`

MUST NOT CHANGE:
- outcome/task/run state;
- #43 lesson validation/projection semantics;
- SQLite schema/store composition;
- lesson promotion/retirement authority;
- Context Builder/startup/routing behavior;
- other agents' branches.

## Contract

Caller supplies:
- canonical `outcome_id`;
- explicit lesson `claim`;
- explicit #43-compatible `applicability`;
- `created_by` and `created_at`.

Builder must:
1. resolve exact canonical outcome;
2. resolve owning canonical task and require `DONE`;
3. if outcome names a run, resolve it and require exact task match;
4. require non-empty canonical outcome task revision;
5. construct exact refs to outcome, task, task revision, and optional run;
6. derive deterministic semantic candidate ID from source refs + claim + normalized applicability;
7. emit only `status=CANDIDATE`, `source_kind=TASK_OUTCOME`, no promotion/retirement/supersession;
8. run the result through #43 `validate_lesson_record()` before returning.

## Non-features

No:
- lesson text generation from outcome notes/source text;
- automatic applicability inference;
- ACTIVE/RETIRED creation;
- `promote()` function;
- lesson persistence/store;
- task/policy/review authority;
- automatic startup/Context Builder injection;
- outcome mutation.

## Acceptance criteria

- [x] Missing outcome/task/run fails closed.
- [x] Outcome task must be DONE.
- [x] Outcome run, when present, must belong to the same task.
- [x] Source refs are exact and deterministic.
- [x] Outcome notes/source prose are not copied into the lesson claim.
- [x] Claim/applicability remain explicit caller inputs.
- [x] Same semantic candidate inputs produce the same candidate ID regardless of `created_at`.
- [x] Material claim/applicability/source changes produce a different candidate ID.
- [x] Result validates through #43 and remains CANDIDATE with no promotion authority.
- [x] Builder mutates no canonical state.

## Verification

Focused:
```text
python -m unittest tests.test_outcome_lesson_candidate -v
```
Full Runtime CI is the repository gate.

Review required: `INDEPENDENT_REVIEW`.

## Stop / escalation

Stop rather than infer if:
- lesson claim would need to be generated from notes/prose;
- applicability is not explicitly supplied;
- promotion authority is requested;
- outcome/run/task identity is inconsistent;
- #43 schema changes before integration.
