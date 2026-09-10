# Pilot-evidence roadmap reconciliation — 2026-09-09

Status: `PLANNING / EVIDENCE — NOT CAPABILITY STATUS AUTHORITY`

Parent task: [`../tasks/roadmap-reconciliation-27-pilot-evidence-bootstrap.md`](../tasks/roadmap-reconciliation-27-pilot-evidence-bootstrap.md)

## Result

Current roadmap direction survives the external-system research. The evidence supports **targeted strengthening and proof**, not a new control plane or wholesale roadmap rewrite.

Classification of the 16 unfinished master capabilities:

```text
STRENGTHEN  8
KEEP        6
DEFER       1
CHALLENGE   1
```

No capability status changes are proposed by this note.

Current source snapshot:

- `main`: `18b064cdce00963b0417c8105c36e7fe624f3e4e`;
- latest canonical capability trajectory evidence: check #26 / merged PR #318, scoreboard `19 DONE / 10 IN PROGRESS / 6 NOT STARTED`;
- `25c7729..18b064c` contains only `docs/wiki/Development.md` + `_Sidebar.md`, so no capability implementation/status changed after check #26;
- PR #319 is an independently owned active lane and is excluded. Nothing below edits, reviews, depends on, or assumes the outcome of #319.

Supporting Pilot evidence: `BigCatMellow/Pilot_Projects`, branch `research/competitive-architecture-borrow-before-build`, especially `complete-ai-work-system/research/MAPS_L-INTEGRATION-MAP.md`, production packets, fix histories, and portable test catalogue.

## Disposition semantics

- `KEEP` — current MAPS plan/gating remains best supported; do not pull the item forward merely because reusable upstream code exists.
- `STRENGTHEN` — preserve the current MAPS owner/mechanism, but add stronger semantics/tests/evidence from the Pilot corpus when that row is worked.
- `DEFER` — keep current evidence-only/non-production posture; no present trigger justifies promotion.
- `CHALLENGE` — one current assumption deserves a bounded discriminating test. This is not supersession authority and does not authorize a replacement.

## Reconciliation of unfinished master capabilities

