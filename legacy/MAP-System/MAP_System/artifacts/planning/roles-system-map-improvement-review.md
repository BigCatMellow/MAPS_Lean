<!-- hpom: file: artifacts/planning/roles-system-map-improvement-review.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: codex-lab-lura -->
<!-- hpom: status: REVISED_PENDING_REREVIEW -->
<!-- hpom: last_verified: 2026-07-26 -->
<!-- hpom: verified_against: TASK-277, roles_in_MAP_system.md, live map.db, current MAP rules/runtime/experiments -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Role-System Review And MAP Improvement Roadmap

- Task: `TASK-277`
- Original author: `codex-lab-kazu`
- Revision owner: `codex-lab-lura`
- Source: `/home/mellow/Projects/MultiAgentProject/roles_in_MAP_system.md`
- Scope: reusable MAP system
- Status: revised after independent review; recommendations not yet adopted
- Decision authority: `command-center`

## Executive Finding

The document makes real progress. It begins with the limited question “should
agents pretend to be professions?” and ends with a coherent operating model:

1. stable organizational roles define authority and responsibility;
2. skills supply task-specific procedures;
3. tasks declare capabilities, scope, evidence, and limits;
4. routing selects a worker/model without embedding that identity in the role;
5. immutable run manifests record exactly what one execution saw;
6. submissions make criterion-level claims backed by evidence;
7. fresh reviews independently verify those claims;
8. deterministic runtime controls permissions and state;
9. compact fingerprints and workstream digests carry useful history forward.

That final model is directionally stronger than MAP's current role handling.
MAP already implements much of the safety backbone, but its role field is
free-form, its routing still mixes worker identity with role/capability, and it
cannot reproduce the exact instruction/context packet used for a run. More
urgently, its current no-self-review checks key on task owner rather than a
durable submission author, so ordinary owner/author drift can let the actual
author pass the nominal separation checks.

The best next move is not to recreate the proposed `.map/` tree. It is to adopt
the missing contracts and runtime behavior incrementally inside the current
architecture.

## Progression In The Source

| Stage | Useful development | Review |
|---|---|---|
| Persona question | Rejects “pretend you are a programmer” as redundant. | Correct. MAP needs operating contracts, not character prompts. |
| Functional seats | Separates DRI, Scout, Implementer, Reviewer, Escalation, local support, and deterministic runtime. | Strong, provided seats are temporary roles rather than permanent agent identities. |
| Superhero analogy | Clarifies each seat's primary question and prevents overlapping responsibility. | Useful as teaching material; aliases should not become canonical schema values. |
| Global/project split | Separates reusable rules from project-local intent, work, evidence, and memory. | MAP already follows this pattern through root/MAP/project-local systems; a filesystem migration is unnecessary. |
| Constitution/role/skill/task templates | Gives stable, comparable contracts and explicit precedence. | Strongest documentation layer, but should consolidate current rules rather than duplicate them. |
| Capability routing and run manifests | Separates task need, role, harness, and model; records exact supplied context. | Highest-value missing runtime design. |
| Submission/review/fingerprint/digest | Separates claims from verification and full evidence from compact memory. | Strong and compatible with MAP's existing task/review/retrieval work. |

## Current MAP Fit

