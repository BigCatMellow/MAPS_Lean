# Development checkpoint 4 — 2026-08-15

Status: `WORKING NOTES — NOT ACTIVE AUTHORITY`

This supplements the earlier 2026-08-15 handoff/checkpoint notes. Canonical code, task state, active instructions, PR state, and reviewed decisions remain authoritative.

## Operator direction still in force

- Continue downstream work while upstream draft PRs await independent review when the dependency is explicit and the next step does not require the review result.
- Keep stacked dependencies visible.
- Do not self-approve, mark ready, or merge review-gated work merely because CI passed.
- Keep writing durable notes during long implementation sessions.

---

# Current verified development topology

## Harness / security stack

```text
main
→ PR #20 harness typed foundation
→ PR #21 hcom normalization + Hook registry
→ PR #22 HarnessService
→ PR #23 canonical run/lease/session guard
→ PR #24 initial agentic security adversarial baseline
```

All implementation tranches #20–#24 have successful full Runtime stack CI on their recorded implementation commits. They remain draft / independently reviewable.

Important unresolved boundary:

- durable late session attachment/replacement/helper lineage is still intentionally unresolved;
- do not create a hidden mutable session authority to solve it;
- provider/session liveness still cannot revive task authority.

## Skills stack

```text
main
→ PR #25 Agent Skills format foundation
→ PR #26 Skills catalog/provenance read model
→ PR #27 frozen Skill-selection evaluation corpus
```

### PR #27 — frozen Skill-selection evaluation

Implementation commit:

`7175282c25584761f52059b36282c1f062d185c0`

Full Runtime stack CI:

`31897351677` — success

Validation/task-record head:

`f6d6685b4396829cc71e67144a3ca0951f1d8b52`

Task:

`work/tasks/skills-selection-eval-wave2.md` → `READY_FOR_REVIEW`

Implemented:

- frozen `skill-selection-v1` corpus;
- five synthetic Skill candidates;
- 24 inspectable task cases;
- categories: direct, paraphrase, vocabulary shift, near miss, hard negative, no-Skill, multi-Skill, ambiguity;
- explicit prediction outcomes: `SELECT`, `ABSTAIN`, `AMBIGUOUS`;
- strict prediction validation;
- exact-case, precision/recall/F1, abstention, ambiguity, false-activation, missed-activation, and category metrics;
- deterministic corpus hash in every report.

Critical boundary:

> The evaluator scores predictions produced elsewhere. It contains no production Skill selector and cannot activate a Skill.

Next safe Skills work:

- candidate selectors may be implemented/evaluated as experiments against this frozen corpus;
- do **not** integrate autonomous Skill routing into Context Builder/runtime until measured results justify a specific approach and review accepts the promotion.

## Environment / reproducibility stack

```text
main
→ PR #28 EnvironmentSpec v1
→ PR #29 EnvironmentFingerprint + compatibility v1
```

### PR #28 — EnvironmentSpec v1

Implementation commit:

`21622438602bc22a70c3dc735c1d918a45463171`

Full Runtime stack CI:

`31897492718` — success

Validation/task-record head:

`6128ef94334b1868677430d65724628d19bb8b70`

Task:

`work/tasks/environment-spec-wave2.md` → `READY_FOR_REVIEW`

Implemented:

- strict JSON EnvironmentSpec v1;
- normalized semantic SHA-256;
- repository assumptions;
- runtime/tool requirements;
- setup/maintenance commands as data only;
- quick/normal/full validation tiers;
- explicit network modes;
- service names;
- secret capability names only;
- dependency input paths;
- pilot `maps-runtime-ci` spec describing the existing Runtime stack workflow.

Critical boundaries:

- unknown spec fields fail closed;
- no setup/validation command execution;
- no secret values;
- EnvironmentSpec does not grant task authority.

### PR #29 — local EnvironmentFingerprint + compatibility

Implementation commit:

`6d639380fe3683745611dc0092edb0ec9b30414a`

Full Runtime stack CI:

`31897745175` — success

Validation/task-record head:

`620834a0db9cce7e2de3d4750c98f1c49687ccdd`

Task:

`work/tasks/environment-fingerprint-wave2.md` → `READY_FOR_REVIEW`

Implemented:

- bounded read-only local version/Git/dependency observation;
- runtime/tool states: `OBSERVED`, `MISSING`, `UNKNOWN`;
- stable fingerprint hash excluding observation timestamp;
- no absolute repo path/environment dump/provider transcript in fingerprint;
- credential requirements represented only as caller-supplied boolean/unknown capability availability;
- narrow numeric runtime constraint checking;
- compatibility states:
  - `COMPATIBLE`
  - `COMPATIBLE_WITH_WARNINGS`
  - `DRIFTED`
  - `INCOMPATIBLE`
  - `UNKNOWN`
- optional reference fingerprint comparison for replacement/recovery evidence.

Critical decisions:

- unknown material evidence never becomes compatible;
- missing hard requirements are incompatible;
- spec/repo/dependency/required-clean-worktree change is drift;
- compatible version changes may be warning-only when the declared requirement still holds;
- fingerprint/compatibility is evidence, not authorization to execute or resume.

---

# Next environment step: E3 run evidence binding

The next safe environment task is E3 from the Environment/Reproducibility roadmap.

Goal:

Bind exact EnvironmentSpec/fingerprint evidence to an existing immutable run without making environment compatibility a task authority.

Preferred design direction to inspect/validate before coding:

- preserve existing immutable `run_manifests`;
- do not mutate `run_manifests.session_id` or overload that table;
- likely add narrow append-only run-environment evidence owned by the canonical task store;
- record exact spec hash, fingerprint hash/body or independently retrievable evidence, compatibility state, actor/time, and optional reference fingerprint;
- trace should eventually be able to show environment evidence;
- environment evidence may prove/deny compatibility but may not claim/renew task ownership or grant operator approval.

Stop if E3 starts becoming:

- a second task/run authority store;
- an automatic recovery/resume controller;
- a container/sandbox manager;
- a secret store.

---

# Broad status

Verified implementation tranches now exist for:

1. typed provider-neutral harness contract;
2. hcom normalization;
3. deterministic Hooks;
4. HarnessService;
5. canonical continuation guard;
6. initial agentic adversarial regressions;
7. Agent Skills format/progressive loading foundation;
8. Skills catalog/provenance read model;
9. frozen Skill-selection benchmark;
10. EnvironmentSpec v1;
11. EnvironmentFingerprint/compatibility v1.

All remain subject to their stated independent review gates. CI success is evidence, not approval.
