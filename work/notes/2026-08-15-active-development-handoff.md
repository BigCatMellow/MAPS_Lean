# Active development handoff — 2026-08-15

Status: `WORKING NOTES — NOT ACTIVE AUTHORITY`

Purpose: preserve enough exact implementation state that work can resume after a context reset without rediscovering the design or accidentally changing boundaries.

Canonical task/policy state, repository instructions, code, and reviewed/merged decisions remain authoritative. These are coordination notes only.

---

## Operator direction

- Continue implementation even while upstream draft PRs await independent review **unless the next step truly requires the review result**.
- Use stacked PRs when code depends on an unmerged upstream tranche; keep the dependency explicit.
- Do not merge, mark ready, self-approve, or bypass independent review.
- Preserve useful mechanisms without rebuilding Prime/MAPS legacy complexity.
- Ordinary work should stay concise/simple; roadmaps are intentionally comprehensive.
- Keep durable notes during long work so context loss does not destroy implementation reasoning.

---

# Current development topology

## Stacked Harness / Security chain

```text
main
  ↓
PR #20  agent/harness-foundation-wave1
  ↓
PR #21  agent/hcom-hooks-wave1
  ↓
PR #22  agent/harness-service-wave1
  ↓
PR #23  agent/harness-canonical-guard-wave1
  ↓
PR #24  agent/agentic-security-baseline-wave1
```

All are draft PRs and remain independently reviewable.

## Parallel Skills track

Branch created independently from `main`:

`agent/skills-format-wave2`

This track deliberately does **not** depend on the Harness stack for its first format/parser tranche.

At the moment this note was written:

- the branch exists;
- no Skills commit has been published yet;
- a blob for the intended `runtime/skills/__init__.py` was prepared during tool work, but because no tree/commit/ref update occurred it is **not part of branch state**;
- next work is to implement `runtime/skills/format.py`, tests, and a task record, then commit/open a draft PR against `main`.

---

# PR #20 — typed Harness foundation

PR: `#20 Add Wave 1 harness contract foundation`

Branch: `agent/harness-foundation-wave1`

Current branch/head recorded earlier:

`ecfc27269e096db5d83bfa376878c33089a4e106`

Code implementation commit:

`5d408fc4c9fef165da3478e86bab3bd964470429`

Validation-record commit:

`ecfc27269e096db5d83bfa376878c33089a4e106`

CI:

- Runtime stack run `31893719145`
- passed on code commit `5d408fc4...`

Implemented:

- `runtime/harness/`
- provider-neutral `OperationResult`
- `ExecutionBinding`
- `SessionRef`
- normalized session states / `SessionStatus`
- retry-safety semantics
- `HarnessAdapter` protocol
- explicit `UNKNOWN` rather than guessed provider state

Authority rule:

> Harness contract describes execution operations. It does not own task authority, scope, policy, approval, review, or completion.

Task file:

`work/tasks/harness-foundation-wave1.md`

State: `READY_FOR_REVIEW`

---

# PR #21 — hcom normalization + initial Hook registry

PR: `#21 Add hcom normalization and deterministic Hook registry`

Branch: `agent/hcom-hooks-wave1`

Implementation commit:

`cca097e69401bf7d79f753970c249c0ed86da3ec`

Validation-record commit / current recorded branch head:

`7a57cb3e59b5775492d5441245e3279b58f47580`

CI:

- Runtime stack run `31894920245`
- passed on implementation commit `cca097e...`

Implemented hcom normalization:

- `inspect`
- `send`
- `stop`

Important semantics:

- exact project/session checks;
- provider state that cannot be mapped remains `UNKNOWN`;
- successful inspection with no matching session is `SESSION_NOT_FOUND`, distinct from transport failure;
- provider errors are normalized without dumping raw exception text into agent-facing summaries;
- `send` and `stop` require explicit session identity through the binding;
- mutating result retry disposition remains conservative when remote acknowledgement cannot prove replay safety.

Explicitly `UNSUPPORTED` for now:

- hcom `start`
- `attach`
- `heartbeat`
- `resume`
- `collect`

Reason: existing hcom behavior does not yet provide enough structured identity/lineage/runtime-mode evidence to normalize those honestly.

Hook registry implemented:

- deterministic priority then registration ordering;
- directives: `ALLOW`, `DENY`, `REQUIRE_APPROVAL`, `ANNOTATE`;
- side-effect classification;
- explicit failure policies;
- fail-closed by default;
- raw Hook exception messages are not propagated by default.

Important helper decision:

> Current helper subsystem is run-to-completion evidence, not a live session API. Do not force helpers into `SessionRef` semantics. Helper lineage should be added through actual helper evidence when the lineage design exists.

Task file:

`work/tasks/hcom-hooks-wave1.md`

State: `READY_FOR_REVIEW`

---

# PR #22 — provider-neutral HarnessService

PR: `#22 Add provider-neutral HarnessService`

Branch: `agent/harness-service-wave1`

Implementation commit:

`96c614846314ea604be95df9feed5c7e3b477b62`

