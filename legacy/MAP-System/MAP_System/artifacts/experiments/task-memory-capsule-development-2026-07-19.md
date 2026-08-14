# TASK-262 Structured Retrieval Capsule Development

## Outcome

Structured Markdown retrieval capsules improved evidence selection on known development data. With the same already-selected task IDs and the same three-source query-wide budget, exact expected-source visibility rose from TASK-261's recorded 16/20 (80%) to 18/20 (90%). Rebuilding the current documents but ignoring capsule fields remained at 16/20, which indicates that the measured gain came from the parsed purpose, proof, applicability, boundary, evidence-type, and status fields rather than merely placing more words near the top of each file.

This is not fresh evidence and is not an integration result. The six pilot documents were selected and authored while the TASK-260/TASK-261 misses were known. The result justifies freezing the convention for a fresh holdout; it does not justify adding capsules across the repository or changing startup, task authority, routing, UI, embeddings, or external services.

## Capsule convention

The guide at `MAP_System/notes/retrieval-capsule-guide.md` defines one exact six-field block:

```md
## Retrieval capsule

- Purpose: ...
- Proves: ...
- Applies to: ...
- Does not provide: ...
- Evidence type: ...
- Status: ...
```

The combined field values must contain 60–120 words. Evidence type and status use controlled values. `Does not provide` must state a meaningful boundary rather than a generic disclaimer. The capsule remains descriptive metadata; it cannot grant authority or override the document body, task database, decisions, reviews, releases, or operator instructions.

The parser treats documents without capsules as valid fallbacks. Present capsules fail validation when they are duplicated, missing fields, contain unknown fields, use the wrong order, have empty or weak boundaries, exceed the word range, or use uncontrolled evidence/status values. Example capsules inside fenced Markdown are ignored rather than mistaken for live metadata.

## Representative additive edits

No existing body prose was rewritten. A capsule was inserted into six documents with different proof roles:

| Document | Evidence type | Status | Capsule words |
|---|---|---|---:|
| `MAP_System/AGENTS.md` | governing rule | current | 79 |
| `MAP_System/notes/practice-scenario-runbook.md` | procedure | current | 84 |
| `MAP_System/artifacts/tests/rns-persistent-supervisor.md` | measured outcome | historical | 88 |
| `MAP_System/artifacts/tests/local-ollama-advisory-lane-test-2026-07-18.md` | measured outcome | historical | 91 |
| `Projects/ClearFront/artifacts/tests/task-214-combat-parity.md` | test evidence | historical | 93 |
| `MAP_System/artifacts/experiments/map-kickoff-alignment-scenario-2026-07-18.md` | measured outcome | historical | 84 |

Authoring cost was 519 words total, with a median capsule length of 88 words. This is small compared with the six documents, but it is not free: every capsule creates another statement that can become stale and must change with the body.

## How capsule scoring works

`MAP_System/scripts/task_memory_capsule_pilot.py` imports the frozen TASK-261 selector rather than modifying it. For Markdown candidates it parses capsules separately from document bodies and records whether a selected source came from a validated capsule or normal fallback.

- Query overlap with `Purpose`, `Proves`, and `Applies to` is a positive signal.
- Query overlap with `Does not provide` is subtractive. Excluded capability language must not be interpreted as evidence that the capability exists.
- Evidence type maps softly to the proof role requested by the query.
- Current evidence receives a small bonus; historical, draft, and superseded capsules are progressively downweighted.
- All original path-health, source-link, clause-coverage, temporal-mode, duplicate-hash, and non-redundancy behavior remains in force.
- Role diversity remains a preference, not a quota, and the selector still returns at most three sources across the task set.

The local model receives no capsule body automatically in this pilot. Capsule fields affect deterministic ranking, and only the selected source leads would be placed in a later packet.

## Known-development comparison

| Query | TASK-261 recorded | Current fallback | Capsule-aware | Effect |
|---|---:|---:|---:|---|
| F1 | 2/3 | 2/3 | 2/3 | Combat parity became visible, but `combat.js` was displaced; no net gain. |
| F2 | 2/2 | 2/2 | 2/2 | No capsule needed. |
| F3 | 3/3 | 3/3 | 3/3 | Historical measured-outcome capsule remained useful. |
| F4 | 2/3 | 2/3 | 3/3 | Exact local advisory outcome replaced the generic second runner test. |
| F5 | 1/2 | 1/2 | 2/2 | Governing-rule capsule surfaced the exact `AGENTS.md` authority boundary. |
| F6 | 2/3 | 2/3 | 2/3 | Remaining miss is `chat.js`, a non-Markdown implementation source. |
| F7 | 2/2 | 2/2 | 2/2 | No capsule needed. |
| F8 | 2/2 | 2/2 | 2/2 | Procedure and measured-outcome capsules preserved exact selection. |
| **Total** | **16/20 (80%)** | **16/20 (80%)** | **18/20 (90%)** | **+2 exact sources.** |

