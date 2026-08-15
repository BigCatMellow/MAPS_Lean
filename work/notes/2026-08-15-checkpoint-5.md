# Development checkpoint 5 — 2026-08-15

Status: `WORKING NOTES — NOT ACTIVE AUTHORITY`

This supplements earlier handoff/checkpoint notes. Canonical code, task state, active instructions, PR state, and reviewed decisions remain authoritative.

## Operator direction still in force

- Continue downstream work while upstream draft PRs await independent review when dependencies are explicit and the next task does not require the review result.
- Keep stacked dependencies visible.
- CI success is evidence, not approval.
- Do not self-approve, mark ready, or merge review-gated work.
- Keep durable notes during long implementation sessions.

---

# Newly verified since checkpoint 4

## PR #30 — append-only run environment evidence

Branch:

`agent/environment-run-evidence-wave2`

Stack:

```text
main
→ PR #28 EnvironmentSpec v1
→ PR #29 EnvironmentFingerprint/compatibility v1
→ PR #30 run environment evidence
```

Implementation commit:

`cf47e82f58586091becc5d298f27833ae97f0aac`

Full Runtime stack CI:

`31898071184` — success

Validation/task-record head after CI:

`862e8bebe852ed6cea4ad0fd69c8bcc4c4251955`

Task:

`work/tasks/environment-run-evidence-wave2.md` → `READY_FOR_REVIEW`

Implemented:

- new append-only `run_environment_evidence` table;
- existing `run_manifests` schema/immutability remains unchanged;
- evidence row preserves:
  - run ID;
  - spec reference;
  - exact EnvironmentSpec hash;
  - fingerprint hash;
  - compatibility state;
  - optional reference fingerprint hash;
  - normalized EnvironmentSpec snapshot;
  - bounded EnvironmentFingerprint snapshot;
  - internally derived compatibility report;
  - recorder identity/time;
- multiple observations append rather than replace;
- UPDATE/DELETE blocked by SQLite triggers;
- evidence recording does not alter task status, claim, lease, heartbeat, policy, review, or run manifest;
- `EnvironmentEvidenceMixin.trace_task()` extends existing read-only trace through MRO composition so evidence appears under the exact run;
- event summaries contain only run/evidence identity + compatibility state.

Important persistence discovery/fix:

EnvironmentSpec commands are data and could accidentally contain a credential literal. Because the exact spec snapshot/hash must remain meaningful, E3 does **not** redact a spec before storing it. Instead, persistence runs the existing sensitive-text detector over `spec_ref` and all normalized snapshots and rejects the evidence record if likely sensitive text is present.

Critical invariant:

> Environment compatibility is evidence, not authority. E3 does not automatically resume, stop, claim, renew, or block tasks.

Do not add environment-based recovery gating until a later guarded integration task explicitly defines the authority boundary.

## PR #31 — static Skill quality/security gate

Branch:

`agent/skills-quality-gate-wave2`

Stack:

```text
main
→ PR #25 Skills format
→ PR #26 Skills catalog/provenance
→ PR #27 frozen selection eval
→ PR #31 static quality/security gate
```

Implementation commit:

`d3d186dbd0903eacd4dbe715335bf2560b1c74d3`

Full Runtime stack CI:

`31898263690` — success

Validation/task-record head:

`e45d74a256d9f215fee49cff8abeb0ac3dfaaf38`

Task:

`work/tasks/skills-quality-gate-wave2.md` → `READY_FOR_REVIEW`

Implemented:

- `assess_skill()` static read-only gate;
- verifies exact Skill hash has not drifted before scanning;
- never executes scripts/resources;
- bounded findings with severity:
  - `INFO`
  - `REVIEW`
  - `BLOCK`
- dispositions:
  - `CLEAR`
  - `REVIEW_REQUIRED`
  - `QUARANTINE`
- **no disposition means approved/trusted**;
- review findings include:
  - executable resource presence;
  - binary/non-UTF8/oversized resources;
  - vague routing descriptions;
  - roleplay/persona-heavy instructions;
  - privilege operations;
  - destructive operations;
  - broad process/environment credential access;
  - script network access;
- quarantine findings include:
  - likely secret literals;
  - sensitive credential/key resource names;
  - authority/policy override claims;
  - fake approval/permission claims;
  - remote-download piped directly into shell/interpreter;
- findings return code/path/summary only, never matched secret/source snippets;
- adversarial tests prove script resources are read but not executed.

Critical invariant:

> Static scan is an early filter, not proof of safety. `CLEAR` is not approval.

Persistent Skill approval/trust/quarantine authority remains deliberately deferred until its lifecycle and operator/reviewer authority are explicitly reviewed.

---

# Current verified capability set

CI-green implementation tranches now exist for:

1. typed provider-neutral Harness contracts;
2. hcom normalization;
3. deterministic Hooks;
4. HarnessService;
5. canonical run/lease/session continuation guard;
6. initial agentic security adversarial baseline;
7. Agent Skills format/progressive-loading foundation;
8. Skill catalog/provenance read model;
9. frozen Skill-selection evaluation corpus;
10. static Skill quality/security gate;
11. EnvironmentSpec v1;
12. EnvironmentFingerprint/compatibility v1;
13. append-only run-environment evidence + trace projection.

All remain subject to their stated independent review gates.

---

# Deliberately unresolved / deferred boundaries

## Durable session lineage

Still unresolved:

- late session attachment;
- replacement session lineage;
- helper lineage joins;
- durable session/run reconciliation.

Do not create a hidden mutable second session authority to solve these.

## Skill approval/trust lifecycle

Still unresolved:

- who can approve a Skill;
- what independent review is required;
- whether approval is local/project/global;
- expiry/supersession;
- how a changed hash invalidates approval;
- how quarantine is persisted and lifted.

Static S5 gate does not answer these and must not be treated as approval.

## Production Skill routing

Still unresolved/promotion-gated:

- candidate selector strategy;
- acceptable precision/recall/false-activation thresholds;
- model/provider independence;
- Context Builder integration.

PR #27 provides the frozen benchmark. Production routing should not be added until candidate strategies are measured against it and independently reviewed.

## Environment-driven recovery/continuation

E1–E3 provide requirements, observations, compatibility evidence, and run binding. They do not grant recovery authority. A later integration must combine environment evidence with canonical task/run/session/policy state.

## Environment validation execution

EnvironmentSpec contains quick/normal/full commands as data only. A runner for those commands should integrate with Harness/Hook authority rather than becoming an independent command-execution path.

---

# Recommended next work

Prefer one of these evidence-first tasks rather than creating new authority state:

1. **Review/evidence revision binding** — ensure reviewers approve the exact source/artifact/evidence revision tested, using existing immutable run/criterion evidence rather than stale prose.
2. **Portable Run Record read model** — assemble task/run/environment/review/outcome evidence without claiming missing hcom/helper lineage is complete.
3. **Skill selector experiment only** — compare one or more candidate selectors against frozen PR #27 corpus; do not integrate production routing.
4. **ACI/tool-result hardening follow-up** — apply normalized operation-result semantics to another concrete existing MAPS tool surface.

Avoid next:

- persistent Skill approval state without explicit authority design;
- automatic environment recovery gating;
- environment command runner outside Hooks/Harness;
- autonomous Skill routing without measured benchmark results;
- second session/task authority store.
