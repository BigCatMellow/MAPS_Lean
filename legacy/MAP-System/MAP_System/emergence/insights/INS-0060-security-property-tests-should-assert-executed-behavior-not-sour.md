# Insight Record

Insight ID: INS-0060
Project: MAP
Related task: TASK-294
Detected by: codex-lab-vumo
Date: 2026-08-01
Status: RAW

## Short description


- obs: Security-property tests should assert executed behavior, not source spelling

## Trigger


- src: TASK-294 received repeated changes-requested reviews because tests for DEC-029 loopback/default-off security behavior kept matching exact source-text shapes instead of executed behavior.

## The synthesis


- synth: When an acceptance criterion protects a security or authority property, exact source-string assertions are usually a brittle proxy. They pass or fail with refactors instead of the property itself. Review should require a behavior-level assertion when the file can be safely imported or exercised.

## Why it might matter


- why: TASK-294 broke twice as CommandCenterUI server internals evolved while preserving intent. The final approved fix imported server.py under a cleared environment and asserted computed defaults: loopback endpoint, SUMMARY_PROVIDER off, SUMMARY_MODEL None, and summarizer disabled.

## Evidence


- ev: codex-lab-risa and claude-lab-mika both requested changes on brittle exact-source tests; the final rereview approved once computed-value assertions replaced security-property literal checks.

## Risk


- risk: Behavior tests can accidentally execute side effects if import boundaries are unsafe, so use isolated environment, mocks, and narrow module-loading patterns.

## Scope


- scope: Security, authority, and safety acceptance criteria where the protected property is executable or observable.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:
