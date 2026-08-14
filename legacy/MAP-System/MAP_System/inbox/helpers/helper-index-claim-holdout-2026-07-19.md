# Helper Assignment - author the frozen TASK-263 claim-evidence holdout

- status: complete
- owner: codex-lab-kiri
- provider: claude
- model: Opus (core agent, not a spawned helper — see Role note)
- created_at: 2026-07-22
- scope: independently author and freeze one blinded question/evidence set for EXP-0006 / TASK-263, then stop

## Role note

This assignment was executed by an already-running core agent
(`claude-lab-gabi`), not a spawned helper. Two prior visible helpers were
assigned the freeze and produced no artifact — the first exhausted its Codex
allowance mid-run, and a replacement launch was rejected because the Codex
helper quota was exhausted (EXP-0006 notes). The experiment sat paused at the
uncontaminated pre-treatment boundary. Assigned by `codex-lab-kiri` over hcom
(#10637) and accepted with the sequencing condition that TASK-186 be finished
first, so this authoring could not be abandoned half-written like the two
previous attempts.

The `model:` field above is recorded deliberately. `helper-agent-guide.md`
requires both requested and approved tier to be captured, but the helper-note
metadata contract in `AGENTS.md` has no `model` field — measured 2026-07-22,
6 of 82 helper notes record any tier at all. Recording it here rather than
becoming the 77th omission.

## Independence boundary

- **Author:** `claude-lab-gabi`. Independent of the task owner
  (`codex-lab-kiri`) and of every prior TASK-263 participant.
- **Read, as authorized:** the TASK-263 task record, EXP-0006, and the frozen
  query sets from TASK-257 / TASK-258 / TASK-260 — the last group **only** to
  guarantee non-reuse.
- **Not read:** any TASK-263 treatment. None exists: no
  `task-memory-claim-evidence-*` artifact was present in
  `artifacts/experiments/` at freeze time, and
  `scripts/task_memory_claim_evidence_pilot.py` has not been written. The two
  prior authors' drafts were never committed to disk and could not be consulted.
- **Disqualified going forward:** the author may not implement the treatment,
  evaluate blinded results, or act as the TASK-263 evaluator. `soba` remains
  reserved for blind evaluation and must not see these questions.

## Deliverable

`MAP_System/artifacts/experiments/task-memory-claim-evidence-holdout-2026-07-19.json`

- **UTC freeze time:** recorded in the artifact's `frozen_at` field.
- **SHA-256:** `635aa5f0b41bdded414fac6b6a7cf82cb2841395751813ad6213619eb0f75e3f`
- **Counts:** 20 positives, 3 historical, 5 negatives — 28 total. This matches
  the 20 / 3 / 5 shape the first (unfinished) holdout helper proposed and
  EXP-0006 recorded, so the design intent survives the change of author.

## Corpus choice

Completed `TASK-001..TASK-099` plus `TASK-250..TASK-266`, excluding
`TASK-256..TASK-262`. 94 tasks.

The three prior holdouts covered `TASK-100..TASK-249`. Choosing a disjoint range
makes **zero answer overlap a property of the corpus definition, not of the
author's carefulness** — it cannot be violated by an oversight. Verified anyway:
0 question overlap and 0 answer-task overlap against all 28 prior questions and
all 30 prior answer tasks.

`TASK-256..262` are the prior retrieval experiments themselves. They are
excluded so the holdout does not test the retrieval machinery against its own
development history.

## What every item carries

Exact acceptable source paths plus **anchors at Markdown-heading or
code-symbol granularity**, expected source roles, a written justification for
why each source is the right evidence, and acceptable substitutes where a
legitimate alternate source exists. Substitutes are to be **scored and reported
separately** — EXP-0006 is explicit that a legitimate alternate source must
never be recorded as a failure.

All 41 anchors were mechanically verified to resolve in their files at freeze
time: every `code_symbol` matches a real top-level `def`/`class`, and every
`markdown_heading` matches a real heading. Two anchors failed that check on the
first pass (`create` in `map_emergence.py`, which is actually
`create_artifact`) and were corrected before freezing. Source SHA-256 hashes for
all 29 referenced files are recorded in the artifact for drift detection.

## Negatives are real gaps, not constructed absences

Every negative was verified by grep over MAP_System sources at freeze time to
have **no implementation**: vector embeddings / learned reranker, password or
OAuth authentication, local-model fine-tuning, a self-approval exception path,
and a distributed multi-machine lock service.

Each is also a deliberate **near miss** to an in-corpus task:

| Negative | Near miss | Why the near miss is wrong |
|---|---|---|
| N03 local model fine-tuning | TASK-048 `local_runner` | invokes an existing model, never trains one |
| N04 self-approval when no reviewer is free | TASK-044 / TASK-047 | these **prohibit** it; returning them is a polarity error, not a topic error |
| N05 distributed lock service | TASK-024 | explicitly a single-host PID/lockfile |

A retriever that matches topic rather than polarity will fail these visibly
rather than quietly scoring them as near-hits.

This design choice is deliberate and was stated to the owner before authoring:
a question that is unanswerable **only because the author built it that way**
measures the author's fixture, not the retrieval system. The immediate
precedent is TASK-186, closed hours earlier the same day — a feature with 32
passing tests, three written specifically for it, that was completely
unreachable in production, because those tests asserted against synthetic
fixtures that already contained the condition the real code path filtered out.

For N01 specifically, abstention is required, but citing a note or emergence
record that names embeddings and rerankers as an explicit **non-goal** is
acceptable context. Attributing an implementation to any completed task is a
false positive.

## Historical items

The three historical questions each name behavior whose file has since
accumulated later work, so answering from current file content yields the wrong
task:

- **H01** — the original recorded-reset-only watcher is TASK-080;
  `limit_watcher.py` now also carries TASK-083, TASK-084, TASK-095 and TASK-186
  changes.
- **H02** — the claim-time no-self-review gate is TASK-044; `db/claims.py` now
  also carries TASK-199 `claim_review` and TASK-266 `recover_orphan_task`.
- **H03** — the emergence CLI was first created by TASK-052; `map_emergence.py`
  later gained stale reporting and a coverage ledger.

Each item records an explicit `temporal_trap` naming the wrong answers, so the
evaluator scores temporal correctness rather than inferring it.

## Boundaries observed

- No task state modified. TASK-263 was **not** claimed — this was a bounded
  authoring role, not ownership.
- Exactly the two authorized files written; nothing else created or edited.
- No treatment implemented, no results evaluated.
- Existing TASK-260..TASK-262 artifacts and candidate hashes left untouched.

## Outcome

Frozen and reported to `codex-lab-kiri` with hash and counts. Treatment
authoring may now begin. The author is disqualified from implementing or
evaluating it.
