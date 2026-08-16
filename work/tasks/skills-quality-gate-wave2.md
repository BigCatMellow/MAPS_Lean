# Task: static Skill quality and security gate

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: add a bounded static quality/security assessment for discovered Skills so risky imported procedures/resources are surfaced before activation, without creating approval authority, persistent trust state, autonomous routing, or script execution.

## Inputs and source of truth

- Inputs: `AGENTS.md`, PRs #25–#27, `runtime/skills/format.py`, Procedural Knowledge & Skills roadmap S5, Agentic Security roadmap Skill/tool supply-chain requirements.
- Authoritative sources: active repository instructions and exact Skill content hash win; gate output is advisory evidence only and cannot override task/policy/operator authority.
- Dependencies / preconditions: verified Skills format/catalog/evaluation stack through head `f6d6685b4396829cc71e67144a3ca0951f1d8b52`.

## Change boundary

- MAY CHANGE: new `runtime/skills/gate.py`, `runtime/skills/__init__.py` exports, focused adversarial gate tests, this task file.
- MUST NOT CHANGE: Skill parser/catalog/evaluator semantics unless a demonstrated defect requires re-shaping, task/policy/review state, Skill routing, Context Builder, script/tool execution, durable approval/trust registry, external systems.
- MAY CHANGE IF NECESSARY: bounded static finding/disposition representation within this S5 tranche.
- OPERATOR APPROVAL REQUIRED: executing Skill resources, marking a Skill approved/trusted, persistent quarantine/approval state, external provider/tool calls, or material scope expansion.

## Decision authority

- Owner may decide: static finding classes, bounded scan limits, severity/disposition mapping, obvious high-risk pattern checks, and adversarial fixtures consistent with the roadmaps.
- Owner must escalate: any design that makes static scanning proof of safety, creates a durable trust authority, executes resources, or silently auto-activates a Skill after a clear scan.

## Acceptance criteria

- [x] gate verifies the Skill has not drifted since discovery before scanning.
- [x] gate reads Skill body/resources statically and never executes scripts/resources.
- [x] report is bound to the exact Skill content SHA-256.
- [x] dispositions are only `CLEAR`, `REVIEW_REQUIRED`, and `QUARANTINE`; none means `APPROVED` or grants runtime capability.
- [x] executable resources trigger review even when no suspicious text is found.
- [x] binary/non-UTF8/oversized resources trigger review rather than being silently skipped.
- [x] vague routing descriptions and persona/roleplay-heavy instructions trigger review.
- [x] privilege, destructive, broad environment/credential access, and script network access trigger review.
- [x] likely secret literals, sensitive credential/key resource names, authority-override/approval claims, and remote-pipe-to-shell patterns trigger quarantine.
- [x] findings contain bounded code/path/summary metadata and do not echo detected secret values/source contents.
- [x] safe procedural Skill can be `CLEAR`, while tests assert that `CLEAR` output contains no approval/trust semantics.
- [x] malicious/adversarial fixture Skills are caught by behavior tests.
- [x] focused tests and full Runtime stack CI pass.
- [ ] independent review remains required before completion.

## Verification and evidence

- Verification: PR-triggered full Runtime stack CI run `31898263690` passed on implementation commit `d3d186dbd0903eacd4dbe715335bf2560b1c74d3`.
- Evidence to preserve: adversarial test cases, GitHub Actions run `31898263690`, PR #31 diff, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: discovered local Skill directories only; static read-only scan.
- Ordered procedure: define bounded gate report → scan metadata/body/resources → adversarial tests → stacked draft PR → full CI → independent review.
- Failure branches: IF a resource cannot be safely decoded/scanned THEN require review instead of claiming clear; IF behavior safety needs execution THEN defer to a later sandboxed behavioral-eval task.
- Rollback / recovery: revert isolated stacked commit/PR; no schema/data migration.
- Security / privacy controls: no script execution, no network calls, bounded scan size, secret findings do not echo matching content.
- External side effects: Git branch/PR publication only.
- Effort limit: static S5 gate foundation only; no durable quarantine workflow or behavioral sandbox.
- Approved reference: Skills roadmap S5 + Agentic Security Skill supply-chain controls.

## Stop / escalate

Stop rather than guess if:

- static inspection would need to execute a script/tool;
- a `CLEAR` result would be used as automatic approval;
- persistent quarantine/trust authority becomes necessary;
- pattern matching begins masquerading as a complete security proof.

Escalate to: operator / roadmap re-shaping as appropriate.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This task stacks on PR #27 but does not make the selection evaluator or any selector part of the security gate.
- Static checks are an early filter, not a proof of safety. `CLEAR` means only that this bounded scan found no configured concerns.
- Script presence alone requires review. Script contents receive additional checks but are never executed.
- High-confidence authority/secret/remote-pipe patterns quarantine; contextual privilege/network/destructive patterns require review rather than blanket rejection.
- Findings intentionally omit matched source snippets so secret detection cannot become a secret-exfiltration surface.
- Existing MAPS diagnostic secret detection is reused rather than creating a separate definition of recognized secret patterns.

## Completion / handoff

- Completed: static Skill quality/security gate, adversarial tests, draft PR #31, and full Runtime stack CI.
- Not completed: independent review / merge.
- Current blocker: independent review required for completion; unrelated roadmap work may continue.
- Next action if not DONE: independent review of PR #31; persistent Skill trust/approval state remains deliberately deferred until its authority lifecycle is explicitly reviewed.