| Item | Disposition | Evidence-backed interpretation | Smallest next proof / trigger |
| --- | --- | --- | --- |
| **6.4 Deterministic Hooks / Interceptors** | **STRENGTHEN** | Current hook architecture is directionally right. Upstream evidence strengthens exact-action identity, fail-closed authority, verified external-effect outcomes, and effective-runtime evidence; it does not justify another hook framework. | Execute the already-merged default-off `HarnessService.stop()` production path and capture the first real `BEFORE_DESTRUCTIVE_ACTION` evidence. Keep status IN PROGRESS until observed. |
| **6.10 Skill provenance / trust / quarantine** | **STRENGTHEN** | Current lifecycle/provenance/capability-gate design matches the strongest external lessons. Sigstore/SLSA/in-toto/TUF and DSH/Letta evidence reinforce immutable identity, provenance-vs-authority separation, and explicit activation trust. | When 6.10 resumes, add only locally applicable third-party/update/capability regression cases; do not build a second package authority or wholesale SBOM platform. |
| **6.11 Context budgets / progressive context** | **STRENGTHEN** | Noriq/DSH/Letta evidence reinforces that canonical required facts need protected space and retrieval relevance is separate from authority/freshness. Current `budget_class` classification is useful but still only partially drives loading. | Reconcile with deferred issue #248; make one bounded real loading decision derive from the existing plan/budget classes before adding semantic/vector infrastructure. |
| **6.19 Task-scoped helper continuity** | **STRENGTHEN** | Hermes/DSH failures show session continuity, task continuity, liveness and current authority must remain separate. Reuse must reject stale observations/ownership even when a child still exists. | Add/verify stale-child, provider-health and superseded-observation cases before automatic helper resume; do not promote metadata TTL reuse into authority. |
| **6.20 Advisory NO_PROGRESS** | **STRENGTHEN** | Restate/Gas City/Optio/Symphony evidence strongly separates process heartbeat from useful progress and human-input waits from retryable stalls. The current advisory-only design is a safe base. | Expand the frozen cases for “alive but not progressing,” explicit human wait, observer suspension, and stale activity. Keep automated recovery gated until false-positive behavior is measured. |
| **6.21 Deterministic `maps flow` lifecycle** | **STRENGTHEN** | The existing deterministic flow family should remain the owner. External systems argue for fresh-state reconciliation, stable operation IDs, and explicit ambiguous external outcomes rather than a second workflow/task engine. | Shape the unresolved recover path as reconciliation over current canonical state; if it can cause external effects, require stable operation identity/receipt semantics before retry. |
| **6.22 Memory trust classes** | **STRENGTHEN** | Current trust/admission/provenance guard matches DSH/Noriq/Letta lessons: model-visible memory is not authority and trust must survive retrieval/compaction. The immediate gap is exposure evidence, not a replacement memory product. | Exercise a real bound `maps run send-context --deliver-context` path and capture the first `BEFORE_SEND` / memory-provenance guard decision. Add poisoning/stale-memory cases only after that path is real. |
| **6.24 Least-privilege capability intersection** | **STRENGTHEN** | Current intersection model aligns with DSH/Noriq and security standards. Pilot research adds useful distinctions among requested config, effective runtime, agent/session identity, credential reference, and delegated authority. | Complete a real end-to-end production exposure of the existing intersection; then add only the missing effective-runtime/delegation/credential cases proven relevant. |
| **6.33 Semantic retrieval / query expansion** | **DEFER** | Current `EVIDENCE-GATED` / evaluation-only posture remains supported. Research provides better provenance/authority criteria but no evidence that a production semantic layer is currently worth its complexity. | Keep explicit-first production behavior. Promote only if frozen context/routing evaluations show a material failure that semantic/query expansion improves without unacceptable hard-negative/authority regressions. |
| **6.35 Portable deployment to external projects** | **CHALLENGE** | Portable deployment itself remains high-value. The narrow challenge is the current v1 choice of **file-convention-only task truth + best-effort review**: it intentionally gives up atomic claim/lease and mechanical no-self-review guarantees that current MAPS and the external durability/review evidence treat as important. Do not redesign from theory; test the assumption. | After cheap 6.4/6.22 closure, run a bounded real external-pilot preflight: can a fresh agent complete one real target task with recoverable owner/status, independent review, exact evidence, and no transcript dependency using the file-only profile? If yes, keep v1. If ambiguity/self-review/recovery failure appears, compare the smallest thin mechanical adapter against the file-only profile before expanding the pilot. |
| **6.12 Capability Packs** | **KEEP** | The roadmap already marks this `TRIGGERED/P2` and says to wait until Skills + Harness API + EnvironmentSpec are stable and one/two domains demonstrate bundling value. Upstream protocol/capability work does not itself create that need. | Trigger only on repeated real composition pain, likely after an external pilot. |
| **6.17 Sandboxes / snapshots / rehydration** | **KEEP** | Current `TRIGGERED` posture is reinforced: the environment roadmap explicitly says declarative reproducibility first and “do not build snapshot infrastructure immediately.” DSH/Restate provide ready evidence/tests if a real isolation/recovery trigger appears. | Trigger on measured setup/recovery cost, remote/untrusted execution, or containment need; evaluate smallest sandbox/snapshot experiment then. |
| **6.25 Credential broker** | **KEEP** | The security roadmap already says broker experimentation is later-stage unless credential-bearing work becomes common/high-risk. DSH and identity/security research validate the target design but do not prove a current MAPS incident/need. | Trigger before broad credential exposure becomes routine or an external/untrusted execution path needs scoped secret use. |
| **6.31 Controlled harness refinement** | **KEEP** | Master roadmap already labels it `EVIDENCE-GATED / LAST`. The large failure/test corpus improves the future evaluation substrate; it is not a reason to start autonomous refinement early. | Start only when stable outcome/eval evidence supports a specific candidate comparison; preserve reviewed promotion/rollback. |
| **6.32 Time-travel / fork debugging** | **KEEP** | Current `TRIGGERED` narrow design is supported. Temporal/DSH/LangGraph give useful checkpoint/fork semantics, but deterministic replay of model thought remains unnecessary. | Trigger on a concrete debugging/evaluation case that cannot be answered from current Run Records/frozen fixtures. |
| **6.34 Mission / multi-task goal object** | **KEEP** | Current master decision is explicit: do not create a separate goal database while project IDs, dependencies, decisions and outcomes are sufficient. Nothing in Pilot research overturns that. | Reconsider only if a real cross-task objective cannot be represented/recovered with current project/task/root structures without duplication. |