Six of the 24 selected source slots used validated capsules; the remaining 18 stayed on ordinary fallback. Median capsule-aware selection time was 8.015 ms. The disposable database stayed 704,512 bytes because capsules were parsed at selection time rather than added to the frozen FTS schema.

## What the result means

The experiment supports a narrow conclusion: concise descriptions of purpose, proof role, applicability, and non-authority boundaries can help an index distinguish two lexically similar Markdown sources. The gains occurred exactly where the old index was confused about proof type:

- an executable runner test versus the measured advisory-lane outcome; and
- graph/build references versus the governing helper metadata rule.

It does not show that all Markdown should be rewritten. Four queries were already exact without capsules, one Markdown capsule merely exchanged which expected source was missed, and the remaining UI miss is JavaScript. Adding capsules indiscriminately would create maintenance load without retrieval value.

## Negative-query and temporal limitations

`Does not provide` is promising for abstention because it gives the index explicit non-capability language. It is also dangerous: a lexical system could accidentally treat words such as “multiplayer” or “release authority” as positive evidence. The pilot only applies a score penalty and did not rerun autonomous negative-task selection. A fresh holdout must contain hard negative and near-miss questions before boundary text is used by an abstention gate.

Historical capsules were authored now about older evidence. Their `historical` status prevents them from masquerading as current proof, but it does not create a task-time snapshot. Current SHA-256 values prove only the post-capsule file state. Task-time source hashes or snapshots are still required to say what a source contained when an older task completed.

Capsule staleness is the principal operational risk. The authoring rule is therefore strict: update or remove a capsule in the same task that materially changes its body. A validator can catch malformed metadata but cannot determine whether a fluent capsule has become semantically false.

## Candidate freeze for a fresh holdout

Freeze this development candidate before any new evaluation:

- guide: `MAP_System/notes/retrieval-capsule-guide.md`
- guide SHA-256: `5cd3ea0e08894d66e911d85510825cb24415befc79ef35f993c7da820532744f`
- parser/scorer: `MAP_System/scripts/task_memory_capsule_pilot.py`
- parser/scorer SHA-256: `310371e44b7abdf3d3566a12507ee755e949dafffc67dd0d1c1f332e72d49b6b`
- tests: `MAP_System/tests/test_task_memory_capsule_pilot.py`
- tests SHA-256: `8519654dece18d5219419b4b918021c6c6b91734c8e08f6b5d69c43442e068df`
- required fields, types, statuses, word range, score weights, and three-source budget: unchanged until holdout completion

The fresh holdout should select capsule candidates before questions are authored, include uncapsulated controls, distinguish required sources from acceptable substitutes, and include negative capability queries that reuse words found in `Does not provide`. Success should require improved acceptable-source visibility without task-recall loss, material context growth, or false historical attribution.

## Verification

- 11 capsule parser, validator, scoring, temporal, deterministic, and repository-document tests passed.
- 32 total capsule, selector, frozen retriever, and holdout-harness tests passed.
- All six pilot capsules validate; the guide's own capsule also validates despite its fenced example.
- TASK-261 selector, tests, JSON result, and report match their recorded SHA-256 values byte-for-byte.
- The machine-readable result records pre-capsule hashes, current hashes, word counts, capsule provenance, fallback comparison, exact-source results, build cost, latency, and frozen-input checks.
- `MAP_System/artifacts/experiments/task-memory-capsule-development-2026-07-19.json` validates as JSON.

## Recommendation

Adopt the capsule format only as a frozen experiment and run one independently authored fresh holdout. Do not mass-add capsules yet. If the fresh result holds, the first production candidates should be high-value governing rules, current-state summaries, procedures, decisions, and measured outcomes that are repeatedly confused with neighboring documents. Pair that adoption with task-time source hashes and a stale-capsule check; do not add embeddings while task retrieval itself remains strong.