| Proposal | Current state | Evidence | Assessment |
|---|---|---|---|
| Universal constitution | Present under another name | `AGENTS.md`, decision/risk/security systems | Do not add a second constitution. Add only missing precedence and completion language to the canonical rules. |
| Stable role contracts | Missing operationally | `tasks.role` is unconstrained text; live DB has 40+ distinct values, including model names and sentence-like roles | Adopt a small stable role vocabulary and validate it. |
| Skills separate from roles | Partial | Procedural guides exist in `notes/`; Codex skills exist outside MAP, but tasks do not select MAP skill IDs | Add a registry/selection contract only after proving a small set of reusable procedures. |
| Capability-based routing | Partial | `shared/hpom.md`, capability matrix, pre-dispatch policy; runner helper-fit logic uses task type/role/keywords | Separate role, capability need, worker alias, provider, and model tier. Do not hard-code model names into task history. |
| Explicit readable/writable/forbidden scope | Partial | output paths are enforced as ownership metadata; task authoring requires input/output paths; no runtime path permission boundary exists | Add schema and preflight first; enforcement must be deterministic before calling it containment. |
| Immutable task revision | Missing | task row has no revision and files are mutable projections | Required before reproducible run manifests and review of “the packet actually implemented.” |
| Exact run/context manifest | Experimental only | Context System, context packet template, STATE_SNAPSHOT, EXP-0004/0005 orientation-manifest evidence | Promote a minimal manifest experiment. The refined treatment preserved all six safety facts at ~94% fewer bytes, but explicitly did not authorize production adoption. |
| Base/result revision provenance | Mostly missing | Git wrapper and release artifacts exist; task schema does not bind a run to base/result commit | Add when a run manifest exists; do not require commits for non-Git/document-only work. |
| Criterion-level submission claims | Partial | task criteria, delivery notes, events, and review artifacts exist; submission is primarily a lifecycle transition and currently clears `claimed_by` without preserving canonical submitter identity (`TASK-274`, `INS-0039`) | First preserve durable submission authorship; then add structured claimed results and evidence references without replacing human-readable delivery notes immediately. |
| Fresh independent review | Material integrity gap | `claim_review()` atomically prevents duplicate open reviews, but compares the reviewer only with `tasks.owner`; approve/reject has no database-backed submission-author guard; `validate_review.py` trusts artifact-supplied owner text | Treat three controls separately: duplicate-review arbitration already exists; author-keyed no-self-review enforcement is missing and urgent; fresh run/session independence is also missing but follows durable run identity. Role normalization alone fixes none of these. |
| Deterministic “Watchtower” | Strong partial | SQLite claims, leases, policy gates, mirrors, review/release gates, validators | Continue moving critical invariants from prose to code: path scope, evidence existence, task revision, run identity, retry limits. |
| Append-only run event stream | Partial | project event log exists | Do not log every file read by default. Capture only events needed for safety, provenance, debugging, and cost/yield analysis. |
| Task fingerprints | Proven promising, not production-ready | TASK-256 pilot: 100% expected-task recall@6; primary-source ranking was weaker | Continue source-aware retrieval work before making fingerprints the default first context source. |
| Workstream digests | Missing/implicit | compactions, current-state, synthesis, and handoffs partially serve this purpose | Pilot only where several released tasks share a durable capability; generate from canonical evidence and review for stale claims. |
| Machine-generated active views | Partial and urgently needed | SQLite/file mirrors plus TASK-276 validator; active-lane table remains hand-maintained and drifts on every transition | Generate the operational lane projection from SQLite; keep prose rationale separate. |

## Recommended Target Model

Keep the present repository layout and introduce five distinct identities:

| Identity | Meaning | Example |
|---|---|---|
| `role_id` | Stable responsibility contract | `delivery-implementer`, `independent-reviewer`, `scout`, `shaper`, `state-steward` |
| `capability_requirements` | What the task needs | code edit, cross-file reasoning, visual inspection, security review |
| `worker_id` | Accountable/live execution identity | `codex-lab-kazu` |
| `provider/model_tier` | Resource used for the run | Codex core, Claude Sonnet helper, local advisory |
| `run_id` | One immutable execution attempt | `RUN-TASK-277-01` |

Submission records must also retain the authoring `worker_id` and `run_id`.
Those canonical fields—not current task owner and not reviewer-authored
artifact text—must drive no-self-review enforcement.

The relationship should be:

```text
task declares role + capabilities
  -> HPOM selects worker/provider/model tier
  -> runtime creates immutable run manifest
  -> worker produces criterion-level submission claims
  -> independent run verifies claims
  -> runtime performs state transition
```