Validation-record commit / current recorded branch head:

`4d4eeb1bd42ada3582aec1efcceeb5e63fb6af0a`

CI:

- Runtime stack run `31895128908`
- passed on implementation commit `96c614...`

Implemented:

- explicit adapter registry;
- one provider-neutral service over adapters + Hooks;
- exact call-time correlation between `ExecutionBinding` and `SessionRef`;
- mutating session-bound calls reject project/worker/session mismatch rather than choosing a likely session;
- explicit `attach` may accept an unbound binding, but it still checks worker/project and does not infer identity;
- Hooks integrated at `RUN_STARTING`, `RUN_STARTED`, `BEFORE_SEND`, `SESSION_STOPPING`;
- pre-operation `DENY` / `REQUIRE_APPROVAL` prevents adapter mutation;
- if a post-start Hook fails after provider mutation, returned result preserves `mutated=true` plus the adapter result rather than pretending nothing happened.

Critical rule:

> HarnessService is a correlation/execution surface, not a source of task authority.

No `TaskStore` dependency was added to the Harness service itself.

Task file:

`work/tasks/harness-service-wave1.md`

State: `READY_FOR_REVIEW`

---

# PR #23 — canonical run/lease/session guard

PR: `#23 Add canonical run guard for harness operations`

Branch: `agent/harness-canonical-guard-wave1`

Implementation commit:

`6c6eeeb050a3bc102250bafba9a849bab1e82b04`

Validation-record commit / current recorded branch head:

`61442600c49798245b80dd9a6602ac82954e27d5`

CI:

- Runtime stack run `31895412303`
- passed on implementation commit `6c6eee...`

Implemented `runtime/policy/harness_guard.py`:

- read-only `CanonicalRunGuard` over canonical task/run evidence;
- verifies task, project, run, worker, immutable run revision;
- continuation operations require canonical task/run evidence rather than provider liveness;
- registered only at pre-mutation Hook points.

Continuation semantics at PR #23 implementation point:

- `start` / `send` require:
  - current task revision;
  - task `ACTIVE`;
  - current claimant matches worker;
  - live lease;
  - non-stale run/context;
- `send` also requires exact durable `run_manifest.session_id` match.

Stop semantics intentionally differ:

- `stop` verifies exact historical task/run/session identity;
- `stop` does **not** require current task revision/live lease/ACTIVE continuation authority;
- rationale: a stale or expired session may still need to be stopped safely by an otherwise authorized recovery/operator path;
- the guard verifies targeting; it does not itself grant stop permission.

Important unresolved design boundary:

> Late session attachment is not solved. `run_manifests.session_id` is immutable. Do not create a hidden mutable duplicate binding merely to make attach convenient. Durable lineage/attachment needs an explicit one-authority design.

Task file:

`work/tasks/harness-canonical-guard-wave1.md`

State: `READY_FOR_REVIEW`

---

# PR #24 — initial agentic security adversarial baseline

PR: `#24 Add initial agentic security adversarial baseline`

Branch: `agent/agentic-security-baseline-wave1`

Implementation commit / current head at note time:

`e25baaa044a2f5bc9b969e59aeffb0036d9a5f05`

CI at note time:

- Runtime stack run `31895641637`
- status when last checked: `in_progress`
- do not record as passed until GitHub confirms success.

This tranche found and fixes a concrete gap:

- `resume` previously had no deterministic pre-resume Hook;
- new `BEFORE_RESUME` Hook event is added;
- `HarnessService.resume()` invokes it before adapter resume;
- `CanonicalRunGuard` treats `resume` as continuation.

After this change, `resume` requires:

- current task revision;
- `ACTIVE` task;
- current claimant;
- live lease;
- non-stale run/context;
- exact durable session binding.

Initial executable adversarial baseline includes:

- **SEC-ADV-005:** payload/tool text claiming “operator approval granted” cannot satisfy a `REQUIRE_APPROVAL` Hook;
- **SEC-ADV-006:** a continuity-linked helper/replacement identity cannot claim independent review;
- **SEC-ADV-007A:** stale session cannot resume after task reshape/revision change;
- **SEC-ADV-007B:** live provider session cannot override expired task lease;
- **SEC-ADV-008:** peer/message text claiming ownership transfer does not mutate canonical task ownership;
- **SEC-ADV-LIVENESS:** inspecting a RUNNING provider session does not renew canonical task heartbeat/lease.

New descriptive security note:

`work/security/AGENTIC_THREAT_MODEL.md`

It is explicitly **not policy authority**. It maps the Agentic Security roadmap's initial 20 attacks into executable/existing/planned coverage without claiming protections that do not exist.

Task file:

`work/tasks/agentic-security-baseline-wave1.md`

Current task status in branch: `ACTIVE` until CI result is confirmed and the validation record is updated.

---

# Parallel Wave 2 Skills work — next active implementation

Branch:

`agent/skills-format-wave2`

Base:

`main`

Roadmap:

`work/roadmaps/agent-harness-capabilities/02-procedural-knowledge-and-skills.md`

