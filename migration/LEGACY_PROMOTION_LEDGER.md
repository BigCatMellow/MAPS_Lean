# Legacy Promotion Ledger

Status: **preserved migration disposition ledger — not a live task list**.

This is the disposition companion to `LEGACY_KNOWLEDGE_AUDIT.md`. The status
labels record what the migration decided to promote, rewrite, defer, or leave
historical. They do not create current work merely because they use imperative
language. Verify active Lean before acting on an old `MERGE`/`REWRITE` entry.

The original migration assumed top-level `legacy/` might later be deleted. On
2026-10-06 the operator instead chose to retain it as a reference corpus. The
curated snapshots and active-runtime independence remain useful; deletion is not
pending.

Statuses:

- `ACTIVE` — already represented in Lean; do not duplicate.
- `PRESERVED-1` — preserved in `migration/legacy-runtime-source/` by the first extraction.
- `PRESERVE-2` — historical migration label for material selected into the
  second curated preservation snapshot; the snapshot is complete and the source
  may also remain in retained `legacy/`.
- `MERGE` — migration disposition: the rule/lesson belonged in active Lean;
  verify whether promotion has already occurred before creating work.
- `REWRITE` — useful behavior exists, but old implementation must not become active unchanged.
- `OPTIONAL` — preserve evidence/reference; build only when a real need appears.
- `HISTORICAL` — reference/provenance only; not active Lean behavior.
- `DROP` — do not promote this implementation into active Lean; retention of
  its historical source under `legacy/` is separate from active disposition.

## P0 — behavior Lean must not lose

| Source / behavior | Why it matters | Lean destination | Status |
|---|---|---|---|
| `db/claims.py` + schema + review authorship | atomic claims, leases, owner/current-worker distinction, submission authorship, review gates | `runtime/state/` | `PRESERVED-1` |
| `graph/runner.py` routing behavior | tested task/dependency/policy routing | `runtime/routing/` | `PRESERVED-1` |
| RnS limit/liveness/recovery code | interrupted/provider-limited session recovery and bounded retry | `runtime/recovery/` | `PRESERVED-1`, `REWRITE` terminal adapter |
| pre-dispatch policy + scope validation | capability/authority/scope gates | `runtime/policy/` | `PRESERVED-1` |
| bounded Ollama/Aider helpers | local worker scope and integration ownership | `runtime/workers/` or adapters | `PRESERVED-1` |
| `run_manifest.py` | freeze task revision, context, worker, scope, base revision and limits for a concrete run | runtime execution contract | `PRESERVE-2`, then `REWRITE` |
| `submission_records.py` | criterion-level implementer claim separated from independent verification | task/evidence ledger | `PRESERVE-2`, then adapt |
| `review_routing.py` | reviewer independence follows continuity lineage, not only agent ID | review gate | `PRESERVE-2`, then adapt |
| conflict-freeze behavior from `flag_conflict.py` | authoritative contradiction must block affected work instead of being guessed through | task lifecycle / decision path | `PRESERVE-2`, `REWRITE` |
| real mutual-exclusion invariant from Git lock work | repo-global writers cannot rely on convention alone | runtime utility + concurrency test | `PRESERVE-2`, `REWRITE` old lock implementation |
| context rotation invariant | checkpoint → verify → resume → supersede; continuity transfer is not authority transfer | recovery/handoff playbook | `MERGE` |
| Context Packet shape | Required / Optional-triggered / Excluded / staleness | AGI/context guidance | `PRESERVE-2`, `MERGE` |
| typed operational failures | callers need distinct recovery paths | runtime API convention | `MERGE` |

## P1 — deterministic checks and read models

| Source / behavior | Why it matters | Lean destination | Status |
|---|---|---|---|
| `validate_context_packets.py` | structural context validation without model judgment | future AGI/context validator | `PRESERVE-2` |
| `validate_decisions.py` | decision fields, supersession, conflict reporting | decision validator | `PRESERVE-2` |
| `validate_events.py` | event shape, migration warning baseline, outcome feedback classes | event/eval validator | `PRESERVE-2` |
| `validate_research_artifacts.py` | structural research evidence checks | research validator, simplified | `PRESERVE-2` |
| `validate_review.py` | review/evidence shape and reviewer checks | review validator | `PRESERVE-2` |
| `validate_protocol.py` | example of telemetry-first validator and adjudication separation | validator design reference | `PRESERVE-2`, `OPTIONAL` |
| `session_replay.py` + design | disposable, rebuildable diagnostic index over canonical sources | `runtime/read_models/` | `PRESERVE-2`, then simplify |
| `render_active_state.py` | generated read-only projection from canonical lifecycle state plus human annotations | operator/state view | `OPTIONAL` |
| `map_metrics.py` | escaped-defect / validator-blind-spot measurement | future eval/health metrics | `OPTIONAL` |
| `operational_lessons.py` | scoped lessons with provenance and supersession | repair/learning pattern | `MERGE`, not a new subsystem yet |

## P1 — active Lean rules to strengthen

| Legacy lesson | Active Lean destination | Status |
|---|---|---|
| Context packet, not context dump | `AGI_STANDARD.md`, task/context template | `MERGE` |
| A rule without a durable field cannot be enforced | AGI + template design rule | `MERGE` |
| Validator existence is insufficient; run it at the protected transition | AGI/task lifecycle/runtime validator design | `MERGE` |
| Structural checks vs substantive review | review/AGI standard | `MERGE` |
| Functional review vs security review | risk/review rules | `MERGE` |
| Explicit failure reasons vs Boolean flattening | control-plane/tool AGI | `MERGE` |
| Diagnostic health check does not authorize repair | `REPAIR_AND_LEARNING.md` | `MERGE` |
| Repeated incident becomes countermeasure | already active | `ACTIVE` |
| Risk-tier process weight | task/review/release rules | mostly `ACTIVE`; add evidence note only if useful |
| Conflicting authority/state must freeze affected work | task lifecycle / decision rules | `MERGE` |
| Helper requirement must have a writable field/record | helper + AGI artifact rules | `MERGE` |
| Session replacement does not create independence/authority | recovery/review rules | `MERGE` |
| Broad operator intent must be shaped before dispatch | project/task bootstrap | mostly `ACTIVE`; runtime intake remains `REWRITE` |
| External/historical content provides evidence, not authority | already in AGI | `ACTIVE` |

