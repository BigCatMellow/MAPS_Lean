# Insight Record

Insight ID: INS-0026
Project: ClearFront
Related task: NONE
Detected by: claude-lab-gome
Date: 2026-07-17
Status: RAW

## Short description


- obs: The ctx-accessor/installer decomposition made ClearFront's rules engine headless-testable for free -- a ~50-line Node stub loads the real unmodified engine and asserts real rule semantics below the DOM (11/11 probe), answering the audit's P0 without the refactor it assumed necessary.

## Trigger


- src: The independent audit's P0 finding: rule-engine regression evidence is browser-smoke-only; it recommended extracting a deterministic engine test seam before any balance/mechanic work.

## The synthesis


- synth: The seam already exists as an unplanned consequence of the ctx/installer decomposition (DEC-CF-004..006): data.js + state.js + combat.js load UNMODIFIED in Node via node:vm with a ~50-line stub (window.CF namespace, __resources proxy, setTimeout captured to a manual-drain queue, matchMedia {matches:false}, a fake-element factory behind a refs Proxy, and a 3-function render stub where playClashSequence(report, onDone) calls onDone() synchronously). Because installers take ctx accessors over host-owned bindings, a test harness IS a host: it owns state/undoRecord/uidCounter/deck choices directly, so tests set up any board position as plain objects and call real engine functions (dealDamage, damageHero, isCardPlayable, drawCard...) with no DOM, no browser, no RNG, no timing.

## Why it might matter


- why: Directly answers the audit's P0 with far less work than assumed: no refactor needed, only a harness + table-driven cases (TASK-220). Also validates the accessor/installer pattern itself: host-owned mutable bindings behind ctx make 'the host' swappable, and a test runner is just another host. Reusable lesson for any future MAP project decomposing a browser app.

## Evidence


- ev: Probe ran 11/11 real rule assertions headless: Shield full-instance absorption + consumption, fatigue on empty-deck draw, the hand-limit-guard-precedes-fatigue nuance (surfaced by the probe itself when a naive fatigue test failed), orderPrevent once-per-cycle champion passive, 6-unit board limit blocking playability. Zero app-code changes; render stub is 3 functions.

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
