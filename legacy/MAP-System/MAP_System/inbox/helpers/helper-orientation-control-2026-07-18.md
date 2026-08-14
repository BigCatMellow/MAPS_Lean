# Helper Assignment — EXP-0004 Canonical Control Answers

- Owner: codex-lab-lilo
- Helper tag: helper-review-steward-moku
- Status: COMPLETE
- Experiment: `EXP-0004`
- Objective: Establish the canonical control answers for the fixed resumed-agent scenario before seeing the compact treatment manifest. This is an independent source-verification pass, not TASK-227 review and not a policy decision.
- Fixed scenario: Claude owns `TASK-227`, which is `CHANGES_REQUESTED` after a plan review; TASK-220 is released; the operator wants continued system improvement; a helper may assist only visibly and within a durable bounded scope. The resumed agent must identify task state/owner, first valid action, authority boundary, helper boundary, and interruption-safe recovery path.
- Scope: Read only the task record, review record, handoff, `AGENTS.md`, `MAP_System/AGENTS.md`, `DECISION_AUTHORITY_SYSTEM.md`, `agents/README.md`, current status, and runner output. Do not read the treatment manifest or the librarian assignment before writing the control answer.
- Required output: `MAP_System/artifacts/experiments/orientation-manifest-canonical-control-2026-07-18.md`. For each of the five questions, give the answer, exact canonical source(s), confidence, and any ambiguity. Include the source list and measured bytes/words. State which facts must not be compressed away.
- Prohibited: source or task-state edits, policy/decision changes, treatment-manifest review, E/I promotion, and hcom requests.
- Completion: reported `MAP_System/artifacts/experiments/orientation-manifest-canonical-control-2026-07-18.md` with 5,104 bytes through hcom; returned to listening. The treatment comparison remains a separate assignment.