Current intended first tranche:

1. support standard-style Skill directory discovery:

```text
skills/<skill-name>/
  SKILL.md
  scripts/        optional
  references/     optional
  assets/         optional
  examples/       optional MAPS convention
```

2. parse minimum frontmatter needed for discovery:
   - `name`
   - `description`

3. do **not** add a YAML package yet solely for this tranche;
4. tolerate unrelated/custom metadata as metadata, never authority;
5. compute stable whole-Skill-directory content hash/version identity;
6. discovery should load compact metadata only;
7. a separate activation/load step should read the `SKILL.md` body;
8. preserve optional resource inventory without executing anything;
9. no Skill may override canonical policy or task authority;
10. no routing/autonomous activation yet;
11. no third-party approval/quarantine database yet;
12. tests should cover valid/invalid frontmatter, duplicate names/IDs, deterministic hash, change detection, resource discovery, and progressive disclosure.

Likely files:

```text
runtime/skills/__init__.py
runtime/skills/format.py
tests/test_skills_format.py
work/tasks/skills-format-wave2.md
```

Then open a **draft PR against `main`**, because this first parser/catalog foundation is deliberately independent of PRs #20–#24.

---

# Major design decisions that must survive context loss

## 1. Stacked PRs are allowed before review

Independent review is a merge/completion gate, not automatically an implementation-start gate. Continue on a stacked branch when the dependency is explicit and upstream code has sufficient verification. If review changes the upstream contract materially, rebase/reshape downstream PRs before merge.

## 2. Session liveness is never task authority

```text
live provider session
≠ task owner
≠ live task lease
≠ current task revision
≠ permission to resume
≠ review authority
```

## 3. Capability is not authority

```text
capability
≠ assignment
≠ ownership
≠ task scope
≠ policy authority
≠ operator approval
```

## 4. Hooks can narrow/block, not grant missing authority

`ALLOW` means the Hook itself does not object. It is not equivalent to task authorization.

`REQUIRE_APPROVAL` is a request/block condition. The Hook cannot manufacture operator approval.

## 5. Stop and continuation have different freshness needs

Continuation (`start/send/resume`) requires current task/run/lease/context evidence.

Stopping an explicitly known stale session may remain necessary for cleanup/recovery. Verify exact historical identity, but do not pretend the old session regained authority.

## 6. Helpers are not sessions just because both execute work

Current helper subsystem returns bounded run results/evidence. Do not invent persistent helper-session semantics until a real continuity design exists.

## 7. Do not create a second task/session truth store

Read/join/normalize existing authorities. Any durable run/session/helper linkage added later must be append-only evidence with explicit reconciliation rules and must not compete with canonical task state or immutable run manifests.

## 8. Durable late session attachment remains unresolved intentionally

Existing `run_manifests.session_id` is optional and immutable. A new binding table may be appropriate, but only after defining:

- whether the manifest session is initial-session identity or authoritative current session;
- how late attachment relates to it;
- how replacement sessions are represented;
- how uniqueness/conflicts are handled;
- which record wins if both exist;
- how trace/recovery/review independence consume the lineage.

Do not patch around this with mutable convenience state.

## 9. Security tests should prove behavior

Prefer public/guarded behavioral properties over checking source text for words like “approval” or “deny.”

## 10. Agent Skills are procedures, not authority/personas

Skill text is reusable procedural knowledge. It must not become another form of permanent expert agent, policy, or automatic privilege bundle.

---

# Immediate continuation checklist

1. Check CI run `31895641637` for PR #24.
2. If green:
   - update `work/tasks/agentic-security-baseline-wave1.md` to `READY_FOR_REVIEW`;
   - record the exact CI run/implementation commit;
   - downstream work may continue without waiting for review.
3. Continue `agent/skills-format-wave2` from `main`:
   - implement `runtime/skills/format.py`;
   - add format/discovery/progressive-loading tests;
   - add task record;
   - commit;
   - open draft PR against `main`;
   - run full Runtime stack CI.
4. Do **not** start durable late-session lineage/schema work until its one-authority/reconciliation semantics are explicitly designed.
5. Keep adding/updating durable task/handoff notes after each substantial tranche or design decision.

---

# Existing roadmap / evidence files worth consulting after reset

- `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md`
- `work/roadmaps/prime-agent-capability-roadmap.md`
- `work/roadmaps/agent-harness-capabilities/01-harness-mechanics.md`
- `work/roadmaps/agent-harness-capabilities/02-procedural-knowledge-and-skills.md`
- `work/roadmaps/agent-harness-capabilities/04-agentic-security.md`
- `migration/FUTURE_IDEAS_BACKLOG.md`
- `migration/LEGACY_IDEA_RECOVERY_AUDIT.md`
- `work/security/AGENTIC_THREAT_MODEL.md` on PR #24 branch
- the task files named above for exact tranche boundaries and acceptance criteria

---

# Review / merge reminder

All implementation PRs remain drafts. Successful CI is evidence, not independent approval. Do not self-approve or merge them merely because downstream implementation has continued.