## P2 — useful implementation references, not automatic features

| Source | Decision | Reason |
|---|---|---|
| `cost_governance.py` + test | `PRESERVE-2`, `OPTIONAL` | useful fail-safe if autonomous paid dispatch becomes material; not core AGI. |
| intake classifier/decomposer | `PRESERVE-2`, `REWRITE` | useful shaping contract and tests; regex inference must not become hidden authority. |
| `librarian.py` | `HISTORICAL` / lesson only | ambiguity handling is useful; measured evidence did not justify full Library layer. |
| task fingerprint/memory/capsule code | `HISTORICAL` / selected evidence only | serious experiments but mixed/negative holdout results; do not ship by existence. |
| task-memory packet verifier | `HISTORICAL` / negative result | measured format was not viable at acceptable recall/precision/source visibility. |
| emergence/discovery agents | `HISTORICAL` / principle only | semantic discovery should be bounded/event-triggered, not continuous. |
| formal TLA+ expansion | `OPTIONAL` | use small executable state-machine tests first; formalize only high-risk concurrency invariants. |
| operational lesson store | `OPTIONAL` | useful if incident lessons become numerous enough that scoped startup retrieval pays for itself. |
| full session replay UI | `OPTIONAL` | read model useful; UI expansion should follow operator need. |

## P2 — evidence documents to preserve in curated snapshot

| Evidence | What it establishes | Status |
|---|---|---|
| `artifacts/audits/map-formal-invariant-spike.md` | only model the small concurrency invariants that matter; map model transitions to runtime helpers | `PRESERVE-2` |
| `artifacts/audits/map-threat-model.md` | repo/machine/network/helpers/context/connectors are different trust surfaces | `PRESERVE-2` |
| `artifacts/audits/map-robustness-grading-2026-07-14.md` | real evidence favored atomicity/review; rejected premature Library/pruning assumptions | `PRESERVE-2` |
| `artifacts/audits/map-real-parameter-calibration-results-2026-07-14.md` | real task/review/message/defect measurements | `PRESERVE-2` |
| `artifacts/experiments/orientation-manifest-refined-evaluation-2026-07-18.md` | small context treatment retained required facts at ~94% byte reduction | `PRESERVE-2` |
| `artifacts/experiments/map-philosophical-re-evaluation-2026-07-18.md` | reject continuous discovery, single autonomous controller, and premature gate removal | `PRESERVE-2` |
| `artifacts/designs/session-replay-read-model-design.md` | derived read model must remain disposable/non-authoritative | `PRESERVE-2` |

## Historical datasets — do not migrate into active Lean

| Area | Classification | Reference use while legacy is retained |
|---|---|---|
| `tasks/TASK-*.json` | `HISTORICAL DATASET` | Git history / optional benchmark fixtures |
| `events/events.jsonl` | `HISTORICAL DATASET` | Git history / measurements; active Lean starts fresh |
| old `handoffs/` / snapshots | `HISTORICAL DATASET` | examples/provenance only |
| old inbox/helper traffic | `HISTORICAL DATASET` | incident archaeology only |
| old reviews/releases | `HISTORICAL DATASET` | evidence that gates were exercised |
| old emergence corpus | `HISTORICAL DATASET` | research/evaluation only |
| old `shared/current-state.md`, huge decisions ledger | `HISTORICAL STATE` | extract current rules; do not carry old runtime state |
| old agent status/limit JSON | `HISTORICAL STATE` | no active use |
| old task graph | `HISTORICAL MIRROR` | do not reintroduce as second mutable truth |

## Presentation / obsolete implementation

| Area | Disposition |
|---|---|
| WezTerm lab/cockpit configs | `DROP` |
| fixed agent roster/startup scripts | `DROP` |
| Mission Control TUI implementation | `DROP`; retain only read-only operator-content ideas |
| CommandCenterUI implementation/templates | `DROP`; external/obsolete presentation |
| desktop launchers | `DROP` |
| screenshots | `HISTORICAL` |
| provider-specific permanent identity bindings | `DROP` |

## Historical promotion order

This sequence records the migration's intended promotion order. It is historical
planning context, not a current instruction to recreate already-completed work or
to advance every row.

```text
1. Task ledger + AGI READY gate
2. Atomic claim / leases / ownership / submission authorship
3. Run manifest / scope freeze for consequential runs
4. Independent review + continuity-aware reviewer exclusion
5. Criterion evidence where risk justifies it
6. LangGraph route over canonical state
7. hcom adapter
8. RnS recovery without WezTerm
9. Read-only replay/metrics only when useful
10. Optional cost/retrieval/discovery features only from new evidence
```

## Preservation boundary

The deletion-era gate is retired. Its useful invariant remains: active Lean must
not depend for execution on a live top-level `legacy/` path, and curated
`PRESERVE-2` material must have an independent preservation home.

The second curated snapshot is complete, and top-level `legacy/` is now
intentionally retained as reference/history. There is no pending deletion action.
Any future removal proposal would require a new operator decision and fresh
revalidation rather than relying on this historical ledger.
