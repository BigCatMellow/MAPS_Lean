# Helper Assignment — EXP-0004 Orientation Manifest Construction

- Owner: codex-lab-lilo
- Helper tag: helper-librarian-rori
- Status: COMPLETE
- Experiment: `EXP-0004`
- Objective: Build the treatment packet for a reversible orientation experiment. The packet must make a resumed agent’s first valid lifecycle action discoverable with less context, while retaining explicit pointers to canonical authority.
- Fixed scenario: Claude owns `TASK-227`, which is `CHANGES_REQUESTED` after a plan review; TASK-220 is released; the operator wants continued system improvement; a helper may assist only visibly and within a durable bounded scope. The resumed agent must identify task state/owner, first valid action, authority boundary, helper boundary, and interruption-safe recovery path.
- Scope: Read-only source inspection plus one experiment artifact. Use only the current canonical sources needed for the scenario: task record, review record, handoff, `AGENTS.md`, `MAP_System/AGENTS.md`, `DECISION_AUTHORITY_SYSTEM.md`, `agents/README.md`, and relevant status/runner output. Do not change the real startup contract, indexes, task state, or policies.
- Required output: `MAP_System/artifacts/experiments/orientation-manifest-control-treatment-2026-07-18.md`. Include (1) control source list and measured bytes/words; (2) a compact treatment manifest with fact, authority class, currentness, and canonical reference for every required answer; (3) treatment bytes/words; (4) explicit gaps/unknowns; (5) a verifier checklist for the five fixed scenario questions.
- Prohibited: implementation/index edits, changing task state, compressing away authority/safety uncertainty, E/I promotion, or hcom requests.
- Completion: reported `MAP_System/artifacts/experiments/orientation-manifest-control-treatment-2026-07-18.md` through hcom with control 51,378 bytes and treatment 5,653 bytes; returned to listening.