## Consequences for sequence

### Immediate — prove what already shipped

1. **6.4** first real destructive-action hook exposure.
2. **6.22** first real context-send/memory-provenance guard exposure.
3. Reconcile the exact rows from observed evidence; do not infer DONE from implementation existence.

These remain first because current `docs/wiki/Development.md` and trajectory check #26 already identify them as the immediate evidence gaps, and the Pilot corpus does not provide a reason to skip them.

### Next — one bounded hardening gate before the external pilot

4. Prefer a cheap **6.24** end-to-end least-privilege exposure if it can be exercised without opening another multi-PR design chain.
5. Keep 6.10/6.11/6.19/6.20/6.21 as strengthened owners; select among them only when a concrete dependency or observed failure makes one the highest-value task.

### System-level proof

6. **6.35 external pilot preflight + real pilot** becomes the strongest candidate for the next broad proof after cheap local closures.
7. Use the pilot to test—not assume—the file-convention-only/best-effort-review v1 profile.
8. Let pilot evidence pull forward 6.11, 6.17, 6.19, 6.20, 6.21, 6.25 or 6.12 only when a real need appears.

This makes the external pilot a prioritization instrument rather than a victory lap.

## Workflow bootstrap: borrow before build, conditionally

The current orchestration loop is retained:

```text
PROGRAM_STEERING
→ task shaping / AGI readiness
→ implementation + deterministic verification
→ independent review
→ ROADMAP_TRAJECTORY_CHECK
→ friction + emergence consumption
```

Add one conditional evidence step **inside Program Steering**, before shaping self-selected work that creates or materially changes a reusable/general mechanism:

```text
candidate reusable mechanism
→ recover current MAPS owner
→ inspect relevant existing MAPS research
→ inspect relevant Pilot packet/source/fix-history/tests when available
→ state reuse/adapt/evaluate/custom posture
→ state known failure cases + smallest discriminating test
→ shape task
```

Trigger examples:

- ownership/lease/fencing/recovery;
- scheduling/backpressure;
- context/memory/retrieval;
- provider/runtime abstraction;
- approval/reviewer/identity/credential authority;
- budget/resource enforcement;
- external-effect/idempotency semantics;
- sandbox/containment;
- protocol/tool interoperability;
- artifact/supply-chain provenance.

Skip for:

- routine local bug fixes;
- documentation corrections of already-established behavior;
- review/revalidation;
- straightforward application of an accepted mechanism;
- work where the current owner already contains the needed evidence and no design choice is reopened.

The check is an evidence-quality safeguard, not a second approval gate and not a requirement to browse the full Pilot corpus.

## What this does not recommend

- no DBOS/Restate/Temporal migration;
- no second task database;
- no universal event-sourcing rewrite;
- no Letta memory adoption;
- no mandatory containers/snapshots;
- no immediate credential broker;
- no semantic/vector retrieval promotion;
- no new Mission object;
- no action on PR #319;
- no capability status flip from research.

## Review questions

Independent review should specifically challenge:

1. Are all 16 unfinished master rows represented exactly once?
2. Does any `STRENGTHEN` recommendation silently change current authority/design rather than add evidence/tests?
3. Is 6.35's `CHALLENGE` genuinely a bounded discriminating test rather than a disguised redesign?
4. Does the borrow-before-build insertion duplicate an existing MAPS method or create routine ceremony?
5. Does any wording depend on PR #319's unmerged supersession authority?
6. Does the proposed sequence preserve 6.4/6.22 as the immediate evidence closures named by current MAPS state?

## Disposition

`READY FOR INDEPENDENT REVIEW`.

This note is a dated evidence/reasoning record. It does not become the canonical capability status overlay and should not be refreshed as a live status file.