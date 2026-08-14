# EXP-0004 Baseline Evaluation

- Evaluator: helper-review-steward-moku
- Scope: exploratory evaluation of one fixed resumed-agent scenario
- Verdict: **REVISE**

## Measurement method

The treatment artifact declares a point-in-time raw-source control of 51,378
bytes and a treatment packet of 5,653 bytes. Arithmetic verification:

| Measure | Value |
|---|---:|
| Stated control | 51,378 bytes |
| Stated treatment | 5,653 bytes |
| Scenario-local reduction | 45,725 bytes / **89.00%** |
| Treatment remaining size | 11.00% of stated control |

This is **not** a measured reduction of the mandatory startup contract. It is
only a scenario-local comparison against the treatment's enumerated source
set. The raw concatenated control and point-in-time hcom output were not
preserved as independently byte-reproducible artifacts, so this evaluation
verifies the stated arithmetic and comparator declaration, not the historical
51,378-byte source measurement itself. Current file sizes (5,104-byte canonical
answer and 9,404-byte combined treatment artifact) are different objects and
must not be substituted for that baseline.

## Scoring

| Required dimension | Score | Evidence |
|---|---|---|
| 1. Terminal/current task state and owner | PASS | Treatment says TASK-227 is `CHANGES_REQUESTED`, owned by `claude-lab-gome`, and says TASK-220 is RELEASED/not to reopen. These agree with the canonical task records and control answer. |
| 2. Immediate safe read before mutation | PARTIAL | Treatment conditions rework on owner readiness and cites review/handoff, but its `next.task_action` makes rework the first named action. It does not explicitly require reading the review and handoff before the later mutation, the exact distinction identified in the preflight and canonical control. |
| 3. Later permitted rework mutation and five required findings | PASS | Treatment requires `map_task.py rework` before plan edits and preserves all five REQUIRED scope items: status read-model contract/test, bounded index, AUTHORITY routing, evidence intake, and lifecycle north star/measures. |
| 4. Authority boundary | PASS | Treatment preserves core-agent proposal versus command-center approval for the helper-mutation AUTHORITY change, and limits helpers to recommendations. |
| 5. Helper boundary | PASS | Treatment retains visible, temporary, scoped, durable helper work under core ownership, without task-ownership or binding-decision bypass. |
| 6. Interruption recovery and live/durable availability uncertainty | PASS | Treatment distinguishes live hcom presence from durable `out_of_tokens` status, states that presence does not prove provider capacity, and retains availability/claim/HANDOFF-or-STATE_SNAPSHOT recovery facts. |

## Exact missing and invented facts

| Type | Fact | Effect |
|---|---|---|
| Missing | "Read `task227-review-lilo.md` and the system-improvement handoff before mutation" is not an explicit immediate action in the treatment. | An evaluator could select rework without demonstrating read-before-mutate safety. |
| Missing | A pre-frozen six-question rubric separating immediate read from later rework does not exist; the preflight identified only five fixed routing questions. | The current pass cannot support a confirmatory correctness claim. |
| Missing | A retained raw control snapshot/hash and predeclared materiality threshold are absent. | The 89.00% claim is scenario-local arithmetic, not independently replayable baseline evidence. |
| Invented canonical facts | None found. | The treatment's additions (TASK-220 terminal state, sole output, output-path handoff restriction, and capacity uncertainty) are traceable to its named task/operating sources or are marked as unknown. |

## Preflight limitation

The discovery preflight already found two design gaps that remain decisive:
there was no answer rubric frozen before treatment construction and no
predeclared materiality threshold. This evaluator therefore does not claim the
treatment "passed" a blinded, confirmatory test. The treatment is a useful
baseline packet that preserves five of six scored dimensions, but its PARTIAL
immediate-action result and unrepeatable historical control prevent adoption.

## Recommendation and smallest next experiment

Record EXP-0004 as **revise**, not reject or park. The smallest next experiment
is one new fixed scenario with:

1. a six-row rubric frozen before treatment creation (including separate
   read-first and rework-later answers, required uncertainty language, and
   canonical references);
2. a retained concatenated control snapshot or content hashes plus exact
   `wc -w -c` command;
3. a predeclared scenario-local threshold (for example at least 50% fewer
   bytes), explicitly separate from mandatory-startup savings; and
4. a blinded evaluator who receives questions plus treatment, then verifies
   against the frozen control/canonical sources.

No runtime/index/policy work follows from this baseline.

## Owner-facing next step

Keep the current treatment as evidence of a promising compression pattern, but
do not generalize it. If the owner wants to continue, author the four-item
revision packet above and rerun one blinded six-question evaluation; otherwise
the canonical startup path remains unchanged.
