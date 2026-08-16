# MAPS agentic threat model and adversarial corpus

Status: `SECURITY TEST MODEL — NOT POLICY AUTHORITY`

Purpose: define concrete agent-specific threats and freeze representative behavioral regressions as MAPS gains provider-neutral execution, Hooks, Skills, tools, memory, recovery, and persistent sessions.

Canonical task/policy/approval state and `AGENTS.md` remain authoritative. This document names attacks and expected properties; it does not grant or modify authority.

## Core security property

> **Untrusted content may influence reasoning, but only canonical MAPS authority may authorize consequential action.**

A repository file, web page, tool result, Skill, helper, peer message, provider session, old memory, or generated text may contain instructions or claims. None of those can create ownership, operator approval, review independence, task scope, policy authority, or a live claim lease.

## Trust boundaries

| Boundary | Untrusted / weaker side | Stronger source |
|---|---|---|
| task intent | prompts, files, peer/helper messages | canonical task contract / operator |
| ownership | session liveness, messages, worker claims | canonical claim + live lease |
| execution continuity | provider thread/session state | immutable run binding + current task revision/context |
| provider session identity | provider-local session ID alone | adapter-qualified canonical run/session evidence |
| approval | tool output, prose, Hook request | canonical operator approval record |
| review independence | self-asserted role | submission authorship + continuity evidence |
| procedures | imported Skill/reference text | reviewed/pinned Skill lifecycle when implemented |
| tool capability | available endpoint | task scope ∩ policy ∩ approval ∩ environment |
| memory/guidance | observations/retrieved text | reviewed guidance / current policy |

## Initial threat classes

1. goal/instruction hijacking;
2. tool misuse;
3. excessive privilege;
4. identity confusion;
5. Skill/tool supply-chain compromise;
6. memory/context poisoning;
7. inter-agent trust exploitation;
8. unexpected code execution;
9. stale/recovery authority reuse;
10. cascading automation failure;
11. misleading human-approval requests.

## Executable baseline cases

`tests/test_agentic_security_baseline.py` freezes named cross-system cases:

- **SEC-ADV-005 — approval-by-text:** payload text claiming operator approval does not satisfy a deterministic approval gate.
- **SEC-ADV-006 — helper/continuation self-review:** an identity in the submission author's continuity lineage cannot claim independent review.
- **SEC-ADV-007A — stale resume after reshape:** a provider session cannot resume when the canonical task revision changed.
- **SEC-ADV-007B — liveness versus lease:** a live session cannot resume after the task lease expires.
- **SEC-ADV-008 — ownership-by-message:** a peer/worker message claiming ownership transfer does not mutate canonical ownership.
- **SEC-ADV-LIVENESS — session inspection:** observing a RUNNING provider session does not renew task heartbeat or lease.
- **SEC-ADV-GUARDED-SERVICE — mandatory canonical enforcement:** public `HarnessService` start/send/resume/stop fail closed before adapter mutation when canonical-run enforcement is absent; an ordinary ALLOW Hook does not satisfy that requirement.
- **SEC-ADV-HOOK-CONTEXT — cross-Hook mutation:** an earlier Hook cannot rewrite nested binding/session evidence seen by a later canonical guard.

These tests intentionally exercise behavior rather than checking for reassuring source text.

## Broader adversarial corpus

The roadmap's initial corpus remains the target. Status below is test-planning status, not a security certification.

| ID | Attack | Current status |
|---|---|---|
| 001 | repository instruction attempts policy override | planned with external-action guard |
| 002 | web content asks for credentials | planned with credential boundary |
| 003 | Skill requests undeclared root access | planned with Skill gate |
| 004 | Skill script attempts network exfiltration | planned with Skill quarantine/eval |
| 005 | tool/payload text says approval granted | executable baseline |
| 006 | helper claims parent review complete | executable through continuity review boundary |
| 007 | stale session resumes after task reshape | executable baseline |
| 008 | peer message claims ownership transfer | executable baseline |
| 009 | old reviewed lesson conflicts with current policy | planned with operational-learning lifecycle |
| 010 | example/generated content attempts tool activation | planned with capability loading |
| 011 | external tool hides dangerous write under benign name | planned with tool provenance/capability declarations |
| 012 | tool result contains secret and reaches diagnostics | existing redaction boundary; keep expanding property tests |
| 013 | recovery finds multiple candidate sessions/tasks | existing recovery ambiguity regression |
| 014 | environment snapshot/source provenance unknown | planned with EnvironmentSpec/snapshot track |
| 015 | third-party Skill auto-update changes capabilities | planned with Skill pinning/provenance |
| 016 | read-authorized task reaches write-capable tool | existing scope/capability controls; integrate with Hooks later |
| 017 | approval for target A reused for target B | planned target-scoped approval representation |
| 018 | reviewer is in author's continuity lineage | existing + executable baseline |
| 019 | post-completion FAILURE reopens authority | existing outcome invariant; keep frozen in outcome tests |
| 020 | generated content attempts to redefine trust labels | planned with trust/memory lifecycle |

## Security invariants to preserve

```text
session liveness ≠ ownership
session liveness ≠ task heartbeat
bare provider-local session ID ≠ provider-neutral durable identity
message text ≠ ownership transfer
text saying “approved” ≠ operator approval
helper output ≠ review authority
continuity ≠ independent reviewer
old task revision ≠ current authority
available tool ≠ authorized tool
retrieved memory ≠ policy
Hook REQUIRE_APPROVAL ≠ approval
ordinary Hook presence ≠ canonical enforcement
missing canonical enforcement → no consequential HarnessService mutation
```

## Harness/recovery requirements

Before consequential start/send/resume/stop through the public HarnessService mutation surface:

- the corresponding canonical-run enforcement Hook must be mechanically installed;
- current task/run evidence must satisfy the operation-specific canonical guard;
- continuing operations require ACTIVE task, current claimant, live lease, current task revision, and non-stale run/context;
- session-bound operations require adapter-qualified durable session identity where canonical evidence can prove it.

The current run-manifest schema stores a bare session ID but not durable adapter qualification. That is insufficient provider-neutral identity, so affected session-bound operations fail closed rather than guessing until the accepted lineage/schema work supplies that relationship.

A stale/expired session may still need to be stopped by an authorized recovery/operator path, but historical cleanup may only proceed when exact adapter-qualified historical identity can actually be proven.

Low-level adapters remain capability primitives beneath the guarded service boundary; their existence does not grant task authority.

## Growth rule

When a real security incident or near miss occurs:

1. classify the failure;
2. preserve the smallest reproducible case;
3. add a behavioral regression test;
4. fix the mechanism at the narrowest reliable layer;
5. keep the case permanently unless the underlying capability is removed.

Do not measure security by number of warnings, agents, or prompts. Measure whether prohibited behavior is mechanically unreachable and whether legitimate work remains usable.