This preserves HPOM's “cheapest competent worker” rule while preventing worker,
model, role, and authority from collapsing into one ambiguous field.

## Prioritized Roadmap

### P0 — Preserve submission authorship and enforce review separation

- Finish durable submission authorship (`TASK-274`) before strengthening the
  terminal review gate.
- Record the submission author's worker/session identity and, once available,
  run ID without erasing it during the `SUBMITTED` transition.
- Key `claim_review()`, approve/reject, and review validation to that canonical
  author record. Keep the existing atomic open-review claim as the separate
  duplicate-work control.
- Reject reviews where the reviewer matches the submission author even when
  task ownership has changed; do not trust artifact-supplied owner fields as
  the authority.

Verification:

- an author cannot claim or complete review after owner reassignment;
- an independent reviewer can review when owner and author differ;
- submission, rejection, rework, and resubmission preserve auditable author
  history;
- existing duplicate-review arbitration still admits only one open claimant.

Why first: this is an exercised integrity failure, not a speculative identity
improvement. Current sanctioned submission destroys the value needed to enforce
the intended no-self-review rule.

### P0 — Generate active operational state

- Split the current active-lane surface into:
  - generated lifecycle fields from SQLite;
  - compact human-authored rationale/gate annotations keyed by task ID.
- Generate the table or Command Center view; retain TASK-276 as a projection
  consistency test during migration.

Verification:

- claim, submit, approve, and release transitions update the displayed status
  without a hand edit;
- rationale survives regeneration;
- no free-prose task mention is treated as lifecycle truth.

Why first: this fixes an observed failure that occurred five times in one day.

### P1 — Normalize role semantics

- Define 5–7 stable role IDs: `shaper`, `scout`, `delivery-implementer`,
  `independent-reviewer`, `state-steward`, `researcher`, and
  `escalation-analyst`.
- Put model/provider preferences in HPOM routing, not `tasks.role`.
- Add role schema validation and a compatibility mapping for historical
  free-form roles; do not rewrite old task history.
- Give each role one compact contract with consistent headings: Mission, Owns,
  May, Must, Must not, Required input/output, Escalate, Complete when.

Verification:

- new tasks reject unknown role IDs;
- current historical tasks still load through compatibility mode;
- runner decisions use normalized roles rather than keyword fragments.

Why now: the current field cannot reliably drive routing, permissions, or
reporting while it contains model names and one-off prose. This improves
operational semantics, but it is not a prerequisite or substitute for
submission-author review separation.

### P1 — Add task revision and minimal run manifests

- Add immutable task revision/hash at dispatch.
- Record run ID, task revision, worker/session identity, role ID, selected
  skills, base revision where applicable, context references with hashes,
  writable scope, and runtime limits.
- Store references and hashes, not copied full context.
- Pilot on one bounded task before making manifests mandatory.

Verification:

- a reviewer can identify the exact task/context revision used;
- stale task/context changes are detected;
- manifest generation adds materially less context than the full source stack;
- no manifest becomes a competing canonical source.

### P1 — Make remaining submission evidence structured

- Extend the P0 canonical submission-author record beyond a generic
  `SUBMITTED` event.
- Record `claimed_status` per acceptance-criterion ID plus evidence references.
- Keep reviewer results separate and use `verified_status`.
- Link both records to task revision and run ID.

Verification:

- submission cannot claim a criterion with missing required evidence;
- review can reject one criterion without rewriting the implementation;
- implementer claims and reviewer/runtime verification remain visibly distinct.

Dependency: finish the P0 durable-authorship/author-guard slice and lifecycle
consistency work (`TASK-268`) first.

### P2 — Enforce scope and budgets deterministically

- Add explicit readable/writable/forbidden path fields.
- Begin with dispatch validation and post-run diff checks.
- Add hard harness containment only where the execution environment can
  genuinely enforce it.
