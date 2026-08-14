# Insight Record

Insight ID: INS-0024
Project: ClearFront
Related task: TASK-207
Detected by: claude-lab-gome
Date: 2026-07-16
Status: RAW

## Short description


- obs: Byte-identical headless screenshots plus a dependency-free CDP interaction script form a cheap, binary parity gate for HTML refactors; harness checked in and already reused across two tasks.

## Trigger


- src: Needed to prove an extracted/refactored HTML game was behaviorally identical to a generated bundle, where a static screenshot alone could miss order-dependent script breakage (RISK-CF-0001).

## The synthesis


- synth: A two-layer parity gate is cheap and strong for single-page HTML app refactors: (1) byte-identical headless-Chromium screenshots (same flags/virtual-time budget) at a deterministic initial screen, (2) a CDP script driving real Input.dispatchMouseEvent interaction while capturing every Runtime.consoleAPICalled and Runtime.exceptionThrown. Byte-identity makes the visual check binary (no perceptual-diff judgment), and the interaction pass catches wiring/state bugs that static rendering hides. The harness is dependency-free (Node >=21 built-in WebSocket) and was reused as-is by the next task (TASK-208) via Projects/ClearFront/artifacts/tests/task208-cdp-smoke.mjs.

## Why it might matter


- why: Every planned ClearFront decomposition task (engine/render/input splits, TASK-209+) needs exactly this regression gate, and any future MAP task refactoring a browser artifact can reuse the pattern and harness directly.

## Evidence


- ev: TASK-207: original vs extracted baseline screenshots md5-identical; CDP run reached turn-1 combat with zero console errors. TASK-208: same method reused by a Fable helper unmodified; caught nothing because the refactor was clean, but provided the binary evidence both reviews relied on.

## Risk


- risk: Acting without promotion could bypass HPOM governance.

## Scope


- scope: Only the files and artifacts named in this record.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:
