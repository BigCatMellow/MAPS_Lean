# Competitive systems mechanisms — security and authority — 2026-09-04 to 2026-09-09

Status: `RESEARCH — NOT ACTIVE AUTHORITY`

Main question: **Which public approval, reviewer-lineage, sandbox, credential, budget, external-effect, and supply-chain mechanisms should strengthen MAPS_L's existing authority/security model?**

## Evidence snapshot

Deep extraction owner: `BigCatMellow/Pilot_Projects` PR #5 at `f6d584465e15b0fcf3cd09fea9e056bc23852e94`.

- Security/source index: https://github.com/BigCatMellow/Pilot_Projects/blob/f6d584465e15b0fcf3cd09fea9e056bc23852e94/complete-ai-work-system/research/competitive-architecture/production-accelerators/SOURCE_INDEX.md
- Approval packet: https://github.com/BigCatMellow/Pilot_Projects/blob/f6d584465e15b0fcf3cd09fea9e056bc23852e94/complete-ai-work-system/research/competitive-architecture/production-accelerators/P0-APPROVAL-AUDIT-FAIL-CLOSED.md
- Sandbox packet: https://github.com/BigCatMellow/Pilot_Projects/blob/f6d584465e15b0fcf3cd09fea9e056bc23852e94/complete-ai-work-system/research/competitive-architecture/production-accelerators/P0-SANDBOX-PATH-ENFORCEMENT.md
- External-effect packet: https://github.com/BigCatMellow/Pilot_Projects/blob/f6d584465e15b0fcf3cd09fea9e056bc23852e94/complete-ai-work-system/research/competitive-architecture/production-accelerators/P0-EXTERNAL-EFFECT-RECEIPTS.md
- Supply-chain packet: https://github.com/BigCatMellow/Pilot_Projects/blob/f6d584465e15b0fcf3cd09fea9e056bc23852e94/complete-ai-work-system/research/competitive-architecture/production-accelerators/P1-SUPPLY-CHAIN-ARTIFACT-PROVENANCE.md

## Findings that strengthen existing MAPS_L security design

### 1. Human approval should activate one scoped grant, not bless an agent

DeepSeek Harness provides concrete fail-closed approval prior art:

- fresh approval identity per request;
- durable `asked -> decided` audit pairing;
- missing/broken approver -> unavailable, not allow;
- only the explicit allow outcome grants the requested action;
- if the audit pair cannot be durably recorded, the decision is not treated as safely usable.

MAPS_L can go further by binding consequential approval to the exact task/run revision, target/action, expiry/use count, resource envelope, and relevant capability.

**MAPS_L implication:** this strengthens current target-scoped approval and authority-intersection design. It does not require a new global approval service.

### 2. Reviewer independence needs runtime lineage, not labels

Taskplane, Optio, GitHub review semantics, and MAPS_L's existing review-evidence work all support the same rule:

```text
"reviewer" role label
!=
independent reviewer evidence
```

Useful eligibility dimensions include:

- producer lineage;
- reviewer execution/session lineage;
- exact artifact revision;
- actual model/runtime when policy cares;
- whether reviewer mutated the artifact;
- whether fallback changed the intended independence condition.

**MAPS_L implication:** preserve exact-revision review evidence and fail closed on ambiguous lineage. Competitor failures provide regression cases, not a replacement review system.

### 3. Sandbox is a vector of enforcement properties, not a boolean

DSH explicitly distinguishes requested sandbox mode from actual enforcement and can report `full` versus `partial`. Its filesystem containment tests emphasize realpath/symlink resolution rather than lexical prefix checks.

Hermes and other runtimes reinforce that filesystem isolation, process isolation, network isolation, credential isolation, and resource limits are separate questions.

**MAPS_L implication:** if 6.17 is triggered, specify exactly which properties a sandbox provider enforces and test path/symlink escapes. Do not treat container/sandbox presence as equivalent to trust or full containment.

### 4. Credentials should be resolved as scoped capability per operation

DSH/Hermes patterns separate configuration references from actual secret resolution. Credentials can be rotated and resolved at the operation boundary rather than copied permanently into long-lived agent state.

