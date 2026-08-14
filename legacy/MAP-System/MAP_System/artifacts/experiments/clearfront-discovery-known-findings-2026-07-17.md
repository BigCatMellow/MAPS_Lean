# Frozen Known-Findings Set — ClearFront Discovery Pilot

- Frozen by: codex-lab-lilo
- Frozen before helper output: yes
- Experiment: EXP-0003 / TASK-226
- Purpose: distinguish actual discovery from restatement.

## Product/rules findings already known

1. Baseline parity is not rules conformance.
2. Equipment, Mind, Forge, Neutral, and Stun are missing; Rush/Drain are
   narrower than documented; fatigue and deck composition diverge.
3. Deterministic engine coverage is incomplete, including passive effects and
   target legality (TASK-220 changes requested).
4. Hidden-information undo was exploitable and was fixed by TASK-213.
5. Mobile card detail behavior is unresolved/ambiguous.
6. Rules-conformance disposition—implement specification or revise it—requires
   a product/design decision.

## Architecture/delivery findings already known

7. `combat.js`, mutable `ctx`, `window.CF`, and cross-module calls remain
   coupled despite file decomposition.
8. Reviews found extractor security/atomicity defects, a missing render
   binding, and four runtime-only extraction defects.
9. The phase lacked an immutable Git snapshot/commit boundary.
10. Browser evidence was manually orchestrated and timing-sensitive; TASK-219
    added a one-command gate, but deterministic semantic coverage remains open.
11. Uniform ceremony made low-risk work slow; risk-tiered review and batched
    low-risk governance were adopted in DEC-CF-008/TASK-218.
12. Evidence/event volume diluted signal; state-change-only events and one
    canonical record per concern were recommended.
13. Project-local versus global event scope diverged.
14. Risks/current-state documents drifted after mitigation.
15. Shared-file ownership limited real implementation parallelism.

## Existing emergence/process learning

16. Byte-identical screenshots plus dependency-free CDP replay form a cheap
    parity gate (INS-0024).
17. The decomposition exposed a headless engine seam inexpensively (INS-0026).
18. Operational notes do not automatically become behavior (INS-0027), now
    addressed by TASK-223.
19. A deterministic E/I Sentinel catches repeated friction but not positive
    emergence or implied needs; its initial recall was 1/4 (TASK-224/INS-0028).
20. Additional agents should be used only for real parallelism, specialization,
    context isolation, or independent verification (TASK-222 study).

## Sentinel candidates already queued

Repeated rework/blocker signals already exist for TASK-083, 103, 141, 158,
189, 206, and 207. A Discovery finding that merely says these tasks had
repeated blockers/rework is a duplicate unless it supplies a materially new,
evidence-backed mechanism or response.

## Adjudication labels

- `known_duplicate`
- `useful_refinement`
- `genuinely_new_useful`
- `weak_or_speculative`
- `scope_drift`

The coordinator will also check classification accuracy, especially whether
optional ideas are mislabeled as requirements.
