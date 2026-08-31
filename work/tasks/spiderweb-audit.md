# Task: Spiderweb audit

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: implementation agent
- Risk: `MEDIUM`
- Goal: add a bounded advisory audit that helps fresh agents find disconnected, stale, or weakly connected durable project information without creating new authority or automatically inventing relationships.

## Connections

- Parent / supports: [Information Lifecycle](../../playbook/INFORMATION_LIFECYCLE.md)
- Derived from: durable-information reconciliation need described in [Information Lifecycle](../../playbook/INFORMATION_LIFECYCLE.md)
- Related: [E/I](../../playbook/EMERGENCE.md), [Roadmap Trajectory Check](../../playbook/ROADMAP_TRAJECTORY_CHECK.md), [Tenth-Seat Review](../../playbook/TENTH_SEAT_REVIEW.md)
- Method: [Spiderweb Audit](../../playbook/SPIDERWEB_AUDIT.md)
- Evidence / review: this task's stacked PR and `tests/test_spiderweb_audit.py`

## Inputs and source of truth

- Inputs: active Markdown records and the repository's existing standard relative Markdown links.
- Authoritative sources: `AGENTS.md`, current playbooks, current code, task truth, and approved decisions remain authoritative; Spiderweb output is advisory evidence only.
- Evidence labels: scanner findings are `OBSERVED STRUCTURE`, not semantic truth.
- Dependencies / preconditions: reconciliation/no-island rules from PR #173's branch.

## Change boundary

- MAY CHANGE: `scripts/check_spiderweb.py`, `tests/test_spiderweb_audit.py`, `playbook/SPIDERWEB_AUDIT.md`, `playbook/INDEX.md`, `playbook/ROADMAP_TRAJECTORY_CHECK.md`, `playbook/INFORMATION_LIFECYCLE.md`, this task record.
- MUST NOT CHANGE: runtime authority, SQLite schema, task lifecycle, review authority, Skill lifecycle, external/destructive-action policy, legacy contents.
- MAY CHANGE IF NECESSARY: small documentation references needed to make the method discoverable.
- OPERATOR APPROVAL REQUIRED: any automatic link creation, task creation, idea promotion, decision reopening, or blocking CI policy beyond an explicit broken-link option.

## Decision authority

- Owner may decide: deterministic parsing/reporting details that remain advisory and provider-neutral.
- Owner must escalate: any semantic auto-linking, new source of truth, graph database, daemon/watcher, automatic authority/status mutation, or broad historical rewrite.

## Acceptance criteria

- [x] A deterministic script scans active Markdown and reports broken links, duplicate declared stable IDs, orphan/thin connection candidates, historical-only connection candidates, unresolved `Not promoted` records, and overdue pending experiments where enough structured date evidence exists.
- [x] Raw historical preservation surfaces are opt-in rather than default scan noise; curated migration ledgers/backlogs remain in the normal scan.
- [x] The script can emit human-readable and JSON results.
- [x] Findings are advisory by default; an optional flag may fail only on objectively broken local links or duplicate declared IDs.
- [x] A Spiderweb AGI tells a fresh agent how to semantically reconcile findings without inventing links or authority.
- [x] The method is connected to the information lifecycle, playbook index, and trajectory-check process.
- [x] Tests cover graph/link resolution, orphans/thin links, duplicate IDs, historical-only links, pending experiments, JSON output, advisory exit behavior, and heading-reference false positives.

## Verification and evidence

- Verification: local isolated run of `tests/test_spiderweb_audit.py` — 12 tests passed; full repository CI remains required on the PR.
- Evidence to preserve: test output, PR review, and later representative repository Spiderweb reports at trajectory boundaries.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: Python 3.12+, standard library only.
- Ordered procedure: deterministic scanner → tests → playbook/AGI → steering/index links → review → first real trajectory-boundary scan.
- Failure branches: if a relationship cannot be established mechanically, report a candidate and defer semantic judgment to the AGI.
- Rollback / recovery: revert the stacked PR; no persistent state is created by the scanner.
- Security / privacy controls: scanner reads repository Markdown only and does not transmit contents.
- External side effects: GitHub branch/PR only.
- Effort limit: do not expand into a graph database, semantic retriever, or background service.
- Approved reference: [Information Lifecycle](../../playbook/INFORMATION_LIFECYCLE.md).

## Stop / escalate

Stop rather than guess if:

- a proposed rule would automatically decide that two artifacts are semantically related;
- a finding would mutate task/decision/idea authority;
- implementing a useful check requires a second mutable truth store.

Escalate to: operator.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Completion / handoff

- Completed: deterministic scanner, JSON/text output, advisory/broken-link modes, 12 focused tests, Spiderweb Reconciliation AGI, steering/information-lifecycle integration, and stacked PR #174.
- Not completed: independent review, full CI, and the first real trajectory-boundary repository scan.
- Current blocker: none; review/CI pending.
- Next action if not DONE: obtain independent review and required checks on PR #174.