- Attach maximum attempts/tool failures/runtime to the run, not the permanent
  role.

Verification:

- out-of-scope writes fail or block submission;
- scope expansion requires a recorded transition;
- retry exhaustion produces an escalation artifact rather than an endless loop.

### P2 — Promote retrieval outputs carefully

- Continue the source-aware fingerprint experiment; do not productionize the
  task-only ranking as complete retrieval.
- Generate a compact task fingerprint after release from canonical task,
  submission, review, and decision evidence.
- Pilot workstream digests after a threshold of related released tasks.

Verification:

- frozen holdout measures task recall, primary-source recall, abstention, and
  token reduction;
- digests preserve decisions, repeated failures, key files, and open risks;
- raw evidence remains retrievable.

## Do Not Adopt As Written

1. **Do not create a parallel `~/.map` installation now.** MAP already has a
   reusable/project-local split. A migration would create two authorities before
   behavior improves.
2. **Do not add `CONSTITUTION.md` beside `AGENTS.md`.** Merge missing rules into
   the existing canonical contract.
3. **Do not make Sonnet the permanent DRI or Codex the permanent builder in
   schema.** Roles describe responsibility; HPOM chooses workers by current
   capability and availability.
4. **Do not deploy the entire seat roster for routine work.** Risk-tiered review
   and direct small-task execution should remain.
5. **Do not log every read or complete internal transcript.** This creates cost,
   privacy, and noise without improving most decisions.
6. **Do not claim path containment until the runtime enforces it.** Prompt rules
   and output-path metadata are not a security boundary.
7. **Do not auto-promote local models through a fixed five-level ladder.**
   Capability must be proven per task shape with frozen evaluations, and
   authority remains bounded even when quality improves.
8. **Do not generate fingerprints or digests as unquestioned truth.** They are
   retrieval projections and must link back to canonical evidence.
9. **Do not create one role per profession or one skill per incidental
   technique.** Add a role only for a distinct authority/responsibility contract
   and a skill only after repeated reuse.

## Proposed Implementation Sequence

| Order | Deliverable | Risk | Prerequisite |
|---|---|---|---|
| 1 | Durable submission author record plus author-keyed claim/review enforcement | PROCESS / STRUCTURAL | TASK-274; migration for existing open submissions |
| 2 | Generated active-lane projection with separate annotations | PROCESS / DRIFT | TASK-276 evidence |
| 3 | Stable role registry, role contracts, compatibility mapper, validator | PROCESS / DRIFT | independent architecture review |
| 4 | Task revision + minimal run-manifest experiment | KNOWLEDGE / STRUCTURAL | EXP-0005 evidence; context system |
| 5 | Submission record with criterion/evidence claims | PROCESS / STRUCTURAL | author record; TASK-268 |
| 6 | Post-run scope verifier and retry/escalation envelope | SECURITY/PROCESS / STRUCTURAL | run manifest |
| 7 | Source-aware fingerprint production pilot | KNOWLEDGE / DRIFT | current retrieval holdout iteration |
| 8 | Workstream digest pilot | KNOWLEDGE / DRIFT | reliable fingerprints and one mature workstream |

Do not combine these into one framework rewrite. Each deliverable should have a
separate task, migration/compatibility plan, focused tests, and independent
review.

## Bottom Line

The source's final architecture should influence MAP. Its central insight is
that roles are temporary authority contracts, not personas or model identities,
and that trustworthy execution needs an inspectable chain from task revision to
run context to claimed evidence to independent verification.

MAP's safest adoption path is evolutionary:

- preserve submission authorship and enforce author-keyed review separation;
- generate operational projections;
- normalize role semantics;
- make runs reproducible;
- make submission evidence structured;
- then strengthen containment and compact memory.

That sequence improves behavior and directly addresses observed MAP failures
without replacing the working system with a speculative new directory tree.