**MAPS_L implication:** this supports the current future credential-broker direction in 6.25. Keep it triggered; use this evidence if/when real credential-bearing work demonstrates the need.

### 5. Hard spend limits need atomic conservative reservation

LiteLLM implements budget reservation but its public failures show several ways "hard budget" can fail in practice:

- concurrent reservations race;
- a scope is omitted from the reservation counter;
- provider/request route cannot be priced up front;
- cache/Redis state diverges from authoritative DB state;
- temporary/multi-window limits follow a different enforcement path;
- oversized request reservation is reduced to remaining headroom and still admitted, allowing actual settled spend above the configured cap.

If MAPS_L later enforces hard paid-resource limits, the safer property is:

```text
conservative maximum cost of next operation
<=
remaining authorized hard budget
```

or reject. Unknown cost/state should not silently fail open when a hard ceiling is part of authority.

This is future security/evaluation input; it does not justify building budget infrastructure now.

### 6. Timeout/cancel is not proof that an external effect did not happen

Across provider/runtime systems, a consequential external operation can succeed after local cancellation or before acknowledgement is lost.

Useful state distinction:

```text
planned
→ authorized
→ dispatching
→ confirmed accepted / confirmed rejected / OUTCOME_UNKNOWN
```

`OUTCOME_UNKNOWN` should trigger reconciliation against the authoritative external system before retry where duplication matters.

Compensation is another fallible operation; it is not magical rollback.

**MAPS_L implication:** strengthen future external/deploy/write operations and recovery semantics with explicit operation identity/effect evidence. This can coexist with existing hook/authority design.

### 7. Supply-chain provenance should reuse mature standards instead of a MAPS-specific signing scheme

Relevant standards divide responsibilities:

- **Sigstore**: artifact signing identity + transparency evidence;
- **SLSA**: build/provenance assurance levels;
- **in-toto**: authorized steps/functionaries/materials/products;
- **TUF**: update metadata, freshness, threshold trust, rollback/freeze/mix-and-match resistance.

Important boundary:

```text
signed/proven artifact
!=
safe artifact
!=
approved MAPS artifact
!=
authorized execution for this task
```

**MAPS_L implication:** 6.10 Skill/tool provenance and future Capability Packs/snapshots should reuse these semantics where valuable rather than invent custom crypto/update protocols.

## Portable security regression cases

1. stale approval from prior task revision -> cannot authorize current action;
2. approval for target A replayed for target B -> denied;
3. approver unavailable/malformed result -> fail closed;
4. reviewer shares producer continuity despite different role label -> ineligible;
5. reviewer requested model differs from actual spawned model where cross-model policy matters -> evidence mismatch;
6. sandbox lexical path looks allowed but symlink resolves outside scope -> denied;
7. sandbox provider reports partial enforcement while task requires full -> refuse/unknown;
8. credential rotates during long-lived run -> next operation resolves current scoped credential without writing secret into durable task text;
9. hard budget remaining below conservative max next request -> reject before provider dispatch;
10. budget store unavailable for explicitly hard-ceiling work -> fail closed rather than dispatch;
11. external action times out after dispatch -> state is unknown until target-system reconciliation;
12. signed imported Skill changes capabilities -> provenance alone does not auto-activate it.

## MAPS_L roadmap mapping

- 6.4 deterministic hooks -> approval/external-effect/security-hook semantics;
- 6.10 Skill trust -> provenance, update/revalidation, supply-chain standards;
- 6.17 sandbox -> explicit enforcement dimensions + path escape tests;
- 6.22 memory trust -> authority/provenance remains stronger than retrieved/persistent text;
- 6.24 least privilege -> effective capability intersection and exact target/action evidence;
- 6.25 credential broker -> per-operation secret resolution if triggered;
- 6.35 portable deployment -> external-project review/authority boundaries should be observed, not assumed.

## Disposition

`STRENGTHEN_EXISTING_OWNER / PORTABLE_TEST_INPUT`.

No new authority follows from these systems. Their value is concrete failure history and implementation-backed semantics that MAPS_L can reuse when the owning security mechanism is touched.